"""
PlateVision AI - Streamlit Version (Lightweight & Memory Optimized)
Automatic Number Plate Recognition using YOLOv8
"""
# CRITICAL: Import signal fix FIRST before any other imports
import fix_signals

import os
os.environ['YOLO_VERBOSE'] = 'False'
os.environ['ULTRALYTICS_HUB_ENABLED'] = 'False'
os.environ['PYTHONUNBUFFERED'] = '1'

import streamlit as st
import cv2
import gc
import tempfile
import time
from pathlib import Path
import pandas as pd
from ultralytics import YOLO
import torch
from PIL import Image
import util
from sort.sort import Sort
from util import get_car, read_license_plate, write_csv
import numpy as np

# Page configuration
st.set_page_config(
    page_title="PlateVision AI",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 10px;
        padding: 10px 24px;
        font-size: 16px;
    }
    .upload-text {
        text-align: center;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Fix for newer Pillow versions
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

# Patch torch.load for PyTorch 2.6+
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

# Global model cache
@st.cache_resource
def load_models():
    """Load models once and cache them - Memory optimized"""
    with st.spinner("🔄 Loading AI models... (first time only)"):
        gc.collect()
        
        coco_model = YOLO('yolov8n.pt')
        coco_model.overrides['verbose'] = False
        
        gc.collect()
        
        plate_model = YOLO('license_plate_detector.pt')
        plate_model.overrides['verbose'] = False
        
        gc.collect()
        
    return coco_model, plate_model

def process_video(video_path, progress_bar, status_text):
    """Process video with ANPR - Memory optimized for Streamlit"""
    try:
        # Load cached models
        coco_model, license_plate_detector = load_models()
        mot_tracker = Sort()
        
        # Load video
        cap = cv2.VideoCapture(video_path)
        vehicles = [2, 3, 5, 7]
        results = {}
        
        # Video properties
        frame_nmr = -1
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Output video setup
        output_path = tempfile.mktemp(suffix='.avi')
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        status_text.text(f"📹 Processing {total_frames} frames...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_nmr += 1
            
            # Update progress
            if frame_nmr % 10 == 0:
                progress = frame_nmr / total_frames
                progress_bar.progress(progress)
                status_text.text(f"🎬 Processing frame {frame_nmr}/{total_frames} ({progress*100:.1f}%)")
            
            # Detect vehicles
            detections = coco_model(frame)[0]
            vehicle_detections = []
            
            for detection in detections.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = detection
                if int(class_id) in vehicles:
                    vehicle_detections.append([x1, y1, x2, y2, score])
            
            # Track vehicles
            track_ids = mot_tracker.update(np.asarray(vehicle_detections))
            
            # Detect license plates
            license_plates = license_plate_detector(frame)[0]
            
            for license_plate in license_plates.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = license_plate
                
                # Assign to vehicle
                xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)
                
                if car_id != -1:
                    # Crop license plate
                    license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
                    
                    # Read plate
                    license_plate_text, license_plate_score = read_license_plate(license_plate_crop)
                    
                    if license_plate_text is not None:
                        results[frame_nmr] = {
                            car_id: {
                                'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},
                                'license_plate': {
                                    'bbox': [x1, y1, x2, y2],
                                    'text': license_plate_text,
                                    'bbox_score': score,
                                    'text_score': license_plate_score
                                }
                            }
                        }
                        
                        # Draw on frame
                        cv2.rectangle(frame, (int(xcar1), int(ycar1)), (int(xcar2), int(ycar2)), (0, 255, 0), 2)
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                        cv2.putText(frame, license_plate_text, (int(x1), int(y1) - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            
            # Write frame
            out.write(frame)
            
            # Garbage collection every 50 frames
            if frame_nmr % 50 == 0:
                gc.collect()
        
        # Cleanup
        cap.release()
        out.release()
        gc.collect()
        
        # Write CSV
        csv_path = tempfile.mktemp(suffix='.csv')
        write_csv(results, csv_path)
        
        progress_bar.progress(1.0)
        status_text.text("✅ Processing complete!")
        
        return output_path, csv_path, results
        
    except Exception as e:
        st.error(f"❌ Error processing video: {str(e)}")
        return None, None, None

def main():
    # Header
    st.title("🚗 PlateVision AI")
    st.markdown("### Automatic Number Plate Recognition powered by YOLOv8")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 About")
        st.info("""
        **PlateVision AI** detects vehicles and license plates in videos using:
        - 🎯 YOLOv8 for detection
        - 🔍 SORT for tracking
        - 📝 OCR for plate reading
        """)
        
        st.header("⚙️ System Info")
        st.metric("Memory Optimized", "512MB")
        st.metric("Processing", "CPU-only")
        
    # Main content
    tab1, tab2 = st.tabs(["📤 Upload Video", "ℹ️ Instructions"])
    
    with tab1:
        st.markdown("### Upload your video file")
        
        uploaded_file = st.file_uploader(
            "Choose a video file (MP4, AVI, MOV, MKV)",
            type=['mp4', 'avi', 'mov', 'mkv'],
            help="Maximum file size: 50MB"
        )
        
        if uploaded_file is not None:
            # Save uploaded file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                tmp_file.write(uploaded_file.read())
                video_path = tmp_file.name
            
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Display video info
            col1, col2 = st.columns(2)
            with col1:
                st.metric("File Size", f"{uploaded_file.size / (1024*1024):.2f} MB")
            with col2:
                st.metric("Format", Path(uploaded_file.name).suffix.upper())
            
            # Process button
            if st.button("🚀 Start Processing", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                start_time = time.time()
                
                # Process video
                output_path, csv_path, results = process_video(video_path, progress_bar, status_text)
                
                if output_path and csv_path:
                    processing_time = time.time() - start_time
                    
                    # Success metrics
                    st.success(f"✅ Processing completed in {processing_time:.1f} seconds!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Frames Processed", len(results))
                    with col2:
                        st.metric("Detections", sum(len(frame_data) for frame_data in results.values()))
                    with col3:
                        st.metric("Processing Time", f"{processing_time:.1f}s")
                    
                    # Download buttons
                    st.markdown("### 📥 Download Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with open(output_path, 'rb') as f:
                            st.download_button(
                                label="📹 Download Processed Video",
                                data=f,
                                file_name=f"annotated_{uploaded_file.name}",
                                mime="video/avi"
                            )
                    
                    with col2:
                        with open(csv_path, 'rb') as f:
                            st.download_button(
                                label="📊 Download CSV Data",
                                data=f,
                                file_name=f"results_{Path(uploaded_file.name).stem}.csv",
                                mime="text/csv"
                            )
                    
                    # Preview results
                    st.markdown("### 📊 Detection Results Preview")
                    df = pd.read_csv(csv_path)
                    st.dataframe(df.head(20), use_container_width=True)
                    
                    # Cleanup temp files
                    try:
                        os.unlink(video_path)
                        os.unlink(output_path)
                        os.unlink(csv_path)
                    except:
                        pass
    
    with tab2:
        st.markdown("""
        ### 📖 How to Use
        
        1. **Upload Video**: Click on the upload area and select your video file
        2. **Start Processing**: Click the "Start Processing" button
        3. **Wait**: Processing may take a few minutes depending on video length
        4. **Download**: Get your annotated video and CSV results
        
        ### 📋 Supported Formats
        - MP4, AVI, MOV, MKV
        - Maximum file size: 50MB
        - Recommended: Short videos (< 1 minute)
        
        ### 🎯 What Gets Detected
        - **Vehicles**: Cars, motorcycles, buses, trucks
        - **License Plates**: Automatically detected and tracked
        - **Plate Text**: Extracted using OCR (when available)
        
        ### ⚠️ Notes
        - First run will download AI models (~12MB)
        - Processing speed: 1-5 FPS on CPU
        - Memory usage optimized for 512MB limit
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: gray;">Built with ❤️ using Streamlit & YOLOv8 | Optimized for Render.com</div>',
        unsafe_allow_html=True
    )

if __name__ == '__main__':
    main()
