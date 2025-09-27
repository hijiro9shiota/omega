const DEFAULT_BASE = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE)
  ? import.meta.env.VITE_API_BASE
  : '/api';

const API_BASE = (DEFAULT_BASE || '/api').replace(/\/$/, '');

function buildUrl(path, params) {
  const url = new URL(`${API_BASE}${path}`, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value === undefined || value === null || value === '') return;
      url.searchParams.set(key, value);
    });
  }
  return url.toString();
}

async function httpGet(path, params) {
  const response = await fetch(buildUrl(path, params));
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `GET ${path} failed with status ${response.status}`);
  }
  return response.json();
}

async function httpPost(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `POST ${path} failed with status ${response.status}`);
  }
  return response.json();
}

export async function searchSymbolsRemote(query, limit = 10) {
  return httpGet('/search', { q: query, limit });
}

export async function fetchHistory(symbol, timeframe, limit = 1000) {
  return httpGet('/history', { symbol, timeframe, limit });
}

export async function fetchLive(symbol, timeframe = '1m') {
  return httpGet('/live', { symbol, timeframe });
}

export async function analyzeSymbol({ symbol, timeframes, lookback, layers }) {
  return httpPost('/analyze', {
    symbol,
    timeframes,
    lookback,
    layers
  });
}

export { API_BASE };
