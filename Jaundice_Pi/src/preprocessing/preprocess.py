import cv2
import numpy as np
from config import settings


def preprocess_image(img: np.ndarray) -> np.ndarray:
    # only the L (lightness) channel gets filtered here — a* and b* are left untouched
    I = img.copy()
    L = I[:, :, 0]

    # gaussian smooths out fine sensor noise
    if settings.NOISE_USE_GAUSSIAN:
        sigma = settings.NOISE_GAUSSIAN_SIGMA
        ksize = int(6 * sigma + 1) | 1
        L_u8 = np.clip(L / 100.0 * 255, 0, 255).astype(np.uint8)
        L_u8 = cv2.GaussianBlur(L_u8, (ksize, ksize), sigma)
        L    = L_u8.astype(np.float64) / 255.0 * 100.0

    if settings.NOISE_USE_MEDIAN:
        ksize = settings.NOISE_MEDIAN_KSIZE
        L_u8  = np.clip(L / 100.0 * 255, 0, 255).astype(np.uint8)
        L_u8  = cv2.medianBlur(L_u8, ksize)
        L     = L_u8.astype(np.float64) / 255.0 * 100.0

    if settings.NOISE_USE_BILATERAL:
        L_u8 = np.clip(L / 100.0 * 255, 0, 255).astype(np.uint8)
        L_u8 = cv2.bilateralFilter(
            L_u8,
            settings.NOISE_BILATERAL_D,
            settings.NOISE_BILATERAL_SIGMA_COLOR,
            settings.NOISE_BILATERAL_SIGMA_SPACE,
        )
        L = L_u8.astype(np.float64) / 255.0 * 100.0

    # CLAHE boosts contrast in dark areas without washing out bright ones
    if settings.CONTRAST_USE_CLAHE:
        L_norm = np.clip(L / 100.0, 0.0, 1.0)
        L_u8   = (L_norm * 255).astype(np.uint8)
        clahe  = cv2.createCLAHE(
            clipLimit=settings.CLAHE_CLIP_LIMIT,
            tileGridSize=settings.CLAHE_TILE_GRID,
        )
        L_eq = clahe.apply(L_u8)
        L    = L_eq.astype(np.float64) / 255.0 * 100.0

    # unsharp mask sharpening — amount is controlled by SHARPEN_AMOUNT in settings
    if settings.SHARPEN_ENABLE:
        L_norm  = np.clip(L / 100.0, 0.0, 1.0)
        L_u8    = (L_norm * 255).astype(np.uint8)
        blurred = cv2.GaussianBlur(L_u8, (0, 0), 3)
        L_u8    = cv2.addWeighted(L_u8, 1 + settings.SHARPEN_AMOUNT,
                                  blurred, -settings.SHARPEN_AMOUNT, 0)
        L = L_u8.astype(np.float64) / 255.0 * 100.0

    I[:, :, 0] = np.clip(L, 0.0, 100.0)
    return I
