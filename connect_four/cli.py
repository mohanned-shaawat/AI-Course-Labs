import time
from solver import (
    GameSolver,
    BOARD_WIDTH,
    BOARD_HIGHT,
    GAME_LENGTH,
    PLAYER1_SYMBOL,
    PLAYER2_SYMBOL,
)


MAX_DIRECT_LINES = 200
PAGE_SIZE = 30


def main():
    print("=== Connect 4: Human vs. Minimax AI (Alpha-Beta Pruning) ===")
    agent_is_first, max_depth, show_boards = get_game_settings()

    solver = GameSolver(agent_is_first=agent_is_first, max_depth=max_depth)
    user_symbol = PLAYER2_SYMBOL if agent_is_first else PLAYER1_SYMBOL

    print(f"\nGame started! Depth K = {max_depth}")
    print(f"You: {user_symbol} | AI Agent: {solver.agent_symbol}")
    print_game_status(solver)

    while not solver.is_finished():
        if solver.is_agent_turn:
            print("AI is thinking...")
            tree_root = solver.current_state

            start_time = time.perf_counter()
            move, _ = solver.agent_move()
            elapsed_time = time.perf_counter() - start_time

            print_minimax_tree(tree_root, move, show_boards=show_boards)
            print(f"AI chose column: {move}")
            print(
                f"Turn stats -> Expanded nodes: {solver.expanded_nodes} | "
                f"Total expanded: {solver.total_expanded_nodes} | "
                f"Time: {elapsed_time:.4f}s"
            )
            print_game_status(solver)
        else:
            valid_cols = solver.available_moves()
            valid_cols_list = list(valid_cols)
            while True:
                raw_move = input(f"Your turn ({user_symbol}). Choose column {valid_cols_list}: ").strip()
                if raw_move.isdigit():
                    move = int(raw_move)
                    if move in valid_cols:
                        solver.user_move(move)
                        break
                print(f"Invalid move. Please choose an available column from {valid_cols_list}.")

            print_game_status(solver)

    agent_pts = solver.agent_score()
    user_pts = solver.user_score()

    print("=" * 40)
    print("GAME OVER - BOARD IS FULL")
    print(f"Final Score -> AI ({solver.agent_symbol}): {agent_pts} | You ({user_symbol}): {user_pts}")
    if agent_pts > user_pts:
        print("Result: AI wins!")
    elif user_pts > agent_pts:
        print("Result: You win!")
    else:
        print("Result: It's a tie!")
    print("=" * 40)


def get_game_settings():
    while True:
        raw_depth = input("Enter search depth K (integer > 0): ").strip()
        if raw_depth.isdigit() and int(raw_depth) > 0:
            max_depth = int(raw_depth)
            break
        print("Invalid depth. Please enter a positive integer.")

    print("\nWho should play first?")
    print(f"  1 - You play first ({PLAYER1_SYMBOL}), AI plays second ({PLAYER2_SYMBOL})")
    print(f"  2 - AI plays first ({PLAYER1_SYMBOL}), You play second ({PLAYER2_SYMBOL})")
    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            agent_is_first = False
            break
        elif choice == "2":
            agent_is_first = True
            break
        print("Invalid choice. Please enter 1 or 2.")

    board_toggle = input("\nPrint board grids inside every tree node? (y/n) [default: n]: ").strip().lower()
    show_boards = board_toggle in ("y", "yes")

    return agent_is_first, max_depth, show_boards


def print_game_status(solver):
    user_symbol = PLAYER2_SYMBOL if solver.agent_symbol == PLAYER1_SYMBOL else PLAYER1_SYMBOL
    print_board(solver.current_state.board)
    print(
        f"Score -> You ({user_symbol}): {solver.user_score()} | "
        f"AI ({solver.agent_symbol}): {solver.agent_score()}\n"
    )

def print_board(board):
    header = "  " + "   ".join(str(col) for col in range(1, BOARD_WIDTH + 1))
    divider = "+" + "---+" * BOARD_WIDTH
    print("\n" + header)
    print(divider)
    for row in board:
        print("| " + " | ".join(row) + " |")
        print(divider)


def print_minimax_tree(root_state, chosen_move, show_boards=False):
    lines = [
        "",
        "=" * 60,
        f"MINIMAX SEARCH TREE (Chosen Move: Column {chosen_move})",
        "=" * 60,
        f"ROOT [MAX] -> Utility: {root_state.utility}",
    ]

    if show_boards:
        _build_mini_board(root_state.board, "│ ", lines)

    if root_state.next_moves:
        children = list(root_state.next_moves.items())
        for idx, (move, child_state) in enumerate(children):
            _build_subtree(
                child_state,
                "",
                idx == len(children) - 1,
                move,
                False,
                show_boards,
                lines,
            )
    lines.append("=" * 60)

    tree_text = "\n".join(lines)
    with open("last_tree.txt", "w", encoding="utf-8") as f:
        f.write(tree_text + "\n")

    if len(lines) <= MAX_DIRECT_LINES:
        print(tree_text + "\n")
    else:
        print(f"\nSearch tree has {len(lines)} lines (full tree saved to 'last_tree.txt').")
        view = input("View tree page-by-page in terminal? (y/n) [default: n]: ").strip().lower()
        if view in ("y", "yes"):
            for start in range(0, len(lines), PAGE_SIZE):
                print("\n".join(lines[start : start + PAGE_SIZE]))
                if start + PAGE_SIZE >= len(lines):
                    break
                end = min(start + PAGE_SIZE, len(lines))
                cmd = input(
                    f"-- Lines {start + 1}-{end} of {len(lines)} (Enter: next, 'q': stop) --: "
                ).strip().lower()
                print("\033[1A\033[2K\r", end="")
                if cmd == "q":
                    break
            print()


def _build_mini_board(board, prefix, lines):
    border = prefix + "+" + "-" * (BOARD_WIDTH * 2 - 1) + "+"
    lines.append(border)
    for row in board:
        lines.append(prefix + "|" + " ".join(cell if cell != " " else "." for cell in row) + "|")
    lines.append(border)
    lines.append(prefix.rstrip())


def _build_subtree(state, prefix, is_last, move, is_max, show_boards, lines):
    dash = "──────" if show_boards else "──"
    pad = "       " if show_boards else "   "
    connector = f"└{dash} " if is_last else f"├{dash} "
    child_prefix = prefix + (f" {pad}" if is_last else f"│{pad}")

    if state.pruned:
        lines.append(f"{prefix}{connector}Col {move} -> [PRUNED]")
        return

    if state.depth == GAME_LENGTH:
        node_type = "LEAF - Terminal"
    elif not state.next_moves:
        node_type = "LEAF - Heuristic"
    else:
        node_type = "MAX" if is_max else "MIN"

    lines.append(f"{prefix}{connector}Col {move} [{node_type}] -> Utility: {state.utility}")

    if show_boards:
        _build_mini_board(state.board, child_prefix, lines)

    if state.next_moves:
        children = list(state.next_moves.items())
        for idx, (child_move, child_state) in enumerate(children):
            _build_subtree(
                child_state,
                child_prefix,
                idx == len(children) - 1,
                child_move,
                not is_max,
                show_boards,
                lines,
            )



if __name__ == "__main__":
    main()