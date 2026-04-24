function Ilab = imageConvert(Iin)

I = Iin;

% convert to double so values are between 0 and 1
I  = im2double(I);
imshow(I)

% convert to different colour spaces for comparison
HSV  = rgb2hsv(I);
YCbCr = rgb2ycbcr(I);
Ilab  = rgb2lab(I);

% show all channels side by side
figure;
subplot(3,3,1), imshow(I), title("RGB")

subplot(3,3,2), imshow(HSV(:,:,1)), title("H")
subplot(3,3,3), imshow(HSV(:,:,2)), title("S")

subplot(3,3,4), imshow(YCbCr(:,:,1)), title("Y")
subplot(3,3,5), imshow(YCbCr(:,:,2)), title("Cb")
subplot(3,3,6), imshow(YCbCr(:,:,3)), title("Cr")

% L needs dividing by 100 and a/b need scaling to show properly
subplot(3,3,7), imshow(Ilab(:,:,1)/100), title("L*")
subplot(3,3,8), imshow((Ilab(:,:,2)+128)/255), title("a*")
subplot(3,3,9), imshow((Ilab(:,:,3)+128)/255), title("b*")

end
