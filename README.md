# SRM 12/8 Parameter Optimisation

Grid-search over SRM geometry and control angles to maximise average torque and minimise torque ripple.  
No iterative solver — exhaustive enumeration + Pareto selection.

---

## Quick start

### 1 — Run the grid search (ANSYS + MATLAB/Simulink)

Open **ANSYS Electronics Desktop**, then:

```
Tools → Run Script → RunGridSearch.py
```

To control parallelism (default 2 workers, 16 cores available):

```
ansysedt -runscript RunGridSearch.py --max-parallel 8
```

Outputs written incrementally to `GridSearchResults.csv`.  
Runs are **resume-safe** — already-completed geometries are skipped automatically.

### 2 — Select the best parameters

```bash
python SelectBestParams.py
# or point to a specific results file:
python SelectBestParams.py --csv path\to\GridSearchResults.csv --no-plot
```

Prints the best combination to console, saves `OptimizationReport.txt` and three PNG plots.

---

## What gets swept

| Parameter | Range | Step | Fixed at |
|---|---|---|---|
| RotorOuterRadius (diameter) | 80 – 100 mm | 5 mm | — |
| RotorPoleArcByPolePitch | 0.20 – 0.50 | 0.05 | — |
| StatorPoleArcByPolePitch | 0.10 – 0.40 | 0.05 | — |
| RotorYoke | — | — | 15 mm |
| gap | — | — | 0.25 mm |
| StatorOuterRadius (OD) | — | — | 80 mm |
| thi (turn-on angle) | 0 – 30 deg | 5 deg | swept in Simulink |
| thf (turn-off angle) | 20 – 45 deg | 5 deg | swept in Simulink |

**Iaa** is computed per geometry: `Iaa = (0.5 × slot_area × 5 A/mm²) / 10 turns`

**Total combinations:** 245 ANSYS runs × ~30 Simulink runs each ≈ 7 350 Simulink evaluations.

---

## Script map

```
RunGridSearch.py          ← ANSYS orchestrator (run via ANSYS scripting)
  └─ calls ANSYS          sets geometry, solves, exports flux_<id>.csv + torque_<id>.csv
  └─ calls MATLAB         ParamSweepAndSave.m  →  sweep_<id>.csv
       └─ parsim           runs all (thi,thf) pairs in parallel using parpool

ParamSweepAndSave.m       ← MATLAB function (called by RunGridSearch.py)
  Loads lookup tables from ANSYS CSVs, runs SRM_2DModel.slx in parallel,
  extracts mean torque and peak-to-peak ripple from yout{1} (total motor torque).

SelectBestParams.py       ← standalone Python, no ANSYS/MATLAB needed
  Reads GridSearchResults.csv, prints Pareto front, saves report + plots.
```

---

## Key constants to verify before running

In `RunGridSearch.py`:

| Constant | Default | Meaning |
|---|---|---|
| `MAX_PARALLEL_WORKERS` | `2` | parpool size passed to MATLAB |
| `H_SY_NOM` | `15.0 mm` | stator yoke thickness — **verify against AEDT nominal** |
| `R_SO` | `80.0 mm` | stator outer radius (fixed OD) |

---

## Requirements

- ANSYS Electronics Desktop 2018+
- MATLAB R2019b+ with Simulink and Parallel Computing Toolbox
- Python 3.x with `matplotlib` (`pip install matplotlib`) for plots in `SelectBestParams.py`
