function poses = bigfluo_angular_convolution_matching(inVols,psf,recon,varargin)

% [rot_sampl,tilt_sampl,psi_sampl,rot_search,tilt_search,psi_search,shift_sampl,shift_search,symmetry]=...
%     process_options(varargin,'angular_sampling',[10],'angular_search',[1000],...
%     'shift_sampling',2,'shift_search',[1000],'symmetry','c1');

nbPoses = size(inVols,4);
bestCorr = zeros(nbPoses,1);
poses = zeros(nbPoses,6);
correspVols = zeros(size(inVols));

%% Discretization parameters
shift_sampling = 0;
angle_sampling = 50;
angle_init = 0;
angle_end = 360;
shift_init = 0;
shift_end = 0;
% nbAngles = ((angle_end-angle_init)/angle_sampling)^3;
% nbShifts = ((shift_end-angle_init)/angle_sampling)^3;

%nbDiscretePoses = floor((shift_end-shift_init)/shift_sampling + 1)^3 * floor((angle_end-angle_init)/angle_sampling + 1)^3
nbDiscretePoses = floor((angle_end-angle_init)/angle_sampling + 1)^3

%% Rotation search
w=waitbar(0);
count = 0;
for rot=angle_init:angle_sampling:angle_end
    for tilt=angle_init:angle_sampling:angle_end
        for psi=angle_init:angle_sampling:angle_end
            rotRecon = bigfluo_rotVol(recon,rot,tilt,psi);
            rotRecon = bigfluo_pad_to_size(rotRecon,size(inVols(:,:,:,1)));
            convRotRecon = bigfluo_convolution3D(rotRecon,psf);
            %% Shift search
            for shiftX=shift_init:shift_end      
               for shiftY=shift_init:shift_end      
                    for shiftZ=shift_init:shift_end      
%             for shiftX=shift_init:shift_sampling:shift_end      
%                for shiftY=shift_init:shift_sampling:shift_end      
%                     for shiftZ=shift_init:shift_sampling:shift_end      
                        count = count + 1;
%                         fprintf('pose nb %d\n',count);
                        transConvRotRecon = convRotRecon;% translation(convRotRecon,shiftX,shiftY,shiftZ);
                        %% Matching
                        for i_vol=1:nbPoses
                            corr = bigfluo_correlation3D(transConvRotRecon,inVols(:,:,:,i_vol));
                            if corr > bestCorr(i_vol);
                                bestCorr(i_vol) = corr;
                                poses(i_vol,:) = [rot,tilt,psi,shiftX,shiftY,shiftZ];
                                correspVols(:,:,:,i_vol) = transConvRotRecon;
                            end
                        end
                        waitbar(count/nbDiscretePoses);
                    end
                end
            end
        end
    end
end
close(w); 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%  Debug  %%%%%%%%%%%%%%%%%%%%%%%%%%%%
for i_vol=1:nbPoses
    tmp1 = inVols(:,:,:,i_vol);
    tmp2 = correspVols(:,:,:,i_vol);
%     figure(1);imagesc(squeeze(tmp1(:,:,floor(size(tmp1,3)/2)))); axis image ; colormap gray;
%     figure(2);imagesc(squeeze(tmp1(floor(size(tmp1,1)/2),:,:))); axis image ; colormap gray;    
% 
%     figure(3);imagesc(squeeze(tmp2(:,:,floor(size(tmp2,3)/2)))); axis image ; colormap gray;
%     figure(4);imagesc(squeeze(tmp2(floor(size(tmp2,1)/2),:,:))); axis image ; colormap gray;    
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Save
%fh = fopen([fnOut '_pose.raw'],'w'); fwrite(fh,poseAssign(:),'float'); fclose(fh);


 