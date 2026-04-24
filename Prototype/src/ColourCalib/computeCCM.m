function [CCM, stats] = computeCCM(RGB_cam, Lab_ref)

% greyscale only CCM - uses only the 6 neutral grey patches
% these patches have a*=0 b*=0 so reference values are more reliable
% grey patches in our card: 1=White 4=LightGrey 7=Grey 10=MidGrey 13=DarkGrey 16=Black

grey_idx = [1, 4, 7, 10, 13, 16];

RGB_cam_grey = RGB_cam(grey_idx, :);
Lab_ref_grey = Lab_ref(grey_idx, :);

% convert reference Lab to RGB
RGB_ref_grey = lab2rgb(Lab_ref_grey);
RGB_ref_grey = max(0, min(1, RGB_ref_grey));

% least squares to find the best 3x3 matrix
CCM = RGB_cam_grey \ RGB_ref_grey;

% evaluate CCM quality on all 18 patches
RGB_ref_all       = max(0, min(1, lab2rgb(Lab_ref)));
RGB_corrected_all = max(0, min(1, RGB_cam * CCM));

Lab_corrected = rgb2lab(RGB_corrected_all);
Lab_measured  = rgb2lab(max(0, min(1, RGB_cam)));

dE_before = sqrt(sum((Lab_measured  - Lab_ref).^2, 2));
dE_after  = sqrt(sum((Lab_corrected - Lab_ref).^2, 2));

stats.dE_before_mean = mean(dE_before);
stats.dE_after_mean  = mean(dE_after);
stats.dE_before_max  = max(dE_before);
stats.dE_after_max   = max(dE_after);
stats.dE_per_patch   = [dE_before, dE_after];

fprintf('\n=== CCM Quality Report ===\n');
fprintf('  Method: Greyscale-only (patches 1,4,7,10,13,16)\n');
fprintf('  Mean ΔE before CCM: %.2f\n', stats.dE_before_mean);
fprintf('  Mean ΔE after  CCM: %.2f\n', stats.dE_after_mean);
fprintf('  Max  ΔE before CCM: %.2f\n', stats.dE_before_max);
fprintf('  Max  ΔE after  CCM: %.2f\n', stats.dE_after_max);

[~, names] = dgk_lab();
fprintf('\n  %-15s  %8s  %8s\n', 'Patch', 'dE before', 'dE after');
fprintf('  %s\n', repmat('-',1,38));
for i = 1:length(dE_before)
    flag = '';
    if dE_after(i) > 5, flag = ' <- high'; end
    fprintf('  %-15s  %8.2f  %8.2f%s\n', ...
        names{i}, dE_before(i), dE_after(i), flag);
end
end
