import pytest
from csp import *

@pytest.mark.benchmark
def test_csp_solver_performance(benchmark):
    """Benchmark the CSP solver execution time."""
    
    print("Benchmark test running...\n")
    
    my_univ = generateUniv2()
    print("Univ generated successfully : ", my_univ)
    print("Generating the CSP (NO OUTPUT TEST ONLY)...")
    result = benchmark(lambda: CSP(my_univ, True))

    # Ensure a solution is returned (not None)
    assert result is not None