# SRM 12/8 Optimisation — Claude Code Context

## What this project does
Grid-search over SRM 12/8 geometry and control angles to maximise average torque and minimise torque ripple.
No iterative solver — exhaustive enumeration + Pareto selection.

## Workflow (end to end)
```
ANSYS (RunGridSearch.py)
  ├─ sets geometry params in SRM_12_8_Optim.aedt / oMaxwell2DDesig_Conditional1
  ├─ runs Setup1 + Optimetrics "Iaa" parametric sweep
  ├─ exports  flux_<geomID>.csv  and  torque_<geomID>.csv
  └─ calls MATLAB ──►

MATLAB (ParamSweepAndSave.m)
  ├─ loads flux / torque CSVs into 2-D lookup tables
  ├─ runs SRM_2DModel.slx sequentially for every (thi, thf) pair
  ├─ yout{1} = total motor torque (sum of 2 phase-shifted LUT torques)
  ├─ yout{2} = power (ignored)
  └─ writes  sweep_<geomID>.csv  ──►

Python (SelectBestParams.py)
  ├─ reads GridSearchResults.csv (master, aggregated from all sweeps)
  ├─ prints best mean-torque, best ripple, and full Pareto front
  └─ saves OptimizationReport.txt + plots
```

## Key files
| File | Role |
|---|---|
| `RunGridSearch.py` | ANSYS orchestrator — run via Tools → Run Script |
| `ParamSweepAndSave.m` | MATLAB function called per geometry |
| `SelectBestParams.py` | Standalone post-processing, no ANSYS/MATLAB needed |
| `TestPipeline.m` | Smoke-test using existing CSVs, 4 Simulink runs |
| `SRM_2DModel.slx` | Simulink model (2-phase LUT-based SRM) |
| `SRM_12_8_Optim.aedt` | ANSYS Maxwell design |
| `GridSearch.log` | Live diary log written by ParamSweepAndSave.m |
| `GridSearchResults.csv` | Master results (all geometries × all angle pairs) |

## Parameter sweep ranges
| Parameter | Range | Notes |
|---|---|---|
| RotorOuterRadius | 40–50 mm radius (80–100 mm dia) | step 2.5 mm radius |
| RotorPoleArcByPolePitch | 0.20–0.50 | step 0.05 |
| StatorPoleArcByPolePitch | 0.10–0.40 | step 0.05 |
| RotorYoke | 15 mm | fixed |
| gap | 0.25 mm | fixed |
| StatorOuterRadius | 80 mm | fixed outside diameter |
| thi (turn-on) | 0–30 deg | step 5 deg, swept in Simulink |
| thf (turn-off) | 20–45 deg | step 5 deg, swept in Simulink |
| Nc | 10 turns | fixed |

Iaa per geometry: `(0.5 × slot_area × 5 A/mm²) / 10`
where `slot_area = (π/12) × (1 − spap) × (R_sy_inner² − R_si²)`, R_sy_inner = 65 mm.

## Constants to verify before a full run
In `RunGridSearch.py`:
- `H_SY_NOM = 15.0` — stator yoke thickness mm, **verify against AEDT nominal**
- `MAX_PARALLEL_WORKERS = 2` — no Parallel Computing Toolbox on this machine; value is passed through but `ParamSweepAndSave.m` runs sequentially

## Known issues / findings (updated 2026-05-30)

### 1 — No Parallel Computing Toolbox
`parsim` and `gcp` throw "requires Parallel Computing Toolbox".
**Fix applied:** `ParamSweepAndSave.m` runs a plain `for` loop with `sim()`. `maxWorkers` arg is accepted but ignored until PCT is installed.

### 2 — Lookup table position offset
ANSYS exports rotor positions starting at `InitPos` (e.g., 10°), not 0°.
Simulink expects 0° = unaligned position. Without correction, positions outside the exported range extrapolate badly → large negative/wrong torques.
**Fix applied:** `ParamSweepAndSave.m` subtracts `min(pos)` from both flux and torque table positions before building the lookup tables.

### 3 — ANSYS current sweep range in test CSVs
The existing `FluxLinkage.csv` / `Torque.csv` were exported with an incorrect current sweep (0–440 A in 44 A steps instead of 0–115 A in 11.5 A steps). This gives a very coarse lookup table.
**Status:** Not yet fixed. Requires a fresh ANSYS run with corrected Optimetrics setup:
`"Data:=", "LINC 0A 115A 10"` in the `Iaa` parametric sweep.

### 4 — Torque sign convention
Torque in the ANSYS CSV is negative for rotor positions before the aligned position and positive after. This is physically correct. The Simulink model averages over a full excitation cycle; if thi is too large (past alignment) net torque will be negative.
**Rule of thumb for 12/8 SRM with this data:** peak positive torque is around θ = 22° (after offset correction); set thi ≈ 10–15° and thf ≈ 22–35° for positive average torque.

## Running on a new machine
1. Clone repo: `git clone git@github.com:KKBHALLA/gpp-swtich_reluctance_motors.git`
2. Open `SRM_12_8_Optim.aedt` in ANSYS Electronics Desktop
3. Open MATLAB, `cd` to the repo folder
4. Run `TestPipeline` in MATLAB to verify the MATLAB/Simulink pipeline
5. Run `RunGridSearch.py` from ANSYS (Tools → Run Script) for full sweep
6. Run `python SelectBestParams.py` for results

## Repo / git
- Remote: `git@github.com:KKBHALLA/gpp-swtich_reluctance_motors.git`
- SSH key: `~/.ssh/id_ed25519` (ed25519, no passphrase)
- Ignored: `slprj/`, `SRM_12_8_Optim.aedtresults/`, `*.slxc`, `*.asv`, `.claude/`, generated CSVs/PNGs
