function run_simulink_bridge_flux_torq(fluxPath, torquePath, modelPath)
    try
        % 1. PROCESS FLUX DATA (For Inverted Table: i = f(phi, theta))
        f_data = readtable(fluxPath);
        pos_f = f_data{:, 1}; curr_f = f_data{:, 2}; flux_val = f_data{:, 3};
        
        u_pos = unique(pos_f);
        % offset = min(pos_f)
        % u_pos = u_pos - offset
        u_curr = unique(curr_f);
        [P, C] = meshgrid(u_pos, u_curr);
        flux_matrix = griddata(pos_f, curr_f, flux_val, P, C);
        
        % Inversion Logic
        bp_flux_inv = linspace(0, max(flux_matrix(:)), length(u_curr))';
        table_curr_inv = zeros(length(bp_flux_inv), length(u_pos));
        for j = 1:length(u_pos)
            table_curr_inv(:, j) = interp1(flux_matrix(:, j), u_curr, bp_flux_inv, 'linear', 'extrap');
        end

        % 2. PROCESS TORQUE DATA (For Forward Table: T = f(i, theta))
        t_data = readtable(torquePath);
        pos_t = t_data{:, 1}; curr_t = t_data{:, 2}; torq_val = t_data{:, 3};
        
        % Use the same meshgrid to ensure alignment
        torque_matrix = griddata(pos_t, curr_t, torq_val, P, C);
        
        % 3. ASSIGN TO WORKSPACE
        % For Flux-Inverted Table:
        assignin('base', 'bp_flux_inv', bp_flux_inv); 
        assignin('base', 'bp_pos', u_pos);
        assignin('base', 'table_curr_inv', table_curr_inv);
        
        % For Torque Table:
        assignin('base', 'bp_curr', u_curr);
        assignin('base', 'table_torque', torque_matrix);

        spd = 1500;
        Tpole = pi/4/spd/pi*30;

        % For Table:
        assignin('base', 'thi', 12);
        assignin('base', 'thf', 30);
        assignin('base', 'Vdc', 72);
        assignin('base', 'Nrpm', spd);
        assignin('base', 'Tsim', Tpole);
        assignin('base', 'Nc', 10);
        assignin('base', 'Ipeak', max(u_curr));


        % % 4. RUN SIMULINK
        % [~, name, ~] = fileparts(modelPath);
        % load_system(modelPath);
        % simOut = sim(name, 'ReturnWorkspaceOutputs', 'on');
        % save(fullfile(fileparts(fluxPath), 'SimulinkResults.mat'), 'simOut');
        
    catch ME
        disp(['Error: ' ME.message]);
    end
end
