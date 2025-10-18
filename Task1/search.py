"""
Generic A* search adapted from Task2/search.py so Task 1 can reuse
the same algorithm and interface without conflicts.

API expectations for `problem`:
- problem.get_initial_state() -> state
- problem.is_goal(state) -> bool
- problem.get_successors(state, current_g_cost) -> List[Tuple[action, next_state]]

Heuristic signature: heuristic(state, problem) -> int
"""

from __future__ import annotations

import heapq
import time
from typing import Any, Tuple


class Node:
    def __init__(self, state: Any, parent: "Node | None", action: str | None, g_cost: int) -> None:
        self.state = state
        self.parent = parent
        self.action = action
        self.g_cost = g_cost

    def __lt__(self, other: "Node") -> bool:
        return self.g_cost < other.g_cost


def a_star_search(problem, heuristic):
    print("Starting A* search...")
    start_time = time.time()

    initial_state = problem.get_initial_state()
    start_node = Node(initial_state, parent=None, action=None, g_cost=0)

    frontier: list[Tuple[int, int, Node]] = []
    tie_breaker = 0
    f_cost = start_node.g_cost + heuristic(start_node.state, problem)
    heapq.heappush(frontier, (f_cost, tie_breaker, start_node))

    explored = set()
    best_g = {initial_state: 0}

    while frontier:
        _, _, current_node = heapq.heappop(frontier)

        if current_node.g_cost > best_g.get(current_node.state, float("inf")):
            continue

        if problem.is_goal(current_node.state):
            end_time = time.time()
            print(f"Solution found in {end_time - start_time:.4f} seconds.")
            print(f"Nodes explored: {len(explored)}")

            path: list[str] = []
            node = current_node
            while node.parent is not None:
                if node.action is not None:
                    path.append(node.action)
                node = node.parent
            path.reverse()
            return path, current_node.g_cost

        explored.add(current_node.state)

        if len(explored) % 10000 == 0:
            print(
                f"Explored {len(explored)} nodes... (Current path cost: {current_node.g_cost})"
            )

        for action, next_state in problem.get_successors(current_node.state, current_node.g_cost):
            new_g = current_node.g_cost + 1
            if new_g >= best_g.get(next_state, float("inf")):
                continue
            best_g[next_state] = new_g
            child_node = Node(next_state, current_node, action, new_g)
            f_cost = child_node.g_cost + heuristic(next_state, problem)
            tie_breaker += 1
            heapq.heappush(frontier, (f_cost, tie_breaker, child_node))

    print("No solution found.")
    return None, 0

