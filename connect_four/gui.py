import time
import tkinter as tk
from tkinter import ttk, messagebox
from solver import (
    GameSolver,
    BOARD_WIDTH,
    BOARD_HIGHT,
    GAME_LENGTH,
    PLAYER1_SYMBOL,
    PLAYER2_SYMBOL,
    EMPTY_SYMBOL,
)

# Color Palette
BG_MAIN = "#0f172a"
BG_PANEL = "#1e293b"
BG_CARD = "#334155"
TEXT_PRIMARY = "#f8fafc"
TEXT_MUTED = "#94a3b8"
ACCENT_BLUE = "#3b82f6"
BOARD_BLUE = "#1d4ed8"
BOARD_BORDER = "#1e40af"
SLOT_EMPTY = "#0f172a"
P1_COLOR = "#ef4444"       # Red for X
P1_HOVER = "#fca5a5"
P2_COLOR = "#facc15"       # Yellow for O
P2_HOVER = "#fef08a"
HIGHLIGHT_RING = "#22c55e"


class Connect4GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4 — Minimax AI with Alpha-Beta Pruning")
        self.root.configure(bg=BG_MAIN)
        self.root.minsize(1060, 680)

        self.solver = None
        self.user_symbol = PLAYER1_SYMBOL
        self.ai_thinking = False
        self.hover_col = None
        self.last_move_rc = None
        self.game_session_id = 0
        self.tree_node_states = {}

        # Geometry constants for main board
        self.cell_size = 72
        self.top_margin = 54
        self.board_pad = 12

        # Geometry constants for mini preview board
        self.mini_cell = 26
        self.mini_pad = 6

        self._configure_styles()
        self._build_layout()
        self.start_new_game()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=BG_MAIN,
            foreground=TEXT_PRIMARY,
            fieldbackground=BG_MAIN,
            borderwidth=0,
            font=("Consolas", 10),
            rowheight=24,
        )
        style.configure(
            "Treeview.Heading",
            background=BG_CARD,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map("Treeview", background=[("selected", ACCENT_BLUE)])

    def _build_layout(self):
        # --- Top Control Bar ---
        top_bar = tk.Frame(self.root, bg=BG_PANEL, pady=10, padx=16)
        top_bar.pack(fill=tk.X)

        tk.Label(
            top_bar,
            text="CONNECT 4 AI",
            bg=BG_PANEL,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 14, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 24))

        tk.Label(
            top_bar,
            text="Search Depth (K):",
            bg=BG_PANEL,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 10),
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.depth_var = tk.StringVar(value="3")
        self.depth_spin = tk.Spinbox(
            top_bar,
            from_=1,
            to=12,
            width=4,
            textvariable=self.depth_var,
            font=("Segoe UI", 10, "bold"),
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            buttonbackground=BG_CARD,
            insertbackground=TEXT_PRIMARY,
            relief="flat",
        )
        self.depth_spin.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            top_bar,
            text="First Turn:",
            bg=BG_PANEL,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 10),
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.first_player_var = tk.StringVar(value="human")
        tk.Radiobutton(
            top_bar,
            text=f"You ({PLAYER1_SYMBOL})",
            variable=self.first_player_var,
            value="human",
            bg=BG_PANEL,
            fg=TEXT_PRIMARY,
            selectcolor=BG_CARD,
            activebackground=BG_PANEL,
            activeforeground=TEXT_PRIMARY,
            font=("Segoe UI", 10),
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Radiobutton(
            top_bar,
            text=f"AI ({PLAYER1_SYMBOL})",
            variable=self.first_player_var,
            value="ai",
            bg=BG_PANEL,
            fg=TEXT_PRIMARY,
            selectcolor=BG_CARD,
            activebackground=BG_PANEL,
            activeforeground=TEXT_PRIMARY,
            font=("Segoe UI", 10),
        ).pack(side=tk.LEFT, padx=(0, 20))

        self.new_game_btn = tk.Button(
            top_bar,
            text="New Game",
            command=self.start_new_game,
            bg=ACCENT_BLUE,
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=4,
            relief="flat",
            cursor="hand2",
        )
        self.new_game_btn.pack(side=tk.LEFT)

        # --- Main Content Area ---
        content = tk.Frame(self.root, bg=BG_MAIN, padx=16, pady=14)
        content.pack(fill=tk.BOTH, expand=True)

        # Left Panel: Game Board & Scoreboard
        left_panel = tk.Frame(content, bg=BG_PANEL, padx=16, pady=14)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))

        self.status_label = tk.Label(
            left_panel,
            text="Your Turn",
            bg=BG_PANEL,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 13, "bold"),
        )
        self.status_label.pack(pady=(0, 8))

        # Scoreboard Row
        score_frame = tk.Frame(left_panel, bg=BG_CARD, padx=12, pady=8)
        score_frame.pack(fill=tk.X, pady=(0, 12))

        self.user_score_label = tk.Label(
            score_frame,
            text="You (X): 0",
            bg=BG_CARD,
            fg=P1_COLOR,
            font=("Segoe UI", 11, "bold"),
        )
        self.user_score_label.pack(side=tk.LEFT, padx=(4, 16))

        self.moves_label = tk.Label(
            score_frame,
            text="Moves: 0/42",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Segoe UI", 10),
        )
        self.moves_label.pack(side=tk.LEFT, expand=True)

        self.ai_score_label = tk.Label(
            score_frame,
            text="AI (O): 0",
            bg=BG_CARD,
            fg=P2_COLOR,
            font=("Segoe UI", 11, "bold"),
        )
        self.ai_score_label.pack(side=tk.RIGHT, padx=(16, 4))

        # Main Board Canvas
        canvas_w = BOARD_WIDTH * self.cell_size + 2 * self.board_pad
        canvas_h = BOARD_HIGHT * self.cell_size + self.top_margin + self.board_pad
        self.board_canvas = tk.Canvas(
            left_panel,
            width=canvas_w,
            height=canvas_h,
            bg=BG_PANEL,
            highlightthickness=0,
            cursor="hand2",
        )
        self.board_canvas.pack()
        self.board_canvas.bind("<Motion>", self._on_board_hover)
        self.board_canvas.bind("<Leave>", self._on_board_leave)
        self.board_canvas.bind("<Button-1>", self._on_board_click)

        # Right Panel: Minimax Search Tree & Node Board Inspector
        right_panel = tk.Frame(content, bg=BG_PANEL, padx=14, pady=14)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(
            right_panel,
            text="Minimax Search Tree (Last AI Turn)",
            bg=BG_PANEL,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        ).pack(fill=tk.X)

        self.telemetry_label = tk.Label(
            right_panel,
            text="Chosen Col: — | Expanded: 0 | Total Expanded: 0 | Time: 0.0000s",
            bg=BG_PANEL,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
            anchor="w",
        )
        self.telemetry_label.pack(fill=tk.X, pady=(2, 8))

        # Treeview + Scrollbars
        tree_container = tk.Frame(right_panel, bg=BG_MAIN)
        tree_container.pack(fill=tk.BOTH, expand=True)

        tree_scroll_y = ttk.Scrollbar(tree_container, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(
            tree_container,
            columns=("role", "utility"),
            show="tree headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
        )
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        self.tree.heading("#0", text="Branch / Move", anchor="w")
        self.tree.heading("role", text="Node Type", anchor="center")
        self.tree.heading("utility", text="Utility", anchor="center")

        self.tree.column("#0", width=210, minwidth=150)
        self.tree.column("role", width=130, minwidth=100, anchor="center")
        self.tree.column("utility", width=90, minwidth=70, anchor="center")

        self.tree.tag_configure("chosen", foreground="#4ade80", font=("Consolas", 10, "bold"))
        self.tree.tag_configure("pruned", foreground="#64748b")
        self.tree.tag_configure("leaf", foreground="#38bdf8")
        self.tree.tag_configure("max_node", foreground=TEXT_PRIMARY)
        self.tree.tag_configure("min_node", foreground="#e2e8f0")

        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_node_select)

        # Bottom of Right Panel: Selected Tree Node Mini-Board Preview
        inspector_frame = tk.Frame(right_panel, bg=BG_CARD, padx=10, pady=8)
        inspector_frame.pack(fill=tk.X, pady=(10, 0))

        mini_w = BOARD_WIDTH * self.mini_cell + 2 * self.mini_pad
        mini_h = BOARD_HIGHT * self.mini_cell + 2 * self.mini_pad
        self.mini_canvas = tk.Canvas(
            inspector_frame,
            width=mini_w,
            height=mini_h,
            bg=BOARD_BLUE,
            highlightthickness=0,
        )
        self.mini_canvas.pack(side=tk.LEFT, padx=(0, 12))

        info_box = tk.Frame(inspector_frame, bg=BG_CARD)
        info_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            info_box,
            text="Tree Node Board Inspector",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill=tk.X)

        self.inspector_detail = tk.Label(
            info_box,
            text="Click any node in the tree above to inspect its board state.",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
            justify=tk.LEFT,
            anchor="nw",
            wraplength=240,
        )
        self.inspector_detail.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    def start_new_game(self):
        raw_k = self.depth_var.get().strip()
        if not raw_k.isdigit() or int(raw_k) <= 0:
            messagebox.showerror("Invalid Depth", "Search depth K must be a positive integer (> 0).")
            return

        max_depth = int(raw_k)
        agent_is_first = self.first_player_var.get() == "ai"

        self.game_session_id += 1
        self.ai_thinking = False
        self.hover_col = None
        self.last_move_rc = None

        self.solver = GameSolver(agent_is_first=agent_is_first, max_depth=max_depth)
        self.user_symbol = PLAYER2_SYMBOL if agent_is_first else PLAYER1_SYMBOL

        self.tree.delete(*self.tree.get_children())
        self.tree_node_states.clear()
        self.telemetry_label.config(
            text=f"Depth K = {max_depth} | Waiting for AI turn..."
        )
        self._draw_mini_board(self.solver.current_state.board)
        self.inspector_detail.config(text="Click any node in the tree above to inspect its board state.")

        self._refresh_board_and_scores()

        if self.solver.is_agent_turn:
            self._schedule_ai_turn()

    def _symbol_color(self, symbol, hover=False):
        if symbol == PLAYER1_SYMBOL:
            return P1_HOVER if hover else P1_COLOR
        if symbol == PLAYER2_SYMBOL:
            return P2_HOVER if hover else P2_COLOR
        return SLOT_EMPTY

    def _refresh_board_and_scores(self):
        user_pts = self.solver.user_score()
        ai_pts = self.solver.agent_score()
        user_col = self._symbol_color(self.user_symbol)
        ai_col = self._symbol_color(self.solver.agent_symbol)

        self.user_score_label.config(text=f"You ({self.user_symbol}): {user_pts}", fg=user_col)
        self.ai_score_label.config(text=f"AI ({self.solver.agent_symbol}): {ai_pts}", fg=ai_col)
        self.moves_label.config(text=f"Moves: {self.solver.current_state.depth}/{GAME_LENGTH}")

        if self.solver.is_finished():
            if ai_pts > user_pts:
                self.status_label.config(text=f"Game Over — AI Wins ({ai_pts} to {user_pts})!", fg=ai_col)
            elif user_pts > ai_pts:
                self.status_label.config(text=f"Game Over — You Win ({user_pts} to {ai_pts})!", fg=user_col)
            else:
                self.status_label.config(text=f"Game Over — It's a Tie ({user_pts} to {ai_pts})!", fg=TEXT_PRIMARY)
        elif self.ai_thinking:
            self.status_label.config(text=f"AI ({self.solver.agent_symbol}) is thinking...", fg=ai_col)
        else:
            self.status_label.config(text=f"Your Turn ({self.user_symbol})", fg=user_col)

        self._draw_main_board()

    def _draw_main_board(self):
        self.board_canvas.delete("all")
        board = self.solver.current_state.board
        valid_cols = set(self.solver.available_moves())

        # Draw column numbers & hover preview disc in the top margin
        for c in range(BOARD_WIDTH):
            col_num = c + 1
            cx = self.board_pad + c * self.cell_size + self.cell_size / 2
            cy = self.top_margin / 2

            if (
                not self.ai_thinking
                and not self.solver.is_finished()
                and self.hover_col == col_num
                and col_num in valid_cols
            ):
                r = self.cell_size * 0.34
                self.board_canvas.create_oval(
                    cx - r,
                    cy - r,
                    cx + r,
                    cy + r,
                    fill=self._symbol_color(self.user_symbol, hover=True),
                    outline="",
                )
            else:
                self.board_canvas.create_text(
                    cx,
                    cy,
                    text=str(col_num),
                    fill=TEXT_MUTED if col_num in valid_cols else "#475569",
                    font=("Segoe UI", 11, "bold"),
                )

        # Blue board frame
        x0 = self.board_pad
        y0 = self.top_margin
        x1 = x0 + BOARD_WIDTH * self.cell_size
        y1 = y0 + BOARD_HIGHT * self.cell_size
        self.board_canvas.create_rectangle(
            x0, y0, x1, y1, fill=BOARD_BLUE, outline=BOARD_BORDER, width=3
        )

        # Draw discs
        radius = self.cell_size * 0.39
        for r in range(BOARD_HIGHT):
            for c in range(BOARD_WIDTH):
                cx = x0 + c * self.cell_size + self.cell_size / 2
                cy = y0 + r * self.cell_size + self.cell_size / 2
                cell = board[r][c]
                fill_color = self._symbol_color(cell)

                is_last = self.last_move_rc == (r, c)
                outline_color = HIGHLIGHT_RING if is_last else BOARD_BORDER
                outline_width = 3 if is_last else 2

                self.board_canvas.create_oval(
                    cx - radius,
                    cy - radius,
                    cx + radius,
                    cy + radius,
                    fill=fill_color,
                    outline=outline_color,
                    width=outline_width,
                )

    def _draw_mini_board(self, board):
        self.mini_canvas.delete("all")
        radius = self.mini_cell * 0.38
        for r in range(BOARD_HIGHT):
            for c in range(BOARD_WIDTH):
                cx = self.mini_pad + c * self.mini_cell + self.mini_cell / 2
                cy = self.mini_pad + r * self.mini_cell + self.mini_cell / 2
                fill_color = self._symbol_color(board[r][c])
                self.mini_canvas.create_oval(
                    cx - radius,
                    cy - radius,
                    cx + radius,
                    cy + radius,
                    fill=fill_color,
                    outline="",
                )

    def _col_from_x(self, x):
        rel_x = x - self.board_pad
        if 0 <= rel_x < BOARD_WIDTH * self.cell_size:
            return int(rel_x // self.cell_size) + 1
        return None

    def _on_board_hover(self, event):
        col = self._col_from_x(event.x)
        if col != self.hover_col:
            self.hover_col = col
            self._draw_main_board()

    def _on_board_leave(self, _event):
        if self.hover_col is not None:
            self.hover_col = None
            self._draw_main_board()

    def _on_board_click(self, event):
        if self.ai_thinking or self.solver.is_finished() or self.solver.is_agent_turn:
            return

        col = self._col_from_x(event.x)
        if col is None:
            return

        new_state = self.solver.user_move(col)
        if new_state is None:
            return

        landed_row = new_state.top[col - 1] + 1
        self.last_move_rc = (landed_row, col - 1)
        self._refresh_board_and_scores()

        if not self.solver.is_finished():
            self._schedule_ai_turn()

    def _schedule_ai_turn(self):
        self.ai_thinking = True
        self._refresh_board_and_scores()
        session_id = self.game_session_id
        self.root.after(60, lambda: self._execute_ai_turn(session_id))

    def _execute_ai_turn(self, session_id):
        if session_id != self.game_session_id or self.solver.is_finished():
            return

        tree_root = self.solver.current_state
        start_time = time.perf_counter()
        move, new_state = self.solver.agent_move()
        elapsed = time.perf_counter() - start_time

        landed_row = new_state.top[move - 1] + 1
        self.last_move_rc = (landed_row, move - 1)
        self.ai_thinking = False

        self.telemetry_label.config(
            text=(
                f"Chosen Col: {move} | Expanded: {self.solver.expanded_nodes} | "
                f"Total Expanded: {self.solver.total_expanded_nodes} | Time: {elapsed:.4f}s"
            )
        )
        self._populate_tree(tree_root, move)
        self._draw_mini_board(new_state.board)
        self.inspector_detail.config(
            text=f"Showing chosen move: Column {move}\nUtility: {new_state.utility}\nClick any node to inspect its board."
        )
        self._refresh_board_and_scores()

    def _populate_tree(self, root_state, chosen_move):
        self.tree.delete(*self.tree.get_children())
        self.tree_node_states.clear()

        root_id = self.tree.insert(
            "",
            "end",
            text=f"ROOT (Chosen: Col {chosen_move})",
            values=("MAX", root_state.utility),
            open=True,
            tags=("chosen",),
        )
        self.tree_node_states[root_id] = root_state

        if root_state.next_moves:
            for move, child_state in root_state.next_moves.items():
                is_chosen = move == chosen_move
                self._insert_tree_node(
                    parent_id=root_id,
                    state=child_state,
                    move=move,
                    is_max=False,
                    is_chosen_root_branch=is_chosen,
                    rel_depth=1,
                )

    def _insert_tree_node(self, parent_id, state, move, is_max, is_chosen_root_branch, rel_depth):
        if state.pruned:
            item_id = self.tree.insert(
                parent_id,
                "end",
                text=f"Col {move}",
                values=("PRUNED", "—"),
                open=False,
                tags=("pruned",),
            )
            self.tree_node_states[item_id] = state
            return

        if state.depth == GAME_LENGTH:
            role = "LEAF (Terminal)"
        elif not state.next_moves:
            role = "LEAF (Heuristic)"
        else:
            role = "MAX" if is_max else "MIN"

        if is_chosen_root_branch and rel_depth == 1:
            tag = "chosen"
        elif role.startswith("LEAF"):
            tag = "leaf"
        else:
            tag = "max_node" if is_max else "min_node"

        # Auto-expand depth 1 so all 7 candidate columns are visible immediately
        should_open = rel_depth == 1

        item_id = self.tree.insert(
            parent_id,
            "end",
            text=f"Col {move}",
            values=(role, state.utility),
            open=should_open,
            tags=(tag,),
        )
        self.tree_node_states[item_id] = state

        if state.next_moves:
            for child_move, child_state in state.next_moves.items():
                self._insert_tree_node(
                    parent_id=item_id,
                    state=child_state,
                    move=child_move,
                    is_max=not is_max,
                    is_chosen_root_branch=False,
                    rel_depth=rel_depth + 1,
                )

    def _on_tree_node_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        item_id = selected[0]
        state = self.tree_node_states.get(item_id)
        if state is None:
            return

        self._draw_mini_board(state.board)
        item_text = self.tree.item(item_id, "text")
        role, util = self.tree.item(item_id, "values")
        status_note = "Pruned before evaluation." if state.pruned else f"Utility Score: {util}"
        self.inspector_detail.config(
            text=f"Node: {item_text}\nType: {role}\nDepth: {state.depth}/{GAME_LENGTH}\n{status_note}"
        )


def main():
    root = tk.Tk()
    Connect4GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()