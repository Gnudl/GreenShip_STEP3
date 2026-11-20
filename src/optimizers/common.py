# -*- coding: utf-8 -*-
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
