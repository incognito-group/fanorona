import { useEffect, useMemo, useState } from 'react';
import GameHeader from './components/GameHeader';
import MainMenu from './components/MainMenu';
import WinAlert from './components/WinAlert';
import GameBoard from './components/GameBoard';
import {
  applyMoveToBoard,
  checkWinCondition,
  chooseAIMove,
  getLegalMoves,
  getNextPhase,
} from './core/gameLogic';
import GameFooter from './components/GameFooter';

const EMPTY_BOARD = Array(9).fill(null);
const PLAYER_LABELS = {
  P1: 'Joueur 1 (Vert)',
  P2: 'Joueur 2 (Noir)',
};

const toApiMove = (data, phase) => {
  if (!data?.hasMove) return null;

  if (phase === 'Placement') {
    return { type: 'placement', index: data.index };
  }

  return { type: 'movement', fromIndex: data.fromIndex, toIndex: data.toIndex };
};

export default function App() {
  const [gameMode, setGameMode] = useState(null);
  const [aiDifficulty, setAiDifficulty] = useState('moyenne');
  const [board, setBoard] = useState(EMPTY_BOARD);
  const [currentPlayer, setCurrentPlayer] = useState('P1');
  const [gamePhase, setGamePhase] = useState('Placement');
  const [selectedPiece, setSelectedPiece] = useState(null);
  const [winner, setWinner] = useState(null);
  const [history, setHistory] = useState([]);
  const [redoStack, setRedoStack] = useState([]);
  const [aiThinking, setAiThinking] = useState(false);
  const [lastAiStats, setLastAiStats] = useState(null);

  const isAiTurn = useMemo(() => (
    !winner && (
      (gameMode === 'ai' && currentPlayer === 'P2')
      || gameMode === 'demo'
    )
  ), [currentPlayer, gameMode, winner]);

  const snapshot = () => ({
    board,
    currentPlayer,
    gamePhase,
    selectedPiece,
    winner,
    lastAiStats,
  });

  const restoreSnapshot = (state) => {
    setBoard(state.board);
    setCurrentPlayer(state.currentPlayer);
    setGamePhase(state.gamePhase);
    setSelectedPiece(state.selectedPiece);
    setWinner(state.winner);
    setLastAiStats(state.lastAiStats);
  };

  const commitSnapshot = (state = snapshot()) => {
    setHistory((items) => [...items, state]);
    setRedoStack([]);
  };

  const finishMove = (move, player, sourceBoard = board, sourcePhase = gamePhase) => {
    const nextBoard = applyMoveToBoard(sourceBoard, move, player);
    const nextWinner = checkWinCondition(nextBoard, player) ? player : null;
    const nextPhase = getNextPhase(nextBoard, sourcePhase);

    setBoard(nextBoard);
    setGamePhase(nextPhase);
    setSelectedPiece(null);
    setWinner(nextWinner);

    if (!nextWinner) {
      setCurrentPlayer(player === 'P1' ? 'P2' : 'P1');
    }

    return { nextBoard, nextPhase, nextWinner };
  };

  const requestServerMove = async (sourceBoard, sourcePhase, player) => {
    const startedAt = performance.now();
    const response = await fetch('/api/get-move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        board1D: sourceBoard,
        difficulty: aiDifficulty,
        phase: sourcePhase === 'Placement' ? 1 : 2,
        aiPlayer: player === 'P1' ? 1 : 2,
      }),
    });

    if (!response.ok) {
      throw new Error(`AI API returned ${response.status}`);
    }

    const data = await response.json();
    return {
      move: toApiMove(data, sourcePhase),
      stats: {
        source: 'API Python',
        durationMs: data.durationMs ?? Math.round(performance.now() - startedAt),
      },
    };
  };

  const triggerAIMove = async (sourceBoard, sourcePhase, player) => {
    setAiThinking(true);
    const beforeAiMove = {
      board: sourceBoard,
      currentPlayer: player,
      gamePhase: sourcePhase,
      selectedPiece: null,
      winner: null,
      lastAiStats,
    };

    try {
      let move = null;
      let stats = null;

      try {
        const serverResult = await requestServerMove(sourceBoard, sourcePhase, player);
        move = serverResult.move;
        stats = serverResult.stats;
      } catch {
        const startedAt = performance.now();
        move = chooseAIMove(sourceBoard, player, sourcePhase, aiDifficulty);
        stats = {
          source: 'IA locale',
          durationMs: Math.round(performance.now() - startedAt),
        };
      }

      if (!move) return;

      commitSnapshot(beforeAiMove);
      finishMove(move, player, sourceBoard, sourcePhase);
      setLastAiStats(stats);
    } finally {
      setAiThinking(false);
    }
  };

  useEffect(() => {
    if (!isAiTurn || aiThinking) return undefined;

    const timer = window.setTimeout(() => {
      triggerAIMove(board, gamePhase, currentPlayer);
    }, gameMode === 'demo' ? 650 : 250);

    return () => window.clearTimeout(timer);
    // triggerAIMove is intentionally omitted: it is recreated per render and guarded by aiThinking/isAiTurn.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [aiThinking, board, currentPlayer, gameMode, gamePhase, isAiTurn]);

  const handlePlacement = (index) => {
    if (board[index] !== null) return;

    commitSnapshot();
    finishMove({ type: 'placement', index }, currentPlayer);
  };

  const handleMovement = (index) => {
    const clickedCell = board[index];

    if (selectedPiece === null) {
      if (clickedCell === currentPlayer) setSelectedPiece(index);
      return;
    }

    if (index === selectedPiece) {
      setSelectedPiece(null);
      return;
    }

    const move = { type: 'movement', fromIndex: selectedPiece, toIndex: index };
    const isLegal = getLegalMoves(board, currentPlayer, gamePhase).some((legalMove) => (
      legalMove.type === 'movement'
      && legalMove.fromIndex === move.fromIndex
      && legalMove.toIndex === move.toIndex
    ));

    if (clickedCell === null && isLegal) {
      commitSnapshot();
      finishMove(move, currentPlayer);
    } else if (clickedCell === currentPlayer) {
      setSelectedPiece(index);
    }
  };

  const handleNodeClick = (index) => {
    if (winner || isAiTurn || aiThinking) return;

    if (gamePhase === 'Placement') handlePlacement(index);
    else handleMovement(index);
  };

  const resetGame = (nextMode = gameMode) => {
    setGameMode(nextMode);
    setBoard(EMPTY_BOARD);
    setCurrentPlayer('P1');
    setGamePhase('Placement');
    setSelectedPiece(null);
    setWinner(null);
    setHistory([]);
    setRedoStack([]);
    setAiThinking(false);
    setLastAiStats(null);
  };

  const undoMove = () => {
    if (history.length === 0 || aiThinking) return;

    const previous = history[history.length - 1];
    setRedoStack((items) => [snapshot(), ...items]);
    setHistory((items) => items.slice(0, -1));
    restoreSnapshot(previous);
  };

  const redoMove = () => {
    if (redoStack.length === 0 || aiThinking) return;

    const [next, ...remaining] = redoStack;
    setHistory((items) => [...items, snapshot()]);
    setRedoStack(remaining);
    restoreSnapshot(next);
  };

  return (
    <div className="w-full max-w-4xl flex flex-col items-center gap-8 py-8 px-4 bg-zinc-50 min-h-screen text-zinc-800">
      <GameHeader />

      {gameMode === null ? (
        <MainMenu
          aiDifficulty={aiDifficulty}
          onDifficultyChange={setAiDifficulty}
          onSelectMode={(mode) => resetGame(mode)}
        />
      ) : (
        <main className="w-full max-w-md flex flex-col items-center bg-white border border-zinc-200 rounded-lg p-6 shadow-sm animate-[fadeIn_0.4s_ease-out]">
          <WinAlert winner={winner} />

          <div className="w-full grid grid-cols-2 gap-3 mb-6 text-sm font-mono">
            <div>
              <span className="text-zinc-400">Phase:</span>{' '}
              <span className="text-zinc-700 font-semibold uppercase">{gamePhase}</span>
            </div>
            <div className="text-right">
              <span className="text-zinc-400">Mode:</span>{' '}
              <span className="text-zinc-700 font-semibold uppercase">
                {gameMode === 'local' ? 'Local' : gameMode === 'demo' ? 'Demo IA' : aiDifficulty}
              </span>
            </div>
            {!winner && (
              <div className="col-span-2">
                <span className="text-zinc-400">Tour:</span>{' '}
                <span className={`font-bold ${currentPlayer === 'P1' ? 'text-emerald-600' : 'text-zinc-800'}`}>
                  {aiThinking ? 'Calcul IA...' : PLAYER_LABELS[currentPlayer]}
                </span>
              </div>
            )}
            {lastAiStats && (
              <div className="col-span-2 text-xs text-zinc-400">
                Derniere IA: {lastAiStats.source} - {lastAiStats.durationMs} ms
              </div>
            )}
          </div>

          <GameBoard
            board={board}
            disabled={isAiTurn || aiThinking}
            selectedPiece={selectedPiece}
            onNodeClick={handleNodeClick}
          />

          <div className="w-full grid grid-cols-2 gap-3 mt-6">
            <button
              onClick={undoMove}
              disabled={history.length === 0 || aiThinking}
              className="py-2 bg-white border border-zinc-200 hover:bg-zinc-50 disabled:opacity-40 disabled:hover:bg-white text-zinc-600 text-xs font-mono rounded uppercase tracking-wider transition-colors"
            >
              Undo
            </button>
            <button
              onClick={redoMove}
              disabled={redoStack.length === 0 || aiThinking}
              className="py-2 bg-white border border-zinc-200 hover:bg-zinc-50 disabled:opacity-40 disabled:hover:bg-white text-zinc-600 text-xs font-mono rounded uppercase tracking-wider transition-colors"
            >
              Redo
            </button>
            <button
              onClick={() => resetGame(gameMode)}
              className="py-2 bg-white border border-zinc-200 hover:bg-zinc-50 text-zinc-600 text-xs font-mono rounded uppercase tracking-wider transition-colors"
            >
              Recommencer
            </button>
            <button
              onClick={() => resetGame(null)}
              className="py-2 bg-zinc-100 hover:bg-zinc-200 text-zinc-500 text-xs font-mono rounded uppercase tracking-wider transition-colors"
            >
              Menu
            </button>
          </div>
        </main>
      )}

      <GameFooter />
    </div>
  );
}
