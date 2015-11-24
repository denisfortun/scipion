function outVol = bigfluo_convolution_matching(fnInVols, fnPsf, fnInitVol, fnOut)

%% Scipion input
inVolsOrig = squeeze(xmipp_read(fnInVols));
initVol =squeeze( xmipp_read(fnInitVol));
psf = squeeze(xmipp_read(fnPsf));
size(inVolsOrig)
data = load('/home/big/Documents/Denis/scipion/matlab_code/convmatch/psf.mat');
psf = data.psf;
data = load('/home/big/Documents/Denis/scipion/matlab_code/convmatch/inVols.mat');
inVolsOrig = data.inVols;
data = load('/home/big/Documents/Denis/scipion/matlab_code/convmatch/recon.mat');
initVol = data.recon;


initVol = (initVol - min(initVol(:)))/(max(initVol(:)) - min(initVol(:)))*255;
for i=1:size(inVolsOrig,4)
    tmp = inVolsOrig(:,:,:,i);
    inVolsOrig(:,:,:,i) = (tmp - min(tmp(:)))/(max(tmp(:)) - min(tmp(:)))*255;
end
inVols = inVolsOrig(:,:,:,:);

figure(31);imagesc(initVol(:,:,round(size(initVol,3)/2),1)); colormap gray; axis image;
figure(32);imagesc(squeeze(initVol(round(size(initVol,1)/2),:,:,1))); colormap gray; axis image;

figure(1);imagesc(inVols(:,:,round(size(inVols,3)/2),1)); colormap gray; axis image;
figure(2);imagesc(squeeze(inVols(round(size(inVols,1)/2),:,:,1))); colormap gray; axis image;

figure(3);imagesc(inVols(:,:,round(size(inVols,3)/2),2)); colormap gray; axis image;
figure(4);imagesc(squeeze(inVols(round(size(inVols,1)/2),:,:,2))); colormap gray; axis image;

figure(5);imagesc(inVols(:,:,round(size(inVols,3)/2),3)); colormap gray; axis image;
figure(6);imagesc(squeeze(inVols(round(size(inVols,1)/2),:,:,3))); colormap gray; axis image;

figure(7);imagesc(inVols(:,:,round(size(inVols,3)/2),4)); colormap gray; axis image;
figure(8);imagesc(squeeze(inVols(round(size(inVols,1)/2),:,:,4))); colormap gray; axis image;

figure(9);imagesc(inVols(:,:,round(size(inVols,3)/2),5)); colormap gray; axis image;
figure(10);imagesc(squeeze(inVols(round(size(inVols,1)/2),:,:,5))); colormap gray; axis image;

figure(11);imagesc(inVols(:,:,round(size(inVols,3)/2),6)); colormap gray; axis image;
figure(12);imagesc(squeeze(inVols(round(size(inVols,1)/2),:,:,6))); colormap gray; axis image;

figure(13);imagesc(inVols(:,:,round(size(inVols,3)/2),7)); colormap gray; axis image;
figure(14);imagesc(squeeze(inVols(round(size(inVols,1)/2),:,:,7))); colormap gray; axis image;

figure(15);imagesc(inVols(:,:,round(size(inVols,3)/2),8)); colormap gray; axis image;
figure(16);imagesc(squeeze(inVols(round(size(inVols,1)/2),:,:,8))); colormap gray; axis image;

figure(17);imagesc(inVols(:,:,round(size(inVols,3)/2),9)); colormap gray; axis image;
figure(18);imagesc(squeeze(inVols(round(size(inVols,1)/2),:,:,9))); colormap gray; axis image;

figure(19);imagesc(inVols(:,:,round(size(inVols,3)/2),10)); colormap gray; axis image;
figure(20);imagesc(squeeze(inVols(round(size(inVols,1)/2),:,:,10))); colormap gray; axis image;

%% Convolution-matching
lambda = 100000;
nbIters = 4;

curVol = initVol;
for i=1:nbIters
    poses = bigfluo_angular_convolution_matching(inVols,psf,curVol)
    curVol = bigfluo_reconstruction(inVols,psf,'poses',poses,'lambda',lambda);
end
    
outVol = curVol;

%% Scipion output
fh = fopen([fnOut '_outVol.raw'],'w'); fwrite(fh,outVol(:),'float'); fclose(fh);
