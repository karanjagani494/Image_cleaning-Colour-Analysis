import os
import re
from datetime import datetime

# 3 levels up from here gets us to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed_images")

# pandas is needed for reading/writing the excel file
try:
    from config import settings
    import pandas as pd
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False


def sanitise_label(label: str) -> str:
    # strips spaces, lowercases, replaces anything that's not a letter or number with _
    label = label.strip().lower()
    label = re.sub(r"[^a-z0-9]+", "_", label)
    label = label.strip("_")
    return label or "unlabelled"


def _load_stats_map() -> dict:
    # loads Lab stats from metadata.xlsx so we can show them in the gallery
    if not PIPELINE_AVAILABLE:
        return {}
    try:
        xlsx = settings.METADATA_PATH
        if not os.path.isfile(xlsx):
            return {}
        df = pd.read_excel(xlsx)
        result = {}
        for _, row in df.iterrows():
            name = os.path.basename(str(row.get("image_name", "")))
            result[name] = {
                "mean_L": round(float(row.get("mean_L", 0)), 2),
                "mean_a": round(float(row.get("mean_a", 0)), 2),
                "mean_b": round(float(row.get("mean_b", 0)), 2),
            }
        return result
    except Exception:
        return {}


def load_all_metadata() -> list:
    if not PIPELINE_AVAILABLE:
        return []
    try:
        xlsx = settings.METADATA_PATH
        if not os.path.isfile(xlsx):
            return []
        df = pd.read_excel(xlsx)
        rows = []
        for _, row in df.iterrows():
            name = os.path.basename(str(row.get("image_name", "")))
            rows.append({
                "image_name": name,
                "image_path": str(row.get("image_path", "")),
                "mean_L":  round(float(row.get("mean_L", 0)), 2),
                "mean_a":  round(float(row.get("mean_a", 0)), 2),
                "mean_b":  round(float(row.get("mean_b", 0)), 2),
                "std_L":   round(float(row.get("std_L",  0)), 2),
                "std_a":   round(float(row.get("std_a",  0)), 2),
                "std_b":   round(float(row.get("std_b",  0)), 2),
                "url":     f"/processed_images/{name}" if name.startswith("processed_") else "",
            })
        return rows[::-1]   # newest first
    except Exception:
        return []


def delete_metadata_row(filename: str) -> None:
    if not PIPELINE_AVAILABLE:
        return
    try:
        xlsx = settings.METADATA_PATH
        if not os.path.isfile(xlsx):
            return
        df = pd.read_excel(xlsx)
        df = df[df["image_name"].apply(lambda x: os.path.basename(str(x)) != filename)]
        df.to_excel(xlsx, index=False)
    except Exception:
        pass


def list_processed_images(allowed_extensions) -> list:
    import os
    from datetime import datetime
    images = []
    try:
        stats_map = _load_stats_map()
        for fname in sorted(os.listdir(PROCESSED_DIR), reverse=True):
            if os.path.splitext(fname)[1].lower() in allowed_extensions:
                fpath = os.path.join(PROCESSED_DIR, fname)
                entry = {
                    "filename": fname,
                    "url":      f"/processed_images/{fname}",
                    "size":     os.path.getsize(fpath),
                    "modified": datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%d %H:%M"),
                    "stats":    stats_map.get(fname),
                }
                images.append(entry)
    except FileNotFoundError:
        os.makedirs(PROCESSED_DIR, exist_ok=True)
    return images
