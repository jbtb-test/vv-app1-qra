# APP1 — QRA (Quality Risk Assessment) — Requirements Quality Assistant

## TL;DR — Démo en 1 phrase
Outil d’analyse qualité d’exigences (type DOORS / Polarion) qui détecte automatiquement les défauts
(ambiguïté, testabilité, critères d’acceptation) et génère un rapport HTML démontrable avec IA optionnelle et non décisionnelle.

**But :** accélérer et fiabiliser la revue qualité d’exigences (type DOORS / Polarion) grâce à un
**pipeline outillé** :
- détection de défauts via **règles déterministes**
- suggestions **optionnelles** via IA (si activée)
- génération d’outputs démontrables (CSV + HTML)

> IA = **suggestion only** (jamais décisionnelle).  
> L’application fonctionne **sans IA** (mode sûr par défaut).

---

## Problème métier (terrain)
La revue d’exigences est souvent :
- longue (volume élevé)
- hétérogène (styles variés)
- sujette à dérive (ambiguïtés, critères d’acceptation absents, non testabilité)
- difficile à démontrer rapidement en entretien (manque d’outputs visibles)

---

## Valeur apportée
- **Standardisation** : score qualité par exigence + liste d’issues typées
- **Gain de temps** : pré-filtrage automatique des défauts récurrents
- **Traçabilité** : règles documentées, tests unitaires, preuves d’exécution
- **Démo immédiate** : dataset fourni + rapport HTML consultable localement

---

## Fonctionnement (résumé pipeline)
1) **Entrée** : CSV d’exigences (format proche DOORS / Polarion)  
2) **Analyse** : règles qualité déterministes  
3) **IA (optionnelle)** : suggestions d’amélioration  
4) **Sorties** :
   - `data/demo_output.csv`
   - `data/demo_output.html`

---

## Quickstart (local)

### 1) Environnement

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / Mac
source .venv/bin/activate

pip install -r requirements.txt
pytest -q
```

### 2) Lancer la démo (sans IA)

```bash
python -m src.main --input data/demo_input.csv --out-dir data
```

**Entrée**
- `data/inputs/demo_input.csv`

**Sorties**
- `data/outputs/demo_output.csv`
- `data/outputs/demo_output.html`

Ouvrir `data/demo_output.html` dans un navigateur.


### 3) Mode IA (optionnel)

```bash
set ENABLE_AI=1
set OPENAI_API_KEY=xxxx

python -m src.main --input data/demo_input.csv --out-dir data
```


## Structure du projet

```text
vv-app1-qra/
├─ src/
├─ tests/
├─ data/
├─ docs/
├─ tools/





