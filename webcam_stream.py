# Program Name: Webcam Integration to Vision-32
# Language: Python
# Dependencies to install : asyncio, cv2, websockets & time.

# Author: Mr. Fayyaz Nisar Shaikh
# Github: github.com/fayyaz-27
# LinkedIn: linkedin.com/in/fayyaz-shaikh-7646312a3/
# Email: fayyaz.nisar.shaikh@gmail.com


import asyncio
import cv2
import websockets
import time


# IP of the ESP32 AP, Connect to the ESP32 Access Point (Hotspot)

ESP32_IP = "192.168.4.1"
ESP32_PORT = 80
WS_URI = f"ws://{ESP32_IP}:{ESP32_PORT}/"

# TFT parameters (MUST match your TFT + JPEG size)
# The JPEG width/height must match the panel if you want full-screen.

TFT_WIDTH  = 320   # change if your display is 120, 160, 240, 480, etc.
TFT_HEIGHT = 240   # change accordingly

# JPEG quality (0–100). Lower = more compression, smaller size, higher FPS.
JPEG_QUALITY = 70

# Target max FPS
TARGET_FPS = 10

# 0 is default camera. Change if you have multiple webcams.
CAMERA_INDEX = 0

# Rotate frame if your orientation is wrong.
# Options: 0 (no rotate), 90, 180, 270
ROTATE_DEG = 0


def process_frame_for_tft(frame):

    """
    - Resize to TFT resolution
    - Rotate if needed
    - Encode to JPEG bytes
    """

    frame_resized = cv2.resize(frame, (TFT_WIDTH, TFT_HEIGHT))

    if ROTATE_DEG == 90:
        frame_resized = cv2.rotate(frame_resized, cv2.ROTATE_90_CLOCKWISE)
    elif ROTATE_DEG == 180:
        frame_resized = cv2.rotate(frame_resized, cv2.ROTATE_180)
    elif ROTATE_DEG == 270:
        frame_resized = cv2.rotate(frame_resized, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # Encode to JPEG
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
    success, encoded = cv2.imencode(".jpg", frame_resized, encode_param)

    if not success:
        raise RuntimeError("Failed to encode frame to JPEG")

    return encoded.tobytes()


async def stream_camera():
    # Open camera
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Check CAMERA_INDEX.")

    print("Webcam opened. Connecting to ESP32 WebSocket:", WS_URI)

    # Keep reconnecting loop
    while True:
        try:
            async with websockets.connect(WS_URI, max_size=None) as ws:
                print("Connected to ESP32 WebSocket.")

                last_time = time.time()

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to read frame from camera.")
                        break

                    # Prepare frame for TFT
                    try:
                        jpeg_bytes = process_frame_for_tft(frame)
                    except Exception as e:
                        print("Frame processing error:", e)
                        continue

                    # Send as one WebSocket message (binary)
                    try:
                        await ws.send(jpeg_bytes)
                    except Exception as e:
                        print("WebSocket send error:", e)
                        break

                    # Basic FPS limiting
                    elapsed = time.time() - last_time
                    target_dt = 1.0 / TARGET_FPS
                    if elapsed < target_dt:
                        await asyncio.sleep(target_dt - elapsed)
                    last_time = time.time()

        except (ConnectionRefusedError, OSError) as e:
            print("Connection failed, retrying in 2 seconds:", e)
            await asyncio.sleep(2)


def main():
    try:
        asyncio.run(stream_camera())
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")


if __name__ == "__main__":
    main()
