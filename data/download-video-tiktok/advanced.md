# Techniques Avancées — OpenClaw

## Suppression du watermark

yt-dlp propose un format spécifique qui peut être sans watermark selon le créateur :

```bash
yt-dlp \
  --format "download_addr-0/bestvideo[ext=mp4]+bestaudio/best" \
  --merge-output-format mp4 \
  --output "/home/claude/%(uploader_id)s_%(id)s.%(ext)s" \
  "{url}"
```

Lister tous les formats disponibles pour vérifier :
```bash
yt-dlp -F "https://www.tiktok.com/@user/video/ID"
```

> ⚠️ La disponibilité du format sans watermark dépend des réglages du créateur de la vidéo.

---

## Cookies et authentification

### Depuis le navigateur (méthode la plus simple)
```bash
# Chrome
yt-dlp --cookies-from-browser chrome URL

# Firefox
yt-dlp --cookies-from-browser firefox URL

# Edge
yt-dlp --cookies-from-browser edge URL
```

### Depuis un fichier cookies (format Netscape)
```bash
yt-dlp --cookies /chemin/vers/cookies.txt URL
```

**Comment exporter les cookies :**
1. Se connecter à TikTok dans Chrome/Firefox
2. Installer l'extension "Get cookies.txt LOCALLY"
3. Ouvrir l'extension sur tiktok.com → exporter
4. Utiliser avec `--cookies cookies.txt`

---

## Contournement du rate limiting

```bash
yt-dlp \
  --sleep-interval 2 \
  --max-sleep-interval 5 \
  --sleep-requests 1 \
  --retries 5 \
  --fragment-retries 5 \
  --retry-sleep 5 \
  "https://www.tiktok.com/@{username}"
```

---

## Headers personnalisés

```bash
yt-dlp \
  --add-header "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  --add-header "Referer: https://www.tiktok.com/" \
  --add-header "Accept-Language: fr-FR,fr;q=0.9,en;q=0.8" \
  "{url}"
```

---

## Proxy

```bash
# SOCKS5
yt-dlp --proxy "socks5://127.0.0.1:1080" URL

# HTTP avec authentification
yt-dlp --proxy "http://user:pass@proxy.example.com:8080" URL

# Bypass géo-restriction sans proxy
yt-dlp --geo-bypass URL
```

---

## Formats vidéo — sélection avancée

```bash
# Meilleure qualité disponible (peut inclure VP9/H.265)
--format "bestvideo+bestaudio/best"

# Forcer H.264 + AAC (compatibilité maximale)
--format "bestvideo[vcodec^=avc]+bestaudio[acodec^=mp4a]/best[ext=mp4]"

# Résolution maximale 720p (économiser l'espace)
--format "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]"

# Audio seul (MP3)
--extract-audio --audio-format mp3 --audio-quality 0
```

---

## Archive — éviter les doublons

Pour des runs répétés sur un même compte :
```bash
yt-dlp \
  --playlist-items 1-20 \
  --download-archive /home/claude/tiktok_archive.txt \
  --output "/home/claude/%(uploader_id)s/%(upload_date)s_%(id)s.%(ext)s" \
  "https://www.tiktok.com/@{username}"
```

Le fichier `tiktok_archive.txt` garde trace des IDs déjà téléchargés.
Lors du prochain run, seules les nouvelles vidéos seront téléchargées.

---

## Structure des URLs TikTok

```
Profil :      https://www.tiktok.com/@{username}
Vidéo :       https://www.tiktok.com/@{username}/video/{video_id}
URL courte :  https://vm.tiktok.com/{short_id}
URL courte :  https://vt.tiktok.com/{short_id}
```

Tous ces formats sont gérés automatiquement par yt-dlp.

---

## ffmpeg — requis pour le merge audio/vidéo

Si absent :
```bash
# Ubuntu/Debian
apt-get install ffmpeg -y

# macOS
brew install ffmpeg

# Vérification
ffmpeg -version
```

---

## Débogage verbose

```bash
yt-dlp --verbose URL 2>&1 | head -50
```
