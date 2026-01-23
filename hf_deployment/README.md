---
title: PlateVision AI
emoji: 🚗
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.28.0"
app_file: app.py
pinned: false
license: mit
python_version: 3.11
---

# 🚗 PlateVision AI

**Automatic Number Plate Recognition (ANPR) System powered by YOLOv8**

## ✨ Features

- 🚙 **Vehicle Detection**: Detects cars, motorcycles, buses, and trucks
- 🔍 **License Plate Detection**: High-accuracy plate localization
- 📝 **OCR Recognition**: Reads plate numbers automatically
- 📊 **Multi-Vehicle Tracking**: SORT algorithm for tracking across frames
- 💾 **CSV Export**: Download complete results with timestamps
- 🎯 **Real-time Processing**: See progress as video is analyzed

## 🚀 How to Use

1. **Upload** a video file (MP4, AVI, MOV, etc.)
2. Click **"Process Video"** button
3. Wait for AI to analyze (progress bar shows status)
4. **Download** the results as CSV

## 📋 Requirements

- Video with visible license plates
- Good lighting conditions
- HD quality recommended (720p+)
- Front or rear view of vehicles

## 🤖 Technology Stack

- **YOLOv8n**: Vehicle detection (COCO dataset)
- **YOLOv8 Custom**: License plate detector
- **SORT**: Simple Online Realtime Tracking
- **OpenCV**: Image processing and video handling
- **Streamlit**: Interactive web interface
- **PyTorch**: Deep learning framework

## 📊 Output Format

The CSV file contains:
- Frame number
- Car ID (tracking ID)
- Vehicle bounding box coordinates
- License plate bounding box
- Detected plate text
- Detection confidence scores
- Timestamps

## 🎯 Use Cases

- Parking management systems
- Traffic monitoring
- Security and surveillance
- Toll collection analysis
- Vehicle tracking

## ⚙️ Performance

- **Processing Speed**: ~5-10 FPS on CPU
- **Accuracy**: Depends on video quality
- **Memory**: ~2-4 GB RAM during processing
- **Models**: Auto-downloaded on first run

## 📝 Notes

- First run downloads models (~50MB total)
- Processing time depends on video length
- Better quality video = better results
- OCR works best with clear, frontal plates

## 🤝 Credits

Built using:
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [SORT Tracking](https://github.com/abewley/sort)
- [Streamlit](https://streamlit.io/)

---

**Made with ❤️ for Hugging Face Spaces**

- YOLOv8 for detection
- SORT for tracking
- Streamlit for UI
