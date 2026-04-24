


% CALIBRATECAMERA  Run once to calibrate camera colour response.
%
% Workflow:
%   1. Place DGK colour checker under enclosure
%   2. Run this script
%   3. Point camera at each patch when prompted, press Enter per sample
%   4. CCM saved to data/results/ccm.mat
%   5. Pipeline will load CCM automatically on next run
%
% Time required: ~18 patches × 10 samples × 5 sec = ~15 minutes
% Only needs doing once (or if lighting/camera changes)

clc; clear; close all;
addpath(genpath("src"));
addpath("config");

p = paths();

% Ensure folders exist
if ~isfolder("data/results")
    mkdir("data/results");
end
if ~isfolder("data/colourCard")
    mkdir("data/colourCard");
end


% ---- Reference values ----
[Lab_ref, names] = dgk_lab();
fprintf('Loaded %d patch reference values\n', size(Lab_ref,1));

% ---- Collect camera measurements ----
Nsamples = 10;   % 10 captures per patch — enough to average out AE variation
RGB_cam  = collectDgkSamples(p, Lab_ref, Nsamples);

% ---- Compute CCM ----
[CCM, stats] = computeCCM(RGB_cam, Lab_ref);

% ---- Save ----
save("data/results/ccm.mat", "CCM", "RGB_cam", "Lab_ref", "names", "stats");
fprintf('CCM saved to data/results/ccm.mat\n');
fprintf('Mean ΔE after calibration: %.2f\n', stats.dE_after_mean);

% ---- Quick visual check ----
figure('Name', 'CCM Calibration Check');
subplot(1,2,1);
    dE = stats.dE_per_patch;
    bar([dE(:,1), dE(:,2)]);
    legend('Before CCM', 'After CCM');
    xlabel('Patch'); ylabel('ΔE');
    title('Colour Error per Patch');
    yline(2, 'r--', 'Perceptible');
    yline(5, 'r-',  'Significant');

subplot(1,2,2);
    % Show corrected vs reference colours as swatches
    RGB_ref       = max(0, min(1, lab2rgb(Lab_ref)));
    RGB_corrected = max(0, min(1, RGB_cam * CCM));
    swatch        = zeros(2, size(Lab_ref,1), 3);
    for i = 1:size(Lab_ref,1)
        swatch(1,i,:) = RGB_ref(i,:);
        swatch(2,i,:) = RGB_corrected(i,:);
    end
    imshow(imresize(swatch, [60, size(Lab_ref,1)*30], 'nearest'));
    title('Top: Reference   Bottom: Camera corrected');

disp('Calibration complete.');