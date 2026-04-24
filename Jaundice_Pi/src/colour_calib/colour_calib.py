import cv2
import numpy as np
import os
from skimage.color import lab2xyz, xyz2lab, rgb2lab, lab2rgb

from config import settings
from src.colour_calib.dgk_lab import get_lab_ref
from src.utilities.debug_camera import capture_single_bgr


def apply_ccm(img_rgb: np.ndarray, CCM: np.ndarray) -> np.ndarray:
    # matrix multiply maps each pixel from camera RGB to XYZ colour space, then converts to Lab
    h, w, _ = img_rgb.shape
    RGB      = img_rgb.reshape(-1, 3).astype(np.float64)
    XYZ      = RGB @ CCM
    XYZ      = np.clip(XYZ, 0.0, None)

    XYZ_img  = XYZ.reshape(h, w, 3)
    Lab      = xyz2lab(XYZ_img)
    return Lab


def save_ccm(CCM: np.ndarray, RGB_cam: np.ndarray, Lab_ref: np.ndarray) -> None:
    os.makedirs(os.path.dirname(settings.CCM_PATH), exist_ok=True)
    np.savez(settings.CCM_PATH, CCM=CCM, RGB_cam=RGB_cam, Lab_ref=Lab_ref)
    print(f"[Calib] CCM saved → {settings.CCM_PATH}")


def load_ccm() -> np.ndarray:
    if not os.path.isfile(settings.CCM_PATH):
        raise FileNotFoundError(
            f"CCM not found at {settings.CCM_PATH}. "
            "Run calibration first: python calibrate.py"
        )
    data = np.load(settings.CCM_PATH)
    return data["CCM"]


def compute_ccm(RGB_cam: np.ndarray, Lab_ref: np.ndarray) -> np.ndarray:
    # least squares fit — finds the 3x3 matrix that maps camera RGB to the reference XYZ values
    XYZ_ref = lab2xyz(Lab_ref)
    CCM, _, _, _ = np.linalg.lstsq(RGB_cam, XYZ_ref, rcond=None)
    return CCM


def _measure_patch_bgr(frame_bgr: np.ndarray) -> np.ndarray:
    clone  = frame_bgr.copy()
    roi    = cv2.selectROI("Draw ROI on colour patch — press ENTER/SPACE to confirm",
                           clone, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()

    x, y, bw, bh = [int(v) for v in roi]
    if bw == 0 or bh == 0:
        raise ValueError("Empty ROI selected.")

    patch = frame_bgr[y:y+bh, x:x+bw]
    patch_rgb = cv2.cvtColor(patch, cv2.COLOR_BGR2RGB).astype(np.float64) / 255.0
    return patch_rgb.reshape(-1, 3).mean(axis=0)


def collect_patch_samples(n_samples: int = None) -> np.ndarray:
    if n_samples is None:
        n_samples = settings.CCM_SAMPLES_PER_PATCH

    Lab_ref, names = get_lab_ref()
    n_patches      = len(names)
    RGB_cam        = np.zeros((n_patches, 3), dtype=np.float64)

    for i, name in enumerate(names):
        print(f"\n=== Patch {i+1}/{n_patches}: {name} ===")
        samples = np.zeros((n_samples, 3))

        for k in range(n_samples):
            print(f"  Sample {k+1}/{n_samples}: Press SPACE in the preview window to capture.")
            input("  [Enter] when camera is positioned, then watch the preview.")
            frame_bgr  = capture_single_bgr()
            samples[k] = _measure_patch_bgr(frame_bgr)
            print(f"    RGB = {samples[k].round(4)}")

        RGB_cam[i] = samples.mean(axis=0)
        print(f"  Mean RGB for '{name}': {RGB_cam[i].round(4)}")

    return RGB_cam
