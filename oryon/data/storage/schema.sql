PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS symbols (
    symbol TEXT PRIMARY KEY,
    exchange TEXT NOT NULL,
    type TEXT NOT NULL,
    base TEXT,
    quote TEXT,
    aliases JSON,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candles (
    symbol TEXT NOT NULL,
    tf TEXT NOT NULL,
    ts INTEGER NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    PRIMARY KEY (symbol, tf, ts)
);

CREATE TABLE IF NOT EXISTS signals (
    id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    tf_entry TEXT NOT NULL,
    ts_entry INTEGER NOT NULL,
    direction TEXT NOT NULL,
    entry REAL NOT NULL,
    sl REAL NOT NULL,
    tp1 REAL,
    tp2 REAL,
    rr REAL,
    score REAL,
    reasons JSON,
    rendered JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    params JSON,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    status TEXT
);

CREATE INDEX IF NOT EXISTS idx_candles_symbol_tf_ts ON candles(symbol, tf, ts);
CREATE INDEX IF NOT EXISTS idx_candles_symbol_ts ON candles(symbol, ts);
