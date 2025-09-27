export function overlaysByKind(signals = []) {
  const map = new Map();
  signals.forEach((signal) => {
    signal.overlays.forEach((overlay) => {
      const items = map.get(overlay.kind) ?? [];
      items.push({ ...overlay.payload, signalId: signal.id, timeframe: signal.timeframe });
      map.set(overlay.kind, items);
    });
  });
  return map;
}

export function tradeLevels(signals = []) {
  return signals.flatMap((signal) => {
    const base = [
      { label: 'Entry', price: signal.entry, color: 'rgba(56,189,248,0.6)' },
      { label: 'Stop', price: signal.stop_loss, color: 'rgba(248,113,113,0.7)' }
    ];
    const tps = signal.take_profits.map((price, index) => ({
      label: `TP${index + 1}`,
      price,
      color: 'rgba(74,222,128,0.7)'
    }));
    return [...base, ...tps].map((item) => ({ ...item, id: `${signal.id}-${item.label}` }));
  });
}

export function formatOverlayLabel(item) {
  if (!item) return '';
  if (item.kind === 'liquidity') {
    return `${item.payload?.kind ?? 'Liquidity'} @ ${item.payload?.level ?? ''}`;
  }
  if (item.kind === 'order_block') {
    return `${item.payload?.direction ?? 'OB'} block`;
  }
  return item.kind;
}
