# Exigences produit — MVP

## 1. Objectif et portée
Marketplace de location directe bailleur–locataire au Cameroun; démarrage à **Yaoundé**, extension par table `City` et filtres géographiques. Plateforme d'annonces et de prise de contact, **pas** agence ni service d'encaissement des loyers.

## 2. Acteurs et autorisations métier
| Acteur | Capacités | Limites |
|---|---|---|
| Visiteur | Rechercher/consulter les annonces actives, consulter les photos, commencer une inscription | Pas de publication ou de contact authentifié |
| Locataire | Profil, recherche, consultation, contact du bailleur, signalement | Ne peut modifier annonces ou paiements |
| Bailleur | Profil, gestion de ses logements, création de publications, dépôt de preuve de paiement, suivi statuts | Ne valide pas son paiement ni sa publication |
| Modérateur | Examiner les annonces, approuver/refuser, suspendre, examiner signalements | Ne confirme pas les paiements sauf habilitation admin distincte |
| Administrateur | Gérer rôles et comptes, confirmer/refuser paiements, intervenir sur modération, consulter audit | Ne modifie pas l'historique immuable des décisions |

Un même compte peut être locataire et bailleur (rôles cumulables). Un compte non authentifié est visiteur; les rôles privilégiés sont attribués uniquement par administration. Interdire l'auto-attribution de privilèges.

## 3. Cas métier
- Un appartement indépendant = 1 `Property`; deux studios loués séparément = 2 `Property` et 2 paiements de 2 000 FCFA pour 30 jours.
- Une maison entière = 1 `Property`, même avec plusieurs pièces.
- Un bailleur peut gérer N `Property`; chacune peut avoir N `Listing` successives.
- Une période de 30 jours correspond à **30 × 24 heures**, décomptées à partir de l'activation. Une annonce approuvée à l'avance ne commence pas son délai avant le paiement ET son activation effectifs.
- Une seule publication en période active est autorisée par logement (concurrence transactionnelle et contrainte à faire respecter en service).
- Sans paiement confirmé et modération approuvée, aucune publication publique.
- Après expiration, la recherche doit l'exclure immédiatement, **même si la tâche de mise à jour des statuts n'a pas tourné**.
- Aucun renouvellement automatique : le bailleur peut demander une nouvelle publication payante, liée au logement existant.
- Les visites, la négociation, la signature, le dépôt de garantie et les loyers sont gérés hors plateforme.

## 4. MVP — parcours
1. Inscription/connexion et vérification minimale du contact (modalités précises à arbitrer; ne pas dépendre d'un fournisseur SMS en V1).
2. Bailleurs : créer/éditer un bien (type, catégorie, titre, descriptif, loyer mensuel en FCFA, ville, quartier, localisation approximative, équipements, photos).
3. Créer une publication brouillon liée au bien puis soumettre à modération et demander le paiement.
4. Le bailleur visualise les instructions de paiement **configurées par l'administrateur** (aucun numéro de collecte présupposé), transmet une référence/justificatif.
5. Un administrateur confirme/rejette le paiement après vérification hors plateforme; un modérateur approuve/rejette le contenu; activation automatique **transactionnelle à l'achèvement des deux conditions**, pour 30 jours.
6. Catalogue public : recherche ville/quartier, type, fourchette de loyer, nombre de chambres, pagination, tri récent/prix; détails du bien et photos.
7. Contact direct via téléphone ou moyen de contact explicitement consenti et révélé selon règles anti-abus; V1 sans messagerie interne.
8. Bailleur indique « loué/indisponible » et archive ou retire la publication, sans remboursement automatique.
9. Modérateur traite les signalements et peut suspendre une annonce.
10. Administration : files d'attente paiements/modération, historique, audit, supervision des expirations.

## 5. Hors périmètre V1
Paiement Mobile Money automatisé, compte séquestre, commission sur loyers, réservation de visites, bail électronique, gestion de loyer, chat intégré, géocodage tiers, recommandation IA, renouvellement automatique, agences multi-collaborateurs.

## 6. Exigences non fonctionnelles
- Interface responsive et mobile-first, faible consommation de données, photos compressées.
- API JSON UTF-8 `/api/v1/`, pagination et filtres whitelistés.
- Stockage dates UTC, rendu local `Africa/Douala`, monnaie XAF sans décimales.
- Accessibilité de base (clavier, libellés, contraste, messages d'erreur).
- Observabilité des décisions de paiement et modération.
- Durée de recherche déterminée par les dates UTC, et non par une tâche asynchrone.
- Pas d'information de paiement sensible dans les journaux ou URL.

## 7. Risques métier et contre-mesures
| Risque | Mesure prévue |
|---|---|
| Faux bailleurs, annonces frauduleuses | Modération, signalement, vérification de contact, politique de suspension |
| Faux justificatifs, doubles validations | Validation admin, références contrôlées, journal d'audit, transaction et idempotence |
| Confusion logement/publication | Modèle séparé et règles par unité indépendante |
| Deux annonces simultanées du même bien | Verrou de ligne transactionnel + validation explicite |
| Visibilité malgré expiration | Prédicat temporel sur chaque requête publique |
| Divulgation de téléphone, adresse exacte | Consentement, adresse approximative publique, contrôles de débit |
| Litige bailleur–locataire | CGU explicites; plateforme intermédiaire d'annonces |
| Contenu illicite ou images non autorisées | Moderation et retrait, limitation fichiers |
| Erreur sur l'« abonnement » | Prix et expiration transparents, aucun débit récurrent |

## 8. Critères d'acceptation produit
- 2 logements indépendants => 2 publications et 2 paiements distincts.
- 1 maison entièrement louée => 1 logement publiable.
- `APPROVED` seul ou `CONFIRMED` seul ne rend pas l'annonce visible.
- `ends_at <= now` => aucune apparition publique, même sans job.
- Une nouvelle période conserve tout l'historique précédent.
- Bailleurs et locataires ne peuvent gérer les données d'autrui.
- Les opérations bail/loyer restent hors plateforme.

## 9. Décisions à confirmer avant développement
Protocole de paiement manuel et bénéficiaire officiel; preuve requise ou référence suffisante; durée de conservation des justificatifs; politique de remboursement; affichage des contacts; exigences d'identification des bailleurs; conditions d'utilisation et traitement des données personnelles au Cameroun.
