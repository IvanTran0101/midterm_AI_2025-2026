from __future__ import annotations

from typing import List, Tuple

from .puzzle_state import PuzzleState


class PuzzleProblem:
    """A thin Problem wrapper so Task 1 can reuse the same A* API
    as Task 2. All moves have unit cost.
    """

    def __init__(self, initial: PuzzleState) -> None:
        self._initial = initial

    # A* API
    def get_initial_state(self) -> PuzzleState:
        return self._initial

    def is_goal(self, state: PuzzleState) -> bool:
        return state.is_goal()

    def get_successors(
        self, current_state: PuzzleState, current_g_cost: int
    ) -> List[Tuple[str, PuzzleState]]:
        # Ignore current_g_cost since costs are uniform.
        # Reorder as (action, next_state) to match the shared A*.
        return [(action, s) for (s, action) in current_state.successors_with_actions()]

