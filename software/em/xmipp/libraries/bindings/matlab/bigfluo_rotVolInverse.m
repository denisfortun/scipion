function [ im ] = bigfluo_rotVolInverse( img, rot, tilt, psi, method, pad )

if ~exist('method', 'var')
    method = 'linear';
end
if ~exist('pad', 'var')
    pad = true;
end

if rot == 0 & tilt == 0 & psi == 0
    im = img;
    return;
end
%tic
sz = size(img);
ratM = eulerAnglesToRotation3d(rot,tilt,psi);
ratM = ratM(1:3,1:3)';

% padding image
if pad
    s = max(sz);
    imagepad = zeros([3 * s, 3 * s, 3 * s]);
    ss = floor((3*s - sz) / 2);
    imagepad(ss(1)+1:ss(1)+sz(1), ...
        ss(2)+1:ss(2)+sz(2), ...
        ss(3)+1:ss(3)+sz(3)) = img;
else
    imagepad = img;
end

[nd1, nd2, nd3] = size(imagepad);
midx=(nd1+1)/2;
midy=(nd2+1)/2;
midz=(nd3+1)/2;

% rotate about center
ii = zeros(size(imagepad));
idx = find( ~ii );
[X, Y, Z] = ind2sub (size(imagepad) , idx ) ;


XYZt = [X(:)-midx Y(:)-midy Z(:)-midz]*ratM;
XYZt = bsxfun(@plus,XYZt,[midx midy midz]);
%toc

xout = XYZt(:,1);
yout = XYZt(:,2);
zout = XYZt(:,3);

%tic
imagerotF = interp3(imagepad, yout, xout, zout, method);
im = reshape(imagerotF, size(imagepad));
%toc
%shrink image to use minimal size
idx=find(abs(im)>0);
[mx, my, mz] = ind2sub(size(im), idx);
im = im(min(mx):max(mx), min(my):max(my), min(mz):max(mz));

end
