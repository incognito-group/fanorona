const DIFFICULTIES = [
  { value: 'facile', label: 'Facile' },
  { value: 'moyenne', label: 'Moyenne' },
  { value: 'difficile', label: 'Difficile' },
];

export default function MainMenu({ aiDifficulty, onDifficultyChange, onSelectMode }) {
  return (
    <main className="w-full max-w-md flex flex-col items-center bg-white border border-zinc-200 rounded-lg p-8 shadow-sm my-auto transition-all duration-300">
      <h1 className="text-3xl font-bold tracking-tight text-zinc-900 mb-2 text-center">
        Fanoron-telo
      </h1>
      <p className="text-zinc-500 text-sm text-center mb-8 font-mono">
        Sélectionnez votre mode de jeu
      </p>

      <div className="w-full mb-5">
        <span className="block text-xs uppercase tracking-wider text-zinc-400 font-mono mb-2">
          Niveau IA
        </span>
        <div className="grid grid-cols-3 gap-2">
          {DIFFICULTIES.map((difficulty) => (
            <button
              key={difficulty.value}
              onClick={() => onDifficultyChange(difficulty.value)}
              className={`py-2 px-3 border text-xs font-mono rounded transition-colors ${
                aiDifficulty === difficulty.value
                  ? 'border-emerald-600 bg-emerald-50 text-emerald-700'
                  : 'border-zinc-200 bg-white text-zinc-500 hover:border-zinc-300'
              }`}
            >
              {difficulty.label}
            </button>
          ))}
        </div>
      </div>

      <div className="w-full flex flex-col gap-4">
        <button
          onClick={() => onSelectMode('local')}
          className="w-full py-4 px-6 border border-zinc-200 hover:border-emerald-600 hover:bg-emerald-50/30 text-zinc-800 font-medium text-sm rounded-lg transition-all duration-200 text-left flex justify-between items-center group"
        >
          <span>Humain vs Humain</span>
          <span className="text-zinc-400 group-hover:text-emerald-600 font-mono text-xs transition-colors">-&gt;</span>
        </button>

        <button
          onClick={() => onSelectMode('ai')}
          className="w-full py-4 px-6 border border-zinc-200 hover:border-emerald-600 hover:bg-emerald-50/30 text-zinc-800 font-medium text-sm rounded-lg transition-all duration-200 text-left flex justify-between items-center group"
        >
          <div>
            <span>Humain vs IA</span>
            <span className="block text-xs text-zinc-400 font-normal mt-0.5 font-mono">Facile / Moyenne / Difficile</span>
          </div>
          <span className="text-zinc-400 group-hover:text-emerald-600 font-mono text-xs transition-colors">-&gt;</span>
        </button>

        <button
          onClick={() => onSelectMode('demo')}
          className="w-full py-4 px-6 border border-zinc-200 hover:border-emerald-600 hover:bg-emerald-50/30 text-zinc-800 font-medium text-sm rounded-lg transition-all duration-200 text-left flex justify-between items-center group"
        >
          <div>
            <span>IA vs IA</span>
            <span className="block text-xs text-zinc-400 font-normal mt-0.5 font-mono">Mode demo automatique</span>
          </div>
          <span className="text-zinc-400 group-hover:text-emerald-600 font-mono text-xs transition-colors">-&gt;</span>
        </button>
      </div>
    </main>
  );
}
