from typing import List
from game_logic import WINNING_LINES, WIN_PATTERNS, ADJACENCY

def evaluate_board(board: List[int], player: int) -> int:
    """
    Evaluates the board state from the perspective of the specified player.
    
    Heuristics used:
    1. Immediate win/loss detection via bitmask patterns (+/-1000)
    2. Two-aligned pieces with open third cell (+/-50)
    3. Control of the center cell 4 (+/-10)
    4. Mobility advantage: difference in number of available moves (+/-5)
    
    Returns:
        int: Board score (higher is better for the specified player).
    """
    opponent = 3 - player
    
    # 1. Check for immediate win/loss using fast bitmask operations
    mask_player = 0
    mask_opponent = 0
    for i, val in enumerate(board):
        if val == player:
            mask_player |= (1 << i)
        elif val == opponent:
            mask_opponent |= (1 << i)

    # Check player win
    for pattern in WIN_PATTERNS:
        if (mask_player & pattern) == pattern:
            return 1000
            
    # Check opponent win
    for pattern in WIN_PATTERNS:
        if (mask_opponent & pattern) == pattern:
            return -1000

    score = 0

    # 2. Check for two-aligned pieces (two pieces of same player, third is empty)
    for line in WINNING_LINES:
        p_count = sum(1 for cell in line if board[cell] == player)
        o_count = sum(1 for cell in line if board[cell] == opponent)
        empty_count = sum(1 for cell in line if board[cell] == 0)
        
        if p_count == 2 and empty_count == 1:
            score += 50
        elif o_count == 2 and empty_count == 1:
            score -= 50
        # Bonus for single piece on open line (strategic positioning)
        elif p_count == 1 and empty_count == 2:
            score += 5
        elif o_count == 1 and empty_count == 2:
            score -= 5

    # 3. Control of the center (cell 4) — most connected cell
    if board[4] == player:
        score += 15
    elif board[4] == opponent:
        score -= 15

    # 4. Mobility advantage: count available moves for each side
    player_moves = 0
    opponent_moves = 0
    for cell in range(9):
        if board[cell] == player:
            for adj in ADJACENCY[cell]:
                if board[adj] == 0:
                    player_moves += 1
        elif board[cell] == opponent:
            for adj in ADJACENCY[cell]:
                if board[adj] == 0:
                    opponent_moves += 1
    score += (player_moves - opponent_moves) * 3

    return score
