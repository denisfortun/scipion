function outVol = bigfluo_convolution_matching(fnInVols, fnPsf, fnInitVol, fnOut)

%% Scipion input
inVols = xmipp_read(fnInVols);
initVol = xmipp_read(fnInitVol);
psf = xmipp_read(fnPsf);

%% Convolution-matching
lambda = 100000;

% Padding for Htg
pad_size = round(max(size(psf))/2);
inVolsPadding = zeros(size(inVols,1)+2*pad_size, size(inVols,2)+2*pad_size, size(inVols,3)+2*pad_size, size(inVols,4));
for i=1:size(inVols,4)
    inVolsPadding(:,:,:,i) = padarray(inVols(:,:,:,i),[round(pad_size) round(pad_size) round(pad_size)]);
end

curVol = initVol;
for i=1:nbIters
    poses = bigfluo_angular_convolution_matching(inVols,psf,curVol);
    curVol = bigfluo_reconstruction(inVolsPadding,psf,'poses',poses,'lambda',lambda);
end
    
outVol = curVol;

%% Scipion output
fh = fopen([fnOut '_outVol.raw'],'w'); fwrite(fh,outVol(:),'float'); fclose(fh);
