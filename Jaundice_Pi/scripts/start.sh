#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

PORT="${2:-5050}"
VENV="$PROJECT_DIR/venv"

if [ -d "$VENV" ]; then
    source "$VENV/bin/activate"
    echo "[start] Using virtualenv: $VENV"
else
    echo "[start] No virtualenv found — using system Python"
fi

python3 -c "import flask, cv2, numpy, skimage" 2>/dev/null || {
    echo "[start] Installing dependencies…"
    pip install -r requirements.txt
}

CCM_FILE="$PROJECT_DIR/data/results/ccm.npz"
if [ ! -f "$CCM_FILE" ]; then
    echo ""
    echo "  ⚠  WARNING: No colour calibration found."
    echo "     Run 'python calibrate.py' before capturing images."
    echo "     Or visit http://$(hostname -I | awk '{print $1}'):$PORT/calibrate"
    echo ""
fi

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   Jaundice Pi — Web Server               ║"
echo "  ╠══════════════════════════════════════════╣"
echo "  ║   http://localhost:$PORT                    ║"
echo "  ║   http://$(hostname -I | awk '{print $1}'):$PORT             ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

python3 app.py
