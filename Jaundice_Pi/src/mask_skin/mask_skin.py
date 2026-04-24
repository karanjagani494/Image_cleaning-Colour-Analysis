import cv2
import numpy as np
from skimage.color import lab2rgb
from config import settings


def mask_skin(img_lab: np.ndarray) -> np.ndarray:
    # builds rejection masks for pixels that are too dark, too bright, or not red enough to be skin
    L   = img_lab[:, :, 0]
    rgb = np.clip(lab2rgb(img_lab), 0.0, 1.0)
    R   = rgb[:, :, 0]
    B   = rgb[:, :, 2]

    dark_mask   = L < settings.SKIN_L_LOW
    bright_mask = L > settings.SKIN_L_HIGH
    colour_mask = R < (B * 0.90)

    # small dark patches are likely pores — erode to find cores then dilate back to mask them
    pore_candidates = ((L < settings.SKIN_PORE_L) & ~dark_mask).astype(np.uint8) * 255
    r_erode = settings.SKIN_PORE_ERODE
    k_erode = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (2 * r_erode + 1, 2 * r_erode + 1))
    k_dilate = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (2 * (r_erode + 1) + 1, 2 * (r_erode + 1) + 1))
    pore_cores = cv2.erode(pore_candidates,  k_erode,  iterations=1)
    pore_mask  = cv2.dilate(pore_cores,      k_dilate, iterations=1).astype(bool)

    # combine all rejection masks and flip to get the clean skin pixels
    dirty = dark_mask | bright_mask | colour_mask | pore_mask
    mask  = (~dirty).astype(np.uint8) * 255

    k2   = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.erode(mask,  k2, iterations=1)
    mask = cv2.dilate(mask, k2, iterations=1)

    coverage = float(np.mean(mask > 0))

    if coverage < settings.SKIN_MIN_COVERAGE:
        print(f"  WARNING: maskSkin — only {coverage*100:.1f}% clean skin "
              f"(threshold: {settings.SKIN_MIN_COVERAGE*100:.0f}%)")

    print(f"  Skin mask: {coverage*100:.1f}% clean pixels  "
          f"(dark={np.mean(dark_mask)*100:.1f}%  "
          f"overexp={np.mean(bright_mask)*100:.1f}%  "
          f"pores={np.mean(pore_mask)*100:.1f}%)")

    if coverage < 0.02:
        print("  maskSkin fallback: returning full mask (coverage < 2%)")
        return np.ones(img_lab.shape[:2], dtype=bool)

    return (mask > 0)
