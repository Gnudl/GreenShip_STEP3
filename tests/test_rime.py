import pytest
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
