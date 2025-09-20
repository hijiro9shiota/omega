# Omega Study Platform

Omega Study est une plateforme académique qui combine une prise de notes vocale locale et des fonctionnalités IA à la demande pour résumer, questionner et ludifier les cours. L'objectif est de limiter l'usage payant d'API en stockant uniquement le texte transcrit et en n'appelant l'IA que lorsque l'utilisateur le demande.

## Aperçu des fonctionnalités

- **Capture vocale côté navigateur** grâce à l'API Web Speech, sans stockage de fichiers audio volumineux.
- **Éditeur de notes en temps réel** avec statistiques de mots et synchronisation avec la transcription.
- **Sauvegarde côté serveur** (Node.js/Express) dans un fichier JSON léger pour éviter une base de données coûteuse.
- **Outils IA à la carte** : résumé, quiz, réponses aux questions et mini-jeux pédagogiques.
- **Stratégies d'optimisation des coûts** :
  - Résumés et quiz locaux (fallback) lorsque la clé OpenAI est absente ou que le texte est court.
  - Mise en cache des réponses IA sur le serveur pour éviter des appels redondants.
  - Possibilité de chunker les transcripts avant envoi à l'IA pour contrôler la consommation de tokens.

## Structure du projet

```
backend/   → API Express, stockage des sessions, intégration OpenAI optionnelle
frontend/  → Interface Vite + React
```

## Pré-requis

- Node.js 18+
- (Optionnel) Une clé API OpenAI disponible dans `backend/.env`

## Installation

```bash
# Installer les dépendances côté backend
cd backend
npm install

# Installer les dépendances côté frontend
cd ../frontend
npm install
```

> 💡 Si le registre npm est restreint dans votre environnement, configurez `npm config set registry https://registry.npmjs.org/` ou un miroir autorisé.

## Configuration

1. Copier le fichier d'exemple et renseigner la clé API si vous souhaitez activer l'IA OpenAI.

```bash
cd backend
cp .env.example .env
# puis éditer .env pour y placer OPENAI_API_KEY=...
```

2. Les appels IA restent facultatifs : sans clé, le serveur emploie des algorithmes locaux pour fournir des résultats basiques.

## Lancer les services

Dans deux terminaux séparés :

```bash
# Terminal 1 - backend
cd backend
npm run dev

# Terminal 2 - frontend
cd frontend
npm run dev
```

Le frontend est accessible sur http://localhost:5173 et proxe automatiquement les requêtes `/api` vers l'API Express sur http://localhost:4000.

## Tests et qualité

- `npm run lint` dans `backend/` vérifie le style de code serveur.
- Un linter React peut être ajouté côté frontend selon vos préférences.

## Déploiement

Pour un déploiement léger :

1. Construire le frontend :

```bash
cd frontend
npm run build
```

2. Servir le dossier généré `frontend/dist` via un CDN ou un serveur statique (ex. Nginx).
3. Héberger le backend (Railway, Render, Fly.io, VPS) en veillant à configurer `OPENAI_API_KEY` et un stockage persistant pour `backend/data/sessions.json`.

## Notes sur la confidentialité

- Les enregistrements vocaux ne quittent jamais le navigateur : seul le texte transcrit est transmis au serveur.
- Les appels IA ne sont déclenchés qu'à la demande explicite de l'utilisateur.

Bon apprentissage avec Omega Study !
