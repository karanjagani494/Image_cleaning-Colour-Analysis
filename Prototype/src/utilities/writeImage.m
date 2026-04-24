function writeImage(LabImg, outPath)

% make output folder if it doesnt exist
outDir = fileparts(outPath);
if ~isfolder(outDir)
    mkdir(outDir);
end

% convert Lab to RGB before saving - imwrite needs RGB not Lab
rgb = lab2rgb(LabImg);
rgb = min(max(rgb, 0), 1);

imwrite(rgb, outPath);

end
