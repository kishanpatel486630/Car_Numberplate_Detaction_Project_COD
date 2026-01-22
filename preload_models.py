#!/usr/bin/env python3
"""
Preload models with aggressive memory management for Render deployment
"""
import os
import gc
import torch
from ultralytics import YOLO

# Set environment variables for memory optimization
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['TORCH_HOME'] = '/tmp/.cache/torch'
os.environ['YOLO_CONFIG_DIR'] = '/tmp/.config/Ultralytics'

print("=" * 60)
print("PRELOADING MODELS WITH MEMORY OPTIMIZATION")
print("=" * 60)

try:
    # Force garbage collection
    gc.collect()
    
    # Load YOLOv8n with minimal settings
    print("\n1. Loading yolov8n.pt...")
    model1 = YOLO('yolov8n.pt')
    model1.overrides['verbose'] = False
    print("✓ yolov8n.pt loaded")
    
    # Force cleanup
    del model1
    gc.collect()
    
    print("\n2. Loading license_plate_detector.pt...")
    model2 = YOLO('license_plate_detector.pt')
    model2.overrides['verbose'] = False
    print("✓ license_plate_detector.pt loaded")
    
    # Final cleanup
    del model2
    gc.collect()
    
    print("\n" + "=" * 60)
    print("ALL MODELS PRELOADED SUCCESSFULLY")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
