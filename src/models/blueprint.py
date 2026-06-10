import re
from dataclasses import dataclass

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
        if len(numbers) != 10:
            raise ValueError(f"Expected 10 integers for a Blueprint, but got {len(numbers)}.")
        return Blueprint(*numbers)
