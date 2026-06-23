import React from 'react';

export default function App() {
  return (
    <div className="flex flex-col justify-between items-center min-h-screen p-6 bg-[#121214] font-sans antialiased">
      
      {/* Header */}
      <header className="w-full max-w-4xl flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-zinc-800 pb-4 text-xs tracking-wider text-zinc-400 uppercase">
        <div className="flex items-center gap-2">
          <span className="font-bold text-zinc-200">ISPM</span>
          <span className="text-zinc-200">|</span>
          <span>Travaux Pratiques</span>
        </div>
        <div className="text-zinc-200 font-mono">
          Matière : Algorithme avancé
        </div>
      </header>

      <main className="w-full max-w-xl my-auto p-8 bg-[#1a1a1e] border border-zinc-800 rounded-lg shadow-sm">
        {/* Wireframe Diagram */}
        <div className="flex justify-center mb-8">
          <div className="relative w-24 h-24 border border-zinc-700 bg-[#121214]">
            {/* Structural Alignment Lines */}
            <div className="absolute top-1/2 left-0 w-full h-[1px] bg-zinc-700 -translate-y-1/2"></div>
            <div className="absolute left-1/2 top-0 w-[1px] h-full bg-zinc-700 -translate-x-1/2"></div>
            <div className="absolute top-0 left-0 w-[141%] h-[1px] bg-zinc-700 rotate-45 origin-top-left"></div>
            <div className="absolute top-0 right-0 w-[141%] h-[1px] bg-zinc-700 -rotate-45 origin-top-right"></div>
            
            {/* Intersection Nodes */}
            <div className="absolute w-2 h-2 bg-zinc-500 rounded-full top-0 left-0 -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute w-2 h-2 bg-zinc-500 rounded-full top-0 left-1/2 -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute w-2 h-2 bg-zinc-500 rounded-full top-0 left-full -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute w-2 h-2 bg-zinc-500 rounded-full top-1/2 left-0 -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute w-2 h-2 bg-zinc-400 rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute w-2 h-2 bg-zinc-500 rounded-full top-1/2 left-full -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute w-2 h-2 bg-zinc-500 rounded-full top-full left-0 -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute w-2 h-2 bg-zinc-500 rounded-full top-full left-1/2 -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute w-2 h-2 bg-zinc-500 rounded-full top-full left-full -translate-x-1/2 -translate-y-1/2"></div>
          </div>
        </div>

        <h1 className="text-2xl font-semibold tracking-tight text-zinc-100 mb-2">
          Fanoron-3 
        </h1>

        <hr className="border-zinc-700 my-8" />

        {/* Console-style Status Bar */}
        <div className="bg-[#121214] border border-zinc-800 p-3 rounded font-mono text-xs text-left text-zinc-400 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
            <span>status: IN_DEVELOPMENT</span>
          </div>
          <span className="text-zinc-600">v1.0.0</span>
        </div>
      </main>
    </div>
  );
}
