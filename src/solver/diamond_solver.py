from src.models.blueprint import Blueprint
from src.models.state import State
from src.solver.cache import StateCache

class DiamondSolver:
    def __init__(self, blueprint: Blueprint, max_time: int):
        self.blueprint = blueprint
        self.max_time = max_time
        self.cache = StateCache()
        self.max_diamonds = 0

    def solve(self) -> int:
        return self._search(State.initial(self.max_time))

    def _search(self, state: State) -> int:
        if state.is_hopeless(self.max_diamonds):
            return 0
        if state.time == 0:
            self.max_diamonds = max(self.max_diamonds, state.diamonds)
            return state.diamonds

        capped = state.get_capped_resources(self.blueprint)
        if self.cache.is_dominated(state, capped):
            return 0

        can_build_diamond = (
            state.geode >= self.blueprint.diamond_robot_geode
            and state.clay >= self.blueprint.diamond_robot_clay
            and state.obsidian >= self.blueprint.diamond_robot_obsidian
        )
        if can_build_diamond and not state.skipped[0]:
            cost = (0, self.blueprint.diamond_robot_clay, self.blueprint.diamond_robot_obsidian, self.blueprint.diamond_robot_geode)
            return self._search(state.next_state((0, 0, 0, 0, 1), cost))

        return self._explore_other_choices(state, can_build_diamond)

    def _explore_other_choices(self, state: State, can_build_diamond: bool) -> int:
        can_geode = state.geode_robots < self.blueprint.max_geode_cost and state.ore >= self.blueprint.geode_robot_ore and state.obsidian >= self.blueprint.geode_robot_obsidian
        can_obsidian = state.obsidian_robots < self.blueprint.max_obsidian_cost and state.ore >= self.blueprint.obsidian_robot_ore and state.clay >= self.blueprint.obsidian_robot_clay
        can_clay = state.clay_robots < self.blueprint.max_clay_cost and state.ore >= self.blueprint.clay_robot_ore
        can_ore = state.ore_robots < self.blueprint.max_ore_cost and state.ore >= self.blueprint.ore_robot_ore

        best = 0
        if can_geode and not state.skipped[1]:
            cost = (self.blueprint.geode_robot_ore, 0, self.blueprint.geode_robot_obsidian, 0)
            best = max(best, self._search(state.next_state((0, 0, 0, 1, 0), cost)))
        if can_obsidian and not state.skipped[2]:
            cost = (self.blueprint.obsidian_robot_ore, self.blueprint.obsidian_robot_clay, 0, 0)
            best = max(best, self._search(state.next_state((0, 0, 1, 0, 0), cost)))
        if can_clay and not state.skipped[3]:
            cost = (self.blueprint.clay_robot_ore, 0, 0, 0)
            best = max(best, self._search(state.next_state((0, 1, 0, 0, 0), cost)))
        if can_ore and not state.skipped[4]:
            cost = (self.blueprint.ore_robot_ore, 0, 0, 0)
            best = max(best, self._search(state.next_state((1, 0, 0, 0, 0), cost)))

        none_state = state.next_state(
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0),
            (can_build_diamond, can_geode, can_obsidian, can_clay, can_ore)
        )
        return max(best, self._search(none_state))
