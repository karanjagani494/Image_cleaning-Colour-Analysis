import numpy as np
from skimage.color import lab2rgb  # for converting Lab colour space back to RGB


def extract_colour_stats(lab: np.ndarray, mask: np.ndarray = None) -> dict:
    # pull out stats from just the skin pixels in the ROI
    if mask is None:
        # no mask means use ALL pixels in the image
        mask   = np.ones(lab.shape[:2], dtype=bool)
        masked = False
    else:
        masked = True

    L  = lab[:, :, 0][mask]
    A  = lab[:, :, 1][mask]
    B  = lab[:, :, 2][mask]

    stats = {
        "meanLAB": [float(np.mean(L)),  float(np.mean(A)),  float(np.mean(B))],
        "stdLAB":  [float(np.std(L)),   float(np.std(A)),   float(np.std(B))],
        "nPixels": int(np.sum(mask)),
        "coverage": float(np.mean(mask)),
        "masked":   masked,
        "cv_b": round(float(abs(np.std(B) / np.mean(B)) * 100), 2)
                if abs(float(np.mean(B))) > 0.1 else 0.0,
    }

    # convert Lab back to RGB so we can also report RGB stats
    # had to look this one up — skimage handles the L:[0,100] a/b:[-128,128] scaling internally
    rgb = lab2rgb(lab)

    R  = rgb[:, :, 0][mask]
    G  = rgb[:, :, 1][mask]
    B2 = rgb[:, :, 2][mask]

    stats["meanRGB"] = [float(np.mean(R)), float(np.mean(G)), float(np.mean(B2))]
    stats["stdRGB"]  = [float(np.std(R)),  float(np.std(G)),  float(np.std(B2))]

    return stats
