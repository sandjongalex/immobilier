# Installation locale et vérifications du socle

Ce guide couvre uniquement la structure technique, sans paiement ni annonce fonctionnelle.

## Prérequis
- Python **3.13** et pip ; venv.
- PostgreSQL **14+** local ou accessible (pas de SQLite).
- Node.js **22.12+** et npm.
- Git. Aucune passerelle de paiement, service cloud ou VPS requis.

## PostgreSQL : préparation manuelle
Créer une base et un rôle distincts (ex. noms locaux `immobilier_dev`) dans PostgreSQL. Donner au rôle local le droit `CREATEDB` **uniquement si nécessaire pour lancer pytest**; ne pas accorder ce droit à un rôle de production. Choisir un mot de passe local personnel, sans le committer. Remplir les variables du `.env` backend. Aucun compte de connexion n'est fourni dans ce dépôt.

## Installation backend — Linux/macOS
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements/dev.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## Installation backend — Windows PowerShell
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements/dev.txt
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Dans les deux cas, reporter la clé aléatoire générée dans `DJANGO_SECRET_KEY` du `.env`. Configurer `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` (et host/port si besoin). `DJANGO_SETTINGS_MODULE` est fixé par `manage.py` en développement et par la configuration du processus en production; il ne suffit pas de changer cette ligne dans `.env`.

Démarrer ensuite :
```bash
python manage.py check
python manage.py migrate
python manage.py runserver
```

Tester `http://127.0.0.1:8000/api/v1/health/` (liveness Django seulement, non diagnostic DB). Documentation de schéma locale : `http://127.0.0.1:8000/api/docs/`. Aucun endpoint de création d'annonce n'existe encore.

### Qualité backend
```bash
ruff check .
ruff format --check .
python manage.py makemigrations --check --dry-run
pytest
```
Pytest utilise `config.settings.testing` et crée `test_<POSTGRES_DB>` séparément ; le rôle doit pouvoir créer la base et les dépendances PostgreSQL doivent être disponibles. Ne pas lancer des tests avec un compte SQL de production.

## Installation frontend
Depuis la racine du dépôt, ouvrir un **autre terminal** :
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```
PowerShell : `Copy-Item .env.example .env` à la place de `cp`. Naviguer à l'adresse annoncée par Vite, généralement `http://localhost:5173`. Le proxy `/api` de Vite n'est pas un backend; celui-ci doit être lancé séparément.

### Qualité frontend
```bash
npm run lint
npm run typecheck
npm run test
npm run build
npm run format:check
```

Le `package-lock.json` créé par `npm install` doit ensuite être ajouté au dépôt pour permettre `npm ci` lors des prochaines installations et en CI.

## Contextes d'exécution
| Mode | Django settings | Base | Particularités |
|---|---|---|---|
| Développement | `config.settings.development` | PostgreSQL de développement | DEBUG activé, schéma OpenAPI consultable |
| Tests | `config.settings.testing` | base PostgreSQL de tests dédiée | Clé volatile si absente, pas de SQLite |
| Production (future) | `config.settings.production` | PostgreSQL de production | DEBUG désactivé, cookies Secure, HTTPS, variables requises |

Les fichiers `.env` sont ignorés par Git; `.env.example` reste suivi. Une variable de frontend préfixée `VITE_` est **publique**. Ne jamais y déposer de secret.

## Blocages possibles
- PostgreSQL indisponible : `migrate` et `pytest` échouent; ne pas basculer vers SQLite.
- `POSTGRES_DB`, `POSTGRES_USER` ou `DJANGO_SECRET_KEY` absent : échec volontaire dès le chargement des settings.
- Pas de registre npm/pip : les installations et les tests dépendants des packages ne peuvent pas être confirmés localement.
- CI GitHub Actions : utilise une base PostgreSQL temporaire avec authentification trust **uniquement dans le conteneur éphémère de CI**, jamais en production.
