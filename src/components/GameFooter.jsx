import React from 'react';

export default function GameFooter() {
  return (
    <footer className="w-full flex flex-col md:flex-row items-center justify-between gap-4 border-t border-zinc-200 pt-4 text-xs tracking-wider text-zinc-500 uppercase font-mono">
      {/* Informations Institutionnelles & Équipe */}
      <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-3 text-center sm:text-left">
        <div className="flex items-center gap-2">
          <span className="text-zinc-600 font-semibold font-sans">TEAM INCOGNITO</span>
        </div>
        <span className="hidden sm:inline text-zinc-300">:</span>
        <span className="text-[10px] text-zinc-400 italic">
          Princy, Nambinintsoa, Ny Avo, Safidy, Sarobidi
        </span>
      </div>
    </footer>
  );
}
