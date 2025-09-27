const DEFAULT_INDEX_URL = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_SYMBOL_INDEX_URL)
  ? import.meta.env.VITE_SYMBOL_INDEX_URL
  : '/symbols-demo.json';

function normaliseRecord(record) {
  const symbol = record.symbol || record.ticker || '';
  return {
    symbol,
    exchange: record.exchange || record.venue || 'LOCAL',
    asset_type: record.asset_type || record.type || 'unknown',
    base: record.base || null,
    quote: record.quote || null,
    score: 0
  };
}

function stringScore(haystack, needle) {
  const h = haystack.toLowerCase();
  const n = needle.toLowerCase();
  if (!n) return 0;
  let score = 0;
  if (h === n) score += 5;
  if (h.startsWith(n)) score += 3;
  if (h.includes(n)) score += 1.5;
  const distance = levenshtein(h, n);
  score += Math.max(0, 3 - distance * 0.5);
  return score;
}

function levenshtein(a, b) {
  const matrix = Array.from({ length: a.length + 1 }, () => new Array(b.length + 1).fill(0));
  for (let i = 0; i <= a.length; i += 1) matrix[i][0] = i;
  for (let j = 0; j <= b.length; j += 1) matrix[0][j] = j;
  for (let i = 1; i <= a.length; i += 1) {
    for (let j = 1; j <= b.length; j += 1) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1,
        matrix[i][j - 1] + 1,
        matrix[i - 1][j - 1] + cost
      );
    }
  }
  return matrix[a.length][b.length];
}

export class SymbolIndex {
  constructor(records = []) {
    this.records = records.map(normaliseRecord);
    this.queryCache = new Map();
  }

  updateRecords(newRecords) {
    const merged = [...this.records];
    newRecords.forEach((record) => {
      const normalised = normaliseRecord(record);
      const existingIndex = merged.findIndex((item) => item.symbol === normalised.symbol);
      if (existingIndex >= 0) {
        merged[existingIndex] = { ...merged[existingIndex], ...normalised };
      } else {
        merged.push(normalised);
      }
    });
    this.records = merged;
    this.queryCache.clear();
  }

  search(query, limit = 10) {
    if (!query) return [];
    const key = `${query.toLowerCase()}::${limit}`;
    if (this.queryCache.has(key)) {
      return this.queryCache.get(key);
    }
    const scored = this.records
      .map((record) => ({
        ...record,
        score: stringScore(record.symbol, query) + stringScore(record.exchange, query) * 0.4
      }))
      .filter((record) => record.score > 0.25)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
    this.queryCache.set(key, scored);
    return scored;
  }
}

export async function createSymbolIndex(fetcher = window.fetch.bind(window)) {
  try {
    const response = await fetcher(DEFAULT_INDEX_URL, { cache: 'no-store' });
    if (!response.ok) {
      throw new Error('symbol index preload failed');
    }
    const payload = await response.json();
    return new SymbolIndex(payload.symbols || payload);
  } catch (err) {
    console.warn('[symbolIndex] fallback to empty index', err);
    return new SymbolIndex();
  }
}
