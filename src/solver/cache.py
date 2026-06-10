from typing import Tuple
from src.models.state import State

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
