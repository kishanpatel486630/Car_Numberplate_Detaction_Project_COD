# 🚀 Hugging Face Spaces Deployment Guide
## PlateVision AI - Complete Setup Instructions

---

## 📋 Prerequisites

1. **Hugging Face Account** (free)
   - Sign up at: https://huggingface.co/join

2. **Files Ready** (already in your project):
   - `app_hf.py` → Will be renamed to `app.py`
   - `util.py` → Utility functions
   - `sort/` folder → Tracking algorithm
   - `requirements-hf.txt` → Will be renamed to `requirements.txt`
   - `README_HF.md` → Will be renamed to `README.md`
   - `license_plate_detector.pt` → Custom YOLOv8 model

---

## 🎯 Method 1: Web Interface Upload (Easiest - 5 Minutes)

### Step 1: Create New Space

1. Go to: **https://huggingface.co/new-space**
2. Fill in the form:
   - **Owner**: Your username
   - **Space name**: `platevision-ai` (or any name you like)
   - **License**: MIT
   - **Select the Space SDK**: **Streamlit**
   - **Space hardware**: **CPU basic** (free)
   - **Space visibility**: Public (or Private if you prefer)
3. Click **"Create Space"**

### Step 2: Upload Files

Your Space will open with a file browser. Upload these files:

#### File Renames (IMPORTANT):
| Current File | Upload As |
|-------------|-----------|
| `app_hf.py` | `app.py` |
| `requirements-hf.txt` | `requirements.txt` |
| `README_HF.md` | `README.md` |

#### Files to Upload (keep same name):
- `util.py`
- `license_plate_detector.pt`
- Entire `sort/` folder (drag and drop the folder)

### Step 3: Upload Files via Web Interface

1. Click **"Files"** tab in your Space
2. Click **"Add file"** → **"Upload files"**
3. Drag and drop or select files:
   ```
   ✅ app.py (renamed from app_hf.py)
   ✅ requirements.txt (renamed from requirements-hf.txt)
   ✅ README.md (renamed from README_HF.md)
   ✅ util.py
   ✅ license_plate_detector.pt
   ✅ sort/ (entire folder with sort.py inside)
   ```
4. Click **"Commit to main"**

### Step 4: Wait for Build

- Your Space will automatically start building
- Watch the **"Logs"** tab for progress
- First build takes ~3-5 minutes (downloads models)
- You'll see: `"Running on local URL: http://0.0.0.0:7860"`
- Status will change to **"Running"** 🟢

### Step 5: Access Your App

Your app will be live at:
```
https://huggingface.co/spaces/YOUR_USERNAME/platevision-ai
```

---

## 🎯 Method 2: Git Upload (Advanced - 3 Minutes)

### Prerequisites
- Git installed on your computer
- Hugging Face account with SSH or access token

### Step 1: Create Space (same as Method 1 Step 1)

### Step 2: Clone Your Space Repository

```bash
# Option A: Using SSH
git clone git@hf.co:spaces/YOUR_USERNAME/platevision-ai
cd platevision-ai

# Option B: Using HTTPS (you'll need a token)
git clone https://huggingface.co/spaces/YOUR_USERNAME/platevision-ai
cd platevision-ai
```

### Step 3: Copy Files

```bash
# From your project directory
cp ../app_hf.py app.py
cp ../requirements-hf.txt requirements.txt
cp ../README_HF.md README.md
cp ../util.py .
cp ../license_plate_detector.pt .
cp -r ../sort .
```

### Step 4: Commit and Push

```bash
git add .
git commit -m "Initial deployment: ANPR system with YOLOv8"
git push
```

### Step 5: Monitor Deployment

Go to your Space URL and watch the **"Logs"** tab.

---

## 📁 Final File Structure in Your Space

```
platevision-ai/
├── app.py                          # Main Streamlit app
├── requirements.txt                # Python dependencies
├── README.md                       # Space documentation (with YAML header)
├── util.py                         # ANPR utility functions
├── license_plate_detector.pt       # Custom YOLOv8 model (~6MB)
└── sort/
    ├── sort.py                     # SORT tracking algorithm
    └── __pycache__/                # Auto-generated (gitignored)

Note: yolov8n.pt (~6MB) downloads automatically on first run
```

---

## 🔧 Configuration Options

### Upgrade to Better Hardware (Optional)

If you want faster processing:

1. Go to your Space → **Settings** → **Resource**
2. Choose upgrade:
   - **CPU Upgrade** ($9/month): 8 vCPU, 32GB RAM, 4x faster
   - **T4 Small GPU** ($0.60/hour): GPU acceleration, 10x faster
   - **T4 Medium GPU** ($1.50/hour): Best performance

### Make Space Private

1. Go to **Settings** → **Visibility**
2. Select **Private**
3. Only you can access it

---

## ✅ Verification Steps

After deployment, test your Space:

### 1. Check Build Logs
```
✅ "Collecting streamlit==1.28.0"
✅ "Collecting ultralytics==8.0.0"
✅ "Successfully installed ..."
✅ "Running on local URL: http://0.0.0.0:7860"
```

### 2. Test the App
1. Upload a sample video
2. Click "Process Video"
3. Should see:
   - "🔄 Loading AI models..." (first time only)
   - Progress bar advancing
   - CSV download button appears

### 3. Check Model Downloads
First run downloads:
- `yolov8n.pt` (~6MB) - Vehicle detection
- Already includes `license_plate_detector.pt`

---

## 🐛 Troubleshooting

### "Application Error" or Build Fails

**Check Logs** for specific errors:

#### Error: "No module named 'cv2'"
- **Fix**: requirements.txt should have `opencv-python-headless==4.8.0.74`

#### Error: "Cannot import ultralytics"
- **Fix**: requirements.txt should have `ultralytics==8.0.0`

#### Error: "No such file: license_plate_detector.pt"
- **Fix**: Upload the `.pt` model file

#### Error: "No module named 'sort'"
- **Fix**: Upload entire `sort/` folder with `sort.py` inside

### Space Stuck on "Building"

- Wait 5 minutes (downloads can be slow)
- Check Logs tab for errors
- Try: Settings → Factory Rebuild

### Models Not Loading

- First run takes longer (~1 minute)
- Models cache after first run
- Check if `yolov8n.pt` downloaded (visible in Logs)

### Video Processing Too Slow

- Free CPU tier processes ~5 FPS
- Upgrade to GPU for 10x speed: Settings → Resource → T4 Small

---

## 🎯 Post-Deployment Checklist

- [ ] Space is **Running** (green status)
- [ ] Can access at `https://huggingface.co/spaces/YOUR_USERNAME/platevision-ai`
- [ ] Upload test video works
- [ ] Process video completes
- [ ] CSV download works
- [ ] README displays properly
- [ ] Models load successfully

---

## 📊 Expected Performance

| Metric | Value |
|--------|-------|
| First Launch | ~1 minute (model download) |
| Subsequent Launches | ~10 seconds |
| Video Processing | ~5-10 FPS (CPU) |
| Memory Usage | ~2-4 GB |
| Model Size | ~12 MB total |
| Build Time | ~3-5 minutes |

---

## 🔗 Useful Links

- **Your Space**: `https://huggingface.co/spaces/YOUR_USERNAME/platevision-ai`
- **HF Docs**: https://huggingface.co/docs/hub/spaces
- **Streamlit on HF**: https://huggingface.co/docs/hub/spaces-sdks-streamlit
- **HF Community**: https://discuss.huggingface.co/

---

## 🎉 Success!

Once you see the green "Running" status and can access your Space, you're done!

**Share your Space:**
- Direct link: `https://huggingface.co/spaces/YOUR_USERNAME/platevision-ai`
- Embed in website using the embed code from Settings
- Share on social media

---

## 💡 Tips

1. **First video**: Use short video (10-30 seconds) to test
2. **Quality**: HD videos give best results
3. **Angle**: Front/rear view works better than side view
4. **Lighting**: Daylight videos work best
5. **Updates**: Edit files directly in HF Space interface or push via git

---

**Need Help?**
- Check Logs tab in your Space
- HF Discord: https://discord.gg/hugging-face
- Open issue on GitHub

**Made with ❤️ for Hugging Face Spaces 🤗**
