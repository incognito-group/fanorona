import React, { useState } from 'react';
import GameHeader from './components/GameHeader';
import MainMenu from './components/MainMenu';
import WinAlert from './components/WinAlert';
import GameBoard from './components/GameBoard';
import { ADJACENCY_MAP } from './constants/gameRules';
import { checkWinCondition } from './core/gameLogic';

export default function App() {
  const [gameMode, setGameMode] = useState(null); 
  const [board, setBoard] = useState(Array(9).fill(null));
  const [currentPlayer, setCurrentPlayer] = useState('P1'); 
  const [gamePhase, setGamePhase] = useState('Placement'); 
  const [selectedPiece, setSelectedPiece] = useState(null);
  const [winner, setWinner] = useState(null);

  const triggerAIMove = async (currentBoard, currentPhase) => {
    try {
      const response = await fetch('/api/get-move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          board1D: currentBoard,
          difficulty: 'difficile', 
          phase: currentPhase === 'Placement' ? 1 : 2,
          aiPlayer: 2 
        })
      });

      const data = await response.json();
      if (!data.hasMove) return;

      const nextBoard = [...currentBoard];

      if (currentPhase === 'Placement') {
        nextBoard[data.index] = 'P2';
        setBoard(nextBoard);
        
        if (checkWinCondition(nextBoard, 'P2')) {
          setWinner('P2');
          return;
        }
        
        const totalPieces = nextBoard.filter(cell => cell !== null).length;
        if (totalPieces === 6) {
          setGamePhase('Movement');
        }
        
        setCurrentPlayer('P1');
      } else {
        nextBoard[data.fromIndex] = null;
        nextBoard[data.toIndex] = 'P2';
        setBoard(nextBoard);

        if (checkWinCondition(nextBoard, 'P2')) {
          setWinner('P2');
          return;
        }
        
        setCurrentPlayer('P1');
      }
    } catch (error) {
      console.error("Failed to fetch AI move:", error);
    }
  };

  const handleNodeClick = (index) => {
    // Bloquer les clics si la partie est finie ou si c'est au tour de l'IA
    if (winner || (gameMode === 'ai' && currentPlayer === 'P2')) return;
    
    if (gamePhase === 'Placement') handlePlacement(index);
    else if (gamePhase === 'Movement') handleMovement(index);
  };

  const handlePlacement = (index) => {
    if (board[index] !== null) return;

    const newBoard = [...board];
    newBoard[index] = currentPlayer;
    setBoard(newBoard);

    if (checkWinCondition(newBoard, currentPlayer)) {
      setWinner(currentPlayer);
      return;
    }

    // Correction de calcul : utiliser l'état du nouveau plateau simulé
    const updatedTotalPlaced = newBoard.filter(cell => cell !== null).length;
    let nextPhase = gamePhase;
    if (updatedTotalPlaced === 6) {
      nextPhase = 'Movement';
      setGamePhase('Movement');
    }

    if (gameMode === 'ai') {
      // C'est au tour de l'IA, on passe à P2 et on déclenche l'appel API immédiatement
      setCurrentPlayer('P2');
      triggerAIMove(newBoard, nextPhase);
    } else {
      // Mode local classique à 2 joueurs
      setCurrentPlayer(currentPlayer === 'P1' ? 'P2' : 'P1');
    }
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

    if (clickedCell === null) {
      const validMoves = ADJACENCY_MAP[selectedPiece];
      if (validMoves.includes(index)) {
        const newBoard = [...board];
        newBoard[selectedPiece] = null;
        newBoard[index] = currentPlayer;
        setBoard(newBoard);
        setSelectedPiece(null);

        if (checkWinCondition(newBoard, currentPlayer)) {
          setWinner(currentPlayer);
          return;
        }

        if (gameMode === 'ai') {
          setCurrentPlayer('P2');
          triggerAIMove(newBoard, gamePhase);
        } else {
          setCurrentPlayer(currentPlayer === 'P1' ? 'P2' : 'P1');
        }
      }
    } else if (clickedCell === currentPlayer) {
      setSelectedPiece(index);
    }
  };

  const resetGame = () => {
    setBoard(Array(9).fill(null));
    setCurrentPlayer('P1');
    setGamePhase('Placement');
    setSelectedPiece(null);
    setWinner(null);
  };

  return (
    <div className="w-full max-w-4xl flex flex-col items-center gap-8 py-8 px-4 bg-zinc-50 min-h-screen text-zinc-800">
      <GameHeader />

      {gameMode === null ? (
        <MainMenu onSelectMode={setGameMode} />
      ) : (
        <main className="w-full max-w-md flex flex-col items-center bg-white border border-zinc-200 rounded-lg p-6 shadow-sm animate-[fadeIn_0.4s_ease-out]">
          <WinAlert winner={winner} />

          <div className="w-full flex justify-between items-center mb-6 text-sm font-mono">
            <div>
              <span className="text-zinc-400">Phase:</span>{' '}
              <span className="text-zinc-700 font-semibold uppercase">{gamePhase}</span>
            </div>
            {!winner && (
              <div>
                <span className="text-zinc-400">Tour:</span>{' '}
                <span className={`font-bold ${currentPlayer === 'P1' ? 'text-emerald-600' : 'text-zinc-800'}`}>
                  {currentPlayer === 'P1' ? 'Joueur 1 (Vert)' : 'Joueur 2 (IA / Noir)'}
                </span>
              </div>
            )}
          </div>

          <GameBoard 
            board={board} 
            selectedPiece={selectedPiece} 
            onNodeClick={handleNodeClick} 
          />

          <div className="w-full flex gap-3 mt-6">
            <button
              onClick={resetGame}
              className="flex-1 py-2 bg-white border border-zinc-200 hover:bg-zinc-50 text-zinc-600 text-xs font-mono rounded uppercase tracking-wider transition-colors"
            >
              Recommencer
            </button>
            <button
              onClick={() => { resetGame(); setGameMode(null); }}
              className="px-4 py-2 bg-zinc-100 hover:bg-zinc-200 text-zinc-500 text-xs font-mono rounded uppercase tracking-wider transition-colors"
            >
              Menu
            </button>
          </div>
        </main>
      )}
    </div>
  );
}
