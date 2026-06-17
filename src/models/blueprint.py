import re
from src.models.resource_pack import ResourcePack

class Blueprint:
    """
    Blueprint defining costs to build each type of robot.
    Uses ResourcePack values internally for structural cohesion.
    Keeps legacy attributes as properties to maintain backward compatibility.
    """
    __slots__ = ("id", "ore_robot_cost", "clay_robot_cost", "obsidian_robot_cost", "geode_robot_cost", "diamond_robot_cost")

    def __init__(
        self,
        id: int,
        ore_robot_ore: int,
        clay_robot_ore: int,
        obsidian_robot_ore: int,
        obsidian_robot_clay: int,
        geode_robot_ore: int,
        geode_robot_obsidian: int,
        diamond_robot_geode: int,
        diamond_robot_clay: int,
        diamond_robot_obsidian: int,
    ):
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "ore_robot_cost", ResourcePack(ore=ore_robot_ore))
        object.__setattr__(self, "clay_robot_cost", ResourcePack(ore=clay_robot_ore))
        object.__setattr__(self, "obsidian_robot_cost", ResourcePack(ore=obsidian_robot_ore, clay=obsidian_robot_clay))
        object.__setattr__(self, "geode_robot_cost", ResourcePack(ore=geode_robot_ore, obsidian=geode_robot_obsidian))
        object.__setattr__(self, "diamond_robot_cost", ResourcePack(geode=diamond_robot_geode, clay=diamond_robot_clay, obsidian=diamond_robot_obsidian))

    @property
    def max_ore_cost(self) -> int:
        return max(
            self.ore_robot_cost.ore,
            self.clay_robot_cost.ore,
            self.obsidian_robot_cost.ore,
            self.geode_robot_cost.ore
        )

    @property
    def max_clay_cost(self) -> int:
        return max(self.obsidian_robot_cost.clay, self.diamond_robot_cost.clay)

    @property
    def max_obsidian_cost(self) -> int:
        return max(self.geode_robot_cost.obsidian, self.diamond_robot_cost.obsidian)

    @property
    def max_geode_cost(self) -> int:
        return self.diamond_robot_cost.geode

    # Backward compatibility properties for unit tests / API endpoints
    @property
    def ore_robot_ore(self) -> int: return self.ore_robot_cost.ore
    @property
    def clay_robot_ore(self) -> int: return self.clay_robot_cost.ore
    @property
    def obsidian_robot_ore(self) -> int: return self.obsidian_robot_cost.ore
    @property
    def obsidian_robot_clay(self) -> int: return self.obsidian_robot_cost.clay
    @property
    def geode_robot_ore(self) -> int: return self.geode_robot_cost.ore
    @property
    def geode_robot_obsidian(self) -> int: return self.geode_robot_cost.obsidian
    @property
    def diamond_robot_geode(self) -> int: return self.diamond_robot_cost.geode
    @property
    def diamond_robot_clay(self) -> int: return self.diamond_robot_cost.clay
    @property
    def diamond_robot_obsidian(self) -> int: return self.diamond_robot_cost.obsidian

    @staticmethod
    def parse(line: str) -> 'Blueprint':
        numbers = list(map(int, re.findall(r"\d+", line)))
        if len(numbers) != 10:
            raise ValueError(f"Expected 10 integers for a Blueprint, but got {len(numbers)}.")
        return Blueprint(*numbers)
