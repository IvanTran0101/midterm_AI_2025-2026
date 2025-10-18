from __future__ import annotations

from typing import Tuple, List

from .puzzle_state import PuzzleState
from .heuristics import Heuristics
from .problem import PuzzleProblem
from .search import a_star_search


def puzzle_heuristic(state: PuzzleState, problem: PuzzleProblem) -> int:
    # Reuse existing h2; ignore problem parameter for compatibility.
    return Heuristics.misplaced_div2(state)


def solve_puzzle_problem(problem: PuzzleProblem) -> Tuple[List[str] | None, int]:
    return a_star_search(problem, puzzle_heuristic)

