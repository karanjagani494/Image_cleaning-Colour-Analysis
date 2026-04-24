clc; clear; close all;

addpath(genpath("src"));
addpath("config");

p      = paths();
params = params();

% make sure output folder exist
if ~isfolder(p.processesOutput)
    mkdir(p.processesOutput);
end

% capture 5 images from different locations
captureImage(p);

fileList = readImages(p);   % get the last 5 raw images

% setup stats array to store results for each image
statsArray = repmat( ...
    struct('meanLAB',zeros(1,3), ...
    'stdLAB',zeros(1,3), ...
    'nPixels',0, ...
    'coverage',0, ...
    'masked',false, ...
    'meanRGB',zeros(1,3), ...
    'stdRGB',zeros(1,3), ...
    'ssim_raw_processed',0), ...
    length(fileList), 1);

% load colour correction matrix if it exists
ccm_path = "data/results/ccm.mat";
if isfile(ccm_path)
    ccm_data  = load(ccm_path, "CCM");
    CCM       = ccm_data.CCM;
    useCCM    = true;
    fprintf('Colour calibration (CCM) loaded.\n');
else
    CCM    = [];
    useCCM = false;
    fprintf('WARNING: No CCM found at %s\n', ccm_path);
    fprintf('         Run calibrateCamera.m first for accurate colour.\n');
end

verbose = false;   % set true to see hair removal debug plots

for i = 1:length(fileList)
    Iraw = im2double(imread(fileList(i)));

    [~, fname, ~] = fileparts(fileList(i));
    fprintf('\nProcessing image %d/%d: %s\n', i, length(fileList), fname);

    % check if image is sharp enough before processing
    [varianceValue, isSharp] = blurCheck(Iraw, params.qc.blurThreshold);
    if isSharp
        fprintf('  Sharpness: %.6f — SHARP\n', varianceValue);
    else
        fprintf('  Sharpness: %.6f — BLURRY (threshold: %.6f)\n', varianceValue, params.qc.blurThreshold);
    end

    % if blurry ask user to retake the image
    while ~isSharp
        warning('Blurry image, consider recapturing');
        choice = questdlg( ...
            sprintf('Image "%s" is blurry. Recapture this position only?', fname), ...
            'Image Quality Check', 'Retry','Skip','Retry');

        if strcmp(choice, 'Retry')
            cam = webcam('USB2.0 UVC PC Camera');
            fprintf('  Point camera at position "%s" and press Enter...\n', fname);
            preview(cam); pause;
            frame = snapshot(cam);
            closePreview(cam); clear cam;
            imwrite(frame, fileList(i));
            Iraw = im2double(imread(fileList(i)));
            [varianceValue, isSharp] = blurCheck(Iraw, params.qc.blurThreshold);
            sharpStr = 'BLURRY';
            if isSharp, sharpStr = 'SHARP'; end
            fprintf('  Sharpness after recapture: %.6f — %s\n', varianceValue, sharpStr);
        else
            fprintf('  Skipping blur check, continuing.\n');
            isSharp = true;
        end
    end

    % apply colour correction or shading correction
    if useCCM
        shading_out = applyCCM(Iraw, CCM);
    else
        shading_out = shadingCorrect(Iraw, params);
    end

    % remove hair from image
    cl_out = hairRemoval(shading_out, params, verbose);

    % preprocess - noise reduction etc
    processed_img = preprocessImage(cl_out, params);

    % get skin mask on full image first for the grid search
    [skinMaskFull, ~] = maskSkin(processed_img, params.mask);

    % find best ROI using grid search
    [ROI_img, roi_y1, roi_x1, ~] = imageROI(processed_img, params, skinMaskFull);

    % compare raw vs processed using ssim
    raw_roi = Iraw(roi_y1:roi_y1+149, roi_x1:roi_x1+149, :);
    ROI_rgb = lab2rgb(ROI_img);
    raw_roi = imresize(raw_roi, [size(ROI_rgb,1), size(ROI_rgb,2)]);
    ssim_raw_processed = ssim(ROI_rgb, raw_roi);
    fprintf('SSIM (raw vs processed): %.4f\n', ssim_raw_processed);

    % save processed image to disk
    [~, rawName, ~] = fileparts(fileList(i));
    procName = strrep(rawName, "raw_", "proc_") + ".jpg";
    outPath  = fullfile(p.processesOutput, procName);
    writeImage(ROI_img, outPath);
    fprintf("Saved processed image: %s\n", procName);

    % skin mask on just the ROI for colour stats
    [skinMask, ~] = maskSkin(ROI_img, params.mask);

    % extract lab stats and store them
    tmpStats = extractColourStats(ROI_img, skinMask);
    statsArray(i).meanLAB          = tmpStats.meanLAB;
    statsArray(i).stdLAB           = tmpStats.stdLAB;
    statsArray(i).nPixels          = tmpStats.nPixels;
    statsArray(i).coverage         = tmpStats.coverage;
    statsArray(i).masked           = tmpStats.masked;
    statsArray(i).meanRGB          = tmpStats.meanRGB;
    statsArray(i).stdRGB           = tmpStats.stdRGB;
    statsArray(i).ssim_raw_processed = ssim_raw_processed;

    % print results to console
    s = statsArray(i);
    fprintf('  Lab  — mean: L=%.2f  a=%.2f  b=%.2f\n', s.meanLAB(1), s.meanLAB(2), s.meanLAB(3));
    fprintf('         std:  L=%.2f  a=%.2f  b=%.2f\n', s.stdLAB(1),  s.stdLAB(2),  s.stdLAB(3));
    fprintf('  RGB  — mean: R=%.3f  G=%.3f  B=%.3f\n', s.meanRGB(1), s.meanRGB(2), s.meanRGB(3));
    fprintf('         std:  R=%.3f  G=%.3f  B=%.3f\n\n', s.stdRGB(1), s.stdRGB(2),  s.stdRGB(3));
end


% compare lab values between all image positions
numImages = length(fileList);

ssim_matrix = zeros(numImages);

for i = 1:numImages
    for j = i+1:numImages
        [~, n1, e1] = fileparts(fileList(i));
        [~, n2, e2] = fileparts(fileList(j));

        procName1 = strrep(n1, "raw_", "proc_") + e1;
        procName2 = strrep(n2, "raw_", "proc_") + e2;

        img1 = im2double(imread(fullfile(p.processesOutput, procName1)));
        img2 = im2double(imread(fullfile(p.processesOutput, procName2)));

        img2 = imresize(img2, [size(img1,1), size(img1,2)]);
        ssim_matrix(i,j) = ssim(img1, img2);
    end
end

% print delta lab between each pair
for i = 1:numImages
    for j = i+1:numImages

        dL = abs(statsArray(i).meanLAB(1) - statsArray(j).meanLAB(1));
        da = abs(statsArray(i).meanLAB(2) - statsArray(j).meanLAB(2));
        db = abs(statsArray(i).meanLAB(3) - statsArray(j).meanLAB(3));

        fprintf('Image %d vs %d → ΔL=%.2f Δa=%.2f Δb=%.2f\n', ...
            i, j, dL, da, db);
    end
end

% summary of how consistent the readings are across positions
fprintf('\n=== Inter-Position Summary ===\n');

allMeanLAB = zeros(numImages, 3);
for i = 1:numImages
    allMeanLAB(i,:) = statsArray(i).meanLAB;
end

% std across all positions for each channel
interpos_sdL = std(allMeanLAB(:,1));
interpos_sdA = std(allMeanLAB(:,2));
interpos_sdB = std(allMeanLAB(:,3));

fprintf('  SD across positions — L: %.3f  a: %.3f  b: %.3f\n', ...
    interpos_sdL, interpos_sdA, interpos_sdB);

% calculate delta E for all pairs
dE_values = [];
for i = 1:numImages
    for j = i+1:numImages
        dL = statsArray(i).meanLAB(1) - statsArray(j).meanLAB(1);
        da = statsArray(i).meanLAB(2) - statsArray(j).meanLAB(2);
        db = statsArray(i).meanLAB(3) - statsArray(j).meanLAB(3);
        dE_values(end+1) = sqrt(dL^2 + da^2 + db^2);
    end
end
mean_dE = mean(dE_values);
max_dE  = max(dE_values);

fprintf('  Mean ΔE across pairs: %.3f\n', mean_dE);
fprintf('  Max  ΔE across pairs: %.3f\n', max_dE);
fprintf('  (ΔE < 1: imperceptible  |  1-2: just visible  |  >3: significant)\n');

% print ssim matrix
fprintf('\n  SSIM matrix (processed images):\n');
for i = 1:numImages
    for j = 1:numImages
        if j < i
            fprintf('    -     ');
        elseif i == j
            fprintf('  1.000  ');
        else
            fprintf('  %.3f  ', ssim_matrix(i,j));
        end
    end
    fprintf('\n');
end

% pack everything into struct for saving
interpos_stats.sdL     = interpos_sdL;
interpos_stats.sdA     = interpos_sdA;
interpos_stats.sdB     = interpos_sdB;
interpos_stats.mean_dE = mean_dE;
interpos_stats.max_dE  = max_dE;

% save all results to excel
saveMetadata(statsArray, fileList, interpos_stats);

disp("Pipeline complete.");
