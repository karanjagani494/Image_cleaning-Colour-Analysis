<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=32&pause=1000&color=C51A4A&center=true&vCenter=true&width=600&lines=🩺+Jaundice+Pi;Neonatal+Jaundice+Detection;Raspberry+Pi+%2B+Dermatoscope" alt="Typing SVG" />

<br/>

**A Raspberry Pi system for real-time neonatal skin imaging and CIE Lab colour analysis.**  
*Built with a USB digital dermatoscope, Flask web interface, and a full computer vision pipeline.*

<br/>

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20Server-000000?style=for-the-badge&logo=flask&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Hardware-C51A4A?style=for-the-badge&logo=raspberry-pi&logoColor=white)
![scikit-image](https://img.shields.io/badge/scikit--image-Image%20Processing-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![MATLAB](https://img.shields.io/badge/MATLAB-Pipeline%20Origin-0076A8?style=for-the-badge&logo=mathworks&logoColor=white)
![License](https://img.shields.io/badge/License-Academic-green?style=for-the-badge)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [MATLAB Origin](#-matlab-origin--python-translation)
- [Tech Stack](#-tech-stack)
- [How It Works](#-how-it-works)
- [Hardware Required](#-hardware-required)
- [Project Structure](#-project-structure)
- [Installation on Raspberry Pi](#-installation-on-raspberry-pi)
- [Colour Calibration](#-colour-calibration-run-once)
- [Starting the System](#-starting-the-system)
- [Connecting via Web Browser (Headless Pi)](#-connecting-via-web-browser-headless-pi)
- [Using the Web Interface](#-using-the-web-interface)
- [Application Pages](#-application-pages)
- [Pipeline Flow](#%EF%B8%8F-capture-pipeline-flow)
- [Performance](#-performance-benchmarks)
- [Troubleshooting](#-troubleshooting)

---

## 🩺 Overview

Jaundice Pi is a non-invasive neonatal jaundice screening tool. It uses a USB digital dermatoscope connected to a Raspberry Pi to capture close-up skin images and extract **CIE Lab colour values** — specifically the **b\* (yellow-blue axis)** which correlates with bilirubin levels in neonatal jaundice assessment.

The system runs a fully automated image processing pipeline and presents results through a clean browser-based web interface — no monitor or keyboard is needed on the Pi itself.

> ⚕️ *This system is a research prototype intended for academic and investigatory use. It is not a certified medical device.*

---

## 📁 MATLAB Project Structure (Original Prototype)

The original algorithm was developed in MATLAB before being translated to this Python/Raspberry Pi system. The MATLAB project is structured as follows:

```
MATLAB_Prototype/
│
├── main.m                    ← 🚀 Entry point — runs the full pipeline on an image
├── params.m                  ← ⚙️  All algorithm parameters (equivalent to config/settings.py)
│
├── hairRemoval.m             ← ✂️  Hair strand detection and inpainting
├── preprocessImage.m         ← 🧹 Noise reduction, CLAHE, sharpening on L-channel
├── maskSkin.m                ← 🎭 Multi-layer skin pixel segmentation
├── imageROI.m                ← 🎯 Fixed-position region of interest cropping
├── shadingCorrect.m          ← 💡 Retinex-style illumination field correction
├── extractColourStats.m      ← 📈 Mean/Std CIE Lab extraction on masked pixels
├── applyCCM.m                ← 🎨 Apply Colour Correction Matrix (RGB → Lab)
│
└── data/
    └── DGK_Lab_refs.mat      ← 🎨 18-patch DGK colour card CIE Lab reference values
```

### MATLAB Pipeline Order (`main.m`)

```matlab
% 1. Load raw image
Iraw = imread(imagePath);

% 2. Colour correction OR shading correction (mutually exclusive)
if useCCM
    shading_out = applyCCM(Iraw, CCM);      % RGB → calibrated Lab
else
    shading_out = shadingCorrect(Iraw);      % RGB → Lab (uncalibrated)
end

% 3. Hair removal
cl_out = hairRemoval(shading_out, params, verbose);

% 4. Preprocessing (noise, CLAHE, sharpen — all off by default)
processed_img = preprocessImage(cl_out, params);

% 5. ROI extraction (fixed position)
ROI_img = imageROI(processed_img);

% 6. Skin masking
[skinMask, ~] = maskSkin(ROI_img, params.mask);

% 7. Colour statistics
statsArray(i) = extractColourStats(ROI_img, skinMask);
```

### Key MATLAB Parameters (`params.m`)

| Parameter | MATLAB Name | Python Equivalent | Default |
|:---|:---|:---|:---:|
| Hair SE scale | `params.hair.seScale` | `HAIR_SE_SCALE` | `0.05` |
| Hair min area | `params.hair.minArea` | `HAIR_MIN_AREA` | `20` |
| Hair max coverage | `params.hair.maxMaskPct` | `HAIR_MAX_MASK_PCT` | `0.40` |
| Skin L low | `params.mask.skin_L_low` | `SKIN_L_LOW` | `30` |
| Skin L high | `params.mask.skin_L_high` | `SKIN_L_HIGH` | `92` |
| Pore L threshold | `params.mask.pore_L` | `SKIN_PORE_L` | `45` |
| Use Gaussian | `params.noise.useGaussian` | `NOISE_USE_GAUSSIAN` | `false` |
| Use CLAHE | `params.contrast.useCLAHE` | `CONTRAST_USE_CLAHE` | `false` |
| Use sharpen | `params.sharpen.useSharpen` | `SHARPEN_ENABLE` | `false` |

> 📌 *If you have access to the original MATLAB source files, the full `.m` code can be viewed alongside this Python implementation to compare the translation directly.*

---

## 🔬 MATLAB Origin & Python Translation

The image processing pipeline in this project is a **direct Python translation of an original MATLAB prototype**. The MATLAB codebase served as the algorithmic reference — every processing stage in Python replicates the exact behaviour of its MATLAB equivalent.

| MATLAB Function | Python Module | What It Does |
|:---|:---|:---|
| `hairRemoval.m` | `src/hair_removal/hair_removal.py` | Line-morphology hair detection + inpainting |
| `preprocessImage.m` | `src/preprocessing/preprocess.py` | Gaussian, CLAHE, sharpening on L-channel |
| `maskSkin.m` | `src/mask_skin/mask_skin.py` | Multi-layer pixel-rule skin segmentation |
| `imageROI.m` | `src/utilities/roi.py` | Region of interest extraction (improved: hair-aware grid search) |
| `shadingCorrect.m` | `src/preprocessing/shading_correct.py` | Retinex-style illumination correction |
| `extractColourStats.m` | `src/utilities/colour_stats.py` | Mean/Std Lab extraction on masked pixels |
| `applyCCM.m` | `src/colour_calib/colour_calib.py` | Colour Correction Matrix application (RGB → Lab) |

**Key translation decisions:**

- MATLAB's `strel('line')` → replaced with `cv2.line` drawn kernels for morphological hair closing
- MATLAB's `mat2gray` normalisation → replicated using min-max scaling before Otsu threshold
- MATLAB's `regionfill` → replaced with `cv2.inpaint` using TELEA algorithm (two-pass)
- MATLAB's `adapthisteq` → replaced with `cv2.createCLAHE` on the L-channel only
- MATLAB's `graythresh` (Otsu) → replaced with `cv2.THRESH_OTSU`
- ROI selection improved beyond MATLAB: Python uses a **mole-aware grid search** rather than a fixed position

> 📌 The MATLAB pipeline was developed as the original research prototype. This Python implementation matches it stage-for-stage, with select improvements noted above for the embedded Raspberry Pi environment.

---

## 🛠️ Tech Stack

| Layer | Technology | Role |
|:---|:---|:---|
| **Backend** | ![Flask](https://img.shields.io/badge/Flask-000?style=flat-square&logo=flask&logoColor=white) **Flask** | Python web framework — handles all HTTP routes, camera streaming (MJPEG), and pipeline triggering |
| **Image Processing** | ![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white) **OpenCV** | Morphological operations, Gaussian blur, bilateral filter, inpainting, colour space conversion |
| **Colour Science** | **scikit-image** | CIE Lab ↔ RGB ↔ XYZ conversion, SSIM calculation |
| **Numerical** | **NumPy** | Matrix operations, least-squares CCM fitting, statistical extraction |
| **Data Export** | **openpyxl** | Writing per-capture Lab values to `metadata.xlsx` |
| **Frontend** | **HTML / CSS / JavaScript** | Jinja2 templates rendered by Flask, MJPEG stream displayed in browser, fetch API for async capture |
| **Hardware Interface** | **OpenCV VideoCapture** | Reads frames from the USB dermatoscope via V4L2 on Linux |
| **Deployment** | **systemd** | Auto-starts the Flask server on Pi boot via `jaundice-pi.service` |
| **Algorithm Origin** | ![MATLAB](https://img.shields.io/badge/MATLAB-0076A8?style=flat-square&logo=mathworks&logoColor=white) **MATLAB** | Original prototype pipeline — fully translated to Python |

### Flask Web Server Architecture

The Flask application in `app.py` serves five main page routes and a set of API endpoints:

```
Browser Request
      ↓
Flask Route (app.py)
      ├── GET  /              → renders capture.html  (live feed page)
      ├── GET  /gallery       → renders gallery.html
      ├── GET  /results       → renders results.html
      ├── GET  /calibrate     → renders calibrate.html
      ├── GET  /debug         → renders debug.html
      ├── GET  /video_feed    → MJPEG stream (multipart/x-mixed-replace)
      ├── POST /capture       → grabs frame → runs pipeline → returns JSON
      ├── POST /debug_pipeline→ runs stage-by-stage → returns base64 images
      ├── GET  /api/results   → returns all metadata rows as JSON
      └── GET  /export/metadata.xlsx → sends file download
```

The camera is managed by a **background thread** (`VideoCamera` in `src/utilities/camera.py`) so the live MJPEG stream and the capture endpoint never block each other.

---

## ⚙️ How It Works

```
📷 Dermatoscope → Raspberry Pi → Flask Web Server → Browser on Any Device
                                       ↓
                    Raw Image → Hair Removal → CCM Colour Calibration
                             → ROI Selection → Skin Masking
                             → L* a* b* Extraction → Results Saved
```

The **b\*** value (yellow component of Lab) is the primary output. Elevated b\* indicates increased skin yellowing, which corresponds with higher bilirubin levels in neonatal jaundice.

---

## 🔌 Hardware Required

| Component | Details |
|:---|:---|
| 🍓 **Raspberry Pi** | Model 3B+, 4, or 5 — Pi 4/5 recommended |
| 🔬 **USB Digital Dermatoscope** | 640×640 resolution, built-in LED ring light |
| 💾 **MicroSD Card** | 16 GB minimum, Class 10 |
| 🌐 **Wi-Fi Network** | Pi and viewing device on same network |
| 🎨 **DGK Colour Card** | 18-patch colour card for CCM calibration |

---

## 📂 Project Structure

```
jaundice_pi/
│
├── app.py                    ← 🌐 Flask web server (all routes)
├── main.py                   ← 🚀 Entry point
├── requirements.txt
├── README.md
│
├── config/
│   └── settings.py           ← ⚙️  All tunable parameters (camera, pipeline thresholds)
│
├── src/                      ← 🧠 Image processing pipeline
│   ├── colour_calib/         ← 🎨 Colour calibration (CCM)
│   │   ├── calibrate.py      ←     Run once to build the matrix
│   │   ├── colour_calib.py   ←     CCM computation & application
│   │   └── dgk_lab.py        ←     DGK 18-patch Lab reference values
│   ├── hair_removal/         ← ✂️  Morphological hair detection + inpainting
│   │   └── hair_removal.py
│   ├── mask_skin/            ← 🎭 Multi-layer skin segmentation
│   │   └── mask_skin.py
│   ├── preprocessing/        ← 🧹 Blur check, denoising, shading correction
│   │   ├── blur_check.py
│   │   ├── preprocess.py
│   │   └── shading_correct.py
│   ├── pipeline/             ← 🚦 Full pipeline orchestration
│   │   ├── runner.py
│   │   └── debug_runner.py
│   └── utilities/            ← 🧰 Camera, ROI, stats, metadata helpers
│       ├── camera.py
│       ├── colour_stats.py
│       ├── data_manager.py
│       ├── io_utils.py
│       ├── metadata.py
│       └── roi.py
│
├── templates/                ← 🖥️  Jinja2 HTML pages
│   ├── base.html
│   ├── capture.html          ←     📸 Page 1 — Live capture
│   ├── gallery.html          ←     🖼️  Page 2 — Image gallery
│   ├── results.html          ←     📊 Page 3 — Data table
│   ├── calibrate.html        ←     🎨 Page 4 — Calibration guide
│   └── debug.html            ←     🐛 Page 5 — Pipeline debug view
│
├── static/
│   ├── css/style.css
│   └── js/app.js
│
├── scripts/                  ← 🛠️  Deployment scripts
│   ├── setup.sh              ←     One-shot Pi setup
│   ├── start.sh              ←     Start the server
│   └── jaundice-pi.service   ←     systemd auto-start service
│
└── data/                     ← 🗄️  Runtime data (gitignored)
    ├── raw_images/
    ├── processed_images/
    └── results/
        ├── ccm.npz           ← 🧮 Saved Colour Correction Matrix
        └── metadata.xlsx     ← 📈 Per-capture Lab statistics log
```

---

## 🚀 Installation on Raspberry Pi

### Step 1 — Copy the Project

Transfer the project folder onto the Raspberry Pi using a USB drive, `scp`, or by cloning from this repository:

```bash
git clone <repo-url> jaundice_pi
cd jaundice_pi
```

### Step 2 — Run the Setup Script

Run the setup script which installs all system packages and Python dependencies automatically:

```bash
bash scripts/setup.sh
```

This script performs the following in sequence:

| Step | Action |
|:---:|:---|
| 1/5 | Installs system packages — OpenCV, HDF5, image libraries via `apt` |
| 2/5 | Creates a Python virtual environment at `./venv` |
| 3/5 | Installs all Python packages from `requirements.txt` |
| 4/5 | Creates data directories (`raw_images`, `processed_images`, `results`) |
| 5/5 | Sets executable permissions on `start.sh` |

<details>
<summary>📋 Manual installation (alternative)</summary>

```bash
sudo apt update && sudo apt install -y \
    python3 python3-pip python3-venv \
    libopencv-dev libatlas-base-dev \
    libhdf5-dev libhdf5-serial-dev \
    libopenjp2-7 libjpeg-dev libpng-dev v4l-utils

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir -p data/raw_images data/processed_images data/results
```

</details>

---

## 🎨 Colour Calibration (Run Once)

Before capturing any patient images, the camera must be calibrated using the **DGK 18-patch colour card**. This generates a **Colour Correction Matrix (CCM)** which maps the camera's raw RGB output to accurate CIE Lab values.

```bash
source venv/bin/activate
python calibrate.py
```

The terminal will walk through each of the 18 colour patches one at a time:

1. Point the dermatoscope at the patch shown in the terminal
2. Press `SPACE` in the preview window to capture a sample
3. Draw a rectangle around the flat centre of the patch and press `ENTER`
4. Repeat 10 times per patch

The completed matrix is saved to `data/results/ccm.npz` and used automatically on every future capture.

> 💡 **Calibration only needs to be done once**, or whenever the camera or lighting conditions change significantly.

---

## ▶️ Starting the System

Once setup and calibration are complete, start the web server with:

```bash
bash scripts/start.sh
```

The terminal will confirm the server is running and display the address:

```
╔══════════════════════════════════════════╗
║   Jaundice Pi — Web Server               ║
╠══════════════════════════════════════════╣
║   http://localhost:5050                  ║
║   http://192.168.x.x:5050               ║
╚══════════════════════════════════════════╝
```

### Auto-Start on Boot (Optional)

To make the system start automatically whenever the Pi powers on:

```bash
sudo cp scripts/jaundice-pi.service /etc/systemd/system/
sudo systemctl enable jaundice-pi
sudo systemctl start jaundice-pi
```

---

## 🌐 Connecting via Web Browser (Headless Pi)

The Raspberry Pi runs in **headless mode** — no screen, mouse, or keyboard is attached. The entire interface is accessed through a browser on any device connected to the same Wi-Fi network.

### Find the Pi's IP Address

Run this on the Pi terminal (via SSH or directly):

```bash
hostname -I
```

This will output something like `192.168.1.42`. Note this address.

### Connect from Any Device

Open a browser on a **laptop, phone, or tablet** on the same Wi-Fi network and go to:

```
http://<Pi-IP-Address>:5050
```

**Example:** `http://192.168.1.42:5050`

> 📱 This works on any device — Windows, Mac, iPhone, Android. No app installation needed.

### Connecting via SSH (for terminal access)

To access the Pi terminal remotely from another machine:

```bash
ssh pi@192.168.1.42
```

Replace `192.168.1.42` with your Pi's actual IP address. The default password is `raspberry` unless changed.

---

## 📸 Using the Web Interface

### Capturing and Analysing an Image

1. Open the web interface in a browser (`http://<Pi-IP>:5050`)
2. The **Capture** page loads with a live camera feed from the dermatoscope
3. Enter the **body part location** (e.g. `forehead`, `chest`, `palm`) in the text field
4. Position the dermatoscope flat against the skin
5. Click **Capture & Analyse**

The system automatically runs the full pipeline and displays results on screen:

| Output | Description |
|:---|:---|
| **L\*** | Lightness value (0 = black, 100 = white) |
| **a\*** | Red-green axis |
| **b\*** | Yellow-blue axis — primary jaundice indicator |
| **Coverage** | Percentage of clean skin pixels in the ROI |
| **SSIM Score** | Structural similarity — measures how much hair removal changed the image |
| **Colour Swatch** | Visual preview of the measured skin colour |
| **Stage Timings** | Time taken by each pipeline stage in milliseconds |

---

## 🖥️ Application Pages

| Page | URL | Description |
|:---|:---|:---|
| 📸 **Capture** | `/` | Live camera feed, body part input, capture button, instant Lab results |
| 🖼️ **Gallery** | `/gallery` | Grid view of all processed images with Lab value chips |
| 📊 **Results** | `/results` | Full data table of all captures with export button |
| 🎨 **Calibrate** | `/calibrate` | Step-by-step calibration instructions and CCM status |
| 🐛 **Debug** | `/debug` | Stage-by-stage pipeline visualisation — shows intermediate images at each step |
| 📥 **Export** | `/export/metadata.xlsx` | Direct download of the full results spreadsheet |

---

## 🛤️ Capture Pipeline Flow

Every time an image is captured, it passes through this automated sequence:

```
📷 Raw Frame Captured
        ↓
🔍 Blur Check  ──── fails ──→  ❌ "Image too blurry" error returned
        ↓ pass
🧮 Colour Correction Matrix (CCM)  →  Converts RGB → CIE Lab
        ↓
✂️  Hair Removal  →  Line-morphology detection + TELEA inpainting
        ↓
🧹 Preprocessing  →  Gaussian filter on L-channel (Dermatoscope: on by default)
        ↓
🎯 ROI Selection  →  Mole-aware grid search for cleanest skin patch
        ↓
🎭 Skin Masking  →  Multi-layer filter (dark pixels, bright pixels, colour rule, pores)
        ↓
📈 Colour Stats  →  Mean/Std of L*, a*, b* on clean skin pixels only
        ↓
💾 Save Outputs  →  Processed image + metadata.xlsx updated
        ↓
✅ JSON Response  →  Web UI updates instantly
```

---

## 🏎️ Performance Benchmarks

| Device | Average Pipeline Time | Notes |
|:---|:---:|:---|
| 🍓 **Raspberry Pi 5** | `~1–2 s` | Excellent — recommended for clinical use |
| 🍓 **Raspberry Pi 4** (4 GB) | `~3–5 s` | Good, comfortable for regular use |
| 🍓 **Raspberry Pi 3B+** | `~10–18 s` | Workable — expect a noticeable delay |
| 🍓 **Raspberry Pi Zero 2W** | `~30–50 s` | Very slow, use loading indicators |

---

## 🔧 Troubleshooting

| Problem | Solution |
|:---|:---|
| ❌ **Camera not detected** | Run `ls /dev/video*` — verify `CAMERA_INDEX` in `config/settings.py` |
| ❌ **Pipeline import errors** | Run `source venv/bin/activate && pip install -r requirements.txt` |
| ❌ **No CCM calibration warning** | Run `python calibrate.py` before capturing any images |
| ❌ **Always fails blur check** | Lower `QC_BLUR_THRESHOLD` in `settings.py` (try `10`) |
| ❌ **Port 5050 already in use** | Run `sudo lsof -i :5050` and `kill -9 <PID>` to free it |
| ❌ **Cannot connect from browser** | Confirm both devices are on the same Wi-Fi — check `hostname -I` on Pi |
| ❌ **Black camera feed in browser** | Wait 5–10 seconds — USB dermatoscope needs warm-up time |
| ❌ **SSH connection refused** | Enable SSH: `sudo systemctl enable ssh && sudo systemctl start ssh` |

---

## 📦 Python Dependencies

```
flask
opencv-python
numpy
scikit-image
openpyxl
```

Install all with:
```bash
pip install -r requirements.txt
```

---

<div align="center">

**Built as part of a Final Year Engineering Project**  
*Anglia Ruskin University — 2025/2026*

![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Runs on Raspberry Pi](https://img.shields.io/badge/Runs%20on-Raspberry%20Pi-C51A4A?style=flat-square&logo=raspberry-pi&logoColor=white)
![Computer Vision](https://img.shields.io/badge/Computer%20Vision-OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white)

</div>
