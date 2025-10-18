from __future__ import annotations

from collections import deque
from typing import List, Tuple

from .puzzle_state import PuzzleState


def _state_label(s: PuzzleState) -> str:
    t = [str(x) if x != 0 else "_" for x in s.to_list()]
    return f"{t[0]}{t[1]}{t[2]}\n{t[3]}{t[4]}{t[5]}\n{t[6]}{t[7]}{t[8]}"


def generate_search_tree_dot(
    initial: PuzzleState,
    n: int,
    include_special: bool = False,
) -> str:
    """
    Build a Graphviz DOT string illustrating the search tree rooted at
    `initial`, expanding nodes in BFS order until reaching `n` nodes.

    - `include_special=False` keeps only slide moves (L,R,U,D) to mimic the
      usual 8-puzzle tree like in the prompt image. Set True to also include
      A9 and Diag moves defined in this project.
    """
    if n <= 0:
        raise ValueError("n must be >= 1")

    # BFS frontier over a pure tree (no dedup for repeated states)
    node_ids: List[str] = []
    node_labels: List[str] = []
    edges: List[Tuple[str, str, str]] = []  # (src_id, dst_id, action)

    make_id = lambda i: f"n{i}"
    q = deque([(initial, None, None)])  # (state, parent_id, action_from_parent)
    created = 0

    while q and created < n:
        state, parent_id, parent_action = q.popleft()

        cur_id = make_id(created)
        node_ids.append(cur_id)
        node_labels.append(_state_label(state))
        if parent_id is not None and parent_action is not None:
            edges.append((parent_id, cur_id, parent_action))

        created += 1
        if created >= n:
            break

        # Enqueue children (search tree => always create fresh nodes)
        for child, action in state.successors_with_actions(include_special=include_special):
            q.append((child, cur_id, action))

    lines: List[str] = []
    lines.append("digraph SearchTree {")
    lines.append("  node [shape=ellipse, fontsize=12];")
    for nid, lbl in zip(node_ids, node_labels):
        safe_lbl = lbl.replace("\n", "\\n")
        lines.append(f'  {nid} [label="{safe_lbl}"];')
    for src, dst, act in edges:
        lines.append(f'  {src} -> {dst} [label="{act}"];')
    lines.append("}")

    return "\n".join(lines)


def write_search_tree_dot(
    initial: PuzzleState,
    n: int,
    out_path: str = "search_tree.dot",
    include_special: bool = False,
) -> str:
    """Convenience helper to write DOT to a file and return the path."""
    dot = generate_search_tree_dot(initial, n, include_special=include_special)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(dot)
    return out_path

