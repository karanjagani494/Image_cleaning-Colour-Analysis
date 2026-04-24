function Lab = shadingCorrect(Iin , params)

% convert to Lab first
Lab = rgb2lab(Iin);

% get the L channel (lightness)
L = Lab(:,:,1);

% blur L heavily to estimate the illumination field
sigma = params.shading.blurSigma;
Lblur = imgaussfilt(L, sigma);

% avoid dividing by zero
Lblur(Lblur < 1e-6) = 1e-6;

% divide by illumination estimate to flatten uneven lighting
Lcorr = (L ./ Lblur) * mean(Lblur(:));

% clamp to valid range
Lcorr = max(0,min(100,Lcorr));

% put corrected L back into Lab image
Lab(:,:,1) = Lcorr;

end
