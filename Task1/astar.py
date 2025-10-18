from typing import Callable, Dict, List, Optional, Tuple
import heapq

from .puzzle_state import PuzzleState


class AStarSolver:
    def __init__(self, heuristic: Callable[[PuzzleState], int]) -> None:
        self.h = heuristic
        # Metrics
        self.last_path_cost: Optional[int] = None
        self.enqueue_count: int = 0
        self.pop_count: int = 0

    def solve(self, start: PuzzleState) -> Optional[List[PuzzleState]]:
        # reset metrics
        self.last_path_cost = None
        self.enqueue_count = 0
        self.pop_count = 0

        s = start.tiles
        open_heap: List[Tuple[int, int, Tuple[int, ...]]] = []  # (f, g, state)
        heapq.heappush(open_heap, (self.h(start), 0, s))
        self.enqueue_count += 1
        g_cost: Dict[Tuple[int, ...], int] = {s: 0}
        parent: Dict[Tuple[int, ...], Optional[Tuple[int, ...]]] = {s: None}

        while open_heap:
            f, g, u = heapq.heappop(open_heap)
            self.pop_count += 1
            u_state = PuzzleState(u)
            if u_state.is_goal():
                # found goal: record path cost
                self.last_path_cost = g
                # reconstruct path
                path: List[PuzzleState] = []
                cur: Optional[Tuple[int, ...]] = u
                while cur is not None:
                    path.append(PuzzleState(cur))
                    cur = parent[cur]
                return list(reversed(path))

            for v_state in PuzzleState(u).successors():
                v = v_state.tiles
                alt = g + 1
                if v not in g_cost or alt < g_cost[v]:
                    g_cost[v] = alt
                    parent[v] = u
                    heapq.heappush(open_heap, (alt + self.h(v_state), alt, v))
                    self.enqueue_count += 1
        return None

