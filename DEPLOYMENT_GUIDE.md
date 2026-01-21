# Complete Deployment Guide for ANPR Project

## 🚀 Recommended Server: **Render.com** (Free Tier Available)

**Why Render.com is Best for This Project:**
- ✅ Handles large Python ML dependencies (PyTorch, OpenCV)
- ✅ No file size limits like Vercel
- ✅ 512 MB RAM on free tier (sufficient for your app)
- ✅ Persistent storage for model files
- ✅ No timeout issues for video processing
- ✅ Simple GitHub integration
- ✅ Free SSL certificate included

---

## 📋 Step-by-Step Deployment on Render.com

### Step 1: Prepare Your Project

1. **Update `.gitignore` to exclude model files:**
   ```bash
   # Add to .gitignore
   *.pt
   *.pth
   yolov8n.pt
   license_plate_detector.pt
   ```

2. **Remove model files from Git (if already committed):**
   ```bash
   git rm --cached yolov8n.pt license_plate_detector.pt
   git add .gitignore
   git commit -m "Remove large model files"
   git push origin main
   ```

### Step 2: Create Render Account

1. Go to https://render.com
2. Click **"Get Started"**
3. Sign up with GitHub (recommended) or email
4. Verify your email

### Step 3: Deploy Your Application

#### Option A: Deploy via Dashboard (Easiest)

1. **Connect Your Repository:**
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub account
   - Select repository: `kishanpatel486630/Car_Numberplate_Detaction_Project_COD`
   - Click **"Connect"**

2. **Configure Service:**
   - **Name:** `car-numberplate-detection` (or your choice)
   - **Region:** Oregon (US West) - closest for best performance
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     gunicorn app:app --bind 0.0.0.0:$PORT --timeout 600 --workers 1
     ```
   - **Instance Type:** `Free` (512 MB RAM, 0.5 CPU)

3. **Environment Variables:**
   - Add `SECRET_KEY` → Generate random value
   - Add `PYTHON_VERSION` → `3.11.0`

4. **Click "Create Web Service"**

#### Option B: Deploy via render.yaml (Automatic)

Your `render.yaml` is already configured! Just:
1. Go to Render Dashboard
2. Click **"New +"** → **"Blueprint"**
3. Connect your repository
4. Render will auto-detect `render.yaml`
5. Click **"Apply"**

### Step 4: Handle Model Files

Since model files are too large for Git, you need to download them at runtime:

**Edit `app.py` to add model download logic:**

```python
import os
import urllib.request

def download_model(url, filename):
    """Download model if not exists"""
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filename)
        print(f"Downloaded {filename}")

# Add before loading models:
download_model('https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt', 'yolov8n.pt')
# For license_plate_detector.pt, host it on GitHub Releases first
# download_model('YOUR_GITHUB_RELEASE_URL/license_plate_detector.pt', 'license_plate_detector.pt')
```

### Step 5: Monitor Deployment

1. **Build Logs:** Watch the deployment progress
2. **Deploy Logs:** Check for any errors
3. **Your App URL:** Will be `https://car-numberplate-detection.onrender.com`

### Step 6: Test Your Deployment

1. Visit your Render URL
2. Upload a test video
3. Check processing works correctly

---

## 🔄 Alternative Deployment Options

### Option 2: Railway.app (Free $5/month credit)

**Steps:**
1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub"**
4. Select your repository
5. Railway auto-detects Python and deploys
6. No configuration needed!

**Pros:**
- Even simpler than Render
- More generous free tier
- Better performance

### Option 3: Hugging Face Spaces (Free, Best for ML)

**Steps:**
1. Go to https://huggingface.co/spaces
2. Create new Space
3. Choose **Gradio** or **Streamlit**
4. Push your code
5. Models stored in Space storage

**Pros:**
- Designed for ML models
- Free GPU option available
- Great for AI projects

### Option 4: DigitalOcean App Platform ($5/month)

**Steps:**
1. Go to https://www.digitalocean.com/products/app-platform
2. Create account ($100 free credit for 60 days)
3. Connect GitHub repository
4. Select Python buildpack
5. Deploy

**Pros:**
- More resources (1GB RAM)
- Better for production
- Scalable

### Option 5: AWS EC2 / Google Cloud / Azure (Traditional VPS)

**For Full Control:**
1. Create a virtual machine
2. Install Python 3.11
3. Clone your repository
4. Install dependencies
5. Run with Gunicorn + Nginx

**Commands:**
```bash
# On Ubuntu server
sudo apt update
sudo apt install python3.11 python3-pip nginx
git clone https://github.com/kishanpatel486630/Car_Numberplate_Detaction_Project_COD.git
cd Car_Numberplate_Detaction_Project_COD
pip install -r requirements.txt
gunicorn app:app --bind 0.0.0.0:8000
```

---

## 📊 Comparison Table

| Platform | Free Tier | RAM | Deployment Time | Best For |
|----------|-----------|-----|-----------------|----------|
| **Render.com** ⭐ | ✅ Yes | 512 MB | 5-10 min | Python ML apps |
| Railway.app | $5 credit | 512 MB | 2-5 min | Quick deployments |
| Hugging Face | ✅ Yes | 16 GB | 10-15 min | ML/AI models |
| Vercel | ✅ Yes | 1 GB | 2-3 min | ❌ Too limited for ML |
| DigitalOcean | $100 credit | 1 GB | 5-10 min | Production apps |
| AWS/GCP/Azure | 12 months | 1+ GB | 15-30 min | Enterprise |

---

## ⚠️ Important Notes

### Model Files Issue:
- **YOLOv8n.pt** (~6 MB) - Auto-downloads from Ultralytics
- **license_plate_detector.pt** (~100 MB) - You must host this!

**Solution for license_plate_detector.pt:**

1. **Upload to GitHub Releases:**
   ```bash
   # Create a release
   git tag v1.0.0
   git push origin v1.0.0
   # Go to GitHub → Releases → Create Release
   # Upload license_plate_detector.pt as asset
   ```

2. **Get download URL:**
   ```
   https://github.com/kishanpatel486630/Car_Numberplate_Detaction_Project_COD/releases/download/v1.0.0/license_plate_detector.pt
   ```

3. **Update app.py** to download at startup

### Environment Variables:
Set these on your deployment platform:
- `SECRET_KEY` - Random string for Flask sessions
- `PYTHON_VERSION` - 3.11.0 (recommended)

### Performance Tips:
1. **Use Gunicorn** with proper timeout: `--timeout 600`
2. **Single Worker** for free tier: `--workers 1`
3. **Limit video size** in app.py: 100 MB max for free tier
4. **Add progress indicators** for long video processing

---

## 🎯 My Recommendation

**Start with Render.com** because:
1. Free tier is perfect for testing
2. Handles your ML dependencies
3. Simple deployment process
4. Can upgrade easily if needed

**If Render is slow or limited:**
- Try **Railway.app** next (easier deployment)
- Then **Hugging Face Spaces** (best for ML)

---

## 🐛 Troubleshooting

### Build Fails:
- Check Python version compatibility
- Verify requirements.txt dependencies
- Check build logs for specific errors

### App Crashes on Startup:
- Ensure model files are downloaded
- Check memory usage (free tier has limits)
- Verify all environment variables are set

### Slow Performance:
- Free tiers have limited resources
- Consider upgrading plan
- Optimize video processing code

---

## 📞 Need Help?

Check deployment logs first:
- **Render:** Dashboard → Your Service → Logs
- **Railway:** Project → Deployments → Logs
- **Hugging Face:** Space → Files → Logs

Common errors and solutions in deployment logs!
