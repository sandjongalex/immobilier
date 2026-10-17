# Backend — Django REST Framework

Socle technique uniquement. Pas de modèles immobiliers, de paiement ni de routes métier.

## Versions
Python 3.13 recommandé, PostgreSQL >= 14; Django 5.2 LTS.

## Préparation (Linux/macOS)
Depuis la racine du dépôt :

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements/dev.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Coller la clé générée dans `.env`, configurer `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` et créer **manuellement** base/utilisateur PostgreSQL. Le fichier d'exemple ne contient aucun secret. Sur Windows : `py -m venv .venv`, `.venv\\Scripts\\Activate.ps1`, `Copy-Item .env.example .env`.

```bash
python manage.py check
python manage.py migrate
python manage.py runserver
```

Liveness : `http://127.0.0.1:8000/api/v1/health/`; doc OpenAPI locale : `/api/docs/` et `/api/schema/`. Ces routes de documentation ne sont pas activées avec `production`.

## Qualité et tests

```bash
ruff check .
ruff format --check .
pytest
python manage.py spectacular --file schema.yml
```

`schema.yml` est généré localement : ne pas le committer sans décision de versionner le contrat. Pour pytest, le runner crée une **base de tests PostgreSQL distincte**; le rôle PostgreSQL doit avoir le droit `CREATEDB`. Aucun SQLite, même en test.

## Environnements
- Local : `config.settings.development` (défaut `manage.py`).
- Tests : `config.settings.testing` (défaut pytest).
- Production : `config.settings.production` (Gunicorn), **jamais activé sans variables explicites et HTTPS**.

Plus de détails : [docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md) et [docs/SECURITY.md](../docs/SECURITY.md).
