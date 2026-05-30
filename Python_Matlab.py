# ----------------------------------------------
# Script Recorded by ANSYS Electronics Desktop Version 2018.0.0
# Updated to include MATLAB/Simulink Integration
# ----------------------------------------------
import ScriptEnv
import os
import subprocess

# --- 1. ANSYS INITIALIZATION ---
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
oProject = oDesktop.SetActiveProject("SRM_12_8_Optim")
oDesign = oProject.SetActiveDesign("oMaxwell2DDesig_Conditional1")

# --- 2. PARAMETER SETUP (Your Original Logic) ---
def SetProp(prop_name, value):
    oDesign.ChangeProperty([
        "NAME:AllTabs",
        ["NAME:LocalVariableTab", ["NAME:PropServers", "LocalVariables"],
        ["NAME:ChangedProps", ["NAME:" + prop_name, "Value:=", value]]]
    ])

SetProp("RotorOuterRadius", "49.6mm")
SetProp("RotorYoke", "15mm")
SetProp("StatorOuterRadius", "80mm")

oModule = oDesign.GetModule("ReportSetup")
oModule.DeleteAllReports()
#oProject.Save()

SetProp("Nc", "10")
SetProp("I_aa", "92A")
# oProject.Save()

# --- 3. ANALYSIS & OPTIMETRICS ---
oDesign.Analyze("Setup1")
oDesign.DeleteFullVariation("All", False)

oModule = oDesign.GetModule("Optimetrics")
# Note: Assuming "Iaa" setup already exists in the project as per your recording
oModule.SolveSetup("Iaa")

# --- 4. EXPORT DATA FOR SIMULINK ---
# Define the export path
export_dir = r"D:\Ansys\ConsultancyWork\GPP\Design"
csv_file_flux = os.path.join(export_dir, "FluxLinkage.csv")
csv_file_torque = os.path.join(export_dir, "Torque.csv")

if not os.path.exists(export_dir):
    os.makedirs(export_dir)

oModule = oDesign.GetModule("ReportSetup")
oModule.CreateReport("FluxLinkage", "Transient", "3D Rectangular Plot", "Setup1 : Transient", [], 
    [
        "Time:=", ["All"], "I_aa:=", ["All"], "RotorYoke:=", ["Nominal"],
        "RotorPoleArcByPolePitch:=", ["Nominal"], "StatorOuterRadius:=", ["Nominal"],
        "gap:=", ["Nominal"], "StatorYoke:=", ["Nominal"],
        "StatorPoleArcByPolePitch:=", ["Nominal"], "ThetaR:=", ["0deg"],
        "I_b:=", ["Nominal"], "I_c:=", ["Nominal"], "param:=", ["0"],
        "ThI:=", ["Nominal"], "Thf:=", ["Nominal"], "RotorOuterRadius:=", ["49.6mm"],
        "Nc:=", ["10"], "Spdr:=", ["Nominal"]
    ], 
    ["X Component:=", "Moving1.Position", "Y Component:=", "I_aa", "Z Component:=", ["FluxLinkage(A)"]], [])
oModule.ExportToFile("FluxLinkage", csv_file_flux)
oModule.CreateReport("Torque", "Transient", "3D Rectangular Plot", "Setup1 : Transient", [], 
    [
        "Time:=", ["All"], "I_aa:=", ["All"], "RotorYoke:=", ["Nominal"],
        "RotorPoleArcByPolePitch:=", ["Nominal"], "StatorOuterRadius:=", ["Nominal"],
        "gap:=", ["Nominal"], "StatorYoke:=", ["Nominal"],
        "StatorPoleArcByPolePitch:=", ["Nominal"], "ThetaR:=", ["0deg"],
        "I_b:=", ["Nominal"], "I_c:=", ["Nominal"], "param:=", ["0"],
        "ThI:=", ["Nominal"], "Thf:=", ["Nominal"], "RotorOuterRadius:=", ["49.6mm"],
        "Nc:=", ["10"], "Spdr:=", ["Nominal"]
    ], 
    ["X Component:=", "Moving1.Position", "Y Component:=", "I_aa", "Z Component:=", ["Moving1.Torque"]], [])
oModule.ExportToFile("Torque", csv_file_torque)
oProject.Save()

exit()

sys.exit("Stopping here for a reason")

# --- 5. INTERFACE WITH MATLAB/SIMULINK ---

# Path to your Simulink model (Ensure this file exists)
simulink_model_name = "SRM_2DModel" # Model name without .slx
simulink_model_path = os.path.join(export_dir, simulink_model_name + ".slx")
matlab_bridge_script = os.path.join(export_dir, "run_simulink_bridge.m")

# Create a MATLAB script dynamically to process the CSV
# This handles the 2D Lookup Table formatting and running the simulation
matlab_code = """
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
"""

# Write the MATLAB bridge file
with open(matlab_bridge_script, "w") as f:
    f.write(matlab_code)

# --- 6. EXECUTE MATLAB ---
# Construct the command line string
# We use -r to run the function then exit
# Updated to pass {1} (Flux) and {2} (Torque)
matlab_cmd = 'matlab -nosplash -nodesktop -wait -r "cd(\'{0}\'); run_simulink_bridge(\'{1}\', \'{2}\', \'{3}\'); exit;"'.format(
    export_dir, 
    flux_csv.replace("\\", "/"), 
    torque_csv.replace("\\", "/"), 
    simulink_model_path.replace("\\", "/")
)

print("Starting MATLAB/Simulink processing...")
try:
    # This will block Python execution until MATLAB closes
    subprocess.call(matlab_cmd, shell=True)
    print("Workflow complete. Data saved in: " + export_dir)
except Exception as e:
    print("Failed to run MATLAB: " + str(e))