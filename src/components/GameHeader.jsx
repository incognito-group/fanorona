import React from 'react';

export default function GameHeader() {
  return (
    <header className="w-full flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-zinc-200 pb-4 text-xs tracking-wider text-zinc-500 uppercase">
      <div className="flex items-center gap-2">
        <span className="font-bold text-zinc-800">ISPM</span>
        <span className="text-zinc-300">|</span>
        <span>Travaux Pratiques</span>
      </div>
      <div className="text-zinc-400 font-mono">
        Algorithme avance | Fanoron-telo
      </div>
    </header>
  );
}