import React from 'react';

export default function MainMenu({ onSelectMode }) {
  return (
    <main className="w-full max-w-md flex flex-col items-center bg-white border border-zinc-200 rounded-lg p-8 shadow-sm my-auto transition-all duration-300">
      <h1 className="text-3xl font-bold tracking-tight text-zinc-900 mb-2 text-center">
        Fanoron-telo
      </h1>
      <p className="text-zinc-500 text-sm text-center mb-8 font-mono">
        Sélectionnez votre mode de jeu
      </p>

      <div className="w-full flex flex-col gap-4">
        <button
          onClick={() => onSelectMode('local')}
          className="w-full py-4 px-6 border border-zinc-200 hover:border-emerald-600 hover:bg-emerald-50/30 text-zinc-800 font-medium text-sm rounded-lg transition-all duration-200 text-left flex justify-between items-center group"
        >
          <span>Mode Local (2 Joueurs)</span>
          <span className="text-zinc-400 group-hover:text-emerald-600 font-mono text-xs transition-colors">&rarr;</span>
        </button>

        <button
          onClick={() => onSelectMode('ai')}
          className="w-full py-4 px-6 border border-zinc-200 hover:border-emerald-600 hover:bg-emerald-50/30 text-zinc-800 font-medium text-sm rounded-lg transition-all duration-200 text-left flex justify-between items-center group"
        >
          <div>
            <span>Contre l'Intelligence Artificielle</span>
            <span className="block text-xs text-zinc-400 font-normal mt-0.5 font-mono">Minimax / Alpha-Beta</span>
          </div>
          <span className="text-zinc-400 group-hover:text-emerald-600 font-mono text-xs transition-colors">&rarr;</span>
        </button>
      </div>
    </main>
  );
}