#!/usr/bin/env python3
"""
REL-050 (back/server/doc/architecture/27-backlog-automatisation-release.md) :
calcule le type de montee de version suggere pour ce silo, a partir de la
comparaison d'API binaire (REL-030, japicmp) et, a titre indicatif, des
messages de commit depuis le dernier tag (REL-020).

japicmp fait foi ; l'estimation basee sur les commits ne sert qu'a la
tracabilite et a signaler un desaccord (ex. un commit etiquete "fix:" qui
casse en realite l'API).

Regle : un element non retrocompatible (binaryCompatible="false", n'importe
quel niveau du rapport : classe, methode, champ, constructeur) -> major.
Sinon, au moins un element modifie/ajoute figure dans le rapport (le pom
configure onlyModified=true : seuls les elements changes y figurent) ->
minor. Sinon (rapport absent ou vide, ou aucune version publiee encore,
cf. ignoreMissingOldVersion) -> patch.

Ecrit version-suggestion.json a la racine du depot et un resume dans
$GITHUB_STEP_SUMMARY si disponible.
"""
import json
import os
import re
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET

MODULES = ["wealth-api", "wealth-core"]
REPO_LABEL = "Patrimoine"

BREAKING_SUBJECT_RE = re.compile(r"^[a-z]+(\([^)]+\))?!:")


def analyse_japicmp(module):
    path = Path(module) / "target" / "japicmp" / "japicmp.xml"
    if not path.exists():
        return {"module": module, "report": "absent", "verdict": "patch"}
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return {"module": module, "report": "illisible", "verdict": "patch"}
    classes = root.find("classes")
    if classes is None or len(list(classes)) == 0:
        return {"module": module, "report": "vide", "verdict": "patch"}
    breaking = any(el.get("binaryCompatible") == "false" for el in classes.iter())
    return {"module": module, "report": "present", "verdict": "major" if breaking else "minor"}


def commits_since_last_tag():
    try:
        last_tag = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0", "--match=v*"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        range_spec = f"{last_tag}..HEAD"
    except subprocess.CalledProcessError:
        last_tag, range_spec = None, "HEAD"
    subjects = subprocess.run(
        ["git", "log", "--pretty=format:%s", range_spec],
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    return last_tag, [s for s in subjects if s and not s.startswith("Merge ")]


def commit_based_guess(subjects):
    if any(BREAKING_SUBJECT_RE.match(s) or "BREAKING CHANGE" in s for s in subjects):
        return "major"
    if any(s.startswith("feat") for s in subjects):
        return "minor"
    return "patch"


def main():
    order = {"patch": 0, "minor": 1, "major": 2}
    module_results = [analyse_japicmp(m) for m in MODULES]
    japicmp_suggestion = max((r["verdict"] for r in module_results), key=lambda v: order[v])
    last_tag, subjects = commits_since_last_tag()
    commit_guess = commit_based_guess(subjects)

    result = {
        "repo": REPO_LABEL,
        "last_tag": last_tag,
        "suggestion": japicmp_suggestion,
        "source": "japicmp",
        "commit_based_guess": commit_guess,
        "mismatch": commit_guess != japicmp_suggestion,
        "modules": module_results,
        "commits_since_last_tag": subjects,
    }

    Path("version-suggestion.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(f"## REL-050 — Suggestion de version ({REPO_LABEL})\n\n")
            f.write(f"- Suggestion (japicmp, fait foi) : **{japicmp_suggestion}**\n")
            f.write(f"- Estimation à partir des commits (indicative) : {commit_guess}\n")
            if result["mismatch"]:
                f.write(
                    "- ⚠️ Les deux estimations divergent — se fier à japicmp, "
                    "pas aux messages de commit.\n"
                )
            for r in module_results:
                f.write(f"  - `{r['module']}` : rapport {r['report']}, verdict {r['verdict']}\n")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
