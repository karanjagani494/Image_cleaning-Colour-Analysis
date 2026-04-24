import os
import pandas as pd  # pandas is great for handling the excel file
from config import settings


def save_metadata(stats_list: list, file_list: list, pre_stats_list: list = None) -> None:
    # builds rows from the colour stats and appends them to metadata.xlsx
    rows = []
    for i, (stats, fpath) in enumerate(zip(stats_list, file_list)):
        name = os.path.basename(fpath)
        row = {
            "image_name": name,
            "image_path": os.path.join("processed_images", name),
            "mean_L": stats["meanLAB"][0],
            "mean_a": stats["meanLAB"][1],
            "mean_b": stats["meanLAB"][2],
            "std_L":  stats["stdLAB"][0],
            "std_a":  stats["stdLAB"][1],
            "std_b":  stats["stdLAB"][2],
            "cv_b":   stats.get("cv_b", None),
            "ssim":   stats.get("ssim", None),
        }
        # PRE-processed stats (raw ROI, all pixels, no skin mask)
        # captured for Ian's paired t-test: compare pre vs post colour values
        if pre_stats_list and i < len(pre_stats_list):
            pre = pre_stats_list[i]
            # store the "before" colour values alongside the "after" ones
            row["pre_mean_L"] = pre["meanLAB"][0]
            row["pre_mean_a"] = pre["meanLAB"][1]
            row["pre_mean_b"] = pre["meanLAB"][2]
            row["pre_std_L"]  = pre["stdLAB"][0]
            row["pre_std_a"]  = pre["stdLAB"][1]
            row["pre_std_b"]  = pre["stdLAB"][2]
        rows.append(row)

    df_new = pd.DataFrame(rows)
    out    = settings.METADATA_PATH

    if os.path.isfile(out):
        # if the excel file already exists, add to it rather than overwriting
        df_old = pd.read_excel(out)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_excel(out, index=False)
    print(f"[Metadata] Saved {len(rows)} rows → {out}")
