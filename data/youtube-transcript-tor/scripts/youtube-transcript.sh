#!/bin/bash
# YouTube Video Transkript İndirici (Tor Proxy ile)
# Kullanım: ./youtube-transcript.sh <video_url veya_video_id> [dil_kodu]

set -e

# Varsayılan değerler
VIDEO="${1:-}"
LANG="${2:-en}"
# Ajan ID'yi al (environment variable veya parametre)
AGENT_ID="${AGENT_ID:-${3:-main}}"
OUTPUT_DIR="${OUTPUT_DIR:-/home/ubuntu/.openclaw/agents/$AGENT_ID/yt-transcripts}"
PROXY="${PROXY:-socks5://127.0.0.1:9050}"

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    echo "Kullanım: $0 <video_url veya_video_id> [dil_kodu]"
    echo "Örnek: $0 dQw4w9WgXcQ"
    exit 1
}

[ -z "$VIDEO" ] && usage

# Çıktı dizini
mkdir -p "$OUTPUT_DIR"

# Tor kontrolü
echo -e "${GREEN}Tor kontrol ediliyor...${NC}"
if ! curl -s --socks5 127.0.0.1:9050 -o /dev/null 2>/dev/null; then
    echo -e "${YELLOW}Tor başlatılıyor...${NC}"
    sudo systemctl start tor 2>/dev/null || true
    sleep 2
fi
echo -e "${GREEN}Hazır!${NC}"

# Altyazı kontrolü
echo -e "${GREEN}Altyazı türleri kontrol ediliyor...${NC}"
SUBS_INFO=$(yt-dlp --proxy "$PROXY" --list-subs "$VIDEO" 2>&1) || true

HAS_MANUAL=false
HAS_AUTO=false

if echo "$SUBS_INFO" | grep -q "Available subtitles"; then
    HAS_MANUAL=true
    echo -e "${GREEN}Manuel altyazı bulundu!${NC}"
fi

if echo "$SUBS_INFO" | grep -q "Available automatic captions"; then
    HAS_AUTO=true
    echo -e "${GREEN}Otomatik altyazı bulundu!${NC}"
fi

# İndir
echo -e "${GREEN}Altyazı indiriliyor...${NC}"

if [ "$HAS_MANUAL" = true ]; then
    echo -e "${GREEN}Manuel altyazı indiriliyor...${NC}"
    yt-dlp --proxy "$PROXY" \
        --write-subs \
        --sub-lang "$LANG" \
        --skip-download \
        --sub-format vtt \
        -o "$OUTPUT_DIR/%(title)s.%(ext)s" \
        "$VIDEO" 2>&1 | grep -v "^WARNING" || true
    
elif [ "$HAS_AUTO" = true ]; then
    echo -e "${YELLOW}Otomatik altyazı indiriliyor...${NC}"
    yt-dlp --proxy "$PROXY" \
        --write-auto-subs \
        --sub-lang "$LANG" \
        --skip-download \
        --sub-format vtt \
        -o "$OUTPUT_DIR/%(title)s.%(ext)s" \
        "$VIDEO" 2>&1 | grep -v "^WARNING" || true
else
    echo -e "${RED}Altyazı bulunamadı!${NC}"
    exit 1
fi

# En son VTT dosyasını bul
VTT_FILE=$(ls -t "$OUTPUT_DIR"/*.vtt 2>/dev/null | head -1)

if [ -z "$VTT_FILE" ]; then
    echo -e "${RED}İndirme başarısız!${NC}"
    exit 1
fi

echo -e "${GREEN}VTT dosyası: $VTT_FILE${NC}"

# Temizle
echo -e "${GREEN}Temizleniyor...${NC}"

BASENAME=$(basename "$VTT_FILE" .vtt)
OUTPUT_CLEAN="$OUTPUT_DIR/${BASENAME}_clean.txt"

python3 << PYEOF
import re

with open("$VTT_FILE", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split('\n')
clean_lines = []

for line in lines:
    line = line.strip()
    if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
        continue
    if '-->' in line:
        continue
    if not line:
        continue
    cleaned = re.sub(r'<[^>]+>', '', line).strip()
    if cleaned:
        clean_lines.append(cleaned)

unique = []
prev = ""
for line in clean_lines:
    if line != prev:
        unique.append(line)
        prev = line

clean_text = '\n'.join(unique)

with open("$OUTPUT_CLEAN", "w", encoding="utf-8") as f:
    f.write(clean_text)

print(f"Temizlendi: $OUTPUT_CLEAN")
print(f"Karakter: {len(clean_text)}, Satır: {len(unique)}")
PYEOF

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Tamamlandı!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "VTT: $VTT_FILE"
echo "Temiz: $OUTPUT_CLEAN"
