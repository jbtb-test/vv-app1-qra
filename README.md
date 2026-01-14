# APP1 — QRA (Quality Risk Assessment) — Requirements Quality Assistant

## TL;DR — Démo en 1 phrase
Outil d’analyse qualité d’exigences (type DOORS / Polarion) qui détecte automatiquement les défauts
(ambiguïté, testabilité, critères d’acceptation) et génère un rapport HTML démontrable avec IA optionnelle et non décisionnelle.

**But :** accélérer et fiabiliser la revue qualité d’exigences grâce à un **pipeline outillé** :
- détection de défauts via **règles déterministes**
- suggestions **optionnelles** via IA
- génération d’outputs démontrables (CSV + HTML)

> IA = **suggestion only** (jamais décisionnelle).
> L’application fonctionne **sans IA** par défaut.

---

## Problème métier
La revue d’exigences est souvent :
- longue et manuelle
- hétérogène (styles variables)
- sujette aux ambiguïtés et défauts de testabilité
- difficile à démontrer rapidement en entretien

## Valeur apportée
- **Standardisation** : score qualité + issues typées par exigence
- **Gain de temps** : pré-filtrage automatique des défauts récurrents
- **Traçabilité V&V** : règles explicites, tests unitaires, décisions auditables
- **Démo portfolio** : aperçu immédiat (PNG) + rapport HTML consultable sans exécution

---

## Fonctionnement (pipeline résumé)

1) **Entrée**  
   CSV d’exigences (format proche DOORS / Polarion)

2) **Analyse déterministe**  
   Règles qualité (ambiguïté, testabilité, critères d’acceptation)

3) **IA (optionnelle)**  
   Suggestions textuelles d’amélioration (non décisionnelles)

4) **Sorties**
   - Rapport CSV (audit)
   - Rapport HTML (consultable)
   - Revue humaine finale

> L’IA est **optionnelle**, **non bloquante**, et **n’influence jamais le score**.

---

## Installation (local)

```bash
python -m venv venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
# option IA
pip install -e ".[dev,ai]"
```

## Tests (CI-friendly)
```bash
pytest -vv
```

---

## Quickstart

### Option A — Démo sans exécution (portfolio)

Démonstration **clé en main pour recruteur**, sans installer ni exécuter Python.

Ouvrir :
- `docs/demo/README.md`

Accès direct :
- **Sans IA (moteur déterministe)**  
  `docs/demo/assets/outputs_no_ai/rapport.html`
- **Avec IA (suggestions gouvernées)**  
  `docs/demo/assets/outputs_ai/rapport.html`

Des captures d’écran sont disponibles dans :
`docs/demo/assets/screenshots/`

### Option B — Reproduire localement (sans IA, recommandé pour démonstration déterministe)

Cette option correspond au mode nominal de l’outil (100 % déterministe).

```bash
python -m vv_app1_qra.main --out-dir data/outputs --verbose
```

Génère automatiquement :
- `data/outputs/qra_output_<timestamp>.csv`
- `data/outputs/qra_output_<timestamp>.html`

Ouvrir le fichier HTML généré dans un navigateur.

### Option C — Mode IA (optionnel, avancé)

Copier `.env.example` en `.env` et renseigner les valeurs localement.  
⚠️ Ne jamais committer `.env` / `.env.*` (seul `.env.example` est versionné).


```powershell
. .\tools\load_env_secret.ps1
$env:ENABLE_AI="1"
python -m vv_app1_qra.main --out-dir data\outputs --verbose
```

> L’IA fournit uniquement des suggestions textuelles.
> Elle ne modifie ni le score ni le statut des exigences.

---

## Structure du projet

```text
vv-app1-qra/
├─ src/
│  └─ vv_app1_qra/
├─ tests/
├─ data/
│  └─ inputs/
├─ docs/
│  └─ demo/
└─ README.md
```

