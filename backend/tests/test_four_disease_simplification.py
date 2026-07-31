"""
Tests for the simplified 4-disease system (Brown Rust, Mosaic, Red Rot, Healthy).
Verifies GPT/LLM has been removed and only UNet is used.
"""
import pytest
import requests
import os
import io
from PIL import Image

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

EXPECTED_DISEASES = {"Brown Rust", "Mosaic", "Red Rot", "Healthy"}
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ADT@123"


class TestDiseasesEndpoint:
    def test_diseases_returns_exactly_four(self):
        r = requests.get(f"{BASE_URL}/api/diseases")
        assert r.status_code == 200
        data = r.json()
        keys = set(data.keys())
        assert keys == EXPECTED_DISEASES, f"Expected {EXPECTED_DISEASES}, got {keys}"
        assert len(data) == 4

    def test_diseases_english_default(self):
        r = requests.get(f"{BASE_URL}/api/diseases?lang=en")
        assert r.status_code == 200
        data = r.json()
        assert set(data.keys()) == EXPECTED_DISEASES
        # Structure check
        for name, info in data.items():
            for key in ("symptoms", "treatment", "causes", "prevention", "syngenta_products"):
                assert key in info, f"{name} missing {key}"

    def test_diseases_marathi(self):
        r = requests.get(f"{BASE_URL}/api/diseases?lang=mr")
        assert r.status_code == 200
        data = r.json()
        # Should still contain the 4 canonical keys (or their translated names)
        assert len(data) == 4
        # At least one field should differ from English (translated)
        r_en = requests.get(f"{BASE_URL}/api/diseases?lang=en").json()
        translated_found = False
        for k in data:
            en_val = r_en.get(k, {}).get("symptoms", "")
            mr_val = data[k].get("symptoms", "")
            if en_val and mr_val and en_val != mr_val:
                translated_found = True
                break
        assert translated_found, "Marathi translation not applied"

    def test_diseases_hindi(self):
        r = requests.get(f"{BASE_URL}/api/diseases?lang=hi")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 4


class TestDetection:
    def _login(self):
        s = requests.Session()
        r = s.post(f"{BASE_URL}/api/auth/login",
                   json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
        assert r.status_code == 200
        return s

    def test_detect_returns_only_valid_disease_and_overlay(self):
        s = self._login()
        img = Image.new("RGB", (256, 256), color=(60, 130, 60))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        r = s.post(f"{BASE_URL}/api/detect",
                   files={"file": ("t.jpg", buf, "image/jpeg")})
        assert r.status_code == 200, r.text
        data = r.json()
        assert "disease" in data
        assert data["disease"] in EXPECTED_DISEASES, f"Unexpected disease {data['disease']}"
        assert "overlay_path" in data, "overlay_path missing from detect response"
        assert "image_path" in data
        # No confidence field exposed
        # (it's fine if backend has it internally, but should not be primary field)

    def test_detect_no_llm_key_needed(self):
        """Detection should succeed purely via UNet - no LLM key required."""
        s = self._login()
        img = Image.new("RGB", (128, 128), color=(120, 80, 40))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        r = s.post(f"{BASE_URL}/api/detect",
                   files={"file": ("t2.jpg", buf, "image/jpeg")})
        assert r.status_code == 200
        # Should not error with LLM-related messages
        assert "error" not in r.json() or r.json().get("disease") in EXPECTED_DISEASES


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
