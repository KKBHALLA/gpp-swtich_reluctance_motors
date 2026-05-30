clc; clear;

csvPath = 'D:\Ansys\ConsultancyWork\GPP\Design/WindingPlot4.csv'

modelPath = 'D:\Ansys\ConsultancyWork\GPP\Design\SRM_2DModel.slx'

run_simulink_bridge('D:\Ansys\ConsultancyWork\GPP\Design/WindingPlot4.csv',...
    'D:\Ansys\ConsultancyWork\GPP\Design\SRM_2DModel.slx')



%%
clc; clear;

run_simulink_bridge_flux_torq('FluxLinkage.csv','Torque.csv', 'SRM_2DModel.slx')