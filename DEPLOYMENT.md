# Vercel Deployment Guide

## Issue Fixed
The deployment was failing because model files (`.pt` files) are too large (~4.38 GB total), exceeding Vercel's 4.29 GB limit.

## Solution Implemented

### 1. Created `.vercelignore`
Excludes large files from deployment:
- Model files (`*.pt`)
- Output directories (`outputs/`, `uploads/`)
- Virtual environments (`.venv/`)
- Cache files (`__pycache__/`)

### 2. Created `vercel.json`
Configures Vercel deployment:
- Increased memory to 3008 MB
- Set max duration to 300 seconds
- Proper Python serverless function configuration

### 3. Model Files Strategy

**Option A: Host Models Externally (Recommended)**
1. Upload `license_plate_detector.pt` to a cloud storage service:
   - GitHub Releases
   - Google Drive (with public link)
   - AWS S3
   - Azure Blob Storage

2. Update `app.py` with the download URL:
   ```python
   download_model_if_needed(
       plate_path, 
       'https://your-storage-url/license_plate_detector.pt'
   )
   ```

**Option B: Use Vercel Blob Storage**
1. Install Vercel Blob: `pip install vercel-blob`
2. Upload models to Vercel Blob
3. Load from Blob storage at runtime

**Option C: Git LFS (Large File Storage)**
1. Install Git LFS
2. Track `.pt` files: `git lfs track "*.pt"`
3. Commit `.gitattributes`
4. Models will be stored separately

## Deployment Steps

1. **Commit the changes:**
   ```bash
   git add .vercelignore vercel.json app.py
   git commit -m "Fix Vercel deployment - exclude large files"
   git push
   ```

2. **Host license_plate_detector.pt:**
   - Upload to GitHub Releases or cloud storage
   - Get public download URL
   - Update app.py with the URL

3. **Deploy to Vercel:**
   - Vercel will automatically redeploy on push
   - Or manually trigger: `vercel --prod`

## Important Notes

- **YOLOv8n.pt**: Will be auto-downloaded by ultralytics library
- **license_plate_detector.pt**: Must be hosted externally and downloaded at runtime
- **First request**: Will be slower due to model download (~1-2 minutes)
- **Subsequent requests**: Models are cached in `/tmp` directory

## Alternative: Use Render/Railway Instead

If Vercel continues to have issues, consider these alternatives that handle large files better:
- **Render.com**: Better for ML applications, 512 MB free tier
- **Railway.app**: Generous free tier, good for Python apps
- **Hugging Face Spaces**: Specifically designed for ML models

## Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Test at http://localhost:5000
```
