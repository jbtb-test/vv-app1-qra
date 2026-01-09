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

- Repository cloné
- Environnement Python prêt
- Fichier `data/inputs/demo_input.csv` présent
- IA désactivée (`ENABLE_AI=0`)

---

## Script chronométré

### ⏱️ 0:00 – 0:30 — Contexte

> « Je pars d’un petit export d’exigences type DOORS ou Polarion.  
> La revue qualité est souvent manuelle, longue et dépendante des personnes.  
> L’objectif ici est de **structurer et sécuriser** cette revue,
> sans remplacer l’expertise humaine. »

*(Aucune manipulation à l’écran)*

---

### ⏱️ 0:30 – 1:00 — Lancement du pipeline

Commande exécutée :

```bash
python -m vv_app1_qra.main --verbose
```

**Le pipeline est entièrement déterministe. Aucune IA n’est utilisée pour détecter ou scorer les défauts.**

### ⏱️ 1:00 – 1:45 — Résultats CSV

Ouvrir le fichier de sortie CSV généré.

**Chaque issue est traçable : règle appliquée, sévérité, exigence concernée. C’est un support orienté audit et revue formelle.**

### ⏱️ 1:45 – 2:30 — Rapport HTML

Ouvrir le rapport HTML localement.

**Ce rapport est lisible sans outil spécifique. Il sert de support immédiat pour une revue ou un entretien.**

Points à montrer rapidement :
- statut global
- exemples d’issues détectées
- lisibilité générale

### ⏱️ 2:30 – 3:00 — Conclusion

**L’outil ne prend aucune décision. Il détecte, structure et met en évidence. La décision reste entièrement humaine.**

Optionnel :

**L’IA peut être activée uniquement pour proposer des suggestions textuelles, sans impact sur les résultats.**

APP1 QRA est un outil d’aide à la revue qualité :
- déterministe
- traçable
- démontrable
- défendable en audit

**L’ingénieur V&V reste au centre de la décision.**