import cv2
import numpy as np
from skimage.color import rgb2lab
from config import settings


def shading_correct(img: np.ndarray) -> np.ndarray:
    if not getattr(settings, 'SHADING_ENABLED', True):
        from skimage.color import rgb2lab
        return rgb2lab(img)
    lab = rgb2lab(img)
    L   = lab[:, :, 0].copy()

    sigma    = settings.SHADING_BLUR_SIGMA
    ksize    = int(6 * sigma + 1) | 1

    # heavily blur L to estimate the background illumination (the LED ring causes vignetting at edges)
    L_f32    = L.astype(np.float32)
    L_blur   = cv2.GaussianBlur(L_f32, (ksize, ksize), sigma).astype(np.float64)
    L_blur   = np.maximum(L_blur, 1e-6)

    # divide by the illumination map to flatten the shading — same idea as retinex
    L_corr   = (L / L_blur) * float(np.mean(L_blur))
    L_corr   = np.clip(L_corr, 0.0, 100.0)

    lab[:, :, 0] = L_corr
    return lab
