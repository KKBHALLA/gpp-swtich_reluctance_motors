% TestPipeline.m
% Quick pipeline smoke-test: skips ANSYS, uses existing FluxLinkage.csv
% and Torque.csv, runs 2 (thi, thf) combinations in parallel, writes
% TestResults.csv, then reports pass/fail.

clc;
BASE = fileparts(mfilename('fullpath'));
diary(fullfile(BASE, 'TestPipeline.log'));
diary on;
fprintf('=== SRM 12/8 Pipeline Test ===\n');

fluxPath   = fullfile(BASE, 'FluxLinkage.csv');
torquePath = fullfile(BASE, 'Torque.csv');
modelPath  = fullfile(BASE, 'SRM_2DModel.slx');
outPath    = fullfile(BASE, 'TestResults.csv');

% Minimal sweep: just 2 valid (thi, thf) pairs
thi_vec = [10, 15];
thf_vec = [30, 35];

% Nominal geometry values (matching the existing ANSYS CSV data)
rotorOR_radius = 49.6;
rpap           = 0.35;
spap           = 0.25;
iaa            = 80.0;
maxWorkers     = 2;

fprintf('Flux CSV  : %s\n', fluxPath);
fprintf('Torque CSV: %s\n', torquePath);
fprintf('Model     : %s\n', modelPath);
fprintf('Sweep     : thi=%s  thf=%s\n', mat2str(thi_vec), mat2str(thf_vec));
fprintf('Workers   : %d\n\n', maxWorkers);

% Delete stale output so we can confirm a fresh write
if exist(outPath, 'file'); delete(outPath); end

%% Run
ParamSweepAndSave(fluxPath, torquePath, modelPath, outPath, ...
                  rotorOR_radius, rpap, spap, iaa, maxWorkers, ...
                  thi_vec, thf_vec);

%% Verify output
if ~exist(outPath, 'file')
    error('FAIL: TestResults.csv was not created.');
end

results = readtable(outPath);
fprintf('\n--- TestResults.csv (%d rows) ---\n', height(results));
disp(results);

if height(results) == 0
    error('FAIL: output file is empty.');
end

fprintf('\nPASS: pipeline completed successfully.\n');
fprintf('Run SelectBestParams.py --csv TestResults.csv to test the Python side.\n');
diary off;
