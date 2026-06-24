import { ADJACENCY_MAP, WINNING_LINES } from '../constants/gameRules.js';

const opponentOf = (player) => (player === 'P1' ? 'P2' : 'P1');

export const checkWinCondition = (currentBoard, player) => (
  WINNING_LINES.some((line) => line.every((index) => currentBoard[index] === player))
);

export const isValidMove = (fromIndex, toIndex) => {
  const validMoves = ADJACENCY_MAP[fromIndex];
  return validMoves ? validMoves.includes(toIndex) : false;
};

export const getNextPhase = (board, phase) => (
  phase === 'Placement' && board.filter(Boolean).length >= 6 ? 'Movement' : phase
);

export const getLegalMoves = (board, player, phase) => {
  if (phase === 'Placement') {
    return board
      .map((cell, index) => (cell === null ? { type: 'placement', index } : null))
      .filter(Boolean);
  }

  return board.flatMap((cell, fromIndex) => {
    if (cell !== player) return [];

    return ADJACENCY_MAP[fromIndex]
      .filter((toIndex) => board[toIndex] === null)
      .map((toIndex) => ({ type: 'movement', fromIndex, toIndex }));
  });
};

export const applyMoveToBoard = (board, move, player) => {
  const nextBoard = [...board];

  if (move.type === 'placement') {
    nextBoard[move.index] = player;
  } else {
    nextBoard[move.fromIndex] = null;
    nextBoard[move.toIndex] = player;
  }

  return nextBoard;
};

const scoreLine = (board, line, player) => {
  const opponent = opponentOf(player);
  const ownCount = line.filter((index) => board[index] === player).length;
  const opponentCount = line.filter((index) => board[index] === opponent).length;
  const emptyCount = line.filter((index) => board[index] === null).length;

  if (ownCount === 3) return 1000;
  if (opponentCount === 3) return -1000;
  if (ownCount === 2 && emptyCount === 1) return 60;
  if (opponentCount === 2 && emptyCount === 1) return -70;
  if (ownCount === 1 && emptyCount === 2) return 8;
  if (opponentCount === 1 && emptyCount === 2) return -8;
  return 0;
};

const evaluateBoard = (board, player, phase) => {
  if (checkWinCondition(board, player)) return 1000;
  if (checkWinCondition(board, opponentOf(player))) return -1000;

  const lineScore = WINNING_LINES.reduce(
    (score, line) => score + scoreLine(board, line, player),
    0,
  );
  const centerScore = board[4] === player ? 20 : board[4] === opponentOf(player) ? -20 : 0;
  const mobilityScore = phase === 'Movement'
    ? (getLegalMoves(board, player, phase).length - getLegalMoves(board, opponentOf(player), phase).length) * 4
    : 0;

  return lineScore + centerScore + mobilityScore;
};

const findImmediateMove = (board, player, phase) => (
  getLegalMoves(board, player, phase).find((move) => (
    checkWinCondition(applyMoveToBoard(board, move, player), player)
  ))
);

const chooseRandomMove = (moves) => moves[Math.floor(Math.random() * moves.length)];

const chooseMediumMove = (board, player, phase) => {
  const legalMoves = getLegalMoves(board, player, phase);
  const winningMove = findImmediateMove(board, player, phase);
  if (winningMove) return winningMove;

  const blockingMove = findImmediateMove(board, opponentOf(player), phase);
  if (blockingMove) {
    return legalMoves.find((move) => {
      if (phase === 'Placement') return move.index === blockingMove.index;
      return move.toIndex === blockingMove.toIndex;
    }) || chooseRandomMove(legalMoves);
  }

  if (phase === 'Placement' && board[4] === null) {
    return { type: 'placement', index: 4 };
  }

  return chooseRandomMove(legalMoves);
};

const minimax = (board, playerToMove, aiPlayer, phase, depth, alpha, beta) => {
  if (checkWinCondition(board, aiPlayer)) return 1000 + depth;
  if (checkWinCondition(board, opponentOf(aiPlayer))) return -1000 - depth;
  if (depth === 0) return evaluateBoard(board, aiPlayer, phase);

  const legalMoves = getLegalMoves(board, playerToMove, phase);
  if (legalMoves.length === 0) return evaluateBoard(board, aiPlayer, phase);

  const isMaximizing = playerToMove === aiPlayer;
  let bestScore = isMaximizing ? -Infinity : Infinity;

  for (const move of legalMoves) {
    const nextBoard = applyMoveToBoard(board, move, playerToMove);
    const nextPhase = getNextPhase(nextBoard, phase);
    const score = minimax(
      nextBoard,
      opponentOf(playerToMove),
      aiPlayer,
      nextPhase,
      depth - 1,
      alpha,
      beta,
    );

    if (isMaximizing) {
      bestScore = Math.max(bestScore, score);
      alpha = Math.max(alpha, score);
    } else {
      bestScore = Math.min(bestScore, score);
      beta = Math.min(beta, score);
    }

    if (beta <= alpha) break;
  }

  return bestScore;
};

const chooseHardMove = (board, player, phase) => {
  const legalMoves = getLegalMoves(board, player, phase);
  const openingMove = phase === 'Placement' && board[4] === null
    ? { type: 'placement', index: 4 }
    : null;

  if (openingMove) return openingMove;

  const depth = phase === 'Placement' ? 6 : 8;
  let bestMove = legalMoves[0];
  let bestScore = -Infinity;

  for (const move of legalMoves) {
    const nextBoard = applyMoveToBoard(board, move, player);
    const nextPhase = getNextPhase(nextBoard, phase);
    const score = minimax(
      nextBoard,
      opponentOf(player),
      player,
      nextPhase,
      depth - 1,
      -Infinity,
      Infinity,
    );

    if (score > bestScore) {
      bestScore = score;
      bestMove = move;
    }
  }

  return bestMove;
};

export const chooseAIMove = (board, player, phase, difficulty) => {
  const legalMoves = getLegalMoves(board, player, phase);
  if (legalMoves.length === 0) return null;

  if (difficulty === 'facile') return chooseRandomMove(legalMoves);
  if (difficulty === 'moyenne') return chooseMediumMove(board, player, phase);
  return chooseHardMove(board, player, phase);
};
