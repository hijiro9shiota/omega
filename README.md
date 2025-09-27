# Oryon — Local institutional-grade market signal research stack

Oryon est une plateforme de recherche de signaux de trading 100 % locale. Elle combine des connecteurs de données gratuits, un
stockage hybride JSON / SQL, des pipelines d’intégration et — dans les lots futurs — des moteurs d’analyse technique
multi-timeframes, un backend API FastAPI et un frontend React. Chaque lot est livré progressivement pour rester exploitable
en environnement limité.

Ce dépôt contient les livraisons combinées des **Lot 1 – Fondation data & configuration** et **Lot 2 – Cœur d’analyse**. Les lots
suivants étendront l’analyse, le backend et le frontend.

## Fonctionnalités du Lot 2

- Tout le socle du Lot 1 (ingestion multi-sources gratuites, stockage JSON/SQLite, scripts utilitaires et tests).
- Moteur d’analyse multi-timeframes avec détection de swings adaptatifs, BOS/CHOCH, order blocks, fair value gaps, turtle soup
  et niveaux de liquidité (equal highs/lows, sessions, daily hi/lo) synchronisés aux indicateurs.
- Suite d’indicateurs vectorisés (moyennes mobiles, momentum RSI/MACD/Stochastique, volatilité ATR/percentile, patterns chandeliers,
  Fibonacci) et microstructure (delta volume).
- Détection de régime de marché (trend/range) avec Hurst exponent, clustering KMeans et percentiles de volatilité.
- Pipeline complet `AnalyzeAssetPipeline` qui agrège les confluences, calcule le risk/reward, calibre un score normalisé et produit des
  signaux explicables avec overlays (order blocks, zones de liquidité).
- Filtres de risque (volatilité, liquidité), post-traitement (déduplication, quality gate) et générateur de signaux prêt pour les lots
  backend/front.
- Tests unitaires ciblant les zones de liquidité, BOS/CHOCH, order blocks et la calibration des scores, plus un test d’intégration du
  pipeline complet.

## Fonctionnalités du Lot 1

- Structure de dépôt complète (`oryon/`) avec configuration (`pyproject.toml`, `oryon_config.yaml`, `.env.example`, `LICENSE`).
- Connecteurs gratuits : Yahoo Finance, Stooq, ccxt (Binance), REST Binance public et lecture CSV locale.
- Gestion du cache disque et du rate limit avec file d’ingestion orchestrée par un `FetchScheduler`.
- Stockage hybride :
  - JSON append-only avec snapshots périodiques.
  - Base SQLite initialisée via `schema.sql` et synchronisation ETL JSON→SQL.
- Utilitaires communs (journalisation, chargement de configuration, maths/statistiques, parallélisme, outils temporels).
- Scripts CLI : construction d’univers de symboles, rafraîchissement des données gratuites, export CSV des signaux.
- Tests unitaires couvrant cache, rate limit, stockage, ETL, config, statistiques et ordonnancement d’ingestion.

## Prise en main rapide

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Configuration

1. Copiez `.env.example` en `.env` et adaptez les chemins si besoin.
2. Le fichier `oryon_config.yaml` contient les chemins des dossiers de données, la TTL du cache, les connecteurs actifs et la
   liste des timeframes. Les variables d’environnement préfixées par `ORYON_` peuvent surcharger la configuration (ex.
   `ORYON_DEFAULTS__DATA_DIR=./data_store_custom`).

### Rafraîchir des données gratuites

```bash
python -m oryon.scripts.refresh_free_data --symbol BTCUSDT --timeframe 1h --timeframe 4h
```

Ce script :

1. Charge la configuration.
2. Instancie les connecteurs disponibles et applique un cache disque + rate limit.
3. Stocke les bougies dans `data_store/json/...`.
4. Synchronise automatiquement la base SQLite (`data_store/oryon.sqlite`).

### Construire l’univers de symboles

Préparez un CSV avec les colonnes `symbol,exchange,asset_type,...`, puis :

```bash
python -m oryon.scripts.build_symbol_universe data_store/symbols.jsonl --static-csv static_symbols.csv
```

Le fichier JSONL produit est exploité par l’API et le frontend (lots ultérieurs) pour alimenter la recherche fuzzy.

### Exporter des signaux (future use)

Lorsque le moteur de signaux sera en place, vous pourrez exporter les signaux SQL vers CSV :

```bash
python -m oryon.scripts.export_signals_csv --output signals.csv
```

## Tests

```bash
pytest oryon/tests/unit
```

Les tests couvrent le cache disque, le rate limit, le stockage JSON/SQL, l’ETL, la configuration et les utilitaires numériques.

## Roadmap des lots suivants

1. **Lot 2 – Cœur d’analyse** : structure de marché, indicateurs, risk management, pipeline multi-timeframe et signaux
   explicables.
2. **Lot 3 – Backend & backtesting** : API FastAPI locale, moteur de backtesting et rapports.
3. **Lot 4 – Frontend React** : interface sombre futuriste avec graphe en temps réel, overlays et recherche fuzzy.

Chaque lot reste local, sans clés API payantes et avec une documentation d’installation actualisée.
