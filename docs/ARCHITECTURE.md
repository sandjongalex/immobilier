# Architecture technique cible

## 1. Décision : monolithe modulaire + SPA
Application Django unique, structurée par domaines, REST DRF, PostgreSQL unique; frontend React séparé. **Pas de microservices, de broker, de Redis ni de Celery imposés en V1.** OpenAPI via drf-spectacular (proposition). Dépendances externes non configurées à ce stade.

```text
Navigateur (React / Vite / TypeScript / Tailwind)
  HTTPS / Nginx
    /          -> build statique React
    /api/v1/   -> Gunicorn -> Django / DRF
    /api/schema/ et /api/docs/ -> contrat OpenAPI (accès à définir)
  Django:
    accounts -> properties -> listings -> payments
                    |           |          |
                    |           +-> moderation
                    +-> media   +-> audit
  PostgreSQL : données transactionnelles
  Fichiers privés / publics contrôlés : photos + preuves de paiement
```

## 2. Modules Django proposés
| App | Responsabilité | Dépendances |
|---|---|---|
| `core` | santé, constantes, pagination, exceptions, transactions | Django |
| `accounts` | utilisateur, profil, rôles, authentification | core |
| `locations` | villes, quartiers, référentiel | core |
| `properties` | unités louables, adresses, caractéristiques, photos | accounts, locations |
| `listings` | publication, règles de visibilité et de durée, recherches | properties |
| `payments` | instructions administrées, demandes, justificatifs, décisions manuelles | listings, accounts |
| `moderation` | validation, suspensions, signalements | listings, accounts |
| `audit` | événements append-only métier et sécurité | core, accounts |

Préférer **services métier transactionnels** pour transitions et validations; serializers DRF pour transport, permissions pour accès, QuerySets/services pour filtrage public. Ne pas disséminer la logique d'activation dans les signaux Django.

## 3. Structure cible (non créée)
```text
backend/
  manage.py
  config/{settings/,urls.py,asgi.py,wsgi.py}
  apps/{core,accounts,locations,properties,listings,payments,moderation,audit}/
  tests/
frontend/
  src/{app,api,features,components,routes,styles}/
docs/
deploy/           # plus tard : nginx, systemd, procédures
```

## 4. Flux d'activation
1. Le bailleur crée une propriété puis un `Listing` en brouillon.
2. Il le soumet : `PENDING_REVIEW`, et génère une demande de paiement `Payment` distincte.
3. Modérateur décide : `APPROVED` ou `REJECTED` (révision possible via nouveau cycle).
4. Administrateur valide manuellement le paiement `CONFIRMED` après rapprochement hors application.
5. Service `try_activate_listing(listing_id)`, exécuté dans une transaction `atomic()`, verrouille la publication et sa propriété, vérifie approbation + paiement confirmé + absence de publication active concurrente + intégrité des photos et du bien; fixe `starts_at = now()`, `ends_at = starts_at + timedelta(days=30)`, état `ACTIVE` et trace l'audit.
6. En cas d'indisponibilité du bien ou de rejet, aucune activation; résolution explicite par administrateur.
7. Lecture publique utilise **toujours** `status=ACTIVE AND starts_at<=NOW() AND ends_at>NOW()` avec les autres restrictions. Une commande périodique `expire_listings` ne fait que mettre en cohérence les statuts et produire les événements. Elle est idempotente.
8. Une nouvelle période est un **nouveau Listing** rattaché à la même `Property`; pas d'extension silencieuse de `ends_at`.

Paiement et modération peuvent arriver dans n'importe quel ordre. La vérification du paiement n'entraîne **aucun** remboursement automatique et aucun paiement ne modifie rétroactivement une période achevée.

## 5. Consistance et concurrence
- Transactions SQL et `select_for_update` pour paiements, publication, propriété et activation; ordre de verrouillage déterministe `Property -> Listing -> Payment`.
- `Payment` confirmé enregistré une seule fois; une tentative répétée retourne l'état courant sans deuxième activation.
- Vérification d'existence d'une période active du logement **sous verrou de sa propriété**; vérification supplémentaire applicative/BD au déploiement.
- Révision substantielle après approbation : repasse en modération; pas de modification silencieuse d'une annonce active sans revue.
- Débit et date de paiement sont indépendants des dates de publicité.
- Logique d'autorisation dans les services et dans DRF, pas uniquement dans le frontend.

## 6. Frontend
React Router, couches `api` typées à partir d'OpenAPI, pages publiques (recherche, détails), espace bailleur, console modération/admin. Séparation état serveur et état présentation; bibliothèque de requêtes à choisir à l'implémentation. Variables de configuration non secrètes en build; secrets exclusivement backend.

## 7. API et documentation
REST `/api/v1/`, JSON, ISO 8601 UTC, IDs UUID, statut HTTP approprié, erreurs structurées, pagination. Contrat de référence : [API_SPECIFICATION.md](API_SPECIFICATION.md). Génération automatique OpenAPI depuis serializers/views; tests de schéma en CI lors de la phase de développement.

## 8. Exploitation cible
Contabo Ubuntu -> Nginx TLS -> Gunicorn -> Django -> PostgreSQL (sur VPS au départ, rôle DB restreint). Fichiers médias sur disque persistant **hors répertoire du code** pour V1, stockages public et privé séparés, stockage objet compatible S3 possible plus tard sans changer le domaine. Pas de DNS, certificat, compte Contabo ou passerelle déjà supposé prêt.

## 9. Extensions prévues
Multi-ville via FK City, quartiers par ville, géolocalisation optionnelle, futur PSP via interface de paiement sans altérer `Listing`. Tout ajout d'intégration devra être isolé par adaptateur et contrat testé.
