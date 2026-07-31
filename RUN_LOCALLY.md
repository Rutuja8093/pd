# Running this project on localhost

This is a FastAPI + React + MongoDB app (built with Emergent) for sugarcane
disease detection. Here's what was changed so it runs locally, and what you
still need to do yourself.

## What I changed

1. **`backend/.env`** (new) — sets `MONGO_URL`, `DB_NAME`, `JWT_SECRET`,
   admin credentials, and `CORS_ORIGINS=http://localhost:3000`.
2. **`frontend/.env`** (new) — sets `REACT_APP_BACKEND_URL=http://localhost:8001`
   so the React app calls your local backend instead of nothing/production.
3. **`backend/server.py`** — the app originally stored uploaded images using
   Emergent's hosted object storage service, which requires an
   `EMERGENT_LLM_KEY` tied to an Emergent account. I added a local-disk
   fallback: if `EMERGENT_LLM_KEY` is not set, uploaded/overlay images are
   saved under `backend/local_storage/` instead. This is what lets the app
   run fully offline/locally. If you *do* have an Emergent key, put it in
   `backend/.env` and it'll use the hosted storage as originally designed.
4. Added `backend/run_local.sh` and `frontend/run_local.sh` helper scripts.

## Things I could NOT fix for you

- **The trained model file is missing.** `backend/models/best_unet.pth` is
  in `.gitignore` in this repo (it's a binary weights file, never included
  in the zip/export). Without it, `/detect` will run but always return
  `"Unrecognized"` for every image, since the segmentation model never
  loads. If you have this file, place it at `backend/models/best_unet.pth`.
- **MongoDB** must be installed and running locally — this isn't something
  a code change can provide. See below.

## Prerequisites

- Python 3.11
- Node.js 18+ and Yarn (`npm install -g yarn`)
- MongoDB running locally on port 27017

### Install MongoDB (if you don't have it)

macOS: `brew tap mongodb/brew && brew install mongodb-community && brew services start mongodb-community`

Ubuntu/Debian: see https://www.mongodb.com/docs/manual/administration/install-on-linux/
(or use Docker: `docker run -d -p 27017:27017 --name mongo mongo:7`)

## Run it

**Terminal 1 — backend:**
```bash
cd backend
./run_local.sh
```
This creates a venv, installs `requirements.txt` (large — includes
PyTorch, so it can take a while), and starts the API at
http://localhost:8001.

**Terminal 2 — frontend:**
```bash
cd frontend
./run_local.sh
```
This installs npm packages and starts the React dev server at
http://localhost:3000.

Then open **http://localhost:3000** in your browser. Log in with
`admin` / `ADT@123` (from `backend/.env`) for admin access, or register a
new farmer account.

## Notes

- `requirements.txt` includes a lot of NVIDIA/CUDA packages even if you
  don't have a GPU — pip will still install them (they're just Python
  packages), it'll just take longer and use more disk space. The app runs
  fine on CPU.
- If port 8001 or 3000 is already in use on your machine, change the port
  in `backend/run_local.sh` (and update `REACT_APP_BACKEND_URL` in
  `frontend/.env` to match) or in `frontend/.env`'s `PORT` variable.
