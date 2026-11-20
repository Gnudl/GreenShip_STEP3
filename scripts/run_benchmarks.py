# -*- coding: utf-8 -*-
"""
Automation Runner for STEP 3 Benchmark Suite (3 funcs x 2 algos x 10 seeds).
"""

import sys
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

# Add paths
root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir))

from optimizers.common import CountedObjective
from optimizers.coa import optimize_coa
from optimizers.rime import optimize_rime
from benchmarks.functions import get_benchmark_suite

def main():
    suite = get_benchmark_suite(dim=10)
    seeds = list(range(10))
    results = []
    curves = {f: {"COA": [], "RIME": []} for f in suite}

    print("Running Benchmark Suite: 3 funcs x 2 algos x 10 seeds (D=10, N=20, max_fe=3000)...")
    for func_name, b_info in suite.items():
        for algo_name, opt_fn in [("COA", optimize_coa), ("RIME", optimize_rime)]:
            runs = []
            for s in seeds:
                obj = CountedObjective(b_info["fn"], budget=3000)
                bx, bf, fe_h, best_h = opt_fn(obj, b_info["bounds"], population_size=20, max_fe=3000, seed=s)
                runs.append({"seed": s, "best_f": bf, "fe": obj.fe})
                curves[func_name][algo_name].append(best_h)
            
            vals = [r["best_f"] for r in runs]
            fes = [r["fe"] for r in runs]
            results.append({
                "Function": func_name,
                "Algorithm": algo_name,
                "Mean": np.mean(vals),
                "Std": np.std(vals),
                "Min": np.min(vals),
                "Median": np.median(vals),
                "Max": np.max(vals),
                "FE": int(np.mean(fes))
            })

    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    
    out_dir = root_dir / "outputs"
    out_dir.mkdir(exist_ok=True)
    df.to_csv(out_dir / "benchmark_results_step3.csv", index=False)
    print(f"Saved CSV: {out_dir / 'benchmark_results_step3.csv'}")

    # Plot convergence
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    for idx, (func_name, c_dict) in enumerate(curves.items()):
        ax = axes[idx]
        fe_grid = np.linspace(20, 3000, 150)
        for algo_name, col, ls in [("COA", "#1F4E79", "-"), ("RIME", "#C00000", "--")]:
            interp_runs = [np.interp(fe_grid, np.linspace(20, 3000, len(c)), c) for c in c_dict[algo_name]]
            mean_c = np.mean(interp_runs, axis=0)
            ax.plot(fe_grid, mean_c, label=algo_name, color=col, linestyle=ls, lw=2)
        ax.set_title(f"Hội tụ hàm {func_name} (D=10, 10 seeds)")
        ax.set_xlabel("Số lần đánh giá hàm (FE)")
        ax.set_ylabel("best_f (Log scale)")
        ax.set_yscale("log")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()
    fig.savefig(out_dir / "benchmark_convergence_step3.png", dpi=300)
    print(f"Saved PNG: {out_dir / 'benchmark_convergence_step3.png'}")

if __name__ == "__main__":
    main()
