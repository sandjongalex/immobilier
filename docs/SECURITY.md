# Sécurité, confidentialité et exploitation

## 1. Modèle de menace
Fraudes immobilières, usurpation bailleur, pièces de paiement falsifiées, accès transversal (IDOR), fuite de numéros/adresses, upload malveillant, abus de prise de contact, bruteforce, CSRF/XSS, erreurs de déploiement, perte de données, accès administrateur compromis.

## 2. Authentification/autorisation
- Django auth avec utilisateur personnalisé dès l'origine; mots de passe hachés via mécanismes Django sécurisés; politique de complexité, limitation tentatives et récupération de compte à définir.
- Sessions HttpOnly, Secure, SameSite approprié, CSRF sur écritures; pas de secrets dans JS/localStorage. Déploiement same-origin préféré.
- Décorateurs DRF + object permissions + vérifications transactionnelles du service; aucun choix de rôle privilégié par l'utilisateur.
- Accès admin/modérateur séparé de l'espace public; MFA pour comptes privilégiés fortement recommandé avant production.
- Principe moindre privilège pour comptes PostgreSQL et serveur; comptes individuels admin, jamais partagés.

## 3. Photos et justificatifs
- Images : formats autorisés JPEG/PNG/WebP; validation MIME **et contenu réel**, poids/dimensions limités, décodage + réencodage, suppression métadonnées EXIF, noms aléatoires, quotas par bien; aucune exécution de fichier.
- Photos approuvées accessibles au public via URLs prévues, stockage hors code; images non approuvées non publiques.
- Justificatifs de paiement et adresses précises **privés**, accessibles uniquement au bailleur propriétaire et administrateur habilité selon endpoint; Nginx ne doit jamais servir directement le dossier des preuves; URLs signées à durée limitée ou streaming autorisé.
- Sauvegarder et restaurer **ensemble** BD et médias; documenter suppression/rétention.
- Aucun fournisseur S3, SMS ou Mobile Money supposé actif.

## 4. API et protection données
- `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, cookies sécurisés, en-têtes de sécurité, HSTS **après test HTTPS**, redirection HTTP->HTTPS.
- Validation serveur des prix, transitions, IDs, quotas et fichiers; requêtes ORM paramétrées; contrôle CORS restrictif si domaine séparé.
- DRF throttling de base et limitation additionnelle reverse proxy pour login, contacts, uploads, rapports; anti-spam.
- Contact bailleur révélé uniquement selon consentement et authentification; ne jamais afficher adresse exacte publique par défaut.
- Collecte minimale des données, politique de conservation et effacement/anonymisation, transparence et consentement; faire valider obligations camerounaises applicables avant lancement.
- Journaliser `request_id`, action, acteur, résultat et horodatage; **jamais** mot de passe, cookie, numéro de transaction complet, justificatif, adresse privée ni données personnelles superflues.
- Pas de paiement automatisé : instructions de paiement officielles paramétrables dans l'administration, vérification humaine obligatoire, double vérification recommandée en cas de doute.

## 5. VPS Ubuntu / Nginx / Gunicorn / PostgreSQL (cible)
- Utilisateur système applicatif sans privilège, SSH par clés, firewall minimal, mises à jour, fail2ban selon besoin, services systemd avec redémarrage supervisé.
- Nginx termine TLS via certificat obtenu pour domaine réel, proxy HTTP local vers Gunicorn, sert build React et médias **publics approuvés** séparément, taille uploads limitée.
- Gunicorn worker sizing basé sur charge/RAM; Django derrière proxy de confiance configuré; PostgreSQL non exposé publiquement; identifiants secrets uniquement variables d'environnement ou secret store protégé.
- Journaux rotation/rétention, métriques basiques uptime, erreurs 5xx, latence, stockage disque, backups, expiration job.
- Ne pas sauvegarder `.env`, dumps SQL ou clés dans Git.
- Procédure de déploiement : migrations sauvegardées, health check, rollback applicatif et plan de restauration DB.

## 6. Sauvegarde et reprise
Proposition initiale : sauvegarde PostgreSQL **quotidienne**, médias **quotidiens**, copie **chiffrée hors VPS**, rétention glissante (ex. 7 quotidiennes, 4 hebdomadaires, 3 mensuelles, valeurs à approuver), vérification automatisée du résultat et test de restauration mensuel dans environnement isolé. Objectifs RPO/RTO à arrêter avant mise en production. Backup non prouvé sans restauration testée.

## 7. Audits et incidents
- Chaque approbation, rejet, confirmation, suspension, changement de rôle est append-only avec identifiant du décideur, motif et horodatage.
- Interdire modification/suppression des événements d'audit via API.
- Procédure de signalement et retrait rapide des annonces litigieuses; blocage compte au besoin.
- Avant mise en ligne : revue dépendances, scans secrets, tests authorization/IDOR/CSRF/upload, restauration backup, checklist TLS et journaux.

## 8. Questions ouvertes
CGU, politique confidentialité, responsabilité juridique, consentement contact, recours/modération, politique remboursements, durées de conservation, identification des bailleurs, acteurs habilités à confirmer les paiements.
