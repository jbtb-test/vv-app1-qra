# APP1 QRA — Setup & Dependencies (notes internes)

Ce document explique la structure **propre et professionnelle** de l’installation et des dépendances de **APP1 QRA**.

Objectifs :
- dépôt **installable**
- **reproductible**
- **audit-friendly**
- **sans fuite de secrets**

Ce socle est volontairement **industriel** et sera répliqué tel quel sur :
- APP2 — TCTC
- APP3 — AITA

---

## 1. Packaging — `pyproject.toml` (source of truth runtime)

### Rôle
`pyproject.toml` est la **référence officielle** pour :
- rendre l’application installable (`pip install -e .`)
- supporter le layout `src/` (pas de `PYTHONPATH`)
- définir les dépendances **runtime strictement nécessaires**

### Choix d’architecture
- Runtime **minimal** : l’outil fonctionne sans IA
- IA **optionnelle**, activable via *extras*

### Exemples d’installation
Installation nominale (sans IA) :
```bash
pip install -e .
Installation avec IA :
```

Installation avec IA :
```bash
pip install -e ".[ai]"
```

Intérêt V&V / recruteur
- Installation Python standard
- Aucun couplage IA forcé
- Comportement reproductible en CI
- Séparation claire runtime / expérimental

---

## 2. Dépendances dev/test — requirements.txt
Rôle
- requirements.txt contient uniquement les dépendances dev / test / outillage :
- framework de tests (pytest)
- dépendances optionnelles testables (openai)
- outils futurs (lint, quality, coverage…)

**Ce fichier ne définit pas le runtime.**

Pourquoi cette séparation
- pyproject.toml → exécution de l’application
- Commande standard
```bash
pip install -r requirements.txt
```

---

## 3. Snapshot d’environnement — requirements.lock.txt
Rôle
requirements.lock.txt est une photographie d’environnement, générée via pip freeze.

Il sert à :
- diagnostiquer un problème précis
- reproduire une démo donnée
- prouver l’environnement exact utilisé

Ce fichier n’est pas la source officielle des dépendances.

**Point important (editable install)**
Quand l’application est installée avec :

```bash
pip install -e .
pip freeze peut produire une ligne du type :
-e git+https://...#egg=vv_app1_qra
```

**👉 Cette ligne ne doit jamais être versionnée.**

Génération recommandée (Windows PowerShell)
Commande filtrée et sûre :

```powershell
pip freeze | Where-Object { $_ -notmatch '^-e\s' } | Set-Content -Encoding utf8 requirements.lock.txt
```

Règle de gestion
- requirements.lock.txt = informatif / interne
- ignoré par Git
- régénérable à tout moment

---

## 4. Secrets & environnement — .env / .env.example

Principe fondamental
- Aucun secret ne doit être versionné
- Les fichiers .env* sont locaux
- Seul .env.example est public

Règles Git
```gitignore
.env
.env.*
!.env.example
```
Résultat
- .env.example : documente les variables attendues
- .env, .env.secret, .env.local : jamais commités
- sécurité garantie même en cas de fork

---

## 5. Normalisation Git — .gitattributes
Rôle
- Éviter les diffs CRLF / LF (Windows vs CI/Linux)
- Stabiliser les revues de code
- Garantir un dépôt propre multi-OS

Politique
- LF imposé pour les fichiers texte
- comportement cohérent sur toutes les machines

---

## 6. Workflow d’installation (machine vierge)
Dans le dossier vv-app1-qra/ :

```powershell
py -3.14 -m venv venv
.\venv\Scripts\Activate.ps1

python -m pip install -U pip
pip install -e .
pip install -r requirements.txt

pytest -vv
python -m vv_app1_qra.main --verbose
```

Résultat attendu
- Tests : PASS
- Outputs générés dans data/outputs/ (gitignored)
- Rapport HTML généré localement
- Aucun artefact polluant le dépôt

---

## 7. Conventions retenues (APP1 → APP2 → APP3)
- pyproject.toml : runtime minimal + extras optionnels
- requirements.txt : dev / test
- requirements.lock.txt : snapshot, ignoré par Git
- .env.example versionné, secrets locaux uniquement
- layout src/ pour imports explicites
- installation éditable (pip install -e .) par défaut

---

## Conclusion
- Cette organisation garantit :
- reproductibilité
- sécurité
- lisibilité pour un recruteur
- cohérence multi-apps
- zéro dépendance cachée