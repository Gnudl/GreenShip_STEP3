import pytest
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
