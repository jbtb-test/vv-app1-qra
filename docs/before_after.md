# Avant / Après — Revue qualité des exigences

Ce document compare une **revue d’exigences manuelle classique**
avec une **revue outillée via APP1 QRA**.

L’objectif est d’illustrer :
- les **gains concrets**
- les **limites assumées**
- la **maîtrise humaine conservée**

---

## Avant — Revue manuelle classique

### Processus typique

1. Consultation des exigences dans un outil (DOORS, Polarion)
2. Lecture individuelle ou en séance de revue
3. Détection des défauts basée sur l’expérience
4. Commentaires libres (outil, Excel, mail)
5. Synthèse variable selon les projets

### Avantages

- Expertise humaine complète
- Compréhension métier et projet fine
- Capacité d’arbitrage contextuel

### Limites observées

- ⏱️ Revue longue sur des volumes importants
- ❌ Variabilité forte entre relecteurs
- ❌ Défauts récurrents parfois non détectés
- ❌ Traçabilité hétérogène
- ❌ Démonstration difficile en audit ou entretien

---

## Après — Revue outillée avec APP1 QRA

### Processus outillé

1. Export CSV des exigences
2. Exécution locale du pipeline APP1 QRA
3. Application de règles qualité **déterministes**
4. (Optionnel) Suggestions IA non décisionnelles
5. Génération d’outputs structurés (CSV + HTML)
6. Revue humaine finale et décision

### Avantages concrets

- ⚡ Réduction immédiate du temps de revue
- ✔️ Détection systématique des défauts standards
- ✔️ Règles explicites, testées et traçables
- ✔️ Résultats reproductibles
- ✔️ Support clair pour revue, audit ou entretien

### Limites maîtrisées

- Ne remplace pas l’analyse métier
- Ne couvre pas les décisions de conception
- Ne prend aucune décision automatique

---

## Rôle de l’IA (optionnelle)
- Désactivée par défaut
- Fournit uniquement :
  - des suggestions de reformulation
  - des pistes d’amélioration

L’IA :
- n’ajoute pas d’issues
- ne modifie pas les résultats
- n’influence pas la décision finale

👉 Elle agit comme **assistant**, jamais comme arbitre.

---

## Comparatif synthétique

| Critère | Revue manuelle | APP1 QRA |
|------|--------------|---------|
| Temps | Élevé | Réduit |
| Homogénéité | Variable | Stable |
| Traçabilité | Faible | Forte |
| Reproductibilité | Faible | Élevée |
| Démonstration | Complexe | Immédiate |
| Décision humaine | Oui | Oui |
| IA décisionnelle | N/A | Non |

---

## Conclusion

APP1 QRA ne remplace pas la revue humaine.  
Il **structure**, **sécurise** et **accélère** la revue qualité.

👉 L’ingénieur V&V reste **responsable de la décision**  
👉 L’outil apporte **cohérence, traçabilité et démonstrabilité**
