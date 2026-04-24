% recomputeCCM.m
% recomputes the CCM from existing saved measurements
% useful if you want to try different method without recapturing

clc;
addpath(genpath("src"));
addpath("config");

% load the previous measurements
old = load("data/results/ccm.mat");
RGB_cam = old.RGB_cam;
Lab_ref = old.Lab_ref;
names   = old.names;

fprintf('Loaded existing measurements for %d patches\n', size(RGB_cam,1));

% recompute using greyscale only method
[CCM, stats] = computeCCM(RGB_cam, Lab_ref);

% save updated CCM
save("data/results/ccm.mat", "CCM", "RGB_cam", "Lab_ref", "names", "stats");
fprintf('\nNew CCM saved.\n');
fprintf('Mean dE after greyscale CCM: %.2f\n', stats.dE_after_mean);

% plot to visually check improvement
figure('Name', 'Greyscale CCM Check');
dE = stats.dE_per_patch;
bar([dE(:,1), dE(:,2)]);
legend('Before CCM', 'After CCM');
xlabel('Patch'); ylabel('dE');
title('Colour Error — Greyscale CCM');
yline(2, 'r--', 'Perceptible');
yline(5, 'r-', 'Significant');
