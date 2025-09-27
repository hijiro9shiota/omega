# Plan de découpage du projet Oryon en quatre lots

Afin de rendre la création du projet Oryon réalisable dans ce contexte, nous proposons de le développer en quatre étapes successives. Chaque lot constitue un livrable cohérent qui peut être exécuté localement et préparera le terrain pour le lot suivant.

## Lot 1 — Fondation data & configuration
- Mettre en place l'architecture du dépôt (`oryon/`) avec la configuration de base (README, LICENSE, `pyproject.toml`, `oryon_config.yaml`).
- Implémenter les connecteurs de données gratuits (yfinance, Stooq, ccxt public, Binance REST public, lecture CSV) avec gestion du cache disque, du contrôle du rate limit et d'une file planifiée d'ingestion.
- Mettre en place la couche de stockage hybride :
  - Gestion des fichiers JSON append-only et snapshots.
  - Base SQLite/DuckDB avec schéma versionné (`schema.sql`).
  - ETL JSON→SQL avec contrôles d'intégrité et synchronisation bidirectionnelle de métadonnées.
- Développer les utilitaires communs (`utils/`) : journalisation structurée, chargement de configuration, outils temps/math/statistiques, parallélisme.
- Créer les premiers tests unitaires (connecteurs, stockage, intégrité ETL) et scripts de maintenance (`build_symbol_universe.py`, `refresh_free_data.py`).
- Livrer une documentation d'installation locale (mode démo offline via CSV).

## Lot 2 — Cœur d'analyse technique & risk management
- Implémenter les modules de structure de marché : swings zigzag adaptatifs, BOS/CHOCH, zones de liquidité, order/ breaker blocks, FVG, VWAP sessions, régime de marché et microstructure simplifiée.
- Ajouter la bibliothèque d'indicateurs (moyennes mobiles, momentum, volatilité, patterns de chandeliers, Fibonacci).
- Construire les modules de risque (`rr_engine`, filtres de marché) et la définition des signaux (`signal_schema`, `signal_builder`, `post_filtering`).
- Mettre en place les pipelines d'analyse multi-timeframes (analyse par symbole, agrégateur multi-timeframes, routeur d'ensemble, calibrateur de scores) avec explication détaillée.
- Enrichir la suite de tests unitaires couvrant chaque composant et ajouter un test d'intégration du pipeline complet.

## Lot 3 — Backend API & backtesting
- Développer l'API FastAPI avec endpoints `search`, `history`, `analyze`, `live` et DTO associés, incluant la sécurité locale, la gestion des logs et le suivi des exécutions.
- Intégrer la couche d'analyse au backend pour générer des signaux explicables à la demande.
- Implémenter le moteur de backtesting (chargement, walk-forward, métriques, rapports HTML/CSV) et un exemple d'exécution.
- Ajouter des tests d'intégration backend et des scénarios de backtesting pour valider la production de signaux cohérents.

## Lot 4 — Frontend React + expérience utilisateur
- Créer l'interface Vite + React + Tailwind en thème sombre futuriste avec animations.
- Développer les composants requis : `SearchBar`, `RealtimeChart`, `AnalyzePanel`, `SignalCard`, `LayersToggles`, `Toaster`, ainsi que les bibliothèques front (`apiClient`, `symbolIndex`, `chartOverlays`).
- Intégrer le graphique Lightweight Charts, les overlays d'annotations et la synchronisation temps réel des signaux.
- Implémenter l'auto-suggest pour l'univers des symboles et les commandes d'analyse.
- Prévoir un bundle statique exécutable hors ligne et des assets (logo, police).
- Ajouter des tests frontend (unitaires et e2e si possible) ou, à défaut, des scénarios manuels documentés.

Chaque lot sera livré avec :
- Code entièrement local, sans dépendances payantes.
- Documentation mise à jour (README, guides d'usage par lot).
- Tests automatisés adaptés au périmètre du lot.
- Scripts de données et exemples permettant de valider les fonctionnalités sans connexion externe.

Ce découpage permet de sécuriser l'implémentation progressive tout en garantissant une base robuste pour un système institutionnel d'analyse et de génération de signaux de trading.
