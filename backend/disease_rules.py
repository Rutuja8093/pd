"""
Disease Rules Engine for Sugarcane Disease Detection (Backend Support)

This module provides rule-based computer vision analysis that complements
the PyTorch UNet model (.pth).

User Domain Rules:
1. Red Rot: Leaf midrib turns red, with red and white patches inside the stem.
2. Mosaic: Leaves develop irregular light-green and dark-green patches.
3. Brown Rust: Small reddish-brown pustules appear on the leaf surface.

When the UNet model is uncertain, fails, or predicts an incorrect class,
these rules provide robust backend verification and support.
All rule evaluation details remain strictly in the backend.
"""

import cv2
import numpy as np
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

# Colors matching UNet visualization overlay (RGBA)
DISEASE_COLORS = {
    "Brown Rust": (255, 140, 0, 150),   # Orange
    "Mosaic": (180, 220, 40, 150),      # Yellow-green
    "Red Rot": (220, 40, 40, 150),       # Red
}


def is_sugarcane_leaf(img_rgb: np.ndarray, img_hsv: np.ndarray) -> tuple:
    """
    Validates whether the input image contains genuine sugarcane plant/leaf tissue.
    Strictly filters out non-supported objects, pests (such as White Grub insects),
    and non-leaf studio backgrounds.
    
    Only 3 sugarcane leaf diseases are supported:
    1. Brown Rust
    2. Red Rot
    3. Mosaic
    (plus Healthy leaf)
    """
    h, w = img_rgb.shape[:2]
    total_pixels = h * w
    r = img_rgb[:, :, 0].astype(np.float32)
    g = img_rgb[:, :, 1].astype(np.float32)
    b = img_rgb[:, :, 2].astype(np.float32)
    
    # 1. Studio white / light gray background (R > 220, G > 220, B > 220, S < 45)
    pure_bg = (r > 220) & (g > 220) & (b > 220) & (img_hsv[:, :, 1] < 45)
    pure_bg_ratio = np.sum(pure_bg) / total_pixels
    
    # 2. Green leaf blade (chlorophyll: H in 20-95, S >= 25, V >= 30)
    green_mask = cv2.inRange(img_hsv, np.array([20, 25, 30]), np.array([95, 255, 255]))
    green_ratio = np.sum(green_mask > 0) / total_pixels
    
    # 3. Straw / dried leaf tissue (H in 12-24, S >= 30, V >= 40)
    straw_mask = cv2.inRange(img_hsv, np.array([12, 30, 40]), np.array([24, 210, 240]))
    straw_ratio = np.sum(straw_mask > 0) / total_pixels
    
    plant_ratio = green_ratio + straw_ratio
    
    # If the image is an isolated object on a studio white background with minimal green leaf blade
    # (e.g. white grub insect on a white studio sheet, isolated pest specimen, etc.)
    if pure_bg_ratio > 0.25 and green_ratio < 0.10:
        return False, f"isolated_object_on_white_bg (pure_bg={round(pure_bg_ratio, 2)}, green={round(green_ratio, 3)})"
        
    # Minimum plant tissue requirement for sugarcane leaf
    if plant_ratio < 0.15:
        return False, f"insufficient_plant_tissue (plant={round(plant_ratio, 3)})"
        
    return True, f"valid_leaf (green={round(green_ratio, 2)}, plant={round(plant_ratio, 2)})"


def analyze_red_rot_rule(img_rgb: np.ndarray, img_hsv: np.ndarray) -> dict:
    """
    Rule: 'Red Rot: Leaf midrib turns red, with red and white patches inside the stem.'
    
    Checks for:
    - Red / crimson / reddish-brown hues in midrib or stalk tissue
    - Distinct lesions aligned along the prominent white/pale leaf midrib
    - Presence of white / pale necrotic patches intermixed with or adjacent to red tissue
    """
    h, w = img_rgb.shape[:2]
    total_pixels = h * w
    
    # Leaf validation check
    is_leaf, _ = is_sugarcane_leaf(img_rgb, img_hsv)
    if not is_leaf:
        return {
            "score": 0.0,
            "red_ratio": 0.0,
            "on_midrib_ratio": 0.0,
            "is_on_midrib": False,
            "has_red_white_patches": False,
            "is_elongated_midrib": False,
            "mask": np.zeros((h, w), dtype=np.uint8),
        }
    
    # 1. Red & reddish-brown lesion detection in HSV & RGB
    red_mask_hsv1 = cv2.inRange(img_hsv, np.array([0, 40, 35]), np.array([16, 255, 255]))
    red_mask_hsv2 = cv2.inRange(img_hsv, np.array([165, 40, 35]), np.array([180, 255, 255]))
    red_mask_hsv = cv2.bitwise_or(red_mask_hsv1, red_mask_hsv2)
    
    r = img_rgb[:, :, 0].astype(np.float32)
    g = img_rgb[:, :, 1].astype(np.float32)
    b = img_rgb[:, :, 2].astype(np.float32)

    # Detect studio white/gray background (R > 225, G > 225, B > 225, S < 40)
    pure_bg_mask = (r > 225) & (g > 225) & (b > 225) & (img_hsv[:, :, 1] < 40)
    pure_bg_ratio = np.sum(pure_bg_mask) / total_pixels

    # Check for presence of sugarcane plant/leaf tissue (green or dry leaf blade)
    green_leaf = cv2.inRange(img_hsv, np.array([20, 20, 30]), np.array([95, 255, 255]))
    straw_leaf = cv2.inRange(img_hsv, np.array([10, 25, 40]), np.array([24, 220, 240]))
    plant_mask = cv2.bitwise_or(green_leaf, straw_leaf)
    plant_ratio = np.sum(plant_mask > 0) / total_pixels

    # If the image is dominated by white background (>35%) and has minimal leaf tissue (<12%),
    # it is an isolated object/insect or non-leaf crop, NOT a leaf midrib
    if pure_bg_ratio > 0.35 and plant_ratio < 0.12:
        return {
            "score": 0.0,
            "red_ratio": 0.0,
            "on_midrib_ratio": 0.0,
            "is_on_midrib": False,
            "has_red_white_patches": False,
            "is_elongated_midrib": False,
            "mask": np.zeros((h, w), dtype=np.uint8),
        }
    
    # Red-dominant check
    red_rgb = (r > 65) & (r > b * 1.15) & (r > g * 1.02)
    red_mask = red_mask_hsv & red_rgb.astype(np.uint8) * 255
    
    # Clean noise with morphological opening
    kernel_small = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    red_mask_cleaned = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel_small)
    
    red_pixels = int(np.sum(red_mask_cleaned > 0))
    red_ratio = red_pixels / total_pixels
    
    # 2. White midrib and pale patches inside/along stem/midrib (exclude pure white non-leaf background)
    white_midrib = (img_hsv[:, :, 1] < 85) & (img_hsv[:, :, 2] > 125) & ~pure_bg_mask
    kernel_midrib = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
    midrib_expanded = cv2.dilate(white_midrib.astype(np.uint8) * 255, kernel_midrib)
    
    on_midrib = (red_mask_cleaned > 0) & (midrib_expanded > 0)
    on_midrib_ratio = np.sum(on_midrib) / max(1, red_pixels)
    
    # 3. Midrib / patch elongation (both axis-aligned and rotated minAreaRect for diagonal leaves)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(red_mask_cleaned)
    max_component_area = 0
    max_aspect_ratio = 1.0
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area > max_component_area:
            max_component_area = area
            cw = max(1, stats[i, cv2.CC_STAT_WIDTH])
            ch = max(1, stats[i, cv2.CC_STAT_HEIGHT])
            max_aspect_ratio = max(cw / ch, ch / cw)
            
    # Rotated bounding box analysis for diagonal leaves/midribs
    contours, _ = cv2.findContours(red_mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    has_rot_elongation = False
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > (total_pixels * 0.0015):
            rect = cv2.minAreaRect(cnt)
            (cx, cy), (rw, rh), angle = rect
            longer = max(rw, rh)
            shorter = max(1.0, min(rw, rh))
            rot_ar = longer / shorter
            if rot_ar > max_aspect_ratio:
                max_aspect_ratio = rot_ar
            if rot_ar >= 2.5 and longer > 30:
                has_rot_elongation = True
                
    is_elongated_midrib = ((max_aspect_ratio > 1.8) and (max_component_area > total_pixels * 0.004)) or has_rot_elongation
    is_on_midrib = (on_midrib_ratio > 0.15 and max_aspect_ratio > 1.4) or has_rot_elongation

    # White / pale center patches (straw-colored centers inside red margins)
    s_channel = img_hsv[:, :, 1]
    v_channel = img_hsv[:, :, 2]
    white_mask = (s_channel < 85) & (v_channel > 130) & (r > 90) & (g > 85)
    
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    red_dilated = cv2.dilate(red_mask_cleaned, kernel_dilate)
    red_white_overlap = (red_dilated > 0) & white_mask
    red_white_pixels = int(np.sum(red_white_overlap))
    has_red_white_patches = red_white_pixels > (total_pixels * 0.0015)
    
    # Calculate score [0.0 to 1.0]
    score = 0.0
    if red_ratio > 0.003:
        score += min(0.40, red_ratio * 15.0)
        # Defining hallmark: lesions specifically situated on or along the midrib!
        if is_on_midrib:
            score += 0.35
        if has_red_white_patches:
            score += 0.15
        if is_elongated_midrib:
            score += 0.20
        if max_component_area > total_pixels * 0.01:
            score += 0.10
            
    score = min(1.0, score)
    
    return {
        "score": round(score, 3),
        "red_ratio": round(red_ratio, 4),
        "on_midrib_ratio": round(float(on_midrib_ratio), 3),
        "is_on_midrib": bool(is_on_midrib),
        "has_red_white_patches": bool(has_red_white_patches),
        "is_elongated_midrib": bool(is_elongated_midrib),
        "mask": red_mask_cleaned,
    }


def analyze_mosaic_rule(img_rgb: np.ndarray, img_hsv: np.ndarray) -> dict:
    """
    Rule: 'Mosaic: Leaves develop irregular light-green and dark-green patches.'
    
    Checks for:
    - Simultaneous presence of irregular light-green and dark-green patches
    - Chlorotic mottling across leaf blade
    - Spatial variation / standard deviation in green tones without red pustules
    """
    h, w = img_rgb.shape[:2]
    total_pixels = h * w
    
    # Leaf mask: green spectrum (H in 22-90, S > 25, V > 35)
    leaf_mask = cv2.inRange(img_hsv, np.array([22, 25, 35]), np.array([92, 255, 255]))
    leaf_pixels = int(np.sum(leaf_mask > 0))
    leaf_ratio = leaf_pixels / total_pixels
    
    if leaf_ratio < 0.15:
        # Not a leaf image or too dark
        return {"score": 0.0, "mottling_index": 0.0, "mask": np.zeros((h, w), dtype=np.uint8)}
    
    # 1. Light-green / chlorotic patches (yellow-green or high-value pale green)
    # Yellow-green: H in 25-45, S in 30-220, V in 70-255
    lg1 = cv2.inRange(img_hsv, np.array([25, 30, 80]), np.array([45, 230, 255]))
    # Bright pale green: H in 45-75, V > 140, S in 30-175
    lg2 = cv2.inRange(img_hsv, np.array([45, 30, 140]), np.array([75, 175, 255]))
    light_green_mask = cv2.bitwise_or(lg1, lg2) & leaf_mask
    
    # 2. Dark-green / healthy dense green patches: H in 48-90, V in 35-135, S in 50-255
    dark_green_mask = cv2.inRange(img_hsv, np.array([48, 50, 35]), np.array([90, 255, 135])) & leaf_mask
    
    lg_ratio = np.sum(light_green_mask > 0) / leaf_pixels
    dg_ratio = np.sum(dark_green_mask > 0) / leaf_pixels
    
    # 3. Measure irregular mottling texture across leaf
    # Calculate standard deviation of Value and Green intensity inside leaf mask
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    leaf_pts = gray[leaf_mask > 0]
    val_std = float(np.std(leaf_pts)) if len(leaf_pts) > 0 else 0.0
    
    # Multiple irregular light-green patches (connected components)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    lg_cleaned = cv2.morphologyEx(light_green_mask, cv2.MORPH_OPEN, kernel)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(lg_cleaned)
    # Count patches of medium size (irregular chlorotic islands)
    island_count = sum(1 for i in range(1, num_labels) if 20 < stats[i, cv2.CC_STAT_AREA] < (total_pixels * 0.15))
    
    # Check if red/rust is absent (Mosaic leaves have green patches, not red/rust)
    r = img_rgb[:, :, 0].astype(np.float32)
    b = img_rgb[:, :, 2].astype(np.float32)
    red_rust_pixels = np.sum((r > 100) & (r > b * 1.3) & (img_hsv[:, :, 0] < 20))
    red_rust_ratio = red_rust_pixels / leaf_pixels
    
    score = 0.0
    # Both light-green and dark-green patches must coexist
    if lg_ratio > 0.08 and dg_ratio > 0.08 and red_rust_ratio < 0.08:
        # Balanced presence of light and dark green
        balance = 1.0 - abs(lg_ratio - dg_ratio) / (lg_ratio + dg_ratio + 1e-6)
        score += min(0.45, balance * 0.45)
        
        # Mottling variance bonus
        if val_std > 22.0:
            score += min(0.30, (val_std - 22.0) / 40.0 * 0.30)
            
        # Multiple irregular patches bonus
        if island_count >= 3:
            score += min(0.25, island_count * 0.04)
            
    score = min(1.0, score)
    
    return {
        "score": round(score, 3),
        "light_green_ratio": round(lg_ratio, 3),
        "dark_green_ratio": round(dg_ratio, 3),
        "val_std": round(val_std, 1),
        "island_count": island_count,
        "mask": lg_cleaned,
    }


def analyze_brown_rust_rule(img_rgb: np.ndarray, img_hsv: np.ndarray, red_rot_mask: np.ndarray = None, red_rot_score: float = 0.0) -> dict:
    """
    Rule: 'Brown Rust: Small reddish-brown pustules appear on the leaf surface.'
    
    Checks for:
    - Reddish-brown / rusty orange-brown pustule coloration
    - Morphological presence of small, scattered pustules / spots on the leaf blade
    - High pustule count / spot density across leaf surface
    """
    h, w = img_rgb.shape[:2]
    total_pixels = h * w

    is_leaf, _ = is_sugarcane_leaf(img_rgb, img_hsv)
    if not is_leaf:
        return {
            "score": 0.0,
            "rust_ratio": 0.0,
            "pustule_count": 0,
            "pustule_coverage": 0.0,
            "mask": np.zeros((h, w), dtype=np.uint8),
        }

    r = img_rgb[:, :, 0].astype(np.float32)
    g = img_rgb[:, :, 1].astype(np.float32)
    b = img_rgb[:, :, 2].astype(np.float32)

    # Detect studio white/gray background
    pure_bg_mask = (r > 225) & (g > 225) & (b > 225) & (img_hsv[:, :, 1] < 40)
    pure_bg_ratio = np.sum(pure_bg_mask) / total_pixels
    green_leaf = cv2.inRange(img_hsv, np.array([20, 20, 30]), np.array([95, 255, 255]))
    straw_leaf = cv2.inRange(img_hsv, np.array([10, 25, 40]), np.array([24, 220, 240]))
    plant_ratio = np.sum(cv2.bitwise_or(green_leaf, straw_leaf) > 0) / total_pixels

    if pure_bg_ratio > 0.35 and plant_ratio < 0.12:
        return {
            "score": 0.0,
            "rust_ratio": 0.0,
            "pustule_count": 0,
            "pustule_coverage": 0.0,
            "mask": np.zeros((h, w), dtype=np.uint8),
        }
    
    # 1. Rust color in HSV (H in 9-26, S in 60-255, V in 35-215)
    rust_hsv = cv2.inRange(img_hsv, np.array([9, 60, 35]), np.array([26, 255, 215]))
    
    # RGB check: Red > Green > Blue (warm rusty tone)
    rust_rgb = (r > 65) & (r > b * 1.25) & (r >= g * 0.95) & (g > b * 0.9)
    
    rust_mask = rust_hsv & rust_rgb.astype(np.uint8) * 255
    
    # 2. Pustule morphology: small spots / pustules
    # Filter noise with small opening
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    rust_cleaned = cv2.morphologyEx(rust_mask, cv2.MORPH_OPEN, kernel)
    
    # Exclude red rot midrib lesion and its halo from rust pustule counting
    # (The borders of red midrib lesions have reddish-brown tones that are part of the midrib lesion, not rust)
    if red_rot_mask is not None and np.sum(red_rot_mask > 0) > (total_pixels * 0.003):
        red_halo = cv2.dilate(red_rot_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        rust_cleaned = cv2.bitwise_and(rust_cleaned, cv2.bitwise_not(red_halo))
    
    rust_pixels = int(np.sum(rust_cleaned > 0))
    rust_ratio = rust_pixels / total_pixels
    
    # Connected component analysis for small pustules
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(rust_cleaned)
    
    # Small reddish-brown pustules: typical area between 4 and 1500 pixels (for 256x256 scaled space)
    min_area = max(4, int(total_pixels * 0.0001))
    max_area = max(50, int(total_pixels * 0.05))
    
    pustule_count = 0
    pustule_pixel_area = 0
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if min_area <= area <= max_area:
            pustule_count += 1
            pustule_pixel_area += area
            
    pustule_coverage = pustule_pixel_area / total_pixels
    
    score = 0.0
    if rust_ratio > 0.01:
        # Base score from rust coverage
        score += min(0.45, rust_ratio * 6.0)
        
        # Pustule count bonus (the definitive hallmark: small pustules on leaf surface)
        if pustule_count >= 5:
            score += min(0.35, pustule_count * 0.035)
        elif pustule_count >= 2:
            score += 0.15
            
        # Pustule area ratio bonus
        if pustule_coverage > 0.01:
            score += min(0.25, pustule_coverage * 10.0)
            
        # Brown Rust occurs across the broad leaf blade (interveinal).
        # If lesions are on or along the central midrib, they are Red Rot midrib lesions, NOT Brown Rust!
        white_midrib = (img_hsv[:, :, 1] < 85) & (img_hsv[:, :, 2] > 125)
        kernel_midrib = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
        midrib_expanded = cv2.dilate(white_midrib.astype(np.uint8) * 255, kernel_midrib)
        on_midrib = (rust_cleaned > 0) & (midrib_expanded > 0)
        on_midrib_ratio = np.sum(on_midrib) / max(1, rust_pixels)
        if on_midrib_ratio > 0.20:
            score *= max(0.10, 1.0 - on_midrib_ratio * 1.6)
            
        # If a prominent Red Rot midrib lesion is present, any minor rust flecking is secondary
        if red_rot_score >= 0.55:
            score = min(score, 0.40)
            
    score = min(1.0, score)
    
    return {
        "score": round(score, 3),
        "rust_ratio": round(rust_ratio, 4),
        "pustule_count": pustule_count,
        "pustule_coverage": round(pustule_coverage, 4),
        "mask": rust_cleaned,
    }


def evaluate_rules(image: Image.Image) -> dict:
    """
    Evaluates backend botanical rules on the input PIL Image.
    Returns scores, best matching disease, and segmentation masks.
    """
    # Resize to standard analysis size for consistent thresholding
    img_resized = image.resize((256, 256), Image.Resampling.LANCZOS)
    img_rgb = np.array(img_resized.convert("RGB"))
    img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    
    # 0. Botanical check: Is this image a sugarcane leaf?
    is_leaf, leaf_reason = is_sugarcane_leaf(img_rgb, img_hsv)
    if not is_leaf:
        return {
            "scores": {"Red Rot": 0.0, "Mosaic": 0.0, "Brown Rust": 0.0, "Healthy": 0.0},
            "top_disease": "Unrecognized",
            "top_score": 0.0,
            "is_healthy": False,
            "is_leaf": False,
            "leaf_reason": leaf_reason,
            "masks": {
                "Red Rot": np.zeros((256, 256), dtype=np.uint8),
                "Mosaic": np.zeros((256, 256), dtype=np.uint8),
                "Brown Rust": np.zeros((256, 256), dtype=np.uint8),
            },
            "details": {}
        }
    
    red_rot = analyze_red_rot_rule(img_rgb, img_hsv)
    mosaic = analyze_mosaic_rule(img_rgb, img_hsv)
    
    # Only suppress rust if Red Rot has a confirmed midrib lesion
    has_midrib_lesion = red_rot["is_elongated_midrib"] or (red_rot["is_on_midrib"] and red_rot["score"] >= 0.50)
    brown_rust = analyze_brown_rust_rule(
        img_rgb,
        img_hsv,
        red_rot_mask=red_rot["mask"] if has_midrib_lesion else None,
        red_rot_score=red_rot["score"] if has_midrib_lesion else 0.0
    )
    
    scores = {
        "Red Rot": red_rot["score"],
        "Mosaic": mosaic["score"],
        "Brown Rust": brown_rust["score"],
    }
    
    # Determine top scoring disease according to rules
    top_disease = max(scores, key=scores.get)
    top_score = scores[top_disease]
    
    # Check if healthy (uniform green leaf, negligible disease score)
    leaf_mask = cv2.inRange(img_hsv, np.array([25, 40, 35]), np.array([85, 255, 255]))
    green_leaf_ratio = np.sum(leaf_mask > 0) / (256 * 256)
    
    is_healthy = False
    if green_leaf_ratio > 0.45 and top_score < 0.22:
        is_healthy = True
        scores["Healthy"] = round(1.0 - top_score, 3)
    else:
        scores["Healthy"] = 0.0
        
    return {
        "scores": scores,
        "top_disease": top_disease if not is_healthy else "Healthy",
        "top_score": top_score if not is_healthy else scores["Healthy"],
        "is_healthy": is_healthy,
        "masks": {
            "Red Rot": red_rot["mask"],
            "Mosaic": mosaic["mask"],
            "Brown Rust": brown_rust["mask"],
        },
        "details": {
            "Red Rot": {k: v for k, v in red_rot.items() if k != "mask"},
            "Mosaic": {k: v for k, v in mosaic.items() if k != "mask"},
            "Brown Rust": {k: v for k, v in brown_rust.items() if k != "mask"},
        }
    }


def generate_rule_overlay(image: Image.Image, disease: str, mask_256: np.ndarray) -> bytes:
    """
    Creates a visual segmentation overlay using the rule-detected mask.
    Matches the UNet overlay style and colors.
    """
    orig_w, orig_h = image.size
    overlay_base = image.resize((256, 256), Image.Resampling.LANCZOS).convert("RGBA")
    
    color = DISEASE_COLORS.get(disease, (220, 40, 40, 150))
    mask_layer = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    mask_pixels = mask_layer.load()
    
    for y in range(256):
        for x in range(256):
            if mask_256[y, x] > 0:
                mask_pixels[x, y] = color
                
    composite = Image.alpha_composite(overlay_base, mask_layer)
    composite = composite.resize((orig_w, orig_h), Image.Resampling.LANCZOS)
    
    buf = io.BytesIO()
    composite.convert("RGB").save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def generate_multi_disease_overlay(
    image: Image.Image,
    rule_masks: dict,
    unet_pred_mask: np.ndarray = None,
    active_diseases: list = None
) -> bytes:
    """
    Creates a dual/multi-disease visual segmentation overlay.
    Each disease is colored distinctly:
    - Brown Rust: Orange (255, 140, 0, 165)
    - Red Rot: Crimson Red (220, 30, 30, 175)
    - Mosaic: Yellow-green (180, 220, 40, 165)
    """
    orig_w, orig_h = image.size
    overlay_base = image.resize((256, 256), Image.Resampling.LANCZOS).convert("RGBA")
    mask_layer = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    mask_pixels = mask_layer.load()
    
    unet_colors = {
        1: (255, 140, 0, 165),    # Brown Rust - orange
        2: (180, 220, 40, 165),   # Mosaic - yellow-green
        3: (220, 30, 30, 175),    # Red Rot - red
    }
    
    # 1. Fill from UNet segmented mask
    if unet_pred_mask is not None:
        for y in range(256):
            for x in range(256):
                cls = int(unet_pred_mask[y, x])
                if cls in unet_colors:
                    mask_pixels[x, y] = unet_colors[cls]
                    
    # 2. Complement with rule masks for active diseases
    if rule_masks:
        # Brown Rust pustules
        if "Brown Rust" in rule_masks and (not active_diseases or "Brown Rust" in active_diseases):
            rust_m = rule_masks["Brown Rust"]
            if rust_m.shape[:2] != (256, 256):
                rust_m = cv2.resize(rust_m, (256, 256), interpolation=cv2.INTER_NEAREST)
            for y in range(256):
                for x in range(256):
                    if rust_m[y, x] > 0:
                        # Don't overwrite Red Rot midrib with rust
                        if mask_pixels[x, y][3] == 0 or mask_pixels[x, y] != unet_colors.get(3):
                            mask_pixels[x, y] = unet_colors[1]
                            
        # Red Rot midrib lesions
        if "Red Rot" in rule_masks and (not active_diseases or "Red Rot" in active_diseases):
            rr_m = rule_masks["Red Rot"]
            if rr_m.shape[:2] != (256, 256):
                rr_m = cv2.resize(rr_m, (256, 256), interpolation=cv2.INTER_NEAREST)
            for y in range(256):
                for x in range(256):
                    if rr_m[y, x] > 0:
                        mask_pixels[x, y] = unet_colors[3]
                        
        # Mosaic
        if "Mosaic" in rule_masks and (not active_diseases or "Mosaic" in active_diseases):
            mos_m = rule_masks["Mosaic"]
            if mos_m.shape[:2] != (256, 256):
                mos_m = cv2.resize(mos_m, (256, 256), interpolation=cv2.INTER_NEAREST)
            for y in range(256):
                for x in range(256):
                    if mos_m[y, x] > 0 and mask_pixels[x, y][3] == 0:
                        mask_pixels[x, y] = unet_colors[2]
                        
    composite = Image.alpha_composite(overlay_base, mask_layer)
    composite = composite.resize((orig_w, orig_h), Image.Resampling.LANCZOS)
    
    buf = io.BytesIO()
    composite.convert("RGB").save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def combine_ensemble_models_and_rules(
    unet_result: dict,
    eff_result: dict,
    image_bytes: bytes
) -> dict:
    """
    Combines two .pth models (UNet ResNet-34 + EfficientNet-B0) with the backend rules engine.
    
    Model 1 (.pth): UNet ResNet-34 (pixel-level segmentation & localized detection)
    Model 2 (.pth): EfficientNet-B0 (global whole-image multi-label classification)
    Backend Rules:
      1. Red Rot: Leaf midrib turns red, with red and white patches inside the stem.
      2. Mosaic: Leaves develop irregular light-green and dark-green patches.
      3. Brown Rust: Small reddish-brown pustules appear on the leaf surface.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        logger.error(f"Failed to open image for ensemble analysis: {e}")
        return {
            "disease": unet_result.get("disease") or eff_result.get("disease") or "Unrecognized",
            "severity": unet_result.get("severity") or "low",
            "affected_percent": unet_result.get("affected_percent", 0.0),
            "overlay_bytes": unet_result.get("overlay_bytes"),
            "backend_source": "image decode error",
        }
        
    rule_eval = evaluate_rules(image)
    
    # 0. Reject non-sugarcane leaf objects (insects like white grubs, pests, non-leaf studio backgrounds)
    if not rule_eval.get("is_leaf", True):
        logger.info(f"Non-sugarcane leaf detected ({rule_eval.get('leaf_reason')}). Returning Unrecognized.")
        return {
            "disease": "Unrecognized",
            "primary_disease": "Unrecognized",
            "secondary_disease": None,
            "is_co_infection": False,
            "predictions": [{
                "disease": "Unrecognized",
                "confidence": 0.0,
                "severity": "low",
                "affected_percent": 0.0
            }],
            "severity": "low",
            "affected_percent": 0.0,
            "overlay_bytes": None,
            "backend_source": "non_sugarcane_leaf_or_object",
            "scores": {"Red Rot": 0.0, "Mosaic": 0.0, "Brown Rust": 0.0}
        }
        
    rule_scores = rule_eval["scores"]
    top_rule_disease = rule_eval["top_disease"]
    top_rule_score = rule_eval["top_score"]
    
    # 1. Extract Model 1 (UNet) details
    unet_disease = unet_result.get("disease")
    unet_conf = unet_result.get("confidence", 0.0)
    unet_probs = unet_result.get("class_probs", {})
    unet_affected = unet_result.get("affected_percent", 0.0)
    unet_overlay = unet_result.get("overlay_bytes")
    
    # 2. Extract Model 2 (EfficientNet) details
    eff_disease = eff_result.get("disease")
    eff_probs = eff_result.get("class_probs", {})
    eff_conf = eff_result.get("confidence", 0.0)
    
    logger.info(
        f"[Two-Model Ensemble] UNet .pth: '{unet_disease}' (probs: {unet_probs}, affected: {unet_affected}%). "
        f"EfficientNet .pth: '{eff_disease}' (probs: {eff_probs}, conf: {round(eff_conf*100, 1)}%). "
        f"Backend Rules: {rule_scores} (top: '{top_rule_disease}' with score {top_rule_score})"
    )
    
    # 3. Fuse probabilities across both .pth models
    diseases = ["Brown Rust", "Mosaic", "Red Rot"]
    fused_model_scores = {}
    for d in diseases:
        p_unet = unet_probs.get(d, 0.0)
        p_eff = eff_probs.get(d, 0.0)
        # Equal ensemble weighting between the two trained models
        fused_model_scores[d] = 0.50 * p_eff + 0.50 * p_unet
        
    logger.info(f"[Ensemble Fused Model Scores]: {fused_model_scores}")
    
    # 4. Integrate with Backend Rules Support
    final_scores = {}
    for d in diseases:
        m_score = fused_model_scores[d]
        r_score = rule_scores.get(d, 0.0)
        
        # Core combination: 65% dual-model ensemble, 35% domain rule
        combined_s = 0.65 * m_score + 0.35 * r_score
        
        # Bonus when both models AND the rule agree
        if (eff_disease == d) and (unet_disease == d) and (r_score > 0.3):
            combined_s += 0.15
            
        final_scores[d] = round(combined_s, 3)
        
    top_combined_disease = max(final_scores, key=final_scores.get)
    max_combined_score = final_scores[top_combined_disease]
    logger.info(f"[Final Combined Scores (2 Models + Rules)]: {final_scores} -> Top: '{top_combined_disease}' ({max_combined_score})")
    
    # 4. Check if neither model is confident and rules don't fire -> Unrecognized (Unsupported disease/pest/image)
    has_confident_unet = bool(unet_disease and unet_disease not in ("Healthy", "Unrecognized") and (unet_conf >= 0.50 or unet_affected >= 0.5))
    has_confident_eff = bool(eff_disease and eff_disease not in ("Healthy", "Unrecognized") and eff_conf >= 0.70)
    has_confident_rule = bool(top_rule_score >= 0.45 and top_rule_disease not in ("Healthy", "Unrecognized"))
    
    # If no confident detection across any of the 3 supported diseases:
    if not (has_confident_unet or has_confident_eff or has_confident_rule or rule_eval["is_healthy"]):
        logger.info(f"Unsupported disease or non-leaf image detected: UNet={unet_disease}, Eff={eff_disease} ({eff_conf}), Rule={top_rule_disease} ({top_rule_score})")
        return {
            "disease": "Unrecognized",
            "primary_disease": "Unrecognized",
            "secondary_disease": None,
            "is_co_infection": False,
            "predictions": [{
                "disease": "Unrecognized",
                "confidence": 0.0,
                "severity": "low",
                "affected_percent": 0.0
            }],
            "severity": "low",
            "affected_percent": 0.0,
            "overlay_bytes": None,
            "backend_source": "unsupported_disease_or_object",
            "scores": final_scores
        }

    sorted_diseases = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    top1_disease, top1_score = sorted_diseases[0]
    top2_disease, top2_score = sorted_diseases[1]

    unet_detected_classes = unet_result.get("detected_classes", {})
    unet_pred_mask = unet_result.get("pred_mask")
    unet_conf = unet_result.get("confidence", 0.0)

    # Co-infection / Different Model Results Check:
    # Requires genuine evidence for BOTH diseases, not background noise
    diff_model_results = (
        bool(unet_disease and eff_disease) and
        (unet_disease != eff_disease) and
        (unet_disease not in ("Healthy", "Unrecognized")) and
        (eff_disease not in ("Healthy", "Unrecognized")) and
        (eff_probs.get(eff_disease, 0) >= 0.55 or eff_conf >= 0.55) and
        (unet_conf >= 0.55 or unet_affected >= 0.5 or unet_probs.get(unet_disease, 0) >= 0.55)
    )

    # 2. Both top diseases have substantial combined scores
    two_confident_scores = (
        top1_score >= 0.60 and top2_score >= 0.48 and
        top1_disease not in ("Healthy", "Unrecognized") and
        top2_disease not in ("Healthy", "Unrecognized") and
        (rule_scores.get(top1_disease, 0) >= 0.35 or unet_probs.get(top1_disease, 0) >= 0.50) and
        (rule_scores.get(top2_disease, 0) >= 0.35 or unet_probs.get(top2_disease, 0) >= 0.50)
    )
    
    # 3. UNet segmented pixels for two distinct classes
    two_unet_classes = [
        c for c, info in unet_detected_classes.items()
        if info.get("pixels", 0) >= 80 and info.get("confidence", 0) >= 0.40 and c in diseases
    ]
    
    # 4. Rules found distinct indicators for two diseases
    two_rule_classes = [
        d for d, s in rule_scores.items()
        if s >= 0.35 and d in diseases
    ]

    # Check if backend rules decisively resolve a conflict between differing model predictions
    rule_conflict_resolved = (
        (top1_score - top2_score >= 0.15) and
        (rule_scores.get(top1_disease, 0) >= 0.50) and
        (rule_scores.get(top2_disease, 0) < 0.35)
    )

    is_co_infection = False
    co_diseases = []

    if not rule_conflict_resolved and (has_confident_unet or has_confident_eff) and (diff_model_results or two_confident_scores or len(two_unet_classes) >= 2 or len(two_rule_classes) >= 2):
        is_co_infection = True
        if diff_model_results:
            # Guarantee both model predictions are included
            d_first = eff_disease if final_scores.get(eff_disease, 0) >= final_scores.get(unet_disease, 0) else unet_disease
            d_second = unet_disease if d_first == eff_disease else eff_disease
            co_diseases = [d_first, d_second]
        else:
            co_diseases = [top1_disease, top2_disease]

    if is_co_infection and len(co_diseases) >= 2:
        d1, d2 = co_diseases[0], co_diseases[1]
        
        def get_pred_meta(d_name):
            d_eff_p = eff_probs.get(d_name, 0.0)
            d_u_info = unet_detected_classes.get(d_name, {})
            d_u_p = d_u_info.get("confidence", unet_probs.get(d_name, 0.0))
            d_u_px = d_u_info.get("pixels", 0)
            
            conf = max(d_eff_p, d_u_p, final_scores.get(d_name, 0.0))
            
            ratio = (d_u_px / (256 * 256)) if d_u_px > 0 else (rule_scores.get(d_name, 0.0) * 0.15)
            if ratio > 0.15 or conf > 0.90:
                sev = "medium"
            elif ratio > 0.25:
                sev = "high"
            else:
                sev = "low"
                
            return {
                "disease": d_name,
                "confidence": round(float(conf), 3),
                "severity": sev,
                "affected_percent": round(ratio * 100, 1),
            }

        pred1 = get_pred_meta(d1)
        pred2 = get_pred_meta(d2)
        predictions = [pred1, pred2]
        
        combined_disease = f"{d1} & {d2}"
        combined_severity = "high" if "high" in (pred1["severity"], pred2["severity"]) else ("medium" if "medium" in (pred1["severity"], pred2["severity"]) else "low")
        combined_affected = round(pred1["affected_percent"] + pred2["affected_percent"], 1)
        
        dual_overlay = generate_multi_disease_overlay(image, rule_eval["masks"], unet_pred_mask, active_diseases=[d1, d2])
        
        logger.info(f"[Dual Prediction / Co-infection Detected]: {combined_disease} | Predictions: {predictions}")
        
        return {
            "disease": combined_disease,
            "primary_disease": d1,
            "secondary_disease": d2,
            "is_co_infection": True,
            "predictions": predictions,
            "severity": combined_severity,
            "affected_percent": combined_affected,
            "overlay_bytes": dual_overlay,
            "backend_source": "dual_prediction_co_infection",
            "scores": final_scores
        }

    final_disease = top_combined_disease
    final_severity = unet_result.get("severity", "low")
    final_affected = unet_affected
    final_overlay = unet_overlay
    decision_source = "dual_model_ensemble"
    
    # 5. Check if Healthy
    if rule_eval["is_healthy"] and max_combined_score < 0.28:
        final_disease = "Healthy"
        final_severity = "low"
        decision_source = "confirmed_healthy"
        final_overlay = None
    elif max_combined_score < 0.22 and not (unet_disease or eff_conf > 0.5 or top_rule_score > 0.35):
        # Image does not match supported diseases
        final_disease = "Unrecognized"
        final_severity = "medium"
        decision_source = "unrecognized"
    else:
        # Determine source
        if unet_disease == top_combined_disease and eff_disease == top_combined_disease:
            decision_source = "both_models_confirmed"
        elif eff_disease == top_combined_disease and (top_rule_disease == top_combined_disease or rule_scores.get(top_combined_disease, 0) > 0.3):
            decision_source = "efficientnet_plus_rule"
        elif unet_disease == top_combined_disease:
            decision_source = "unet_plus_rule"
        elif top_rule_score > 0.5:
            decision_source = "rule_correction"
            
        # Ensure overlay exists for final disease
        if (not final_overlay or unet_disease != final_disease) and final_disease in rule_eval["masks"]:
            mask = rule_eval["masks"][final_disease]
            final_overlay = generate_rule_overlay(image, final_disease, mask)
            mask_ratio = np.sum(mask > 0) / (256 * 256)
            final_affected = round(mask_ratio * 100, 1)
            
        # Compute severity based on affected percent
        if final_affected > 20.0:
            final_severity = "high"
        elif final_affected > 6.0:
            final_severity = "medium"
        else:
            final_severity = "low"
            
    logger.info(f"[Final Decision] Disease: '{final_disease}', Severity: '{final_severity}', Source: '{decision_source}'")
    
    return {
        "disease": final_disease,
        "primary_disease": final_disease,
        "secondary_disease": None,
        "is_co_infection": False,
        "predictions": [
            {
                "disease": final_disease,
                "confidence": round(float(max_combined_score), 3),
                "severity": final_severity,
                "affected_percent": final_affected
            }
        ],
        "severity": final_severity,
        "affected_percent": final_affected,
        "overlay_bytes": final_overlay,
        "backend_source": decision_source,
        "scores": final_scores
    }


def combine_model_and_rules(
    unet_result: dict,
    image_bytes: bytes
) -> dict:
    """
    Combines the .pth UNet model prediction with the backend rules engine.
    
    Strategy:
    1. Base inference comes from the trained .pth UNet model.
    2. If the .pth model fails or produces 'Unrecognized' (low confidence or small area),
       the backend rules step in to identify the disease.
    3. If the .pth model predicts a disease, the rules cross-verify:
       - If model and rules agree: Confirmed high-confidence output.
       - If rules strongly contradict a false prediction (e.g. model says Mosaic but
         clear red midrib with white patches is present), the rules correct the output.
    4. An overlay is generated if the UNet did not provide one or if the prediction
       was corrected.
    5. All rule details remain strictly in the backend.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        logger.error(f"Failed to open image for rule analysis: {e}")
        return {
            "disease": unet_result.get("disease") or "Unrecognized",
            "severity": unet_result.get("severity") or "low",
            "affected_percent": unet_result.get("affected_percent", 0.0),
            "overlay_bytes": unet_result.get("overlay_bytes"),
            "backend_notes": "image decode error",
        }
        
    rule_eval = evaluate_rules(image)
    scores = rule_eval["scores"]
    top_rule_disease = rule_eval["top_disease"]
    top_rule_score = rule_eval["top_score"]
    
    unet_disease = unet_result.get("disease")
    unet_severity = unet_result.get("severity", "low")
    unet_affected = unet_result.get("affected_percent", 0.0)
    unet_overlay = unet_result.get("overlay_bytes")
    
    logger.info(
        f"[Disease Detection Engine] UNet prediction: '{unet_disease}' (affected: {unet_affected}%). "
        f"Backend Rules scores: {scores} (top: '{top_rule_disease}' with score {top_rule_score})"
    )
    
    final_disease = unet_disease
    final_severity = unet_severity
    final_affected = unet_affected
    final_overlay = unet_overlay
    decision_source = "model"
    
    # CASE 1: UNet did not detect a disease (returned None or Unrecognized)
    if not unet_disease or unet_disease == "Unrecognized":
        if rule_eval["is_healthy"]:
            final_disease = "Healthy"
            final_severity = "low"
            decision_source = "rule_healthy"
            logger.info("Rules identified clean, uniform green leaf -> Classified as Healthy")
        elif top_rule_score >= 0.24 and top_rule_disease in DISEASE_COLORS:
            # Rules detected clear disease symptoms!
            final_disease = top_rule_disease
            decision_source = "rule_fallback"
            
            # Estimate affected percent from rule mask
            mask = rule_eval["masks"][top_rule_disease]
            affected_ratio = np.sum(mask > 0) / (256 * 256)
            final_affected = round(affected_ratio * 100, 1)
            
            if final_affected > 20.0:
                final_severity = "high"
            elif final_affected > 6.0:
                final_severity = "medium"
            else:
                final_severity = "low"
                
            final_overlay = generate_rule_overlay(image, final_disease, mask)
            logger.info(
                f"UNet was unconfident, but Backend Rules detected '{final_disease}' "
                f"(score: {top_rule_score}, affected: {final_affected}%) -> Rescued detection!"
            )
        else:
            final_disease = "Unrecognized"
            final_severity = "medium"
            decision_source = "model_unrecognized"
            
    # CASE 2: UNet predicted a disease ("Brown Rust", "Mosaic", or "Red Rot")
    else:
        # Check rule confidence for the UNet predicted disease
        unet_disease_rule_score = scores.get(unet_disease, 0.0)
        
        # Check if another disease has overwhelmingly stronger rule evidence
        # e.g., UNet mistakenly predicted Mosaic, but there is an unmistakable Red Rot midrib with white patches
        contradiction = False
        competing_disease = None
        for d, s in scores.items():
            if d != unet_disease and d in ("Red Rot", "Mosaic", "Brown Rust"):
                # If competitor rule score is high and significantly beats unet class rule score
                if s >= 0.55 and s > (unet_disease_rule_score + 0.35):
                    contradiction = True
                    competing_disease = d
                    break
                    
        if contradiction and competing_disease:
            logger.warning(
                f"UNet predicted '{unet_disease}', but backend rule for '{competing_disease}' "
                f"strongly fired (score: {scores[competing_disease]} vs {unet_disease_rule_score}). "
                f"Correcting prediction to '{competing_disease}' based on backend rules!"
            )
            final_disease = competing_disease
            decision_source = "rule_correction"
            mask = rule_eval["masks"][competing_disease]
            affected_ratio = np.sum(mask > 0) / (256 * 256)
            final_affected = round(affected_ratio * 100, 1)
            if final_affected > 20.0:
                final_severity = "high"
            elif final_affected > 6.0:
                final_severity = "medium"
            else:
                final_severity = "low"
            final_overlay = generate_rule_overlay(image, final_disease, mask)
        else:
            # Model and rules either agree or model has sufficient standing
            final_disease = unet_disease
            decision_source = "model_confirmed"
            if not final_overlay and unet_disease in rule_eval["masks"]:
                # Generate overlay from rule mask if model didn't produce one
                final_overlay = generate_rule_overlay(image, final_disease, rule_eval["masks"][unet_disease])
                
    logger.info(f"[Final Decision] Disease: '{final_disease}', Severity: '{final_severity}', Source: '{decision_source}'")
    
    return {
        "disease": final_disease,
        "severity": final_severity,
        "affected_percent": final_affected,
        "overlay_bytes": final_overlay,
        "backend_source": decision_source,
    }

