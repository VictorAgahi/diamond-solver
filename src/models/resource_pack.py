from typing import NamedTuple

class ResourcePack(NamedTuple):
    """
    Value Object representing resources or robots counts.
    Prevents primitive obsession and simplifies operations.
    """
    ore: int = 0
    clay: int = 0
    obsidian: int = 0
    geode: int = 0
    diamond: int = 0

    def add(self, other: 'ResourcePack') -> 'ResourcePack':
        return ResourcePack(
            ore=self.ore + other.ore,
            clay=self.clay + other.clay,
            obsidian=self.obsidian + other.obsidian,
            geode=self.geode + other.geode,
            diamond=self.diamond + other.diamond
        )

    def subtract(self, other: 'ResourcePack') -> 'ResourcePack':
        return ResourcePack(
            ore=self.ore - other.ore,
            clay=self.clay - other.clay,
            obsidian=self.obsidian - other.obsidian,
            geode=self.geode - other.geode,
            diamond=self.diamond - other.diamond
        )
