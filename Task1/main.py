

if __name__ == "__main__" and (__package__ is None or __package__ == ""):
    import os
    import sys
    _pkg_dir = os.path.dirname(os.path.abspath(__file__))
    _parent = os.path.dirname(_pkg_dir)
    if _parent not in sys.path:
        sys.path.insert(0, _parent)
    __package__ = os.path.basename(_pkg_dir)

from .puzzle_state import PuzzleState
from .problem import PuzzleProblem
from .strategies import solve_puzzle_problem
from .visual_search_tree import (
    generate_search_tree_dot_astar,
    render_search_tree_png,
)


def run_demo() -> None:
    initial = PuzzleState.from_list([
        7, 8, 6,
        1, 3, 4,
        5, 0, 2,
    ])

    problem = PuzzleProblem(initial)
    actions, cost = solve_puzzle_problem(problem)

    if actions is not None:
        print(f"Độ dài lời giải: {len(actions)} bước")
        print(f"Path cost (g): {cost}\n")

        # Reconstruct and print states along the action path for readability
        cur = initial
        print("Trạng thái ban đầu:")
        for i in range(0, 9, 3):
            print(cur.to_list()[i:i+3])
        print("---")

        for a in actions:
            # find successor matching action label
            next_candidates = cur.successors_with_actions()
            matched = [s for (s, act) in next_candidates if act == a]
            if not matched:
                # Should not happen; break gracefully
                break
            cur = matched[0]
            for i in range(0, 9, 3):
                print(cur.to_list()[i:i+3])
            print(f"(Action: {a})")
            print("---")
    else:
        print("Không tìm thấy lời giải.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Puzzle demo & tree visualize")
    parser.add_argument("--tree", type=int, default=0, help="Xuất DOT cây tìm kiếm với n nút")
    parser.add_argument("--include-special", action="store_true", help="Bao gồm nước đi đặc biệt (A9, Diag)")
    parser.add_argument("--png", action="store_true", help="Render PNG sau khi tạo DOT")
    parser.add_argument("--png-out", type=str, default="search_tree.png", help="Đường dẫn file PNG output")
    args = parser.parse_args()

    if args.tree > 0:
        initial = PuzzleState.from_list([
            7, 8, 6,
            1, 3, 4,
            5, 0, 2,
        ])
        # Generate DOT for A*-order search tree (replaces previous BFS DOT)
        dot_str = generate_search_tree_dot_astar(initial, args.tree, include_special=args.include_special)
        out = "search_tree.dot"
        with open(out, "w", encoding="utf-8") as f:
            f.write(dot_str)
        print(f"Đã ghi DOT cây tìm kiếm vào: {out}")
        print("Dùng Graphviz để render, ví dụ:")
        print("dot -Tpng search_tree.dot -o search_tree.png")

        if args.png:
            png_out = args.png_out
            try:
                render_search_tree_png(initial, n=args.tree, out_png=png_out, include_special=args.include_special)
                print(f"Đã render PNG: {png_out}")
            except Exception as e:
                print("Không thể render PNG tự động:", e)
                print("Bạn có thể thử thủ công: dot -Tpng", out, "-o", png_out)
    else:
        run_demo()
