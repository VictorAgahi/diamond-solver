from typing import Optional
from src.models.blueprint import Blueprint
from src.models.state import State
from src.models.resource_pack import ResourcePack
from src.solver.cache import StateCache

class DiamondSolver:
    """
    Solves the problem of maximizing diamond production using a DFS algorithm with pruning.
    Allows cache dependency injection for better testability and SOLID adherence.
    """
    def __init__(self, blueprint: Blueprint, max_time: int, cache: Optional[StateCache] = None):
        self.blueprint = blueprint
        self.max_time = max_time
        # DIP: Injection of cache layer
        self.cache = cache if cache is not None else StateCache()
        self.max_diamonds = 0

    def solve(self) -> int:
        return self._search(State.initial(self.max_time))

    def _is_hopeless(self, state: State) -> bool:
        """Branch-and-bound optimization to check if current branch can beat the best found score."""
        max_possible = (
            state.resources.diamond 
            + state.robots.diamond * state.time 
            + state.time * (state.time - 1) // 2
        )
        return max_possible <= self.max_diamonds

    def _get_capped_resources(self, state: State) -> ResourcePack:
        """Limits resources in state representations to optimize caching search-space size."""
        def cap(value: int, max_cost: int, robots: int) -> int:
            return min(value, max(0, max_cost * state.time - robots * (state.time - 1)))

        bp = self.blueprint
        return ResourcePack(
            ore=cap(state.resources.ore, bp.max_ore_cost, state.robots.ore),
            clay=cap(state.resources.clay, bp.max_clay_cost, state.robots.clay),
            obsidian=cap(state.resources.obsidian, bp.max_obsidian_cost, state.robots.obsidian),
            geode=cap(state.resources.geode, bp.max_geode_cost, state.robots.geode),
        )

    def _search(self, state: State) -> int:
        if self._is_hopeless(state):
            return 0
        if state.time == 0:
            self.max_diamonds = max(self.max_diamonds, state.resources.diamond)
            return state.resources.diamond

        capped = self._get_capped_resources(state)
        if self.cache.check_and_update_dominance(state, capped):
            return 0

        # Optimization: Prioritize building diamond robots
        can_build_diamond = (
            state.resources.geode >= self.blueprint.diamond_robot_cost.geode
            and state.resources.clay >= self.blueprint.diamond_robot_cost.clay
            and state.resources.obsidian >= self.blueprint.diamond_robot_cost.obsidian
        )
        if can_build_diamond and not state.skipped[0]:
            return self._search(
                state.next_state(
                    robot_diff=ResourcePack(diamond=1),
                    cost=self.blueprint.diamond_robot_cost
                )
            )

        return self._explore_other_choices(state, can_build_diamond)

    def _explore_other_choices(self, state: State, can_build_diamond: bool) -> int:
        bp = self.blueprint
        res = state.resources
        rob = state.robots

        can_geode = rob.geode < bp.max_geode_cost and res.ore >= bp.geode_robot_cost.ore and res.obsidian >= bp.geode_robot_cost.obsidian
        can_obsidian = rob.obsidian < bp.max_obsidian_cost and res.ore >= bp.obsidian_robot_cost.ore and res.clay >= bp.obsidian_robot_cost.clay
        can_clay = rob.clay < bp.max_clay_cost and res.ore >= bp.clay_robot_cost.ore
        can_ore = rob.ore < bp.max_ore_cost and res.ore >= bp.ore_robot_cost.ore

        best = 0
        if can_geode and not state.skipped[1]:
            best = max(best, self._search(state.next_state(ResourcePack(geode=1), bp.geode_robot_cost)))
        if can_obsidian and not state.skipped[2]:
            best = max(best, self._search(state.next_state(ResourcePack(obsidian=1), bp.obsidian_robot_cost)))
        if can_clay and not state.skipped[3]:
            best = max(best, self._search(state.next_state(ResourcePack(clay=1), bp.clay_robot_cost)))
        if can_ore and not state.skipped[4]:
            best = max(best, self._search(state.next_state(ResourcePack(ore=1), bp.ore_robot_cost)))

        none_state = state.next_state(
            robot_diff=ResourcePack(),
            cost=ResourcePack(),
            skipped_next=(can_build_diamond, can_geode, can_obsidian, can_clay, can_ore)
        )
        return max(best, self._search(none_state))
