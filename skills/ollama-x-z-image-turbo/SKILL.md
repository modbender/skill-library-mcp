# Ollama x/z-image-turbo Skill

## Description
Génère des images via **Ollama** (modèle `x/z-image-turbo`) et les envoie sur WhatsApp.

## Déclenchement
Quand l'utilisateur demande de **générer/créer/dessiner une image** (ou variantes), suivre ces étapes :

### Étape 1 — Générer l'image
Exécuter via `exec` avec **pty=true** (obligatoire) :
```bash
python3 /Users/openclaw/.openclaw/skills/ollama-x-z-image-turbo/runner.py \
  --prompt "<PROMPT>" \
  --width 1024 --height 1024 --steps 20 \
  --out /Users/openclaw/.openclaw/workspace/tmp/ollama_image.png -v
```

**Important** :
- `pty=true` est **obligatoire** (Ollama nécessite un TTY)
- `timeout=120` minimum recommandé
- Ajuster `--width`, `--height`, `--steps` selon la demande

### Étape 2 — Envoyer sur WhatsApp
Utiliser l'outil **message** :
```
action: send
channel: whatsapp
to: <numéro>
message: <légende>
filePath: /Users/openclaw/.openclaw/workspace/tmp/ollama_image.png
```

## Paramètres disponibles
| Paramètre   | Défaut | Description                     |
|-------------|--------|---------------------------------|
| --prompt    | requis | Description de l'image          |
| --width     | 1024   | Largeur en pixels               |
| --height    | 1024   | Hauteur en pixels               |
| --steps     | 20     | Étapes de débruitage            |
| --seed      | aléa   | Graine pour reproductibilité    |
| --negative  | aucun  | Prompt négatif                  |
| --timeout   | 300    | Timeout en secondes             |

## Exemples de demandes utilisateur
- "Génère une image d'un chat astronaute"
- "Crée-moi une illustration d'un coucher de soleil"
- "Dessine un robot dans une forêt"
- "Fais une image de …"

## Prérequis
- Ollama actif sur `http://127.0.0.1:11434`
- Modèle installé : `x/z-image-turbo:latest`
