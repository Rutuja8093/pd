"""Test UNet overlay generation and admin approval flow with overlay_path"""
import pytest
import requests
import os
import io
import uuid
from PIL import Image

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ADT@123"


def create_test_image(color='green', size=(400, 400)):
    img = Image.new('RGB', size, color=color)
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf


@pytest.fixture(scope="module")
def admin_session():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, r.text
    return s


@pytest.fixture(scope="module")
def farmer_session():
    s = requests.Session()
    uname = f"TEST_farmer_{uuid.uuid4().hex[:8]}"
    r = s.post(f"{BASE_URL}/api/auth/register", json={"username": uname, "password": "farm123"})
    assert r.status_code == 200, r.text
    return s, uname


class TestUNetDetection:
    def test_detect_returns_overlay_path(self, admin_session):
        """POST /api/detect returns overlay_path field"""
        img = create_test_image()
        r = admin_session.post(f"{BASE_URL}/api/detect", files={"file": ("t.jpg", img, "image/jpeg")})
        assert r.status_code == 200, r.text
        data = r.json()
        assert "overlay_path" in data, "Missing overlay_path field"
        assert "ai_disease" in data
        assert data["status"] == "pending"
        print(f"overlay_path={data.get('overlay_path')!r}, ai_disease={data.get('ai_disease')}")
        return data

    def test_overlay_file_accessible(self, admin_session):
        """When overlay_path is present, the file endpoint returns image"""
        img = create_test_image(color='brown')
        r = admin_session.post(f"{BASE_URL}/api/detect", files={"file": ("t.jpg", img, "image/jpeg")})
        assert r.status_code == 200
        overlay = r.json().get("overlay_path")
        if not overlay:
            pytest.skip("No overlay produced for this image")
        fr = admin_session.get(f"{BASE_URL}/api/files/{overlay}")
        assert fr.status_code == 200, f"Overlay file fetch failed: {fr.status_code}"
        assert fr.headers.get("content-type", "").startswith("image/"), fr.headers
        assert len(fr.content) > 100
        print(f"Overlay file ok ({len(fr.content)} bytes)")


class TestAdminPendingHasOverlay:
    def test_pending_items_have_overlay_path(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/admin/pending")
        assert r.status_code == 200
        items = r.json()
        if not items:
            pytest.skip("no pending")
        # Verify structure
        it = items[0]
        assert "image_path" in it
        # overlay_path may exist as empty string for older items
        assert "overlay_path" in it, f"pending item missing overlay_path: {list(it.keys())}"
        print(f"pending[0] has overlay_path={it.get('overlay_path')!r}")


class TestHistoryHasOverlay:
    def test_history_returns_overlay_path(self, admin_session):
        # Create a fresh detection
        img = create_test_image()
        admin_session.post(f"{BASE_URL}/api/detect", files={"file": ("t.jpg", img, "image/jpeg")})
        r = admin_session.get(f"{BASE_URL}/api/history")
        assert r.status_code == 200
        h = r.json()
        assert isinstance(h, list) and len(h) > 0
        assert "overlay_path" in h[0], f"history missing overlay_path: {list(h[0].keys())}"
        print(f"history[0] overlay_path={h[0].get('overlay_path')!r}")


class TestApproveKeepsOverlay:
    def test_approve_preserves_overlay(self, admin_session, farmer_session):
        session, uname = farmer_session
        img = create_test_image()
        r = session.post(f"{BASE_URL}/api/detect", files={"file": ("t.jpg", img, "image/jpeg")})
        assert r.status_code == 200
        did = r.json()["id"]
        original_overlay = r.json().get("overlay_path")

        rr = admin_session.post(f"{BASE_URL}/api/admin/review/{did}", json={"action": "approve"})
        assert rr.status_code == 200
        approved = rr.json()
        assert approved["status"] == "approved"
        # overlay preserved
        assert approved.get("overlay_path") == original_overlay, "overlay_path changed after approve"

        # farmer sees it in history
        hr = session.get(f"{BASE_URL}/api/history")
        assert hr.status_code == 200
        item = next((h for h in hr.json() if h["id"] == did), None)
        assert item is not None
        assert item["status"] == "approved"
        assert item.get("overlay_path") == original_overlay
        print(f"Approved item retains overlay_path={original_overlay!r}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
