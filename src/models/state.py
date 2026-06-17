from typing import NamedTuple, Tuple
from src.models.resource_pack import ResourcePack

class State(NamedTuple):
    """
    Represents the state of search at any given minute.
    Uses ResourcePack to represent robots and resources type-safely.
    """
    time: int
    robots: ResourcePack
    resources: ResourcePack
    skipped: Tuple[bool, bool, bool, bool, bool]  # skipped building: (diamond, geode, obsidian, clay, ore)

    @staticmethod
    def initial(max_time: int) -> 'State':
        return State(
            time=max_time,
            robots=ResourcePack(ore=1),
            resources=ResourcePack(),
            skipped=(False, False, False, False, False),
        )

    def next_state(
        self,
        robot_diff: ResourcePack,
        cost: ResourcePack,
        skipped_next: Tuple[bool, bool, bool, bool, bool] = (False, False, False, False, False),
    ) -> 'State':
        """Transitions to the next minute's state, performing resource collection and consumption."""
        return State(
            time=self.time - 1,
            robots=self.robots.add(robot_diff),
            resources=self.resources.subtract(cost).add(self.robots),
            skipped=skipped_next
        )
