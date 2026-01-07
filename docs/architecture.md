# Architecture — APP1 QRA (Quality Risk Assessment)

## Objectif
APP1 QRA est une application d’analyse de la **qualité des exigences** (type DOORS / Polarion),
basée sur un pipeline déterministe, avec **assistance IA optionnelle et non décisionnelle**.

L’objectif est de :
- détecter automatiquement les défauts de qualité récurrents
- produire des résultats démontrables (CSV, HTML)
- conserver une **maîtrise humaine totale** des décisions

---

## Vue d’ensemble

L’application suit un **pipeline linéaire**, exécutable en CLI, conforme à une logique V-cycle
(outillage, règles testées, outputs traçables).

```text
CSV exigences
     |
     v
[ Parser CSV ]
     |
     v
[ Modèles métier ]
     |
     v
[ Règles qualité déterministes ]
     |
     +--------------------+
     |                    |
     v                    v
[ Issues détectées ]   [ IA (optionnelle) ]
     |                    |
     +---------+----------+
               |
               v
        [ Agrégation ]
               |
               v
        [ Rapport CSV ]
               |
               v
        [ Rapport HTML ]
               |
               v
         Revue humaine
