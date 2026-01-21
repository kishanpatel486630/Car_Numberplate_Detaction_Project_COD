from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
import time
from werkzeug.utils import secure_filename
import urllib.request
import cv2
from ultralytics import YOLO
import torch
from PIL import Image
import util
from sort.sort import Sort
from util import get_car, read_license_plate, write_csv
import numpy as np
import subprocess
import pandas as pd

# Fix for newer Pillow versions
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

# Patch torch.load for PyTorch 2.6+
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

def download_model_if_needed(filename, url=None):
    """Download model file if it doesn't exist"""
    if not os.path.exists(filename):
        if url:
            print(f"Downloading {filename}...")
            try:
                urllib.request.urlretrieve(url, filename)
                print(f"✓ Downloaded {filename}")
            except Exception as e:
                print(f"✗ Error downloading {filename}: {str(e)}")
                return False
        else:
            print(f"⚠ Warning: {filename} not found and no download URL provided")
            return False
    return True

# Download models at startup if needed
# YOLOv8n will auto-download via ultralytics if missing
# For license_plate_detector.pt, uncomment and add your GitHub Release URL:
# LICENSE_PLATE_URL = 'https://github.com/kishanpatel486630/Car_Numberplate_Detaction_Project_COD/releases/download/v1.0.0/license_plate_detector.pt'
# download_model_if_needed('license_plate_detector.pt', LICENSE_PLATE_URL)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv'}

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_video(video_path, output_folder):
    """Process video with ANPR and return paths to results"""
    try:
        # Load models
        coco_model = YOLO('yolov8n.pt')
        license_plate_detector = YOLO('license_plate_detector.pt')
        
        mot_tracker = Sort()
        
        # Load video
        cap = cv2.VideoCapture(video_path)
        
        vehicles = [2, 3, 5, 7]
        results = {}
        
        # Read frames
        frame_nmr = -1
        ret = True
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Processing {total_frames} frames...")
        
        while ret:
            frame_nmr += 1
            ret, frame = cap.read()
            
            if frame_nmr % 50 == 0:
                print(f"Processing frame {frame_nmr}/{total_frames}")
            
            if ret:
                results[frame_nmr] = {}
                
                # Detect vehicles
                detections = coco_model(frame)[0]
                detections_ = []
                for detection in detections.boxes.data.tolist():
                    x1, y1, x2, y2, score, class_id = detection
                    if int(class_id) in vehicles:
                        detections_.append([x1, y1, x2, y2, score])
                
                # Track vehicles
                track_ids = mot_tracker.update(np.asarray(detections_))
                
                # Detect license plates
                license_plates = license_plate_detector(frame)[0]
                for license_plate in license_plates.boxes.data.tolist():
                    x1, y1, x2, y2, score, class_id = license_plate
                    
                    # Assign license plate to car
                    xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)
                    
                    if car_id != -1:
                        # Crop license plate
                        license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]
                        
                        # Process license plate
                        license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                        _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)
                        
                        # Read license plate number
                        license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)
                        
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
        
        cap.release()
        
        # Write results to CSV
        csv_path = os.path.join(output_folder, 'results.csv')
        write_csv(results, csv_path)
        
        print("Generating output video...")
        # Generate output video directly from raw results
        output_video = os.path.join(output_folder, 'output.avi')
        generate_output_video_simple(video_path, csv_path, output_video)
        
        return {
            'csv': csv_path,
            'video': output_video
        }
        
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e

def generate_output_video_simple(input_video, csv_file, output_video):
    """Generate visualization video from CSV results"""
    import ast
    
    # Check if CSV exists and has data
    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        return
    
    results = pd.read_csv(csv_file)
    if len(results) == 0:
        print("No results found in CSV")
        return
        
    cap = cv2.VideoCapture(input_video)
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    
    frame_nmr = -1
    ret = True
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Rendering {total_frames} frames...")
    
    while ret:
        ret, frame = cap.read()
        frame_nmr += 1
        
        if frame_nmr % 100 == 0:
            print(f"Rendering frame {frame_nmr}/{total_frames}")
        
        if ret:
            # Get detections for this frame
            df_ = results[results['frame_nmr'] == frame_nmr]
            
            for row_indx in range(len(df_)):
                try:
                    # Draw car bounding box
                    car_bbox = ast.literal_eval(df_.iloc[row_indx]['car_bbox'].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))
                    car_x1, car_y1, car_x2, car_y2 = car_bbox
                    cv2.rectangle(frame, (int(car_x1), int(car_y1)), (int(car_x2), int(car_y2)), (0, 255, 0), 3)
                    
                    # Draw license plate bounding box
                    lp_bbox = ast.literal_eval(df_.iloc[row_indx]['license_plate_bbox'].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))
                    x1, y1, x2, y2 = lp_bbox
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                    
                    # Add license plate text
                    license_text = str(df_.iloc[row_indx]['license_number'])
                    cv2.putText(frame, license_text, (int(car_x1), int(car_y1) - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                except Exception as e:
                    print(f"Error processing frame {frame_nmr}, row {row_indx}: {e}")
                    continue
            
            out.write(frame)
    
    out.release()
    cap.release()
    print("Video rendering complete!")
    out.release()
    cap.release()
    print("Video rendering complete!")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['video']
    
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Create output folder for this video
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], timestamp)
        os.makedirs(output_folder, exist_ok=True)
        
        try:
            # Process video
            results = process_video(filepath, output_folder)
            
            return render_template('result.html', 
                                 video_name=filename,
                                 output_video=os.path.basename(results['video']),
                                 timestamp=timestamp)
        except Exception as e:
            flash(f'Error processing video: {str(e)}')
            return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload MP4, AVI, MOV, or MKV files.')
        return redirect(url_for('index'))

@app.route('/download/<timestamp>/<filename>')
def download_file(timestamp, filename):
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], timestamp, filename)
    return send_file(filepath, as_attachment=True)

@app.route('/video/<timestamp>/<filename>')
def serve_video(timestamp, filename):
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], timestamp, filename)
    return send_file(filepath, mimetype='video/x-msvideo')

if __name__ == '__main__':
    # Use PORT environment variable for cloud deployment (Render, etc.)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
