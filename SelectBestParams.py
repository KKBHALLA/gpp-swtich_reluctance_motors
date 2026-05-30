#!/usr/bin/env python3
"""
SelectBestParams.py
Post-processing script: reads GridSearchResults.csv (written by RunGridSearch.py)
and selects optimal SRM 12/8 parameters using:
  - Single-objective: maximum mean torque
  - Single-objective: minimum torque ripple (within 80 % of peak torque)
  - Multi-objective : Pareto front (maximise mean torque AND minimise ripple)

Usage (standalone, no ANSYS required):
    python SelectBestParams.py
    python SelectBestParams.py --csv path\to\GridSearchResults.csv
    python SelectBestParams.py --no-plot
"""

import csv
import os
import argparse

try:
    import matplotlib
    matplotlib.use("Agg")          # non-interactive backend for Windows without display
    import matplotlib.pyplot as plt
    HAS_PLOT = True
except ImportError:
    HAS_PLOT = False

DEFAULT_CSV = r"D:\Ansys\ConsultancyWork\GPP\Design\GridSearchResults.csv"
REPORT_PATH = r"D:\Ansys\ConsultancyWork\GPP\Design\OptimizationReport.txt"

# ── DATA LOADING ──────────────────────────────────────────────────────────────

def load_results(csv_path):
    rows = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append({
                    "geom_id":                  row["geom_id"].strip(),
                    "RotorOR_dia_mm":           float(row["RotorOR_dia_mm"]),
                    "RotorPoleArcByPolePitch":  float(row["RotorPoleArcByPolePitch"]),
                    "StatorPoleArcByPolePitch": float(row["StatorPoleArcByPolePitch"]),
                    "Iaa_A":                    float(row["Iaa_A"]),
                    "thi_deg":                  float(row["thi_deg"]),
                    "thf_deg":                  float(row["thf_deg"]),
                    "mean_torque_Nm":           float(row["mean_torque_Nm"]),
                    "torque_ripple_Nm":         float(row["torque_ripple_Nm"]),
                })
            except (KeyError, ValueError):
                pass  # skip malformed rows
    return rows

# ── PARETO FRONT ──────────────────────────────────────────────────────────────

def pareto_front(rows):
    """Non-dominated set: maximise mean_torque, minimise torque_ripple."""
    front = []
    for candidate in rows:
        dominated = False
        for other in rows:
            if other is candidate:
                continue
            better_torque = other["mean_torque_Nm"]  >= candidate["mean_torque_Nm"]
            better_ripple = other["torque_ripple_Nm"] <= candidate["torque_ripple_Nm"]
            strictly_better = (
                other["mean_torque_Nm"]  > candidate["mean_torque_Nm"] or
                other["torque_ripple_Nm"] < candidate["torque_ripple_Nm"]
            )
            if better_torque and better_ripple and strictly_better:
                dominated = True
                break
        if not dominated:
            front.append(candidate)
    return front

# ── PRINT HELPERS ─────────────────────────────────────────────────────────────

def print_row(label, row):
    if row["mean_torque_Nm"] > 0:
        ripple_pct = row["torque_ripple_Nm"] / row["mean_torque_Nm"] * 100.0
    else:
        ripple_pct = float("nan")
    print("  {}".format(label))
    print("    Geom ID                 : {}".format(row["geom_id"]))
    print("    Rotor OD (diameter)     : {:.1f} mm".format(row["RotorOR_dia_mm"]))
    print("    RotorPoleArcByPolePitch : {:.2f}".format(row["RotorPoleArcByPolePitch"]))
    print("    StatorPoleArcByPolePitch: {:.2f}".format(row["StatorPoleArcByPolePitch"]))
    print("    Iaa (peak current)      : {:.2f} A".format(row["Iaa_A"]))
    print("    Turn-on  angle  (thi)   : {:.1f} deg".format(row["thi_deg"]))
    print("    Turn-off angle  (thf)   : {:.1f} deg".format(row["thf_deg"]))
    print("    Mean torque             : {:.4f} Nm".format(row["mean_torque_Nm"]))
    print("    Torque ripple (pk-pk)   : {:.4f} Nm  ({:.1f} % of mean)".format(
        row["torque_ripple_Nm"], ripple_pct))


def fmt_row(row):
    ripple_pct = (row["torque_ripple_Nm"] / row["mean_torque_Nm"] * 100.0
                  if row["mean_torque_Nm"] > 0 else float("nan"))
    return ("  geom={:<30s}  thi={:4.0f}  thf={:4.0f}"
            "  T={:.4f} Nm  ripple={:.4f} Nm ({:.1f}%)").format(
        row["geom_id"],
        row["thi_deg"], row["thf_deg"],
        row["mean_torque_Nm"], row["torque_ripple_Nm"], ripple_pct)

# ── REPORT ────────────────────────────────────────────────────────────────────

def save_report(rows, front, best_torque, best_ripple):
    front_sorted = sorted(front, key=lambda r: -r["mean_torque_Nm"])
    with open(REPORT_PATH, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("SRM 12/8 Grid Search Optimisation Report\n")
        f.write("=" * 70 + "\n\n")
        f.write("Total evaluated combinations : {}\n".format(len(rows)))
        f.write("Pareto-optimal combinations  : {}\n\n".format(len(front)))

        f.write("--- Best Mean Torque ---\n")
        for k, v in best_torque.items():
            f.write("  {:30s}: {}\n".format(k, v))
        f.write("\n")

        f.write("--- Lowest Torque Ripple (torque >= 80% of peak) ---\n")
        for k, v in best_ripple.items():
            f.write("  {:30s}: {}\n".format(k, v))
        f.write("\n")

        f.write("--- Pareto Front (sorted by torque) ---\n")
        for i, row in enumerate(front_sorted):
            f.write("  #{:02d}  {}\n".format(i + 1, fmt_row(row)))

    print("\nText report saved to: {}".format(REPORT_PATH))

# ── PLOTS ─────────────────────────────────────────────────────────────────────

def plot_results(rows, front, out_dir):
    # 1. Pareto scatter
    torques   = [r["mean_torque_Nm"]   for r in rows]
    ripples   = [r["torque_ripple_Nm"] for r in rows]
    f_torques = [r["mean_torque_Nm"]   for r in front]
    f_ripples = [r["torque_ripple_Nm"] for r in front]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(torques, ripples, c="steelblue", alpha=0.3, s=12,
               label="All combinations ({})".format(len(rows)))
    ax.scatter(f_torques, f_ripples, c="crimson", s=55, zorder=5,
               label="Pareto front ({})".format(len(front)))
    ax.set_xlabel("Mean Torque (Nm)")
    ax.set_ylabel("Torque Ripple peak-to-peak (Nm)")
    ax.set_title("SRM 12/8 Optimisation — Pareto Front")
    ax.legend()
    fig.tight_layout()
    p = os.path.join(out_dir, "ParetoFront.png")
    fig.savefig(p, dpi=150)
    plt.close(fig)
    print("Pareto plot saved: {}".format(p))

    # 2. Parameter sensitivity: mean torque vs each geometric param
    param_keys   = ["RotorOR_dia_mm",
                    "RotorPoleArcByPolePitch",
                    "StatorPoleArcByPolePitch"]
    param_labels = ["Rotor OD (mm)",
                    "RotorPoleArcByPolePitch",
                    "StatorPoleArcByPolePitch"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, pk, pl in zip(axes, param_keys, param_labels):
        pv = [r[pk] for r in rows]
        ax.scatter(pv, torques, alpha=0.25, s=8, c="steelblue")
        ax.set_xlabel(pl)
        ax.set_ylabel("Mean Torque (Nm)")
        ax.set_title(pl)
    fig.suptitle("Parameter Sensitivity — Mean Torque")
    fig.tight_layout()
    p = os.path.join(out_dir, "ParamSensitivity.png")
    fig.savefig(p, dpi=150)
    plt.close(fig)
    print("Sensitivity plot saved: {}".format(p))

    # 3. thi / thf heat-map for the best geometry (most common in Pareto front)
    if front:
        from collections import Counter
        geom_counts = Counter(r["geom_id"] for r in front)
        top_geom    = geom_counts.most_common(1)[0][0]
        geom_rows   = [r for r in rows if r["geom_id"] == top_geom]
        if geom_rows:
            thi_vals  = sorted(set(r["thi_deg"] for r in geom_rows))
            thf_vals  = sorted(set(r["thf_deg"] for r in geom_rows))
            heat      = [[float("nan")] * len(thf_vals) for _ in thi_vals]
            for r in geom_rows:
                i = thi_vals.index(r["thi_deg"])
                j = thf_vals.index(r["thf_deg"])
                heat[i][j] = r["mean_torque_Nm"]

            fig, ax = plt.subplots(figsize=(8, 6))
            import numpy as np
            img = ax.imshow(heat, aspect="auto", origin="lower",
                            extent=[min(thf_vals)-2.5, max(thf_vals)+2.5,
                                    min(thi_vals)-2.5, max(thi_vals)+2.5])
            plt.colorbar(img, ax=ax, label="Mean Torque (Nm)")
            ax.set_xlabel("thf (deg)")
            ax.set_ylabel("thi (deg)")
            ax.set_title("thi / thf Map — best geometry\n{}".format(top_geom))
            fig.tight_layout()
            p = os.path.join(out_dir, "ThetaMap_BestGeom.png")
            fig.savefig(p, dpi=150)
            plt.close(fig)
            print("Theta map saved: {}".format(p))

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Select best SRM parameters from grid search results.")
    parser.add_argument("--csv",     default=DEFAULT_CSV,
                        help="Path to GridSearchResults.csv")
    parser.add_argument("--no-plot", action="store_true",
                        help="Skip matplotlib plots")
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print("ERROR: results file not found:\n  {}".format(args.csv))
        return

    rows = load_results(args.csv)
    print("Loaded {} rows from {}".format(len(rows), args.csv))
    if not rows:
        print("No data found.")
        return

    # Filter degenerate rows (zero or negative mean torque)
    rows = [r for r in rows if r["mean_torque_Nm"] > 0.0]
    print("Valid rows (mean_torque > 0): {}".format(len(rows)))
    if not rows:
        print("No valid rows after filtering.")
        return

    # ── Single-objective: maximum mean torque ─────────────────────────────────
    best_torque_row = max(rows, key=lambda r: r["mean_torque_Nm"])

    # ── Single-objective: minimum ripple, restricted to top 80 % of torque ───
    threshold       = 0.80 * best_torque_row["mean_torque_Nm"]
    high_torque     = [r for r in rows if r["mean_torque_Nm"] >= threshold]
    best_ripple_row = min(high_torque, key=lambda r: r["torque_ripple_Nm"])

    # ── Multi-objective Pareto front ──────────────────────────────────────────
    front = pareto_front(rows)
    front_sorted = sorted(front, key=lambda r: -r["mean_torque_Nm"])

    # ── Print to console ──────────────────────────────────────────────────────
    sep = "=" * 70
    print("\n" + sep)
    print("SINGLE-OBJECTIVE: Maximum Mean Torque")
    print(sep)
    print_row("", best_torque_row)

    print("\n" + sep)
    print("SINGLE-OBJECTIVE: Minimum Torque Ripple  "
          "(torque >= {:.2f} Nm, i.e. >= 80% of peak)".format(threshold))
    print(sep)
    print_row("", best_ripple_row)

    print("\n" + sep)
    print("PARETO FRONT — {} points  (sorted by torque, highest first)".format(len(front)))
    print(sep)
    for i, row in enumerate(front_sorted):
        print("  #{:02d}  {}".format(i + 1, fmt_row(row)))

    # ── Save text report ──────────────────────────────────────────────────────
    bt = {k: best_torque_row[k] for k in best_torque_row}
    br = {k: best_ripple_row[k] for k in best_ripple_row}
    save_report(rows, front, bt, br)

    # ── Plots ─────────────────────────────────────────────────────────────────
    out_dir = os.path.dirname(args.csv)
    if HAS_PLOT and not args.no_plot:
        plot_results(rows, front, out_dir)
    elif not HAS_PLOT:
        print("matplotlib not available — skipping plots (install with: pip install matplotlib).")


if __name__ == "__main__":
    main()
