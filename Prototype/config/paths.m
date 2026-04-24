function paths = paths()

paths.project = pwd;
paths.dataRaw = fullfile(paths.project, "data", "raw_images");
paths.clrCard = fullfile(paths.project, "data", "colourCard");
paths.cleanOutput  = fullfile(paths.project, "data", "cleaned_images");
paths.processesOutput  = fullfile(paths.project, "data", "processed_images");
paths.results  = fullfile(paths.project, "data", "results");

end
