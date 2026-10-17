# Roadmap — phases indépendantes et testables

**Phase 0 uniquement livrée ici : documentation et décisions, sans code fonctionnel.** Toute phase suivante exige instruction explicite.

## Phase 0 — cadrage et architecture (cette livraison)
Livrables : `README.md` + six documents `docs/`. Vérifications : cohérence Property/Listing/Payment, statuts, rôle, prix 2 000 XAF, 30 jours, expiration en lecture, plan de déploiement et de tests, risques et décisions ouvertes. Validation humaine avant changement d'étape.

## Phase 1 — socle technique et CI (future)
Configurer Django/DRF, PostgreSQL, modèle User custom, React/Vite/TS/Tailwind, OpenAPI, variables d'environnement exemple sans secrets, lint/typecheck, pytest et CI. **Tests :** migration sur DB vierge, GET health, génération schéma OpenAPI, compilation frontend, pipeline vert. Aucun encaissement.

## Phase 2 — comptes, lieux et logements
Authentification par session/CSRF, rôles, City/Neighborhood (Yaoundé), Property, photos sécurisées. **Tests :** séparation entre bailleurs, validations ville/quartier, upload rejets, absence d'adresse privée dans JSON public.

## Phase 3 — publications, modération et recherche
Listing, Review, transitions métier, catalogue filtré, signalement et audit. **Tests :** aucune visibilité avant paiement; transitions illégales 409; pagination; verrouillage anti-annonces concurrentes; expiration temporelle même sans job.

## Phase 4 — paiements manuels et activation
Payment, preuve privée, confirmation admin, prix/durée figés, activation atomique et tâche de cohérence pour expiration. **Tests :** approbation et paiement dans les deux ordres; double validation; montant incorrect; tentatives multiples mais une confirmée; 2 studios = 2 paiements; nouveau cycle = nouveau Listing; aucun renouvellement auto.

## Phase 5 — finition MVP et qualité
Dashboard bailleur, consoles modérateur/admin, contact consenti, UI responsive, accessibilité, contrôles abus, performance. **Tests :** navigation mobile, actions selon rôle, parcours complet avec données factices, E2E essentiels.

## Phase 6 — préparation production VPS
Nginx/Gunicorn/Ubuntu/HTTPS/Postgres, backup et restore, rotation journaux, monitoring minimal, guide d'exploitation. **Tests :** staging HTTPS, migrations/rollback, restauration complète, sécurité et charge légère. **Déploiement réel seulement avec autorisation et ressources configurées.**

## Matrice de validation métier transverse
| Référence | Scénario | Résultat attendu |
|---|---|---|
| M01 | Maison entière | Une propriété, une publication |
| M02 | Deux studios indépendants | Deux propriétés, publications et paiements distincts |
| M03 | Modération approuvée, paiement non confirmé | Invisible |
| M04 | Paiement confirmé, modération en attente | Invisible |
| M05 | Les deux autorisations réunies | Activation atomique pour 30 × 24h |
| M06 | Requête à `now = ends_at` | Invisible immédiatement |
| M07 | Deux confirmations simultanées | Un paiement confirmé et une activation, sans chevauchement |
| M08 | Renouvellement demandé | Nouvelle publication manuelle, paiement nouveau |
| M09 | Bailleur A accède au bien B | Refus contrôlé |
| M10 | Locataire essaie de confirmer paiement | Refus |
| M11 | Retrait ou suspension | Invisible immédiatement |
| M12 | Extension à Douala | Ajouter ville sans changer les modèles |
| M13 | Justificatif paiement demandé anonymement | Refus |
| M14 | Recherche sans tâche d'expiration | Exclut toutes périodes achevées |

## Définition de « terminé » pour phase 0
- [x] Inspection du dépôt avant ajout de fichiers.
- [x] Architecture modulaire documentée, sans supposition de service externe.
- [x] Règles de facturation, activation, expiration et non-renouvellement explicites.
- [x] Schéma logique, états, contrats API et privilèges décrits.
- [x] Risques, sécurité, sauvegardes et exploitation documentés.
- [x] Phases futures avec critères de test indépendants.
- [ ] Arbitrages métier ouverts confirmés par le porteur de projet.
- [ ] Revue et approbation formelles de phase 0.

## Sujets à arbitrer AVANT phase de paiement
Canal et coordonnées officiels d'encaissement; preuve et méthode de vérification, délai de traitement, remboursement et contestations, suspension et sort des jours restants, consentement et confidentialité des contacts, procédures KYC/anti-fraude et obligations locales.
