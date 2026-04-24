function [mask, coverage] = maskSkin(Lab, params)

% builds a mask of only the clean skin pixels
% we dont want hair, pores or overexposed areas messing up the stats

if nargin < 2 || isempty(params)
    params = struct();
end

% thresholds - can adjust these in params
L_low    = getparam(params, 'skin_L_low',    30);
L_high   = getparam(params, 'skin_L_high',   92);
pore_L   = getparam(params, 'skin_pore_L',   42);
pore_erode = getparam(params, 'pore_erode',   3);
min_coverage = getparam(params, 'min_coverage', 0.15);

% convert to rgb so we can use colour rule
rgb = lab2rgb(Lab);
R   = rgb(:,:,1);
G   = rgb(:,:,2);
B   = rgb(:,:,3);
L   = Lab(:,:,1);

% layer 1 - dark pixels like hair roots and shadows
dark_mask = L < L_low;

% layer 2 - overexposed/blown out pixels
bright_mask = L > L_high;

% layer 3 - pixels that are not skin colour (skin should have R > B)
colour_mask = R < (B * 0.90);

% layer 4 - pore detection using small dark blobs
pore_candidates = (L < pore_L) & ~dark_mask;
pore_cores = imerode(pore_candidates, strel('disk', pore_erode));
pore_mask = imdilate(pore_cores, strel('disk', pore_erode + 1));

% combine all dirty pixel types and invert to get clean skin
dirty = dark_mask | bright_mask | colour_mask | pore_mask;
mask  = ~dirty;

% morphological cleanup to remove noise at edges
mask = imerode(mask,  strel('disk', 2));
mask = imdilate(mask, strel('disk', 2));

coverage = mean(mask(:));

% warn if not much clean skin found
if coverage < min_coverage
    fprintf('  WARNING: maskSkin — only %.1f%% clean skin found (threshold: %.0f%%)\n', ...
        coverage*100, min_coverage*100);
    fprintf('           Stats may be unreliable. Check image quality.\n');
end

fprintf('  Skin mask: %.1f%% clean pixels  (hair=%.1f%%  overexp=%.1f%%  pores=%.1f%%)\n', ...
    coverage*100, ...
    mean(dark_mask(:))*100, ...
    mean(bright_mask(:))*100, ...
    mean(pore_mask(:))*100);

end

% helper to get param value or use default if not set
function v = getparam(params, field, default)
    if isfield(params, field)
        v = params.(field);
    else
        v = default;
    end
end
