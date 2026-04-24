function [Lab_ref, names] = dgk_lab()

% reference Lab values for all 18 patches on the DGK colour card
% these are the "correct" values we want the camera to match

names = {
    'White',      'Red',        'Dark Red', ...
    'Light Grey', 'Yellow',     'Orange', ...
    'Grey',       'Lime Green', 'Cyan Blue', ...
    'Mid Grey',   'Cyan',       'Magenta', ...
    'Dark Grey',  'Dark Navy',  'Skin Tone 1', ...
    'Black',      'Hot Pink',   'Skin Tone 2'
};

%          L       a       b
Lab_ref = [
   96.0,   0.0,   0.0;   %  1 White
   52.0,  74.0,  54.0;   %  2 Red
   41.0,  51.0,  26.0;   %  3 Dark Red
   73.0,   0.0,   0.0;   %  4 Light Grey
   95.0,  -6.0,  95.0;   %  5 Yellow
   61.0,  29.0,  57.0;   %  6 Orange
   62.0,   0.0,   0.0;   %  7 Grey
   69.0, -43.0,  50.0;   %  8 Lime Green
   52.0, -24.0, -24.0;   %  9 Cyan Blue
   50.0,   0.0,   0.0;   % 10 Mid Grey
   62.0, -44.0, -50.0;   % 11 Cyan
   52.0,  47.0, -14.0;   % 12 Magenta
   38.0,   0.0,   0.0;   % 13 Dark Grey
   11.0,  10.0, -39.0;   % 14 Dark Navy
   69.0,  14.0,  17.0;   % 15 Skin Tone 1
   20.0,   0.0,   0.0;   % 16 Black
   52.0,  81.0,  -7.0;   % 17 Hot Pink
   64.0,  14.0,  17.0;   % 18 Skin Tone 2
];
end
