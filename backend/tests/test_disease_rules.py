"""
Unit tests for Backend Disease Rules Engine and Model+Rule Combination.

Tests domain rules:
- Red Rot: Leaf midrib turns red, with red and white patches inside the stem.
- Mosaic: Leaves develop irregular light-green and dark-green patches.
- Brown Rust: Small reddish-brown pustules appear on the leaf surface.
"""

import pytest
import numpy as np
from PIL import Image, ImageDraw
import io
import sys
from pathlib import Path

# Ensure backend is on sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from disease_rules import (
    evaluate_rules,
    combine_model_and_rules,
    combine_ensemble_models_and_rules,
    generate_rule_overlay,
    DISEASE_COLORS
)


def create_red_rot_image():
    """Generates synthetic leaf with red midrib and white internal patches."""
    img = np.zeros((256, 256, 3), dtype=np.uint8)
    img[:, :] = [35, 130, 40]  # Green leaf
    img[:, 118:138] = [195, 25, 25]  # Red midrib
    img[70:120, 122:134] = [235, 230, 225]  # White patch inside red midrib
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, format="PNG")
    return buf.getvalue(), Image.fromarray(img)


def create_mosaic_image():
    """Generates synthetic leaf with irregular light-green and dark-green patches."""
    img = np.zeros((256, 256, 3), dtype=np.uint8)
    img[:, :] = [25, 95, 30]  # Dark green background
    # Add multiple irregular light-green chlorotic islands
    for y in range(25, 235, 35):
        for x in range(25, 235, 35):
            img[y:y+22, x:x+22] = [165, 220, 65]  # Light yellow-green patches
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, format="PNG")
    return buf.getvalue(), Image.fromarray(img)


def create_brown_rust_image():
    """Generates synthetic leaf with small reddish-brown pustules on leaf surface."""
    img = np.zeros((256, 256, 3), dtype=np.uint8)
    img[:, :] = [45, 135, 45]  # Green leaf
    np.random.seed(101)
    for _ in range(45):
        y = np.random.randint(15, 235)
        x = np.random.randint(15, 235)
        img[y:y+4, x:x+6] = [175, 75, 25]  # Reddish-brown pustule
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, format="PNG")
    return buf.getvalue(), Image.fromarray(img)


def create_healthy_image():
    """Generates synthetic clean, uniform healthy green leaf."""
    img = np.zeros((256, 256, 3), dtype=np.uint8)
    img[:, :] = [40, 150, 40]  # Uniform green
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, format="PNG")
    return buf.getvalue(), Image.fromarray(img)


class TestDiseaseRulesEngine:
    def test_red_rot_rule_detection(self):
        """Rule: Leaf midrib turns red, with red and white patches inside the stem."""
        _, img = create_red_rot_image()
        result = evaluate_rules(img)
        assert result["top_disease"] == "Red Rot"
        assert result["scores"]["Red Rot"] > 0.5
        assert result["details"]["Red Rot"]["is_elongated_midrib"] is True
        assert result["details"]["Red Rot"]["has_red_white_patches"] is True

    def test_mosaic_rule_detection(self):
        """Rule: Leaves develop irregular light-green and dark-green patches."""
        _, img = create_mosaic_image()
        result = evaluate_rules(img)
        assert result["top_disease"] == "Mosaic"
        assert result["scores"]["Mosaic"] > 0.5
        assert result["details"]["Mosaic"]["light_green_ratio"] > 0.1
        assert result["details"]["Mosaic"]["dark_green_ratio"] > 0.1

    def test_brown_rust_rule_detection(self):
        """Rule: Small reddish-brown pustules appear on the leaf surface."""
        _, img = create_brown_rust_image()
        result = evaluate_rules(img)
        assert result["top_disease"] == "Brown Rust"
        assert result["scores"]["Brown Rust"] > 0.4
        assert result["details"]["Brown Rust"]["pustule_count"] >= 5

    def test_healthy_leaf_rule_detection(self):
        """Uniform green leaf with no symptoms should evaluate as Healthy."""
        _, img = create_healthy_image()
        result = evaluate_rules(img)
        assert result["top_disease"] == "Healthy"
        assert result["is_healthy"] is True


class TestModelRulesCombination:
    def test_rescues_unrecognized_when_rule_fires(self):
        """When UNet fails / returns None, rules identify the disease."""
        bytes_data, _ = create_red_rot_image()
        unet_failed = {"disease": None, "severity": "low", "affected_percent": 0.0, "overlay_bytes": None}
        combined = combine_model_and_rules(unet_failed, bytes_data)
        assert combined["disease"] == "Red Rot"
        assert combined["backend_source"] == "rule_fallback"
        assert combined["overlay_bytes"] is not None

    def test_corrects_wrong_prediction(self):
        """When UNet predicts wrong disease (e.g. Mosaic on Red Rot leaf), rule corrects it."""
        bytes_data, _ = create_red_rot_image()
        unet_wrong = {"disease": "Mosaic", "severity": "low", "affected_percent": 3.0, "overlay_bytes": None}
        combined = combine_model_and_rules(unet_wrong, bytes_data)
        assert combined["disease"] == "Red Rot"
        assert combined["backend_source"] == "rule_correction"

    def test_confirms_correct_prediction(self):
        """When UNet and rules agree, prediction is confirmed."""
        bytes_data, _ = create_brown_rust_image()
        unet_correct = {"disease": "Brown Rust", "severity": "medium", "affected_percent": 8.0, "overlay_bytes": b"fake_overlay"}
        combined = combine_model_and_rules(unet_correct, bytes_data)
        assert combined["disease"] == "Brown Rust"
        assert combined["backend_source"] == "model_confirmed"

    def test_overlay_generation_format(self):
        """Overlay produced by rules should match JPEG format."""
        _, img = create_mosaic_image()
        mask = np.zeros((256, 256), dtype=np.uint8)
        mask[50:150, 50:150] = 255
        overlay = generate_rule_overlay(img, "Mosaic", mask)
        assert len(overlay) > 100
        # Check it is valid image bytes
        loaded = Image.open(io.BytesIO(overlay))
        assert loaded.size == img.size


class TestTwoModelEnsemble:
    def test_both_models_agree(self):
        """When both UNet and EfficientNet predict the same disease, output is confirmed."""
        bytes_data, _ = create_brown_rust_image()
        unet_res = {"disease": "Brown Rust", "class_probs": {"Brown Rust": 0.8, "Mosaic": 0.05, "Red Rot": 0.05}, "severity": "medium", "affected_percent": 12.0, "overlay_bytes": b"unet_overlay"}
        eff_res = {"disease": "Brown Rust", "class_probs": {"Brown Rust": 0.95, "Mosaic": 0.02, "Red Rot": 0.03}, "confidence": 0.95}
        combined = combine_ensemble_models_and_rules(unet_res, eff_res, bytes_data)
        assert combined["disease"] == "Brown Rust"
        assert combined["backend_source"] == "both_models_confirmed"

    def test_efficientnet_rescues_low_confidence_unet(self):
        """When UNet has low pixel count but EfficientNet detects disease, combination outputs disease."""
        bytes_data, _ = create_mosaic_image()
        unet_res = {"disease": None, "class_probs": {"Brown Rust": 0.0, "Mosaic": 0.15, "Red Rot": 0.0}, "severity": "low", "affected_percent": 0.0, "overlay_bytes": None}
        eff_res = {"disease": "Mosaic", "class_probs": {"Brown Rust": 0.05, "Mosaic": 0.88, "Red Rot": 0.04}, "confidence": 0.88}
        combined = combine_ensemble_models_and_rules(unet_res, eff_res, bytes_data)
        assert combined["disease"] == "Mosaic"
        assert combined["overlay_bytes"] is not None

    def test_rules_resolve_conflict_between_models(self):
        """When UNet and EfficientNet disagree, backend rules resolve to the visually correct disease."""
        bytes_data, _ = create_red_rot_image()
        # UNet mistakenly predicted Brown Rust, EfficientNet predicted Red Rot
        unet_res = {"disease": "Brown Rust", "class_probs": {"Brown Rust": 0.45, "Mosaic": 0.1, "Red Rot": 0.3}, "severity": "low", "affected_percent": 2.0, "overlay_bytes": None}
        eff_res = {"disease": "Red Rot", "class_probs": {"Brown Rust": 0.4, "Mosaic": 0.05, "Red Rot": 0.6}, "confidence": 0.6}
        combined = combine_ensemble_models_and_rules(unet_res, eff_res, bytes_data)
        # Visually this is a Red Rot leaf (red midrib with white patch)
        assert combined["disease"] == "Red Rot"

    def test_non_sugarcane_leaf_or_pest_rejected_as_unrecognized(self):
        """Non-sugarcane leaf images (like insects/white grubs on white background) must be rejected as Unrecognized."""
        # Create an image dominated by white background (80%) with a tan/brown insect-like shape
        img = Image.new("RGB", (256, 256), color=(250, 250, 250))
        draw = ImageDraw.Draw(img)
        # Tan/yellowish curved blob (insect)
        draw.ellipse([60, 60, 180, 200], fill=(230, 200, 150))
        # Reddish head
        draw.ellipse([140, 50, 190, 100], fill=(160, 60, 30))
        
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        bytes_data = buf.getvalue()
        
        # Even if models had low noisy predictions:
        unet_res = {"disease": None, "confidence": 0.0, "class_probs": {"Brown Rust": 0.2, "Mosaic": 0.05, "Red Rot": 0.1}, "severity": "low", "affected_percent": 0.0, "overlay_bytes": None}
        eff_res = {"disease": "Brown Rust", "confidence": 0.58, "class_probs": {"Brown Rust": 0.58, "Mosaic": 0.12, "Red Rot": 0.51}}
        
        combined = combine_ensemble_models_and_rules(unet_res, eff_res, bytes_data)
        assert combined["disease"] == "Unrecognized"
        assert combined["is_co_infection"] is False
        assert combined["overlay_bytes"] is None
        assert combined["backend_source"] == "non_sugarcane_leaf_or_object"

