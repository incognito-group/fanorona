import numpy as np
from typing import List, Tuple, Optional, Dict, Set

# Adjacency list for Fanoron-telo board connections
# Corners (0, 2, 6, 8) connect to orthogonal neighbors and the center (4) diagonally.
# Edges (1, 3, 5, 7) connect orthogonally to neighbors and the center (4).
# Center (4) connects to all 8 surrounding cells.
ADJACENCY: Dict[int, List[int]] = {
    0: [1, 3, 4],
    1: [0, 2, 4],
    2: [1, 5, 4],
    3: [0, 6, 4],
    4: [0, 1, 2, 3, 5, 6, 7, 8],
    5: [2, 8, 4],
    6: [3, 7, 4],
    7: [6, 8, 4],
    8: [5, 7, 4]
}

# The 8 winning lines represented as tuples of cell indices
WINNING_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
    (0, 4, 8), (2, 4, 6)              # Diagonals
]

# Winning line bitmasks for fast win-checking using bitwise operations
WIN_PATTERNS = [
    7,    # 000000111 -> Row 0 (0,1,2)
    56,   # 000111000 -> Row 1 (3,4,5)
    448,  # 111000000 -> Row 2 (6,7,8)
    73,   # 001001001 -> Col 0 (0,3,6)
    146,  # 010010010 -> Col 1 (1,4,7)
    292,  # 100100100 -> Col 2 (2,5,8)
    273,  # 100010001 -> Main Diagonal (0,4,8)
    84    # 001010100 -> Anti-Diagonal (2,4,6)
]

class FanoronGame:
    def __init__(self):
        self.reset()

    def reset(self):
        # Board representation: 9 integers (0: empty, 1: Player 1, 2: Player 2)
        self.board: List[int] = [0] * 9
        self.current_player: int = 1
        self.winner: Optional[int] = None  # None: active, 1 or 2: winner, -1: draw
        self.phase: str = "placement"      # "placement" or "movement"
        
        # Incremental bitmasks for fast win-checking
        self.p1_mask: int = 0
        self.p2_mask: int = 0
        self.piece_count: int = 0  # Total pieces on board
        
        # History stacks for undo/redo
        # A history entry contains: (board_snapshot, current_player, phase, move_played, winner, p1_mask, p2_mask, piece_count)
        self.history: List[Tuple] = []
        self.redo_stack: List[Tuple] = []
        
        # State frequencies to detect 3-fold repetition draws in Phase 2
        self.state_frequencies: Dict[str, int] = {}
        self._record_state_frequency()

    def _record_state_frequency(self):
        state_str = "".join(map(str, self.board)) + f"-{self.current_player}"
        self.state_frequencies[state_str] = self.state_frequencies.get(state_str, 0) + 1

    def _remove_state_frequency(self):
        state_str = "".join(map(str, self.board)) + f"-{self.current_player}"
        if state_str in self.state_frequencies:
            self.state_frequencies[state_str] -= 1
            if self.state_frequencies[state_str] <= 0:
                del self.state_frequencies[state_str]

    @property
    def board_bitmask_p1(self) -> int:
        """Returns player 1's pieces as a bitmask (uses cached incremental value)."""
        return self.p1_mask

    @property
    def board_bitmask_p2(self) -> int:
        """Returns player 2's pieces as a bitmask (uses cached incremental value)."""
        return self.p2_mask

    def _get_mask(self, player: int) -> int:
        """Returns the bitmask for the given player."""
        return self.p1_mask if player == 1 else self.p2_mask

    def _set_cell(self, cell: int, player: int):
        """Sets a cell to a player value and updates bitmasks incrementally."""
        old_val = self.board[cell]
        # Remove old value from masks
        if old_val == 1:
            self.p1_mask &= ~(1 << cell)
            self.piece_count -= 1
        elif old_val == 2:
            self.p2_mask &= ~(1 << cell)
            self.piece_count -= 1
        # Set new value
        self.board[cell] = player
        if player == 1:
            self.p1_mask |= (1 << cell)
            self.piece_count += 1
        elif player == 2:
            self.p2_mask |= (1 << cell)
            self.piece_count += 1

    def _clear_cell(self, cell: int):
        """Clears a cell and updates bitmasks incrementally."""
        old_val = self.board[cell]
        if old_val == 1:
            self.p1_mask &= ~(1 << cell)
            self.piece_count -= 1
        elif old_val == 2:
            self.p2_mask &= ~(1 << cell)
            self.piece_count -= 1
        self.board[cell] = 0

    def check_win(self, player: int) -> bool:
        """Checks if the given player has aligned 3 pieces using fast bitboard checks."""
        mask = self._get_mask(player)
        for pattern in WIN_PATTERNS:
            if (mask & pattern) == pattern:
                return True
        return False

    def is_board_full_for_phase1(self) -> bool:
        """Returns True if 6 pieces are placed on the board (end of Phase 1)."""
        return self.piece_count >= 6

    def get_legal_moves(self) -> List[Dict]:
        """
        Returns a list of legal moves for the current player.
        Each move is represented as a dictionary:
        - Phase 1 (Placement): {"type": "placement", "cell": int}
        - Phase 2 (Movement): {"type": "movement", "from_cell": int, "to_cell": int}
        """
        if self.winner is not None:
            return []

        moves = []
        if self.phase == "placement":
            # Any empty cell is a legal placement
            for cell in range(9):
                if self.board[cell] == 0:
                    moves.append({"type": "placement", "cell": cell})
        else:
            # Move a piece to an adjacent empty cell
            for cell in range(9):
                if self.board[cell] == self.current_player:
                    for adj in ADJACENCY[cell]:
                        if self.board[adj] == 0:
                            moves.append({
                                "type": "movement",
                                "from_cell": cell,
                                "to_cell": adj
                            })
        return moves

    def make_move(self, move: Dict) -> bool:
        """
        Executes a move, checks for win or draw, and switches the active player.
        Saves state to history to enable undo. Clear redo stack on new move.
        Returns True if the move was successfully made, False otherwise.
        """
        legal_moves = self.get_legal_moves()
        # Validate move
        is_legal = False
        for legal in legal_moves:
            if move["type"] == "placement":
                if legal["type"] == "placement" and legal["cell"] == move["cell"]:
                    is_legal = True
                    break
            elif move["type"] == "movement":
                if (legal["type"] == "movement" and 
                    legal["from_cell"] == move["from_cell"] and 
                    legal["to_cell"] == move["to_cell"]):
                    is_legal = True
                    break
        
        if not is_legal:
            return False

        # Save snapshot to history (including bitmask state)
        self.history.append((
            list(self.board),
            self.current_player,
            self.phase,
            move,
            self.winner,
            self.p1_mask,
            self.p2_mask,
            self.piece_count
        ))
        self.redo_stack.clear()

        # Apply move using incremental bitmask updates
        if move["type"] == "placement":
            self._set_cell(move["cell"], self.current_player)
        elif move["type"] == "movement":
            self._clear_cell(move["from_cell"])
            self._set_cell(move["to_cell"], self.current_player)

        # Check for immediate victory
        if self.check_win(self.current_player):
            self.winner = self.current_player
        else:
            # Check phase transition: from placement to movement
            if self.phase == "placement" and self.is_board_full_for_phase1():
                self.phase = "movement"

            # Switch player
            self.current_player = 3 - self.current_player

            # Check for draw by 3-fold repetition in Phase 2
            if self.phase == "movement":
                self._record_state_frequency()
                state_str = "".join(map(str, self.board)) + f"-{self.current_player}"
                if self.state_frequencies.get(state_str, 0) >= 3:
                    self.winner = -1  # Draw

            # Check if next player has any legal moves. If not, they lose.
            if self.winner is None and len(self.get_legal_moves()) == 0:
                self.winner = 3 - self.current_player  # The other player wins

        return True

    # ─── Fast Make/Undo for AI Search (no history, no validation) ───

    def make_move_fast(self, move: Dict) -> Tuple:
        """
        Lightweight move application for AI search trees.
        Skips validation, history, and redo stacks for maximum speed.
        Returns a snapshot tuple to restore via undo_move_fast().
        """
        snapshot = (
            list(self.board),
            self.current_player,
            self.phase,
            self.winner,
            self.p1_mask,
            self.p2_mask,
            self.piece_count
        )

        # Apply move
        if move["type"] == "placement":
            self._set_cell(move["cell"], self.current_player)
        elif move["type"] == "movement":
            self._clear_cell(move["from_cell"])
            self._set_cell(move["to_cell"], self.current_player)

        # Check for immediate victory
        if self.check_win(self.current_player):
            self.winner = self.current_player
        else:
            # Check phase transition
            if self.phase == "placement" and self.is_board_full_for_phase1():
                self.phase = "movement"

            # Switch player
            self.current_player = 3 - self.current_player

            # Check if next player has any legal moves
            if self.winner is None and len(self.get_legal_moves()) == 0:
                self.winner = 3 - self.current_player

        return snapshot

    def undo_move_fast(self, snapshot: Tuple):
        """
        Restores the game state from a snapshot created by make_move_fast().
        O(9) operation — much faster than copy.deepcopy.
        """
        (self.board, self.current_player, self.phase,
         self.winner, self.p1_mask, self.p2_mask, self.piece_count) = snapshot

    # ─── Standard Undo/Redo (with full history) ───

    def undo(self) -> bool:
        """Undoes the last move. Returns True if successful."""
        if not self.history:
            return False

        # Remove current state frequency count
        if self.phase == "movement" and self.winner != self.current_player:
            self._remove_state_frequency()

        # Pop from history and push current state to redo stack
        (prev_board, prev_player, prev_phase, prev_move,
         prev_winner, prev_p1, prev_p2, prev_count) = self.history.pop()
        
        self.redo_stack.append((
            list(self.board),
            self.current_player,
            self.phase,
            prev_move,
            self.winner,
            self.p1_mask,
            self.p2_mask,
            self.piece_count
        ))

        # Restore state
        self.board = prev_board
        self.current_player = prev_player
        self.phase = prev_phase
        self.winner = prev_winner
        self.p1_mask = prev_p1
        self.p2_mask = prev_p2
        self.piece_count = prev_count

        return True

    def redo(self) -> bool:
        """Redoes the previously undone move. Returns True if successful."""
        if not self.redo_stack:
            return False

        # Pop from redo stack and apply
        (next_board, next_player, next_phase, next_move,
         next_winner, next_p1, next_p2, next_count) = self.redo_stack.pop()

        self.history.append((
            list(self.board),
            self.current_player,
            self.phase,
            next_move,
            self.winner,
            self.p1_mask,
            self.p2_mask,
            self.piece_count
        ))

        # Restore state
        self.board = next_board
        self.current_player = next_player
        self.phase = next_phase
        self.winner = next_winner
        self.p1_mask = next_p1
        self.p2_mask = next_p2
        self.piece_count = next_count

        if self.phase == "movement" and self.winner is None:
            self._record_state_frequency()

        return True
