# Convention de commit — Conventional Commits

Ce dépôt (silo Patrimoine) suit la convention [Conventional Commits](https://www.conventionalcommits.org/fr/).
Elle alimente l'automatisation du cycle de release du projet MyFamilyBudget (voir
`back/server/doc/architecture/27-backlog-automatisation-release.md` dans le dépôt principal
[bulldozer27350/MyFamilyBudget](https://github.com/bulldozer27350/MyFamilyBudget)) : génération du
changelog (REL-040) et choix automatique du type de montée de version (REL-050).

## Format

```
<type>(<portée optionnelle>): <description>

<corps optionnel>

<pied de page optionnel>
```

## Types autorisés

| Type | Usage |
|---|---|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction de bug |
| `docs` | Documentation uniquement |
| `style` | Mise en forme (espaces, point-virgules…), sans effet sur le comportement |
| `refactor` | Changement de code sans ajout de fonctionnalité ni correction de bug |
| `perf` | Amélioration de performance |
| `test` | Ajout ou correction de tests |
| `build` | Build, dépendances, outillage |
| `ci` | Intégration continue |
| `chore` | Tâche de maintenance ne rentrant dans aucune autre catégorie |
| `revert` | Annulation d'un commit précédent |

## Breaking change

Un changement d'API non rétrocompatible se signale de deux façons (combinables) :
- `!` juste après le type ou la portée : `feat!: ...` ou `feat(api)!: ...`
- un pied de page `BREAKING CHANGE: <description>` dans le corps du commit

## Exemples

- `fix: corrige un arrondi dans le calcul du moteur`
- `feat(api): ajoute un nouveau champ au contrat du silo Patrimoine`
- `feat(api)!: retire un champ du contrat (changement non rétrocompatible)`
- `chore: met à jour flatten-maven-plugin vers 1.6.0`
- `docs: documente la convention de commit`

## Validation

Un job de CI (`lint-commits`) vérifie automatiquement, sur chaque pull request vers `main`, que les
messages de commit respectent ce format. Les commits de fusion (`Merge ...`) sont exclus de la
vérification.
