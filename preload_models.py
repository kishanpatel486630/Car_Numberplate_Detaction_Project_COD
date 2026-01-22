#!/usr/bin/env python3
"""
Download model files without loading them to avoid memory spike during build
"""
import os
import urllib.request

print("=" * 60)
print("DOWNLOADING MODEL FILES (NO LOADING)")
print("=" * 60)

# Set cache directories
os.makedirs('/tmp/.cache/torch', exist_ok=True)
os.makedirs('/tmp/.config/Ultralytics', exist_ok=True)

models = {
    'yolov8n.pt': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt',
    # license_plate_detector.pt should be in your repo or add download URL
}

for model_name, url in models.items():
    if not os.path.exists(model_name):
        print(f"\nDownloading {model_name}...")
        try:
            urllib.request.urlretrieve(url, model_name)
            print(f"✓ {model_name} downloaded")
        except Exception as e:
            print(f"✗ Could not download {model_name}: {e}")
            print("  (Will download at runtime)")
    else:
        print(f"✓ {model_name} already exists")

print("\n" + "=" * 60)
print("MODEL FILES READY")
print("=" * 60)
