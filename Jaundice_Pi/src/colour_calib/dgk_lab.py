# Lab reference values for all 18 patches on the DGK 5x7 colour card
# layout is 6 columns x 3 rows — row 1 is greyscale, row 2 chromatic primaries, row 3 secondaries + skin tones
# these were verified against the physical card in April 2026

import numpy as np

PATCH_NAMES = [
    "White",       "Light Grey",  "Grey",
    "Mid Grey",    "Dark Grey",   "Black",
    "Red",         "Yellow",      "Lime Green",
    "Cyan",        "Dark Navy",   "Hot Pink",
    "Dark Red",    "Orange",      "Cyan Blue",
    "Magenta",     "Skin Tone 1", "Skin Tone 2",
]

LAB_REF = np.array([
    [100.0,   0.0,   0.0],   #  1 White
    [ 87.0,   0.0,   0.0],   #  2 Light Grey
    [ 73.0,   0.0,   0.0],   #  3 Grey
    [ 62.0,   0.0,   0.0],   #  4 Mid Grey
    [ 50.0,   0.0,   0.0],   #  5 Dark Grey
    [  0.0,   0.0,   0.0],   #  6 Black
    [ 52.0,  74.0,  54.0],   #  7 Red
    [ 95.0,  -6.0,  95.0],   #  8 Yellow
    [ 69.0, -43.0,  50.0],   #  9 Lime Green
    [ 72.0, -28.0, -28.0],   # 10 Cyan
    [ 25.0,  10.0, -30.0],   # 11 Dark Navy
    [ 55.0,  70.0,  -5.0],   # 12 Hot Pink
    [ 38.0,  47.0,  28.0],   # 13 Dark Red
    [ 62.0,  27.0,  52.0],   # 14 Orange
    [ 72.0, -17.0, -22.0],   # 15 Cyan Blue
    [ 52.0,  81.0,  -7.0],   # 16 Magenta
    [ 62.0,  15.0,  22.0],   # 17 Skin Tone 1
    [ 76.0,   8.0,  18.0],   # 18 Skin Tone 2
], dtype=np.float64)

def get_lab_ref():
    return LAB_REF.copy(), PATCH_NAMES
