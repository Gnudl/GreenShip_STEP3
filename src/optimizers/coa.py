# -*- coding: utf-8 -*-
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
