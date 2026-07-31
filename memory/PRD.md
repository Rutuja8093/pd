# SUGARCANE AI - Product Requirements Document

## Problem Statement
Sugarcane disease analysis website using UNet segmentation model. Full Disease Library with 23 diseases/pests management practices.

## Core Features
- **UNet Detection**: 3 diseases (Brown Rust, Mosaic, Red Rot) + Unrecognized fallback
- **Disease Library**: 23 diseases with 5 practice categories, hero banner, animated UI
- **Admin Panel**: Pending Reviews, Reviewed, Overview, Users (from DB), All Scans, ZIP download
- **Admin Approval Workflow**: Farmer uploads → Pending → Admin reviews/suggests → Farmer sees result
- **Multilingual**: English, Hindi, Marathi (UI + disease data)
- **Segmentation Overlay**: Colored overlay on detected images
- **No AI/LLM** — pure PyTorch UNet inference
- **No product recommendations** (Azoxystrobin etc. removed)

## Architecture
- Frontend: React + TailwindCSS + lucide-react + framer-motion + i18next
- Backend: FastAPI + MongoDB + segmentation_models_pytorch (UNet/ResNet34)
- Model: best_unet.pth (94MB, 4 classes)

## Backlog
- P2: Camera capture for mobile users
- P2: Backend refactoring (split server.py)
