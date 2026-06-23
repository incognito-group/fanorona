import time
from typing import Dict, Tuple, Optional
from game_logic import FanoronGame
from ai.minimax.evaluation import evaluate_board

def minimax_decision(game: FanoronGame, depth: int = 3) -> Tuple[Optional[Dict], float, int]:
    """
    Finds the best move using the Minimax algorithm with depth limit.
    
    The search always maximizes for the calling player regardless of whether
    it is Player 1 or Player 2.
    
    Returns:
        (best_move, score, states_explored)
    """
    player = game.current_player
    states_explored = 0

    def minimax(current_game: FanoronGame, current_depth: int, is_maximizing: bool) -> Tuple[Optional[Dict], float]:
        nonlocal states_explored
        states_explored += 1

        # Base cases: win, loss, draw, or depth reached
        if current_game.winner is not None or current_depth == 0:
            val = evaluate_board(current_game.board, player)
            # Adjust score by depth to prefer quicker wins and slower losses
            if val >= 900:
                val += current_depth  # Higher remaining depth = found win sooner
            elif val <= -900:
                val -= current_depth
            return None, val

        legal_moves = current_game.get_legal_moves()
        if not legal_moves:
            # Stalemate check
            val = evaluate_board(current_game.board, player)
            return None, val

        best_move = legal_moves[0]  # Default to first legal move
        if is_maximizing:
            best_val = -float('inf')
            for move in legal_moves:
                # Use fast make/undo instead of copy.deepcopy
                snapshot = current_game.make_move_fast(move)
                _, val = minimax(current_game, current_depth - 1, False)
                current_game.undo_move_fast(snapshot)
                if val > best_val:
                    best_val = val
                    best_move = move
            return best_move, best_val
        else:
            best_val = float('inf')
            for move in legal_moves:
                # Use fast make/undo instead of copy.deepcopy
                snapshot = current_game.make_move_fast(move)
                _, val = minimax(current_game, current_depth - 1, True)
                current_game.undo_move_fast(snapshot)
                if val < best_val:
                    best_val = val
                    best_move = move
            return best_move, best_val

    # Run Minimax — always start maximizing for the calling player
    best_move, score = minimax(game, depth, True)
    return best_move, score, states_explored
