function [Htg,eigsHtH,eigsDtD] = bigfluo_precompute_admm(g,h,poses)

sg = size(g(:,:,:,1));
nbImgs = size(g,4);
eigsDtD = abs(fftn(cat(2,1,-1),sg)).^2 + abs(fftn(cat(1,1,-1),sg)).^2 + abs(fftn(cat(3,1,-1),sg)).^2;
eigsHtH = 0;
Htg = 0;
for i=1:nbImgs
    gRegistered = apply_pose_inverse(g(:,:,:,i), poses(i,:));
    hRegistered = apply_pose_inverse(h, poses(i,:));
        
    eigsHtH = eigsHtH + abs(fftn(hRegistered,sg)).^2;
    Htg = Htg + convolution3D(gRegistered, hRegistered);
end
