%Init Fxn
clc;clear
thi =10
thf = 55

Nrpm = 2500;
Vdc = 96;



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
clc; clear;
Vdc = 96;
Nrpm = 2500;

mdl = 'SRM_1DModel.slx';

thi_vec = 10:20; 
thf_vec = 55:65;

Results = [];
q=0;

in = Simulink.SimulationInput(mdl);

for i=1:length(thi_vec)
    for j =1:length(thf_vec)

        in = in.setVariable('thi', thi_vec(i));
        in = in.setVariable('thf', thf_vec(j));
        out = parsim(in, 'ShowProgress', 'off');

        Results(end+1,:) = [thi_vec(i) thf_vec(j) mean(out.yout{1}.Values.Data)];
        q=q+1;
    end
end

index = find(Results(:,3)==max(Results(:,3)))
thi = Results(index,1);
thf = Results(index,2);

figure;
scatter(Results(:,1),Results(:,2),150,Results(:,3)*1e2,'filled','square')
colorbar
colormap('jet')



%% Speed and Vdc variation

clc; clear;
mdl = 'SRM_1DModel.slx';
thi = 12; 
thf = 56;

vdc_vec = 48:3:96;
nrpm_vec = 1000:500:3000;

Results = [];
q=0;

in = Simulink.SimulationInput(mdl);

for i=1:length(vdc_vec)
    for j=1:length(nrpm_vec)

        in = in.setVariable('Vdc', vdc_vec(i));
        in = in.setVariable('Nrpm', nrpm_vec(j));
        out = parsim(in, 'ShowProgress', 'off');

        Results(end+1,:) = [vdc_vec(i)  nrpm_vec(j)  mean(out.yout{1}.Values.Data(5000:end)) ... 
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




