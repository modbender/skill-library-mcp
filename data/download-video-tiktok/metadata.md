# Métadonnées TikTok — Référence yt-dlp

## Champs disponibles

### Identifiants
| Champ | Description | Exemple |
|-------|-------------|---------|
| `id` | ID unique de la vidéo | `7298765432109876543` |
| `uploader` | Nom d'affichage | `Mon Compte` |
| `uploader_id` | @username | `moncompte` |
| `webpage_url` | URL canonique | `https://www.tiktok.com/@moncompte/video/...` |

### Données temporelles
| Champ | Description | Exemple |
|-------|-------------|---------|
| `upload_date` | Date YYYYMMDD | `20240315` |
| `timestamp` | Unix timestamp | `1710460800` |
| `duration` | Durée en secondes | `28` |

### Contenu
| Champ | Description |
|-------|-------------|
| `title` | Titre / description de la vidéo |
| `description` | Description complète |
| `tags` | Liste des hashtags |
| `categories` | Catégories TikTok |

### Statistiques
| Champ | Description |
|-------|-------------|
| `view_count` | Nombre de vues |
| `like_count` | Nombre de likes |
| `comment_count` | Nombre de commentaires |
| `repost_count` | Nombre de reposts |

### Audio / Musique
| Champ | Description |
|-------|-------------|
| `track` | Titre du son utilisé |
| `artist` | Artiste |

---

## Commandes d'extraction

### Print formaté (aucun fichier créé)
```bash
# Infos essentielles
yt-dlp \
  --playlist-items 1 \
  --no-download \
  --print "%(uploader_id)s | %(upload_date)s | %(duration)ss | %(view_count)s vues" \
  "https://www.tiktok.com/@{username}"

# Titre et URL
yt-dlp \
  --playlist-items 1 \
  --no-download \
  --print "%(title)s" \
  --print "%(webpage_url)s" \
  "https://www.tiktok.com/@{username}"

# Hashtags seulement
yt-dlp \
  --playlist-items 1 \
  --no-download \
  --print "%(tags)s" \
  "https://www.tiktok.com/@{username}"
```

### Export JSON complet
```bash
yt-dlp \
  --playlist-items 1 \
  --skip-download \
  --write-info-json \
  --output "/home/claude/%(uploader_id)s_%(id)s" \
  "https://www.tiktok.com/@{username}"
# → Crée : moncompte_1234567890.info.json
```

### Lecture du JSON en Python
```python
import json

with open("moncompte_1234567890.info.json") as f:
    data = json.load(f)

print(data["title"])
print(data["upload_date"])
print(data["view_count"])
print(data.get("tags", []))
```

### N dernières vidéos — extraction titres et URLs
```bash
yt-dlp \
  --playlist-items 1-5 \
  --no-download \
  --print "%(upload_date)s | %(title).60s | %(webpage_url)s" \
  "https://www.tiktok.com/@{username}"
```

---

## Formats de nommage recommandés

```bash
# Nommage avec date et ID (évite les collisions)
--output "%(uploader_id)s_%(upload_date)s_%(id)s.%(ext)s"

# Nommage organisé par dossier
--output "%(uploader_id)s/%(upload_date)s_%(id)s.%(ext)s"

# Nommage avec titre (attention aux caractères spéciaux)
--output "%(uploader_id)s_%(title).50s_%(id)s.%(ext)s"
```

---

## Miniature seule
```bash
yt-dlp \
  --playlist-items 1 \
  --skip-download \
  --write-thumbnail \
  --output "/home/claude/%(uploader_id)s_%(id)s" \
  "https://www.tiktok.com/@{username}"
```
