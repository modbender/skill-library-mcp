# TODO - Token Alert Skill

## 🎨 UI/UX Improvements

### High Priority - Icons (mit AI erstellen)

- [ ] **Custom Dashboard Icon** (statt 🔶 Emoji)
  - Hochwertiges Design
  - Passt zum Thema "Token"
  - Farblich abgestimmt (Orange/Gradient)
  - Format: SVG (skalierbar)
  - Verwendung: Dashboard Header Icon
  - Ideen:
    - Token/Münze mit Füllstand
    - Chip/Prozessor mit Progress
    - Batterie-Style mit Token-Symbol
    - Gauge/Meter Design

- [ ] **Provider Icons** (AI-generiert, hochwertig)
  - 🤖 Anthropic - Claude Logo (hochwertig)
  - 🧠 OpenAI - GPT Logo (hochwertig)
  - ✨ Gemini - Google Gemini Logo (hochwertig)
  - Konsistenter Design-Stil
  - SVG Format
  - Farblich passend zum Theme

### Provider Switching (v1.1.0)

- [ ] **Provider-Button Click Handler**
  - Abfrage: "Tracking für [Provider] starten?"
  - Bei Ja: Setup-Wizard für diesen Provider
  - API Key / Credentials abfragen
  - Provider sofort tracken
  - Anzeige aktualisieren

- [ ] **Provider-Tab Funktionalität**
  - Umschalten zwischen konfigurierten Providern
  - Zeige nur konfigurierte Provider
  - "+" Button für neue Provider
  - Inaktive Provider ausblenden

- [ ] **Model-Name vollständig anzeigen**
  - Claude: "Claude Sonnet 4.5" (statt "Sonnet")
  - OpenAI: "GPT-4 Turbo" (statt "GPT-4")
  - Gemini: "Gemini Pro 1.5" (statt "Gemini")
  - Versionsnummer immer dabei

## 🔧 Features

### v1.1.0
- [ ] OpenAI API Implementation
  - Token tracking via API
  - Model limits konfigurierbar
  - Rate limit tracking

- [ ] Gemini API Implementation
  - Token tracking via API
  - Model limits konfigurierbar

- [ ] Multi-Provider Aggregate View
  - Gesamt-Übersicht aller Provider
  - Combined token usage
  - Beste/Schlechteste Provider

### v1.2.0
- [ ] Historical Usage Tracking
  - Token usage über Zeit
  - Tages/Wochen/Monats-Charts
  - Export zu CSV/JSON

- [ ] Web Scraping Fallback
  - Claude.ai (Browser + OCR/DOM)
  - ChatGPT Plus (Browser)
  - Session Cookie Management

### v2.0.0
- [ ] Real-time Notifications
  - Push notifications via Telegram
  - Desktop notifications
  - Sound alerts (optional)

- [ ] Advanced Analytics
  - Token cost calculator
  - Provider comparison
  - Usage predictions

## 🐛 Bugs

Keine bekannten Bugs.

## 📝 Documentation

- [ ] Video Tutorial (Dashboard Demo)
- [ ] Provider Setup Guide (mit Screenshots)
- [ ] Best Practices Artikel

## 🔒 Security

- [ ] API Key Encryption
- [ ] Session Token Security Audit
- [ ] Config File Permissions Check

---

**Priorität:** Custom Icon > OpenAI/Gemini Implementation > Historical Tracking
