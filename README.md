# MyFamilyBudget — Silo Patrimoine (`domain-wealth`)

Dépôt autonome contenant les contrats et l'implémentation métier du domaine **Patrimoine** de MyFamilyBudget.

## Structure des modules

- **`wealth-api`** : contrats, ports, interfaces de service (projection patrimoniale, évolution des placements). Purement JDK (sans dépendance externe Spring ni JPA).
- **`wealth-core`** : moteurs de calcul purs, et persistance JPA des placements, de l'immobilier et des catégories d'actifs.

## Compilation et tests

```bash
mvn clean verify
```

## Publication sur GitHub Packages

Les artefacts sont publiés sur GitHub Packages via le workflow GitHub Actions lors de tout push sur `main` ou création de tag `v*` :

```bash
mvn deploy
```


# Processus de release

Ce dépôt est l'un des 11 satellites Maven consommés exclusivement par
[MyFamilyBudget](https://github.com/bulldozer27350/MyFamilyBudget). Il n'a pas
d'autre consommateur : toute release ici n'a de sens que si elle est
destinée à être référencée dans le BOM de l'application
(`back/pom.xml`, property `<xxx.version>`).

## Principes

- Versionnage SemVer strict `x.y.z`, jamais de ranges ni de `LATEST`/`RELEASE`.
- En continu, `pom.xml` reste en `x.y.z-SNAPSHOT` : chaque push sur `main`
  republie ce SNAPSHOT (le job `publish-snapshot` de `ci.yml` s'en charge,
  et ne fait rien si la version n'est pas un SNAPSHOT).
- **Une release ne se décide jamais indépendamment de l'application** : ne
  taguez ce dépôt que si l'intégration a déjà été validée côté
  MyFamilyBudget (confiance insuffisante dans les tests unitaires isolés
  de ce satellite).
- Une version déjà publiée ne se réécrit jamais. Les tags `v*` sont
  protégés (GitHub Ruleset `protect-release-tags`) : suppression et
  déplacement bloqués pour tout le monde sauf un admin du dépôt en
  dernier recours. En cas d'erreur après coup, publiez une nouvelle
  version corrective plutôt que de toucher au tag existant.

## Marche à suivre pour livrer une version stable

1. **Mettre à jour `release-note.md`** : ajouter en tête du fichier une
   nouvelle section au format `## [x.y.z] - AAAA-MM-JJ` décrivant le
   contenu de la version. Le job `release` extrait automatiquement cette
   première section pour en faire le corps de la GitHub Release — sans
   cette étape, la Release sera créée avec un corps vide ou erroné.

2. **Bumper `pom.xml`** : retirer le suffixe `-SNAPSHOT`
   (ex. `0.1.0-SNAPSHOT` → `0.1.0`). Committer sur `main`.
   ```bash
   git add pom.xml release-note.md
   git commit -m "Release 0.1.0"
   git push origin main
   ```
   Le push déclenche `ci.yml` normalement ; `publish-snapshot` ne fera
   rien (la version n'est plus un SNAPSHOT), c'est attendu.

3. **Poser le tag et le pousser** :
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
   Cela déclenche le job `release` de `ci.yml` :
   - garde-fou : échoue si `pom.xml` est encore en SNAPSHOT ou si sa
     version ne correspond pas exactement au tag ;
   - build + déploiement de l'artefact release sur GitHub Packages ;
   - création de la GitHub Release, corps généré depuis `release-note.md`.

4. **Reprendre le développement en continu** : bumper `pom.xml` vers le
   SNAPSHOT suivant (ex. `0.1.1-SNAPSHOT` ou `0.2.0-SNAPSHOT` selon la
   nature des changements prévus), committer et pousser sur `main`.
   Sans cette étape, le prochain push sur `main` ne republiera plus rien
   (`publish-snapshot` exige un SNAPSHOT).

5. **Côté MyFamilyBudget** : une fois la Release confirmée ici, mettre à
   jour la property correspondante dans `back/pom.xml` (ex.
   `<xxx.version>0.1.0</xxx.version>`) et committer sur `main`. Cette
   étape est un pré-requis au garde-fou 2 de `release.yml` sur
   MyFamilyBudget (aucune property du BOM ne doit être en SNAPSHOT au
   moment du tag de l'application).

## Points de vigilance

- Le workflow échoue volontairement et explicitement en cas d'erreur
  (version SNAPSHOT au tag, version pom ≠ version du tag) : c'est un
  garde-fou, pas un bug.
- Un tag déjà poussé est protégé : pas de `git tag -f` ni de suppression
  possible en usage courant (voir Ruleset). En cas d'erreur, publiez une
  version corrective.
