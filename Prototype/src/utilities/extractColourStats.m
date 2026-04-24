function stats = extractColourStats(Lab, mask)

% compute mean and std of Lab values on clean skin pixels only
% if no mask is given it uses all pixels but thats not recommended

if nargin < 2 || isempty(mask)
    mask = true(size(Lab,1), size(Lab,2));
    masked = false;
else
    masked = true;
end

% extract each channel and apply mask
L  = Lab(:,:,1);  L  = L(mask);
A  = Lab(:,:,2);  A  = A(mask);
B2 = Lab(:,:,3);  B2 = B2(mask);

stats.meanLAB    = [mean(L),  mean(A),  mean(B2)];
stats.stdLAB     = [std(L),   std(A),   std(B2)];
stats.nPixels    = sum(mask(:));
stats.coverage   = mean(mask(:));
stats.masked     = masked;

% also get RGB stats - have to convert whole image then mask
rgb = lab2rgb(Lab);
R = rgb(:,:,1);  R = R(mask);
G = rgb(:,:,2);  G = G(mask);
B = rgb(:,:,3);  B = B(mask);

stats.meanRGB = [mean(R), mean(G), mean(B)];
stats.stdRGB  = [std(R),  std(G),  std(B)];

end
