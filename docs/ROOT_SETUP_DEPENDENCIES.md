# APP1 QRA — Setup & Dependencies (notes internes)

Ce document décrit l’organisation **volontairement industrielle** 
de l’installation et de la gestion des dépendances de APP1 — QRA.

Objectifs :
- dépôt installable immédiatement
- exécution reproductible
- audit-friendly
- aucune fuite de secrets

Ce socle est conçu pour être répliqué à l’identique sur :
- APP2 — TCTC
- APP3 — AITA

---

## 1. Packaging — `pyproject.toml` (source of truth runtime)

### Rôle

`pyproject.toml` est la **référence unique** pour :
- rendre l’application installable (`pip install -e ".[dev,ai]"`)
- supporter le layout `src/` sans manipulation de `PYTHONPATH`
- définir les dépendances **strictement nécessaires au runtime**

### Choix d’architecture

- Runtime **minimal** : l’outil fonctionne sans IA
- IA **optionnelle**, activable via *extras*

### Exemples d’installation

Installation nominale (sans IA) :
```bash
pip install -e ".[dev]"
```

Installation avec IA :
```bash
pip install -e ".[dev,ai]"
```

Intérêt V&V / recruteur
- Installation Python standard
- Aucun couplage IA forcé
- Comportement reproductible en CI
- Séparation claire runtime / expérimental

---

## 2. Dépendances dev/test — requirements.txt (informatif)

Rôle
- `requirements.txt` est un **document informatif** (compatibilité / rappel).
- La **source de vérité** est `pyproject.toml` (extras `dev` / `ai`).

Règle
- ✅ Installer via :
  - `pip install -e ".[dev]"`
  - `pip install -e ".[dev,ai]"`
- ❌ Ne pas utiliser l’installation via requirements.txt (ce fichier est informatif uniquement).


---

## 3. Snapshot d’environnement — requirements.lock.txt

Rôle
requirements.lock.txt est une photographie d’environnement, générée via pip freeze.

Utilisations :
- diagnostic ciblé
- reproduction d’une démonstration
- preuve d’environnement

**Ce fichier n’est pas la source officielle des dépendances.**

Point d’attention — installation éditable
Avec :
```bash
pip install -e ".[dev,ai]"

pip freeze peut produire :
-e git+https://...#egg=vv_app1_qra
```

**👉 Cette ligne ne doit jamais être versionnée.**

Génération recommandée (PowerShell)
```powershell
pip freeze | Where-Object { $_ -notmatch '^-e\s' } | Set-Content -Encoding utf8 requirements.lock.txt
```

Règle de gestion
- informatif uniquement
- **versionné** (snapshot reproductibilité)
- régénérable à tout moment


---

## 4. Secrets & environnement — .env / .env.example

Principe fondamental
- aucun secret versionné
- tous les fichiers .env* sont locaux
- seul .env.example est public

Règles Git
```gitignore
.env
.env.*
!.env.example
```

Résultat
- .env.example documente les variables attendues
- secrets toujours locaux
- sécurité garantie même en cas de fork

---

## 5. Normalisation Git — .gitattributes

Rôle
- éviter les diffs CRLF / LF
- stabiliser les revues de code
- assurer un dépôt propre multi-OS

Politique :
- LF imposé pour les fichiers texte
- comportement cohérent Windows / Linux / CI

---

## 6. Workflow d’installation — machine vierge

Dans le dossier vv-app1-qra/ :
```powershell
py -3.14 -m venv venv
.\venv\Scripts\Activate.ps1

python -m pip install -U pip
pip install -e ".[dev]"
# option IA (facultatif)
pip install -e ".[dev,ai]"

pytest -vv
python -m vv_app1_qra.main --out-dir data\outputs --verbose

```

Résultat attendu
- tests PASS
- outputs générés dans data/outputs/ (gitignored)
- rapport HTML local
- aucun artefact polluant le dépôt

---

## 7. Conventions retenues (APP1 → APP2 → APP3)

- pyproject.toml : runtime minimal + extras optionnels
- requirements.txt : dev / test
- requirements.lock.txt : snapshot (informativo), versionné pour reproductibilité
- .env.example versionné, secrets locaux uniquement
- layout src/
- installation éditable par défaut

---

## Conclusion

Cette organisation garantit :
- reproductibilité
- sécurité
- lisibilité pour un recruteur
- cohérence multi-applications
- absence totale de dépendances cachées