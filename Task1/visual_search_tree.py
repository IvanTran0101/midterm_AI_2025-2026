from __future__ import annotations

# Allow running this file directly without package context
if __name__ == "__main__" and (__package__ is None or __package__ == ""):
    import os as _os, sys as _sys
    _pkg_dir = _os.path.dirname(_os.path.abspath(__file__))
    _parent = _os.path.dirname(_pkg_dir)
    if _parent not in _sys.path:
        _sys.path.insert(0, _parent)
    __package__ = _os.path.basename(_pkg_dir)

import heapq
import random
from typing import Callable, Dict, Optional, Tuple, List
import os
import shutil
import subprocess

try:
    from graphviz import Digraph  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Digraph = None  # type: ignore

from .puzzle_state import PuzzleState
from .heuristics import Heuristics


def _state_label(s: PuzzleState) -> str:
    t = [str(x) if x != 0 else "_" for x in s.to_list()]
    return f"{t[0]} {t[1]} {t[2]}\n{t[3]} {t[4]} {t[5]}\n{t[6]} {t[7]} {t[8]}"


def illustrate_search_tree_astar(
    initial: PuzzleState,
    n: int = 20,
    heuristic: Optional[Callable[[PuzzleState], int]] = None,
    include_special: bool = True,
):
    """
    Vẽ cây tìm kiếm theo thứ tự mở rộng của A* (tối đa n nút).

    - initial: trạng thái bắt đầu.
    - n: số nút tối đa để vẽ.
    - heuristic: hàm h(state)->int. Mặc định dùng Heuristics.h2.
    - include_special: có bao gồm nước đi đặc biệt (A9, Diag) khi sinh kế tiếp.

    Trả về đối tượng graphviz.Digraph hoặc None nếu graphviz chưa cài.
    """
    if Digraph is None:
        print("Graphviz (python-graphviz) chưa được cài. Hãy cài: pip install graphviz")
        return None

    if n <= 0:
        raise ValueError("n phải >= 1")

    h = heuristic if heuristic is not None else Heuristics.h2

    dot = Digraph(comment=f"A* Search Tree (first {n} nodes)")
    dot.attr("node", shape="box", fontname="Courier New")
    dot.attr("edge", fontname="Helvetica", fontsize="10")
    dot.attr(rankdir="TB")

    # Frontier tuples: (f, tie_breaker, g, state, parent_state, action)
    frontier: list[Tuple[int, int, int, PuzzleState, Optional[PuzzleState], Optional[str]]] = []
    tie = 0
    start_g = 0
    start_f = start_g + h(initial)
    heapq.heappush(frontier, (start_f, tie, start_g, initial, None, None))

    best_g: Dict[PuzzleState, int] = {initial: 0}
    assigned_id: Dict[PuzzleState, str] = {}
    drawn: Dict[PuzzleState, bool] = {}
    created = 0

    def _id_for(state: PuzzleState) -> str:
        if state not in assigned_id:
            assigned_id[state] = f"n{len(assigned_id)}"
        return assigned_id[state]

    while frontier and created < n:
        f, _, g, state, parent_state, action = heapq.heappop(frontier)

        if g > best_g.get(state, float("inf")):
            continue

        cur_id = _id_for(state)
        if not drawn.get(state, False):
            node_color = "blue" if state.is_goal() else ("green" if parent_state is None else "black")
            dot.node(cur_id, _state_label(state), color=node_color, fontcolor=node_color)
            if parent_state is not None and action is not None:
                dot.edge(_id_for(parent_state), cur_id, label=action)
            drawn[state] = True
            created += 1
            if created >= n:
                break

        for child, act in state.successors_with_actions(include_special=include_special):
            new_g = g + 1
            if new_g >= best_g.get(child, float("inf")):
                continue
            best_g[child] = new_g
            tie += 1
            new_f = new_g + h(child)
            heapq.heappush(frontier, (new_f, tie, new_g, child, state, act))

    if created == 0:
        print("Không thể vẽ được nút bắt đầu.")
        return None

    return dot


def generate_random_state_for_viz(n_shuffles: int = 10, include_special: bool = True) -> PuzzleState:
    """Sinh trạng thái ngẫu nhiên bằng cách xáo trộn từ goal bằng các nước đi hợp lệ."""
    state = PuzzleState.from_list([1, 2, 3, 4, 5, 6, 7, 8, 0])
    for _ in range(max(0, n_shuffles)):
        succ = state.successors_with_actions(include_special=include_special)
        if not succ:
            break
        state = random.choice(succ)[0]
    return state


def generate_search_tree_dot_astar(
    initial: PuzzleState,
    n: int,
    heuristic: Optional[Callable[[PuzzleState], int]] = None,
    include_special: bool = True,
) -> str:
    """Sinh chuỗi DOT thể hiện cây mở rộng theo A* (không cần python-graphviz)."""
    if n <= 0:
        raise ValueError("n phải >= 1")

    h = heuristic if heuristic is not None else Heuristics.h2

    frontier: list[Tuple[int, int, int, PuzzleState, Optional[PuzzleState], Optional[str]]] = []
    tie = 0
    start_g = 0
    start_f = start_g + h(initial)
    heapq.heappush(frontier, (start_f, tie, start_g, initial, None, None))

    best_g: Dict[PuzzleState, int] = {initial: 0}
    assigned_id: Dict[PuzzleState, str] = {}
    drawn: Dict[PuzzleState, bool] = {}
    created = 0

    nodes: List[Tuple[str, str, str]] = []  # (id, label, color)
    edges: List[Tuple[str, str, str]] = []  # (src_id, dst_id, action)

    def _id_for(state: PuzzleState) -> str:
        if state not in assigned_id:
            assigned_id[state] = f"n{len(assigned_id)}"
        return assigned_id[state]

    while frontier and created < n:
        f, _, g, state, parent_state, action = heapq.heappop(frontier)
        if g > best_g.get(state, float("inf")):
            continue

        cur_id = _id_for(state)
        if not drawn.get(state, False):
            color = "blue" if state.is_goal() else ("green" if parent_state is None else "black")
            label = _state_label(state).replace("\n", "\\n")
            nodes.append((cur_id, label, color))
            if parent_state is not None and action is not None:
                edges.append((_id_for(parent_state), cur_id, action))
            drawn[state] = True
            created += 1
            if created >= n:
                break

        for child, act in state.successors_with_actions(include_special=include_special):
            new_g = g + 1
            if new_g >= best_g.get(child, float("inf")):
                continue
            best_g[child] = new_g
            tie += 1
            new_f = new_g + h(child)
            heapq.heappush(frontier, (new_f, tie, new_g, child, state, act))

    lines: List[str] = []
    lines.append("digraph SearchTreeAStar {")
    lines.append("  node [shape=box, fontname=\"Courier New\"];\n  edge [fontname=\"Helvetica\", fontsize=10];")
    for nid, lbl, color in nodes:
        lines.append(f'  {nid} [label="{lbl}", color="{color}", fontcolor="{color}"];')
    for src, dst, act in edges:
        lines.append(f'  {src} -> {dst} [label="{act}"];')
    lines.append("}")
    return "\n".join(lines)


def render_search_tree_png(
    initial: PuzzleState,
    n: int,
    out_png: str = "search_tree.png",
    heuristic: Optional[Callable[[PuzzleState], int]] = None,
    include_special: bool = True,
) -> str:
    """Convenience wrapper: render trực tiếp PNG.

    - Ưu tiên dùng python-graphviz nếu có.
    - Nếu không có, fallback sang lệnh `dot` CLI.
    Trả về đường dẫn file PNG đã tạo.
    """
    def _stem(p: str) -> str:
        return p[:-4] if p.lower().endswith(".png") else p

    stem = _stem(out_png)

    if Digraph is not None:
        g = illustrate_search_tree_astar(initial, n=n, heuristic=heuristic, include_special=include_special)
        if g is None:
            raise RuntimeError("Không thể khởi tạo graphviz Digraph.")
        g.render(stem, format="png", cleanup=True)
        return out_png

    dot_path = stem + ".dot"
    dot_str = generate_search_tree_dot_astar(initial, n=n, heuristic=heuristic, include_special=include_special)
    with open(dot_path, "w", encoding="utf-8") as f:
        f.write(dot_str)

    if shutil.which("dot") is None:
        raise RuntimeError("Không tìm thấy 'dot' trong PATH. Hãy cài Graphviz CLI hoặc python-graphviz.")

    subprocess.run(["dot", "-Tpng", dot_path, "-o", out_png], check=True)
    try:
        os.remove(dot_path)
    except Exception:
        pass
    return out_png


if __name__ == "__main__":
    # Minimal self-test to write DOT
    init = generate_random_state_for_viz(n_shuffles=5)
    dot = generate_search_tree_dot_astar(init, n=20)
    with open("search_tree_astar.dot", "w", encoding="utf-8") as f:
        f.write(dot)
    print("Đã ghi DOT A* vào: search_tree_astar.dot")
