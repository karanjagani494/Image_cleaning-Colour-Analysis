# checks if the captured image is sharp enough to process
# uses Laplacian variance — blurry images have weak edges so variance ends up very low

import cv2
import numpy as np
from config import settings


def blur_check(img: np.ndarray, threshold: float = None) -> tuple:
    if threshold is None:
        # use the value from settings if nothing is passed in
        threshold = settings.QC_BLUR_THRESHOLD

    # convert to grayscale uint8 — Laplacian needs a single channel
    gray = cv2.cvtColor((np.clip(img, 0, 1) * 255).astype(np.uint8),
                        cv2.COLOR_RGB2GRAY)

    lap      = cv2.Laplacian(gray.astype(np.float64), cv2.CV_64F)
    variance = float(np.var(lap))   # high variance = sharp, low = blurry
    is_sharp = variance >= threshold

    return variance, is_sharp
