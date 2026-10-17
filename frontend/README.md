# Frontend — React, Vite, TypeScript, Tailwind CSS 4

Socle d'interface statique de préparation **sans faux logements ni API simulée**. Node.js >= 22.12 et npm sont nécessaires.

## Démarrage

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Sur Windows PowerShell, remplacer `cp` par `Copy-Item`. Vite affiche l'URL locale (habituellement `http://localhost:5173`). Le proxy de développement `/api` pointe vers `VITE_DEV_PROXY_TARGET` ; il n'installe ni ne démarre Django.

## Vérifications

```bash
npm run lint
npm run typecheck
npm run test
npm run build
npm run format:check
```

`npm install` produit `package-lock.json` : **le versionner** après résolution sur une machine disposant du registre npm. L'installation réelle n'a pas été effectuée dans ce dépôt lors de sa préparation. Ne pas utiliser de variables `VITE_*` pour des clés privées : elles sont exposées au navigateur.

## Build production futur
`npm run build` produit `dist/`, à servir par Nginx. Les requêtes `/api/` devront être proxifiées vers Django sur le même domaine. Le déploiement lui-même n'est pas configuré.
