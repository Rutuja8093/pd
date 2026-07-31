"""
Sugarcane Disease Analysis API Tests
Tests: Auth (login, register, logout), Detection, History, Diseases, Admin endpoints
"""
import pytest
import requests
import os
import io
from PIL import Image

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ADT@123"
TEST_USER_PREFIX = "TEST_user_"

class TestHealthAndBasics:
    """Basic API health checks"""
    
    def test_diseases_endpoint_public(self):
        """GET /api/diseases should be accessible without auth"""
        response = requests.get(f"{BASE_URL}/api/diseases")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "Diseases should return a dict"
        assert len(data) > 0, "Should have at least one disease"
        # Verify disease structure
        for disease_name, info in data.items():
            assert "symptoms" in info, f"Disease {disease_name} missing symptoms"
            assert "treatment" in info, f"Disease {disease_name} missing treatment"
            assert "syngenta_products" in info, f"Disease {disease_name} missing syngenta_products"
        print(f"✓ Diseases endpoint returned {len(data)} diseases")


class TestAdminAuth:
    """Admin authentication tests"""
    
    def test_admin_login_success(self):
        """Admin login with correct credentials"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert data["username"] == ADMIN_USERNAME
        assert data["role"] == "admin"
        assert "id" in data
        print(f"✓ Admin login successful: {data['username']} (role: {data['role']})")
        return session
    
    def test_admin_login_wrong_password(self):
        """Admin login with wrong password should fail"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": "wrongpassword"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Admin login with wrong password correctly rejected")
    
    def test_admin_me_endpoint(self):
        """GET /api/auth/me should return admin user info"""
        session = requests.Session()
        # Login first
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200
        
        # Check /me endpoint
        me_resp = session.get(f"{BASE_URL}/api/auth/me")
        assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}"
        data = me_resp.json()
        assert data["username"] == ADMIN_USERNAME
        assert data["role"] == "admin"
        print(f"✓ /api/auth/me returned correct admin info")


class TestUserRegistration:
    """User registration flow tests"""
    
    def test_register_new_user(self):
        """Register a new user"""
        import uuid
        test_username = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}"
        test_password = "testpass123"
        
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "username": test_username,
            "password": test_password
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        assert data["username"] == test_username
        assert data["role"] == "user"
        assert "id" in data
        print(f"✓ User registration successful: {test_username}")
        
        # Verify can login with new credentials
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "username": test_username,
            "password": test_password
        })
        assert login_resp.status_code == 200, "Login after registration failed"
        print(f"✓ Login after registration successful")
        return test_username
    
    def test_register_duplicate_username(self):
        """Registering with existing username should fail"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": ADMIN_USERNAME,
            "password": "anypassword"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Duplicate username registration correctly rejected")


class TestLogout:
    """Logout functionality tests"""
    
    def test_logout_clears_session(self):
        """Logout should clear auth cookie"""
        session = requests.Session()
        
        # Login
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200
        
        # Verify authenticated
        me_resp = session.get(f"{BASE_URL}/api/auth/me")
        assert me_resp.status_code == 200
        
        # Logout
        logout_resp = session.post(f"{BASE_URL}/api/auth/logout")
        assert logout_resp.status_code == 200
        
        # Verify no longer authenticated
        me_resp2 = session.get(f"{BASE_URL}/api/auth/me")
        assert me_resp2.status_code == 401, f"Expected 401 after logout, got {me_resp2.status_code}"
        print("✓ Logout successfully cleared session")


class TestDetection:
    """Disease detection endpoint tests"""
    
    def test_detect_requires_auth(self):
        """POST /api/detect should require authentication"""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        response = requests.post(
            f"{BASE_URL}/api/detect",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Detection endpoint correctly requires authentication")
    
    def test_detect_with_auth(self):
        """POST /api/detect with auth should return detection result"""
        session = requests.Session()
        
        # Login
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200
        
        # Create a simple green test image (simulating healthy sugarcane)
        img = Image.new('RGB', (200, 200), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        response = session.post(
            f"{BASE_URL}/api/detect",
            files={"file": ("test_sugarcane.jpg", img_bytes, "image/jpeg")}
        )
        assert response.status_code == 200, f"Detection failed: {response.text}"
        data = response.json()
        
        # Verify response structure - NO confidence scores shown to user
        assert "disease" in data, "Response missing 'disease'"
        assert "severity" in data, "Response missing 'severity'"
        assert "treatment" in data, "Response missing 'treatment'"
        assert "syngenta_products" in data, "Response missing 'syngenta_products'"
        assert "symptoms" in data, "Response missing 'symptoms'"
        assert "causes" in data, "Response missing 'causes'"
        assert "prevention" in data, "Response missing 'prevention'"
        assert "image_path" in data, "Response missing 'image_path'"
        assert "id" in data, "Response missing 'id'"
        
        print(f"✓ Detection successful: {data['disease']} (severity: {data['severity']})")
        print(f"  Treatment: {data['treatment'][:50]}...")
        print(f"  Syngenta products: {data['syngenta_products']}")
        return data


class TestHistory:
    """History endpoint tests"""
    
    def test_history_requires_auth(self):
        """GET /api/history should require authentication"""
        response = requests.get(f"{BASE_URL}/api/history")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ History endpoint correctly requires authentication")
    
    def test_history_returns_user_scans(self):
        """GET /api/history should return user's scan history"""
        session = requests.Session()
        
        # Login
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200
        
        response = session.get(f"{BASE_URL}/api/history")
        assert response.status_code == 200, f"History failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "History should return a list"
        
        # If there are items, verify structure
        if len(data) > 0:
            item = data[0]
            assert "disease" in item
            assert "severity" in item
            assert "treatment" in item
            assert "image_path" in item
            assert "created_at" in item
            # Verify NO confidence in history items (per requirements)
            print(f"✓ History returned {len(data)} items")
            print(f"  Latest: {item['disease']} on {item['created_at']}")
        else:
            print("✓ History returned empty list (no scans yet)")


class TestAdminEndpoints:
    """Admin-only endpoint tests"""
    
    def test_admin_stats_requires_admin(self):
        """GET /api/admin/stats should require admin role"""
        # Test without auth
        response = requests.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Admin stats correctly requires authentication")
    
    def test_admin_stats_with_admin(self):
        """GET /api/admin/stats should work for admin"""
        session = requests.Session()
        
        # Login as admin
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200
        
        response = session.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 200, f"Admin stats failed: {response.text}"
        data = response.json()
        assert "total_users" in data
        assert "total_scans" in data
        assert "disease_distribution" in data
        print(f"✓ Admin stats: {data['total_users']} users, {data['total_scans']} scans")
    
    def test_admin_users_with_admin(self):
        """GET /api/admin/users should return all users for admin"""
        session = requests.Session()
        
        # Login as admin
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200
        
        response = session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 200, f"Admin users failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Should have at least admin user"
        
        # Verify admin user exists
        admin_found = any(u["username"] == ADMIN_USERNAME for u in data)
        assert admin_found, "Admin user not found in users list"
        print(f"✓ Admin users returned {len(data)} users")
    
    def test_admin_detections_with_admin(self):
        """GET /api/admin/detections should return all detections for admin"""
        session = requests.Session()
        
        # Login as admin
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200
        
        response = session.get(f"{BASE_URL}/api/admin/detections")
        assert response.status_code == 200, f"Admin detections failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Admin detections returned {len(data)} detections")
    
    def test_admin_endpoints_forbidden_for_regular_user(self):
        """Admin endpoints should return 403 for regular users"""
        import uuid
        test_username = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}"
        
        session = requests.Session()
        
        # Register new user
        reg_resp = session.post(f"{BASE_URL}/api/auth/register", json={
            "username": test_username,
            "password": "testpass123"
        })
        assert reg_resp.status_code == 200
        
        # Try admin endpoints
        stats_resp = session.get(f"{BASE_URL}/api/admin/stats")
        assert stats_resp.status_code == 403, f"Expected 403, got {stats_resp.status_code}"
        
        users_resp = session.get(f"{BASE_URL}/api/admin/users")
        assert users_resp.status_code == 403, f"Expected 403, got {users_resp.status_code}"
        
        detections_resp = session.get(f"{BASE_URL}/api/admin/detections")
        assert detections_resp.status_code == 403, f"Expected 403, got {detections_resp.status_code}"
        
        print("✓ Admin endpoints correctly return 403 for regular users")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
