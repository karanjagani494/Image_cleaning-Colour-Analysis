function captureImage(paths)

% captures 5 images from 5 different body locations
% user types in the location name before each capture

cam = webcam('USB2.0 UVC PC Camera');
disp('Starting capture for 5 body locations')

for i = 1:5
    location = input('Enter body location (forehead/arm/etc): ', 's');
    location = strrep(strtrim(location), ' ', '_');

    % let camera settle on this skin patch before capturing
    fprintf('Settling camera on %s (wait 3 sec)...\n', location);
    for w = 1:20
        snapshot(cam);
        pause(0.05);
    end
    pause(2);

    % show preview so user can check positioning then press enter to capture
    preview(cam); pause;
    closePreview(cam);

    frame     = snapshot(cam);
    timestamp = datestr(now, 'yyyymmdd_HHMMSS');
    filename  = sprintf('raw_%s_%s.jpg', location, timestamp);
    filepath  = fullfile(paths.dataRaw, filename);
    imwrite(frame, filepath);
    fprintf('Saved image: %s\n', filename);
end

clear cam
disp('Capture complete')
end
