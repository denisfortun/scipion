function [outVol] = convolution3D(fnInVol,fnInKer,fnOut)

%% Load
%inVol = bigfluo_load_tiff(fnInVol);
%inKer = bigfluo_load_tiff(fnInKer);

inVol = xmipp_read(fnInVol);
inKer = xmipp_read(fnInKer);

inVol = squeeze(inVol);
inKer = squeeze(inKer);

%% Simple Fourier version
maxDim = [max(size(inVol,1),size(inKer,1)), max(size(inVol,2),size(inKer,2)), max(size(inVol,3),size(inKer,3))];
outVol = real(ifftn(fftn(inVol,maxDim) .* fftn(inKer,maxDim), size(inVol)));

%% Padded version
% % Size of the input volumes
% inVolSize=size(inVol);
% inVolSide=max(inVolSize);
% inKerSize=size(inKer);
% inKerSide=max(size(inKer));
% 
% % Fourrier tranform of the volume and inKer.
% extr(1:3)={0};
% for iDim=(1:3),
%     inVol=fft(inVol,inVolSide+inKerSide-1,iDim);
%     inKer=fft(inKer,inVolSide+inKerSide-1,iDim);
%     extr{iDim}=ceil((inKerSize(iDim)-1)/2)+(1:inVolSize(iDim));
% end
% 
% % Multiplication of the Fourrier tranforms
% conv_FFT=inVol.*inKer;
% 
% % Inverse Fourrier Transform of the convolution
% for iDim=(1:3),
%     conv_FFT=ifft(conv_FFT,[],iDim);
% end
% 
% % Crop the side of the image in relation to the size of the kernel
% convinVol=conv_FFT(extr{:});
% 
% % limit the results
% outVol=real(convinVol);

%% Save
% Problem in the convolution to solve
%outVol = rescale(outVol,min(min(min(inVol))),max(max(max(inVol))));
%outVolSave = uint16(outVol);

% Save tiff
%save_tiff(outVolSave,fnOut);

% Save raw
fh = fopen([fnOut '_convolved.raw'],'w'); fwrite(fh,outVol(:),'float'); fclose(fh);

