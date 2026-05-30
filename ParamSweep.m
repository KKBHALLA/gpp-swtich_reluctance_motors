%Init Fxn
clc;clear
thi =0
thf = 20

Nrpm = 1500;
Vdc = 72;

Tsim = pi/4/Nrpm/pi*30;


%%
% mdl = 'untitled0x2E55';
% 
% load_system('untitled0x2E55')
% 
% set_param('untitled0x2E55','thi','10')
% set_param('untitled0x2E55','thf','20')
% 
% out = sim(mdl);


%%
% clc; clear;
% Vdc = 96;
% Nrpm = 2500;

mdl = 'SRM_2DModel.slx';

thi_vec = 0:30; 
thf_vec = 20:45;

Results = [];
q=0;

in = Simulink.SimulationInput(mdl);

for i=1:length(thi_vec)
    for j =1:length(thf_vec)

        if thf_vec(j) <= thi_vec(i)
            continue
        end

        in = in.setVariable('thi', thi_vec(i));
        in = in.setVariable('thf', thf_vec(j));
        out = parsim(in, 'ShowProgress', 'off');

        Results(end+1,:) = [thi_vec(i) thf_vec(j) mean(out.yout{1}.Values.Data(1000:end))];
        q=q+1;
    end
end

index = find(Results(:,3)==max(Results(:,3)))
thi = Results(index,1);
thf = Results(index,2);

figure;
scatter(Results(:,1),Results(:,2),150,Results(:,3),'filled','square')
colorbar
colormap('jet')



%% Speed and Vdc variation

clc; clear;
mdl = 'SRM_2DModel.slx';
thi = 6; 
thf = 30;

vdc_vec = 72; %48:3:96;
nrpm_vec = 1000:500:3000;

Results = [];
q=0;

in = Simulink.SimulationInput(mdl);

for i=1:length(vdc_vec)
    for j=1:length(nrpm_vec)

        in = in.setVariable('Vdc', vdc_vec(i));
        in = in.setVariable('Nrpm', nrpm_vec(j));
        out = parsim(in, 'ShowProgress', 'off');

        Results(end+1,:) = [vdc_vec(i)  nrpm_vec(j)  mean(out.yout{1}.Values.Data(1000:end)) ... 
            mean(out.yout{2}.Values.Data(5000:end))];
        q=q+1;
        fprintf('%d, %d \n', vdc_vec(i), nrpm_vec(j))
    end
end

figure;
scatter(Results(:,1),Results(:,2),150,Results(:,3),'filled','square')
colorbar
colormap('jet')

figure;
scatter(Results(:,1),Results(:,2),150,Results(:,4),'filled','square')
colorbar
colormap('jet')




%%
%% number of turns variation

% clc; clear;
mdl = 'SRM_2DModel.slx';
thi = 0; 
thf = 20;
Nrpm = 1500;
Vdc = 72;

Tsim = pi/4/Nrpm/pi*30;

nc_vec = 3:2:15;

Results = [];
q=0;

in = Simulink.SimulationInput(mdl);

for i=1:length(nc_vec)
        in = in.setVariable('Nc', nc_vec(i));
        % in = in.setVariable('Nrpm', nrpm_vec(j));
        out = parsim(in, 'ShowProgress', 'off');

        Results(end+1,:) = [nc_vec(i)   mean(out.yout{1}.Values.Data(1000:end)) ];
        q=q+1;
        fprintf('%d \n', nc_vec(i))
end

index = find(Results(:,2)==max(Results(:,2)))
thi = Results(index,1);
thf = Results(index,2);
% 
% figure;
% scatter(Results(:,1),Results(:,2),150,Results(:,3),'filled','square')
% colorbar
% colormap('jet')
% 
% figure;
% scatter(Results(:,1),Results(:,2),150,Results(:,4),'filled','square')
% colorbar
% colormap('jet')