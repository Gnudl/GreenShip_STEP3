# -*- coding: utf-8 -*-
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
