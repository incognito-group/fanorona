export default function WinAlert({ winner }) {
  if (!winner) return null;

  return (
    <div className="w-full mb-6 bg-emerald-50 border border-emerald-200 rounded-lg p-4 text-center animate-[scaleIn_0.3s_ease-out]">
      <span className="text-emerald-700 font-bold uppercase tracking-wider block text-base">
        Félicitations !
      </span>
      <span className="text-xs font-mono text-emerald-600 mt-1 block">
        {winner === 'P1' ? 'Joueur 1 (Vert)' : 'Joueur 2 (Noir)'} a remporté la partie par alignement.
      </span>
    </div>
  );
}
