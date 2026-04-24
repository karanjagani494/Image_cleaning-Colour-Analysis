function rgb = measurePatch(I)

% show image and let user draw a rectangle over the patch
% then returns the mean rgb value inside that region

figure; imshow(I); title("Draw ROI inside colour patch");
h = drawrectangle;
pos = round(h.Position);

patch = I(pos(2):pos(2)+pos(4), pos(1):pos(1)+pos(3), :);
rgb = squeeze(mean(mean(patch,1),2));
rgb = im2double(rgb(:))';

close;
end
