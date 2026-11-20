import os
from pathlib import Path

step3_dir = Path(r"C:\Users\Admin\OneDrive\Desktop\Bao_Cao_NCKH\step3")

# ==============================================================================
# 1. src/optimizers/common.py
# ==============================================================================
common_py = '''# -*- coding: utf-8 -*-
"""
Common Optimization Interface and FE Counter for STEP 3.
Guarantees fair, deterministic, and identical budget evaluation.
"""

from typing import Callable, List, Tuple, Any
import numpy as np

class CountedObjective:
    """Wraps an objective function to strictly count each Function Evaluation (FE)."""
    def __init__(self, fn: Callable[[np.ndarray], float], budget: int = 3000):
        self.fn = fn
        self.budget = budget
        self.fe = 0
        self.history_fe = []
        self.history_best = []
        self.best_f = float("inf")
        self.best_x = None

    def __call__(self, x: np.ndarray) -> float:
        if self.fe >= self.budget:
            return self.best_f
        self.fe += 1
        val = float(self.fn(x))
        if val < self.best_f:
            self.best_f = val
            self.best_x = np.copy(x)
        self.history_fe.append(self.fe)
        self.history_best.append(self.best_f)
        return val

def check_bounds(x: np.ndarray, bounds: List[Tuple[float, float]]) -> np.ndarray:
    """Clips solution vector strictly inside [lb, ub]."""
    lb = np.array([b[0] for b in bounds], dtype=float)
    ub = np.array([b[1] for b in bounds], dtype=float)
    return np.clip(x, lb, ub)
'''
(step3_dir / "src" / "optimizers" / "common.py").write_text(common_py, encoding="utf-8")
(step3_dir / "src" / "optimizers" / "__init__.py").write_text('from .common import CountedObjective, check_bounds\n', encoding="utf-8")

# ==============================================================================
# 2. src/optimizers/coa.py
# ==============================================================================
coa_py = '''# -*- coding: utf-8 -*-
"""
Crayfish Optimization Algorithm (COA) - Original Implementation.
Reference:
Jia, H., Rao, H., Wen, C., & Mirjalili, S. (2023).
Crayfish optimization algorithm: a new bio-inspired metaheuristic algorithm for solving engineering problems.
Artificial Intelligence Review, 56(Suppl 2), 1919-1979. DOI: 10.1007/s10462-023-10567-4
"""

from typing import List, Tuple
import numpy as np
from .common import CountedObjective, check_bounds

def summer_resort(X_i: np.ndarray, X_cave: np.ndarray, C1: float, rng: np.random.Generator) -> np.ndarray:
    """Summer resort stage: crayfish moves towards cave shelter (Eq. 4)."""
    dim = len(X_i)
    return X_i + C1 * rng.uniform(0.0, 1.0, dim) * (X_cave - X_i)

def competition(X_i: np.ndarray, X_z: np.ndarray, X_cave: np.ndarray) -> np.ndarray:
    """Competition stage: crayfish competes with individual z for cave (Eq. 5)."""
    return X_i - X_z + X_cave

def foraging(X_i: np.ndarray, X_food: np.ndarray, C1: float, Q: float, rng: np.random.Generator) -> np.ndarray:
    """Foraging stage: small food direct approach or large food tearing (Eq. 8, 11, 12)."""
    dim = len(X_i)
    if Q <= 2.0:
        p = C1 * (rng.uniform(0.0, 1.0, dim) - 0.5)
        return X_i + C1 * rng.uniform(0.0, 1.0, dim) * (X_food - X_i) + p
    else:
        angle = rng.uniform(0.0, 2.0 * np.pi)
        X_torn = np.exp(-1.0 / Q) * X_food
        return X_i + X_torn * (np.cos(angle) - np.sin(angle))

def optimize_coa(objective: CountedObjective, bounds: List[Tuple[float, float]], 
                 population_size: int = 20, max_fe: int = 3000, seed: int = 0):
    """
    Standard optimization interface for COA.
    Returns: (best_solution, best_fitness, history_fe, history_best)
    """
    rng = np.random.default_rng(seed)
    dim = len(bounds)
    lb = np.array([b[0] for b in bounds], dtype=float)
    ub = np.array([b[1] for b in bounds], dtype=float)

    # 1. Initialization
    X = lb + rng.uniform(0.0, 1.0, (population_size, dim)) * (ub - lb)
    fitness = np.zeros(population_size)
    for i in range(population_size):
        if objective.fe >= max_fe:
            break
        fitness[i] = objective(X[i])

    best_idx = np.argmin(fitness)
    best_solution = np.copy(X[best_idx])
    best_fitness = fitness[best_idx]

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
                if rng.uniform(0.0, 1.0) < 0.5:
                    X_cand = summer_resort(X[i], X_cave, C1, rng)
                else:
                    z = rng.integers(0, population_size)
                    X_cand = competition(X[i], X[z], X_cave)
            else:
                Q = rng.uniform(0.5, 2.5)
                X_cand = foraging(X[i], X_food, C1, Q, rng)

            X_cand = check_bounds(X_cand, bounds)
            f_new = objective(X_cand)
            if f_new < fitness[i]:
                fitness[i] = f_new
                X[i] = np.copy(X_cand)
                if f_new < best_fitness:
                    best_fitness = f_new
                    best_solution = np.copy(X_cand)

    return best_solution, best_fitness, objective.history_fe, objective.history_best
'''
(step3_dir / "src" / "optimizers" / "coa.py").write_text(coa_py, encoding="utf-8")

# ==============================================================================
# 3. src/optimizers/rime.py
# ==============================================================================
rime_py = '''# -*- coding: utf-8 -*-
"""
RIME Optimization Algorithm - Original Implementation.
Reference:
Su, H., Zhao, D., Heidari, A. A., Liu, L., Zhang, X., Mafarja, M., & Chen, H. (2023).
RIME: A physics-based optimization algorithm.
Neurocomputing, 532, 183-214. DOI: 10.1016/j.neucom.2023.02.010
"""

from typing import List, Tuple
import numpy as np
from .common import CountedObjective, check_bounds

def soft_rime_search(Rime: np.ndarray, best_solution: np.ndarray, E: float, R: float, 
                     lb: np.ndarray, ub: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Soft-rime search strategy: condensation with wind disturbance (Eq. 3, 4, 5)."""
    pop_size, dim = Rime.shape
    new_Rime = np.copy(Rime)
    for i in range(pop_size):
        for j in range(dim):
            if rng.uniform(0.0, 1.0) < E:
                new_Rime[i, j] = best_solution[j] + R * (rng.uniform(0.0, 1.0) * (ub[j] - lb[j]) + lb[j])
    return new_Rime

def hard_rime_puncture(new_Rime: np.ndarray, best_solution: np.ndarray, 
                       fitness: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Hard-rime puncture mechanism: crossover replacement (Eq. 7, 8)."""
    pop_size, dim = new_Rime.shape
    f_min, f_max = np.min(fitness), np.max(fitness)
    denom = f_max - f_min + 1e-12
    fit_norm = (fitness - f_min) / denom
    for i in range(pop_size):
        for j in range(dim):
            if rng.uniform(0.0, 1.0) < fit_norm[i]:
                new_Rime[i, j] = best_solution[j]
    return new_Rime

def optimize_rime(objective: CountedObjective, bounds: List[Tuple[float, float]], 
                  population_size: int = 20, max_fe: int = 3000, seed: int = 0):
    """
    Standard optimization interface for RIME.
    Returns: (best_solution, best_fitness, history_fe, history_best)
    """
    rng = np.random.default_rng(seed)
    dim = len(bounds)
    lb = np.array([b[0] for b in bounds], dtype=float)
    ub = np.array([b[1] for b in bounds], dtype=float)

    # 1. Initialization
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
        R = rng.uniform(-1.0, 1.0) * np.cos((np.pi * t) / (2.0 * max_iter))
        E = np.sqrt(min(1.0, (t + 1.0) / max_iter))
        
        # Soft-rime search
        new_Rime = soft_rime_search(Rime, best_solution, E, R, lb, ub, rng)
        # Hard-rime puncture
        new_Rime = hard_rime_puncture(new_Rime, best_solution, fitness, rng)

        # Positive-greedy selection
        for i in range(population_size):
            if objective.fe >= max_fe:
                break
            cand = check_bounds(new_Rime[i], bounds)
            f_new = objective(cand)
            if f_new < fitness[i]:
                fitness[i] = f_new
                Rime[i] = np.copy(cand)
                if f_new < best_fitness:
                    best_fitness = f_new
                    best_solution = np.copy(cand)

    return best_solution, best_fitness, objective.history_fe, objective.history_best
'''
(step3_dir / "src" / "optimizers" / "rime.py").write_text(rime_py, encoding="utf-8")

# ==============================================================================
# 4. benchmarks/functions.py
# ==============================================================================
benchmarks_py = '''# -*- coding: utf-8 -*-
"""
Standard Benchmark Suite for STEP 3 (Sphere, Rastrigin, Rosenbrock).
"""

from typing import Dict, Any
import numpy as np

def sphere(x: np.ndarray) -> float:
    """F1: Sphere function, Global min = 0 at [0, ..., 0]."""
    x = np.asarray(x, dtype=float)
    return float(np.sum(x**2))

def rastrigin(x: np.ndarray) -> float:
    """F4: Rastrigin function, Global min = 0 at [0, ..., 0]."""
    x = np.asarray(x, dtype=float)
    return float(10.0 * len(x) + np.sum(x**2 - 10.0 * np.cos(2.0 * np.pi * x)))

def rosenbrock(x: np.ndarray) -> float:
    """F3: Rosenbrock function, Global min = 0 at [1, ..., 1]."""
    x = np.asarray(x, dtype=float)
    return float(np.sum(100.0 * (x[1:] - x[:-1]**2)**2 + (x[:-1] - 1.0)**2))

def get_benchmark_suite(dim: int = 10) -> Dict[str, Dict[str, Any]]:
    """Returns standardized suite specification."""
    return {
        "Sphere": {
            "fn": sphere,
            "bounds": [(-5.12, 5.12)] * dim,
            "optimum_x": np.zeros(dim),
            "optimum_f": 0.0,
            "type": "Unimodal, separable"
        },
        "Rastrigin": {
            "fn": rastrigin,
            "bounds": [(-5.12, 5.12)] * dim,
            "optimum_x": np.zeros(dim),
            "optimum_f": 0.0,
            "type": "Multimodal, separable"
        },
        "Rosenbrock": {
            "fn": rosenbrock,
            "bounds": [(-2.048, 2.048)] * dim,
            "optimum_x": np.ones(dim),
            "optimum_f": 0.0,
            "type": "Narrow valley, non-separable"
        }
    }
'''
(step3_dir / "benchmarks" / "functions.py").write_text(benchmarks_py, encoding="utf-8")
(step3_dir / "benchmarks" / "__init__.py").write_text('from .functions import sphere, rastrigin, rosenbrock, get_benchmark_suite\n', encoding="utf-8")

# ==============================================================================
# 5. scripts/run_benchmarks.py
# ==============================================================================
run_bench_py = '''# -*- coding: utf-8 -*-
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
'''
(step3_dir / "scripts" / "run_benchmarks.py").write_text(run_bench_py, encoding="utf-8")

# ==============================================================================
# 6. tests/test_benchmarks.py
# ==============================================================================
test_bench_py = '''import pytest
import numpy as np
from benchmarks.functions import sphere, rastrigin, rosenbrock, get_benchmark_suite

def test_sphere_properties():
    # Global minimum is 0 at origin
    assert sphere(np.zeros(10)) == 0.0
    assert sphere(np.ones(10)) == 10.0
    assert sphere(np.array([2.0, -2.0])) == 8.0
    assert sphere(np.random.uniform(-5, 5, 10)) >= 0.0

def test_rastrigin_properties():
    # Global minimum is 0 at origin
    assert rastrigin(np.zeros(10)) == 0.0
    assert rastrigin(np.random.uniform(-5.12, 5.12, 10)) >= 0.0

def test_rosenbrock_properties():
    # Global minimum is 0 at [1, ..., 1]
    assert rosenbrock(np.ones(10)) == 0.0
    # At origin, f(0) = D - 1 = 9 for D=10
    assert rosenbrock(np.zeros(10)) == 9.0

def test_benchmark_suite_structure():
    suite = get_benchmark_suite(dim=10)
    assert len(suite) == 3
    for name, item in suite.items():
        assert len(item["bounds"]) == 10
        assert item["optimum_f"] == 0.0
'''
(step3_dir / "tests" / "test_benchmarks.py").write_text(test_bench_py, encoding="utf-8")

# ==============================================================================
# 7. tests/test_coa.py
# ==============================================================================
test_coa_py = '''import pytest
import numpy as np
from src.optimizers.common import CountedObjective
from src.optimizers.coa import optimize_coa, summer_resort, competition, foraging
from benchmarks.functions import sphere

def test_coa_budget_exactness():
    obj = CountedObjective(sphere, budget=300)
    bounds = [(-5.12, 5.12)] * 10
    bx, bf, fe_h, best_h = optimize_coa(obj, bounds, population_size=10, max_fe=300, seed=42)
    assert obj.fe == 300
    assert len(bx) == 10
    assert all(-5.12 <= x <= 5.12 for x in bx)
    assert bf <= best_h[0]

def test_coa_operators_bounds():
    rng = np.random.default_rng(42)
    x = np.array([2.0, -3.0])
    cave = np.array([0.0, 0.0])
    # summer resort moves towards cave
    x_shelter = summer_resort(x, cave, C1=1.0, rng=rng)
    assert len(x_shelter) == 2

    # competition with z
    z = np.array([-1.0, 1.0])
    x_comp = competition(x, z, cave)
    assert len(x_comp) == 2

    # foraging small and large
    x_small = foraging(x, cave, C1=1.0, Q=1.5, rng=rng)
    x_large = foraging(x, cave, C1=1.0, Q=2.2, rng=rng)
    assert len(x_small) == 2
    assert len(x_large) == 2

def test_coa_determinism():
    bounds = [(-5.12, 5.12)] * 5
    obj1 = CountedObjective(sphere, budget=100)
    bx1, bf1, _, _ = optimize_coa(obj1, bounds, population_size=10, max_fe=100, seed=123)
    obj2 = CountedObjective(sphere, budget=100)
    bx2, bf2, _, _ = optimize_coa(obj2, bounds, population_size=10, max_fe=100, seed=123)
    assert bf1 == bf2
    np.testing.assert_array_equal(bx1, bx2)
'''
(step3_dir / "tests" / "test_coa.py").write_text(test_coa_py, encoding="utf-8")

# ==============================================================================
# 8. tests/test_rime.py
# ==============================================================================
test_rime_py = '''import pytest
import numpy as np
from src.optimizers.common import CountedObjective
from src.optimizers.rime import optimize_rime, soft_rime_search, hard_rime_puncture
from benchmarks.functions import sphere

def test_rime_budget_exactness():
    obj = CountedObjective(sphere, budget=300)
    bounds = [(-5.12, 5.12)] * 10
    bx, bf, fe_h, best_h = optimize_rime(obj, bounds, population_size=10, max_fe=300, seed=42)
    assert obj.fe == 300
    assert len(bx) == 10
    assert all(-5.12 <= x <= 5.12 for x in bx)
    assert bf <= best_h[0]

def test_rime_operators():
    rng = np.random.default_rng(42)
    Rime = np.array([[2.0, -3.0], [1.0, 1.0]])
    best = np.array([0.0, 0.0])
    lb = np.array([-5.12, -5.12])
    ub = np.array([5.12, 5.12])
    
    soft = soft_rime_search(Rime, best, E=0.5, R=0.2, lb=lb, ub=ub, rng=rng)
    assert soft.shape == (2, 2)
    
    fitness = np.array([13.0, 2.0])
    hard = hard_rime_puncture(soft, best, fitness, rng=rng)
    assert hard.shape == (2, 2)

def test_rime_determinism():
    bounds = [(-5.12, 5.12)] * 5
    obj1 = CountedObjective(sphere, budget=100)
    bx1, bf1, _, _ = optimize_rime(obj1, bounds, population_size=10, max_fe=100, seed=123)
    obj2 = CountedObjective(sphere, budget=100)
    bx2, bf2, _, _ = optimize_rime(obj2, bounds, population_size=10, max_fe=100, seed=123)
    assert bf1 == bf2
    np.testing.assert_array_equal(bx1, bx2)
'''
(step3_dir / "tests" / "test_rime.py").write_text(test_rime_py, encoding="utf-8")

# ==============================================================================
# 9. tests/test_step2_regression.py
# ==============================================================================
test_regr_py = '''import pytest
import json
import yaml
from pathlib import Path
import pandas as pd
from src.evaluator import doc_tham_so_tau, lay_gia_tri_tham_so, evaluate_route, MatNaDatLien, TEP_SHAPEFILE
from src.weather import KhoDuLieuThoiTiet
from src.route_geometry import doc_cac_tuyen

def test_power_positive_validation():
    # Power = 0 must raise ValueError in engine-driven vessel mode
    ship_zero = {
        "parameters": {
            "speed_through_water_kn": {"value": 12.0, "unit": "kn"},
            "service_power_kw": {"value": 0.0, "unit": "kW"},
            "sfoc_g_per_kwh": {"value": 190.0, "unit": "g/kWh"},
            "co2_emission_factor_t_per_t_fuel": {"value": 3.114, "unit": "tCO2/t-fuel"}
        }
    }
    with pytest.raises(ValueError):
        lay_gia_tri_tham_so(ship_zero, "service_power_kw", "kW", cho_phep_bang_khong=False)

def test_power_negative_validation():
    ship_neg = {
        "parameters": {
            "speed_through_water_kn": {"value": 12.0, "unit": "kn"},
            "service_power_kw": {"value": -1.0, "unit": "kW"},
            "sfoc_g_per_kwh": {"value": 190.0, "unit": "g/kWh"},
            "co2_emission_factor_t_per_t_fuel": {"value": 3.114, "unit": "tCO2/t-fuel"}
        }
    }
    with pytest.raises(ValueError):
        lay_gia_tri_tham_so(ship_neg, "service_power_kw", "kW", cho_phep_bang_khong=False)

def test_eta_coverage_buffer():
    # ETA of R01 must precede mandatory dataset coverage
    routes = doc_cac_tuyen()
    r01 = next(r for r in routes if r["route_id"] == "R01")
    cfg = yaml.safe_load(open("config/scenario.yaml", "r", encoding="utf-8"))
    ship = json.load(open("config/ship.json", "r", encoding="utf-8"))
    land = MatNaDatLien.doc_tu_shapefile(TEP_SHAPEFILE)
    weather = KhoDuLieuThoiTiet()
    
    res = evaluate_route(r01, cfg["departure_utc"], ship, weather, land, cfg)
    eta = pd.Timestamp(cfg["departure_utc"]) + pd.Timedelta(hours=res["duration_h"])
    mandatory_end = pd.Timestamp("2024-10-14T23:00:00Z")
    assert eta < mandatory_end
    # Buffer is >= 50 hours
    assert (mandatory_end - eta).total_seconds() / 3600.0 >= 50.0
'''
(step3_dir / "tests" / "test_step2_regression.py").write_text(test_regr_py, encoding="utf-8")
(step3_dir / "tests" / "__init__.py").write_text('', encoding="utf-8")

# ==============================================================================
# 10. README.md & requirements.txt
# ==============================================================================
readme_md = '''# GREENSHIP STEP 3: BỔ SUNG STEP 2 VÀ TÁI HIỆN ĐỘC LẬP COA – RIME

Đề tài Nghiên cứu Khoa học Sinh viên: **Tối ưu lộ trình hàng hải xanh thích ứng thời tiết sử dụng thuật toán lai Crayfish–RIME**  
Nhóm thực hiện: **Hải Thần** (Đặng Long Ngũ, Nguyễn Trần Như Nguyệt, Nguyễn Phương Thùy)  
Phiên bản: 19/11/2026 (Tag: `step3-benchmarks`, Commit: `4f7e2a9`)

---

## 1. Cấu trúc thư mục chuẩn
```text
step3/
├── config/                      # Kịch bản bài toán WGS84 và thông số tàu toy model
│   ├── scenario.yaml
│   └── ship.json
├── data/                        # Dữ liệu thật lưu riêng biệt (độc lập)
│   ├── processed/               # Dữ liệu NetCDF gió (wind.nc), sóng (waves.nc), dòng chảy (currents.nc)
│   ├── land/                    # Đa giác đất liền Natural Earth Land 5.1.1 (1:10m)
│   ├── routes/                  # 3 tuyến thủ công mẫu R01, R02, R03
│   └── source_register.csv      # Danh mục 4 nguồn dữ liệu khí tượng hải dương
├── src/                         # Mã nguồn cốt lõi
│   ├── evaluator.py             # Hàm evaluate_route() cố định từ STEP 2 (bổ sung power > 0, check ETA)
│   ├── weather.py               # Tra cứu thời tiết weather_at()
│   ├── route_geometry.py        # Hình học trắc địa WGS84 geodesic và kiểm tra cắt đất
│   ├── constraints.py           # Phân loại ràng buộc hard/soft
│   └── optimizers/              # Triển khai thuật toán tối ưu hóa độc lập
│       ├── common.py            # Lớp CountedObjective và giao diện optimize chuẩn
│       ├── coa.py               # Thuật toán Crayfish Optimization Algorithm (Jia et al., 2023)
│       └── rime.py              # Thuật toán RIME (Su et al., 2023)
├── benchmarks/                  # Bộ hàm benchmark chuẩn (D=10)
│   └── functions.py             # Sphere (F1), Rastrigin (F4), Rosenbrock (F3)
├── scripts/                     # Kịch bản thực thi tự động
│   └── run_benchmarks.py        # Chạy ma trận 3 hàm x 2 thuật toán x 10 seeds (N=20, max_fe=3000)
├── tests/                       # Bộ kiểm thử tự động pytest
│   ├── test_benchmarks.py       # Kiểm thử tính đúng của 3 hàm benchmark tại nghiệm chuẩn
│   ├── test_coa.py              # Unit test các toán tử COA
│   ├── test_rime.py             # Unit test các toán tử RIME
│   └── test_step2_regression.py # Kiểm thử hồi quy STEP 2 (power=0, ETA buffer)
├── outputs/                     # Kết quả thực nghiệm và minh chứng
│   ├── benchmark_results_step3.csv
│   ├── benchmark_convergence_step3.png
│   ├── Ban_do_ba_tuyen_Hs.png
│   ├── step3_part_a_results.json
│   └── step3_trace_results.json
└── reports/                     # Báo cáo Word hoàn chỉnh
    ├── STEP3_Bao_cao_Nhom_Hai_Than_Da_dien.docx
    ├── STEP3_Huong_dan_va_hoan_thien_STEP2_Nhom_Hai_Than.docx
    └── STEP3_Mau_bao_cao_tu_dien_Nhom_Hai_Than (1).docx
```

---

## 2. Hướng dẫn chạy và tái lập thực nghiệm

1. **Cài đặt môi trường:**
   ```powershell
   python -m pip install -r requirements.txt
   ```

2. **Chạy kiểm thử tự động (Pytest):**
   ```powershell
   pytest tests/ -v
   ```

3. **Chạy ma trận benchmark và sinh đồ thị hội tụ:**
   ```powershell
   python scripts/run_benchmarks.py
   ```
'''
(step3_dir / "README.md").write_text(readme_md, encoding="utf-8")

reqs_txt = '''numpy>=1.26.0
pandas>=2.2.0
xarray>=2024.1.0
scipy>=1.12.0
matplotlib>=3.8.0
python-docx>=1.2.0
pyyaml>=6.0
pytest>=8.0.0
netCDF4>=1.6.5
'''
(step3_dir / "requirements.txt").write_text(reqs_txt, encoding="utf-8")

print("Created all source code, benchmark, test, script, and documentation files successfully!")
