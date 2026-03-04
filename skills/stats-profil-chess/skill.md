---
name: chesscom-player-stats
description: Affiche les stats Chess.com d'un joueur (rapid/blitz/bullet + puzzles) via l'API publique.
---

# Chess.com — Player Stats

## Usage
- Demande à l'utilisateur un `username` Chess.com (ex: "erik").
- Lance le script Python local `chesscom_stats.py` avec ce username.
- Affiche un résumé clair (ratings + W/L/D) + un extrait du JSON brut si besoin.

## Workflow
1. Valider l'entrée:
   - username non vide
   - uniquement lettres/chiffres/underscore/tiret (sinon demander un username valide)
2. Exécuter:
   - `python3 chesscom_stats.py "<username>"`
3. Si erreur:
   - si "404": dire que le joueur n'existe pas ou profil non public
   - sinon afficher le message d'erreur et proposer de réessayer

## Output format (obligatoire)
- Titre: "Stats Chess.com — <username>"
- Sections (si disponibles):
  - Rapid
  - Blitz
  - Bullet
  - Puzzles
- Pour Rapid/Blitz/Bullet afficher:
  - rating actuel, best, record (win/loss/draw), last date
- Pour Puzzles afficher:
  - rating actuel, best

## Guardrails
- Ne jamais demander de mot de passe, token ou donnée privée (API publique uniquement).
- Ne pas prétendre pouvoir jouer des coups ou modifier un compte (API read-only).