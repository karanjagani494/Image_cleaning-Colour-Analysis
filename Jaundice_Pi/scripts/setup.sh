#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

echo "================================================"
echo "  Jaundice Pi — Raspberry Pi Setup"
echo "================================================"

echo ""
echo "[1/5] Installing system packages (sudo required)…"
sudo apt-get update -qq
sudo apt-get install -y \
    python3 python3-pip python3-venv \
    libopencv-dev \
    libatlas-base-dev \
    libhdf5-dev libhdf5-serial-dev \
    libopenjp2-7 \
    libtiff5 \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    v4l-utils

echo "  ✓ System packages installed"

echo ""
echo "[2/5] Creating Python virtual environment…"
python3 -m venv venv
source venv/bin/activate
echo "  ✓ Virtual environment created at ./venv"

echo ""
echo "[3/5] Installing Python packages (this may take a few minutes on Pi 3/4)…"
pip install --upgrade pip -q
pip install -r requirements.txt
echo "  ✓ Python packages installed"

echo ""
echo "[4/5] Creating data directories…"
mkdir -p data/raw_images data/processed_images data/results
echo "  ✓ Directories created"

echo ""
echo "[5/5] Setting permissions…"
chmod +x scripts/start.sh
echo "  ✓ scripts/start.sh is executable"

echo ""
echo "================================================"
echo "  Setup complete!"
echo ""
echo "  Next steps:"
echo "  1. Calibrate the camera (run once):"
echo "       source venv/bin/activate"
echo "       python calibrate.py"
echo ""
echo "  2. Start the web server:"
echo "       bash start.sh"
echo ""
echo "  3. Open in a browser:"
echo "       http://$(hostname -I | awk '{print $1}'):5050"
echo "================================================"
