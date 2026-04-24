function saveMetadata(statsArray, fileList, interpos_stats)

% saves all the Lab stats to an excel file
% appends to existing file if it already exist

csvFile = "data/results/metadata.xlsx";
n       = length(fileList);
rows    = cell(n, 10);

sessionTime = string(datetime('now', 'Format', 'yyyy-MM-dd HH:mm:ss'));

for i = 1:n
    [~, name, ext] = fileparts(fileList(i));
    imageName = name + ext;
    rows(i,:) = { ...
        sessionTime, ...
        imageName, ...
        "raw_images/" + imageName, ...
        statsArray(i).meanLAB(1), statsArray(i).meanLAB(2), statsArray(i).meanLAB(3), ...
        statsArray(i).stdLAB(1),  statsArray(i).stdLAB(2),  statsArray(i).stdLAB(3), ...
        statsArray(i).ssim_raw_processed};
end

T = cell2table(rows, 'VariableNames', ...
    {'session','image_name','image_path','mean_L','mean_a','mean_b', ...
     'std_L','std_a','std_b','ssim_raw_processed'});

if isfile(csvFile)
    writetable(T, csvFile, 'WriteMode', 'append', 'WriteVariableNames', false);
else
    writetable(T, csvFile);
end

% save inter position stats to sheet 2
if nargin >= 3 && ~isempty(interpos_stats)
    T2 = table(interpos_stats.sdL, interpos_stats.sdA, interpos_stats.sdB, ...
               interpos_stats.mean_dE, interpos_stats.max_dE, ...
               'VariableNames', {'interpos_sdL','interpos_sdA','interpos_sdB','mean_dE','max_dE'});
    writetable(T2, csvFile, 'Sheet', 'InterPosition');
end

end
