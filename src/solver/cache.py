from typing import Dict, Tuple
from src.models.state import State
from src.models.resource_pack import ResourcePack

class StateCache:
    """
    State cache tracking evaluated configurations to prune dominated branches.
    Adheres to Command-Query Separation (CQS) by naming state changes explicitly.
    """
    def __init__(self):
        # Maps robot counts at a specific time remaining to the best resource counts found so far.
        self.visited: Dict[Tuple[int, ResourcePack], ResourcePack] = {}

    def check_and_update_dominance(self, state: State, capped: ResourcePack) -> bool:
        """
        Checks if the current state is dominated by a previously visited state.
        If it is not dominated, but dominates/improves on the cache, it updates the cache.
        Returns True if the current state is dominated (should prune), False otherwise.
        """
        state_key = (state.time, state.robots)

        if state_key in self.visited:
            prev = self.visited[state_key]
            # Dominance rule check
            if (
                capped.ore <= prev.ore
                and capped.clay <= prev.clay
                and capped.obsidian <= prev.obsidian
                and capped.geode <= prev.geode
                and state.resources.diamond <= prev.diamond
            ):
                return True
            
            # Update cache if current state dominates the previous one
            if (
                capped.ore >= prev.ore
                and capped.clay >= prev.clay
                and capped.obsidian >= prev.obsidian
                and capped.geode >= prev.geode
                and state.resources.diamond >= prev.diamond
            ):
                self.visited[state_key] = ResourcePack(
                    ore=capped.ore,
                    clay=capped.clay,
                    obsidian=capped.obsidian,
                    geode=capped.geode,
                    diamond=state.resources.diamond
                )
        else:
            # First visit to this robot configuration at this time limit
            self.visited[state_key] = ResourcePack(
                ore=capped.ore,
                clay=capped.clay,
                obsidian=capped.obsidian,
                geode=capped.geode,
                diamond=state.resources.diamond
            )
        return False
