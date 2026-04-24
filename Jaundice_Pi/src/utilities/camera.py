import cv2
import threading
import numpy as np

from config import settings

CAMERA_TIMEOUT = 5

class VideoCamera:

    def __init__(self, camera_index: int = 0, timeout: int = CAMERA_TIMEOUT):
        self.lock = threading.Lock()
        self.cap  = None
        self._open_camera(camera_index, timeout)

    def _open_camera(self, idx, timeout):
        result = {"cap": None}

        def _open():
            try:
                cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
                if not cap.isOpened():
                    cap = cv2.VideoCapture(idx)
                if not cap.isOpened():
                    return
                cap.set(cv2.CAP_PROP_FRAME_WIDTH,  settings.CAPTURE_WIDTH)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.CAPTURE_HEIGHT)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                # flush the first few frames — USB cameras often return stale/bad frames on startup
                for _ in range(5):
                    cap.read()
                result["cap"] = cap
            except Exception:
                pass

        t = threading.Thread(target=_open, daemon=True)
        t.start()
        t.join(timeout=timeout)
        if t.is_alive():
            print("[WARN] Camera open timed out — running without camera.")
            self.cap = None
        else:
            self.cap = result["cap"]

    def is_opened(self) -> bool:
        return self.cap is not None and self.cap.isOpened()

    def get_frame(self):
        if not self.is_opened():
            return None
        with self.lock:
            ok, frame = self.cap.read()
        if not ok or frame is None:
            return None
        _, jpeg = cv2.imencode(".jpg", frame)
        return jpeg.tobytes()

    def get_raw_frame(self):
        if not self.is_opened():
            return None
        with self.lock:
            ok, frame = self.cap.read()
        return frame if ok else None

    def release(self):
        if self.cap:
            with self.lock:
                self.cap.release()


_camera = None
_camera_lock = threading.Lock()


def get_camera() -> VideoCamera:
    global _camera
    with _camera_lock:
        if _camera is None:
            _camera = VideoCamera(0)
    return _camera


# cached placeholder frame shown in the browser when no camera is connected
_PLACEHOLDER: bytes | None = None

def placeholder_frame() -> bytes:
    global _PLACEHOLDER
    if _PLACEHOLDER is None:
        img = np.zeros((settings.CAPTURE_HEIGHT, settings.CAPTURE_WIDTH, 3), dtype=np.uint8)
        img[:] = (30, 30, 30)
        cv2.putText(img, "Camera not available", (50, settings.CAPTURE_HEIGHT//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 140, 255), 2, cv2.LINE_AA)
        _, buf = cv2.imencode(".jpg", img)
        _PLACEHOLDER = buf.tobytes()
    return _PLACEHOLDER
