from dataclasses import dataclass
from typing import Tuple
from src.models.blueprint import Blueprint

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
