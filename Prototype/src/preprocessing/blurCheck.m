function [varianceValue, isSharp] = blurCheck(Iraw, threshold)

% uses laplacian variance to check if image is sharp
% higher variance = more edges = sharper image

if nargin < 2
    threshold = 1e-4;
end

gray          = rgb2gray(Iraw);
laplacianImg  = del2(gray);
varianceValue = var(laplacianImg(:));
isSharp       = varianceValue >= threshold;

end
