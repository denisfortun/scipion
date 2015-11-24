function [Htg,eigsHtH,eigsDtD] = bigfluo_precompute_admm(g,h,poses)

pad_size = round(max(size(h))/2);
sg = size(g(:,:,:,1)) + 2*pad_size;
nbImgs = size(g,4);
eigsDtD = abs(fftn(cat(2,1,-1),sg)).^2 + abs(fftn(cat(1,1,-1),sg)).^2 + abs(fftn(cat(3,1,-1),sg)).^2;
eigsHtH = 0;
Htg = 0;
for i=1:nbImgs
    fprintf('%d ',i)
    gRegistered = bigfluo_apply_pose_inverse(g(:,:,:,i), poses(i,:));
    hRegistered = bigfluo_apply_pose_inverse(h, poses(i,:));
        
    % Padding for Htg
    gRegisteredPad = zeros(sg);
    gRegisteredPad = padarray(gRegistered,[round(pad_size) round(pad_size) round(pad_size)]);
    
    eigsHtH = eigsHtH + abs(fftn(hRegistered,sg)).^2;
    Htg = Htg + bigfluo_convolution3D(gRegisteredPad, hRegistered);
end
