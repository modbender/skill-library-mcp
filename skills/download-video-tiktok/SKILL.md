---
name: openclaw
description: >
  Télécharge automatiquement la dernière vidéo (ou les N dernières) d'un compte TikTok public
  via yt-dlp. Utilise ce skill dès que l'utilisateur mentionne TikTok, un @username TikTok,
  "télécharger une vidéo TikTok", "récupérer le dernier post TikTok", "dernière vidéo d'un compte",
  "scraper TikTok", ou toute demande de download/extraction de contenu depuis TikTok.
  Fonctionne aussi pour récupérer uniquement les métadonnées (titre, hashtags, date, stats)
  sans téléchargement. À utiliser aussi quand l'utilisateur demande "télécharger un compte TikTok",
  "archiver des vidéos TikTok", ou veut automatiser la récupération de contenu TikTok.
---

# OpenClaw — TikTok Video Downloader

## Vue d'ensemble

OpenClaw permet de télécharger la dernière vidéo (ou plusieurs) d'un compte TikTok public
via **yt-dlp**. Avant tout code ou exécution, lis cette documentation complète.

## Prérequis

Vérifier et installer yt-dlp si nécessaire :

```bash
pip install -U yt-dlp --break-system-packages 2>/dev/null || pip install yt-dlp
yt-dlp --version
```

## Types d'opérations

Ce skill supporte quatre types d'opérations. Détermine lesquelles l'utilisateur souhaite :

1. **Download rapide** — Téléchargement de la dernière vidéo d'un compte
2. **Download multiple** — Téléchargement des N dernières vidéos
3. **Métadonnées seules** — Récupérer infos/stats sans télécharger la vidéo
4. **Vidéo directe** — Télécharger depuis une URL de vidéo spécifique

## Workflows

### 1. Download Rapide — Dernière vidéo d'un compte

**Quand l'utiliser :** L'utilisateur donne un @username ou une URL de profil

**Étapes :**
1. Normaliser le username (supprimer le `@` si présent)
2. Construire l'URL du profil : `https://www.tiktok.com/@{username}`
3. Récupérer les métadonnées de la dernière vidéo (`--playlist-items 1 --no-download`)
4. Afficher les infos à l'utilisateur (titre, date, durée)
5. Télécharger avec la commande optimale
6. Confirmer le succès et donner le chemin du fichier

**Commande :**
```bash
yt-dlp \
  --playlist-items 1 \
  --format "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --merge-output-format mp4 \
  --output "/home/claude/%(uploader_id)s_%(upload_date)s_%(id)s.%(ext)s" \
  "https://www.tiktok.com/@{username}"
```

**Vérifier le résultat :**
```bash
ls -lh /home/claude/*.mp4
```

### 2. Download Multiple — N dernières vidéos

**Quand l'utiliser :** L'utilisateur veut plusieurs vidéos (`--playlist-items 1-N`)

**Étapes :**
1. Demander combien de vidéos (si non précisé, défaut = 5)
2. Construire la commande avec `--playlist-items 1-N`
3. Ajouter `--download-archive` pour éviter les doublons
4. Télécharger avec progression
5. Lister les fichiers téléchargés

**Commande :**
```bash
yt-dlp \
  --playlist-items 1-{N} \
  --format "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --merge-output-format mp4 \
  --download-archive /home/claude/tiktok_archive.txt \
  --output "/home/claude/%(uploader_id)s/%(upload_date)s_%(id)s.%(ext)s" \
  "https://www.tiktok.com/@{username}"
```

### 3. Métadonnées seules

**Quand l'utiliser :** L'utilisateur veut les infos sans télécharger

**Lire :** `references/metadata.md` pour les champs disponibles et la commande complète

**Commande rapide :**
```bash
yt-dlp \
  --playlist-items 1 \
  --skip-download \
  --write-info-json \
  --print "%(uploader_id)s | %(upload_date)s | %(duration)ss | %(view_count)s vues | %(title)s" \
  "https://www.tiktok.com/@{username}"
```

### 4. Vidéo directe depuis une URL

**Quand l'utiliser :** L'utilisateur fournit une URL de vidéo directe

**Commande :**
```bash
yt-dlp \
  --format "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --merge-output-format mp4 \
  --output "/home/claude/%(uploader_id)s_%(id)s.%(ext)s" \
  "{url_de_la_video}"
```

## Gestion des erreurs courantes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `HTTP Error 403` | Rate limiting TikTok | Ajouter `--sleep-interval 3 --max-sleep-interval 6` |
| `Unable to extract` | yt-dlp obsolète | `pip install -U yt-dlp --break-system-packages` |
| `Private account` | Compte privé | Utiliser `--cookies-from-browser chrome` si connecté |
| `No video formats` | Géo-restriction | Ajouter `--geo-bypass` |
| `Sign in required` | Contenu restreint | Fournir cookies via `--cookies cookies.txt` |
| `Merge requires ffmpeg` | ffmpeg absent | `apt-get install ffmpeg -y` |

## Normalisation du username

```python
# Accepte tous ces formats :
# @moncompte  →  moncompte
# moncompte   →  moncompte
# https://www.tiktok.com/@moncompte  →  moncompte

def normalize(input_str):
    if "tiktok.com/@" in input_str:
        return input_str.split("tiktok.com/@")[-1].split("/")[0]
    return input_str.lstrip("@").strip()
```

## Fichiers de référence

Charge ces références selon le besoin :

**references/metadata.md**
- Quand : Récupération de métadonnées, champs JSON disponibles
- Contient : Tous les champs yt-dlp disponibles, formats de print, export JSON

**references/advanced.md**
- Quand : Suppression watermark, cookies, proxy, headers personnalisés
- Contient : Techniques avancées, contournement restrictions, options yt-dlp complètes

**KBLICENSE.txt**
- Quand : Questions sur les droits d'utilisation ou les CGU
- Contient : Conditions d'utilisation, usages autorisés et interdits

## Directives de sortie

- Toujours afficher les métadonnées avant le téléchargement (titre, date, durée)
- Confirmer le chemin du fichier téléchargé
- Indiquer la taille du fichier final
- En cas d'erreur, proposer la solution directement

## Exemples de requêtes

**Download rapide :**
- "Télécharge la dernière vidéo de @lecompte"
- "Récupère le dernier post TikTok de moncompte"
- "Download la dernière vidéo de https://www.tiktok.com/@user"

**Download multiple :**
- "Télécharge les 5 dernières vidéos de @user"
- "Récupère les 10 dernières vidéos du compte @toto"

**Métadonnées :**
- "Donne-moi les infos de la dernière vidéo de @user"
- "Quel est le titre et la date du dernier post de @compte"

**URL directe :**
- "Télécharge cette vidéo TikTok : https://www.tiktok.com/@user/video/123456"
