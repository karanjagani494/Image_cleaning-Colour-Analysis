import os
import cv2
import base64
import numpy as np
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import settings
    from src.preprocessing.blur_check     import blur_check
    from src.preprocessing.preprocess     import preprocess_image
    from src.preprocessing.shading_correct import shading_correct
    from src.colour_calib.colour_calib    import apply_ccm, load_ccm
    from src.hair_removal.hair_removal    import remove_hair
    from src.mask_skin.mask_skin          import mask_skin
    from src.utilities.colour_stats        import extract_colour_stats
    from src.utilities.roi                 import extract_roi, extract_roi_position
    from skimage.color import lab2rgb as _l2r, rgb2lab as _r2l
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False


def _encode(img_float):
    img_u8 = (np.clip(img_float, 0, 1) * 255).astype(np.uint8)
    bgr = cv2.cvtColor(img_u8, cv2.COLOR_RGB2BGR)
    _, buf = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, 88])
    return "data:image/jpeg;base64," + base64.b64encode(buf).decode()

def _encode_lab(lab):
    return _encode(np.clip(_l2r(lab), 0, 1))

def _encode_mask(mask):
    m = (mask.astype(np.uint8) * 255) if mask.dtype == bool else mask
    _, buf = cv2.imencode(".jpg", m, [cv2.IMWRITE_JPEG_QUALITY, 88])
    return "data:image/jpeg;base64," + base64.b64encode(buf).decode()


def run_debug_pipeline(frame, captured_dir: str) -> dict:
    # runs the full pipeline step by step and returns each stage as a base64 image for the debug page
    if not PIPELINE_AVAILABLE:
        return {"error": "Pipeline libraries not installed."}

    stages = {}
    errors = {}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_path = os.path.join(captured_dir, f"debug_{timestamp}.jpg")
    cv2.imwrite(raw_path, frame)
    
    img = frame[:, :, ::-1].astype(np.float64) / 255.0
    stages["1_raw"] = {"label": "1. Raw capture", "img": _encode(img), "meta": ""}

    try:
        variance, is_sharp = blur_check(img)
        stages["1_raw"]["meta"] = f"Laplacian variance: {variance:.6f} — {'SHARP OK' if is_sharp else 'BLURRY FAIL'}"
    except Exception as e:
        errors["blur"] = str(e)

    I_lab = None
    try:
        ccm_path = os.path.join(BASE_DIR, "data", "results", "ccm.npz")
        if os.path.isfile(ccm_path):
            CCM   = load_ccm()
            I_lab = apply_ccm(img, CCM)
            stages["2_ccm_shading"] = {"label": "2. CCM applied → Lab (calibrated)",
                "img": _encode_lab(I_lab), "meta": "CCM loaded — shading correction skipped (MATLAB behaviour)"}
        else:
            I_lab = shading_correct(img)
            stages["2_ccm_shading"] = {"label": "2. Shading corrected → Lab (no CCM)",
                "img": _encode_lab(I_lab), "meta": "No CCM — shadingCorrect converts RGB→Lab"}
    except Exception as e:
        errors["ccm_shading"] = str(e)
        I_lab = _r2l(img)

    I_hair = I_lab; final_mask = np.zeros(img.shape[:2], dtype=np.uint8)
    try:
        se_length = max(int(round(settings.HAIR_SE_SCALE * min(img.shape[:2]))), 5)
        gray_u8   = (np.clip(I_lab[:,:,0]/100.0, 0, 1)*255).astype(np.uint8)
        closed    = np.zeros_like(gray_u8)
        for angle in range(0, 180, 30):
            klen = se_length*2+1; kern = np.zeros((klen,klen),dtype=np.uint8)
            cx,cy = klen//2, klen//2; rad=np.deg2rad(angle)
            dx=int(round(se_length*np.cos(rad))); dy=int(round(se_length*np.sin(rad)))
            cv2.line(kern,(cx-dx,cy-dy),(cx+dx,cy+dy),255,1)
            closed = np.maximum(closed, cv2.morphologyEx(gray_u8,cv2.MORPH_CLOSE,kern))
        diff = np.clip(closed.astype(np.float64)-gray_u8.astype(np.float64),0,None)
        d_min,d_max = diff.min(),diff.max()
        hair_norm = ((diff-d_min)/(d_max-d_min)*255).astype(np.uint8) if d_max>d_min else np.zeros_like(gray_u8)
        stages["3a_hair_map"] = {"label": f"3a. Hair diff map (SE={se_length}px, mat2gray)",
            "img": _encode_mask(hair_norm),
            "meta": f"Max:{int(hair_norm.max())} Mean:{hair_norm.mean():.1f} — mat2gray normalised (matches MATLAB)"}
        _, mask_otsu = cv2.threshold(hair_norm,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) if np.any(hair_norm>0) else (None,np.zeros_like(hair_norm))
        stages["3b_hair_mask"] = {"label": "3b. Hair mask (Otsu on normalised map)",
            "img": _encode_mask(mask_otsu),
            "meta": f"Coverage: {np.count_nonzero(mask_otsu)/mask_otsu.size*100:.1f}%"}
        I_hair, final_mask = remove_hair(I_lab, verbose=True)
        fc = np.count_nonzero(final_mask)/final_mask.size
        stages["3c_hair_result"] = {"label": "3c. After hair removal (inpainted)",
            "img": _encode_lab(I_hair),
            "meta": f"Coverage:{fc*100:.1f}% — {'Inpainted OK' if fc < settings.HAIR_MAX_MASK_PCT else 'TOO DENSE skipped'}"}
    except Exception as e:
        errors["hair"] = str(e)

    I_processed = I_hair
    try:
        I_processed = preprocess_image(I_hair)
        stages["4_preprocess"] = {"label": "4. Preprocessed (L-channel only — matches MATLAB)",
            "img": _encode_lab(I_processed),
            "meta": f"Gaussian={'ON' if settings.NOISE_USE_GAUSSIAN else 'OFF'}  "
                    f"CLAHE={'ON' if settings.CONTRAST_USE_CLAHE else 'OFF'}  "
                    f"(MATLAB defaults: both OFF)"}
    except Exception as e:
        errors["preprocess"] = str(e)

    roi_lab = None
    try:
        roi_lab = extract_roi(I_processed, final_mask, lab_img=I_processed)
        roi_rgb  = np.clip(_l2r(roi_lab), 0, 1)
        full_rgb = np.clip(_l2r(I_processed), 0, 1).copy()
        h, w     = full_rgb.shape[:2]; rs = settings.ROI_SIZE
        x1, y1  = extract_roi_position(final_mask, lab_img=I_processed)
        full_u8  = (full_rgb*255).astype(np.uint8)
        cv2.rectangle(full_u8,(x1,y1),(x1+rs,y1+rs),(0,255,0),3)
        stages["5a_roi_loc"] = {"label": "5a. ROI location (green box — auto hair-aware)",
            "img": _encode(full_u8.astype(np.float64)/255),
            "meta": f"Python improvement: picks cleanest patch. Top-left:({x1},{y1}) {rs}x{rs}px"}
        stages["5b_roi_crop"] = {"label": "5b. ROI crop", "img": _encode(roi_rgb), "meta": ""}
    except Exception as e:
        errors["roi"] = str(e)

    skin_mask = np.ones(roi_lab.shape[:2], dtype=bool) if roi_lab is not None else None
    try:
        skin_mask = mask_skin(roi_lab)
        coverage  = float(np.mean(skin_mask))
        base_rgb = np.clip(_l2r(roi_lab), 0, 1).copy()
        base_rgb[~skin_mask] = base_rgb[~skin_mask] * 0.3
        stages["6_skin"] = {"label": "6. Skin mask on ROI (MATLAB multi-layer rules)",
            "img": _encode(base_rgb),
            "meta": f"Coverage:{coverage*100:.1f}% — dark<{settings.SKIN_L_LOW} / bright>{settings.SKIN_L_HIGH} / colour-rule / pores"}
    except Exception as e:
        errors["skin"] = str(e)

    try:
        stats = extract_colour_stats(roi_lab, skin_mask)
        L_m,a_m,b_m = stats["meanLAB"]
        stages["7_stats"] = {"label": "7. Colour stats (extractColourStats)", "img": None,
            "meta": f"L*={L_m:.2f}  a*={a_m:.2f}  b*={b_m:.2f}  Coverage={stats['coverage']*100:.1f}%  nPx={stats['nPixels']}"}
    except Exception as e:
        errors["stats"] = str(e)

    return {
        "stages": [{"key": k, "label": v["label"], "img": v.get("img"), "meta": v.get("meta","")}
                   for k, v in sorted(stages.items())],
        "errors": errors,
    }
