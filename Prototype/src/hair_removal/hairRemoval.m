function [cl_out, HairMask] = hairRemoval(Lab, params, verbose)

if nargin < 2 || isempty(params)
    params = struct('hair', struct('seScale',0.05,'minArea',30,'maxMaskPct',0.40));
end
if nargin < 3, verbose = false; end

% use L channel to find dark line structures (hair)
Gray     = Lab(:,:,1) / 100;
seLength = round(params.hair.seScale * min(size(Gray)));
seLength = max(seLength, 5);

% build line structuring elements at different angles
angles  = 0:30:150;
seLines = arrayfun(@(a) strel('line', seLength, a), angles, 'UniformOutput', false);
seDisk  = strel('disk', 2);

% close image at each angle and take max - this fills in hair gaps
Closed = zeros(size(Gray));
for k = 1:length(angles)
    Closed = max(Closed, imclose(Gray, seLines{k}));
end

% difference between closed and original shows where hair is
HairMapN = mat2gray(Closed - Gray);
T        = graythresh(HairMapN);
HairMask = HairMapN > T;
HairMask = bwareaopen(HairMask, params.hair.minArea);
HairMask = imdilate(HairMask, seDisk);
HairMask = imfill(HairMask, 'holes');

maskCoverage = mean(HairMask(:));
fprintf('  Hair mask coverage: %.1f%%', maskCoverage * 100);

% if too much of the image is hair dont bother inpainting, it wont work well
if maskCoverage > params.hair.maxMaskPct
    fprintf(' — TOO DENSE (>%.0f%%), skipping inpainting\n', ...
        params.hair.maxMaskPct * 100);
    cl_out = Lab;
    return;
end

fprintf(' — inpainting\n');

% fill in hair pixels using surrounding skin values
cl_out = Lab;
if any(HairMask(:))
    for c = 1:size(Lab, 3)
        cl_out(:,:,c) = regionfill(Lab(:,:,c), HairMask);
    end
end

% show debug figures if verbose is on
if verbose
    figure;
    subplot(1,4,1); imshow(lab2rgb(Lab));     title('Input');
    subplot(1,4,2); imshow(HairMapN,[]);      title(sprintf('Hair Map (T=%.2f)',T));
    subplot(1,4,3); imshow(HairMask);         title(sprintf('Mask %.1f%%',maskCoverage*100));
    subplot(1,4,4); imshow(lab2rgb(cl_out));  title('Output');
end

end
