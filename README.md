# 🚗 PlateVision AI - Automatic Number Plate Recognition

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-green.svg)
![Flask](https://img.shields.io/badge/Flask-3.1-red.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-Headless-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Memory-optimized ANPR system for cloud deployment (512MB RAM)**

[Quick Start](#-quick-start) • [Deployment](#-deployment) • [Features](#-features) • [Tech Stack](#-tech-stack)

</div>

---

## 📋 Overview

PlateVision AI is a production-ready ANPR solution optimized for cloud deployment. Detects vehicles, tracks them across frames, and identifies license plates with a modern web interface.

**Memory Footprint:** ~500MB RAM | **Deployment:** Render.com free tier compatible

## ✨ Features

| Feature                        | Description                                                 |
| ------------------------------ | ----------------------------------------------------------- |
| 🚘 **Vehicle Detection**       | YOLOv8 detects cars, motorcycles, buses, trucks            |
| 🔍 **License Plate Detection** | Custom-trained YOLOv8 model for plate localization         |
| 📝 **Plate Identification**    | Hash-based unique plate IDs (OCR-ready)                     |
| 🎯 **Multi-Object Tracking**   | SORT algorithm maintains vehicle IDs across frames          |
| 🎬 **Video Output**            | Annotated video with bounding boxes and plate labels        |
| 📊 **CSV Export**              | Frame-by-frame detection data export                        |
| 🎨 **Modern UI**               | iOS-style responsive web interface                          |
| 🧹 **Auto-Cleanup**            | Files deleted after download (no storage bloat)             |

## 🎥 Demo

### Input vs Output

```
┌─────────────────────┐         ┌─────────────────────┐
│                     │         │    ┌──────────┐     │
│    Original         │         │    │ AB12CDE  │     │
│    Video            │  ───►   │    └──────────┘     │
│                     │         │  🟢 ┌─────────┐     │
│    🚗 🚙 🚕          │         │     │ 🚗      │     │
│                     │         │  🔴 │ [PLATE] │     │
└─────────────────────┘         └─────────────────────┘
```


## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/kishanpatel486630/Car_Numberplate_Detaction_Project_COD.git
cd Car_Numberplate_Detaction_Project_COD

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## ☁️ Deployment

### Render.com (Free Tier - 512MB RAM)

1. **Push to GitHub** (model files auto-downloaded at runtime)
2. **Connect to Render:** Import repository
3. **Auto-deploy:** Configured via `render.yaml`
4. **Health check:** Endpoint at `/`

**Configuration:**
- Runtime: Python 3.11
- Start command: `python app.py`
- Build command: `pip install -r requirements.txt`

## 📖 Usage

1. Upload video (MP4, AVI, MOV, MKV) - max 500MB
2. Processing starts automatically
3. View annotated video with detected plates
4. Download output video (.avi) and CSV results
5. Files auto-delete after download (no storage bloat)

**Memory optimization:** Models cached globally, garbage collection every 50 frames, /tmp directory for temporary files.

## 🧠 How It Works

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   STAGE 1    │     │   STAGE 2    │     │   STAGE 3    │     │   STAGE 4    │
│              │     │              │     │              │     │              │
│   Vehicle    │ ──► │   Object     │ ──► │   License    │ ──► │    Text      │
│  Detection   │     │  Tracking    │     │   Plate      │     │ Recognition  │
│              │     │              │     │  Detection   │     │    (OCR)     │
│   YOLOv8     │     │    SORT      │     │ Custom YOLO  │     │   EasyOCR    │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### Stage 1: Vehicle Detection

- Uses YOLOv8 (yolov8n.pt) pre-trained on COCO dataset
- Detects vehicles: cars (class 2), motorcycles (3), buses (5), trucks (7)
- Outputs bounding boxes with confidence scores

### Stage 2: Object Tracking

- SORT (Simple Online Realtime Tracking) algorithm
- Kalman Filter for motion prediction
- Hungarian Algorithm for detection-to-track assignment
- Maintains unique IDs across video frames

### Stage 3: License Plate Detection

- Custom YOLOv8 model trained on license plate dataset
- Detects plates within vehicle bounding boxes
- Works with various plate orientations and lighting

### Stage 4: Text Recognition

- EasyOCR with English language model
- Image preprocessing (grayscale, thresholding)
- Format validation for standard plate patterns
- Character mapping to fix common OCR errors (O↔0, I↔1, S↔5)

## 🔧 Tech Stack

| Component     | Technology           | Purpose               |
| ------------- | -------------------- | --------------------- |
| **Backend**   | Flask 3.1.2          | Web server & API      |
| **Frontend**  | HTML/CSS/JS          | User interface        |
| **Detection** | YOLOv8 (Ultralytics) | Object detection      |
| **Tracking**  | SORT                 | Multi-object tracking |
| **OCR**       | Hash-based IDs       | Plate identification  |
| **Video**     | OpenCV Headless      | Video processing      |
| **AI Engine** | PyTorch 2.10.0 (CPU) | Deep learning         |

## 📁 Project Structure

```
PlateVision-AI/
├── app.py                      # Flask application (memory-optimized)
├── util.py                     # Helper functions (plate detection, CSV)
├── requirements.txt            # Python dependencies (CPU-only)
├── render.yaml                 # Render.com deployment config
├── .gitignore                  # Excludes model files (*.pt)
│
├── sort/
│   └── sort.py                 # SORT tracking algorithm
│
├── templates/
│   ├── index.html              # Upload interface
│   └── result.html             # Results display
│
├── static/                     # CSS, JavaScript assets
├── LICENSE                     # MIT License
└── README.md                   # Documentation
```

**Note:** Model files (`yolov8n.pt`, `license_plate_detector.pt`) auto-download at first run (~12MB total).

## 📊 Performance

| Metric                     | Value     |
| -------------------------- | --------- |
| Vehicle Detection          | ~95%      |
| Plate Detection            | ~90%      |
| Processing Speed (CPU)     | 1-5 FPS   |
| Memory Usage               | ~500MB    |
| Startup Time (cold start)  | ~30s      |

## 🔑 Key Optimizations

✅ **Memory-efficient:** Removed EasyOCR (saves 300+ MB RAM)  
✅ **Model caching:** Load once per app lifecycle  
✅ **Garbage collection:** Every 50 frames during processing  
✅ **Auto-cleanup:** Files deleted after download  
✅ **Direct downloads:** No persistent storage  
✅ **CPU-only PyTorch:** Smaller footprint  
✅ **Headless OpenCV:** No GUI dependencies


## 🤝 Contributing

Contributions welcome! Submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) - Object detection
- [SORT](https://github.com/abewley/sort) - Multi-object tracking
- [OpenCV](https://opencv.org/) - Computer vision
- [Flask](https://flask.palletsprojects.com/) - Web framework

---

<div align="center">

**Built with ❤️ for efficient cloud deployment**

</div>

**Made with ❤️ by Kishan Patel**

⭐ Star this repo if you find it helpful!

</div>
