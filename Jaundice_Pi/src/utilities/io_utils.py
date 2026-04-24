import cv2
import numpy as np
import glob
import os
from config import settings


def read_image_file(filepath: str) -> np.ndarray:
    bgr = cv2.imread(filepath)  # opencv reads as BGR by default (annoying but that's how it works)
    if bgr is None:
        raise FileNotFoundError(f"Cannot read image: {filepath}")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)  # flip to RGB for our pipeline
    return rgb.astype(np.float64) / 255.0  # scale to 0-1 range


def write_image(img: np.ndarray, filepath: str) -> None:
    img = np.clip(img, 0.0, 1.0)  # clamp just in case values are slightly out of range
    bgr = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)  # back to BGR for opencv
    cv2.imwrite(filepath, bgr)


def read_latest_raw_images(n: int = 5) -> list:
    pattern = os.path.join(settings.DATA_RAW, "raw_*.jpg")
    files   = glob.glob(pattern)
    files.sort(key=os.path.getmtime, reverse=True)
    return files[:n]
