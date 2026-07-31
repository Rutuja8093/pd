from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Depends, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import requests
from PIL import Image
import io
import zipfile
import torch
import numpy as np
import segmentation_models_pytorch as smp
from torchvision import transforms
from disease_translations import DISEASE_INFO_MR, DISEASE_INFO_HI
from disease_practices import DISEASE_PRACTICES
from disease_practices_mr import DISEASE_PRACTICES_MR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Object Storage Setup
STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "sugarcane-disease"
storage_key = None

# When no EMERGENT_LLM_KEY is configured (e.g. running locally), fall back
# to storing uploaded/overlay images on local disk instead of Emergent's
# hosted object storage service.
USE_LOCAL_STORAGE = not EMERGENT_KEY
LOCAL_STORAGE_DIR = ROOT_DIR / "local_storage"
if USE_LOCAL_STORAGE:
    LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    logging.info("EMERGENT_LLM_KEY not set - using local disk storage for images instead of Emergent object storage")

# JWT Configuration
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALGORITHM = "HS256"

# Load UNet model (segmentation: 4 classes)
UNET_CLASSES = {0: "Background", 1: "Brown Rust", 2: "Mosaic", 3: "Red Rot"}
UNET_COLORS = {
    1: (255, 140, 0, 140),    # Brown Rust - orange
    2: (180, 220, 40, 140),   # Mosaic - yellow-green
    3: (220, 40, 40, 140),    # Red Rot - red
}
unet_model = None
unet_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

try:
    unet_model = smp.Unet(
        encoder_name="resnet34",
        encoder_weights=None,
        in_channels=3,
        classes=4,
        activation=None
    )
    unet_weights_path = ROOT_DIR / "models" / "best_unet.pth"
    state = torch.load(str(unet_weights_path), map_location="cpu", weights_only=False)
    unet_model.load_state_dict(state)
    unet_model.eval()
    logging.info("UNet model (best_unet.pth) loaded successfully - 4 classes")
except Exception as e:
    logging.error(f"Failed to load UNet model: {e}")
    logging.info("Will rely on GPT Vision API only")


# Disease Information Database — only UNet-supported diseases
DISEASE_INFO = {
    "Brown Rust": {
        "symptoms": "Brown/orange pustules on leaf surfaces, premature drying of leaves, reduced photosynthesis, yellow halos",
        "causes": "Fungal infection (Puccinia melanocephala), favored by humid conditions and moderate temperatures",
        "prevention": "Use resistant varieties, adequate plant spacing, remove crop residues, avoid overhead irrigation",
        "treatment": "Apply fungicides at early disease stage, ensure proper air circulation",
        "syngenta_products": ["Azoxystrobin + Difenoconazole"]
    },
    "Mosaic": {
        "symptoms": "Yellow-green mottling on leaves, stunted growth, reduced yield, irregular chlorotic patches",
        "causes": "Viral infection (Sugarcane Mosaic Virus) transmitted by aphid vectors",
        "prevention": "Use virus-free planting material, control aphid populations, remove infected plants",
        "treatment": "No chemical cure; remove and destroy infected plants, control vector insects",
        "syngenta_products": []
    },
    "Red Rot": {
        "symptoms": "Reddening of internal tissues, withering of leaves, sour smell from affected stalks, white patches in red tissue",
        "causes": "Fungal infection (Colletotrichum falcatum), waterlogged conditions, wounded stalks",
        "prevention": "Use resistant varieties, proper drainage, avoid injuries during harvesting, hot water treatment of setts",
        "treatment": "Remove infected plants, apply recommended fungicides, avoid ratoon from infected fields",
        "syngenta_products": ["Azoxystrobin + Difenoconazole"]
    },
    "Healthy": {
        "symptoms": "No visible disease symptoms, vibrant green leaves, normal growth",
        "causes": "N/A",
        "prevention": "Continue good agricultural practices, regular monitoring, balanced nutrition",
        "treatment": "No treatment needed",
        "syngenta_products": []
    },
    "Unrecognized": {
        "symptoms": "Could not be identified by our model",
        "causes": "This disease is not yet supported by our detection model",
        "prevention": "Consult with agricultural experts for guidance",
        "treatment": "Admin will review your scan and provide personalized suggestions",
        "syngenta_products": []
    }
}


def get_translated_disease_info(disease_name: str, lang: str = "en") -> Dict[str, Any]:
    """Get disease info in the requested language"""
    # Get English info as base
    info = None
    for key, val in DISEASE_INFO.items():
        if key.lower() == disease_name.lower():
            info = dict(val)
            disease_name = key
            break
    if not info:
        # Disease not in DISEASE_INFO — create a minimal base
        info = {"symptoms": "", "causes": "", "prevention": "", "treatment": "", "syngenta_products": []}
    
    if lang == "mr" and disease_name in DISEASE_INFO_MR:
        mr = DISEASE_INFO_MR[disease_name]
        info["disease_name_local"] = mr.get("disease_name", disease_name)
        if mr.get("symptoms"): info["symptoms"] = mr["symptoms"]
        if mr.get("causes"): info["causes"] = mr["causes"]
        if mr.get("prevention"): info["prevention"] = mr["prevention"]
        if mr.get("treatment"): info["treatment"] = mr["treatment"]
    elif lang == "hi" and disease_name in DISEASE_INFO_HI:
        hi = DISEASE_INFO_HI[disease_name]
        info["disease_name_local"] = hi.get("disease_name", disease_name)
        if hi.get("symptoms"): info["symptoms"] = hi["symptoms"]
        if hi.get("causes"): info["causes"] = hi["causes"]
        if hi.get("prevention"): info["prevention"] = hi["prevention"]
        if hi.get("treatment"): info["treatment"] = hi["treatment"]
    else:
        info["disease_name_local"] = disease_name
    
    return info


# Helper Functions
def init_storage():
    global storage_key
    if storage_key:
        return storage_key
    try:
        resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
        resp.raise_for_status()
        storage_key = resp.json()["storage_key"]
        return storage_key
    except Exception as e:
        logging.error(f"Storage init failed: {e}")
        raise

def put_object(path: str, data: bytes, content_type: str) -> dict:
    if USE_LOCAL_STORAGE:
        dest = LOCAL_STORAGE_DIR / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        # Save content type alongside the file so get_object can restore it
        (dest.parent / f"{dest.name}.ctype").write_text(content_type)
        return {"path": path}

    key = init_storage()
    resp = requests.put(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key, "Content-Type": content_type},
        data=data, timeout=120
    )
    resp.raise_for_status()
    return resp.json()

def get_object(path: str) -> tuple[bytes, str]:
    if USE_LOCAL_STORAGE:
        src = LOCAL_STORAGE_DIR / path
        ctype_file = src.parent / f"{src.name}.ctype"
        content_type = ctype_file.read_text() if ctype_file.exists() else "application/octet-stream"
        return src.read_bytes(), content_type

    key = init_storage()
    resp = requests.get(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key}, timeout=60
    )
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(user_id: str, username: str) -> str:
    payload = {
        "sub": user_id,
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        from bson import ObjectId
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])}, {"_id": 0, "password_hash": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user["id"] = payload["sub"]
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Disease detection functions
CONFIDENCE_THRESHOLD = 0.75  # Only accept pixel predictions above 75% softmax confidence
MIN_AFFECTED_RATIO = 0.02   # At least 2% of confident pixels must be disease to count

async def detect_disease_unet(image_bytes: bytes) -> Dict[str, Any]:
    """Primary: Use trained UNet model for segmentation and classification"""
    if not unet_model:
        return {"disease": None, "severity": "unknown", "mask_data": None}
    
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        orig_w, orig_h = image.size
        
        # Preprocess
        input_tensor = unet_transform(image).unsqueeze(0)  # [1, 3, 256, 256]
        
        with torch.no_grad():
            output = unet_model(input_tensor)  # [1, 4, 256, 256]
        
        # Apply softmax to get per-pixel confidence
        probs = torch.softmax(output.squeeze(0), dim=0).numpy()  # [4, 256, 256]
        pred_mask_raw = np.argmax(probs, axis=0)  # [256, 256]
        max_probs = np.max(probs, axis=0)  # [256, 256] confidence per pixel
        
        # Only keep predictions where model is confident enough
        # Low-confidence pixels revert to background (0)
        pred_mask = pred_mask_raw.copy()
        pred_mask[max_probs < CONFIDENCE_THRESHOLD] = 0
        
        total_pixels = pred_mask.size
        class_counts = {}
        avg_confidences = {}
        for cls_id in range(1, 4):  # Skip background (0)
            cls_mask = pred_mask == cls_id
            count = int(np.sum(cls_mask))
            if count > 0:
                class_counts[cls_id] = count
                avg_confidences[cls_id] = float(np.mean(probs[cls_id][cls_mask]))
        
        if not class_counts:
            logging.info("UNet: No disease pixels above confidence threshold")
            return {"disease": None, "severity": "low", "mask_data": None}
        
        # Dominant disease class (most pixels)
        dominant_cls = max(class_counts, key=class_counts.get)
        disease_name = UNET_CLASSES[dominant_cls]
        affected_ratio = class_counts[dominant_cls] / total_pixels
        avg_conf = avg_confidences.get(dominant_cls, 0)
        
        logging.info(f"UNet detail: {disease_name}, pixels={class_counts[dominant_cls]}, affected={round(affected_ratio*100,2)}%, avg_conf={round(avg_conf*100,1)}%")
        
        # If affected area is too small, treat as noise / unrecognized
        if affected_ratio < MIN_AFFECTED_RATIO:
            logging.info(f"UNet: {disease_name} detected but only {round(affected_ratio*100,1)}% — below minimum threshold, treating as unrecognized")
            return {"disease": None, "severity": "low", "mask_data": None}
        
        # Severity based on affected area percentage
        if affected_ratio > 0.25:
            severity = "high"
        elif affected_ratio > 0.08:
            severity = "medium"
        else:
            severity = "low"
        
        # Generate overlay image (only show confident pixels)
        overlay_image = image.resize((256, 256), Image.LANCZOS)
        overlay_rgba = overlay_image.convert("RGBA")
        mask_layer = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        mask_pixels = mask_layer.load()
        
        for y in range(256):
            for x in range(256):
                cls = int(pred_mask[y, x])
                if cls in UNET_COLORS:
                    mask_pixels[x, y] = UNET_COLORS[cls]
        
        # Composite: original + colored mask
        composite = Image.alpha_composite(overlay_rgba, mask_layer)
        # Resize back to original dimensions
        composite = composite.resize((orig_w, orig_h), Image.LANCZOS)
        
        # Convert to bytes
        buf = io.BytesIO()
        composite.convert("RGB").save(buf, format="JPEG", quality=85)
        overlay_bytes = buf.getvalue()
        
        logging.info(f"UNet: {disease_name}, affected={round(affected_ratio*100,1)}%, severity={severity}")
        return {
            "disease": disease_name,
            "severity": severity,
            "affected_percent": round(affected_ratio * 100, 1),
            "overlay_bytes": overlay_bytes,
        }
    except Exception as e:
        logging.error(f"UNet error: {e}")
        return {"disease": None, "severity": "unknown", "mask_data": None}


# Pydantic Models
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None

class AdminReview(BaseModel):
    action: str  # "approve", "reject"
    disease: Optional[str] = None  # Admin can correct the disease
    severity: Optional[str] = None
    suggestion: Optional[str] = ""

class DetectionResult(BaseModel):
    id: str
    user_id: str
    image_path: str
    disease: str
    confidence: float
    severity: str
    treatment: str
    syngenta_products: List[str]
    created_at: str

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Startup event
@app.on_event("startup")
async def startup():
    try:
        try:
            init_storage()
            logging.info("Storage initialized")
        except Exception as e:
            logging.error(f"Storage init failed (non-fatal, using local storage): {e}")
        
        # Create indexes
        
        # Create indexes
        await db.users.create_index("username", unique=True)
        
        # Seed admin
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        admin_password = os.environ.get("ADMIN_PASSWORD", "ADT@123")
        existing = await db.users.find_one({"username": admin_username})
        
        if not existing:
            hashed = hash_password(admin_password)
            await db.users.insert_one({
                "username": admin_username,
                "password_hash": hashed,
                "role": "admin",
                "name": "Administrator",
                "mobile": "",
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            logging.info("Admin user created")
        elif not verify_password(admin_password, existing["password_hash"]):
            await db.users.update_one(
                {"username": admin_username},
                {"$set": {"password_hash": hash_password(admin_password)}}
            )
        
        # Write test credentials
        with open("/app/memory/test_credentials.md", "w") as f:
            f.write("# Test Credentials\n\n")
            f.write(f"## Admin\n- Username: {admin_username}\n- Password: {admin_password}\n- Role: admin\n\n")
            f.write("## Test User\n- Username: user1\n- Password: user123\n- Role: user\n\n")
            f.write("## Endpoints\n- POST /api/auth/register\n- POST /api/auth/login\n- GET /api/auth/me\n- POST /api/detect\n- GET /api/history\n")
            
    except Exception as e:
        logging.error(f"Startup error: {e}")

# Auth Routes
@api_router.post("/auth/register")
async def register(user: UserRegister, response: Response):
    existing = await db.users.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed = hash_password(user.password)
    user_doc = {
        "username": user.username,
        "password_hash": hashed,
        "role": "user",
        "name": "",
        "mobile": "",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    access_token = create_access_token(user_id, user.username)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800,
        path="/"
    )
    
    return {
        "id": user_id,
        "username": user.username,
        "role": "user",
        "name": "",
        "mobile": ""
    }

@api_router.post("/auth/login")
async def login(user: UserLogin, response: Response):
    db_user = await db.users.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    user_id = str(db_user["_id"])
    access_token = create_access_token(user_id, user.username)
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800,
        path="/"
    )
    
    return {
        "id": user_id,
        "username": db_user["username"],
        "role": db_user.get("role", "user"),
        "name": db_user.get("name", ""),
        "mobile": db_user.get("mobile", "")
    }

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Logged out successfully"}

@api_router.put("/profile")
async def update_profile(profile: UserProfile, current_user: dict = Depends(get_current_user)):
    from bson import ObjectId
    update_data = {}
    if profile.name:
        update_data["name"] = profile.name
    if profile.mobile:
        update_data["mobile"] = profile.mobile
    
    if update_data:
        await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$set": update_data}
        )
    
    updated_user = await db.users.find_one(
        {"_id": ObjectId(current_user["id"])},
        {"_id": 0, "password_hash": 0}
    )
    updated_user["id"] = current_user["id"]
    return updated_user

# Detection Routes
@api_router.post("/detect")
async def detect_disease(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        image_bytes = await file.read()
        
        # Store image in object storage
        ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        image_id = str(uuid.uuid4())
        storage_path = f"{APP_NAME}/uploads/{current_user['id']}/{image_id}.{ext}"
        
        storage_result = put_object(storage_path, image_bytes, file.content_type or "image/jpeg")
        
        # Run UNet segmentation model only (no AI)
        logging.info("Running UNet segmentation model...")
        unet_result = await detect_disease_unet(image_bytes)
        logging.info(f"UNet: {unet_result.get('disease')} (affected: {unet_result.get('affected_percent', 0)}%)")
        
        # Store overlay image if UNet produced one
        overlay_path = ""
        overlay_bytes = unet_result.get("overlay_bytes")
        if overlay_bytes:
            overlay_storage_path = f"{APP_NAME}/overlays/{current_user['id']}/{image_id}_overlay.jpg"
            try:
                put_object(overlay_storage_path, overlay_bytes, "image/jpeg")
                overlay_path = overlay_storage_path
            except Exception as e:
                logging.warning(f"Failed to store overlay: {e}")
        
        # Use UNet result directly
        # If UNet found no disease regions, mark as "Unrecognized" (not in our model yet)
        unet_disease = unet_result.get("disease")
        if unet_disease:
            final_disease = unet_disease
            final_severity = unet_result.get("severity", "low")
        else:
            final_disease = "Unrecognized"
            final_severity = "medium"
        
        logging.info(f"FINAL RESULT: {final_disease} (severity: {final_severity})")
        
        # Normalize severity
        if final_severity not in ("high", "medium", "low"):
            final_severity = "medium" if final_disease != "Healthy" else "low"
        
        # Get disease info (case-insensitive lookup)
        disease_info = None
        for key, val in DISEASE_INFO.items():
            if key.lower() == final_disease.lower():
                disease_info = val
                final_disease = key  # Normalize to correct case
                break
        if not disease_info:
            disease_info = DISEASE_INFO.get("Healthy", {
                "symptoms": "Unknown",
                "causes": "Unknown", 
                "prevention": "Unknown",
                "treatment": "Unknown",
                "syngenta_products": []
            })
        
        # Get practices for the disease
        practices = DISEASE_PRACTICES.get(final_disease, {})
        
        # Save detection result as PENDING (admin must approve before farmer sees it)
        detection_doc = {
            "id": image_id,
            "user_id": current_user["id"],
            "username": current_user["username"],
            "image_path": storage_result["path"],
            "overlay_path": overlay_path,
            "ai_disease": final_disease,
            "ai_severity": final_severity,
            "disease": final_disease,
            "severity": final_severity,
            "treatment": disease_info["treatment"],
            "symptoms": disease_info["symptoms"],
            "causes": disease_info["causes"],
            "prevention": disease_info["prevention"],
            "cultural_practices": practices.get("cultural", []),
            "mechanical_practices": practices.get("mechanical", []),
            "biological_practices": practices.get("biological", []),
            "chemical_practices": practices.get("chemical", []),
            "spray_timing": practices.get("timing", []),
            "status": "pending",
            "admin_suggestion": "",
            "reviewed_by": "",
            "reviewed_at": "",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.detections.insert_one(detection_doc)
        detection_doc.pop("_id", None)
        
        return detection_doc
        
    except Exception as e:
        logging.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@api_router.get("/history")
async def get_history(lang: str = "en", current_user: dict = Depends(get_current_user)):
    detections = await db.detections.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    # Translate disease info based on language
    for det in detections:
        if det.get("status") == "approved" and det.get("disease"):
            translated = get_translated_disease_info(det["disease"], lang)
            det["disease_name_local"] = translated.get("disease_name_local", det["disease"])
            det["symptoms"] = translated["symptoms"]
            det["causes"] = translated["causes"]
            det["prevention"] = translated["prevention"]
            det["treatment"] = translated["treatment"]
            # Add practices for approved items
            disease_name = det["disease"]
            if lang == "mr" and disease_name in DISEASE_PRACTICES_MR:
                practices = DISEASE_PRACTICES_MR[disease_name]
            else:
                practices = DISEASE_PRACTICES.get(disease_name, {})
            det["cultural_practices"] = practices.get("cultural", [])
            det["mechanical_practices"] = practices.get("mechanical", [])
            det["biological_practices"] = practices.get("biological", [])
            det["chemical_practices"] = practices.get("chemical", [])
            det["spray_timing"] = practices.get("timing", [])
    
    return detections

@api_router.get("/files/{path:path}")
async def get_file(path: str):
    try:
        data, content_type = get_object(path)
        return Response(content=data, media_type=content_type)
    except:
        raise HTTPException(status_code=404, detail="File not found")

@api_router.get("/diseases")
async def get_diseases(lang: str = "en"):
    result = {}
    # Include ALL diseases from practices document
    for name in DISEASE_PRACTICES.keys():
        # Always get translated info (works for all diseases now)
        translated = get_translated_disease_info(name, lang)
        # Add practices data - use translated if available
        if lang == "mr" and name in DISEASE_PRACTICES_MR:
            practices = DISEASE_PRACTICES_MR[name]
        else:
            practices = DISEASE_PRACTICES.get(name, {})
        translated["cultural_practices"] = practices.get("cultural", [])
        translated["mechanical_practices"] = practices.get("mechanical", [])
        translated["biological_practices"] = practices.get("biological", [])
        translated["chemical_practices"] = practices.get("chemical", [])
        translated["spray_timing"] = practices.get("timing", [])
        result[name] = translated
    return result

# Admin Routes
@api_router.get("/admin/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(1000)
    return users

@api_router.get("/admin/detections")
async def get_all_detections(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    detections = await db.detections.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return detections

@api_router.get("/admin/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_users = await db.users.count_documents({"role": "user"})
    total_scans = await db.detections.count_documents({})
    
    # Disease distribution - only count diseases in current system
    valid_diseases = list(DISEASE_INFO.keys())
    pipeline = [
        {"$match": {"disease": {"$in": valid_diseases}}},
        {"$group": {"_id": "$disease", "count": {"$sum": 1}}}
    ]
    disease_stats = await db.detections.aggregate(pipeline).to_list(100)
    
    return {
        "total_users": total_users,
        "total_scans": total_scans,
        "disease_distribution": disease_stats
    }

@api_router.get("/admin/download-images")
async def download_all_images(current_user: dict = Depends(get_current_user)):
    """Admin only: Download all uploaded images as a ZIP file"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    detections = await db.detections.find({}, {"_id": 0, "image_path": 1, "disease": 1, "username": 1, "created_at": 1}).to_list(5000)
    
    if not detections:
        raise HTTPException(status_code=404, detail="No images found")
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for det in detections:
            try:
                image_data, content_type = get_object(det["image_path"])
                # Organize by disease folder: disease_name/username_datetime.ext
                disease_folder = det.get("disease", "Unknown").replace(" ", "_")
                username = det.get("username", "unknown")
                timestamp = det.get("created_at", "")[:19].replace(":", "-")
                ext = det["image_path"].rsplit(".", 1)[-1] if "." in det["image_path"] else "jpg"
                filename = f"{disease_folder}/{username}_{timestamp}.{ext}"
                zf.writestr(filename, image_data)
            except Exception as e:
                logging.warning(f"Failed to fetch image {det['image_path']}: {e}")
                continue
    
    zip_buffer.seek(0)
    timestamp_now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=sugarcane_images_{timestamp_now}.zip"}
    )

@api_router.get("/admin/pending")
async def get_pending_reviews(current_user: dict = Depends(get_current_user)):
    """Admin: Get all pending scans awaiting review"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    pending = await db.detections.find(
        {"status": "pending"},
        {"_id": 0}
    ).sort("created_at", -1).to_list(500)
    return pending

@api_router.post("/admin/review/{detection_id}")
async def review_detection(detection_id: str, review: AdminReview, current_user: dict = Depends(get_current_user)):
    """Admin: Approve or reject a detection with optional corrections and suggestions"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    detection = await db.detections.find_one({"id": detection_id}, {"_id": 0})
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    
    if review.action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")
    
    update_data = {
        "status": "approved" if review.action == "approve" else "rejected",
        "admin_suggestion": review.suggestion or "",
        "reviewed_by": current_user["username"],
        "reviewed_at": datetime.now(timezone.utc).isoformat()
    }
    
    # If admin corrected the disease
    if review.action == "approve" and review.disease:
        corrected_disease = review.disease
        # Look up disease info for the corrected disease
        disease_info = None
        for key, val in DISEASE_INFO.items():
            if key.lower() == corrected_disease.lower():
                disease_info = val
                corrected_disease = key
                break
        if disease_info:
            update_data["disease"] = corrected_disease
            update_data["treatment"] = disease_info["treatment"]
            update_data["symptoms"] = disease_info["symptoms"]
            update_data["causes"] = disease_info["causes"]
            update_data["prevention"] = disease_info["prevention"]
            # Update practices too
            practices = DISEASE_PRACTICES.get(corrected_disease, {})
            update_data["cultural_practices"] = practices.get("cultural", [])
            update_data["mechanical_practices"] = practices.get("mechanical", [])
            update_data["biological_practices"] = practices.get("biological", [])
            update_data["chemical_practices"] = practices.get("chemical", [])
            update_data["spray_timing"] = practices.get("timing", [])
        else:
            update_data["disease"] = corrected_disease
    
    if review.action == "approve" and review.severity:
        update_data["severity"] = review.severity
    
    await db.detections.update_one({"id": detection_id}, {"$set": update_data})
    
    updated = await db.detections.find_one({"id": detection_id}, {"_id": 0})
    return updated

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
