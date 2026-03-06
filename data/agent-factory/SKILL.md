---
name: agent-factory
description: |
  Ajan oluşturma ve ajanlar arası geçiş (v1.0.5 - chromium destekli + tüm yetenekler).
  Kullanım:
  - /create_agent İsim - Yeni ajan oluşturur ve config'e ekler
  - /switch ajan-id - Ajan değiştirir
---

# Agent Factory

Ajan yönetimi için kullanılır: ajan oluşturma ve ajanlar arası geçiş.

## 1. /create_agent Komutu

Yeni ajan oluşturmak için:

```
/create_agent Muhasebeci
/create_agent Coderman
/create_agent Analist
```

### Parametreler

- **İsim**: Ajanın görünen adı
- **Emoji**: Varsayılan: 🤖
- **Görev**: Varsayılan: "Kullanıcıya yardımcı olmak"

### Script Kullanımı

```bash
/home/ubuntu/.openclaw/workspace/skills/agent-factory/scripts/create_agent.sh \
  --id "ajan-id" \
  --name "İsim" \
  --emoji "⚙️" \
  --task "Görev tanımı"
```

### Oluşturulan Dosyalar

Script otomatik olarak oluşturur:

- IDENTITY.md - Kimlik kartı
- SOUL.md - Görev ve davranış kuralları
- USER.md - Kullanıcı bilgileri
- AGENTS.md - Çalışma kuralları
- TOOLS.md - Araçlar
- MEMORY.md - Uzun süreli hafıza
- HEARTBEAT.md - Boş (heartbeat kapalı)
- cron/README.md - Cron dosyaları için şablon
- cron/ornek.py - Örnek cron scripti

## ⚡ Tüm Ajanların Otomatik Eriştiği Yetenekler

Yeni oluşturulan her ajan aşağıdaki yeteneklere sahiptir:

### 1. Web Search (Brave API)

- Tüm ajanlar web araması yapabilir
- API Key: Gateway config'de tanımlı
- Kullanım: `web_search` tool

### 2. Browser (Chromium)

Her ajan tarayıcı kontrolü yapabilir:

#### Screenshot Almak için:

```bash
# Browser snapshot
browser action=snapshot profile=openclaw targetUrl=https://orneksite.com
```

#### Web Sayfası Taramak için:

```bash
# Sayfa içeriğini çek
browser action=open profile=openclaw targetUrl=https://orneksite.com
browser action=snapshot profile=openclaw
```

#### Etkileşim (tıklama, form doldurma):

```bash
browser action=act profile=openclaw request='{"kind": "click", "ref": "button-id"}'
browser action=act profile=openclaw request='{"kind": "type", "ref": "input-id", "text": "değer"}'
```

**Not:** `profile=openclaw` izole browser için, `profile=chrome` mevcut Chrome sekmeleri için.

### 3. Web Fetch

- Hafif HTML içerik çekme (API yanıtları için)
- Kullanım: `web_fetch` tool

### 4. Google Sheets (gog)

- Sheets okuma/yazma
- Kullanım: gog CLI

### 5. Cron Jobs

- Her ajan kendi cron job'unu oluşturabilir
- cron/ klasörü otomatik oluşturulur

## 2. /switch Komutu

Ajan değiştirmek için:

```
/switch angarya
/switch main
```

### Alternatif Yöntemler

**Telegram'da:**

- `angarya: <mesaj>` - Ajan'a doğrudan mesaj
- `/pm angarya <mesaj>` - Aynı işlev

**Sub-agent olarak:**

- "Angarya'ya şunu yaptır: ..." → Ajanı çağırır

## 3. Ajanlara Görev Gönderme

Sen benim üzerinden başka ajanlara görev gönderebilirsin:

```
Angarya'ya sor ne yapıyor
Angarya'ya şunu yaptır: çalışan servisleri kontrol et
```

## 4. Varsayılan Modeller

Yeni ajan, OpenClaw'ın ana ajanının varsayılan modellerini kullanır:

Bu modeller, OpenClaw'ın kendi varsayılan model ayarlarıdır — bu skill'i kuran herkes kendi OpenClaw'ındaki model yapılandırmasını kullanır.

## Örnek Kullanımlar

| Komut                            | Açıklama                        |
| -------------------------------- | ------------------------------- |
| `/create_agent Muhasebeci`       | Yeni ajan oluştur               |
| `/switch angarya`                | Angarya'ya geç                  |
| `angarya: merhaba`               | Angarya'ya mesaj gönder         |
| "Angarya'ya sor ne yapıyor"      | Angarya'nın durumunu kontrol et |
| "Angarya'ya şunu yaptır: ls -la" | Angarya'ya görev ver            |

## Not

- Oluşturulan ajanlar config'e otomatik eklenir
- Gateway restart gerekir: /restart
