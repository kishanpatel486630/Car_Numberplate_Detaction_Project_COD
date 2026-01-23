"""
PlateVision AI - Hugging Face Spaces
Automatic Number Plate Recognition using YOLOv8
"""
import os
os.environ['YOLO_VERBOSE'] = 'False'
os.environ['ULTRALYTICS_HUB_ENABLED'] = 'False'

import streamlit as st
import cv2
import gc
import tempfile
from pathlib import Path
import pandas as pd
from ultralytics import YOLO
import torch
from PIL import Image
import numpy as np
import util
from sort.sort import Sort
from util import get_car, read_license_plate, write_csv

# Page configuration
st.set_page_config(
    page_title="PlateVision AI - ANPR System",
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
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    .upload-text {
        text-align: center;
        padding: 20px;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 12px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Fix for newer Pillow versions
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

# Global model cache
@st.cache_resource
def load_models():
    """Load YOLOv8 models once and cache them"""
    with st.spinner("🔄 Loading AI models... (first time only, takes ~1 minute)"):
        gc.collect()
        
        # Load vehicle detection model
        coco_model = YOLO('yolov8n.pt')
        coco_model.overrides['verbose'] = False
        
        gc.collect()
        
        # Load license plate detection model
        plate_model = YOLO('license_plate_detector.pt')
        plate_model.overrides['verbose'] = False
        
        gc.collect()
        
    return coco_model, plate_model

def process_video(video_path, progress_bar, status_text):
    """Process video with Automatic Number Plate Recognition"""
    try:
        # Load cached models
        coco_model, license_plate_detector = load_models()
        mot_tracker = Sort()
        
        # Vehicle class IDs in COCO dataset
        vehicles = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        results = {}
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        frame_nmr = -1
        ret = True
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        st.info(f"📹 Video info: {total_frames} frames, {fps:.1f} FPS")
        
        while ret:
            frame_nmr += 1
            ret, frame = cap.read()
            
            if not ret:
                break
            
            results[frame_nmr] = {}
            
            # Update progress
            progress = (frame_nmr + 1) / total_frames
            progress_bar.progress(progress)
            status_text.text(f"🔍 Processing frame {frame_nmr + 1}/{total_frames} ({progress*100:.1f}%)")
            
            # Detect vehicles
            detections = coco_model(frame)[0]
            detections_ = []
            for detection in detections.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = detection
                if int(class_id) in vehicles:
                    detections_.append([x1, y1, x2, y2, score])
            
            # Track vehicles across frames
            track_ids = mot_tracker.update(np.asarray(detections_))
            
            # Detect license plates
            license_plates = license_plate_detector(frame)[0]
            for license_plate in license_plates.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = license_plate
                
                # Assign license plate to vehicle
                xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)
                
                if car_id != -1:
                    # Crop license plate region
                    license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
                    
                    # Preprocess license plate
                    license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                    _, license_plate_crop_thresh = cv2.threshold(
                        license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV
                    )
                    
                    # Read license plate text
                    license_plate_text, license_plate_text_score = read_license_plate(
                        license_plate_crop_thresh
                    )
                    
                    if license_plate_text is not None:
                        results[frame_nmr][car_id] = {
                            'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},
                            'license_plate': {
                                'bbox': [x1, y1, x2, y2],
                                'text': license_plate_text,
                                'bbox_score': score,
                                'text_score': license_plate_text_score
                            }
                        }
            
            # Garbage collection every 50 frames
            if frame_nmr % 50 == 0:
                gc.collect()
        
        cap.release()
        gc.collect()
        
        # Write results to CSV
        output_csv = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w')
        write_csv(results, output_csv.name)
        output_csv.close()
        
        return output_csv.name
        
    except Exception as e:
        st.error(f"❌ Error processing video: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None
    finally:
        gc.collect()

# Main UI
st.title("🚗 PlateVision AI")
st.markdown("### Automatic Number Plate Recognition System")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📋 How to Use")
    st.markdown("""
    1. **Upload** a video file containing vehicles
    2. Click **Process Video** button
    3. Wait for AI to analyze the video
    4. **Download** the results as CSV
    
    **Supported Formats:**
    - MP4, AVI, MOV, MKV
    - Maximum size: 200MB
    - Better quality = better results
    """)
    
    st.markdown("---")
    
    st.header("🤖 Technology Stack")
    st.markdown("""
    - **YOLOv8n**: Vehicle detection
    - **YOLOv8 Custom**: Plate detection
    - **SORT**: Multi-object tracking
    - **OpenCV**: Image processing
    - **Streamlit**: Web interface
    """)
    
    st.markdown("---")
    
    st.header("ℹ️ Features")
    st.markdown("""
    ✅ Real-time vehicle tracking  
    ✅ License plate detection  
    ✅ OCR text recognition  
    ✅ CSV export with timestamps  
    ✅ Multi-vehicle support  
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📤 Upload Video")
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
        help="Upload a video containing vehicles with visible license plates"
    )

with col2:
    st.subheader("📊 Statistics")
    if uploaded_file:
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
        st.metric("File Size", f"{file_size:.2f} MB")
        st.metric("File Name", uploaded_file.name)
    else:
        st.info("No file uploaded yet")

st.markdown("---")

if uploaded_file is not None:
    # Save uploaded file temporarily
    temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix)
    temp_input.write(uploaded_file.read())
    temp_input.close()
    
    st.success(f"✅ File uploaded successfully: **{uploaded_file.name}**")
    
    # Process button
    if st.button("🚀 Process Video", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        start_time = pd.Timestamp.now()
        
        with st.spinner("🔄 Processing video... This may take a few minutes."):
            output_csv = process_video(temp_input.name, progress_bar, status_text)
        
        end_time = pd.Timestamp.now()
        processing_time = (end_time - start_time).total_seconds()
        
        if output_csv:
            st.balloons()
            st.success(f"✅ Processing complete! Took {processing_time:.1f} seconds")
            
            # Load and display results
            df = pd.read_csv(output_csv)
            
            # Statistics
            st.subheader("📈 Results Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Detections", len(df))
            col2.metric("Unique Vehicles", df['car_id'].nunique() if 'car_id' in df.columns else 0)
            col3.metric("Frames Processed", df['frame_nmr'].nunique() if 'frame_nmr' in df.columns else 0)
            col4.metric("Processing Time", f"{processing_time:.1f}s")
            
            st.markdown("---")
            
            # Show results preview
            st.subheader("📋 Results Preview (First 20 rows)")
            st.dataframe(df.head(20), use_container_width=True)
            
            # Download button
            st.subheader("💾 Download Results")
            with open(output_csv, 'rb') as f:
                csv_data = f.read()
                st.download_button(
                    label="📥 Download Full Results (CSV)",
                    data=csv_data,
                    file_name=f"anpr_results_{uploaded_file.name.split('.')[0]}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
            
            # Cleanup
            try:
                os.unlink(output_csv)
            except:
                pass
        
        # Cleanup input file
        try:
            os.unlink(temp_input.name)
        except:
            pass
else:
    st.info("👆 **Please upload a video file to get started**")
    
    # Example section
    with st.expander("💡 Tips for Best Results"):
        st.markdown("""
        **For optimal license plate detection:**
        
        1. **Video Quality**: Use HD resolution (720p or higher)
        2. **Lighting**: Ensure good lighting conditions
        3. **Angle**: Front or rear view of vehicles works best
        4. **Distance**: Vehicles should be clearly visible, not too far
        5. **Speed**: Slower moving vehicles give better results
        6. **Stability**: Stable camera position (not too shaky)
        
        **Common Issues:**
        - Blurry plates → Won't be detected
        - Very small plates → May be missed
        - Extreme angles → Lower accuracy
        - Low light → Reduced detection rate
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "PlateVision AI | Powered by YOLOv8 & Streamlit | "
    "Built for Hugging Face Spaces 🤗"
    "</div>",
    unsafe_allow_html=True
)
