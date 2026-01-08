# APP1 — QRA — Walkthrough de démonstration

## Objectif
Guider une démonstration claire et reproductible de l’outil APP1 — QRA.

## Étape 1 — Démo sans exécution (recommandée en entretien)
1. Ouvrir :
   docs/outputs_demo/qra_output_demo.html
2. Montrer :
   - le score global,
   - le statut qualité,
   - la table de synthèse,
   - le détail par exigence.

Message clé :
> Chaque exigence est analysée indépendamment avec justification explicite.

## Étape 2 — Exécution locale (optionnelle)
Commande :
```bash
python -m vv_app1_qra.main --verbose
```

Résultats générés :
- data/outputs/qra_output_<timestamp>.csv
- data/outputs/qra_report.html

Ouvrir le rapport HTML généré.

Message clé :
> Le rapport runtime est généré automatiquement et reflète l’état courant du moteur.

## Étape 3 — IA optionnelle (si demandé)

```powershell
$env:ENABLE_AI="1"
$env:OPENAI_API_KEY="your_key_here"
python -m vv_app1_qra.main --verbose
```

À montrer :
- suggestions IA clairement identifiées,
- score et statut inchangés.

Message clé :
> L’IA n’influence jamais la décision qualité.

## Conclusion
- règles déterministes prioritaires,
- IA maîtrisée,
- résultats auditables et démontrables.