# Developer Transparency - AgentShield Architecture

> **"Trust through Transparency"** - Vollständige Offenlegung unserer Infrastruktur

---

## 🏗️ Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────────────┐
│                     YOUR LOCAL ENVIRONMENT                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Your Agent   │  │ AgentShield  │  │ 52+ Security Tests   │ │
│  │ (OpenClaw)   │→ │ Skill        │→ │ (Local Subagents)    │ │
│  │              │  │ (Installed)  │  │                      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│         │                                               │      │
│         │  Ed25519 Key Generation (Local)               │      │
│         │  Challenge Signing (Local)                    │      │
│         │  PDF Generation (Local)                       │      │
│         └───────────────────────────────────────────────┘      │
│                              │                                  │
│                              │  NUR Public Key + Challenge      │
│                              │  (Keine Prompts, Kein Code)      │
│                              ▼                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │  HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              AGENTSHIELD REGISTRY (Heroku/Dev)                 │
│  • Certificate ID (Public Key Hash)                            │
│  • Trust Score (Berechnet aus Challenge-Responses)             │
│  • Revocation Status (CRL)                                     │
│  • Verification History                                        │
│                                                                 │
│  ❌ KEINE Prompts                                              │
│  ❌ KEIN Agent Code                                            │
│  ❌ KEINE Test-Ergebnisse                                      │
│  ❌ KEINE Nutzerdaten                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔴 WICHTIG: Entwickler-Hinweise

### 1. Heroku-Server Status

> **⚠️ DEV ENVIRONMENT**
> 
> Der aktuelle Heroku-Server (`agentshield-api-bartel-...herokuapp.com`) ist eine **Entwicklungsumgebung**.
>
> **Roadmap:**
> - **Q2 2026:** Migration zu dedizierter Infrastruktur (Hetzner/AWS)
> - **Q3 2026:** Multi-Region Deployment (EU, US, APAC)
> - **Q4 2026:** Self-Hosted Registry für Enterprise
>
> **Für Contributors:**
> - Der Server-Code ist Open Source (siehe `server/` Ordner)
> - Du kannst den Registry-Server lokal selbst hosten
> - API ist vollständig dokumentiert für eigene Implementierungen

### 2. Daten-Flow Transparenz

**Was der Server NIEMALS sieht:**

| Daten | Status | Grund |
|-------|--------|-------|
| 🚫 Agent Prompts | **NIEMALS** | Tests laufen lokal |
| 🚫 Interner Code | **NIEMALS** | Kein Upload |
| 🚫 Test-Ergebnisse | **NIEMALS** | PDF bleibt lokal |
| 🚫 Kommunikationsdaten | **NIEMALS** | Nur Public Key |
| 🚫 System-Logs | **NIEMALS** | Lokale Subagents |

**Was der Server SIEHT:**

| Daten | Status | Verwendung |
|-------|--------|------------|
| ✅ Public Key (Ed25519) | **ÖFFENTLICH** | Certificate Registry |
| ✅ Challenge-Response | **ÖFFENTLICH** | Identitäts-Verifikation |
| ✅ Timestamp | **ÖFFENTLICH** | Audit Trail |
| ✅ Trust Score | **ÖFFENTLICH** | Reputation System |

### 3. Zero-Knowledge-Verifikation

Wir nutzen **kryptographische Beweise** statt Daten:

```javascript
// Dein Agent generiert lokal:
const keypair = Ed25519.generateKeyPair();
const publicKey = keypair.public;   // → An Server
const privateKey = keypair.private; // ← Bleibt lokal!

// Challenge-Response (Zero-Knowledge):
const challenge = "random_nonce_123";
const signature = sign(challenge, privateKey); // Lokal signiert!
verify(signature, challenge, publicKey);       // Server prüft nur
```

**Der Server kann die Signatur prüfen, OHNE den Private Key zu kennen.**

---

## 🎯 Für Entwickler & Contributors

### Lokale Entwicklung

**Ohne Server-Verbindung testen:**
```bash
# 1. Lokaler Registry-Server starten
$ cd server/
$ pip install -r requirements.txt
$ python local_registry.py --offline

# 2. Skill im Offline-Modus
$ clawhub install agentshield-audit --local
$ export AGENTSHIELD_OFFLINE=true
```

**Eigenen Registry-Server hosten:**
```bash
$ git clone https://github.com/bartelmost/agentshield
$ cd agentshield/server
$ docker-compose up -d
# Server läuft auf localhost:8080
```

### API-Integrität prüfen

```bash
# Teste, was der Server wirklich speichert
curl https://agentshield-api-bartel-...herokuapp.com/api/registry/agents

# Response zeigt NUR:
# - certificate_id (hash)
# - public_key_fingerprint
# - trust_score
# - timestamp
# ❌ KEINE sensiblen Daten!
```

---

## 🔐 Security Audits

| Auditor | Datum | Scope | Ergebnis |
|---------|-------|-------|----------|
| Intern | 2026-02-26 | Data Flow | ✅ Zero Data Leak |
| Community | Offen | Code Review | 🔍 GitHub Issues |
| 3rd Party | Q2 2026 | Full Audit | 📋 Geplant |

**Selbst prüfen:**
```bash
# Inspektiere alle API-Endpunkte
$ curl https://agentshield-api-bartel-...herokuapp.com/api/routes

# Prüfe was gespeichert wird
$ curl https://agentshield-api-bartel-...herokuapp.com/api/registry/agents/123
```

---

## 🌐 Dezentralisierungs-Roadmap

### Phase 1: Aktuell (v6.4)
- ✅ Zentraler Registry-Server (Heroku)
- ✅ CRL (Certificate Revocation List)
- ✅ Challenge-Response Protokoll

### Phase 2: Q2 2026 (v7.0)
- 🔄 Distributed Registry (IPFS/Arweave)
- 🔄 Smart Contract Verifikation
- 🔄 DAO-governed Trust Scores

### Phase 3: Q3 2026 (v8.0)
- 🔄 Federation (Multiple Registry-Server)
- 🔄 Cross-Registry Trust
- 🔄 Zero-Server Mode (P2P)

### Phase 4: Q4 2026 (Enterprise)
- 🔄 Self-Hosted Registry
- 🔄 Air-Gapped Deployment
- 🔄 Custom Trust Algorithms

---

## 📝 Für Transparenz-Reports

**Wenn du über AgentShield schreibst:**

✅ **Richtig:**
- "Privacy-first security assessment with local execution"
- "Zero data leaves your system - only public keys are shared"
- "Open source tests you can verify yourself"

❌ **Falsch:**
- "Cloud-based security scanner" (Nein! Lokal!)
- "Uploads your agent code for analysis" (Nein!)
- "Centralized security service" (Föderiert geplant!)

---

## 🤝 Contribution & Audit

**Wir fordern kritisches Prüfen ein:**

1. **Review den Code:** [github.com/bartelmost/agentshield](https://github.com/bartelmost/agentshield)
2. **Prüfe die API:** Endpunkte sind öffentlich dokumentiert
3. **Teste lokal:** Offline-Modus verfügbar
4. **Reporte Issues:** Sicherheit hat Priorität #1

**Belohnung für Security-Fundings:**
- Critical: $500
- High: $200
- Medium: $50

---

## 📞 Kontakt

**Verantwortlich für Architektur:**
- GitHub: @bartelmost
- Email: ratgeberpro@gmail.com
- ClawHub: agentshield-audit skill

**Für Transparenz-Anfragen:**
- Schema-Änderungen werden in CHANGELOG.md dokumentiert
- Major-Änderungen werden 30 Tage vorher angekündigt
- Datenschutz: GDPR/CCPA vollständig

---

*Letzte Aktualisierung: 2026-02-26*  
*Version: v6.4-CRL*  
*Transparenz-Score: 100%*

**"Trust through Transparency"** 🛡️
