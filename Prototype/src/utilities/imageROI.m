function [roi_img, best_y1, best_x1, best_coverage] = imageROI(I, params, skinMaskFull)

[h, w, ~] = size(I);
roi_size   = 150;

% if we have a skin mask, do grid search to find cleanest patch
if nargin >= 3 && ~isempty(skinMaskFull)

    step = 10;
    if nargin >= 2 && isstruct(params) && isfield(params, 'roi') && isfield(params.roi, 'searchStep')
        step = params.roi.searchStep;
    end

    best_coverage = -1;
    best_y1 = 1;
    best_x1 = 1;

    % slide window across image and pick position with most clean skin
    for y1 = 1 : step : (h - roi_size + 1)
        for x1 = 1 : step : (w - roi_size + 1)
            window_mask = skinMaskFull(y1:y1+roi_size-1, x1:x1+roi_size-1);
            coverage    = mean(window_mask(:));
            if coverage > best_coverage
                best_coverage = coverage;
                best_y1       = y1;
                best_x1       = x1;
            end
        end
    end

    fprintf('  ROI grid search: best position (row=%d, col=%d), coverage=%.1f%%\n', ...
        best_y1, best_x1, best_coverage * 100);

else
    % fallback to fixed centre crop if no mask given
    y_center = round(h * 0.55);
    x_center = round(w * 0.79);

    best_x1 = x_center - floor(roi_size/2);
    best_y1 = y_center - floor(roi_size/2);

    best_x1 = max(1, min(best_x1, w - roi_size));
    best_y1 = max(1, min(best_y1, h - roi_size));

    best_coverage = 0;
    fprintf('  ROI: fixed centre crop (row=%d, col=%d)\n', best_y1, best_x1);
end

roi_img = I(best_y1:best_y1+roi_size-1, best_x1:best_x1+roi_size-1, :);

end
