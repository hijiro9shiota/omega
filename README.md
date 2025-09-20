# Omega Study Platform

Omega Study est une plateforme académique qui combine une prise de notes vocale locale et des fonctionnalités IA à la demande pour résumer, questionner et ludifier les cours. L'objectif est de limiter l'usage payant d'API en stockant uniquement le texte transcrit et en n'appelant l'IA que lorsque l'utilisateur le demande.

## Aperçu des fonctionnalités

- **Capture vocale côté navigateur** grâce à l'API Web Speech, sans stockage de fichiers audio volumineux.

- **Éditeur de notes en temps réel** avec statistiques, tags contextuels et sauvegarde locale automatique.
- **Outils IA à la carte** : résumé, quiz, réponses aux questions et mini-jeux pédagogiques. Chaque outil ne contacte le backend qu'à la demande et met en cache ses réponses pour économiser les crédits IA.
- **Fallback local intelligent** lorsque le serveur IA est indisponible : résumés simplifiés, quiz générés via heuristiques et conseils d'auto-révision.
- **Exports instantanés** en Markdown ou JSON pour partager vos notes.

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
frontend/  → Interface HTML/CSS/JS autonome (aucune étape de build nécessaire)
```

## Utilisation de l'interface

1. Ouvrez simplement `frontend/index.html` dans votre navigateur (double-clic ou « Ouvrir avec Live Server »). Aucun bundler n'est requis.
2. Cliquez sur « Commencer l'enregistrement » pour déclencher la reconnaissance vocale (Chrome recommandé). Les notes sont nettoyées en direct et enrichies de suggestions d'actions.
3. Utilisez les boutons de la section « Analyse IA à la demande » pour générer résumé, quiz, réponses et jeux. En l'absence de backend, une version locale vous est proposée pour continuer à travailler sans attendre.
4. Ajoutez des tags contextuels, suivez les statistiques automatiques et exportez vos notes en Markdown ou JSON.

> 💡 L'autosauvegarde locale conserve votre travail même en cas de fermeture d'onglet.

## Configuration du backend (optionnelle)

Le backend Express reste disponible pour stocker les sessions et déléguer les analyses IA complètes.

1. Installez les dépendances côté backend :

   ```bash
   cd backend
   npm install
   ```

   > Si le registre npm est restreint dans votre environnement, configurez `npm config set registry https://registry.npmjs.org/` ou un miroir autorisé.

2. Créez le fichier `.env` depuis l'exemple et ajoutez votre clé OpenAI :

   ```bash
   cp .env.example .env
   # puis éditez .env pour y placer OPENAI_API_KEY=...
   ```

3. Lancez le serveur :

   ```bash
   npm run dev
   ```

4. Les appels IA resteront facultatifs : sans clé, le serveur emploie des algorithmes locaux pour fournir des résultats basiques. L'interface détecte automatiquement la présence du backend et profite de la mise en cache côté serveur.

## Déploiement

- **Frontend** : il s'agit d'un bundle statique. Publiez simplement le dossier `frontend/` (ou son contenu) sur un hébergement statique, un CDN ou même un dossier partagé.
- **Backend** : déployez `backend/` sur la plateforme de votre choix (Railway, Render, Fly.io, VPS…) en veillant à configurer `OPENAI_API_KEY` et un stockage persistant pour `backend/data/sessions.json`.

## Notes sur la confidentialité

- Les enregistrements vocaux ne quittent jamais le navigateur : seul le texte transcrit est stocké.
- Les appels IA ne sont déclenchés qu'à la demande explicite de l'utilisateur et profitent d'une mise en cache pour limiter la facture.
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
