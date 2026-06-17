# Diamond Solver Pro

Une application web complète pour résoudre le problème de production de diamants à l'aide d'un algorithme Depth-First Search (DFS) optimisé, avec un frontend moderne en Drag & Drop.

## Architecture

Le projet utilise une architecture propre séparant le backend algorithmique du frontend graphique.

- **Backend (FastAPI)**: Situé dans `src/`. Expose l'API et implémente le moteur de résolution (`DiamondSolver`).
- **Frontend (Next.js)**: Situé dans `frontend/`. Fournit une interface utilisateur riche avec Next.js et TailwindCSS.
- **Tests**: Situés dans `tests/` pour le backend et `frontend/e2e/` pour le frontend. Couverture complète (Unitaires, Intégration, E2E).

## Installation & Démarrage

### 1. Démarrer le Backend (FastAPI) avec `uv`

Nous recommandons d'utiliser [uv](https://github.com/astral-sh/uv) pour une installation Python ultra-rapide.

```bash
# Créer l'environnement virtuel avec uv
uv venv

# Activer l'environnement virtuel
source .venv/bin/activate

# Installer les dépendances depuis requirements.txt
uv pip install -r requirements.txt

# Lancer l'API FastAPI
uvicorn src.api.main:app --port 4000 --reload
```
L'API sera disponible sur [http://127.0.0.1:4000](http://127.0.0.1:4000).

### 2. Démarrer le Frontend (Next.js)

```bash
# Dans un nouveau terminal, aller dans le dossier frontend
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement Next.js
npm run dev
```
Le Frontend sera disponible sur [http://127.0.0.1:3000](http://127.0.0.1:3000) (ou 3001/3002 s'il y a un conflit de port).

## Utilisation

Rendez-vous sur l'interface graphique (Frontend). Glissez-déposez le fichier `seed.txt` (ou tout autre fichier de blueprints valide) dans la zone dédiée. L'application communiquera avec l'API pour lancer l'algorithme sur le contenu du fichier, puis affichera instantanément les résultats (Partie 1 et Partie 2).

## Documentation de l'Algorithme

Pour une explication détaillée de l'algorithme de résolution (les principes de dominance, la coupure des stocks, l'exploration de l'arbre), consultez la [Presentation complète du projet](Presentation.MD).

## Tests

Pour lancer les tests du projet :

```bash
# Tests Backend (Unitaires & Intégration)
pytest tests/

# Tests Frontend (End-to-End avec Playwright)
cd frontend
npx playwright test e2e/
```
