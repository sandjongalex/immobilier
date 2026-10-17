# Déploiement — préparation seulement

**Aucun VPS Contabo, DNS, certificat, serveur PostgreSQL ni accès SSH n'est préconfiguré.** Ce dossier accueillera ultérieurement les fichiers de production testés et validés.

## Cible prévue
- Ubuntu sur VPS Contabo : compte système applicatif limité, mises à jour et SSH sécurisé.
- Nginx : `/` -> fichiers statiques build React; `/api/` -> Gunicorn sur socket/port local; `/static/` -> staticfiles Django; `/media/` -> fichiers publics approuvés seulement.
- Gunicorn : `config.wsgi:application` avec `DJANGO_SETTINGS_MODULE=config.settings.production`.
- PostgreSQL >= 14 non exposé sur Internet, rôle applicatif restreint.
- HTTPS : vrai domaine + certificat avant d'activer les cookies sécurisés et l'accès public.
- Sauvegardes hors VPS et test de restauration (DB **et** médias).

## Avant production
1. Fournir le domaine, VPS, comptes techniques, PostgreSQL, volumes et secrets via environnement protégé.
2. Adapter `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `DJANGO_SECRET_KEY`, `POSTGRES_*`, `DJANGO_MEDIA_ROOT`; jamais dans Git.
3. Installer `backend/requirements/prod.txt`, générer le build frontend, créer services systemd/Nginx.
4. Tester `python manage.py check --deploy --settings=config.settings.production`, migrations, restaurations, SSL, contrôle d'accès.
5. Ouvrir en production **seulement après validation des phases métier et sécurité**.

Aucune preuve de paiement ne devra se trouver dans les médias directement exposés par Nginx. Les scripts de production seront écrits et audités lors de la phase de déploiement, pas maintenant.
