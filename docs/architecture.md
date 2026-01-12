# Architecture — APP1 QRA (Quality Risk Assessment)

> Démo recruteur (sans exécuter le code) : voir `docs/demo/README.md`

## 1. Objectif

APP1 QRA est une application d’analyse de la **qualité des exigences**
(ex. exports DOORS / Polarion), basée sur un **pipeline déterministe**
avec **assistance IA optionnelle et non décisionnelle**.

L’objectif est de :

- détecter automatiquement les défauts de qualité récurrents
- appliquer des **règles explicites, testées et traçables**
- produire des résultats exploitables (CSV, HTML)
- garantir une **maîtrise humaine totale** des décisions

APP1 QRA est conçue comme un **outil d’aide à la revue**, et non comme
un moteur de décision automatisé.

---

## 2. Principes d’architecture

Principes directeurs :

- **Déterminisme prioritaire**
- **Traçabilité complète** (input → règles → output)
- **Lisibilité audit / entretien**
- **Aucune dépendance IA par défaut**
- **Exécution locale reproductible**

L’architecture privilégie la simplicité et la robustesse
plutôt que l’optimisation prématurée.

---

## 3. Vue d’ensemble du pipeline

L’application suit un **pipeline linéaire**, exécutable en ligne de commande,
inspiré d’une logique V-cycle (outillage, règles testées, résultats vérifiables).

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
```

---

## 4. Description des composants

### 4.1 Entrée — CSV exigences

- Fichier CSV standardisé (data/inputs/demo_input.csv)
- Colonnes attendues documentées
- Aucune dépendance à un outil propriétaire

### 4.2 Parser CSV

- Implémenté dans main.py
- Rôle :
	- lire le CSV
	- valider la structure minimale
	- transformer chaque ligne en objet métier
Aucune logique métier n’est appliquée à ce stade.

### 4.3 Modèles métier

- Implémentés dans models.py
- Responsabilités :
	- représenter une exigence
	- représenter une issue de qualité
	- typer la sévérité et la catégorie
Les modèles sont simples, explicites et testables.

###  4.4 Règles qualité déterministes

- Implémentées dans rules.py
- Chaque règle :
	- est explicite
	- est testée unitairement
	- produit des issues traçables
	
Exemples :
- exigence non testable
- ambiguïté lexicale
- formulation non normative

Les règles constituent le cœur décisionnel de l’application.

###  4.5 Assistance IA (optionnelle)

- Implémentée dans ia_assistant.py
- Désactivée par défaut
- Rôle strictement limité à :
	- suggérer des reformulations
	- proposer des pistes d’amélioration

Contraintes fortes :
- aucune modification automatique des données
- aucune suppression ou création d’issue
- aucune décision finale

L’IA est un outil de confort, jamais une autorité.

###  4.6 Agrégation des résultats

- Centralisation des issues par exigence
- Préparation des données de sortie
- Logique déterministe et traçable

###  4.7 Rapports

CSV
- Sortie brute exploitable
- Traçabilité maximale
- Support d’outillage externe

HTML
- Généré via report.py
- Lisible localement (sans serveur)
- Support principal de démonstration en entretien

---

## 5. Exécution

Commande principale :
```bash
python -m vv_app1_qra.main --verbose
```

Résultats :
- CSV de synthèse
- Rapport HTML
- Logs explicites

---

## 6. Non-objectifs (assumés)

APP1 QRA ne vise pas à :
- remplacer un ingénieur V&V
- certifier automatiquement une exigence
- apprendre ou modifier ses règles
- dépendre d’une IA pour fonctionner

Ces choix sont volontaires et alignés avec un usage industriel maîtrisé.

---

## 7. Positionnement entretien / audit

APP1 QRA démontre :
- une approche V&V structurée
- une maîtrise du déterminisme
- une intégration raisonnée de l’IA
- une capacité à produire des preuves concrètes

L’outil est conçu pour être compris en quelques minutes, sans prérequis techniques.
