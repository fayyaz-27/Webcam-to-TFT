# 🎥 Webcam to ESP32 Vision-32 (WebSocket Streaming)

Real-time webcam streaming from a PC to an ESP32 (Vision-32) over WiFi using WebSockets.

This project captures video frames using OpenCV, compresses them into JPEG format, and streams them to an ESP32 Access Point for live display on a TFT screen.

---

## 📌 Overview

- Captures webcam video using OpenCV  
- Resizes frames to match TFT resolution  
- Optional frame rotation (0°, 90°, 180°, 270°)  
- JPEG compression for optimized transfer  
- Streams frames via WebSocket to ESP32  
- FPS control for stable real-time streaming  

---

## 🛠 Requirements

Install the required Python dependencies:

```bash
pip install asyncio cv2 websockets time
