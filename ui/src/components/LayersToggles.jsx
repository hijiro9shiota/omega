const DEFAULT_LAYERS = [
  { key: 'order_block', label: 'Order Blocks' },
  { key: 'liquidity', label: 'Liquidité' },
  { key: 'fvg', label: 'FVG' },
  { key: 'microstructure', label: 'Microstructure' }
];

export default function LayersToggles({ layers, onToggle }) {
  return (
    <div className="glass-panel rounded-3xl px-6 py-4">
      <p className="text-xs uppercase tracking-widest text-slate-500 mb-3">Calques</p>
      <div className="flex flex-wrap gap-2">
        {DEFAULT_LAYERS.map((layer) => {
          const active = layers[layer.key];
          return (
            <button
              key={layer.key}
              type="button"
              onClick={() => onToggle(layer.key, !active)}
              className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
                active
                  ? 'border-accent-500/70 bg-accent-500/20 text-accent-100 shadow-neon'
                  : 'border-slate-700/70 text-slate-400 hover:border-accent-500/50 hover:text-accent-100'
              }`}
            >
              {layer.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
