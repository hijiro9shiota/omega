# Omega Study Platform

Omega Study est une plateforme académique qui combine une prise de notes vocale locale et des fonctionnalités IA à la demande pour résumer, questionner et ludifier les cours. L'objectif est de limiter l'usage payant d'API en stockant uniquement le texte transcrit et en n'appelant l'IA que lorsque l'utilisateur le demande.

## Aperçu des fonctionnalités

- **Capture vocale côté navigateur** grâce à l'API Web Speech, sans stockage de fichiers audio volumineux.
- **Éditeur de notes en temps réel** avec statistiques, tags contextuels et sauvegarde locale automatique.
- **Outils IA à la carte** : résumé, quiz, réponses aux questions et mini-jeux pédagogiques. Chaque outil ne contacte le backend qu'à la demande et met en cache ses réponses pour économiser les crédits IA.
- **Fallback local intelligent** lorsque le serveur IA est indisponible : résumés simplifiés, quiz générés via heuristiques et conseils d'auto-révision.
- **Exports instantanés** en Markdown ou JSON pour partager vos notes.

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

Bon apprentissage avec Omega Study !
