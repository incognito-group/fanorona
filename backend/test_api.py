"""
API integration tests for Fanoron-telo backend.
Run with: python -m pytest test_api.py -v

Requires: pip install httpx  (for FastAPI TestClient async support)
"""
import pytest
from fastapi.testclient import TestClient
from main import app, active_game


@pytest.fixture(autouse=True)
def reset_game():
    """Reset the game state before each test."""
    active_game.reset()
    yield
    active_game.reset()


client = TestClient(app)


# ─── Game Endpoints ───

class TestNewGame:
    def test_new_game_returns_200(self):
        response = client.post("/game/new")
        assert response.status_code == 200

    def test_new_game_returns_empty_board(self):
        response = client.post("/game/new")
        data = response.json()
        assert data["board"] == [0] * 9
        assert data["current_player"] == 1
        assert data["phase"] == "placement"
        assert data["winner"] is None

    def test_new_game_has_nine_legal_moves(self):
        response = client.post("/game/new")
        data = response.json()
        assert len(data["legal_moves"]) == 9


class TestGetState:
    def test_get_state_returns_current(self):
        client.post("/game/new")
        response = client.get("/game/state")
        assert response.status_code == 200
        data = response.json()
        assert data["board"] == [0] * 9


class TestPlayMove:
    def test_placement_move(self):
        client.post("/game/new")
        response = client.post("/game/play", json={"cell": 4})
        assert response.status_code == 200
        data = response.json()
        assert data["board"][4] == 1
        assert data["current_player"] == 2

    def test_movement_with_from_to(self):
        """Test Phase 2 movement with explicit from/to cells."""
        client.post("/game/new")
        # Setup: Place 6 pieces without alignment
        placements = [0, 3, 1, 5, 8, 7]
        for cell in placements:
            client.post("/game/play", json={"cell": cell})
        
        # Now in movement phase, move P1 piece from 1 to 4
        response = client.post("/game/play", json={"from_cell": 1, "to_cell": 4})
        assert response.status_code == 200
        data = response.json()
        assert data["board"][1] == 0
        assert data["board"][4] == 1

    def test_illegal_move_returns_400(self):
        client.post("/game/new")
        client.post("/game/play", json={"cell": 4})
        # Try placing on occupied cell
        response = client.post("/game/play", json={"cell": 4})
        assert response.status_code == 400

    def test_play_after_game_over_returns_400(self):
        client.post("/game/new")
        # P1 wins with row 0
        client.post("/game/play", json={"cell": 0})
        client.post("/game/play", json={"cell": 3})
        client.post("/game/play", json={"cell": 1})
        client.post("/game/play", json={"cell": 4})
        client.post("/game/play", json={"cell": 2})  # P1 wins
        
        response = client.post("/game/play", json={"cell": 5})
        assert response.status_code == 400

    def test_empty_request_returns_400(self):
        client.post("/game/new")
        response = client.post("/game/play", json={})
        assert response.status_code == 400


class TestUndoRedo:
    def test_undo_after_move(self):
        client.post("/game/new")
        client.post("/game/play", json={"cell": 4})
        
        response = client.post("/game/undo")
        assert response.status_code == 200
        data = response.json()
        assert data["board"][4] == 0
        assert data["current_player"] == 1

    def test_undo_empty_returns_400(self):
        client.post("/game/new")
        response = client.post("/game/undo")
        assert response.status_code == 400

    def test_redo_after_undo(self):
        client.post("/game/new")
        client.post("/game/play", json={"cell": 4})
        client.post("/game/undo")
        
        response = client.post("/game/redo")
        assert response.status_code == 200
        data = response.json()
        assert data["board"][4] == 1

    def test_redo_empty_returns_400(self):
        client.post("/game/new")
        response = client.post("/game/redo")
        assert response.status_code == 400


# ─── AI Endpoints ───

class TestAiMove:
    def test_easy_ai_returns_move(self):
        client.post("/game/new")
        response = client.post("/ai/move", json={"difficulty": "easy"})
        assert response.status_code == 200
        data = response.json()
        assert "move" in data
        assert "confidence" in data
        assert "duration_ms" in data
        assert data["move"] in range(9)

    def test_medium_ai_returns_move(self):
        client.post("/game/new")
        response = client.post("/ai/move", json={"difficulty": "medium"})
        assert response.status_code == 200
        data = response.json()
        assert "move" in data
        assert data["depth_reached"] == 3

    def test_hard_ai_returns_move(self):
        client.post("/game/new")
        response = client.post("/ai/move", json={"difficulty": "hard"})
        assert response.status_code == 200
        data = response.json()
        assert "move" in data

    def test_invalid_difficulty_returns_400(self):
        client.post("/game/new")
        response = client.post("/ai/move", json={"difficulty": "impossible"})
        assert response.status_code == 400

    def test_ai_move_after_game_over(self):
        client.post("/game/new")
        # Play to win
        client.post("/game/play", json={"cell": 0})
        client.post("/game/play", json={"cell": 3})
        client.post("/game/play", json={"cell": 1})
        client.post("/game/play", json={"cell": 4})
        client.post("/game/play", json={"cell": 2})  # P1 wins
        
        response = client.post("/ai/move", json={"difficulty": "easy"})
        assert response.status_code == 400


# ─── Model Endpoints ───

class TestModelEndpoints:
    def test_model_history_returns_list(self):
        response = client.get("/model/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_training_status(self):
        response = client.get("/train/status")
        assert response.status_code == 200
        data = response.json()
        assert "running" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
