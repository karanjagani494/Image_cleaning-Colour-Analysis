function params = params()

% --------------------
% I/O
% --------------------
params.exts = {'.jpg','.png','.jpeg'};


% Blur check 
params.qc.blurThreshold = 1e-4;




% --------------------
% Illumination
% --------------------
params.shading.blurSigma = 40;     % heavy blur for illumination field


% --------------------
% Hair Removal (hairRemoval.m)
% --------------------
params.hair.seScale    = 0.05;   % structuring element as fraction of image size
params.hair.minArea    = 30;     % minimum blob size to count as hair (pixels)
params.hair.maxMaskPct = 0.20;   

% --------------------
% Texture suppression
% --------------------
params.texture.method = 'guided';
params.texture.radius = 8;
params.texture.epsilon = 1e-3;

% --------------------
% Valid pixel thresholds
% --------------------
params.valid.L_prctile = [5 95];    % discard extreme dark/bright
params.valid.dE_thresh = 10;        % ΔE outlier threshold

% --------------------
% Quality Check
% --------------------
params.qc.minValidPct = 0.3;        % reject if <30% pixels valid


% For preprocessing function

params.noise.useGaussian = false;
params.noise.gaussianSigma = 0.8;

params.noise.useMedian = false;
params.noise.medianSize = 3;

params.noise.useBilateral = false;
params.noise.bilateralDegree = 0.03;
params.noise.bilateralSigma = 2;

params.contrast.useCLAHE = false;
params.contrast.clipLimit = 0.02;
params.contrast.numTiles = [4 4];


params.sharpen.useSharpen = false;   % ⚠ leave OFF for skin
params.sharpen.radius = 1.5;
params.sharpen.amount = 2;
params.sharpen.threshold = 0.01;




% --------------------
% Skin Mask (maskSkin.m)
% --------------------
params.mask.skin_L_low    = 30;    % L* below = dark/hair (0-100 scale)
params.mask.skin_L_high   = 92;    % L* above = overexposed
params.mask.skin_pore_L   = 42;    % L* below = pore candidate
params.mask.pore_erode    = 3;     % morphological erosion for pore detection
params.mask.min_coverage  = 0.15;  % warn if <15% clean skin in ROI



end