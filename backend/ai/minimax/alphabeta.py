import time
from typing import Dict, Tuple, Optional, List
from game_logic import FanoronGame
from ai.minimax.evaluation import evaluate_board
from ai.minimax.cache import TranspositionTable

def alphabeta_decision(
    game: FanoronGame, 
    max_depth: int = 8, 
    time_limit_sec: float = 1.5
) -> Tuple[Optional[Dict], float, int, int]:
    """
    Finds the best move using Minimax with Alpha-Beta pruning, transposition table, 
    and iterative deepening up to max_depth.
    
    The search always maximizes for the calling player regardless of whether
    it is Player 1 or Player 2.
    
    Returns:
        (best_move, score, depth_reached, states_explored)
    """
    player = game.current_player
    tt = TranspositionTable()
    states_explored = 0
    start_time = time.time()
    
    global_best_move: Optional[Dict] = None
    global_best_score: float = -float('inf')
    
    # Move ordering: put the best move from a previous depth or TT first
    # to improve pruning efficiency.
    def order_moves(moves: List[Dict], table_best_move: Optional[Dict]) -> List[Dict]:
        if not table_best_move:
            return moves
        
        ordered = []
        for m in moves:
            if _moves_equal(m, table_best_move):
                ordered.insert(0, m)
            else:
                ordered.append(m)
        return ordered

    def _moves_equal(a: Dict, b: Dict) -> bool:
        """Helper to compare two move dicts."""
        if a.get("type") != b.get("type"):
            return False
        if a["type"] == "placement":
            return a["cell"] == b["cell"]
        else:
            return a["from_cell"] == b["from_cell"] and a["to_cell"] == b["to_cell"]

    def alphabeta(
        current_game: FanoronGame,
        depth: int,
        alpha: float,
        beta: float,
        is_maximizing: bool
    ) -> Tuple[Optional[Dict], float]:
        nonlocal states_explored
        states_explored += 1
        
        # Check time limit
        if time.time() - start_time > time_limit_sec:
            raise TimeoutError()

        # Generate transposition table key
        state_key = tt.get_state_key(current_game.board, current_game.current_player, current_game.phase)
        cached = tt.lookup(state_key)
        
        # If cache exists and has been searched to at least the current depth, use it
        if cached is not None and cached["depth"] >= depth:
            if cached["flag"] == "EXACT":
                return cached["best_move"], cached["value"]
            elif cached["flag"] == "LOWERBOUND":
                alpha = max(alpha, cached["value"])
            elif cached["flag"] == "UPPERBOUND":
                beta = min(beta, cached["value"])
            if alpha >= beta:
                return cached["best_move"], cached["value"]

        # Base cases
        if current_game.winner is not None or depth == 0:
            val = evaluate_board(current_game.board, player)
            # Adjust score to prefer shorter paths to victory
            if val >= 900:
                val += depth  # Higher depth remaining = found win sooner = better
            elif val <= -900:
                val -= depth  # Found loss sooner = worse
            return None, val

        legal_moves = current_game.get_legal_moves()
        if not legal_moves:
            val = evaluate_board(current_game.board, player)
            return None, val

        # Order moves using cached best move if available
        table_best_move = cached["best_move"] if cached else None
        ordered_moves = order_moves(legal_moves, table_best_move)

        # Save original alpha for TT flag determination
        original_alpha = alpha

        best_move = ordered_moves[0]  # Default to first move
        if is_maximizing:
            value = -float('inf')
            for move in ordered_moves:
                # Use fast make/undo instead of copy.deepcopy
                snapshot = current_game.make_move_fast(move)
                try:
                    _, val = alphabeta(current_game, depth - 1, alpha, beta, False)
                except TimeoutError:
                    current_game.undo_move_fast(snapshot)
                    raise
                current_game.undo_move_fast(snapshot)
                
                if val > value:
                    value = val
                    best_move = move
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # Beta cutoff
            
            # Store in Transposition Table with correct flag logic
            if value <= original_alpha:
                flag = "UPPERBOUND"
            elif value >= beta:
                flag = "LOWERBOUND"
            else:
                flag = "EXACT"
            tt.store(state_key, value, depth, flag, best_move)
            
            return best_move, value
        else:
            value = float('inf')
            for move in ordered_moves:
                # Use fast make/undo instead of copy.deepcopy
                snapshot = current_game.make_move_fast(move)
                try:
                    _, val = alphabeta(current_game, depth - 1, alpha, beta, True)
                except TimeoutError:
                    current_game.undo_move_fast(snapshot)
                    raise
                current_game.undo_move_fast(snapshot)

                if val < value:
                    value = val
                    best_move = move
                beta = min(beta, value)
                if alpha >= beta:
                    break  # Alpha cutoff
            
            # Store in Transposition Table with correct flag logic
            if value >= beta:
                flag = "LOWERBOUND"
            elif value <= original_alpha:
                flag = "UPPERBOUND"
            else:
                flag = "EXACT"
            tt.store(state_key, value, depth, flag, best_move)
            
            return best_move, value

    # Iterative deepening loop
    depth_reached = 0
    for d in range(1, max_depth + 1):
        try:
            # Always start maximizing for the calling player
            best_move, score = alphabeta(
                game, 
                d, 
                -float('inf'), 
                float('inf'), 
                is_maximizing=True
            )
            if best_move is not None:
                global_best_move = best_move
                global_best_score = score
            depth_reached = d
            
            # Early exit if we found a guaranteed win
            if global_best_score >= 900:
                break
        except TimeoutError:
            # Return the best move found at the previous completed depth
            break

    # Fallback: if no move was found, select the first legal move
    if global_best_move is None:
        legal = game.get_legal_moves()
        if legal:
            global_best_move = legal[0]
            global_best_score = 0.0

    return global_best_move, global_best_score, depth_reached, states_explored
