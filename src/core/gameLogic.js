import { WINNING_LINES } from '../constants/gameRules';

export const checkWinCondition = (currentBoard, player) => {
  return WINNING_LINES.some(line => line.every(index => currentBoard[index] === player));
};

export const isValidMove = (fromIndex, toIndex) => {
  const validMoves = ADJACENCY_MAP[fromIndex];
  return validMoves ? validMoves.includes(toIndex) : false;
};