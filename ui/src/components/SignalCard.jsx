import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale/fr';

const directionColor = {
  long: 'text-emerald-300 border-emerald-500/60',
  short: 'text-rose-300 border-rose-500/60'
};

export default function SignalCard({ signal, onHighlight }) {
  const createdAt = signal.created_at ? new Date(signal.created_at) : new Date();
  const distance = formatDistanceToNow(createdAt, { locale: fr, addSuffix: true });
  return (
    <article className="glass-panel flex flex-col gap-3 rounded-3xl px-5 py-4">
      <header className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-500">{signal.timeframe}</p>
          <h3 className="text-lg font-semibold text-slate-100">{signal.symbol}</h3>
        </div>
        <span className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase ${directionColor[signal.direction]}`}>
          {signal.direction}
        </span>
      </header>
      <section className="grid grid-cols-2 gap-3 text-xs text-slate-300 sm:grid-cols-4">
        <Info label="Entrée" value={signal.entry} />
        <Info label="Stop" value={signal.stop_loss} />
        <Info label="RR" value={signal.rr.toFixed(2)} />
        <Info label="Score" value={signal.score.toFixed(2)} />
      </section>
      <section className="flex flex-wrap gap-2">
        {signal.take_profits.map((tp, index) => (
          <span key={`${signal.id}-tp-${index}`} className="tag-chip bg-emerald-500/10 text-emerald-200">
            TP{index + 1} → {tp.toFixed(4)}
          </span>
        ))}
      </section>
      <section className="flex flex-wrap gap-2">
        {signal.reasons.map((reason, index) => (
          <button
            key={`${signal.id}-reason-${index}`}
            type="button"
            className="tag-chip border border-primary-500/30 bg-primary-600/10 text-primary-100 hover:bg-primary-600/30"
            onClick={() => onHighlight?.(signal.id, reason)}
          >
            {reason.label}
            {reason.detail ? ` · ${reason.detail}` : ''}
          </button>
        ))}
      </section>
      <footer className="text-[11px] uppercase tracking-widest text-slate-500">{distance}</footer>
    </article>
  );
}

function Info({ label, value }) {
  return (
    <div>
      <p className="text-[10px] uppercase tracking-widest text-slate-500">{label}</p>
      <p className="text-sm font-semibold text-slate-100">{value}</p>
    </div>
  );
}
