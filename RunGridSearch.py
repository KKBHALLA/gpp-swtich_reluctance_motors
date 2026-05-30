# RunGridSearch.py
# Full parameter grid search for SRM 12/8 optimization.
# Run from ANSYS Electronics Desktop: Tools > Run Script > RunGridSearch.py
#
# Geometric sweep (StatorOuterRadius = 80 mm radius, fixed outside diameter):
#   RotorOuterRadius : 40-50 mm radius  (= 80-100 mm diameter), step 2.5 mm
#   RotorYoke        : 15 mm (fixed)
#   gap              : 0.25 mm (fixed)
#   StatorYoke       : Nominal (from AEDT, unchanged)
#   RotorPoleArcByPolePitch  : 0.20 - 0.50, step 0.05
#   StatorPoleArcByPolePitch : 0.10 - 0.40, step 0.05
#
# For each geometry Iaa is computed from half the slot area at 5 A/mm^2.
# thi / thf are swept inside MATLAB by ParamSweepAndSave.m.
# Results accumulate in GridSearchResults.csv.

import ScriptEnv
import os
import subprocess
import math
import sys

# ── HYPERPARAMETER ─────────────────────────────────────────────────────────────
# Number of Simulink simulations MATLAB runs in parallel (controls parpool size).
# Default: 2 (conservative test setting on a 16-core PC).
# To override from command line when invoking via  ansysedt -runscript:
#   ansysedt -runscript RunGridSearch.py --max-parallel 8
MAX_PARALLEL_WORKERS = 2
_argv = list(sys.argv)
if '--max-parallel' in _argv:
    try:
        MAX_PARALLEL_WORKERS = int(_argv[_argv.index('--max-parallel') + 1])
        print("MAX_PARALLEL_WORKERS set to {} from command line.".format(MAX_PARALLEL_WORKERS))
    except (IndexError, ValueError):
        print("WARNING: --max-parallel value missing or invalid; using default {}.".format(
              MAX_PARALLEL_WORKERS))

# ── CONFIGURATION ──────────────────────────────────────────────────────────────
EXPORT_DIR   = r"D:\Ansys\ConsultancyWork\GPP\Design"
RESULTS_CSV  = os.path.join(EXPORT_DIR, "GridSearchResults.csv")
MODEL_PATH   = os.path.join(EXPORT_DIR, "SRM_2DModel.slx")

# Motor constants
NS        = 12       # number of stator poles
NC        = 10       # turns per coil (fixed)
J         = 5.0      # current density A/mm^2
FILL      = 0.5      # slot fill factor (half slot area)
R_SO      = 80.0     # stator outer radius mm (fixed outside diameter)
H_SY_NOM  = 15.0     # stator yoke thickness mm  -- verify against AEDT nominal
GAP       = 0.25     # air gap mm (fixed)
ROTOR_YOKE = 15.0    # rotor yoke mm (fixed)

# Geometric parameter grid
# RotorOuterRadius given as diameter 80-100 mm  =>  radius 40-50 mm, step 2.5 mm
ROTOR_OR_VEC = [40.0, 42.5, 45.0, 47.5, 50.0]
RPAP_VEC     = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
SPAP_VEC     = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]

# ── HELPERS ────────────────────────────────────────────────────────────────────

def set_prop(prop_name, value_str):
    oDesign.ChangeProperty([
        "NAME:AllTabs",
        ["NAME:LocalVariableTab",
         ["NAME:PropServers", "LocalVariables"],
         ["NAME:ChangedProps", ["NAME:" + prop_name, "Value:=", value_str]]]
    ])


def calc_iaa(r_ro, spap):
    """Peak phase current from half slot area × 5 A/mm².

    Slot area modelled as annular sector between stator bore and yoke inner radius.
    Returns None when geometry is infeasible (pole height <= 0).
    """
    r_si        = r_ro + GAP                    # stator bore radius
    r_sy_inner  = R_SO - H_SY_NOM              # inner radius of stator yoke
    h_pole      = r_sy_inner - r_si
    if h_pole <= 0.0:
        return None
    # annular sector area: (pi/Ns) * (1 - spap) * (r_sy_inner^2 - r_si^2)
    slot_area = (math.pi / NS) * (1.0 - spap) * (r_sy_inner**2 - r_si**2)
    return round((FILL * slot_area * J) / NC, 2)


def make_geom_id(r_ro, rpap, spap):
    raw = "RR{:04.1f}_RPAP{:.2f}_SPAP{:.2f}".format(r_ro, rpap, spap)
    return raw.replace(".", "p")


def export_flux_torque(r_ro, rpap, spap, iaa):
    """Set geometry in ANSYS, solve parametric sweep, export Flux and Torque CSVs.

    Skips if CSV files already exist (allows resuming a partial run).
    Returns (flux_csv_path, torque_csv_path).
    """
    gid        = make_geom_id(r_ro, rpap, spap)
    flux_csv   = os.path.join(EXPORT_DIR, "flux_{}.csv".format(gid))
    torque_csv = os.path.join(EXPORT_DIR, "torque_{}.csv".format(gid))

    if os.path.exists(flux_csv) and os.path.exists(torque_csv):
        print("  [SKIP ANSYS] results already exist for {}".format(gid))
        return flux_csv, torque_csv

    # Set geometry parameters
    set_prop("RotorOuterRadius",         "{:.2f}mm".format(r_ro))
    set_prop("RotorYoke",                "{:.1f}mm".format(ROTOR_YOKE))
    set_prop("gap",                      "{:.2f}mm".format(GAP))
    set_prop("RotorPoleArcByPolePitch",  str(rpap))
    set_prop("StatorPoleArcByPolePitch", str(spap))
    set_prop("StatorOuterRadius",        "{:.1f}mm".format(R_SO))
    set_prop("Nc",                       str(NC))
    set_prop("I_aa",                     "{:.2f}A".format(iaa))

    oModule_rep = oDesign.GetModule("ReportSetup")
    oModule_rep.DeleteAllReports()
    oProject.Save()

    # Solve transient
    oDesign.Analyze("Setup1")
    oDesign.DeleteFullVariation("All", False)

    # Update I_aa parametric sweep range to match computed peak current
    oModule_optim = oDesign.GetModule("Optimetrics")
    oModule_optim.EditSetup("Iaa", [
        "NAME:Iaa",
        "IsEnabled:=", True,
        ["NAME:ProdOptiSetupDataV2",
         "SaveFields:=", False, "CopyMesh:=", False,
         "SolveWithCopiedMeshOnly:=", False],
        ["NAME:StartingPoint", "I_aa:=", "{:.2f}A".format(iaa)],
        "Sim. Setups:=", ["Setup1"],
        ["NAME:Sweeps",
         ["NAME:SweepDefinition",
          "Variable:=", "I_aa",
          "Data:=",     "LINC 0A {:.2f}A 10".format(iaa),
          "OffsetF1:=", False,
          "Synchronize:=", 0]],
        ["NAME:Sweep Operations"],
        ["NAME:Goals"]
    ])
    oProject.Save()
    oModule_optim.SolveSetup("Iaa")

    # Common report parameter list (all geometric params at Nominal = current set values)
    rep_params = [
        "Time:=", ["All"], "I_aa:=", ["All"],
        "RotorYoke:=",                 ["Nominal"],
        "RotorPoleArcByPolePitch:=",   ["Nominal"],
        "StatorOuterRadius:=",         ["Nominal"],
        "gap:=",                       ["Nominal"],
        "StatorYoke:=",                ["Nominal"],
        "StatorPoleArcByPolePitch:=",  ["Nominal"],
        "ThetaR:=",                    ["0deg"],
        "I_b:=", ["Nominal"], "I_c:=", ["Nominal"],
        "param:=", ["0"],
        "ThI:=",  ["Nominal"], "Thf:=", ["Nominal"],
        "RotorOuterRadius:=",          ["Nominal"],
        "Nc:=",   [str(NC)],
        "Spdr:=", ["Nominal"]
    ]

    oModule_rep.CreateReport(
        "FluxLinkage", "Transient", "3D Rectangular Plot",
        "Setup1 : Transient", [], rep_params,
        ["X Component:=", "Moving1.Position",
         "Y Component:=", "I_aa",
         "Z Component:=", ["FluxLinkage(A)"]], [])
    oModule_rep.ExportToFile("FluxLinkage", flux_csv)

    oModule_rep.CreateReport(
        "Torque", "Transient", "3D Rectangular Plot",
        "Setup1 : Transient", [], rep_params,
        ["X Component:=", "Moving1.Position",
         "Y Component:=", "I_aa",
         "Z Component:=", ["Moving1.Torque"]], [])
    oModule_rep.ExportToFile("Torque", torque_csv)

    oModule_rep.DeleteAllReports()
    oProject.Save()

    return flux_csv, torque_csv


def run_matlab_sweep(flux_csv, torque_csv, r_ro, rpap, spap, iaa, max_workers):
    """Call MATLAB to sweep thi/thf for the given geometry.

    MATLAB runs ParamSweepAndSave, which writes a per-geometry CSV.
    max_workers is forwarded to MATLAB to control the parsim parpool size.
    Returns path to that CSV (or None if MATLAB failed).
    """
    gid       = make_geom_id(r_ro, rpap, spap)
    sweep_csv = os.path.join(EXPORT_DIR, "sweep_{}.csv".format(gid))

    if os.path.exists(sweep_csv):
        print("  [SKIP MATLAB] sweep already done for {}".format(gid))
        return sweep_csv

    cmd = (
        "matlab -nosplash -nodesktop -wait "
        "-r \"cd('{dir}'); "
        "ParamSweepAndSave('{flux}', '{torque}', '{model}', '{out}', "
        "{r_ro}, {rpap}, {spap}, {iaa}, {max_workers}); exit;\""
    ).format(
        dir         = EXPORT_DIR.replace("\\", "/"),
        flux        = flux_csv.replace("\\", "/"),
        torque      = torque_csv.replace("\\", "/"),
        model       = MODEL_PATH.replace("\\", "/"),
        out         = sweep_csv.replace("\\", "/"),
        r_ro        = r_ro,
        rpap        = rpap,
        spap        = spap,
        iaa         = iaa,
        max_workers = max_workers
    )
    subprocess.call(cmd, shell=True)

    if not os.path.exists(sweep_csv):
        print("  [WARN] MATLAB sweep produced no output for {}".format(gid))
        return None
    return sweep_csv


# ── MAIN ───────────────────────────────────────────────────────────────────────
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
oProject = oDesktop.SetActiveProject("SRM_12_8_Optim")
oDesign  = oProject.SetActiveDesign("oMaxwell2DDesig_Conditional1")

# Write master CSV header once
if not os.path.exists(RESULTS_CSV):
    with open(RESULTS_CSV, "w") as f:
        f.write("geom_id,RotorOR_dia_mm,RotorPoleArcByPolePitch,"
                "StatorPoleArcByPolePitch,Iaa_A,"
                "thi_deg,thf_deg,mean_torque_Nm,torque_ripple_Nm\n")

total      = len(ROTOR_OR_VEC) * len(RPAP_VEC) * len(SPAP_VEC)
completed  = 0
skipped    = 0

for r_ro in ROTOR_OR_VEC:
    for rpap in RPAP_VEC:
        for spap in SPAP_VEC:
            iaa = calc_iaa(r_ro, spap)
            if iaa is None or iaa <= 0:
                print("SKIP infeasible geometry: RR={} SPAP={}".format(r_ro, spap))
                skipped += 1
                continue

            gid = make_geom_id(r_ro, rpap, spap)
            completed += 1
            print("[{}/{}] {} | Iaa={:.1f} A".format(completed, total - skipped, gid, iaa))

            try:
                flux_csv, torque_csv = export_flux_torque(r_ro, rpap, spap, iaa)
                sweep_csv = run_matlab_sweep(flux_csv, torque_csv, r_ro, rpap, spap, iaa,
                                             MAX_PARALLEL_WORKERS)

                # Append per-geometry rows to master results CSV
                if sweep_csv and os.path.exists(sweep_csv):
                    with open(sweep_csv, "r") as fsrc:
                        lines = fsrc.readlines()
                    with open(RESULTS_CSV, "a") as fdst:
                        fdst.writelines(lines[1:])  # skip header

            except Exception as ex:
                print("  ERROR for {}: {}".format(gid, str(ex)))

print("\nGrid search complete. Master results: {}".format(RESULTS_CSV))
