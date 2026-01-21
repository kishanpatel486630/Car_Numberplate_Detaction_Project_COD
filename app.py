from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
import os
import time
import sys
from werkzeug.utils import secure_filename
import urllib.request

# Set environment before importing heavy libraries
os.environ['YOLO_VERBOSE'] = 'False'
os.environ['OMP_NUM_THREADS'] = '1'

# Check if running on Vercel
IS_VERCEL = os.environ.get('VERCEL') == '1'

# Import numpy and cv2 with error handling
try:
    import cv2
    import numpy as np
    import pandas as pd
    CV2_AVAILABLE = True
except ImportError as e:
    print(f"Warning: OpenCV import failed: {e}")
    CV2_AVAILABLE = False
    np = None
    pd = None

# Lazy load heavy ML libraries for faster cold starts
_models_loaded = False
_coco_model = None
_license_plate_detector = None

def download_model_if_needed(model_path, model_url):
    """Download model file if it doesn't exist"""
    if not os.path.exists(model_path):
        print(f"Downloading {os.path.basename(model_path)}...")
        os.makedirs(os.path.dirname(model_path) if os.path.dirname(model_path) else '.', exist_ok=True)
        urllib.request.urlretrieve(model_url, model_path)
        print(f"Downloaded {os.path.basename(model_path)}")

def load_models():
    """Lazy load ML models"""
    global _models_loaded, _coco_model, _license_plate_detector
    if not _models_loaded:
        try:
            from ultralytics import YOLO
            import torch
            from PIL import Image
            
            # Fix for newer Pillow versions
            if not hasattr(Image, 'ANTIALIAS'):
                Image.ANTIALIAS = Image.LANCZOS
            
            # Patch torch.load for PyTorch 2.6+
            _original_torch_load = torch.load
            def _patched_torch_load(*args, **kwargs):
                kwargs['weights_only'] = False
                return _original_torch_load(*args, **kwargs)
            torch.load = _patched_torch_load
            
            # Get model paths
            base_path = os.path.dirname(os.path.abspath(__file__))
            yolo_path = os.path.join(base_path, 'yolov8n.pt')
            plate_path = os.path.join(base_path, 'license_plate_detector.pt')
            
            # For Vercel deployment - download license plate detector if not exists
            # Upload your license_plate_detector.pt to GitHub Releases and uncomment:
            # LICENSE_PLATE_MODEL_URL = 'https://github.com/kishanpatel486630/Car_Numberplate_Detaction_Project_COD/releases/download/v1.0.0/license_plate_detector.pt'
            # if not os.path.exists(plate_path):
            #     download_model_if_needed(plate_path, LICENSE_PLATE_MODEL_URL)
            
            print("Loading YOLO models...")
            _coco_model = YOLO(yolo_path)  # YOLOv8n auto-downloads if missing
            
            if os.path.exists(plate_path):
                _license_plate_detector = YOLO(plate_path)
                print("Models loaded successfully!")
            else:
                print(f"Warning: {plate_path} not found. Upload required!")
                _license_plate_detector = None
                
            _models_loaded = True
            
        except Exception as e:
            print(f"Error loading models: {str(e)}")
            raise
    
    return _coco_model, _license_plate_detector

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'platevision-secret-key-2024')

# Use /tmp for Vercel serverless (writable directory)
UPLOAD_FOLDER = '/tmp/uploads' if IS_VERCEL else 'uploads'
OUTPUT_FOLDER = '/tmp/outputs' if IS_VERCEL else 'outputs'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25MB for serverless
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv'}

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Health check endpoint for Vercel
@app.route('/api/health')
@app.route('/health')
def health_check():
    try:
        status_info = {
            'status': 'ok', 
            'vercel': IS_VERCEL,
            'cv2_available': CV2_AVAILABLE,
            'python_version': sys.version
        }
        
        # Only try loading models if dependencies are available
        if CV2_AVAILABLE:
            try:
                coco_model, plate_detector = load_models()
                status_info['models'] = {
                    'yolo': coco_model is not None,
                    'license_plate': plate_detector is not None
                }
            except Exception as model_error:
                status_info['models_error'] = str(model_error)
        
        return jsonify(status_info)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'type': type(e).__name__,
            'vercel': IS_VERCEL
        }), 500

@app.route('/')
def index():
    if not CV2_AVAILABLE and IS_VERCEL:
        return jsonify({
            'error': 'Application not fully initialized',
            'message': 'Required dependencies are not available on this platform',
            'suggestion': 'This application requires heavy ML dependencies. Consider using Railway, Render, or Hugging Face Spaces instead of Vercel.'
        }), 503
    return render_template('index.html')

def process_video(video_path, output_folder):
    """Process video with ANPR and return paths to results"""
    from sort.sort import Sort
    from util import get_car, read_license_plate, write_csv
    
    try:
        # Load models (lazy loading)
        coco_model, license_plate_detector = load_models()
        
        if license_plate_detector is None:
            raise Exception("License plate detector model not found. Please upload license_plate_detector.pt to GitHub Releases.")
        
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
    """Generate visualization video from CSV results with plate crops and labels"""
    import ast
    import numpy as np
    
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
    
    # Pre-compute best license plate crop for each car
    license_plate_data = {}
    for car_id in results['car_id'].unique():
        car_results = results[results['car_id'] == car_id]
        max_score = car_results['license_number_score'].max()
        best_row = car_results[car_results['license_number_score'] == max_score].iloc[0]
        
        # Get the best frame for this car
        best_frame_nmr = int(best_row['frame_nmr'])
        cap.set(cv2.CAP_PROP_POS_FRAMES, best_frame_nmr)
        ret, frame = cap.read()
        
        if ret:
            try:
                lp_bbox = ast.literal_eval(str(best_row['license_plate_bbox']).replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))
                x1, y1, x2, y2 = [int(v) for v in lp_bbox]
                
                # Crop and resize license plate
                license_crop = frame[y1:y2, x1:x2, :]
                if license_crop.size > 0:
                    # Resize to standard height while maintaining aspect ratio
                    crop_h, crop_w = license_crop.shape[:2]
                    new_height = 60
                    new_width = int(crop_w * new_height / crop_h)
                    license_crop = cv2.resize(license_crop, (new_width, new_height))
                    
                    license_plate_data[car_id] = {
                        'crop': license_crop,
                        'text': str(best_row['license_number'])
                    }
            except Exception as e:
                print(f"Error getting plate crop for car {car_id}: {e}")
    
    # Reset video to start
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
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
                    row = df_.iloc[row_indx]
                    car_id = row['car_id']
                    
                    # Parse bounding boxes
                    car_bbox = ast.literal_eval(str(row['car_bbox']).replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))
                    car_x1, car_y1, car_x2, car_y2 = [int(v) for v in car_bbox]
                    
                    lp_bbox = ast.literal_eval(str(row['license_plate_bbox']).replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))
                    x1, y1, x2, y2 = [int(v) for v in lp_bbox]
                    
                    # Draw green bounding box around car (thick corners style)
                    thickness = 3
                    corner_length = min(50, (car_x2 - car_x1) // 4, (car_y2 - car_y1) // 4)
                    color_green = (0, 255, 0)
                    
                    # Top-left corner
                    cv2.line(frame, (car_x1, car_y1), (car_x1 + corner_length, car_y1), color_green, thickness)
                    cv2.line(frame, (car_x1, car_y1), (car_x1, car_y1 + corner_length), color_green, thickness)
                    # Top-right corner
                    cv2.line(frame, (car_x2, car_y1), (car_x2 - corner_length, car_y1), color_green, thickness)
                    cv2.line(frame, (car_x2, car_y1), (car_x2, car_y1 + corner_length), color_green, thickness)
                    # Bottom-left corner
                    cv2.line(frame, (car_x1, car_y2), (car_x1 + corner_length, car_y2), color_green, thickness)
                    cv2.line(frame, (car_x1, car_y2), (car_x1, car_y2 - corner_length), color_green, thickness)
                    # Bottom-right corner
                    cv2.line(frame, (car_x2, car_y2), (car_x2 - corner_length, car_y2), color_green, thickness)
                    cv2.line(frame, (car_x2, car_y2), (car_x2, car_y2 - corner_length), color_green, thickness)
                    
                    # Draw red bounding box around license plate
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    
                    # Get pre-computed license plate data
                    if car_id in license_plate_data:
                        plate_data = license_plate_data[car_id]
                        license_crop = plate_data['crop']
                        license_text = plate_data['text']
                        
                        crop_h, crop_w = license_crop.shape[:2]
                        
                        # Calculate text size for the label
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        font_scale = 0.8
                        font_thickness = 2
                        (text_w, text_h), baseline = cv2.getTextSize(license_text, font, font_scale, font_thickness)
                        
                        # Make label width match crop width or text width (whichever is larger)
                        label_width = max(crop_w, text_w + 20)
                        label_height = text_h + 20
                        
                        # Position: above the car bounding box
                        label_x = car_x1 + (car_x2 - car_x1) // 2 - label_width // 2
                        label_y = car_y1 - crop_h - label_height - 10
                        
                        # Ensure it stays within frame bounds
                        label_x = max(5, min(label_x, width - label_width - 5))
                        label_y = max(5, label_y)
                        
                        crop_x = label_x + (label_width - crop_w) // 2
                        crop_y = label_y + label_height + 5
                        
                        # Check if there's enough space
                        if label_y > 5 and crop_y + crop_h < car_y1:
                            # Draw white background for text label
                            cv2.rectangle(frame, 
                                         (label_x, label_y), 
                                         (label_x + label_width, label_y + label_height), 
                                         (255, 255, 255), -1)
                            
                            # Draw black text on white background
                            text_x = label_x + (label_width - text_w) // 2
                            text_y = label_y + label_height - 8
                            cv2.putText(frame, license_text, (text_x, text_y),
                                       font, font_scale, (0, 0, 0), font_thickness)
                            
                            # Place license plate crop below the text label
                            if crop_y >= 0 and crop_x >= 0 and crop_y + crop_h <= height and crop_x + crop_w <= width:
                                frame[crop_y:crop_y + crop_h, crop_x:crop_x + crop_w] = license_crop
                        else:
                            # Fallback: just draw text near the plate if no space above
                            cv2.rectangle(frame, (x1, y1 - 25), (x1 + text_w + 10, y1), (255, 255, 255), -1)
                            cv2.putText(frame, license_text, (x1 + 5, y1 - 7),
                                       font, font_scale, (0, 0, 0), font_thickness)
                    
                except Exception as e:
                    print(f"Error processing frame {frame_nmr}, row {row_indx}: {e}")
                    continue
            
            out.write(frame)
    
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
            print(f"Processing error: {str(e)}")
            flash(f'Error processing video: {str(e)}')
            return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload MP4, AVI, MOV, or MKV files.')
        return redirect(url_for('index'))

@app.route('/download/<timestamp>/<filename>')
def download_file(timestamp, filename):
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], timestamp, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        flash('File not found')
        return redirect(url_for('index'))

@app.route('/video/<timestamp>/<filename>')
def serve_video(timestamp, filename):
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], timestamp, filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='video/x-msvideo')
    else:
        return jsonify({'error': 'Video not found'}), 404

# Error handlers
@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 25MB.')
    return redirect(url_for('index'))

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

# Vercel requires the app to be named 'app'
# This is for local development only
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
