import { useEffect } from 'react';

export default function Toaster({ messages, onDismiss }) {
  useEffect(() => {
    if (!messages || messages.length === 0) return undefined;
    const timers = messages.map((message) =>
      setTimeout(() => onDismiss(message.id), message.duration ?? 4000)
    );
    return () => timers.forEach((timer) => clearTimeout(timer));
  }, [messages, onDismiss]);

  if (!messages || messages.length === 0) {
    return null;
  }

  return (
    <div className="pointer-events-none fixed bottom-6 right-6 z-50 flex w-80 flex-col gap-3">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`pointer-events-auto rounded-2xl border px-4 py-3 text-sm shadow-lg transition ${severityStyle(message.type)}`}
        >
          <p className="font-semibold">{message.title}</p>
          {message.description && <p className="text-xs text-slate-300">{message.description}</p>}
          <button
            type="button"
            className="mt-2 text-xs uppercase tracking-widest text-slate-400 hover:text-slate-200"
            onClick={() => onDismiss(message.id)}
          >
            Fermer
          </button>
        </div>
      ))}
    </div>
  );
}

function severityStyle(type = 'info') {
  if (type === 'error') {
    return 'border-rose-500/50 bg-rose-500/20 text-rose-100';
  }
  if (type === 'success') {
    return 'border-emerald-500/50 bg-emerald-500/20 text-emerald-100';
  }
  return 'border-slate-700/60 bg-slate-900/90 text-slate-100';
}
