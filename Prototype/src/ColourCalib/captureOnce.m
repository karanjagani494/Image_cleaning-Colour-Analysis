function filepath = captureOnce(paths)

% just captures a single image from the camera and saves it

cam = webcam("USB2.0 UVC PC Camera");

frame     = snapshot(cam);
timestamp = datestr(now, 'yyyymmdd_HHMMSS');
filename  = sprintf("calib_%s.jpg", timestamp);
filepath  = fullfile(paths.clrCard, filename);
imwrite(frame, filepath);

clear cam
end
