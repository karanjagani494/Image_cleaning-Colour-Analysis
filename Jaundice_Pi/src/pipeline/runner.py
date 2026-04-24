import os
import re
import time
import traceback
import numpy as np
import cv2
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed_images")
os.makedirs(PROCESSED_DIR, exist_ok=True)

try:
    from config import settings
    from src.utilities.io_utils            import read_image_file, write_image
    from src.utilities.colour_stats        import extract_colour_stats
    from src.utilities.roi                 import extract_roi
    from src.utilities.metadata            import save_metadata
    from src.preprocessing.blur_check     import blur_check
    from src.preprocessing.preprocess     import preprocess_image
    from src.preprocessing.shading_correct import shading_correct
    from src.colour_calib.colour_calib    import apply_ccm, load_ccm
    from src.hair_removal.hair_removal    import remove_hair
    from src.mask_skin.mask_skin          import mask_skin
    from skimage.color                    import lab2rgb
    PIPELINE_AVAILABLE = True
except ImportError as _e:
    print(f"[WARN] Pipeline modules not importable: {_e}")
    PIPELINE_AVAILABLE = False


def sanitise_label(label: str) -> str:
    label = label.strip().lower()
    label = re.sub(r"[^a-z0-9]+", "_", label)
    label = label.strip("_")          # remove leading/trailing underscores
    return label or "unlabelled"


def _ms(t_start: float) -> int:
    return int((time.perf_counter() - t_start) * 1000)


def _serialise_stats(stats: dict) -> dict:
    return {
        "meanLAB":  [round(v, 2) for v in stats["meanLAB"]],
        "stdLAB":   [round(v, 2) for v in stats["stdLAB"]],
        "meanRGB":  [round(v, 4) for v in stats["meanRGB"]],
        "stdRGB":   [round(v, 4) for v in stats["stdRGB"]],
        "nPixels":  int(stats["nPixels"]),
        "coverage": round(float(stats["coverage"]) * 100, 1),
        "cv_b":     round(float(stats.get("cv_b", 0)), 2),
        "ssim":     stats.get("ssim"),   # float or None
    }


def run_pipeline_on_file(raw_filepath: str, body_part: str) -> dict:
    # runs all pipeline stages in order and times each one — returns a result dict for the frontend
    result = {"success": False, "stats": None, "processed": None,
              "error": None, "stages": {}}

    if not PIPELINE_AVAILABLE:
        result["error"] = "Pipeline libraries not installed."
        return result

    ccm_path  = os.path.join(BASE_DIR, "data", "results", "ccm.npz")
    ccm_found = os.path.isfile(ccm_path)

    try:
        t0 = time.perf_counter()

        img = read_image_file(raw_filepath)
        result["stages"]["load_ms"] = _ms(t0)

        t1 = time.perf_counter()
        variance, is_sharp = blur_check(img)
        result["stages"]["blur_ms"] = _ms(t1)
        if not is_sharp:
            result["error"] = (
                f"Image is too blurry (variance {variance:.6f}). "
                "Please focus the camera and try again."
            )
            return result

        t2 = time.perf_counter()
        if ccm_found:
            CCM   = load_ccm()
            I_lab = apply_ccm(img, CCM)
            result["stages"]["ccm_ms"] = _ms(t2)
        else:
            I_lab = shading_correct(img)
            result["ccm_skipped"] = True
            result["stages"]["shading_ms"] = _ms(t2)

        t3 = time.perf_counter()
        I_hair, hair_mask = remove_hair(I_lab, verbose=True)
        hair_coverage = float(np.count_nonzero(hair_mask)) / hair_mask.size
        print(f"[Hair] coverage: {hair_coverage*100:.1f}%")
        result["stages"]["hair_ms"] = _ms(t3)
        result["stages"]["hair_coverage_pct"] = round(hair_coverage * 100, 1)

        t4 = time.perf_counter()
        I_processed = preprocess_image(I_hair)
        result["stages"]["preprocess_ms"] = _ms(t4)

        t5 = time.perf_counter()
        roi_lab = extract_roi(I_processed, hair_mask, lab_img=I_processed)
        result["stages"]["roi_ms"] = _ms(t5)

        t6 = time.perf_counter()
        skin_mask = mask_skin(roi_lab)
        coverage  = float(np.mean(skin_mask))
        result["stages"]["skin_ms"] = _ms(t6)

        if coverage < 0.05:
            result["error"] = (
                f"Skin coverage too low ({coverage*100:.1f}%). "
                "Check lighting and position."
            )
            return result

        t7 = time.perf_counter()
        stats = extract_colour_stats(roi_lab, skin_mask)
        result["stages"]["stats_ms"] = _ms(t7)

        t8 = time.perf_counter()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        label     = sanitise_label(body_part)
        proc_name = f"processed_{label}_{timestamp}.jpg"
        proc_path = os.path.join(PROCESSED_DIR, proc_name)
        write_image(lab2rgb(I_processed), proc_path)
        result["stages"]["save_ms"] = _ms(t8)

        try:
            try:
                from skimage.metrics import structural_similarity as ssim_fn
            except ImportError:
                from skimage.measure import compare_ssim as ssim_fn
                
            raw_bgr  = cv2.imread(raw_filepath)
            proc_bgr = cv2.imread(proc_path)
            if raw_bgr is not None and proc_bgr is not None:
                if raw_bgr.shape != proc_bgr.shape:
                    proc_bgr = cv2.resize(proc_bgr, (raw_bgr.shape[1], raw_bgr.shape[0]))
                raw_g  = cv2.cvtColor(raw_bgr,  cv2.COLOR_BGR2GRAY)
                proc_g = cv2.cvtColor(proc_bgr, cv2.COLOR_BGR2GRAY)
                ssim_score = round(float(ssim_fn(raw_g, proc_g, data_range=255)), 4)
                stats["ssim"] = ssim_score
        except Exception as e:
            print(f"SSIM Error: {e}")
            stats["ssim"] = None

        save_metadata([stats], [proc_path])

        result["success"]   = True
        result["stats"]     = _serialise_stats(stats)
        result["processed"] = proc_name
        result["stages"]["total_ms"] = _ms(t0)

    except Exception as exc:
        result["error"] = str(exc)
        traceback.print_exc()

    return result