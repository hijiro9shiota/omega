import { useEffect, useMemo, useRef } from 'react';
import { createChart, CrosshairMode } from 'lightweight-charts';
import { overlaysByKind, tradeLevels } from '../lib/chartOverlays.js';

function toChartData(candles) {
  return candles.map((candle) => ({
    time: Math.floor(new Date(candle.timestamp).getTime() / 1000),
    open: Number(candle.open),
    high: Number(candle.high),
    low: Number(candle.low),
    close: Number(candle.close)
  }));
}

function toMarkers(overlaysMap, activeLayers) {
  const markers = [];
  if (activeLayers.liquidity && overlaysMap.has('liquidity')) {
    overlaysMap.get('liquidity').forEach((item) => {
      markers.push({
        time: Math.floor(new Date(item.start ?? item.timestamp ?? Date.now()).getTime() / 1000),
        position: 'aboveBar',
        shape: 'arrowDown',
        color: '#38bdf8',
        text: `${item.kind ?? 'LQ'} ${item.level ?? ''}`
      });
    });
  }
  if (activeLayers.order_block && overlaysMap.has('order_block')) {
    overlaysMap.get('order_block').forEach((item) => {
      markers.push({
        time: Math.floor(new Date(item.timestamp ?? Date.now()).getTime() / 1000),
        position: item.direction === 'long' ? 'belowBar' : 'aboveBar',
        shape: item.direction === 'long' ? 'arrowUp' : 'arrowDown',
        color: '#a855f7',
        text: `${item.direction === 'long' ? 'Bull' : 'Bear'} OB`
      });
    });
  }
  return markers;
}

export default function RealtimeChart({
  symbol,
  timeframe,
  candles,
  livePrice,
  signals,
  activeLayers
}) {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const priceLinesRef = useRef([]);

  const overlayMap = useMemo(() => overlaysByKind(signals), [signals]);

  useEffect(() => {
    if (!containerRef.current || chartRef.current) return;
    const chart = createChart(containerRef.current, {
      layout: {
        background: { color: 'rgba(2, 6, 23, 0)' },
        textColor: '#94a3b8',
        fontFamily: 'OryonRobot, Inter, system-ui'
      },
      crosshair: { mode: CrosshairMode.Magnet },
      grid: {
        vertLines: { color: 'rgba(148, 163, 184, 0.12)' },
        horzLines: { color: 'rgba(148, 163, 184, 0.12)' }
      },
      rightPriceScale: {
        borderColor: 'rgba(148,163,184,0.2)'
      },
      timeScale: {
        borderColor: 'rgba(148,163,184,0.2)'
      }
    });
    const series = chart.addCandlestickSeries({
      upColor: 'rgba(34,197,94,0.9)',
      downColor: 'rgba(248,113,113,0.9)',
      wickUpColor: 'rgba(34,197,94,0.9)',
      wickDownColor: 'rgba(248,113,113,0.9)',
      borderVisible: false
    });
    chartRef.current = { chart, series };
    const resizeObserver = new ResizeObserver((entries) => {
      entries.forEach((entry) => {
        chart.applyOptions({ width: entry.contentRect.width, height: entry.contentRect.height });
      });
    });
    resizeObserver.observe(containerRef.current);
    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!chartRef.current) return;
    const series = chartRef.current.series;
    series.setData(toChartData(candles));
    if (candles.length > 0) {
      chartRef.current.chart.timeScale().fitContent();
    }
  }, [candles]);

  useEffect(() => {
    if (!chartRef.current || !livePrice) return;
    const series = chartRef.current.series;
    const time = Math.floor(new Date(livePrice.timestamp ?? livePrice.received_at ?? Date.now()).getTime() / 1000);
    series.update({
      time,
      open: livePrice.open ?? livePrice.price,
      high: livePrice.high ?? livePrice.price,
      low: livePrice.low ?? livePrice.price,
      close: livePrice.price
    });
  }, [livePrice]);

  useEffect(() => {
    if (!chartRef.current) return;
    const series = chartRef.current.series;
    priceLinesRef.current.forEach((line) => series.removePriceLine(line));
    priceLinesRef.current = tradeLevels(signals).map((level) =>
      series.createPriceLine({
        price: level.price,
        color: level.color,
        lineStyle: 2,
        lineWidth: 2,
        axisLabelVisible: true,
        title: level.label
      })
    );
  }, [signals]);

  useEffect(() => {
    if (!chartRef.current) return;
    const series = chartRef.current.series;
    const markers = toMarkers(overlayMap, activeLayers);
    series.setMarkers(markers);
  }, [overlayMap, activeLayers]);

  return (
    <div className="glass-panel h-[460px] w-full rounded-3xl p-2">
      <header className="flex items-center justify-between px-4 py-2 text-xs uppercase tracking-widest text-slate-400">
        <span>{symbol ? `${symbol} · ${timeframe}` : 'Sélectionnez un symbole'}</span>
        <span>{signals.length > 0 ? `${signals.length} signal(s)` : 'En attente de signal'}</span>
      </header>
      <div ref={containerRef} className="h-[400px] w-full" />
    </div>
  );
}
