import { useEffect, useState } from 'react';

export default function AnalyzePanel({
  selectedSymbol,
  timeframes,
  activeTimeframe,
  onActiveTimeframeChange,
  onAnalyze,
  isAnalyzing,
  lookback,
  onLookbackChange,
  lastRun
}) {
  const [hoveredTf, setHoveredTf] = useState(null);

  useEffect(() => {
    setHoveredTf(null);
  }, [selectedSymbol]);

  return (
    <div className="glass-panel rounded-3xl px-6 py-5 space-y-4">
      <header className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-500">Analyse multi-timeframes</p>
          <h2 className="text-lg font-semibold text-slate-100">
            {selectedSymbol ? selectedSymbol.symbol : 'Choisissez un symbole'}
          </h2>
        </div>
        <div className="text-right text-[11px] text-slate-400">
          <p>{timeframes.length} timeframes actives</p>
          {lastRun && <p>Dernière analyse {lastRun}</p>}
        </div>
      </header>
      <div>
        <label className="text-xs uppercase tracking-widest text-slate-500">Fenêtre de lookback (bougies)</label>
        <input
          type="range"
          min="200"
          max="2000"
          step="100"
          value={lookback}
          onChange={(event) => onLookbackChange(Number(event.target.value))}
          className="mt-2 w-full accent-primary-500"
        />
        <p className="mt-1 text-xs text-slate-400">{lookback} bougies / timeframe</p>
      </div>
      <div className="rounded-2xl border border-slate-700/60 bg-slate-900/70 px-4 py-3 text-xs text-slate-300">
        <p>
          Les signaux sont déclenchés uniquement lorsque les biais HTF, la structure LTF et le profil de liquidité sont
          alignés. Le score pénalise les ranges sans direction et les setups dont le ratio rendement/risque est insuffisant.
        </p>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex flex-wrap gap-2 text-xs text-slate-400">
          {timeframes.map((tf) => (
            <span
              key={tf}
              role="button"
              tabIndex={0}
              className={`tag-chip cursor-pointer border ${
                activeTimeframe === tf
                  ? 'border-primary-500/80 bg-primary-600/40 text-primary-100'
                  : 'border-transparent'
              } ${hoveredTf === tf ? 'bg-primary-600/20 text-primary-100' : ''}`}
              onMouseEnter={() => setHoveredTf(tf)}
              onMouseLeave={() => setHoveredTf(null)}
              onClick={() => onActiveTimeframeChange?.(tf)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  onActiveTimeframeChange?.(tf);
                }
              }}
            >
              {tf}
            </span>
          ))}
        </div>
        <button
          type="button"
          disabled={!selectedSymbol || isAnalyzing || timeframes.length === 0}
          onClick={onAnalyze}
          className="rounded-2xl border border-primary-600/60 bg-primary-600/10 px-6 py-2 text-sm font-semibold uppercase tracking-wide text-primary-100 transition hover:bg-primary-600/20 disabled:cursor-not-allowed disabled:border-slate-700 disabled:text-slate-500"
        >
          {isAnalyzing ? 'Analyse en cours…' : 'Analyser'}
        </button>
      </div>
    </div>
  );
}
