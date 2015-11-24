function f = bigfluo_reconstruction(g,h,varargin)
[lambda,poses]=...
    process_options(varargin,'lambda',1000,'poses',[]);

%% Some variables
nb_imgs = size(g,4);
sg   = size(g(:,:,:,1));
[D,Dt]  = defDDt;
gamma = 2;
change_tol = 1e-7;
max_iters = 100;
mu_init=2;
beta = 0.7;

%% Initialization
f = g(:,:,:,1);
Df = D(f);
mu = mu_init;
alpha  = zeros(size(f,1),size(f,2),size(f,3),3);
u = alpha;
nbPixs = size(f,1)*size(f,2)*size(f,3);
rnorm = sqrt(norm(reshape(Df(:,:,:,1),nbPixs,1)-reshape(u(:,:,:,1),nbPixs,1), 'fro')^2 + norm(reshape(Df(:,:,:,2),nbPixs,1)-reshape(u(:,:,:,2),nbPixs,1), 'fro')^2 + norm(reshape(Df(:,:,:,3),nbPixs,1)-reshape(u(:,:,:,3),nbPixs,1), 'fro')^2);
E = [];
iters = [];

%% Precomputation of constant terms for minimization on the data part
[Htg,eigsHtH,eigsDtD] = precompute_admm(g,h,poses);

%% Main iterations loop
%figure(10);hold on
fprintf('iterations: ')
for it=1:max_iters
    fprintf('%d ',it)
    f_prev = f;
    rnorm_prev  = rnorm;

    %% Data update 
    den = lambda/mu*eigsHtH + eigsDtD;
    f = real( ifftn( fftn( (lambda/mu)*Htg + Dt(u - (1/mu)*alpha)) ./ den ) );
    Df = D(f);

    %% Regularization update
    v = Df + (1/mu)*alpha;
    v0 = sqrt(v(:,:,:,1).^2 + v(:,:,:,2).^2 + v(:,:,:,3).^2);
    v0 = max(v0 - 1/mu,0)./v0;
    u = v.*cat(4,v0,cat(4,v0,v0));

  
    %% Lagrange parameter update
    alpha = alpha - mu*(u - Df);
    
     %% Update coupling parameter
    rnorm = sqrt(norm(reshape(Df(:,:,:,1),nbPixs,1)-reshape(u(:,:,:,1),nbPixs,1), 'fro')^2 + norm(reshape(Df(:,:,:,2),nbPixs,1)-reshape(u(:,:,:,2),nbPixs,1), 'fro')^2 + norm(reshape(Df(:,:,:,3),nbPixs,1)-reshape(u(:,:,:,3),nbPixs,1), 'fro')^2);  
     if rnorm>beta*rnorm_prev
         mu  = mu * gamma;
     end

    %% Debug
%     E = [E compute_energy(f,Df(:,:,:,1),Df(:,:,:,2),Df(:,:,:,3),g,h,lambda)];
%     iters = [iters it];
%     figure(10);plot(iters,E)
%       f_est_crop = crop_fit_size_center(f,size(fgt));   
% %    [L2,L1,RMSE,MAE,SNR,PSNR,c]=Evaluation(fgt,f_est_crop,1);
%     [snr,mse]=psnr(fgt,f_est_crop)
% 
     figure(5);imagesc(squeeze(f(:,:,floor(size(f,3)/2)))); axis image ; colormap gray;
     figure(6);imagesc(squeeze(f(floor(size(f,1)/2),:,:))); axis image ; colormap gray;

    %% End of iterations checking
     change = norm(f(:)-f_prev(:))/norm(f_prev(:));
    if change < change_tol
        break
    end
end
fprintf('\n ',it)

%% Post processing
% for z=1:size(f,3)
%     fpost = jointWMF(f(:,:,z),f(:,:,z),10,25.5,256,256,1,'exp');
%     f(:,:,z) = fpost;
% end
    %% Debug
%     figure(11);imagesc(squeeze(f(:,:,floor(sz/2)))); axis image ; colormap gray;
%     figure(12);imagesc(squeeze(f(floor(sx/2),:,:))); axis image ; colormap gray;

end

function E = compute_energy(f,Dfx,Dfy,Dfz,g,h,lambda)

data = 0;
for i=1:length(h)
    Hxi = convolution3D_FFTdomain(f, h{i});
    data = data + sum((g{i}(:) - Hxi(:)).^2);
end

reg = norm(Dfx(:,1),1) + norm(Dfy(:,1),1) + norm(Dfz(:,1),1);

E = data + lambda*reg;

end

%% Derivative functions
function [D,Dt] = defDDt()
D = @(U) ForwardD(U);
Dt = @(V) Dive(V);
end

function Du = ForwardD(U)

Du = zeros(size(U,1),size(U,2),size(U,3),3);
Du(:,:,:,1) = cat(2,diff(U,1,2), U(:,1,:) - U(:,end,:));
Du(:,:,:,2) = cat(1,diff(U,1,1), U(1,:,:) - U(end,:,:));
Du(:,:,:,3) = cat(3,diff(U,1,3), U(:,:,1) - U(:,:,end));
end

function DtXYZ = Dive(V)
X = V(:,:,:,1);
Y = V(:,:,:,2);
Z = V(:,:,:,3);

DtXYZ = cat(2,X(:,end,:) - X(:, 1,:), -diff(X,1,2));
DtXYZ = DtXYZ + cat(1,Y(end,:,:) - Y(1,:,:), -diff(Y,1,1));
DtXYZ = DtXYZ + cat(3,Z(:,:,end) - Z(:,:,1), -diff(Z,1,3));
end
