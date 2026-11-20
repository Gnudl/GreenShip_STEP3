import pytest
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
