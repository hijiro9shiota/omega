import { useEffect, useMemo, useState } from 'react';
import { searchSymbolsRemote } from '../lib/apiClient.js';

const AVAILABLE_TIMEFRAMES = ['1w', '1d', '12h', '4h', '1h', '30m', '15m', '5m', '1m'];

export default function SearchBar({
  symbolIndex,
  selectedSymbol,
  onSymbolSelect,
  timeframes,
  onTimeframesChange,
  onQueryFeedback
}) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (selectedSymbol) {
      setQuery(selectedSymbol.symbol);
    }
  }, [selectedSymbol]);

  useEffect(() => {
    let cancelled = false;
    async function run() {
      if (!query || query.length < 2) {
        setSuggestions([]);
        return;
      }
      const localMatches = symbolIndex?.search(query, 8) ?? [];
      setSuggestions(localMatches);
      setIsLoading(true);
      try {
        const remote = await searchSymbolsRemote(query, 12);
        if (!cancelled) {
          symbolIndex?.updateRecords(remote);
          const merged = symbolIndex?.search(query, 12) ?? [];
          setSuggestions(merged);
        }
      } catch (err) {
        console.warn('remote search failed', err);
        onQueryFeedback?.({ type: 'error', message: "Recherche distante indisponible" });
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }
    run();
    return () => {
      cancelled = true;
    };
  }, [query, symbolIndex, onQueryFeedback]);

  const timeframeChoices = useMemo(
    () =>
      AVAILABLE_TIMEFRAMES.map((tf) => ({
        value: tf,
        active: timeframes.includes(tf)
      })),
    [timeframes]
  );

  const toggleTimeframe = (tf) => {
    if (timeframes.includes(tf)) {
      onTimeframesChange(timeframes.filter((item) => item !== tf));
    } else {
      onTimeframesChange([...timeframes, tf]);
    }
  };

  return (
    <div className="glass-panel rounded-3xl px-6 py-4 space-y-4">
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Rechercher un symbole (ex: BTCUSDT, EURUSD, CAC40)"
            className="w-full rounded-2xl bg-slate-900/90 border border-slate-700/60 px-4 py-3 text-sm focus:ring-2 focus:ring-primary-500 focus:outline-none"
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-500">
            {isLoading ? '…' : '⏎'}
          </div>
        </div>
        <button
          type="button"
          className="rounded-2xl border border-primary-600/50 px-4 py-2 text-xs font-semibold text-primary-200 uppercase tracking-wide transition hover:bg-primary-600/20"
          onClick={() => {
            if (query && suggestions.length > 0) {
              onSymbolSelect(suggestions[0]);
            }
          }}
        >
          Sélection rapide
        </button>
      </div>
      {suggestions.length > 0 && (
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          {suggestions.map((item) => (
            <button
              key={item.symbol}
              type="button"
              onClick={() => onSymbolSelect(item)}
              className={`flex flex-col items-start rounded-2xl border border-slate-700/60 px-4 py-3 text-left transition hover:border-primary-500/80 hover:shadow-neon ${
                selectedSymbol?.symbol === item.symbol ? 'border-primary-500/80 bg-primary-600/10' : 'bg-slate-900/70'
              }`}
            >
              <span className="text-sm font-semibold tracking-wide text-slate-100">{item.symbol}</span>
              <span className="text-[11px] uppercase text-slate-400">{item.exchange} · {item.asset_type}</span>
            </button>
          ))}
        </div>
      )}
      <div>
        <p className="text-xs uppercase tracking-widest text-slate-500 mb-2">Timeframes</p>
        <div className="flex flex-wrap gap-2">
          {timeframeChoices.map(({ value, active }) => (
            <button
              key={value}
              type="button"
              onClick={() => toggleTimeframe(value)}
              className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
                active
                  ? 'border-primary-500/80 bg-primary-600/20 text-primary-100 shadow-neon'
                  : 'border-slate-700/70 text-slate-400 hover:border-primary-500/50 hover:text-primary-100'
              }`}
            >
              {value}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
