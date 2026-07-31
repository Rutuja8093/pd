# AWS Deployment Guide - SugarCane AI Disease Detection

## Quick Start (Simplest Way)

### What You Need
- AWS Account
- Your GitHub repo: `https://github.com/sankalpkhatake07/SUGARCANE_AI`
- Your Emergent LLM Key (from your Emergent profile)

---

## Option 1: AWS EC2 (Recommended - Simplest)

### Step 1: Launch EC2 Instance

1. Go to **AWS Console** → **EC2** → **Launch Instance**
2. Settings:
   - **Name**: `sugarcane-ai`
   - **AMI**: Ubuntu 24.04 LTS
   - **Instance type**: `t3.medium` (4GB RAM, enough for your 6.5MB YOLO model)
     - *If you want GPU for faster YOLO*: use `g4dn.xlarge` (~$380/month)
   - **Key pair**: Create or select existing
   - **Security Group**: Allow ports **22** (SSH), **80** (HTTP), **443** (HTTPS)
   - **Storage**: 30 GB

3. Click **Launch Instance**

### Step 2: Connect to Your Server

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Step 3: Install Everything

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python, Node.js, MongoDB, Nginx
sudo apt install -y python3.11 python3.11-venv python3-pip nginx git curl

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
npm install -g yarn

# Install MongoDB
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Step 4: Clone Your Code

```bash
cd /home/ubuntu
git clone https://github.com/sankalpkhatake07/SUGARCANE_AI.git
cd SUGARCANE_AI
```

### Step 5: Setup Backend

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cat > .env << 'EOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=sugarcane_db
EMERGENT_LLM_KEY=YOUR_EMERGENT_KEY_HERE
JWT_SECRET=your-random-secret-change-this-to-something-long
ADMIN_USERNAME=admin
ADMIN_PASSWORD=ADT@123
EOF

# Test backend starts
uvicorn server:app --host 0.0.0.0 --port 8001
# Press Ctrl+C after confirming it works
```

### Step 6: Setup Frontend

```bash
cd /home/ubuntu/SUGARCANE_AI/frontend

# Install dependencies
yarn install

# Configure environment - replace YOUR_DOMAIN with your EC2 IP or domain
cat > .env << 'EOF'
REACT_APP_BACKEND_URL=http://YOUR_EC2_PUBLIC_IP
EOF

# Build for production
yarn build
```

### Step 7: Configure Nginx

```bash
sudo cat > /etc/nginx/sites-available/sugarcane << 'EOF'
server {
    listen 80;
    server_name _;

    # Frontend (React build)
    location / {
        root /home/ubuntu/SUGARCANE_AI/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 50M;
    }

    # File uploads
    location /api/files/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/sugarcane /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Step 8: Run Backend as a Service

```bash
sudo cat > /etc/systemd/system/sugarcane-backend.service << 'EOF'
[Unit]
Description=SugarCane AI Backend
After=network.target mongod.service

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/SUGARCANE_AI/backend
Environment=PATH=/home/ubuntu/SUGARCANE_AI/backend/venv/bin
ExecStart=/home/ubuntu/SUGARCANE_AI/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start sugarcane-backend
sudo systemctl enable sugarcane-backend
```

### Step 9: Verify

```bash
# Check everything is running
sudo systemctl status sugarcane-backend
sudo systemctl status nginx
sudo systemctl status mongod

# Test API
curl http://localhost:8001/api/diseases
```

Now open **http://YOUR_EC2_PUBLIC_IP** in your browser!

---

## Step 10: Add HTTPS / Custom Domain (Optional)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get free SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is set up automatically
```

After adding a domain, update `frontend/.env`:
```
REACT_APP_BACKEND_URL=https://yourdomain.com
```
Then rebuild: `cd frontend && yarn build`

---

## Cost Estimate

| Instance Type | RAM | Cost/Month | Best For |
|---|---|---|---|
| `t3.micro` (free tier) | 1GB | Free (1yr) | Testing only |
| `t3.medium` | 4GB | ~$30 | Production (CPU YOLO) |
| `t3.large` | 8GB | ~$60 | Production (larger traffic) |
| `g4dn.xlarge` (GPU) | 16GB | ~$380 | Fast GPU YOLO inference |

**Your model is only 6.5MB** — `t3.medium` is more than enough!

---

## Important Notes

1. **Replace these values** before deploying:
   - `YOUR_EC2_PUBLIC_IP` → Your actual EC2 public IP
   - `YOUR_EMERGENT_KEY_HERE` → Your Emergent LLM Key (Profile → Universal Key)
   - `your-random-secret-change-this-to-something-long` → Any random string for JWT

2. **Security**: 
   - Never commit `.env` files to GitHub
   - Use AWS Security Groups to restrict access
   - Enable HTTPS with Certbot for production

3. **Monitoring**:
   ```bash
   # View backend logs
   sudo journalctl -u sugarcane-backend -f
   
   # View nginx logs
   sudo tail -f /var/log/nginx/error.log
   ```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Backend won't start | Check logs: `sudo journalctl -u sugarcane-backend -n 50` |
| MongoDB connection error | `sudo systemctl restart mongod` |
| 502 Bad Gateway | Backend not running: `sudo systemctl restart sugarcane-backend` |
| Images not uploading | Check nginx `client_max_body_size` (set to 50M) |
| YOLO model error | Verify `backend/models/best.pt` exists (6.5MB) |
