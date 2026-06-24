export default function GameBoard({ board, disabled, selectedPiece, onNodeClick }) {
  return (
    <div className="relative w-72 h-72 my-4 bg-zinc-50 border border-zinc-200 rounded p-4 flex items-center justify-center">
      <svg className="absolute inset-0 w-full h-full stroke-zinc-300 stroke-[2px] fill-none pointer-events-none">
        <line x1="16.66%" y1="16.66%" x2="83.33%" y2="16.66%" />
        <line x1="16.66%" y1="50%" x2="83.33%" y2="50%" />
        <line x1="16.66%" y1="83.33%" x2="83.33%" y2="83.33%" />

        <line x1="16.66%" y1="16.66%" x2="16.66%" y2="83.33%" />
        <line x1="50%" y1="16.66%" x2="50%" y2="83.33%" />
        <line x1="83.33%" y1="16.66%" x2="83.33%" y2="83.33%" />

        <line x1="16.66%" y1="16.66%" x2="83.33%" y2="83.33%" />
        <line x1="83.33%" y1="16.66%" x2="16.66%" y2="83.33%" />
      </svg>

      <div className="absolute inset-0 grid grid-cols-3 grid-rows-3 p-[10%]">
        {board.map((cell, index) => (
          <div key={index} className="flex items-center justify-center">
            <button
              disabled={disabled}
              onClick={() => onNodeClick(index)}
              className={`relative z-10 w-10 h-10 rounded-full border transition-all duration-150 flex items-center justify-center text-[10px] font-mono disabled:cursor-wait
                ${cell === 'P1' ? 'bg-emerald-600 border-emerald-600 text-white shadow-md' : ''}
                ${cell === 'P2' ? 'bg-zinc-900 border-zinc-900 text-white shadow-md' : ''}
                ${cell === null ? 'bg-white border-zinc-300 hover:border-zinc-400' : ''}
                ${selectedPiece === index ? 'ring-4 ring-emerald-500/30 border-emerald-600 scale-110 animate-[pulseScale_1.5s_infinite_ease-in-out]' : ''}
              `}
            >
              {cell === null && <span className="opacity-0 hover:opacity-40 text-zinc-400">{index}</span>}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
