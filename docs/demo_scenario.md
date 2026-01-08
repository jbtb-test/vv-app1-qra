# Scénario de démonstration — APP1 QRA (2–3 minutes)

Ce scénario est conçu pour une **démonstration courte en entretien**.
Il montre la valeur de l’outil sans prérequis techniques complexes
et **sans dépendance à l’IA** (mode par défaut).

---

## Objectif de la démo
- Illustrer la **détection automatique** des défauts de qualité d’exigences
- Montrer des **outputs concrets** (CSV + HTML)
- Insister sur la **maîtrise humaine** et la **non-décision IA**

---

## Pré-requis (avant entretien)
- Repo cloné
- Environnement Python prêt
- Fichier `data/demo_input.csv` présent
- IA désactivée (`ENABLE_AI=0`)

---

## Script chronométré

### ⏱️ 0:00 – 0:30 — Contexte
> « Je pars d’un petit export d’exigences type DOORS / Polarion.
> La revue manuelle est longue et hétérogène.
> J’utilise un outil qui **outille** la revue qualité sans remplacer l’expert. »

---

### ⏱️ 0:30 – 1:00 — Lancement
Commande exécutée :

```bash
python -m src.main --input data/demo_input.csv --out-dir data
