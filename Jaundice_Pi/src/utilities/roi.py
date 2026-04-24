import numpy as np
from config import settings


def extract_roi(img: np.ndarray,
                hair_mask: np.ndarray = None,
                skin_mask: np.ndarray = None,
                lab_img: np.ndarray = None) -> np.ndarray:
    h, w     = img.shape[:2]
    roi_size = settings.ROI_SIZE

    if hair_mask is not None or skin_mask is not None:
        L_map = lab_img[:, :, 0] if lab_img is not None else None
        x1, y1 = _best_roi_position(hair_mask, skin_mask, roi_size, h, w, L_map)
    else:
        x1, y1 = _fixed_roi_position(roi_size, h, w)

    return img[y1 : y1 + roi_size, x1 : x1 + roi_size]


def extract_roi_position(hair_mask: np.ndarray = None,
                         skin_mask: np.ndarray = None,
                         lab_img: np.ndarray = None) -> tuple:
    """Return (x1, y1) top-left corner without cropping. Used for debug box."""
    if hair_mask is not None or skin_mask is not None:
        ref   = hair_mask if hair_mask is not None else skin_mask
        h, w  = ref.shape[0], ref.shape[1]
        L_map = lab_img[:, :, 0] if lab_img is not None else None
        return _best_roi_position(hair_mask, skin_mask, settings.ROI_SIZE, h, w, L_map)
    return _fixed_roi_position(settings.ROI_SIZE,
                               settings.CAPTURE_HEIGHT, settings.CAPTURE_WIDTH)


def _fixed_roi_position(roi_size, h, w):
    y_center = int(round(h * settings.ROI_ROW_FRAC))
    x_center = int(round(w * settings.ROI_COL_FRAC))
    x1 = max(0, min(x_center - roi_size // 2, w - roi_size))
    y1 = max(0, min(y_center - roi_size // 2, h - roi_size))
    return x1, y1


def _best_roi_position(hair_mask, skin_mask, roi_size, h, w, L_map=None):
    # patches with average L* below this threshold are likely moles or dark lesions — skip them
    MOLE_L_THRESHOLD = 55.0

    if skin_mask is not None and hair_mask is not None:
        hair_bin  = (hair_mask > 0) if hair_mask.dtype != bool else hair_mask
        score_map = (skin_mask & ~hair_bin).astype(np.float32)
    elif skin_mask is not None:
        score_map = skin_mask.astype(np.float32)
    elif hair_mask is not None:
        score_map = 1.0 - (hair_mask > 0).astype(np.float32)
    else:
        score_map = np.ones((h, w), dtype=np.float32)

    stride     = max(roi_size // 2, 10)
    best_score = -1.0
    best_x1, best_y1 = _fixed_roi_position(roi_size, h, w)

    # step through the image in overlapping patches and score each one by how much clean skin it has
    for y in range(0, h - roi_size + 1, stride):
        for x in range(0, w - roi_size + 1, stride):

            if L_map is not None:
                mean_L = float(L_map[y : y + roi_size, x : x + roi_size].mean())
                if mean_L < MOLE_L_THRESHOLD:
                    continue

            s = score_map[y : y + roi_size, x : x + roi_size].sum()
            if s > best_score:
                best_score = s
                best_x1, best_y1 = x, y
                if best_score == roi_size * roi_size:
                    return best_x1, best_y1

    return best_x1, best_y1
