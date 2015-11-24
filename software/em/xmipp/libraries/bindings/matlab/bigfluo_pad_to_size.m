function outVol = bigfluo_pad_to_size(inVol, targetSize)

inSize = size(inVol);
padSize = ceil((targetSize-inSize)/2);

outVol = padarray(inVol,[max(padSize(1),0),max(padSize(2),0),max(padSize(3),0)]);
%outVol = outVol(1:targetSize(1),1:targetSize(2),1:targetSize(3));

outVol = bigfluo_crop_fit_size_center(outVol,targetSize);