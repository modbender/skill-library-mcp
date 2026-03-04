#!/bin/bash
# Arena System Setup

ARENA_DIR="${1:-$HOME/clawd/arena}"

echo "🎭 Arena System Kurulumu"
echo "========================"
echo "Hedef klasör: $ARENA_DIR"

# Klasörleri oluştur
mkdir -p "$ARENA_DIR"/{outputs/agent,outputs/anti-agent,prompts}

# State dosyası
cat > "$ARENA_DIR/state.json" << 'EOF'
{
  "current_turn": "agent",
  "iteration": 0,
  "topic": "default",
  "active": true,
  "max_iterations": 10,
  "last_update": null
}
EOF

# Agent promptu
cat > "$ARENA_DIR/prompts/agent.md" << 'EOF'
# Agent Rolü

Sen geliştirici rolündesin. Görevin:

1. Anti-Agent'ın son raporunu oku (varsa)
2. Eleştirileri değerlendir
3. Konuyu geliştir/düzelt
4. Detaylı rapor yaz

## Kurallar
- Somut ol, belirsiz ifadelerden kaçın
- Eleştirileri ciddiye al
- Her raporda bir öncekinden ilerleme göster

## Çıktı Formatı
Raporunu `outputs/agent/iteration_N.md` olarak yaz.
EOF

# Anti-Agent promptu
cat > "$ARENA_DIR/prompts/anti-agent.md" << 'EOF'
# Anti-Agent Rolü

Sen denetçi/eleştirmen rolündesin. Görevin:

1. Agent'ın son raporunu oku
2. Zayıf noktaları bul
3. Sorgulanması gereken varsayımları belirle
4. Anti-rapor yaz

## Sorulacak Sorular
- Bu gerçekten doğru mu?
- Kanıt var mı?
- Alternatifler düşünüldü mü?
- Risk analizi yapıldı mı?
- Gözden kaçan bir şey var mı?

## Kurallar
- Yapıcı eleştiri yap, sadece yıkma
- Somut öneriler sun
- Overconfidence'ı sorgula

## Çıktı Formatı
Raporunu `outputs/anti-agent/iteration_N.md` olarak yaz.
EOF

# Heartbeat snippet
cat > "$ARENA_DIR/heartbeat-snippet.md" << 'EOF'
## 🎭 Arena Döngüsü

State dosyası: `~/clawd/arena/state.json`

### Her Heartbeat'te:
1. `state.json` oku → `active: true` mi?
2. Eğer aktifse:
   - `current_turn` kimde?
   - O rolün promptunu oku (`prompts/agent.md` veya `prompts/anti-agent.md`)
   - Karşı tarafın son raporunu oku
   - Yeni rapor yaz → `outputs/{role}/iteration_N.md`
   - `current_turn` değiştir, `iteration++`, state kaydet
3. `max_iterations`'a ulaşıldıysa `active: false` yap
EOF

echo ""
echo "✅ Kurulum tamamlandı!"
echo ""
echo "Sonraki adımlar:"
echo "1. prompts/ klasöründeki promptları düzenle"
echo "2. heartbeat-snippet.md içeriğini HEARTBEAT.md'ye ekle"
echo "3. state.json'da topic'i belirle"
echo ""
