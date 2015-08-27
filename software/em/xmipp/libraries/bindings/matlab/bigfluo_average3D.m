function bigfluo_average3D(fnInVols,fnOutVol)

InVols = xmipp_read(fnInVols);

outVol = sum(InVols,4)/size(InVols,4);

fh = fopen([fnOutVol '_average.raw'],'w'); fwrite(fh,outVol(:),'float'); fclose(fh);
