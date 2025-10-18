from .puzzle_state import PuzzleState
from .constants import GOAL_STATES


class Heuristics:
    @staticmethod
    def misplaced_div2(state: PuzzleState) -> int:
        # Tính số ô sai vị trí đối với từng goal, lấy min rồi chia 2.
        best_mis = min(
            sum(1 for i in range(9) if state.tiles[i] != 0 and state.tiles[i] != goal[i])
            for goal in GOAL_STATES
        )
        return best_mis // 2

    @staticmethod
    def manhattan_blank(state: PuzzleState) -> int:
        i = state.index_of(0)
        r, c = divmod(i, 3)
        best = 10
        for goal in GOAL_STATES:
            gi = goal.index(0)
            gr, gc = divmod(gi, 3)
            d = abs(r - gr) + abs(c - gc)
            if d < best:
                best = d
        return best

    @staticmethod
    def h2(state: PuzzleState) -> int:
        return min(Heuristics.misplaced_div2(state), Heuristics.manhattan_blank(state))

