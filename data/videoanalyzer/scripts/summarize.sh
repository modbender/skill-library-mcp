#!/bin/bash
# Transcript'i özetle
# Usage: ./summarize.sh ./outputs/transcript.txt

TRANSCRIPT="$1"
OUTPUT="${2:-summary.md}"

if [ ! -f "$TRANSCRIPT" ]; then
    echo "❌ Transcript dosyası bulunamadı: $TRANSCRIPT"
    exit 1
fi

echo "📝 Özet oluşturuluyor..."

# Transcript'i oku ve özet için hazırla
CONTENT=$(cat "$TRANSCRIPT" | head -c 50000)

# AI'a gönder (clawdbot veya başka CLI)
cat << EOF
# Video Özeti

## İçerik

Bu transcript'i analiz et ve şunları çıkar:

1. **Ana Konular** (bullet points)
2. **Önemli Noktalar** (key takeaways)
3. **Bahsedilen İsimler/Projeler**
4. **Rakamlar/İstatistikler** (varsa)
5. **Kısa Özet** (3-5 cümle)

---

Transcript:
$CONTENT
EOF

echo ""
echo "👆 Bu prompt'u AI'a yapıştır veya:"
echo "   cat $TRANSCRIPT | clawdbot ask 'Özetle'"
