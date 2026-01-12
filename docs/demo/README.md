# APP1 QRA — Demo Pack (Recruteur)

Ce dossier est une **démo consultable sans exécuter le code** :
- un **input CSV**
- des **outputs** en 2 modes : **Sans IA** (défaut) / **Avec IA** (optionnel)
- (à ajouter) **captures PNG** pour lecture rapide

---

## 1) Input
- `assets/inputs/demo_input.csv`

## 2) Outputs — Sans IA (déterministe)
- HTML : `assets/outputs_no_ai/report.html`
- CSV  : `assets/outputs_no_ai/results.csv`

## 3) Outputs — Avec IA (suggestion-only)
- HTML : `assets/outputs_ai/report.html`
- CSV  : **à venir** (quand le code générera `qra_report.csv`)

## 4) Gouvernance IA (résumé)
- Par défaut : IA désactivée
- L’IA ne décide rien : elle ajoute uniquement des suggestions
- Fallback strict : si IA indisponible → aucun impact sur les résultats déterministes
