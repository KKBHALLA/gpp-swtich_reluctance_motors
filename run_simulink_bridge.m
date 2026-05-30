
function run_simulink_bridge(csvPath, modelPath)
    try
        % 1. Load the Ansys CSV
        opts = detectImportOptions(csvPath);
        data = readtable(csvPath, opts);
        
        % Mapping based on Ansys export: 
        % Col1: Position, Col2: Current, Col3: Flux
        pos_raw = data{:, 1};
        curr_raw = data{:, 2};
        flux_raw = data{:, 3};
        
        % 2. Create 2D Gridded Data for Lookup Table
        unique_pos = unique(pos_raw);
        unique_curr = unique(curr_raw);
        
        [P, C] = meshgrid(unique_pos, unique_curr);
        % Interpolate onto a grid to ensure matrix format for Simulink
        flux_matrix = griddata(pos_raw, curr_raw, flux_raw, P, C);
        
        % 3. Assign to Base Workspace for Simulink access
        assignin('base', 'bp_pos', unique_pos);
        assignin('base', 'bp_curr', unique_curr);
        assignin('base', 'table_flux', flux_matrix);
        
        % 4. Run Simulink
        [pathstr, name, ext] = fileparts(modelPath);
        load_system(modelPath);
        simOut = sim(name, 'ReturnWorkspaceOutputs', 'on');
        
        % 5. Save Simulink Output to CSV
        % Assuming the model has a log or Outport named 'simResult'
        % Adjust 'logsout' name based on your specific model settings
        savePath = fullfile(pathstr, 'SimulinkResults.mat');
        save(savePath, 'simOut');
        
        disp('MATLAB: Simulation and Data Save Complete.');
    catch ME
        disp(['MATLAB Error: ' ME.message]);
    end
end
