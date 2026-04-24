import cv2
import numpy as np
from config import settings


def remove_hair(lab: np.ndarray, verbose: bool = False) -> tuple:
    # uses morphological closing at multiple angles to detect hair strands, then inpaints them
    L    = lab[:, :, 0]
    gray = np.clip(L / 100.0, 0.0, 1.0)

    se_length = max(int(round(settings.HAIR_SE_SCALE * min(gray.shape))), 5)

    gray_u8 = (gray * 255).astype(np.uint8)
    closed  = np.zeros_like(gray_u8)

    # run closing at 6 different angles (0°, 30°, 60°...) to catch hair in every direction
    for angle in range(0, 180, 30):
        klen = se_length * 2 + 1
        kern = np.zeros((klen, klen), dtype=np.uint8)
        cx, cy = klen // 2, klen // 2
        rad = np.deg2rad(angle)
        dx  = int(round(se_length * np.cos(rad)))
        dy  = int(round(se_length * np.sin(rad)))
        cv2.line(kern, (cx - dx, cy - dy), (cx + dx, cy + dy), 255, 1)

        cl     = cv2.morphologyEx(gray_u8, cv2.MORPH_CLOSE, kern)
        closed = np.maximum(closed, cl)

    # hair pixels are brighter than surrounding skin after closing — subtract to find them
    diff = closed.astype(np.float64) - gray_u8.astype(np.float64)
    diff = np.clip(diff, 0.0, None)

    d_min, d_max = diff.min(), diff.max()
    if d_max > d_min:
        hair_map_norm = (diff - d_min) / (d_max - d_min)
    else:
        hair_map_norm = np.zeros_like(diff)

    hair_map_u8 = (hair_map_norm * 255).astype(np.uint8)

    if np.any(hair_map_u8 > 0):
        _, mask = cv2.threshold(hair_map_u8, 0, 255,
                                cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        mask = np.zeros_like(hair_map_u8)

    mask = _remove_small_blobs(mask, settings.HAIR_MIN_AREA)

    disk2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask  = cv2.dilate(mask, disk2, iterations=1)

    coverage = float(np.count_nonzero(mask)) / mask.size
    if verbose:
        print(f"  Hair mask coverage: {coverage*100:.1f}%", end="")

    # if hair covers more than 40% of the image, its probably skin texture not actual hair — skip inpainting
    if coverage > settings.HAIR_MAX_MASK_PCT:
        if verbose:
            print(f" — TOO DENSE (>{settings.HAIR_MAX_MASK_PCT*100:.0f}%), "
                  "skipping inpainting")
        return lab.copy(), mask

    if verbose:
        print(" — inpainting")

    # inpaint each Lab channel separately — two passes so thick strands get filled properly
    lab_out = lab.copy()
    if np.any(mask):
        disk_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask_pass2 = cv2.dilate(mask, disk_small, iterations=1)

        for c in range(3):
            ch     = lab[:, :, c]
            ch_min = ch.min();  ch_max = ch.max()
            rng    = ch_max - ch_min if (ch_max - ch_min) > 0 else 1.0
            ch_u8  = ((ch - ch_min) / rng * 255).astype(np.uint8)

            p1 = cv2.inpaint(ch_u8, mask,       inpaintRadius=10,
                             flags=cv2.INPAINT_TELEA)
            p2 = cv2.inpaint(p1,   mask_pass2,  inpaintRadius=5,
                             flags=cv2.INPAINT_TELEA)

            lab_out[:, :, c] = p2.astype(np.float64) / 255.0 * rng + ch_min

    return lab_out, mask


def _remove_small_blobs(mask_u8: np.ndarray, min_area: int) -> np.ndarray:
    # removes connected components smaller than min_area pixels — filters out noise dots
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask_u8, connectivity=8)
    out = np.zeros_like(mask_u8)
    for lbl in range(1, n_labels):
        if stats[lbl, cv2.CC_STAT_AREA] >= min_area:
            out[labels == lbl] = 255
    return out
