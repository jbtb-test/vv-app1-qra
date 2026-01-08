# Avant / Après — Revue qualité des exigences

Ce document compare une **revue d’exigences manuelle classique** avec une
**revue outillée via APP1 QRA**, avec IA optionnelle et non décisionnelle.

L’objectif est d’illustrer le **gain réel**, les **limites**, et la **maîtrise humaine conservée**.

---

## Avant — Revue manuelle classique

### Processus typique
1. Lecture manuelle des exigences (DOORS / Polarion)
2. Identification des défauts à l’expérience
3. Commentaires libres ou annotations
4. Synthèse souvent orale ou non structurée

### Avantages
- Expertise humaine complète
- Compréhension métier fine
- Adaptation au contexte projet

### Limites
- ⏱️ Chronophage (volume élevé)
- ❌ Détection hétérogène selon les relecteurs
- ❌ Défauts récurrents parfois oubliés
- ❌ Peu de traçabilité formelle
- ❌ Difficile à démontrer rapidement (entretien / audit)

---

## Après — Revue outillée avec APP1 QRA

### Processus outillé
1. Export CSV des exigences
2. Lancement du pipeline QRA
3. Analyse déterministe automatique
4. (Optionnel) Suggestions IA
5. Génération d’outputs (CSV + HTML)
6. Revue humaine finale

### Avantages
- ⚡ Gain de temps immédiat
- ✔️ Détection systématique des défauts courants
- ✔️ Règles explicites, testées et traçables
- ✔️ Résultats structurés et démontrables
- ✔️ Support clair pour discussion technique

### Limites maîtrisées
- Ne remplace pas l’expertise humaine
- Ne couvre pas le contexte métier complexe
- L’IA ne prend aucune décision

---

## Rôle de l’IA (optionnelle)

- Désactivée par défaut
- Fournit uniquement des **suggestions textuelles**
- Aucun impact sur :
  - détection déterministe
  - scoring
  - décision finale

👉 L’IA est un **assistant**, pas un arbitre.

---

## Comparatif synthétique

| Critère | Revue manuelle | APP1 QRA |
|------|--------------|---------|
| Temps | Élevé | Réduit |
| Homogénéité | Variable | Stable |
| Traçabilité | Faible | Forte |
| Démonstration | Difficile | Immédiate |
| Décision humaine | Oui | Oui |
| IA décisionnelle | N/A | Non |

---

## Conclusion

APP1 QRA ne remplace pas la revue humaine.  
Il **outille**, **structure** et **sécurise** la revue qualité des exigences.

👉 L’ingénieur V&V reste **au centre de la décision**.  
👉 L’outil apporte **efficacité, cohérence et démonstrabilité**.
