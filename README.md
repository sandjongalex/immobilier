# Immobilier — plateforme de location au Cameroun

**Statut : phase 1 — socle technique initial.** Backend Django et frontend React initialisés, sans fonctionnalités métier ni infrastructure déployée.

## Vision
Mettre directement en relation bailleurs et locataires, d'abord à Yaoundé. Le service **ne collecte pas de loyers**, n'organise pas les visites, ne négocie pas, ne rédige ni ne signe les baux et ne garantit pas la qualité juridique des biens. Les utilisateurs gèrent ces démarches eux-mêmes.

## Règle économique centrale
- **2 000 FCFA par logement publié pour une période de 30 jours**, sans reconduction automatique.
- Une unité louable de façon indépendante = une `Property` et une publication payante `Listing` distincte.
- Une maison louée entièrement = une seule unité.
- Le bailleur peut gérer plusieurs logements.
- La publication n'est visible publiquement **qu'après validation éditoriale ET confirmation manuelle du paiement**.
- Les annonces expirées, suspendues ou retirées ne sont jamais retournées par la recherche publique.
- Chaque nouvelle période payante est une publication `Listing` distincte rattachée au même logement, afin de conserver dates et historique.

## Stack cible
- API : Python / Django / Django REST Framework, contrat OpenAPI (drf-spectacular proposé).
- Web : React / Vite / TypeScript / Tailwind CSS.
- Base : PostgreSQL.
- Production envisagée : Ubuntu sur VPS Contabo, Nginx, Gunicorn, TLS/HTTPS.
- Tests : pytest/pytest-django, tests DRF, Vitest/React Testing Library, Playwright ciblé (à décider lors de l'implémentation).
Ces outils ne sont pas supposés installés ou configurés.

## Documentation
1. [Exigences produit](docs/PRODUCT_REQUIREMENTS.md)
2. [Architecture](docs/ARCHITECTURE.md)
3. [Modèle de données](docs/DATA_MODEL.md)
4. [Contrat d'API](docs/API_SPECIFICATION.md)
5. [Sécurité et exploitation](docs/SECURITY.md)
6. [Roadmap et validation](docs/ROADMAP.md)

## Décisions structurantes
Les montants sont stockés en entier FCFA; les dates sont stockées en UTC et affichées en heure d'Afrique/Douala; une annonce n'est active que si `status=ACTIVE`, `starts_at <= now < ends_at`, `Property` est publiable et l'utilisateur n'est pas bloqué. La création d'une nouvelle période n'efface jamais les périodes ni les paiements précédents.

## Démarrage du socle (sans annonces fonctionnelles)
- **Pré-requis** : Python 3.13, PostgreSQL 14+, Node.js 22.12+, npm.
- Backend : voir [backend/README.md](backend/README.md).
- Frontend : voir [frontend/README.md](frontend/README.md).
- Guide Windows / Ubuntu, variables et tests : [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).
- Déploiement futur : [deploy/README.md](deploy/README.md).

**Le dépôt ne fournit aucun compte de paiement, aucun secret, aucune base préconfigurée et aucun logement fictif.** Chaque environnement doit être configuré explicitement. La prochaine phase métier ne sera pas développée sans instruction.
