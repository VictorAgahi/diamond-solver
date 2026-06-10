from src.models.blueprint import Blueprint
from src.solver.diamond_solver import DiamondSolver

def test_diamond_solver_small_run():
    # Provide a simple blueprint
    bp = Blueprint(1, 4, 2, 3, 14, 2, 7, 1, 5, 3)
    # Give it a very small time to avoid long test execution times
    solver = DiamondSolver(bp, max_time=10)
    result = solver.solve()
    assert isinstance(result, int)
    assert result >= 0
