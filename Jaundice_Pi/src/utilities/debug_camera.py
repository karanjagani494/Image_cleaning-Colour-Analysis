"""
camera.py — Raspberry Pi camera capture via OpenCV.

Works with any USB webcam or the Pi Camera Module (via libcamera-v4l2 driver).
"""

import cv2
import numpy as np
import os
import time
from datetime import datetime

from config import settings


def _open_camera() -> cv2.VideoCapture:
    """Open the camera and configure resolution."""
    cap = cv2.VideoCapture(settings.CAMERA_INDEX, cv2.CAP_V4L2)
    if not cap.isOpened():
        # Fallback: try without backend hint
        cap = cv2.VideoCapture(settings.CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(
            f"Cannot open camera at index {settings.CAMERA_INDEX}. "
            "Check it is connected and not in use."
        )

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  settings.CAPTURE_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.CAPTURE_HEIGHT)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)   # always grab latest frame

    # Warm-up: discard first N frames (sensor auto-exposure stabilise)
    for _ in range(settings.CAMERA_WARMUP_FRAMES):
        cap.read()

    return cap


def capture_image(save_prefix: str = "raw") -> np.ndarray:
    """
    Open camera, show live preview, capture on keypress, save & return image.

    Returns
    -------
    np.ndarray  float64 RGB image in [0, 1]
    """
    cap = _open_camera()

    print("\n[Camera] Live preview — press SPACE to capture, Q to quit.")
    frame_bgr = None

    while True:
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("Failed to read frame from camera.")

        cv2.imshow("Preview — SPACE to capture", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(" "):
            frame_bgr = frame.copy()
            break
        elif key == ord("q"):
            cap.release()
            cv2.destroyAllWindows()
            raise KeyboardInterrupt("Capture cancelled by user.")

    cap.release()
    cv2.destroyAllWindows()

    # Convert BGR → RGB, normalise to float [0,1]
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    img_float = frame_rgb.astype(np.float64) / 255.0

    # Save raw image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"{save_prefix}_{timestamp}.jpg"
    filepath  = os.path.join(settings.DATA_RAW, filename)
    cv2.imwrite(filepath, frame_bgr)
    print(f"[Camera] Image saved → {filepath}")

    return img_float


def capture_single_bgr() -> np.ndarray:
    """
    Capture one frame (BGR uint8) without interactive preview.
    Used during colour calibration loops.
    """
    cap = _open_camera()
    for _ in range(3):        # drain buffer
        cap.read()
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise RuntimeError("Failed to capture frame.")
    return frame
