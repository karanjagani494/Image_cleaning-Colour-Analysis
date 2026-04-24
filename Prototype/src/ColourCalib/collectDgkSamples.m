function RGB_cam = collectDgkSamples(p, Lab_ref, Nsamples)

% goes through each colour card patch and captures multiple images
% then averages the RGB values to reduce noise

if nargin < 3, Nsamples = 10; end

[~, names] = dgk_lab();
n         = size(Lab_ref, 1);
RGB_cam   = zeros(n, 3);
crop_size = 100;

fprintf('\n=== DGK Colour Calibration ===\n');
fprintf('    %d patches × %d samples = %d captures total\n\n', ...
    n, Nsamples, n*Nsamples);
fprintf('Instructions:\n');
fprintf('  1. Point camera at patch centre\n');
fprintf('  2. Press Enter — camera settles then takes %d images automatically\n', Nsamples);
fprintf('  3. Move to next patch and repeat\n\n');

for i = 1:n
    fprintf('--- Patch %2d/%d : %-15s ---\n', i, n, names{i});
    fprintf('    Reference: L=%.1f  a=%.1f  b=%.1f\n', ...
        Lab_ref(i,1), Lab_ref(i,2), Lab_ref(i,3));
    fprintf('    Point camera at this patch then press Enter...');
    pause;

    % open camera for this patch
    cam = webcam("USB2.0 UVC PC Camera");

    % warmup so auto exposure settles before we start capturing
    fprintf('\n    Settling camera (wait)...');
    for w = 1:25
        snapshot(cam);
        pause(0.1);
    end
    pause(2);
    fprintf(' done.\n');

    fprintf('    Capturing %d images...\n', Nsamples);
    rgb_samples = zeros(Nsamples, 3);

    for k = 1:Nsamples
        frame = snapshot(cam);
        Iraw  = im2double(frame);

        % save to colour card folder
        timestamp = datestr(now, 'yyyymmdd_HHMMSS_FFF');
        filename  = sprintf('calib_%s_%02d_%s.jpg', names{i}, k, timestamp);
        filepath  = fullfile(p.clrCard, filename);
        imwrite(frame, filepath);

        % crop centre of image and take mean rgb
        [h, w, ~] = size(Iraw);
        y1 = max(1, round(h/2) - floor(crop_size/2));
        x1 = max(1, round(w/2) - floor(crop_size/2));
        crop = Iraw(y1:y1+crop_size-1, x1:x1+crop_size-1, :);

        rgb_samples(k,:) = [mean(mean(crop(:,:,1))), ...
                            mean(mean(crop(:,:,2))), ...
                            mean(mean(crop(:,:,3)))];

        fprintf('    Image %2d/%d — R=%.3f G=%.3f B=%.3f\n', ...
            k, Nsamples, rgb_samples(k,1), rgb_samples(k,2), rgb_samples(k,3));

        pause(0.3);
    end

    clear cam;

    % average all samples for this patch
    RGB_cam(i,:) = mean(rgb_samples, 1);

    fprintf('    >> Mean:  R=%.4f  G=%.4f  B=%.4f\n', ...
        RGB_cam(i,1), RGB_cam(i,2), RGB_cam(i,3));
    fprintf('    >> Std:   R=%.4f  G=%.4f  B=%.4f\n\n', ...
        std(rgb_samples(:,1)), std(rgb_samples(:,2)), std(rgb_samples(:,3)));

    % warn if readings were inconsistent
    if any(std(rgb_samples) > 0.05)
        fprintf('    WARNING: High variation (std > 0.05)\n\n');
    end
end

fprintf('=== Collection complete ===\n\n');
end
