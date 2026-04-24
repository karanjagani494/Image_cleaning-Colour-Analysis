import os

# paths — all data goes under the data/ folder at project root
PROJECT_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW       = os.path.join(PROJECT_ROOT, "data", "raw_images")
DATA_PROCESSED = os.path.join(PROJECT_ROOT, "data", "processed_images")
DATA_RESULTS   = os.path.join(PROJECT_ROOT, "data", "results")
CCM_PATH       = os.path.join(DATA_RESULTS, "ccm.npz")
METADATA_PATH  = os.path.join(DATA_RESULTS, "metadata.xlsx")

for _d in (DATA_RAW, DATA_PROCESSED, DATA_RESULTS):
    os.makedirs(_d, exist_ok=True)

# camera
CAMERA_INDEX         = 0
CAPTURE_WIDTH        = 640
CAPTURE_HEIGHT       = 640
CAMERA_WARMUP_FRAMES = 3

# quality control
QC_BLUR_THRESHOLD = 30
QC_MIN_VALID_PCT  = 0.30

# shading correction
SHADING_ENABLED    = False
SHADING_BLUR_SIGMA = 40

# hair removal
HAIR_SE_SCALE     = 0.05
HAIR_MIN_AREA     = 20
HAIR_MAX_MASK_PCT = 0.40

# noise reduction — only Gaussian is on by default
NOISE_USE_GAUSSIAN          = True
NOISE_GAUSSIAN_SIGMA        = 0.8
NOISE_USE_MEDIAN            = False
NOISE_MEDIAN_KSIZE          = 3
NOISE_USE_BILATERAL         = False
NOISE_BILATERAL_D           = 5
NOISE_BILATERAL_SIGMA_COLOR = 15
NOISE_BILATERAL_SIGMA_SPACE = 15

# contrast and sharpening
CONTRAST_USE_CLAHE = False
CLAHE_CLIP_LIMIT   = 0.02
CLAHE_TILE_GRID    = (4, 4)

SHARPEN_ENABLE = False
SHARPEN_AMOUNT = 2.0

# skin mask thresholds
SKIN_L_LOW        = 30
SKIN_L_HIGH       = 92
SKIN_PORE_L       = 45
SKIN_PORE_ERODE   = 3
SKIN_MIN_COVERAGE = 0.15

# ROI
ROI_SIZE     = 150
ROI_ROW_FRAC = 0.50
ROI_COL_FRAC = 0.50

# colour calibration
CCM_SAMPLES_PER_PATCH = 10
