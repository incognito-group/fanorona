import os
import json
import time
import random
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import joblib
import numpy as np

from game_logic import FanoronGame, ADJACENCY
from ai.minimax.minimax import minimax_decision
from ai.minimax.alphabeta import alphabeta_decision
from train import generate_selfplay_data, train_model, normalize_board, get_source_cell_for_dest

# Global game session state
active_game = FanoronGame()
# Global model reference
clf_model: Any = None
# Global metrics reference
model_metrics: Dict[str, Any] = {}
# Training status for non-blocking training
training_status: Dict[str, Any] = {
    "running": False,
    "progress": "",
    "result": None,
    "error": None
}

def load_local_model() -> bool:
    """Loads the trained model from disk if it exists."""
    global clf_model, model_metrics
    model_path = os.path.join("models", "fanoron.joblib")
    metrics_path = os.path.join("models", "metrics.json")
    
    if os.path.exists(model_path):
        try:
            clf_model = joblib.load(model_path)
            print("Model loaded successfully from models/fanoron.joblib")
            if os.path.exists(metrics_path):
                with open(metrics_path, "r") as f:
                    model_metrics = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
    return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Check if model exists, if not generate dataset & train it
    model_path = os.path.join("models", "fanoron.joblib")
    if not os.path.exists(model_path):
        print("No trained model found. Generating dataset and training automatically...")
        try:
            generate_selfplay_data(num_games=10000)
            train_model(epochs=50)
        except Exception as e:
            print(f"Error during auto-training on startup: {e}")
            
    # Load model
    load_local_model()
    yield
    # Shutdown: clean up if necessary
    pass

app = FastAPI(
    title="Fanoron-telo API",
    description="Backend API for Fanoron-telo game featuring Minimax, Alpha-Beta, and trained MLPClassifier AI.",
    version="2.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Pydantic Schemas ───

class PlayRequest(BaseModel):
    cell: Optional[int] = None
    from_cell: Optional[int] = None
    to_cell: Optional[int] = None

class AiMoveRequest(BaseModel):
    difficulty: str  # "easy", "medium", "hard"

class TrainRequest(BaseModel):
    episodes: int = 5000

# ─── Helpers ───

def get_game_state_response() -> Dict[str, Any]:
    """Helper to format the current game state response."""
    return {
        "board": active_game.board,
        "current_player": active_game.current_player,
        "phase": active_game.phase,
        "winner": active_game.winner,
        "legal_moves": active_game.get_legal_moves(),
        "has_undo": len(active_game.history) > 0,
        "has_redo": len(active_game.redo_stack) > 0,
        "history": [entry[3] for entry in active_game.history]  # List of played moves
    }

# ─── Game Endpoints ───

@app.get("/game/state")
def get_state():
    """Returns the current game state without modifying anything."""
    return get_game_state_response()

@app.post("/game/new")
def new_game():
    """Initializes a new game session."""
    active_game.reset()
    state = get_game_state_response()
    # Return both {"state": ...} and flatten board for compatibility
    return {"state": state["board"], **state}

@app.post("/game/play")
def play_move(req: PlayRequest):
    """
    Applies a user move.
    Can accept:
    - 'cell' (Phase 1 placement, or Phase 2 destination with auto tie-breaker)
    - 'from_cell' and 'to_cell' (Phase 2 movement)
    """
    if active_game.winner is not None:
        raise HTTPException(status_code=400, detail="Game has already ended")

    move_dict = None
    
    # 1. Check if placement/movement is specified by from_cell / to_cell
    if req.from_cell is not None and req.to_cell is not None:
        move_dict = {
            "type": "movement",
            "from_cell": req.from_cell,
            "to_cell": req.to_cell
        }
    # 2. Check if only cell is specified
    elif req.cell is not None:
        if active_game.phase == "placement":
            move_dict = {
                "type": "placement",
                "cell": req.cell
            }
        else:
            # In Phase 2 movement, cell acts as destination 'to_cell'.
            # Resolve the source cell using the game rules.
            src = get_source_cell_for_dest(active_game.board, active_game.current_player, req.cell)
            if src is not None:
                move_dict = {
                    "type": "movement",
                    "from_cell": src,
                    "to_cell": req.cell
                }
            else:
                raise HTTPException(status_code=400, detail="No pieces can move to this cell")
    else:
        raise HTTPException(status_code=400, detail="Invalid request parameters")

    # Apply the move
    success = active_game.make_move(move_dict)
    if not success:
        raise HTTPException(status_code=400, detail=f"Illegal move: {move_dict}")
        
    return get_game_state_response()

@app.post("/game/undo")
def undo_move():
    """Undoes the last move."""
    success = active_game.undo()
    if not success:
        raise HTTPException(status_code=400, detail="No moves to undo")
    return get_game_state_response()

@app.post("/game/redo")
def redo_move():
    """Redoes the last undone move."""
    success = active_game.redo()
    if not success:
        raise HTTPException(status_code=400, detail="No moves to redo")
    return get_game_state_response()

# ─── AI Endpoints ───

VALID_DIFFICULTIES = {"easy", "medium", "hard"}

@app.post("/ai/move")
def get_ai_move(req: AiMoveRequest):
    """
    Returns the AI's selected move based on difficulty.
    - Easy: selects a random legal move.
    - Medium: Minimax (depth 3).
    - Hard: Uses MLPClassifier Joblib model. Falls back to Alpha-Beta (depth 8) if unavailable.
    """
    legal_moves = active_game.get_legal_moves()
    if not legal_moves:
        raise HTTPException(status_code=400, detail="No legal moves available")

    difficulty = req.difficulty.lower()
    if difficulty not in VALID_DIFFICULTIES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid difficulty level '{difficulty}'. Must be one of: {', '.join(VALID_DIFFICULTIES)}"
        )
    
    start_time = time.time()
    
    move_result = None
    confidence = 1.0
    nodes_explored = 0
    depth_reached = 0

    if difficulty == "easy":
        move_result = random.choice(legal_moves)
        depth_reached = 0
        nodes_explored = 1
        
    elif difficulty == "medium":
        # Minimax depth 3
        best_move, _, nodes_explored = minimax_decision(active_game, depth=3)
        move_result = best_move
        depth_reached = 3
        
    elif difficulty == "hard":
        global clf_model
        # Use trained MLP model if loaded
        if clf_model is not None:
            try:
                # Format input
                x = normalize_board(active_game.board, active_game.current_player)
                # Predict probability distribution over the 9 cells
                probs = clf_model.predict_proba([x])[0]  # Array of 9 probabilities
                
                # Filter by legal moves: find the legal move with the highest NN probability
                best_legal_move = None
                best_prob = -1.0
                
                for m in legal_moves:
                    target_cell = m["cell"] if m["type"] == "placement" else m["to_cell"]
                    prob = probs[target_cell]
                    if prob > best_prob:
                        best_prob = prob
                        best_legal_move = m
                
                move_result = best_legal_move
                confidence = float(best_prob)
                depth_reached = 0
                nodes_explored = 1  # Single forward pass
            except Exception as e:
                print(f"MLP prediction failed, falling back to Alpha-Beta: {e}")
                move_result = None  # Force fallback without clearing model permanently
                
        # Fallback to Alpha-Beta depth 8
        if move_result is None:
            best_move, _, depth, nodes = alphabeta_decision(active_game, max_depth=8, time_limit_sec=1.5)
            move_result = best_move
            depth_reached = depth
            nodes_explored = nodes
            confidence = 1.0

    if move_result is None:
        # Emergency fallback
        move_result = random.choice(legal_moves)

    # Format move output
    move_cell = move_result["cell"] if move_result["type"] == "placement" else move_result["to_cell"]
    from_cell = move_result.get("from_cell", None)
    
    computation_time = time.time() - start_time
    
    return {
        "move": move_cell,
        "from_cell": from_cell,
        "to_cell": move_cell,
        "confidence": round(confidence, 4),
        "duration_ms": int(computation_time * 1000),
        "nodes_explored": nodes_explored,
        "depth_reached": depth_reached,
        "move_details": move_result
    }

# ─── Training Endpoints ───

def _run_training_task(num_games: int, epochs: int):
    """Background task that runs dataset generation and model training."""
    global training_status
    try:
        training_status["progress"] = f"Generating {num_games} self-play games..."
        generate_selfplay_data(num_games=num_games)
        
        training_status["progress"] = f"Training MLP for {epochs} epochs..."
        metrics = train_model(epochs=epochs)
        
        # Reload model weights
        load_local_model()
        
        training_status["result"] = {
            "accuracy": round(metrics["accuracy"], 4),
            "dataset_size": metrics["dataset_size"],
            "training_time": metrics["training_time_sec"]
        }
        training_status["progress"] = "Completed"
    except Exception as e:
        training_status["error"] = str(e)
        training_status["progress"] = f"Failed: {str(e)}"
    finally:
        training_status["running"] = False

@app.post("/train")
def train_ai_model(req: TrainRequest, background_tasks: BackgroundTasks):
    """
    Triggers the generation of the dataset (based on number of episodes)
    and trains the MLP Neural Network in a background task.
    
    For backward compatibility, this endpoint runs synchronously if the
    training completes quickly. Use GET /train/status to poll progress.
    """
    if training_status["running"]:
        raise HTTPException(status_code=409, detail="Training is already in progress")
    
    num_games = max(req.episodes, 1000)
    
    # Run synchronously for backward compatibility with the frontend
    # (the frontend expects the result in the response)
    try:
        training_status["running"] = True
        training_status["error"] = None
        training_status["result"] = None
        training_status["progress"] = f"Generating {num_games} self-play games..."
        
        generate_selfplay_data(num_games=num_games)
        
        training_status["progress"] = "Training MLP for 50 epochs..."
        metrics = train_model(epochs=50)
        
        # Load new model weights
        load_local_model()
        
        training_status["running"] = False
        training_status["progress"] = "Completed"
        training_status["result"] = {
            "accuracy": round(metrics["accuracy"], 4),
            "dataset_size": metrics["dataset_size"],
            "training_time": metrics["training_time_sec"]
        }
        
        return {
            "accuracy": round(metrics["accuracy"], 4),
            "dataset_size": metrics["dataset_size"],
            "training_time": metrics["training_time_sec"]
        }
    except Exception as e:
        training_status["running"] = False
        training_status["error"] = str(e)
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@app.get("/train/status")
def get_training_status():
    """Returns the current training status (useful for polling during background training)."""
    return training_status

@app.post("/model/load")
def load_model_route():
    """Forces reloading of the Joblib model from disk."""
    success = load_local_model()
    if not success:
        raise HTTPException(status_code=400, detail="Model file not found on disk")
    return {
        "status": "success",
        "message": "Model loaded successfully",
        "metrics": model_metrics
    }

@app.get("/model/history")
def get_model_history():
    """Returns training history log from disk."""
    history_path = os.path.join("models", "training_history.json")
    if os.path.exists(history_path):
        try:
            with open(history_path, "r") as f:
                return json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading history: {e}")
    return []

# Serve static frontend files directly from root URL
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
