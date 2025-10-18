from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .constants import GOAL_STATES


@dataclass(frozen=True)
class PuzzleState:
    """Trạng thái 3x3 bất biến, lưu dưới dạng tuple 9 phần tử.
    Cung cấp các phép sinh trạng thái kế tiếp (slide blank, Adj9Swap, CornerDiag).
    """

    tiles: Tuple[int, ...]

    @staticmethod
    def from_list(values: List[int]) -> "PuzzleState":
        if len(values) != 9:
            raise ValueError("PuzzleState requires exactly 9 values")
        return PuzzleState(tuple(values))

    def to_list(self) -> List[int]:
        return list(self.tiles)

    def is_goal(self) -> bool:
        t = list(self.tiles)
        return any(t == g for g in GOAL_STATES)

    def index_of(self, value: int) -> int:
        return self.tiles.index(value)

    def _swap(self, i: int, j: int) -> "PuzzleState":
        t = list(self.tiles)
        t[i], t[j] = t[j], t[i]
        return PuzzleState(tuple(t))

    def successors_with_actions(self, include_special: bool = True) -> List[Tuple["PuzzleState", str]]:
        succ: List[Tuple[PuzzleState, str]] = []

        # 1) Slide blank (0)
        b = self.index_of(0)
        r, c = divmod(b, 3)
        dir_map = {(1, 0): "D", (-1, 0): "U", (0, 1): "R", (0, -1): "L"}
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                j = nr * 3 + nc
                succ.append((self._swap(b, j), dir_map[(dr, dc)]))

        if include_special:
            # 2) Adj9Swap (cặp kề ngang/dọc, tổng = 9, không chứa blank)
            def try_swap(i: int, j: int) -> None:
                a, b = self.tiles[i], self.tiles[j]
                if a != 0 and b != 0 and (a + b == 9):
                    succ.append((self._swap(i, j), "A9"))

            # Ngang
            for rr in range(3):
                i, j, k = rr * 3 + 0, rr * 3 + 1, rr * 3 + 2
                try_swap(i, j)
                try_swap(j, k)
            # Dọc
            for cc in range(3):
                i, j, k = 0 * 3 + cc, 1 * 3 + cc, 2 * 3 + cc
                try_swap(i, j)
                try_swap(j, k)

            # 3) CornerDiagSwap (đổi chéo 2 góc, bỏ qua nếu dính blank)
            for (r1, c1), (r2, c2) in [((0, 0), (2, 2)), ((0, 2), (2, 0))]:
                i, j = r1 * 3 + c1, r2 * 3 + c2
                if self.tiles[i] != 0 and self.tiles[j] != 0:
                    succ.append((self._swap(i, j), "Diag"))

        return succ

    def successors(self) -> List["PuzzleState"]:
        return [s for s, _ in self.successors_with_actions(include_special=True)]

    def __str__(self) -> str:
        rows = [self.tiles[i:i+3] for i in range(0, 9, 3)]
        return "\n".join(str(list(r)) for r in rows)

