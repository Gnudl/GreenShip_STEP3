# -*- coding: utf-8 -*-
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
