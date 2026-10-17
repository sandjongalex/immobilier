# API REST — contrat fonctionnel V1 (projet, non implémenté)

Base `/api/v1`; JSON; auth proposée : **sessions Django avec cookies HttpOnly + CSRF** pour application web same-origin derrière Nginx (pas de jetons dans localStorage). HTTPS obligatoire en prod. OpenAPI généré via drf-spectacular à partir du code : `/api/schema/` et `/api/docs/` si exposition autorisée.

## Convention
- Identifiants UUID; heures ISO 8601 UTC; argent entier `*_xaf`.
- Pagination `?page=1&page_size=20` (maximum serveur fixé à l'implémentation), enveloppe DRF `count,next,previous,results`.
- Erreur standard proposée : `{"code":"invalid_transition","detail":"...","fields":{}}`; validation 400, auth 401/403 selon auth, absence ou objet inaccessible 404, conflit d'état 409, débit 429.
- `Idempotency-Key` pour soumission et décisions de paiement, activations protégées par transaction; si mise en œuvre différée, documenter comportement strict de répétition avant ouverture au public.
- Documentation détaillera exemples, schémas, limites, champs obligatoires/optionnels et codes d'erreur à l'implémentation.

## Public
| Verbe | Route | Accès | Fonction |
|---|---|---|---|
| GET | `/cities/` | Public | Villes activées |
| GET | `/neighborhoods/?city_id=` | Public | Quartiers |
| GET | `/listings/` | Public | Uniquement annonces visibles; filtres city_id, neighborhood_id, kind, min_rent, max_rent, bedrooms_min, ordering |
| GET | `/listings/{id}/` | Public | Annonce visible uniquement; sans adresse exacte ni preuve de paiement |
| POST | `/auth/register/` | Visiteur | Créer compte sans rôle privilégié |
| POST | `/auth/login/` | Visiteur | Session + CSRF |
| POST | `/auth/logout/` | Authentifié | Fin session |
| GET | `/auth/me/` | Authentifié | Identité/rôles |
| GET | `/auth/csrf/` | Public | Initialise cookie CSRF si nécessaire |

## Bailleur (scopé au propriétaire)
| Verbe | Route | Fonction |
|---|---|---|
| GET, POST | `/landlord/properties/` | Lister / créer mes unités |
| GET, PATCH | `/landlord/properties/{id}/` | Consulter / modifier mon unité (modifs approuvées re-modérées) |
| POST | `/landlord/properties/{id}/images/` | Ajout image contrôlé |
| DELETE | `/landlord/properties/{id}/images/{image_id}/` | Retirer image autorisée |
| GET, POST | `/landlord/properties/{id}/listings/` | Historique / créer publication |
| GET | `/landlord/listings/{id}/` | Détail statut, dates, décisions non sensibles |
| POST | `/landlord/listings/{id}/submit/` | DRAFT/REJECTED -> PENDING_REVIEW |
| POST | `/landlord/listings/{id}/withdraw/` | Retirer publication selon état |
| GET, POST | `/landlord/listings/{id}/payments/` | Tentatives de paiement et demande |
| POST | `/landlord/payments/{id}/submit-proof/` | Soumettre référence/preuve, sans confirmer |
| GET | `/landlord/listings/{id}/history/` | Historique de sa publication |

## Locataire / authentifié
| Verbe | Route | Fonction |
|---|---|---|
| GET | `/listings/{id}/contact/` | Contact révélé sous consentement et anti-abus; authentifié |
| POST | `/listings/{id}/reports/` | Signaler une annonce visible; authentifié |

## Modération
| Verbe | Route | Règle |
|---|---|---|
| GET | `/moderation/listings/?status=pending_review` | MODERATOR/ADMIN |
| GET | `/moderation/listings/{id}/` | MODERATOR/ADMIN |
| POST | `/moderation/listings/{id}/approve/` | MODERATOR/ADMIN, état et version vérifiés |
| POST | `/moderation/listings/{id}/reject/` | MODERATOR/ADMIN, motif requis |
| POST | `/moderation/listings/{id}/suspend/` | MODERATOR/ADMIN, motif requis |
| GET, PATCH | `/moderation/reports/` et `/moderation/reports/{id}/` | MODERATOR/ADMIN |

## Administration
| Verbe | Route | Règle |
|---|---|---|
| GET | `/admin/payments/?status=submitted` | ADMIN uniquement |
| GET | `/admin/payments/{id}/` | ADMIN, preuve via accès privé contrôlé |
| POST | `/admin/payments/{id}/confirm/` | ADMIN, montant/référence vérifiés + audit |
| POST | `/admin/payments/{id}/reject/` | ADMIN, motif obligatoire |
| GET | `/admin/audit-events/` | ADMIN, filtres et données caviardées |
| GET, PATCH | `/admin/users/` et `/admin/users/{id}/` | ADMIN, opérations restreintes/auditées |

**Attention :** `/api/v1/admin/*` désigne l'API administrative, distincte de l'interface Django admin (dont le chemin doit être explicitement configuré).

## Autorisations systématiques
- Visiteur : GET catalogue et géographie uniquement.
- Locataire : consultation/contact et signalement; aucune écriture Property/Listing/Payment.
- Bailleur : `property.landlord_id=request.user.id` + publication rattachée; impossible de confirmer paiement ou de modérer.
- Modérateur : modération et signalements; pas de confirmation financière.
- Admin : contrôle paiement et rôle, actions sensibles auditées.
- Vérifier l'ownership dans les listes ET actions de détail (IDOR), filtrer les champs écrits (`status`, `confirmed_at`, `reviewed_by`, dates d'activation non modifiables par client).
- Ne pas faire confiance au frontend pour permissions ni aux valeurs de `amount_xaf` fournies par le client.

## Exemple minimal de recherche
`GET /api/v1/listings/?city_id=<uuid>&max_rent=150000&ordering=-created_at` -> 200, seulement unités actives à la date de la requête. Aucun listing expiré n'est retourné même avant exécution du traitement périodique.

## Contrats de tests API
401/403/404 selon visibilité; cross-owner toujours rejeté; confirmation réservée admin; redoublement de confirmation idempotent; paiement insuffisant => 409; pagination/filtres déterministes; état temporel contrôlé avec horloge figée.
