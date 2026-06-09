import re
import sys
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Blueprint:
    id: int
    ore_robot_ore: int
    clay_robot_ore: int
    obsidian_robot_ore: int
    obsidian_robot_clay: int
    geode_robot_ore: int
    geode_robot_obsidian: int
    diamond_robot_geode: int
    diamond_robot_clay: int
    diamond_robot_obsidian: int

    @property
    def max_ore_cost(self) -> int:
        return max(
            self.ore_robot_ore,
            self.clay_robot_ore,
            self.obsidian_robot_ore,
            self.geode_robot_ore
        )

    @property
    def max_clay_cost(self) -> int:
        return max(self.obsidian_robot_clay, self.diamond_robot_clay)

    @property
    def max_obsidian_cost(self) -> int:
        return max(self.geode_robot_obsidian, self.diamond_robot_obsidian)

    @property
    def max_geode_cost(self) -> int:
        return self.diamond_robot_geode

    @staticmethod
    def parse(line: str) -> 'Blueprint':
        numbers = list(map(int, re.findall(r"\d+", line)))
        return Blueprint(*numbers)


@dataclass(frozen=True)
class State:
    time: int
    ore_robots: int
    clay_robots: int
    obsidian_robots: int
    geode_robots: int
    diamond_robots: int
    ore: int
    clay: int
    obsidian: int
    geode: int
    diamonds: int
    skipped: Tuple[bool, bool, bool, bool, bool]

    @staticmethod
    def initial(max_time: int) -> 'State':
        return State(
            time=max_time,
            ore_robots=1,
            clay_robots=0,
            obsidian_robots=0,
            geode_robots=0,
            diamond_robots=0,
            ore=0,
            clay=0,
            obsidian=0,
            geode=0,
            diamonds=0,
            skipped=(False, False, False, False, False),
        )

    def next_state(
        self,
        robot_diff: Tuple[int, int, int, int, int],
        cost: Tuple[int, int, int, int],
        skipped_next: Tuple[bool, bool, bool, bool, bool] = (False, False, False, False, False),
    ) -> 'State':
        c_ore, c_clay, c_obs, c_geode = cost
        return State(
            time=self.time - 1,
            ore_robots=self.ore_robots + robot_diff[0],
            clay_robots=self.clay_robots + robot_diff[1],
            obsidian_robots=self.obsidian_robots + robot_diff[2],
            geode_robots=self.geode_robots + robot_diff[3],
            diamond_robots=self.diamond_robots + robot_diff[4],
            ore=self.ore - c_ore + self.ore_robots,
            clay=self.clay - c_clay + self.clay_robots,
            obsidian=self.obsidian - c_obs + self.obsidian_robots,
            geode=self.geode - c_geode + self.geode_robots,
            diamonds=self.diamonds + self.diamond_robots,
            skipped=skipped_next
        )

    def get_capped_resources(self, blueprint: Blueprint) -> Tuple[int, int, int, int]:
        def cap(value: int, max_cost: int, robots: int) -> int:
            return min(value, max(0, max_cost * self.time - robots * (self.time - 1)))

        capped_ore = cap(self.ore, blueprint.max_ore_cost, self.ore_robots)
        capped_clay = cap(self.clay, blueprint.max_clay_cost, self.clay_robots)
        capped_obsidian = cap(self.obsidian, blueprint.max_obsidian_cost, self.obsidian_robots)
        capped_geode = cap(self.geode, blueprint.max_geode_cost, self.geode_robots)
        return capped_ore, capped_clay, capped_obsidian, capped_geode

    def is_hopeless(self, best_known_diamonds: int) -> bool:
        max_possible = self.diamonds + self.diamond_robots * self.time + self.time * (self.time - 1) // 2
        return max_possible <= best_known_diamonds


class StateCache:
    def __init__(self):
        self.visited = {}

    def is_dominated(self, state: State, capped: Tuple[int, int, int, int]) -> bool:
        capped_ore, capped_clay, capped_obsidian, capped_geode = capped
        state_key = (
            state.time,
            state.ore_robots,
            state.clay_robots,
            state.obsidian_robots,
            state.geode_robots,
            state.diamond_robots,
        )

        if state_key in self.visited:
            prev_ore, prev_clay, prev_obs, prev_geode, prev_diamonds = self.visited[state_key]
            if (
                capped_ore <= prev_ore
                and capped_clay <= prev_clay
                and capped_obsidian <= prev_obs
                and capped_geode <= prev_geode
                and state.diamonds <= prev_diamonds
            ):
                return True
            if (
                capped_ore >= prev_ore
                and capped_clay >= prev_clay
                and capped_obsidian >= prev_obs
                and capped_geode >= prev_geode
                and state.diamonds >= prev_diamonds
            ):
                self.visited[state_key] = (capped_ore, capped_clay, capped_obsidian, capped_geode, state.diamonds)
        else:
            self.visited[state_key] = (capped_ore, capped_clay, capped_obsidian, capped_geode, state.diamonds)
        return False


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


class GameRunner:
    @staticmethod
    def solve_part_one(blueprints: list[Blueprint]) -> int:
        return sum(bp.id * DiamondSolver(bp, 24).solve() for bp in blueprints)

    @staticmethod
    def solve_part_two(blueprints: list[Blueprint]) -> int:
        product = 1
        for bp in blueprints[:3]:
            product *= DiamondSolver(bp, 32).solve()
        return product


def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else "seed.txt"
    try:
        with open(filepath) as f:
            lines = f.read().strip().splitlines()
        blueprints = [Blueprint.parse(line) for line in lines if line]
        
        print(f"Part 1: {GameRunner.solve_part_one(blueprints)}")
        print(f"Part 2: {GameRunner.solve_part_two(blueprints)}")
    except FileNotFoundError:
        print(f"File {filepath} not found.")


if __name__ == "__main__":
    main()
