from typing import List
from src.models.blueprint import Blueprint
from src.solver.diamond_solver import DiamondSolver

class GameRunner:
    @staticmethod
    def solve_part_one(blueprints: List[Blueprint]) -> int:
        return sum(bp.id * DiamondSolver(bp, 24).solve() for bp in blueprints)

    @staticmethod
    def solve_part_two(blueprints: List[Blueprint]) -> int:
        product = 1
        for bp in blueprints[:3]:
            product *= DiamondSolver(bp, 32).solve()
        return product
