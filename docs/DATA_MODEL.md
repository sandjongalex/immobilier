# Modèle de données logique (PostgreSQL)

## 1. Principe
`Property` = **unité louable réelle**, indépendante du financement. `Listing` = **une fenêtre commerciale de publication payante**. `Payment` = **une opération de preuve et vérification manuelle** pour une publication. Ne jamais fusionner ces trois notions.

```text
User 1---N Property 1---N Listing 1---N Payment
                         |                |
                         N                N
                   ModerationReview  PaymentDecision/AuditEvent
Property 1---N PropertyImage
City 1---N Neighborhood; City 1---N Property
Listing 1---N Report
```

## 2. Tables et champs principaux
### accounts.User
`id UUID PK, email UNIQUE, password_hash, phone(nullable), is_active, created_at, updated_at`. Modèle utilisateur personnalisé dès migration initiale; identité non exposée. `UserRole(user_id, role)` unique; `role IN (TENANT, LANDLORD, MODERATOR, ADMIN)`; visiteur anonyme. `LandlordProfile(user_id UNIQUE, display_name, contact_visibility_consent, verification_status)`.

### locations.City / Neighborhood
`City(id, name, slug UNIQUE, is_enabled)`; `Neighborhood(id, city_id FK, name, slug, UNIQUE(city_id,slug))`. Seed initial Yaoundé; nouvelles villes par configuration/administration, pas par changement structurel.

### properties.Property
`id UUID PK, landlord_id FK(User), city_id FK, neighborhood_id FK nullable, kind ENUM(HOUSE,APARTMENT,STUDIO,ROOM,OTHER), rental_scope ENUM(WHOLE_UNIT,INDEPENDENT_UNIT), title, description, monthly_rent_xaf BIGINT CHECK>=0, bedrooms INT CHECK>=0, bathrooms INT CHECK>=0, area_m2 NUMERIC nullable CHECK>0, approximate_location TEXT, precise_address TEXT nullable PRIVATE, features JSONB, availability ENUM(AVAILABLE,RENTED,UNAVAILABLE), is_archived BOOL, created_at, updated_at`.
Une ligne = une unité qui peut se louer indépendamment. Adresse exacte jamais exposée publiquement. Validation : quartier appartient à ville; prix strictement positif pour publication.
`PropertyImage(id UUID PK, property_id FK, storage_key, alt_text, sort_order, mime_type, size_bytes, is_approved, created_at)`. Clé fichier interne; URLs temporaires ou contrôlées pour contenu privé.

### listings.Listing
`id UUID PK, property_id FK, created_by_id FK, status ENUM(DRAFT,PENDING_REVIEW,APPROVED,REJECTED,ACTIVE,EXPIRED,SUSPENDED,WITHDRAWN), review_state ENUM(NOT_SUBMITTED,PENDING,APPROVED,REJECTED), starts_at TIMESTAMPTZ nullable, ends_at TIMESTAMPTZ nullable, price_xaf INT NOT NULL DEFAULT 2000 CHECK(price_xaf=2000 for MVP), duration_days SMALLINT DEFAULT 30 CHECK(duration_days=30 for MVP), content_snapshot JSONB, submitted_at, approved_at, activated_at, withdrawn_at, created_at, updated_at`.
Les prix/durée sont **figés au moment de création** et non lus d'une constante courante pour les anciennes publications. `ends_at = starts_at + interval '30 days'` à l'activation. `review_state` représente une décision indépendante du paiement; `status` est l'état de cycle de vie. Les changements éditoriaux après soumission créent une nouvelle version de contenu à modérer; le contenu publié reste figé. Historique `ListingTransition(id, listing_id, from_status, to_status, actor_id nullable, reason, occurred_at)`.

### payments.Payment
`id UUID PK, listing_id FK, amount_xaf INT CHECK(amount_xaf>0), currency CHAR(3) DEFAULT 'XAF', method ENUM(MANUAL_TRANSFER,MOBILE_MONEY_MANUAL,OTHER_MANUAL), status ENUM(PENDING_PROOF,SUBMITTED,CONFIRMED,REJECTED,CANCELLED), payer_reference nullable, proof_storage_key nullable PRIVATE, submitted_at nullable, confirmed_at nullable, reviewed_by_id FK(User) nullable, review_note nullable, created_at, updated_at`.
Plusieurs tentatives possibles sur un Listing, mais **au plus un paiement confirmé** (index unique partiel `WHERE status='CONFIRMED'`). Refuser confirmation si montant ou devise ne correspondent pas à la publication. Les instructions/coordonnées du bénéficiaire doivent être administrées séparément; aucune donnée de collecte préinventée. `PaymentDecision` immuable (`payment_id, actor_id, decision, note, occurred_at`). Référence de paiement ne prouve jamais seule l'encaissement.

### moderation.ModerationReview / Report
`ModerationReview(id, listing_id FK, reviewer_id FK, decision ENUM(APPROVE,REJECT), reason, content_version, reviewed_at)`.
`Report(id, listing_id FK, reporter_id FK, reason_code, details, status ENUM(OPEN,INVESTIGATING,CLOSED), created_at, resolved_at)`.

### audit.AuditEvent
`id UUID PK, actor_id FK nullable, entity_type, entity_id UUID, action, before JSONB redacted, after JSONB redacted, request_id, ip_hash nullable, created_at`. Append-only au niveau applicatif et privilèges SQL; politique de rétention/documentation à définir; ne pas stocker mot de passe, adresse privée ou justificatif dans audit.

## 3. Contraintes et index
- FK restrictives pour historique, suppression logique de biens et utilisateurs; suppression physique selon politique légale de rétention/anonymisation.
- `INDEX Property(city_id, neighborhood_id, kind, monthly_rent_xaf)`.
- `INDEX Listing(status, starts_at, ends_at)` et `Listing(property_id, created_at DESC)`.
- `INDEX Payment(listing_id, status)`, unique partiel pour paiement confirmé.
- Un Listing référence exactement un Property et chaque Payment exactement un Listing. Un Payment confirmé ne peut financer qu'un Listing.
- L'unicité des périodes actives d'une propriété dépend de NOW() et ne se modélise pas directement avec un index partiel temporel : **verrou de Property + contrôle métier**; alternative exclusion de plages temporelles PostgreSQL évaluée ultérieurement.
- Aucune ligne sensible ne doit être accessible hors contrôles d'appartenance/permission.

## 4. États et transitions

### Listing.status (cycle)
| Origine | Destination | Déclencheur |
|---|---|---|
| DRAFT | PENDING_REVIEW | Bailleur soumet |
| PENDING_REVIEW | APPROVED | Modérateur approuve; `review_state=APPROVED` |
| PENDING_REVIEW | REJECTED | Modérateur refuse |
| REJECTED | PENDING_REVIEW | Bailleur corrige et soumet nouvelle version |
| APPROVED | ACTIVE | Service activation si paiement confirmé et aucune publication active concurrente |
| PENDING_REVIEW | ACTIVE | Service activation lorsque la revue approuve et le paiement était déjà confirmé (transition logique atomique avec APPROVED) |
| ACTIVE | EXPIRED | `now >= ends_at`, expiration idempotente |
| ACTIVE | SUSPENDED | Modération/admin |
| ACTIVE | WITHDRAWN | Bailleur/admin, motif tracé |
| DRAFT/PENDING_REVIEW/APPROVED/REJECTED | WITHDRAWN | Bailleur retire sa demande |
| SUSPENDED | WITHDRAWN | Administrateur clôture |

`SUSPENDED` n'est **pas** réactivé directement en V1 : reprise exige nouvelle décision explicite et politique de période résiduelle à arbitrer avant implémentation. `EXPIRED` et `WITHDRAWN` terminaux. Un nouveau cycle payant = nouveau Listing.

### Payment.status
`PENDING_PROOF -> SUBMITTED -> CONFIRMED | REJECTED`; `PENDING_PROOF -> CANCELLED`; `SUBMITTED -> CANCELLED` (avant examen, selon permissions); `REJECTED` est terminal et nouvelle tentative = nouveau Payment. `CONFIRMED` est terminal (toute correction via décision administrative d'exception, jamais mutation silencieuse). Administration seule confirme/rejette; auteur ne peut confirmer son propre paiement.

## 5. Invariants à tester
- `Listing.ACTIVE` => revue approuvée, paiement confirmé, dates complètes et bien disponible.
- Visible => `status=ACTIVE AND starts_at<=now<ends_at` et bien/compte autorisés.
- Une seule fenêtre active simultanée par Property.
- `Payment.CONFIRMED` = montant 2 000 XAF exactement pour la V1, une seule confirmation par Listing.
- `starts_at` est fixé une seule fois; pas de renouvellement automatique ni mutation d'une période terminée.
- City/Neighborhood cohérents et accès multi-utilisateur isolé.
