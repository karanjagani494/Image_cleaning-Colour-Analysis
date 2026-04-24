 function files = readImages(paths)

 % read the 5 most recent raw images from the data folder
 fileStruct = dir(fullfile(paths.dataRaw,"raw_*.jpg"));

 % sort newest first
 [~, idx] = sort([fileStruct.datenum], 'descend');
 fileStruct = fileStruct(idx);

 % only take last 5
 fileStruct = fileStruct(1:5);

 files = strings(1,5);

 for i = 1:5
     files(i) = fullfile(fileStruct(i).folder, fileStruct(i).name);
 end

 end
