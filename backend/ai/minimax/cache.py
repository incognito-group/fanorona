from typing import Dict, Any, Optional

class TranspositionTable:
    def __init__(self):
        # Maps state key string to a dictionary with evaluation details
        self.table: Dict[str, Dict[str, Any]] = {}

    def get_state_key(self, board: list, player: int, phase: str) -> str:
        """Converts board state, player, and phase into a unique key string."""
        board_str = "".join(map(str, board))
        return f"{board_str}-{player}-{phase}"

    def lookup(self, key: str) -> Optional[Dict[str, Any]]:
        """Returns cache entry if it exists, otherwise None."""
        return self.table.get(key, None)

    def store(self, key: str, value: float, depth: int, flag: str, best_move: Optional[dict]):
        """Stores evaluation information in the table."""
        # Replace if existing entry was searched at lower depth
        if key in self.table and self.table[key]["depth"] > depth:
            return
        self.table[key] = {
            "value": value,
            "depth": depth,
            "flag": flag,
            "best_move": best_move
        }

    def clear(self):
        """Clears the table."""
        self.table.clear()
