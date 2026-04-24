function Lab = applyCCM(Irgb, CCM)

% apply the colour correction matrix to fix camera colour errors
% this needs to run before converting to Lab

[h, w, ~] = size(Irgb);

% flatten to Nx3, multiply by CCM, reshape back
RGB_flat     = reshape(Irgb, [], 3);
RGB_corrected = RGB_flat * CCM;

% clamp values - matrix can push things out of range sometimes
RGB_corrected = max(0, min(1, RGB_corrected));

% reshape and convert to Lab
RGB_out = reshape(RGB_corrected, h, w, 3);
Lab     = rgb2lab(RGB_out);

end
