# Guide : Analyse du Travail

Méthodologie terrain pour le diagnostic de services.

---

## 1. Interviews Semi-Dirigées

### Préparation

- Planifier 45-60 min par entretien
- Lieu neutre si possible (pas le bureau du manager)
- Préciser le cadre : confidentialité, anonymat des verbatims
- Prendre des notes manuscrites ou PC (demander accord)

### Grille d'Entretien - Collaborateur

**Introduction (5 min)**
- Présentation mission et objectifs
- Cadre de confidentialité
- "Il n'y a pas de bonne ou mauvaise réponse"

**Parcours et rôle (10 min)**
- Pouvez-vous me décrire votre rôle ?
- Depuis combien de temps êtes-vous sur ce poste ?
- Comment s'organise une journée type ?

**Activité quotidienne (15 min)**
- Quelles sont vos tâches principales ?
- Quels outils utilisez-vous au quotidien ?
- Avec qui interagissez-vous le plus ?
- Quels sont vos pics d'activité ?

**Irritants et difficultés (15 min)**
- Qu'est-ce qui vous fait perdre du temps ?
- Quelles sont vos principales difficultés ?
- Y a-t-il des tâches que vous trouvez inutiles ou redondantes ?
- Quels sont les points de blocage récurrents ?

**Suggestions et vision (10 min)**
- Si vous pouviez changer une chose, ce serait quoi ?
- Qu'est-ce qui fonctionne bien et qu'il faut préserver ?
- Comment voyez-vous l'évolution du service ?

**Conclusion (5 min)**
- Y a-t-il autre chose que vous souhaitez partager ?
- Des questions sur la suite de la mission ?

### Grille d'Entretien - Manager

Ajouter aux questions collaborateur :
- Comment pilotez-vous l'activité de l'équipe ?
- Quels indicateurs suivez-vous ?
- Comment gérez-vous les pics et les absences ?
- Quelles sont vos relations avec les autres services ?
- Quels sont vos enjeux pour les 6-12 prochains mois ?

### Grille d'Entretien - Client Interne

- Quel est votre besoin vis-à-vis du service [X] ?
- Comment évaluez-vous la qualité du service rendu ?
- Quels sont les délais constatés ?
- Qu'est-ce qui pourrait être amélioré selon vous ?
- Avez-vous des exemples de dysfonctionnements récents ?

---

## 2. Observations Terrain

### Préparation

- Prévenir l'équipe en amont (pas d'effet surprise)
- Prévoir 1-2 jours d'immersion
- Avoir un carnet + chronomètre
- Se faire discret, observer sans interférer

### Grille d'Observation

**Environnement de travail**
- Disposition des postes
- Niveau de bruit, interruptions
- Accès aux outils/documents
- Affichages, aides visuelles

**Organisation du travail**
- Qui fait quoi ?
- Comment sont réparties les tâches ?
- Y a-t-il des files d'attente visibles ?
- Comment sont gérées les urgences ?

**Flux et circulation**
- Déplacements physiques (imprimante, archives...)
- Circulation de l'information
- Sollicitations et interruptions
- Temps d'attente observés

**Outils et SI**
- Fluidité d'utilisation
- Temps de chargement/lenteurs
- Ressaisies observées
- Contournements ("bidouilles")

**Interactions**
- Fréquence des échanges
- Canaux utilisés (oral, mail, chat)
- Sollicitations du manager
- Ambiance générale

### Chronométrage

Pour les tâches clés, mesurer :
| Tâche | Heure début | Heure fin | Durée | Interruptions | Notes |
|-------|-------------|-----------|-------|---------------|-------|
| | | | | | |

---

## 3. Analyse des Flux

### Cartographie Processus (BPMN Simplifié)

Utiliser les symboles de base :
- ⬭ Début/Fin (ovale)
- ▭ Tâche (rectangle)
- ◇ Décision (losange)
- → Flux

**Informations à capturer par étape :**
- Acteur responsable
- Outil utilisé
- Input / Output
- Délai moyen
- Taux d'erreur si connu

### Questions pour chaque processus

- Quelles sont les étapes du processus ?
- Qui intervient à chaque étape ?
- Quels sont les points de contrôle/validation ?
- Où sont les temps d'attente ?
- Y a-t-il des boucles de retour (corrections, rejets) ?
- Qu'est-ce qui déclenche le processus ?
- Qu'est-ce qui marque sa fin ?

---

## 4. Données Quantitatives

### Sources à exploiter

- Extractions SI (volumes, délais, statuts)
- Tableaux de bord existants
- Reporting managérial
- Fichiers de suivi Excel
- Données RH (effectifs, absences, turnover)

### Indicateurs à collecter

| Catégorie | Indicateur | Source | Période |
|-----------|------------|--------|---------|
| Volume | Nb dossiers traités | SI | Mensuel |
| Délai | Délai moyen de traitement | SI | Mensuel |
| Qualité | Taux d'erreur/retour | SI/Manuel | Mensuel |
| Charge | Dossiers par collaborateur | Calcul | Mensuel |
| Saisonnalité | Volume par semaine/mois | SI | 12 mois |

### Analyse

- Calculer moyennes, médianes, écarts-types
- Identifier les outliers
- Repérer les tendances et saisonnalités
- Comparer par collaborateur (attention à l'anonymat)
- Benchmarker si données disponibles

---

## 5. Synthèse et Croisement

Croiser les 4 sources pour valider les constats :

| Constat | Interview | Observation | Flux | Data | Validé |
|---------|-----------|-------------|------|------|--------|
| Délai étape X trop long | ✓ | ✓ | ✓ | ✓ | ✅ |
| Outil Y peu ergonomique | ✓ | ✓ | | | ⚠️ |

Un constat est **solide** si confirmé par au moins 2 sources.
