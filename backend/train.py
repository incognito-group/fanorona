import os
import json
import random
import time
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import joblib

from game_logic import FanoronGame, ADJACENCY
from ai.minimax.alphabeta import alphabeta_decision
from ai.minimax.evaluation import evaluate_board

# Ensure directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)

# Global cache to speed up dataset generation (board solved states lookup)
# Key: board_str + player + phase
# Value: best_move_dict
SOLVED_STATES_CACHE: Dict[str, Dict] = {}

def get_best_move_cached(game: FanoronGame) -> Dict:
    """Gets the optimal move for a state, using global cache if available, else running search."""
    board_str = "".join(map(str, game.board))
    key = f"{board_str}-{game.current_player}-{game.phase}"
    
    if key in SOLVED_STATES_CACHE:
        return SOLVED_STATES_CACHE[key]
    
    # Run Alpha-Beta search with depth 6 for dataset generation (fast & highly optimal)
    best_move, _, _, _ = alphabeta_decision(game, max_depth=6, time_limit_sec=0.5)
    
    # If no move, get first legal
    if best_move is None:
        legal = game.get_legal_moves()
        if legal:
            best_move = legal[0]
            
    if best_move is not None:
        SOLVED_STATES_CACHE[key] = best_move
        
    return best_move

def get_source_cell_for_dest(board: List[int], player: int, dest_cell: int) -> Optional[int]:
    """
    Resolves which piece should move to dest_cell in Phase 2.
    If multiple sources are valid, selects the one yielding the best board evaluation.
    """
    if board[dest_cell] != 0:
        return None
        
    valid_sources = []
    for cell in range(9):
        if board[cell] == player:
            if dest_cell in ADJACENCY[cell]:
                valid_sources.append(cell)
    if not valid_sources:
        return None
    if len(valid_sources) == 1:
        return valid_sources[0]
    
    # Tie-breaking: choose the source that gives the highest evaluation score
    best_source = valid_sources[0]
    best_score = -float('inf')
    for src in valid_sources:
        board_copy = list(board)
        board_copy[src] = 0
        board_copy[dest_cell] = player
        try:
            score = evaluate_board(board_copy, player)
        except Exception:
            score = 0
        if score > best_score:
            best_score = score
            best_source = src
    return best_source

def generate_selfplay_data(num_games: int = 10000) -> List[Dict]:
    """
    Simulates self-play games where moves are selected using an epsilon-greedy strategy.
    Uses Alpha-Beta search to determine the optimal move, and records game states
    for supervised training of the neural network.
    
    Args:
        num_games: Number of games to simulate.
        
    Returns:
        List of state records (board, current_player, legal_moves, best_move, reward).
    """
    print(f"Starting self-play simulation of {num_games} games...")
    start_time = time.time()
    
    dataset = []
    stats = {"p1_wins": 0, "p2_wins": 0, "draws": 0}
    
    for game_idx in range(num_games):
        if (game_idx + 1) % 1000 == 0 or game_idx == 0:
            elapsed = time.time() - start_time
            print(f"Simulated {game_idx + 1}/{num_games} games... (Time elapsed: {elapsed:.1f}s)")
            
        game = FanoronGame()
        game_history = []  # To store states encountered in this game
        
        # Max moves to prevent infinite loops in Phase 2 draw states
        max_moves = 40
        move_cnt = 0
        
        while game.winner is None and move_cnt < max_moves:
            legal_moves = game.get_legal_moves()
            if not legal_moves:
                break
                
            # Get optimal move (using search)
            opt_move = get_best_move_cached(game)
            if opt_move is None:
                break
                
            # Epsilon-greedy exploration (85% optimal, 15% random)
            if random.random() < 0.15:
                chosen_move = random.choice(legal_moves)
            else:
                chosen_move = opt_move
                
            # Determine cell representation for the dataset
            best_cell = opt_move["cell"] if opt_move["type"] == "placement" else opt_move["to_cell"]
            legal_cells = [m["cell"] if m["type"] == "placement" else m["to_cell"] for m in legal_moves]
            
            # Record state details
            state_record = {
                "board": list(game.board),
                "current_player": game.current_player,
                "legal_moves": list(set(legal_cells)),
                "best_move": best_cell,
                "reward": 0  # to be filled at end of game
            }
            game_history.append((game.current_player, state_record))
            
            game.make_move(chosen_move)
            move_cnt += 1
            
        # Determine reward
        winner = game.winner
        # If max_moves was reached without winner, it's a draw (winner = -1)
        if winner is None:
            winner = -1
        
        # Track statistics
        if winner == 1:
            stats["p1_wins"] += 1
        elif winner == 2:
            stats["p2_wins"] += 1
        else:
            stats["draws"] += 1
            
        for player_turn, record in game_history:
            if winner == -1:
                record["reward"] = 0
            elif winner == player_turn:
                record["reward"] = 1
            else:
                record["reward"] = -1
            dataset.append(record)
            
    total_time = time.time() - start_time
    print(f"Self-play simulation completed. Total states collected: {len(dataset)} in {total_time:.1f}s")
    print(f"Statistics: P1 wins={stats['p1_wins']}, P2 wins={stats['p2_wins']}, Draws={stats['draws']}")
    
    # Save as JSON
    json_path = os.path.join("data", "dataset.json")
    with open(json_path, "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"Dataset saved to {json_path}")
    
    # Save as CSV
    csv_rows = []
    for r in dataset:
        row = {}
        for idx, val in enumerate(r["board"]):
            row[f"board_{idx}"] = val
        row["current_player"] = r["current_player"]
        row["best_move"] = r["best_move"]
        row["reward"] = r["reward"]
        csv_rows.append(row)
        
    df = pd.DataFrame(csv_rows)
    csv_path = os.path.join("data", "dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"Dataset saved to {csv_path}")
    
    return dataset

def normalize_board(board: List[int], current_player: int) -> np.ndarray:
    """Normalizes the board representation: 1 for active player, -1 for opponent, 0 for empty."""
    norm = []
    opponent = 3 - current_player
    for val in board:
        if val == current_player:
            norm.append(1.0)
        elif val == opponent:
            norm.append(-1.0)
        else:
            norm.append(0.0)
    return np.array(norm, dtype=np.float32)

def _vectorized_normalize(boards: np.ndarray, players: np.ndarray) -> np.ndarray:
    """
    Vectorized board normalization using NumPy broadcasting.
    Much faster than iterating row-by-row with normalize_board().
    
    Args:
        boards: (N, 9) array of board states
        players: (N,) array of current players
        
    Returns:
        (N, 9) normalized array (1.0 = own piece, -1.0 = opponent, 0.0 = empty)
    """
    players_col = players[:, np.newaxis]  # (N, 1) for broadcasting
    result = np.zeros_like(boards, dtype=np.float32)
    result[boards == players_col] = 1.0
    result[(boards != 0) & (boards != players_col)] = -1.0
    return result

def train_model(epochs: int = 50) -> Dict:
    """
    Loads dataset.csv, trains an MLPClassifier (Neural Network),
    and saves the model weights and training statistics.
    
    Uses vectorized preprocessing for fast data loading.
    
    Args:
        epochs: Number of training epochs (partial_fit iterations).
        
    Returns:
        Dictionary with accuracy, dataset_size, and training_time_sec.
    """
    print("Loading dataset for training...")
    csv_path = os.path.join("data", "dataset.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Please run generate_selfplay_data first.")
        
    df = pd.read_csv(csv_path)
    
    # Vectorized preprocessing — much faster than iterrows()
    board_cols = [f"board_{i}" for i in range(9)]
    boards = df[board_cols].values.astype(np.int32)    # (N, 9)
    players = df["current_player"].values.astype(np.int32)  # (N,)
    y = df["best_move"].values.astype(np.int32)        # (N,)
    
    X = _vectorized_normalize(boards, players)
    
    print(f"Training data shape: {X.shape}, labels shape: {y.shape}")
    
    # Split into train/validation
    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.15, random_state=42)
    
    from sklearn.neural_network import MLPClassifier
    
    # Architecture: 9 inputs -> 128 hidden -> 64 hidden -> 9 classes
    # We use partial_fit in a loop to monitor training metrics per epoch.
    clf = MLPClassifier(
        hidden_layer_sizes=(128, 64),
        activation='relu',
        solver='adam',
        max_iter=1,  # We will call partial_fit to monitor training per epoch
        random_state=42,
        warm_start=True
    )
    
    classes = np.arange(9)
    history = []
    start_time = time.time()
    
    print("Training MLPClassifier neural network...")
    best_val_acc = 0.0
    best_clf_state = None
    
    for epoch in range(1, epochs + 1):
        # partial_fit on training data
        clf.partial_fit(X_train, y_train, classes=classes)
        
        # Calculate loss and accuracies
        train_loss = clf.loss_
        train_acc = clf.score(X_train, y_train)
        val_acc = clf.score(X_val, y_val)
        
        history.append({
            "epoch": epoch,
            "loss": float(train_loss),
            "accuracy": float(train_acc),
            "val_accuracy": float(val_acc)
        })
        
        # Track best model (early stopping logic — save best weights)
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            # Save a copy of the model at best validation accuracy
            best_clf_state = joblib.dumps(clf)
        
        # Print progress
        if epoch % 5 == 0 or epoch == 1 or epoch == epochs:
            print(f"Epoch {epoch}/{epochs}")
            print(f"Loss: {train_loss:.4f}")
            print(f"Accuracy: {int(train_acc * 100)}%")
            print(f"Val Accuracy: {int(val_acc * 100)}%")
            print("-" * 20)
            
    total_train_time = time.time() - start_time
    
    # Restore best model if we tracked one
    if best_clf_state is not None:
        clf = joblib.loads(best_clf_state)
        
    final_acc = float(clf.score(X_val, y_val))
    print(f"Training completed in {total_train_time:.1f}s. Best Val Accuracy: {final_acc*100:.1f}%")
    
    # Save the model
    model_path = os.path.join("models", "fanoron.joblib")
    joblib.dump(clf, model_path)
    print(f"Model saved to {model_path}")
    
    # Save metrics
    metrics = {
        "accuracy": final_acc,
        "epochs": epochs,
        "training_time_sec": total_train_time,
        "dataset_size": len(df)
    }
    metrics_path = os.path.join("models", "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
        
    # Save training history
    history_path = os.path.join("models", "training_history.json")
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)
        
    return metrics

if __name__ == "__main__":
    # Generate 10,000 games of self play
    generate_selfplay_data(num_games=10000)
    # Train for 50 epochs
    train_model(epochs=50)
