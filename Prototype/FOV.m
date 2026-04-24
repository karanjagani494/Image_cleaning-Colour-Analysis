function [px_per_mm ,mm_per_pixel, FOVw , FOVh] = FOV()

% calculates the field of view of the dermatoscope
% you click on grid intersections and it works out how many pixels per mm

I = imread("captureImage_20251228_114424.jpg");
imshow(I); zoom on;
title("Click 11 grid intersections along a straight line (10 steps). Press Enter when done.");

[x,y] = ginput();

% calculate pixel distance from first click point
dpx = hypot(x-x(1), y-y(1));
mm  = (0:numel(x)-1)' * 0.1;   % each grid step is 0.1mm

% fit a line to get pixels per mm
p = polyfit(mm, dpx, 1);
px_per_mm   = p(1);
mm_per_pixel = 1/px_per_mm;
px_per_mm = px_per_mm*0.1;

% calculate actual FOV size
rows = size(I,1); cols = size(I,2);
FOVw = cols * mm_per_pixel;
FOVh = rows * mm_per_pixel;

fprintf("px per 0.1mm step ≈ %.2f px\n", px_per_mm);
fprintf("mm/pixel = %.6f\n", mm_per_pixel);
fprintf("FOV = %.2f mm (W) x %.2f mm (H)\n", FOVw, FOVh);

end
