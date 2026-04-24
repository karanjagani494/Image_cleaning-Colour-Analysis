function Iout = preprocessImage(Iin, params)

% takes Lab image and optionally applies noise reduction, CLAHE, sharpening
% all operations are on L channel only so we dont touch the colour info

I = Iin;

% noise reduction - only one method used at a time
if params.noise.useBilateral
    I(:,:,1) = imbilatfilt(I(:,:,1), params.noise.bilateralDegree, params.noise.bilateralSigma);
elseif params.noise.useGaussian
    I(:,:,1) = imgaussfilt(I(:,:,1), params.noise.gaussianSigma);
elseif params.noise.useMedian
    I(:,:,1) = medfilt2(I(:,:,1), [params.noise.medianSize params.noise.medianSize]);
end

% CLAHE for contrast - normalise L to 0-1 first then back to 0-100
if params.contrast.useCLAHE
    L  = I(:,:,1) / 100;
    L2 = adapthisteq(L, ...
        'ClipLimit', params.contrast.clipLimit, ...
        'NumTiles',  params.contrast.numTiles);
    I(:,:,1) = max(0, min(100, L2 * 100));
end

% optional sharpening on L channel
if params.sharpen.useSharpen
    L  = I(:,:,1) / 100;
    L  = imsharpen(L, ...
        'Radius',    params.sharpen.radius, ...
        'Amount',    params.sharpen.amount, ...
        'Threshold', params.sharpen.threshold);
    I(:,:,1) = max(0, min(100, L * 100));
end

Iout = I;

end
