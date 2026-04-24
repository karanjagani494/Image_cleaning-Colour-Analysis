#!/usr/bin/env python3
# run this once before using the system — it builds the colour correction matrix (CCM)
# point the camera at each patch on the DGK colour card and follow the prompts

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from src.colour_calib.dgk_lab import get_lab_ref
from src.colour_calib.colour_calib import collect_patch_samples, compute_ccm, save_ccm


def main():
    print("=" * 60)
    print("  Neonatal Jaundice Pipeline — Colour Calibration")
    print("=" * 60)
    print("\nYou will be asked to capture each of the 18 colour card patches.")
    print("For each patch:")
    print("  - Point the camera squarely at the patch")
    print("  - Press ENTER in the terminal to open the preview")
    print("  - Press SPACE to capture")
    print("  - Draw a rectangle tightly inside the patch, press ENTER\n")

    input("Press ENTER to begin calibration...")

    # get the reference Lab values for all 18 patches on the colour card
    Lab_ref, _  = get_lab_ref()
    # capture what the camera sees for each patch
    RGB_cam     = collect_patch_samples()
    # compute the correction matrix that maps camera RGB to true Lab
    CCM         = compute_ccm(RGB_cam, Lab_ref)

    print("\n[Calib] Computed CCM:")
    print(CCM.round(5))

    save_ccm(CCM, RGB_cam, Lab_ref)
    print("\n✓ Calibration complete. You can now run:  python main.py")


if __name__ == "__main__":
    main()
