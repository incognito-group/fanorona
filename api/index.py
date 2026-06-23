from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Allow importing your AI script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from game_ai import facile, moyenne, difficile

app = FastAPI()

class GameState(BaseModel):
    board1D: List[Optional[str]] # ['P1', 'P2', None, ...] from React
    difficulty: str             # 'facile', 'moyenne', 'difficile'
    phase: int                  # 1 or 2
    aiPlayer: int               # 2 (Black/Noir) or 1 (White/Vert)

def convert_1d_to_2d(board1d):
    matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for index, cell in enumerate(board1d):
        i = index // 3
        j = index % 3
        if cell == 'P1': matrix[i][j] = 1
        elif cell == 'P2': matrix[i][j] = 2
        else: matrix[i][j] = 0
    return matrix

@app.post("/api/get-move")
async def get_move(state: GameState):
    # 1. Transform React format to Python matrix format
    plateau = convert_1d_to_2d(state.board1D)
    
    # 2. Match difficulty level to correct function
    if state.difficulty == "facile":
        coup = facile(plateau, state.aiPlayer, state.phase)
    elif state.difficulty == "moyenne":
        coup = moyenne(plateau, state.aiPlayer, state.phase)
    elif state.difficulty == "difficile":
        coup = difficile(plateau, state.aiPlayer, state.phase)
    else:
        raise HTTPException(status_code=400, detail="Invalid difficulty level")

    if coup is None:
        return {"hasMove": False}

    # 3. Format structural output for React consumption
    if state.phase == 1:
        # Placement move: (i, j)
        i, j = coup
        return {
            "hasMove": True,
            "index": i * 3 + j
        }
    else:
        # Movement move: ((i1, j1), (i2, j2))
        (i1, j1), (i2, j2) = coup
        return {
            "hasMove": True,
            "fromIndex": i1 * 3 + j1,
            "toIndex": i2 * 3 + j2
        }