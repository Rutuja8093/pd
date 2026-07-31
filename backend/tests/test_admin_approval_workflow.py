"""
Admin Approval Workflow Tests
Tests: Detection saves as pending, Admin pending endpoint, Admin review (approve/reject),
       Farmer sees results only after approval, Access control for admin endpoints
"""
import pytest
import requests
import os
import io
import uuid
from PIL import Image

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ADT@123"
TEST_USER_PREFIX = "TEST_farmer_"


@pytest.fixture(scope="module")
def admin_session():
    """Create authenticated admin session"""
    session = requests.Session()
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return session


@pytest.fixture(scope="module")
def farmer_session():
    """Create authenticated farmer (regular user) session"""
    session = requests.Session()
    test_username = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}"
    
    # Register new farmer
    response = session.post(f"{BASE_URL}/api/auth/register", json={
        "username": test_username,
        "password": "farmer123"
    })
    assert response.status_code == 200, f"Farmer registration failed: {response.text}"
    return session, test_username


def create_test_image():
    """Create a simple test image for detection"""
    img = Image.new('RGB', (200, 200), color='green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


class TestDetectionSavesPending:
    """Test that detection saves with status='pending'"""
    
    def test_detect_returns_pending_status(self, admin_session):
        """POST /api/detect should return status='pending'"""
        img_bytes = create_test_image()
        
        response = admin_session.post(
            f"{BASE_URL}/api/detect",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        assert response.status_code == 200, f"Detection failed: {response.text}"
        data = response.json()
        
        # Verify pending status
        assert "status" in data, "Response missing 'status' field"
        assert data["status"] == "pending", f"Expected status='pending', got '{data['status']}'"
        
        # Verify AI prediction fields are saved
        assert "ai_disease" in data, "Response missing 'ai_disease'"
        assert "ai_severity" in data, "Response missing 'ai_severity'"
        assert "id" in data, "Response missing 'id'"
        
        print(f"✓ Detection saved with status='pending', AI predicted: {data['ai_disease']}")
        return data["id"]


class TestAdminPendingEndpoint:
    """Test GET /api/admin/pending endpoint"""
    
    def test_pending_requires_auth(self):
        """GET /api/admin/pending should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/pending")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Admin pending endpoint requires authentication")
    
    def test_pending_requires_admin_role(self, farmer_session):
        """GET /api/admin/pending should require admin role"""
        session, _ = farmer_session
        response = session.get(f"{BASE_URL}/api/admin/pending")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Admin pending endpoint requires admin role")
    
    def test_pending_returns_pending_scans(self, admin_session):
        """GET /api/admin/pending should return pending scans with AI prediction"""
        response = admin_session.get(f"{BASE_URL}/api/admin/pending")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Should return a list"
        
        # If there are pending items, verify structure
        if len(data) > 0:
            item = data[0]
            assert "id" in item, "Missing 'id'"
            assert "status" in item, "Missing 'status'"
            assert item["status"] == "pending", f"Expected pending status, got {item['status']}"
            assert "ai_disease" in item or "disease" in item, "Missing disease prediction"
            assert "username" in item, "Missing 'username'"
            assert "image_path" in item, "Missing 'image_path'"
            print(f"✓ Admin pending returned {len(data)} pending scans")
            print(f"  First item: {item.get('ai_disease', item.get('disease'))} by {item['username']}")
        else:
            print("✓ Admin pending returned empty list (no pending scans)")
        
        return data


class TestAdminReviewEndpoint:
    """Test POST /api/admin/review/{id} endpoint"""
    
    def test_review_requires_auth(self):
        """POST /api/admin/review/{id} should require authentication"""
        response = requests.post(f"{BASE_URL}/api/admin/review/fake-id", json={
            "action": "approve"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Admin review endpoint requires authentication")
    
    def test_review_requires_admin_role(self, farmer_session):
        """POST /api/admin/review/{id} should require admin role"""
        session, _ = farmer_session
        response = session.post(f"{BASE_URL}/api/admin/review/fake-id", json={
            "action": "approve"
        })
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Admin review endpoint requires admin role")
    
    def test_review_invalid_action(self, admin_session):
        """POST /api/admin/review/{id} with invalid action should fail"""
        # First create a detection
        img_bytes = create_test_image()
        detect_resp = admin_session.post(
            f"{BASE_URL}/api/detect",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        assert detect_resp.status_code == 200
        detection_id = detect_resp.json()["id"]
        
        # Try invalid action
        response = admin_session.post(f"{BASE_URL}/api/admin/review/{detection_id}", json={
            "action": "invalid_action"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Admin review rejects invalid action")
    
    def test_review_not_found(self, admin_session):
        """POST /api/admin/review/{id} with non-existent ID should return 404"""
        response = admin_session.post(f"{BASE_URL}/api/admin/review/nonexistent-id-12345", json={
            "action": "approve"
        })
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Admin review returns 404 for non-existent detection")


class TestApprovalWorkflow:
    """Test complete approval workflow"""
    
    def test_approve_scan_basic(self, admin_session):
        """Admin can approve a scan"""
        # Create detection
        img_bytes = create_test_image()
        detect_resp = admin_session.post(
            f"{BASE_URL}/api/detect",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        assert detect_resp.status_code == 200
        detection = detect_resp.json()
        detection_id = detection["id"]
        
        # Approve
        review_resp = admin_session.post(f"{BASE_URL}/api/admin/review/{detection_id}", json={
            "action": "approve"
        })
        assert review_resp.status_code == 200, f"Approve failed: {review_resp.text}"
        data = review_resp.json()
        
        assert data["status"] == "approved", f"Expected approved, got {data['status']}"
        assert "reviewed_by" in data, "Missing reviewed_by"
        assert "reviewed_at" in data, "Missing reviewed_at"
        assert data["reviewed_by"] == ADMIN_USERNAME
        print(f"✓ Scan approved successfully by {data['reviewed_by']}")
    
    def test_approve_with_disease_correction(self, admin_session):
        """Admin can correct disease when approving"""
        # Create detection
        img_bytes = create_test_image()
        detect_resp = admin_session.post(
            f"{BASE_URL}/api/detect",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        assert detect_resp.status_code == 200
        detection = detect_resp.json()
        detection_id = detection["id"]
        original_disease = detection.get("ai_disease", detection.get("disease"))
        
        # Approve with correction
        corrected_disease = "Brown Rust"
        review_resp = admin_session.post(f"{BASE_URL}/api/admin/review/{detection_id}", json={
            "action": "approve",
            "disease": corrected_disease,
            "severity": "high"
        })
        assert review_resp.status_code == 200, f"Approve failed: {review_resp.text}"
        data = review_resp.json()
        
        assert data["status"] == "approved"
        assert data["disease"] == corrected_disease, f"Disease not corrected: {data['disease']}"
        assert data["severity"] == "high", f"Severity not updated: {data['severity']}"
        # Treatment should be updated based on corrected disease
        assert "treatment" in data
        print(f"✓ Disease corrected from '{original_disease}' to '{corrected_disease}'")
    
    def test_approve_with_suggestion(self, admin_session):
        """Admin can add suggestion when approving"""
        # Create detection
        img_bytes = create_test_image()
        detect_resp = admin_session.post(
            f"{BASE_URL}/api/detect",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        assert detect_resp.status_code == 200
        detection_id = detect_resp.json()["id"]
        
        # Approve with suggestion
        suggestion = "Apply fungicide within 3 days for best results"
        review_resp = admin_session.post(f"{BASE_URL}/api/admin/review/{detection_id}", json={
            "action": "approve",
            "suggestion": suggestion
        })
        assert review_resp.status_code == 200, f"Approve failed: {review_resp.text}"
        data = review_resp.json()
        
        assert data["status"] == "approved"
        assert data["admin_suggestion"] == suggestion, f"Suggestion not saved: {data.get('admin_suggestion')}"
        print(f"✓ Admin suggestion saved: '{suggestion[:30]}...'")
    
    def test_reject_scan(self, admin_session):
        """Admin can reject a scan"""
        # Create detection
        img_bytes = create_test_image()
        detect_resp = admin_session.post(
            f"{BASE_URL}/api/detect",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        assert detect_resp.status_code == 200
        detection_id = detect_resp.json()["id"]
        
        # Reject
        rejection_note = "Image quality too poor for accurate diagnosis"
        review_resp = admin_session.post(f"{BASE_URL}/api/admin/review/{detection_id}", json={
            "action": "reject",
            "suggestion": rejection_note
        })
        assert review_resp.status_code == 200, f"Reject failed: {review_resp.text}"
        data = review_resp.json()
        
        assert data["status"] == "rejected", f"Expected rejected, got {data['status']}"
        assert data["admin_suggestion"] == rejection_note
        assert data["reviewed_by"] == ADMIN_USERNAME
        print(f"✓ Scan rejected with note: '{rejection_note[:30]}...'")


class TestFarmerHistoryWithStatus:
    """Test farmer sees correct status in history"""
    
    def test_farmer_history_shows_pending_status(self):
        """Farmer history should show pending status for unreviewed scans"""
        # Create new farmer
        session = requests.Session()
        test_username = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}"
        reg_resp = session.post(f"{BASE_URL}/api/auth/register", json={
            "username": test_username,
            "password": "farmer123"
        })
        assert reg_resp.status_code == 200
        
        # Upload image
        img_bytes = create_test_image()
        detect_resp = session.post(
            f"{BASE_URL}/api/detect",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        assert detect_resp.status_code == 200
        detection = detect_resp.json()
        assert detection["status"] == "pending"
        
        # Check history
        history_resp = session.get(f"{BASE_URL}/api/history")
        assert history_resp.status_code == 200
        history = history_resp.json()
        
        assert len(history) > 0, "History should have at least one item"
        latest = history[0]
        assert latest["status"] == "pending", f"Expected pending, got {latest['status']}"
        print(f"✓ Farmer history shows pending status correctly")
    
    def test_farmer_history_shows_approved_with_details(self, admin_session):
        """After approval, farmer should see full details in history"""
        # Create new farmer
        farmer_session = requests.Session()
        test_username = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}"
        reg_resp = farmer_session.post(f"{BASE_URL}/api/auth/register", json={
            "username": test_username,
            "password": "farmer123"
        })
        assert reg_resp.status_code == 200
        
        # Upload image
        img_bytes = create_test_image()
        detect_resp = farmer_session.post(
            f"{BASE_URL}/api/detect",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        assert detect_resp.status_code == 200
        detection_id = detect_resp.json()["id"]
        
        # Admin approves with suggestion
        suggestion = "Test admin suggestion for farmer"
        review_resp = admin_session.post(f"{BASE_URL}/api/admin/review/{detection_id}", json={
            "action": "approve",
            "suggestion": suggestion
        })
        assert review_resp.status_code == 200
        
        # Farmer checks history
        history_resp = farmer_session.get(f"{BASE_URL}/api/history")
        assert history_resp.status_code == 200
        history = history_resp.json()
        
        # Find the approved item
        approved_item = next((h for h in history if h["id"] == detection_id), None)
        assert approved_item is not None, "Approved item not found in history"
        assert approved_item["status"] == "approved"
        assert "disease" in approved_item
        assert "treatment" in approved_item
        assert "syngenta_products" in approved_item
        assert approved_item["admin_suggestion"] == suggestion
        print(f"✓ Farmer sees approved scan with full details and admin suggestion")
    
    def test_farmer_history_shows_rejected_with_note(self, admin_session):
        """After rejection, farmer should see rejected status with admin note"""
        # Create new farmer
        farmer_session = requests.Session()
        test_username = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}"
        reg_resp = farmer_session.post(f"{BASE_URL}/api/auth/register", json={
            "username": test_username,
            "password": "farmer123"
        })
        assert reg_resp.status_code == 200
        
        # Upload image
        img_bytes = create_test_image()
        detect_resp = farmer_session.post(
            f"{BASE_URL}/api/detect",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        assert detect_resp.status_code == 200
        detection_id = detect_resp.json()["id"]
        
        # Admin rejects
        rejection_note = "Please upload a clearer image"
        review_resp = admin_session.post(f"{BASE_URL}/api/admin/review/{detection_id}", json={
            "action": "reject",
            "suggestion": rejection_note
        })
        assert review_resp.status_code == 200
        
        # Farmer checks history
        history_resp = farmer_session.get(f"{BASE_URL}/api/history")
        assert history_resp.status_code == 200
        history = history_resp.json()
        
        # Find the rejected item
        rejected_item = next((h for h in history if h["id"] == detection_id), None)
        assert rejected_item is not None, "Rejected item not found in history"
        assert rejected_item["status"] == "rejected"
        assert rejected_item["admin_suggestion"] == rejection_note
        print(f"✓ Farmer sees rejected scan with admin note")


class TestAccessControl:
    """Test access control for admin endpoints"""
    
    def test_regular_user_cannot_access_pending(self):
        """Regular user cannot access /api/admin/pending"""
        session = requests.Session()
        test_username = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}"
        
        # Register
        reg_resp = session.post(f"{BASE_URL}/api/auth/register", json={
            "username": test_username,
            "password": "user123"
        })
        assert reg_resp.status_code == 200
        
        # Try to access pending
        response = session.get(f"{BASE_URL}/api/admin/pending")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Regular user cannot access /api/admin/pending")
    
    def test_regular_user_cannot_review(self):
        """Regular user cannot access /api/admin/review/{id}"""
        session = requests.Session()
        test_username = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}"
        
        # Register
        reg_resp = session.post(f"{BASE_URL}/api/auth/register", json={
            "username": test_username,
            "password": "user123"
        })
        assert reg_resp.status_code == 200
        
        # Try to review
        response = session.post(f"{BASE_URL}/api/admin/review/any-id", json={
            "action": "approve"
        })
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Regular user cannot access /api/admin/review")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
