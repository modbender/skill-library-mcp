# Template : Matrice Impact / Effort

## Principe

Outil de priorisation visuel permettant de classer les actions selon deux axes :
- **Impact** : Bénéfice attendu (gain de temps, qualité, satisfaction...)
- **Effort** : Ressources nécessaires (temps, coût, complexité...)

---

## La Matrice

```
                            IMPACT
                    Faible          Fort
                ┌───────────┬───────────┐
                │           │           │
        Faible  │  À        │  QUICK    │
                │  ÉCARTER  │  WINS     │
                │           │  ⭐⭐⭐    │
   EFFORT       ├───────────┼───────────┤
                │           │           │
        Fort    │  À        │  PROJETS  │
                │  ÉVITER   │  MAJEURS  │
                │           │  ⭐⭐      │
                └───────────┴───────────┘
```

---

## Quadrants Expliqués

| Quadrant | Impact | Effort | Stratégie |
|----------|--------|--------|-----------|
| **Quick Wins** ⭐⭐⭐ | Fort | Faible | Prioriser immédiatement. Gains rapides, créent de la dynamique. |
| **Projets Majeurs** ⭐⭐ | Fort | Fort | Planifier soigneusement. Nécessitent ressources mais ROI important. |
| **À écarter** ⭐ | Faible | Faible | Faire si temps disponible. Faible valeur ajoutée. |
| **À éviter** ❌ | Faible | Fort | Ne pas faire. Mauvais ratio coût/bénéfice. |

---

## Grille d'Évaluation

### Évaluer l'IMPACT (1 à 5)

| Score | Niveau | Critères |
|-------|--------|----------|
| 5 | Très fort | Gain majeur sur KPI clé (>30%), transformation visible |
| 4 | Fort | Gain significatif (15-30%), amélioration notable |
| 3 | Moyen | Gain modéré (5-15%), amélioration perceptible |
| 2 | Faible | Gain marginal (<5%), peu perceptible |
| 1 | Très faible | Gain négligeable ou incertain |

**Critères d'impact possibles :**
- Réduction délai de traitement
- Gain en ETP / charge de travail
- Réduction taux d'erreur
- Amélioration satisfaction client/collaborateur
- Conformité réglementaire
- Réduction des risques

### Évaluer l'EFFORT (1 à 5)

| Score | Niveau | Critères |
|-------|--------|----------|
| 1 | Très faible | < 1 jour, pas de budget, autonomie équipe |
| 2 | Faible | 1-5 jours, budget minime, peu de dépendances |
| 3 | Moyen | 1-4 semaines, budget modéré, quelques dépendances |
| 4 | Fort | 1-3 mois, budget conséquent, nombreuses dépendances |
| 5 | Très fort | > 3 mois, budget élevé, projet complexe |

**Critères d'effort possibles :**
- Temps de mise en œuvre
- Coût financier
- Compétences requises
- Dépendances (SI, autres services, prestataires)
- Conduite du changement nécessaire
- Risques de mise en œuvre

---

## Matrice à Compléter

| ID | Action | Impact (1-5) | Effort (1-5) | Score | Quadrant | Priorité |
|----|--------|--------------|--------------|-------|----------|----------|
| A01 | | | | | | |
| A02 | | | | | | |
| A03 | | | | | | |
| A04 | | | | | | |
| A05 | | | | | | |

**Calcul du Score** : Impact / Effort (plus c'est élevé, plus c'est prioritaire)

**Classification automatique :**
- Impact ≥ 4 et Effort ≤ 2 → Quick Win
- Impact ≥ 4 et Effort > 2 → Projet Majeur
- Impact < 4 et Effort ≤ 2 → À écarter
- Impact < 4 et Effort > 2 → À éviter

---

## Exemple Rempli

| ID | Action | Impact | Effort | Score | Quadrant | Priorité |
|----|--------|--------|--------|-------|----------|----------|
| A01 | Créer template réponse standard | 4 | 1 | 4.0 | Quick Win | 1 |
| A02 | Former équipe nouvel outil | 4 | 3 | 1.3 | Projet Majeur | 3 |
| A03 | Réorganiser archivage | 2 | 2 | 1.0 | À écarter | 5 |
| A04 | Refonte SI métier | 5 | 5 | 1.0 | Projet Majeur | 4 |
| A05 | Simplifier circuit validation | 5 | 2 | 2.5 | Quick Win | 2 |
| A06 | Changer mobilier bureau | 1 | 3 | 0.3 | À éviter | ❌ |

---

## Visualisation pour Présentation

```
        ┌─────────────────────────────────────────────┐
        │                 IMPACT FORT                 │
        │                                             │
        │   A01 ●────────────────────────● A04        │
        │   Template                      Refonte SI  │
        │                                             │
        │   A05 ●────────────────● A02                │
        │   Circuit valid.        Formation           │
        │                                             │
EFFORT  ├─────────────────────────────────────────────┤
FAIBLE  │                 IMPACT FAIBLE         EFFORT│
        │                                        FORT │
        │                                             │
        │   A03 ●────────────────────────● A06        │
        │   Archivage                     Mobilier    │
        │                                             │
        └─────────────────────────────────────────────┘
```

---

## Conseils d'Animation

1. **En atelier collectif** : Chaque action est évaluée par le groupe (consensus ou vote)
2. **Utiliser des post-its** : Placer physiquement les actions sur un tableau
3. **Débattre des scores** : Les désaccords révèlent des perceptions différentes
4. **Réévaluer régulièrement** : L'effort/impact peut changer avec le temps
5. **Ne pas surcharger** : Max 15-20 actions par matrice pour lisibilité
