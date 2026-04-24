import os
import sys
import time
from datetime import datetime

import numpy as np
import cv2
from flask import (
    Flask, Response, jsonify, render_template,
    request, send_from_directory,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

try:
    from src.utilities.camera import VideoCamera, get_camera, placeholder_frame
    from src.pipeline.runner import run_pipeline_on_file, PIPELINE_AVAILABLE
    from src.pipeline.debug_runner import run_debug_pipeline
    from src.utilities.data_manager import (
        sanitise_label,
        list_processed_images,
        load_all_metadata,
        delete_metadata_row
    )
except ImportError as _e:
    print(f"[WARN] Pipeline modules not importable: {_e}")
    print("[WARN] Image processing will be skipped — raw capture still works.")
    PIPELINE_AVAILABLE = False


app = Flask(__name__)

CAPTURED_DIR  = os.path.join(BASE_DIR, "data", "raw_images")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed_images")
for _d in (CAPTURED_DIR, PROCESSED_DIR):
    os.makedirs(_d, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}


@app.route("/")
def capture_page():
    ccm_ready = os.path.isfile(os.path.join(BASE_DIR, "data", "results", "ccm.npz"))
    return render_template("capture.html", ccm_ready=ccm_ready,
                           pipeline_available=PIPELINE_AVAILABLE)


@app.route("/gallery")
def gallery_page():
    images = list_processed_images(ALLOWED_EXTENSIONS) if PIPELINE_AVAILABLE else []
    return render_template("gallery.html", images=images)


@app.route("/calibrate")
def calibrate_page():
    return render_template("calibrate.html",
                           pipeline_available=PIPELINE_AVAILABLE)


@app.route("/debug")
def debug_page():
    return render_template("debug.html", pipeline_available=PIPELINE_AVAILABLE)


@app.route("/results")
def results_page():
    rows = load_all_metadata() if PIPELINE_AVAILABLE else []
    return render_template("results.html", rows=rows)


@app.route("/camera_status")
def camera_status():
    cam = get_camera()
    ccm_ready = os.path.isfile(os.path.join(BASE_DIR, "data", "results", "ccm.npz"))
    return jsonify({
        "available":          cam.is_opened(),
        "pipeline_available": PIPELINE_AVAILABLE,
        "ccm_ready":          ccm_ready,
    })


@app.route("/video_feed")
def video_feed():
    cam = get_camera()
    return Response(_generate_frames(cam),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


def _generate_frames(cam):
    while True:
        data = cam.get_frame()
        if data is None:
            data = placeholder_frame()
            time.sleep(0.5)
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + data + b"\r\n"


@app.route("/capture", methods=["POST"])
def capture_image():
    body_part = request.form.get("body_part", "").strip()
    label     = sanitise_label(body_part) if PIPELINE_AVAILABLE else "unlabelled"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_name  = f"raw_{label}_{timestamp}.jpg"
    raw_path  = os.path.join(CAPTURED_DIR, raw_name)

    cam   = get_camera()
    frame = cam.get_raw_frame()
    if frame is None:
        return jsonify({"success": False, "error": "Camera not available."}), 500

    try:
        cv2.imwrite(raw_path, frame)
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500

    if PIPELINE_AVAILABLE:
        pipe_result = run_pipeline_on_file(raw_path, body_part)
    else:
        pipe_result = {"error": "Pipeline libraries not installed."}

    response = {
        "success":       True,
        "filename":      raw_name,
        "body_part":     body_part or "Unlabelled",
        "message":       f"Image saved as {raw_name}",
        "pipeline":      pipe_result,
    }
    return jsonify(response)


@app.route("/debug_pipeline", methods=["POST"])
def debug_pipeline():
    if not PIPELINE_AVAILABLE:
        return jsonify({"error": "Pipeline libraries not installed."}), 500

    cam = get_camera()
    frame = cam.get_raw_frame()
    if frame is None:
        return jsonify({"error": "Camera not available."}), 500

    result = run_debug_pipeline(frame, CAPTURED_DIR)
    if "error" in result:
        return jsonify({"error": result["error"]}), 500

    return jsonify(result)


@app.route("/pipeline_status")
def pipeline_status():
    ccm_path  = os.path.join(BASE_DIR, "data", "results", "ccm.npz")
    ccm_ready = os.path.isfile(ccm_path)
    return jsonify({
        "pipeline_available": PIPELINE_AVAILABLE,
        "ccm_ready":          ccm_ready,
        "ccm_path":           ccm_path if ccm_ready else None,
    })


@app.route("/processed_images/<path:filename>")
def serve_processed_image(filename):
    return send_from_directory(PROCESSED_DIR, filename)


@app.route("/captured_images/<path:filename>")
def serve_captured_image(filename):
    return send_from_directory(CAPTURED_DIR, filename)


@app.route("/export/metadata.xlsx")
def export_metadata():
    xlsx = os.path.join(BASE_DIR, "data", "results", "metadata.xlsx")
    if not os.path.isfile(xlsx):
        return jsonify({"error": "No results yet."}), 404
    return send_from_directory(
        os.path.join(BASE_DIR, "data", "results"),
        "metadata.xlsx",
        as_attachment=True,
    )


@app.route("/delete_image", methods=["POST"])
def delete_image():
    filename = request.form.get("filename", "").strip()
    if not filename or ".." in filename or "/" in filename:
        return jsonify({"success": False, "error": "Invalid filename."}), 400
    path = os.path.join(PROCESSED_DIR, filename)
    if not os.path.isfile(path):
        return jsonify({"success": False, "error": "File not found."}), 404
    try:
        os.remove(path)
        if PIPELINE_AVAILABLE:
            delete_metadata_row(filename)
        return jsonify({"success": True, "filename": filename})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/results")
def api_results():
    if PIPELINE_AVAILABLE:
        return jsonify(load_all_metadata())
    return jsonify([])


@app.route("/shutdown", methods=["POST"])
def shutdown():
    import signal
    print("[Server] Received shutdown request. Stopping...")
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify({"success": True})


if __name__ == "__main__":
    print("=" * 55)
    print("  Neonatal Jaundice — Flask + Pipeline Web Server")
    print("=" * 55)
    print(f"  Pipeline available : {PIPELINE_AVAILABLE}")
    ccm_ok = os.path.isfile(os.path.join(BASE_DIR, "data", "results", "ccm.npz"))
    print(f"  CCM calibrated     : {ccm_ok}")
    if not ccm_ok:
        print("  ⚠  Run calibration at http://<pi-ip>:5050/calibrate")
    print(f"  Captured images    : {CAPTURED_DIR}")
    print(f"  Processed images   : {PROCESSED_DIR}")
    print("=" * 55)
    app.run(host="0.0.0.0", port=5050, debug=False, threaded=True)