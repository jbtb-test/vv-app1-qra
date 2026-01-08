# APP1 — Validation intégration IA (1.9.2)

## Objectif

Ce document interne décrit et valide l’intégration de l’IA dans l’application **APP1 – QRA (Quality Risk Assessment)**.

Il est destiné :
- à moi-même (mémoire projet),
- à la préparation d’entretien technique,
- à justifier une intégration IA **maîtrisée, non bloquante et auditable**.

⚠️ Ce document n’est **pas destiné au recruteur** (le recruteur voit le README et les outputs).

L’objectif de la version **1.9.2** est :
- d’intégrer des **suggestions IA optionnelles** dans la CLI,
- sans jamais remettre en cause les règles déterministes,
- sans dépendance forte à la disponibilité de l’IA.

## Architecture

### Vue globale du repo
```text
vv-app1-qra/
├─ src/
│ └─ vv_app1_qra/
│ ├─ main.py # Point d’entrée CLI
│ ├─ ia_assistant.py # Suggestions IA (optionnelles)
│ ├─ rules_engine.py # Règles déterministes V&V
│ ├─ models.py # Modèles métier (Requirement, Issue…)
│ └─ exporters.py # Exports CSV / HTML
│
├─ data/
│ ├─ inputs/
│ │ └─ demo_input.csv
│ └─ outputs/
│ └─ qra_output_<timestamp>.csv / .html
│
├─ tests/
│ └─ test_*.py
│
├─ .env.secret # Clé OpenAI (non committée)
└─ README.md
```

### Principe architectural clé

- **Le moteur principal est déterministe**
- L’IA est un **module optionnel**, appelé uniquement si explicitement activé
- Aucune logique métier critique ne dépend de l’IA

## Description pipeline

### Pipeline logique (ordre strict)
```text
CSV input
↓
Parsing exigences
↓
Rules Engine (toujours exécuté)
↓
[Optionnel] IA – suggest_improvements()
↓
Fusion RULE + AI
↓
Calcul score / status
↓
Export CSV + HTML
```

### Point clé

> Les règles déterministes sont **toujours exécutées avant l’IA**.

L’IA :
- n’empêche jamais l’exécution,
- n’altère jamais le score,
- n’altère jamais le statut,
- ajoute uniquement des **suggestions textuelles**.

## Détail des CAS (0 → 4)

### CAS 0 — Baseline tests

**Objectif**  
Valider la stabilité du socle sans exécution CLI.

**Commande**
```bash
pytest -q
```

Résultat attendu
- Tous les tests passent
- Aucun accès IA
- Environnement stable

Résultat obtenu
- 33 tests OK

### CAS 1 — CLI sans IA (mode déterministe)

**Variables**
- ENABLE_AI=0
- OPENAI_API_KEY non définie

**Commande**
```bash
python -m vv_app1_qra.main --verbose
```

Comportement
- Rules Engine exécuté
- IA totalement ignorée
- Outputs générés

Résultat
- suggestions_json = RULE uniquement
- CSV et HTML générés

###  CAS 2 — IA demandée sans clé

**Variables**
- ENABLE_AI=1
- OPENAI_API_KEY absente

**Commandes (PowerShell)**
```powershell
$env:ENABLE_AI="1"; Remove-Item Env:OPENAI_API_KEY; python -m vv_app1_qra.main --verbose
```
Comportement
- Tentative IA
- Détection clé absente
- Log explicite
- Fallback propre

Résultat
- Aucun crash
- Outputs générés
- Pas de suggestions AI

###  CAS 3 — IA réelle (clé valide)

**Variables**
- ENABLE_AI=1
- OPENAI_API_KEY valide
- OPENAI_MODEL configuré

**Commandes (PowerShell)**
```powershell
# Activer l'environnement Python
.\venv\Scripts\activate.ps1

# Charger les variables OpenAI (clé + modèle) depuis .env.secret
Get-Content .env.secret | ForEach-Object {
  if ($_ -match "^\s*#") { return }
  if ($_ -match "^\s*$") { return }
  $name, $value = $_ -split "=", 2
  Set-Item -Path "Env:$name" -Value $value
}
# Activer l'IA
$env:ENABLE_AI="1"
# Lancer la CLI
python -m vv_app1_qra.main --verbose
```

Comportement
- Rules exécutées
- Appel `ia_assistant.suggest_improvements()` (suggestions textuelles uniquement)
- Suggestions IA ajoutées au résultat

Résultat
- suggestions_json contient "source":"AI"
- Suggestions combinées avec RULE
- Score inchangé

###  CAS 4 — IA invalide (clé erronée)

**Variables**
- ENABLE_AI=1
- OPENAI_API_KEY=sk-INVALID

**Commandes (PowerShell)**
```powershell
$env:ENABLE_AI="1"; $env:OPENAI_API_KEY="sk-INVALID"; python -m vv_app1_qra.main --verbose
```

Comportement
- Appel IA → erreur 401
- Exception catchée
- Fallback []
- Pipeline continue

Résultat
- Aucun crash
- Outputs générés
- Pas de suggestions AI

## Variables d’environnement

| Variable | Rôle |
|--------|------|
| ENABLE_AI | Active / désactive l’IA |
| OPENAI_API_KEY | Clé API OpenAI |
| OPENAI_MODEL | Modèle utilisé (si IA active) |


Règles
- ENABLE_AI=0 → IA totalement ignorée
- ENABLE_AI=1 + clé absente → fallback
- ENABLE_AI=1 + clé invalide → fallback
- La clé n’est jamais committée

## Règles de sécurité IA

Principes appliqués :

1. **IA non bloquante**
- Toute erreur IA est catchée
- Fallback systématique

2. **IA non décisionnelle**
- Le score est calculé uniquement par les règles
- L’IA ne modifie jamais le statut

3. **IA auditable**
- Chaque suggestion a un champ "source":"AI"
- Traçable dans le CSV

4. **IA optionnelle**
- Désactivable par variable d’environnement
- Aucun impact sur la CI

## Conclusion

L’intégration IA 1.9.2 respecte les objectifs suivants :
- ✅ Robustesse (CAS 0 → CAS 4 validés)
- ✅ Séparation claire RULE / AI
- ✅ IA non critique et non bloquante
- ✅ Résultats auditables et traçables
- ✅ Architecture défendable en contexte V&V / Safety / QA

>  L’IA agit comme un assistant expert, jamais comme un juge.

