
# basically just sets up paths and starts the flask server
import os
import sys

# need to add the project folder to python's path so imports work
# without this, python can not find our src/ and config/ folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# pull in the flask app and some flags from app.py
from app import app, PIPELINE_AVAILABLE, CAPTURED_DIR, PROCESSED_DIR

if __name__ == "__main__":
    print("=" * 55)
    print("  Neonatal Jaundice — Flask + Image Cleaning Pipeline Web Server")
    print("=" * 55)
    print(f"  Pipeline available : {PIPELINE_AVAILABLE}")
    
    # check if the colour calibration file exists — if not, user needs to calibrate first
    ccm_ok = os.path.isfile(os.path.join(BASE_DIR, "data", "results", "ccm.npz"))
    print(f"  CCM calibrated     : {ccm_ok}")
    
    if not ccm_ok:
        print("  ⚠  Run calibration at http://<pi-ip>:5050/calibrate")
        
    print(f"  Captured images    : {CAPTURED_DIR}")
    print(f"  Processed images   : {PROCESSED_DIR}")
    print("=" * 55)
    
    # start the web server — 0.0.0.0 means anyone on the network can access it (not just localhost)
    # threaded=True so multiple people can use it at once without freezing
    app.run(host="0.0.0.0", port=5050, debug=False, threaded=True)
