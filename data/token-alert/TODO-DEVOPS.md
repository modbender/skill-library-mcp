# Token Alert - DevOps/Deployment TODO

**Status:** 📋 Brainstorming Required
**Priority:** Low (nach A+B Features)

---

## 🐳 1. Docker Container

**Goal:** Ein-Klick-Deployment des Token Alert Dashboards

### Requirements Analysis Needed:
- [ ] **Architecture Decision:** 
  - Standalone Container (Dashboard + Proxy)?
  - Sidecar zu Clawdbot Gateway?
  - docker-compose mit Gateway?

- [ ] **Networking:**
  - Wie erreicht Container den Gateway? (localhost vs. docker network)
  - Proxy-Server in Container oder Host?
  - Port-Mapping Strategy

- [ ] **Persistence:**
  - localStorage → Volume mounting?
  - Config-Files wohin?
  - Logs/State-Files?

- [ ] **Image Strategy:**
  - Base image: node:alpine vs. nginx:alpine?
  - Multi-stage build?
  - Image size optimization

### Open Questions:
1. Soll Container Gateway starten oder nur Dashboard?
2. Wie handlen wir Gateway-Auth-Token (ENV var vs. mounted config)?
3. Health-Checks für Container?
4. Auto-restart Policy?

---

## 🌐 2. GitHub Pages Hosting

**Goal:** Static hosting des Dashboards ohne eigenen Server

### Challenges to Solve:
- [ ] **CORS Problem:**
  - GitHub Pages = https://r00tid.github.io/token-alert
  - Gateway = http://localhost:18789
  - Browser blockt mixed content (HTTPS→HTTP)
  
- [ ] **Solutions to Research:**
  - Option A: Browser Extension (bypass CORS)
  - Option B: Cloudflare Worker als Proxy
  - Option C: User muss lokalen Proxy starten
  - Option D: Gateway muss HTTPS + CORS support

- [ ] **Deployment Flow:**
  - GitHub Actions für Auto-Deploy?
  - Versionierung der HTML-Datei?
  - Asset-Optimierung (minify)?

### Open Questions:
1. Ist GitHub Pages überhaupt sinnvoll wenn User lokalen Gateway braucht?
2. Alternative: Serve Dashboard direkt vom Gateway (Port 18789/dashboard)?
3. Electron App statt Web-Hosting?

---

## 🔄 3. Auto-Update Mechanism

**Goal:** Dashboard checkt auf neue Versionen und updated sich

### Implementation Ideas:
- [ ] **Version Check:**
  - Fetch latest from GitHub Releases API
  - Compare mit aktueller Version (in HTML meta tag?)
  - Notification wenn Update verfügbar

- [ ] **Update Strategy:**
  - Option A: In-place update (fetch new HTML + reload)
  - Option B: "Update available" Banner mit Download-Link
  - Option C: ServiceWorker für App-Cache update

- [ ] **Breaking Changes:**
  - Wie handlen wir Breaking Changes in API?
  - Migration-Scripts für localStorage?
  - Rollback-Mechanismus?

### Open Questions:
1. Wie häufig soll gecheckt werden? (Bei Start? Täglich?)
2. Auto-Update oder User-Consent?
3. Changelog-Anzeige im Dashboard?
4. Wie testen wir Updates ohne Production zu brechen?

---

## 💭 Brainstorming Session Needed

**Date:** TBD
**Participants:** Kelle + Grym
**Duration:** ~2h

### Agenda:
1. Docker Strategy & Architecture Review (30min)
2. GitHub Pages vs. Alternatives (30min)
3. Auto-Update UX/Security Discussion (30min)
4. Priority & Timeline (30min)

### Pre-Work:
- [ ] Research Docker best practices for dashboard apps
- [ ] Test GitHub Pages CORS workarounds
- [ ] Look at how other dashboards handle updates (Grafana, Prometheus, etc.)

---

## 📊 Prioritization Matrix

| Feature | User Value | Complexity | Priority |
|---------|-----------|-----------|----------|
| Docker Container | High (easy deploy) | Medium | 🟡 Medium |
| GitHub Pages | Low (CORS issues) | High | 🔴 Low |
| Auto-Update | Medium (convenience) | Medium | 🟡 Medium |

**Recommended Order:**
1. Docker Container (most valuable, reasonable effort)
2. Auto-Update (nice-to-have, not critical)
3. GitHub Pages (maybe skip if Docker works well)

---

**Next Steps:**
1. Complete A+B feature implementation first
2. Schedule brainstorming session
3. Create detailed specs based on discussion
4. Implement one-by-one with testing

---

*Last Updated: 2026-01-27*
