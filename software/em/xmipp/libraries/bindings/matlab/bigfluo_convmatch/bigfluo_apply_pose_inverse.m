function outVol = bigfluo_apply_pose_inverse(inVol, poses)

outVol = rotVolInverse(inVol,poses(1),poses(2),poses(3));
outVol = pad_to_size(outVol,size(inVol));
outVol = imtranslate(outVol,-[poses(4),poses(5),poses(6)]);

