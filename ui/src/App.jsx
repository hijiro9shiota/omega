import { useCallback, useEffect, useMemo, useState } from 'react';
import AnalyzePanel from './components/AnalyzePanel.jsx';
import LayersToggles from './components/LayersToggles.jsx';
import RealtimeChart from './components/RealtimeChart.jsx';
import SearchBar from './components/SearchBar.jsx';
import SignalCard from './components/SignalCard.jsx';
import Toaster from './components/Toaster.jsx';
import { analyzeSymbol, fetchHistory, fetchLive } from './lib/apiClient.js';
import { createSymbolIndex } from './lib/symbolIndex.js';

const INITIAL_TIMEFRAMES = ['4h', '1h', '15m', '5m'];
const DEFAULT_LAYERS_STATE = {
  order_block: true,
  liquidity: true,
  fvg: false,
  microstructure: false
};

export default function App() {
  const [symbolIndex, setSymbolIndex] = useState(null);
  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const [timeframes, setTimeframes] = useState(INITIAL_TIMEFRAMES);
  const [activeTimeframe, setActiveTimeframe] = useState('1h');
  const [candles, setCandles] = useState([]);
  const [livePrice, setLivePrice] = useState(null);
  const [signals, setSignals] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [lookback, setLookback] = useState(600);
  const [lastRun, setLastRun] = useState(null);
  const [layers, setLayers] = useState(DEFAULT_LAYERS_STATE);

  useEffect(() => {
    createSymbolIndex().then(setSymbolIndex);
  }, []);

  useEffect(() => {
    if (!timeframes.includes(activeTimeframe) && timeframes.length > 0) {
      setActiveTimeframe(timeframes[0]);
    }
  }, [timeframes, activeTimeframe]);

  const pushToast = useCallback((type, title, description) => {
    setToasts((prev) => [
      ...prev,
      {
        id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
        type,
        title,
        description
      }
    ]);
  }, []);

  const dismissToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  useEffect(() => {
    if (!selectedSymbol) {
      setCandles([]);
      setLivePrice(null);
      return;
    }
    let cancelled = false;
    async function loadHistory() {
      try {
        const data = await fetchHistory(selectedSymbol.symbol, activeTimeframe, 1000);
        if (!cancelled) {
          setCandles(data);
        }
      } catch (err) {
        console.warn('history error', err);
        if (!cancelled) {
          pushToast('error', 'Historique indisponible', err.message);
        }
      }
    }
    loadHistory();
    return () => {
      cancelled = true;
    };
  }, [selectedSymbol, activeTimeframe, pushToast]);

  useEffect(() => {
    if (!selectedSymbol) return undefined;
    let cancelled = false;
    async function poll() {
      try {
        const live = await fetchLive(selectedSymbol.symbol, activeTimeframe);
        if (!cancelled) {
          setLivePrice(live);
        }
      } catch (err) {
        if (!cancelled) {
          pushToast('error', 'Flux live indisponible', err.message);
        }
      }
    }
    poll();
    const interval = setInterval(poll, 30_000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [selectedSymbol, activeTimeframe, pushToast]);

  const handleAnalyze = useCallback(async () => {
    if (!selectedSymbol) return;
    setIsAnalyzing(true);
    try {
      const response = await analyzeSymbol({
        symbol: selectedSymbol.symbol,
        timeframes,
        lookback,
        layers: Object.entries(layers)
          .filter(([, enabled]) => enabled)
          .map(([key]) => key)
      });
      setSignals(response.signals ?? []);
      if (response.generated_at) {
        setLastRun(new Date(response.generated_at).toLocaleTimeString('fr-FR'));
      }
      pushToast('success', 'Analyse terminée', `${response.signals?.length ?? 0} signal(s) détectés`);
    } catch (err) {
      console.error('analyze failed', err);
      pushToast('error', 'Analyse impossible', err.message);
    } finally {
      setIsAnalyzing(false);
    }
  }, [selectedSymbol, timeframes, lookback, layers, pushToast]);

  const handleReasonHighlight = useCallback((signalId, reason) => {
    pushToast('info', reason.label, reason.detail ?? `Signal ${signalId}`);
  }, [pushToast]);

  const activeLayers = useMemo(() => layers, [layers]);

  return (
    <div className="mx-auto flex min-h-screen max-w-6xl flex-col gap-6 px-6 py-8">
      <header className="flex flex-col gap-2">
        <p className="text-xs uppercase tracking-[0.35em] text-primary-300">Oryon Lot 4</p>
        <h1 className="text-3xl font-semibold text-slate-100">Console d'analyse institutionnelle</h1>
        <p className="text-sm text-slate-400">
          Analyse multi-actifs 100 % locale. Combinez structure de marché, liquidité et risk management pour dériver des
          signaux explicables.
        </p>
      </header>
      <main className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-1">
          <SearchBar
            symbolIndex={symbolIndex}
            selectedSymbol={selectedSymbol}
            onSymbolSelect={(symbol) => {
              setSelectedSymbol(symbol);
              setActiveTimeframe((prev) => (timeframes.includes(prev) ? prev : timeframes[0]));
              pushToast('info', 'Symbole sélectionné', `${symbol.symbol} @ ${symbol.exchange}`);
            }}
            timeframes={timeframes}
            onTimeframesChange={(list) => setTimeframes(list)}
            onQueryFeedback={(payload) =>
              pushToast(payload.type ?? 'info', payload.title ?? 'Recherche', payload.message)
            }
          />
          <AnalyzePanel
            selectedSymbol={selectedSymbol}
            timeframes={timeframes}
            activeTimeframe={activeTimeframe}
            onActiveTimeframeChange={setActiveTimeframe}
            onAnalyze={handleAnalyze}
            isAnalyzing={isAnalyzing}
            lookback={lookback}
            onLookbackChange={setLookback}
            lastRun={lastRun}
          />
          <LayersToggles
            layers={layers}
            onToggle={(key, value) => setLayers((prev) => ({ ...prev, [key]: value }))}
          />
        </div>
        <div className="lg:col-span-2 space-y-4">
          <RealtimeChart
            symbol={selectedSymbol?.symbol}
            timeframe={activeTimeframe}
            candles={candles}
            livePrice={livePrice}
            signals={signals}
            activeLayers={activeLayers}
          />
          {signals.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {signals.map((signal) => (
                <SignalCard key={signal.id} signal={signal} onHighlight={handleReasonHighlight} />
              ))}
            </div>
          ) : (
            <div className="glass-panel rounded-3xl px-6 py-10 text-center text-sm text-slate-400">
              Lancez une analyse pour générer des signaux multi-timeframes. Les overlays s'afficheront sur le graphe en temps
              réel.
            </div>
          )}
        </div>
      </main>
      <footer className="py-6 text-center text-[11px] uppercase tracking-widest text-slate-600">
        Oryon tourne localement · Aucune donnée n'est envoyée vers des services externes.
      </footer>
      <Toaster messages={toasts} onDismiss={dismissToast} />
    </div>
  );
}
