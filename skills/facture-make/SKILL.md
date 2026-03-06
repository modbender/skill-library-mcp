---
name: "Skill: Facture Make"
description: Ce skill permet de générer et d'envoyer des factures
  professionnelles vers Make.com après une étape de confirmation humaine.
---

# Skill: Facture Make

Ce skill permet de générer et d'envoyer des factures professionnelles vers Make.com après une étape de confirmation humaine.

## Utilisation

Déclenchez ce skill lorsque l'utilisateur exprime l'intention de créer une facture.
- "crée une facture"
- "générer une facture pour [X] jours"
- "fais une facture pour le client [NOM]"

## Flux de travail (Workflow)

1. **Préparation** : Appeler `prepare_invoice.py`. Ce script calcule les montants et prépare le libellé.
2. **Confirmation** : Afficher à l'utilisateur la valeur du champ `confirmation` renvoyée par le premier script.
3. **Envoi** : Si l'utilisateur confirme, appeler `send_invoice.py` en lui passant **uniquement** l'objet JSON contenu dans la clé `invoice`.

## Spécifications Techniques

### 1. Script de préparation : `prepare_invoice.py`
- **Rôle** : Reçoit les détails (jours, client) et retourne un JSON.
- **Format de sortie attendu** :
```json
{
  "invoice": {
    "client": "Nom du client",
    "jours": 3,
    "tjm": 280,
    "libelle": "Consulting Février 2026",
    "total": 840
  },
  "confirmation": "Texte de confirmation à lire à l'utilisateur"
}

## Réponse finale
Réponds exclusivement par : "Envoi confirmé."
