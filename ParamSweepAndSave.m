function ParamSweepAndSave(fluxPath, torquePath, modelPath, outCsvPath, ...
                            rotorOR_radius, rpap, spap, iaa, maxWorkers, ...
                            thi_vec, thf_vec)
% ParamSweepAndSave  Sweep thi/thf in Simulink for one pre-solved geometry.
%
%   Loads flux/torque lookup tables from ANSYS CSVs, runs the SRM_2DModel
%   Simulink model for every valid (thi, thf) pair in parallel, records
%   mean torque and peak-to-peak torque ripple, and saves all results to
%   outCsvPath (one row per (thi, thf) combination).
%
%   The Simulink model contains two phase-shifted instances of the torque
%   lookup table (T = f(i, theta)), each shifted by the pole pitch, whose
%   outputs are summed to give the total motor torque.  yout{1} is that
%   total torque signal.  Mean torque and ripple are computed from it.
%
%   Called by RunGridSearch.py for each ANSYS geometry combination.
%
%   Inputs:
%     fluxPath       - full path to FluxLinkage CSV for this geometry
%     torquePath     - full path to Torque CSV for this geometry
%     modelPath      - full path to SRM_2DModel.slx
%     outCsvPath     - output CSV path (written fresh each call)
%     rotorOR_radius - RotorOuterRadius radius value in mm
%     rpap           - RotorPoleArcByPolePitch (dimensionless)
%     spap           - StatorPoleArcByPolePitch (dimensionless)
%     iaa            - peak phase current in A (computed from slot area)
%     maxWorkers     - number of parallel Simulink workers (default: 2)
%     thi_vec        - turn-on  angle sweep vector, deg (default: 0:5:30)
%     thf_vec        - turn-off angle sweep vector, deg (default: 20:5:45)

    if nargin < 9  || isempty(maxWorkers); maxWorkers = 2;      end
    if nargin < 10 || isempty(thi_vec);   thi_vec = 0:5:30;    end
    if nargin < 11 || isempty(thf_vec);   thf_vec = 20:5:45;   end

    % Append key milestones to GridSearch.log in the output directory
    logFile = fullfile(fileparts(outCsvPath), 'GridSearch.log');
    diary(logFile); diary on;
    fprintf('[%s] START  %s  Iaa=%.1fA  workers=%d\n', ...
        datestr(now,'HH:MM:SS'), make_geom_id(rotorOR_radius,rpap,spap), iaa, maxWorkers);

    %% --- 1. Load flux-linkage and torque lookup tables ---
    % (Same inversion logic as run_simulink_bridge_flux_torq.m)
    f_data  = readtable(fluxPath);
    pos_f   = f_data{:,1};
    curr_f  = f_data{:,2};
    flux_v  = f_data{:,3};

    u_pos  = unique(pos_f);
    u_curr = unique(curr_f);
    [P, C] = meshgrid(u_pos, u_curr);
    flux_matrix = griddata(pos_f, curr_f, flux_v, P, C);

    % Inverted flux table: i = f(phi, theta)
    bp_flux_inv    = linspace(0, max(flux_matrix(:)), length(u_curr))';
    table_curr_inv = zeros(length(bp_flux_inv), length(u_pos));
    for k = 1:length(u_pos)
        table_curr_inv(:,k) = interp1(flux_matrix(:,k), u_curr, ...
                                       bp_flux_inv, 'linear', 'extrap');
    end

    % Torque table: T = f(i, theta)
    t_data  = readtable(torquePath);
    pos_t   = t_data{:,1};
    curr_t  = t_data{:,2};
    torq_v  = t_data{:,3};
    torque_matrix = griddata(pos_t, curr_t, torq_v, P, C);

    % Push all lookup tables into the base workspace for Simulink
    assignin('base', 'bp_flux_inv',    bp_flux_inv);
    assignin('base', 'bp_pos',         u_pos);
    assignin('base', 'table_curr_inv', table_curr_inv);
    assignin('base', 'bp_curr',        u_curr);
    assignin('base', 'table_torque',   torque_matrix);
    assignin('base', 'Ipeak',          max(u_curr));

    %% --- 2. Fixed simulation parameters ---
    Nrpm = 1500;
    Vdc  = 72;
    Tsim = pi/4 / Nrpm / pi * 30;   % one electrical period at Nrpm
    Nc   = 10;

    assignin('base', 'Vdc',  Vdc);
    assignin('base', 'Nrpm', Nrpm);
    assignin('base', 'Tsim', Tsim);
    assignin('base', 'Nc',   Nc);

    %% --- 3. Configure parallel pool ---
    % parsim draws from the current parpool; create one with exactly maxWorkers.
    existing = gcp('nocreate');
    if isempty(existing)
        parpool('local', maxWorkers);
    elseif existing.NumWorkers ~= maxWorkers
        delete(existing);
        parpool('local', maxWorkers);
    end
    %% --- 4. Build all SimulationInput objects for parallel execution ---
    % yout{1} in SRM_2DModel is the TOTAL motor torque = sum of two phase-shifted
    % torques, each computed from the ANSYS-derived lookup table T(i, theta).
    % Mean and ripple are extracted from this signal only.
    TOTAL_TORQUE_IDX = 1;

    % thi_vec / thf_vec come from function arguments (defaults set above)

    [~, mdlName, ~] = fileparts(modelPath);
    load_system(modelPath);

    sim_inputs  = Simulink.SimulationInput.empty;
    pair_list   = zeros(0, 2);    % [thi, thf] for each input

    for i = 1:length(thi_vec)
        for j = 1:length(thf_vec)
            % Require at least 5 deg conduction window
            if thf_vec(j) <= thi_vec(i) + 5
                continue
            end

            in_ij = Simulink.SimulationInput(mdlName);
            in_ij = in_ij.setVariable('thi',  thi_vec(i));
            in_ij = in_ij.setVariable('thf',  thf_vec(j));
            in_ij = in_ij.setVariable('Vdc',  Vdc);
            in_ij = in_ij.setVariable('Nrpm', Nrpm);
            in_ij = in_ij.setVariable('Tsim', Tsim);
            in_ij = in_ij.setVariable('Nc',   Nc);

            sim_inputs(end+1) = in_ij;       %#ok<AGROW>
            pair_list(end+1,:) = [thi_vec(i), thf_vec(j)];
        end
    end

    fprintf('[%s] running %d sims  (%d workers)...\n', ...
        datestr(now,'HH:MM:SS'), length(sim_inputs), maxWorkers);

    %% --- 5. Run all simulations in parallel ---
    % TransferBaseWorkspaceVariables copies the lookup tables assigned via
    % assignin('base',...) to every parallel worker before simulation starts.
    outs = parsim(sim_inputs, 'ShowProgress', 'on', ...
                  'TransferBaseWorkspaceVariables', 'on');

    close_system(mdlName, 0);

    %% --- 6. Extract metrics and write CSV ---
    geom_id = make_geom_id(rotorOR_radius, rpap, spap);

    fid = fopen(outCsvPath, 'w');
    fprintf(fid, ['geom_id,RotorOR_dia_mm,RotorPoleArcByPolePitch,' ...
                  'StatorPoleArcByPolePitch,Iaa_A,' ...
                  'thi_deg,thf_deg,mean_torque_Nm,torque_ripple_Nm\n']);

    n_written = 0;
    for idx = 1:length(outs)
        if ~isempty(outs(idx).ErrorMessage)
            fprintf('  [WARN] sim %d failed: %s\n', idx, outs(idx).ErrorMessage);
            continue
        end

        % Total motor torque = sum of 2 phase-shifted torques from lookup table
        torque_data = outs(idx).yout{TOTAL_TORQUE_IDX}.Values.Data;
        % Use the latter half to skip start-up transients
        n_start = max(1, floor(length(torque_data) / 2));
        T_ss    = torque_data(n_start:end);

        mean_T   = mean(T_ss);
        ripple_T = max(T_ss) - min(T_ss);

        fprintf(fid, '%s,%.1f,%.2f,%.2f,%.2f,%.1f,%.1f,%.6f,%.6f\n', ...
            geom_id, rotorOR_radius * 2, rpap, spap, iaa, ...
            pair_list(idx,1), pair_list(idx,2), mean_T, ripple_T);
        n_written = n_written + 1;
    end

    fclose(fid);
    fprintf('[%s] DONE   %s  %d rows written\n', ...
        datestr(now,'HH:MM:SS'), make_geom_id(rotorOR_radius,rpap,spap), n_written);
    diary off;
end


% ── helper ────────────────────────────────────────────────────────────────────
function gid = make_geom_id(r_ro, rpap, spap)
    raw = sprintf('RR%04.1f_RPAP%.2f_SPAP%.2f', r_ro, rpap, spap);
    gid = strrep(raw, '.', 'p');
end
