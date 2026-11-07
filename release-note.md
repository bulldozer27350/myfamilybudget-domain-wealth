# Release Notes — Silo Patrimoine (domain-wealth)

Toutes les versions publiées de ce dépôt respectent la spécification [SemVer 2.0.0](https://semver.org/lang/fr/).

---

## [0.0.1] - 2026-11-07

### Type de release
**Version initiale** (mise en place et validation de la structure autonome multi-dépôts)

### Résumé
Première version stable du silo Patrimoine (`domain-wealth`), regroupant `wealth-api` et `wealth-core` avec import du BOM centralisé, cycle de build autonome et configuration de déploiement GitHub Packages.

### Changements par composant
- **`wealth-api`** : contrats, ports, interfaces de service (projection patrimoniale, évolution des placements) (aucun changement métier).
- **`wealth-core`** : moteurs de calcul purs, et persistance JPA des placements, de l'immobilier et des catégories d'actifs.

### Rétro-compatibilité & Compatibilité binaire
Non applicable : version initiale, aucune version antérieure publiée.
