#!/bin/bash
# Agent Factory - Yeni Ajan Oluşturma Scripti
# Kullanım: ./create_agent.sh --id "ajan-id" --name "İsim" --emoji "Emoji" --task "Görev"

set -e

# Argümanları parse et
while [[ $# -gt 0 ]]; do
  case $1 in
    --id)
      AGENT_ID="$2"
      shift 2
      ;;
    --name)
      AGENT_NAME="$2"
      shift 2
      ;;
    --emoji)
      AGENT_EMOJI="$2"
      shift 2
      ;;
    --task)
      AGENT_TASK="$2"
      shift 2
      ;;
    *)
      echo "Bilinmeyen argüman: $1"
      exit 1
      ;;
  esac
done

# Zorunlu alanları kontrol et
if [[ -z "$AGENT_ID" ]] || [[ -z "$AGENT_NAME" ]]; then
  echo "Hata: --id ve --name zorunludur!"
  echo "Kullanım: ./create_agent.sh --id 'angarya' --name 'Angarya' --emoji '⚙️' --task 'Görev'"
  exit 1
fi

# ID'yi küçük harfe çevir ve özel karakterleri kaldır
AGENT_ID=$(echo "$AGENT_ID" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9_-]//g')

# Varsayılan değerler
AGENT_EMOJI="${AGENT_EMOJI:-🤖}"
AGENT_TASK="${AGENT_TASK:-Kullanıcıya yardımcı olmak}"

echo "🤖 Agent Factory - Ajan Oluşturuluyor..."
echo "   ID: $AGENT_ID"
echo "   İsim: $AGENT_NAME"
echo "   Emoji: $AGENT_EMOJI"
echo "   Görev: $AGENT_TASK"
echo ""

# Klasör yapısı - sadece ID kullan (id-workspace yerine)
WORKSPACE_DIR="/home/ubuntu/.openclaw/agents/${AGENT_ID}"
AGENT_DIR="/home/ubuntu/.openclaw/agents/${AGENT_ID}/agent"

echo "📁 Klasörler oluşturuluyor..."
mkdir -p "$WORKSPACE_DIR/memory"
mkdir -p "$WORKSPACE_DIR/sessions"
mkdir -p "$WORKSPACE_DIR/skills"
mkdir -p "$AGENT_DIR"

# IDENTITY.md
echo "📝 IDENTITY.md oluşturuluyor..."
cat > "$WORKSPACE_DIR/IDENTITY.md" << EOF
# IDENTITY.md - Kimlik

- **Name:** ${AGENT_NAME}
- **Creature:** AI asistanı
- **Vibe:** Samimi, yardımsever
- **Emoji:** ${AGENT_EMOJI}
- **Avatar:** _henüz yok_

---

Bu dosya ajanın kimlik kartıdır.
EOF

# SOUL.md
echo "📝 SOUL.md oluşturuluyor..."
cat > "$WORKSPACE_DIR/SOUL.md" << EOF
# SOUL.md - Kimlik

## Görev
${AGENT_TASK}

## Davranış
- Kullanıcıya yardımcı ol
- Samimi ve sıcak ol
- Gereksiz yere konuşma
- Öğrenmeye açık ol

## Sınırlar
- Özel bilgileri paylaşma
- Dışarıya veri gönderme
- Güvensiz işlem yapma

## Vibe
Asistan gibi değil, dijital dost gibi davran.
EOF

# USER.md
echo "📝 USER.md oluşturuluyor..."
cat > "$WORKSPACE_DIR/USER.md" << EOF
# USER.md - Kullanıcı

- **Name:** Tevfik Gülep
- **Notlar:** _Ajan bu alanı zamanla dolduracak_

---

Bu ajanın ana kullanıcısı hakkında bilgiler.
EOF

# AGENTS.md
echo "📝 AGENTS.md oluşturuluyor..."
cat > "$WORKSPACE_DIR/AGENTS.md" << EOF
# AGENTS.md

Bu ajanın çalışma klasörü. Diğer ajanlar gibi aynı kurallar geçerlidir.

## Her Session'da

1. Read SOUL.md — bu kimsin
2. Read USER.md — kime yardım ediyorsun
3. Read memory/YYYY-MM-DD.md — bugün ne olmuş

## Memory

Günlük notlar: memory/YYYY-MM.md
Uzun süreli: MEMORY.md

## Güvenlik

- Özel bilgileri sakla
- Güvensiz işlemleri reddet
EOF

# TOOLS.md
echo "📝 TOOLS.md oluşturuluyor..."
cat > "$WORKSPACE_DIR/TOOLS.md" << EOF
# TOOLS.md - Araçlar

Bu ajanın araçları. Ana ajanın araçlarıyla aynı.

## Sistem

- Gateway: systemctl ile yönetilir
- Session: Telegram ve WhatsApp üzerinden erişim

## Notlar

Ajanın kullandığı özel araçlar veya ayarlar buraya.
EOF

# MEMORY.md
echo "📝 MEMORY.md oluşturuluyor..."
cat > "$WORKSPACE_DIR/MEMORY.md" << EOF
# MEMORY.md - Uzun Süreli Hafıza

Bu ajanın uzun süreli hafızası.

---

*Boş başlangıç - zamanla dolacak*
EOF

# HEARTBEAT.md
echo "📝 HEARTBEAT.md oluşturuluyor..."
cat > "$WORKSPACE_DIR/HEARTBEAT.md" << EOF
# HEARTBEAT.md

# Keep this file empty to skip heartbeat API calls.
EOF

# BOOTSTRAP.md (varsa ana workspace'dan kopyala)
if [[ -f "/home/ubuntu/.openclaw/workspace/BOOTSTRAP.md" ]]; then
  echo "📝 BOOTSTRAP.md kopyalanıyor..."
  cp "/home/ubuntu/.openclaw/workspace/BOOTSTRAP.md" "$WORKSPACE_DIR/"
fi

# Cron klasörü oluştur (gelecekte kullanmak için)
mkdir -p "$WORKSPACE_DIR/cron"

# Cron README oluştur
cat > "$WORKSPACE_DIR/cron/README.md" << 'CRONEOF'
# Cron Dosyaları

Bu klasör {AGENT_NAME} ajanına ait cron işleri için.

## Kurallar
- Her cron dosyasının başına owner bilgisi ekle:
  ```python
  # Owner: {AGENT_ID}
  # Ajan: {AGENT_NAME}
  ```

## Örnek Kullanım
1. Bu klasöre yeni .py dosyası oluştur
2. Dosyanın başına yukarıdaki owner bilgisini ekle
3. İşlemi yaz
4. Dosyayı /home/ubuntu/.openclaw/workspace/cron/ klasörüne kopyala
5. OpenClaw cron job olarak ekle

## Not
OpenClaw cron sistemi henüz ajan başına klasör desteklemiyor.
Bu klasör gelecekteki kullanım için hazırlık niteliğindedir.
CRONEOF

# Örnek cron dosyası oluştur
cat > "$WORKSPACE_DIR/cron/ornek.py" << 'ORNEKEOF'
#!/usr/bin/env python3
"""
Örnek Cron Dosyası - Şablon

# Owner: {AGENT_ID}
# Ajan: {AGENT_NAME}

Kullanım:
1. Bu dosyayı düzenle
2. /home/ubuntu/.openclaw/workspace/cron/ klasörüne kopyala
3. OpenClaw cron job olarak ekle
"""

def main():
    print("Cron çalıştı!")
    # İşlemler buraya
    
if __name__ == "__main__":
    main()
ORNEKEOF

# Yer tutucuları değiştir
sed -i "s/{AGENT_ID}/${AGENT_ID}/g" "$WORKSPACE_DIR/cron/README.md"
sed -i "s/{AGENT_NAME}/${AGENT_NAME}/g" "$WORKSPACE_DIR/cron/README.md"
sed -i "s/{AGENT_ID}/${AGENT_ID}/g" "$WORKSPACE_DIR/cron/ornek.py"
sed -i "s/{AGENT_NAME}/${AGENT_NAME}/g" "$WORKSPACE_DIR/cron/ornek.py"

echo "✅ Cron klasörü ve örnek dosya oluşturuldu!"

echo "✅ Tüm dosyalar oluşturuldu!"

# Config'e ekle
echo ""
echo "⚙️ Config güncelleniyor..."

CONFIG_FILE="/home/ubuntu/.openclaw/openclaw.json"
TEMP_FILE="/tmp/openclaw_agent_$$.json"

# Yeni ajan object'ini oluştur (tek değişkende)
# Not: Model ayarları agents.defaults'tan gelir - buraya gerek yok
NEW_AGENT=$(jq -n \
  --arg id "$AGENT_ID" \
  --arg name "$AGENT_NAME" \
  --arg emoji "$AGENT_EMOJI" \
  '{
    id: $id,
    name: $name,
    workspace: ("/home/ubuntu/.openclaw/agents/" + $id),
    agentDir: ("/home/ubuntu/.openclaw/agents/" + $id + "/agent"),
    identity: {
      name: $name,
      emoji: $emoji
    }
  }')

# Mevcut config'i al ve yeni ajanı ekle
jq --argjson newAgent "$NEW_AGENT" \
   '.agents.list += [$newAgent]' \
   "$CONFIG_FILE" > "$TEMP_FILE" && mv "$TEMP_FILE" "$CONFIG_FILE"

echo "✅ Ajan config'e eklendi!"
echo ""
echo "🎉 Ajan '$AGENT_NAME' başarıyla oluşturuldu!"
echo ""
echo "⚠️  Gateway'i yeniden başlatmak için şunu söyle:"
echo "    'Gateway restart'"
echo ""
echo "Sonra ajanı kullanmak için:"
echo "   • /switch $AGENT_ID"
echo "   • Veya: $AGENT_ID: merhaba"
