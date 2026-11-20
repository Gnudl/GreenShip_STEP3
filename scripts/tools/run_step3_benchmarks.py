import sys
import os
import time
import math
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

# Set up matplotlib config dir to avoid permission warnings
os.environ["MPLCONFIGDIR"] = str(Path.cwd() / "outputs" / ".matplotlib")

# 1. Benchmark Functions (D=10)
def sphere(x):
    x = np.asarray(x, dtype=float)
    return float(np.sum(x**2))

def rastrigin(x):
    x = np.asarray(x, dtype=float)
    return float(10.0 * len(x) + np.sum(x**2 - 10.0 * np.cos(2.0 * np.pi * x)))

def rosenbrock(x):
    x = np.asarray(x, dtype=float)
    return float(np.sum(100.0 * (x[1:] - x[:-1]**2)**2 + (x[:-1] - 1.0)**2))

class CountedObjective:
    def __init__(self, fn, budget=3000):
        self.fn = fn
        self.budget = budget
        self.fe = 0
        self.history_fe = []
        self.history_best = []
        self.best_f = float("inf")
        self.best_x = None

    def __call__(self, x):
        if self.fe >= self.budget:
            # Return current best or evaluate without exceeding budget
            return self.best_f
        self.fe += 1
        val = float(self.fn(x))
        if val < self.best_f:
            self.best_f = val
            self.best_x = np.copy(x)
        self.history_fe.append(self.fe)
        self.history_best.append(self.best_f)
        return val

# 2. Implementation of Original COA (Jia et al., 2023) with FE counter
def optimize_coa(objective, bounds, population_size=20, max_fe=3000, seed=0):
    rng = np.random.default_rng(seed)
    dim = len(bounds)
    lb = np.array([b[0] for b in bounds], dtype=float)
    ub = np.array([b[1] for b in bounds], dtype=float)

    # Initialization
    X = lb + rng.uniform(0.0, 1.0, (population_size, dim)) * (ub - lb)
    fitness = np.zeros(population_size)
    for i in range(population_size):
        if objective.fe >= max_fe:
            break
        fitness[i] = objective(X[i])

    best_idx = np.argmin(fitness)
    best_solution = np.copy(X[best_idx])
    best_fitness = fitness[best_idx]

    # Iteration loop
    # Estimate max iterations from budget
    max_iter = max(1, max_fe // population_size)
    t = 0
    while objective.fe < max_fe:
        t += 1
        temp = rng.uniform(20.0, 35.0)
        C1 = 2.0 * (1.0 - t / max_iter) if t <= max_iter else 0.05
        X_cave = np.copy(best_solution)
        X_food = np.copy(best_solution)

        for i in range(population_size):
            if objective.fe >= max_fe:
                break
            if temp > 30.0:
                # Summer resort stage
                if rng.uniform(0.0, 1.0) < 0.5:
                    # Seeking shelter
                    X[i] = X[i] + C1 * rng.uniform(0.0, 1.0, dim) * (X_cave - X[i])
                else:
                    # Competition stage
                    z = rng.integers(0, population_size)
                    X[i] = X[i] - X[z] + X_cave
            else:
                # Foraging stage (temp <= 30)
                Q = rng.uniform(0.5, 2.5)
                if Q <= 2.0:
                    # Small food: direct foraging
                    p = C1 * (rng.uniform(0.0, 1.0, dim) - 0.5)
                    X[i] = X[i] + C1 * rng.uniform(0.0, 1.0, dim) * (X_food - X[i]) + p
                else:
                    # Large food: tearing motion
                    angle = rng.uniform(0.0, 2.0 * np.pi)
                    X_torn = np.exp(-1.0 / Q) * X_food
                    X[i] = X[i] + X_torn * (np.cos(angle) - np.sin(angle))

            # Boundary clipping
            X[i] = np.clip(X[i], lb, ub)
            f_new = objective(X[i])
            if f_new < fitness[i]:
                fitness[i] = f_new
                if f_new < best_fitness:
                    best_fitness = f_new
                    best_solution = np.copy(X[i])

    return best_solution, best_fitness, objective.history_fe, objective.history_best

# 3. Implementation of Original RIME (Su et al., 2023) with FE counter
def optimize_rime(objective, bounds, population_size=20, max_fe=3000, seed=0):
    rng = np.random.default_rng(seed)
    dim = len(bounds)
    lb = np.array([b[0] for b in bounds], dtype=float)
    ub = np.array([b[1] for b in bounds], dtype=float)

    # Initialization
    Rime = lb + rng.uniform(0.0, 1.0, (population_size, dim)) * (ub - lb)
    fitness = np.zeros(population_size)
    for i in range(population_size):
        if objective.fe >= max_fe:
            break
        fitness[i] = objective(Rime[i])

    best_idx = np.argmin(fitness)
    best_solution = np.copy(Rime[best_idx])
    best_fitness = fitness[best_idx]

    max_iter = max(1, max_fe // population_size)
    t = 0
    while objective.fe < max_fe:
        t += 1
        # Soft-rime motion coefficient R
        R = rng.uniform(-1.0, 1.0) * np.cos((np.pi * t) / (2.0 * max_iter))
        # Adhesion coefficient E
        E = np.sqrt(min(1.0, (t + 1.0) / max_iter))
        new_Rime = np.copy(Rime)

        # Soft-rime search strategy
        for i in range(population_size):
            for j in range(dim):
                if rng.uniform(0.0, 1.0) < E:
                    new_Rime[i, j] = best_solution[j] + R * (rng.uniform(0.0, 1.0) * (ub[j] - lb[j]) + lb[j])

        # Hard-rime puncture mechanism
        f_min, f_max = np.min(fitness), np.max(fitness)
        denom = f_max - f_min + 1e-12
        fit_norm = (fitness - f_min) / denom

        for i in range(population_size):
            for j in range(dim):
                if rng.uniform(0.0, 1.0) < fit_norm[i]:
                    new_Rime[i, j] = best_solution[j]

        # Greedy selection & evaluation
        for i in range(population_size):
            if objective.fe >= max_fe:
                break
            new_Rime[i] = np.clip(new_Rime[i], lb, ub)
            f_new = objective(new_Rime[i])
            if f_new < fitness[i]:
                fitness[i] = f_new
                Rime[i] = np.copy(new_Rime[i])
                if f_new < best_fitness:
                    best_fitness = f_new
                    best_solution = np.copy(new_Rime[i])

    return best_solution, best_fitness, objective.history_fe, objective.history_best

print("=== CHẠY BENCHMARK 3 HÀM X 2 THUẬT TOÁN X 10 SEEDS (D=10, N=20, MAX_FE=3000) ===")
benchmarks = {
    "Sphere": {"fn": sphere, "bounds": [(-5.12, 5.12)] * 10, "opt": 0.0},
    "Rastrigin": {"fn": rastrigin, "bounds": [(-5.12, 5.12)] * 10, "opt": 0.0},
    "Rosenbrock": {"fn": rosenbrock, "bounds": [(-2.048, 2.048)] * 10, "opt": 0.0}
}

seeds = list(range(10))
results_summary = []
convergence_curves = {}

for func_name, b_info in benchmarks.items():
    convergence_curves[func_name] = {"COA": [], "RIME": []}
    for algo_name, opt_fn in [("COA", optimize_coa), ("RIME", optimize_rime)]:
        runs = []
        for s in seeds:
            obj = CountedObjective(b_info["fn"], budget=3000)
            best_x, best_f, fe_hist, best_hist = opt_fn(obj, b_info["bounds"], population_size=20, max_fe=3000, seed=s)
            runs.append({"seed": s, "best_f": best_f, "fe": obj.fe})
            convergence_curves[func_name][algo_name].append(best_hist)
            
        vals = [r["best_f"] for r in runs]
        fes = [r["fe"] for r in runs]
        results_summary.append({
            "Function": func_name,
            "Algorithm": algo_name,
            "Mean": np.mean(vals),
            "Std": np.std(vals),
            "Min": np.min(vals),
            "Median": np.median(vals),
            "Max": np.max(vals),
            "FE": int(np.mean(fes))
        })

df_res = pd.DataFrame(results_summary)
print(df_res.to_string(index=False))

# Lưu CSV
df_res.to_csv("outputs/benchmark_results_step3.csv", index=False)

# Vẽ đồ thị Convergence
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
for idx, (func_name, curves) in enumerate(convergence_curves.items()):
    ax = axes[idx]
    for algo_name, color, line in [("COA", "#1F4E79", "-"), ("RIME", "#C00000", "--")]:
        # Interpolate curves over uniform FE grid
        fe_grid = np.linspace(20, 3000, 150)
        interp_runs = []
        for c in curves[algo_name]:
            # make sure length matches
            x_pts = np.linspace(20, 3000, len(c))
            interp_runs.append(np.interp(fe_grid, x_pts, c))
        mean_curve = np.mean(interp_runs, axis=0)
        ax.plot(fe_grid, mean_curve, label=algo_name, color=color, linestyle=line, lw=2)
    ax.set_title(f"Hội tụ hàm {func_name} (D=10, 10 seeds)")
    ax.set_xlabel("Số lần đánh giá hàm (FE)")
    ax.set_ylabel("Hàm mục tiêu tốt nhất (best_f)")
    ax.set_yscale("log")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend()

fig.savefig("outputs/benchmark_convergence_step3.png", dpi=300)
print("\nĐã lưu ảnh hội tụ outputs/benchmark_convergence_step3.png")

# Trích xuất trace N=4, D=2
print("\n=== TRÍCH XUẤT TRACE NHỎ N=4, D=2 (COA VÀ RIME) ===")
# COA trace
trace_coa = []
obj_trace = CountedObjective(sphere, budget=50)
rng = np.random.default_rng(42)
bounds = [(-5.12, 5.12)] * 2
X = np.array([[-3.0, 4.0], [2.0, -1.0], [-1.0, -2.0], [3.0, 1.0]], dtype=float)
fitness = np.array([obj_trace(x) for x in X])
best_idx = np.argmin(fitness)
best_x = np.copy(X[best_idx])
best_f = fitness[best_idx]

temp = 32.5  # temp > 30 -> summer resort
for i in range(4):
    fe_b = obj_trace.fe
    fit_b = fitness[i]
    if rng.uniform(0.0, 1.0) < 0.5:
        op = "summer_resort"
        X[i] = X[i] + 1.5 * rng.uniform(0.0, 1.0, 2) * (best_x - X[i])
    else:
        op = "competition"
        z = rng.integers(0, 4)
        X[i] = X[i] - X[z] + best_x
    X[i] = np.clip(X[i], -5.12, 5.12)
    fit_a = obj_trace(X[i])
    fe_a = obj_trace.fe
    if fit_a < fitness[i]:
        fitness[i] = fit_a
        if fit_a < best_f:
            best_f = fit_a
            best_x = np.copy(X[i])
    trace_coa.append({
        "individual": i, "operator": op, "temp": temp,
        "fe_before": fe_b, "fe_after": fe_a,
        "fitness_before": round(fit_b, 4), "fitness_after": round(fit_a, 4),
        "best_so_far": round(best_f, 4)
    })

print("Trace COA (N=4, D=2):")
print(pd.DataFrame(trace_coa).to_string(index=False))

# RIME trace
trace_rime = []
obj_trace_r = CountedObjective(sphere, budget=50)
rng_r = np.random.default_rng(42)
Rime = np.array([[-3.0, 4.0], [2.0, -1.0], [-1.0, -2.0], [3.0, 1.0]], dtype=float)
fitness_r = np.array([obj_trace_r(x) for x in Rime])
best_idx_r = np.argmin(fitness_r)
best_x_r = np.copy(Rime[best_idx_r])
best_f_r = fitness_r[best_idx_r]

R_val = -0.45 * np.cos(np.pi / 20.0)
E_val = np.sqrt(1.0 / 10.0)
new_Rime = np.copy(Rime)
# soft rime
for i in range(4):
    fe_b = obj_trace_r.fe
    fit_b = fitness_r[i]
    op = "soft_rime_search"
    for j in range(2):
        if rng_r.uniform(0.0, 1.0) < E_val:
            new_Rime[i, j] = best_x_r[j] + R_val * (rng_r.uniform(0.0, 1.0) * 10.24 - 5.12)
    new_Rime[i] = np.clip(new_Rime[i], -5.12, 5.12)
    fit_a = obj_trace_r(new_Rime[i])
    fe_a = obj_trace_r.fe
    if fit_a < fitness_r[i]:
        fitness_r[i] = fit_a
        Rime[i] = np.copy(new_Rime[i])
        if fit_a < best_f_r:
            best_f_r = fit_a
            best_x_r = np.copy(new_Rime[i])
    trace_rime.append({
        "individual": i, "operator": op, "prob_E": round(E_val, 4),
        "fe_before": fe_b, "fe_after": fe_a,
        "fitness_before": round(fit_b, 4), "fitness_after": round(fit_a, 4),
        "best_so_far": round(best_f_r, 4)
    })

print("\nTrace RIME (N=4, D=2):")
print(pd.DataFrame(trace_rime).to_string(index=False))

with open("outputs/step3_trace_results.json", "w", encoding="utf-8") as f:
    json.dump({"coa_trace": trace_coa, "rime_trace": trace_rime}, f, indent=2)
