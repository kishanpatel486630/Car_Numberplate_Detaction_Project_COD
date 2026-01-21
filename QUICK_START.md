# 🚀 Quick Deployment Steps

## Deploy to Render.com (5 Minutes)

### Step 1: Remove Model Files from Git
```bash
git rm --cached yolov8n.pt license_plate_detector.pt
git add .gitignore app.py
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Deploy on Render
1. Go to https://render.com
2. Sign up with GitHub
3. Click **"New +"** → **"Web Service"**
4. Connect your repository
5. Use these settings:
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 600 --workers 1`
6. Click **"Create Web Service"**

### Step 3: Upload License Plate Model
1. Go to GitHub → Your Repo → Releases → Create Release
2. Tag: `v1.0.0`
3. Upload `license_plate_detector.pt` file
4. Publish release
5. Copy download URL
6. Update `app.py` line 47-48 with your URL:
   ```python
   LICENSE_PLATE_URL = 'https://github.com/YOUR_USERNAME/YOUR_REPO/releases/download/v1.0.0/license_plate_detector.pt'
   download_model_if_needed('license_plate_detector.pt', LICENSE_PLATE_URL)
   ```
7. Commit and push

### Step 4: Done! 🎉
Your app will be live at: `https://your-app-name.onrender.com`

---

## Alternative: Deploy to Railway (Even Easier!)

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub"**
4. Select your repository
5. Done! Railway auto-detects everything

---

## Need Full Guide?
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions and alternatives.
