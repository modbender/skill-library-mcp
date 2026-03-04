# Asterisk Implementation Plan for Amber Voice Assistant

> **Status: Future Roadmap** — This document describes a planned future carrier integration (Asterisk/SIP) for cost reduction. It is not part of the current release. The current implementation uses Twilio as the telephony provider.

## Executive Summary

**Feasibility:** ✅ **HIGHLY FEASIBLE** - Multiple working implementations exist in production

**Cost Savings:** 🎯 **70-90% reduction** compared to Twilio (SIP trunks + self-hosted Asterisk)

**Complexity:** ⚠️ **Medium-High** - Requires server setup, networking knowledge, but well-documented

---

## Your Questions Answered

### Q1: Would it completely eliminate the need for Twilio subscription?

**Answer:** YES and NO

**What Asterisk REPLACES:**
- ✅ Twilio's SIP bridge infrastructure
- ✅ Twilio's call routing/PBX features
- ✅ Twilio's audio handling and mixing
- ✅ Twilio's monthly platform fees

**What you STILL NEED (but can get elsewhere):**
- 📞 **Phone number provisioning** - You need a SIP trunk provider
- 🌐 **PSTN connectivity** - Connection to the public phone network

**The key insight:** Asterisk is **PBX software** (Private Branch Exchange). It handles the call routing, audio mixing, and SIP signaling. But it doesn't magically give you phone numbers or connect you to the phone network - you need a **SIP trunk provider** for that.

---

### Q2: How would I reserve a number if not through Twilio?

**Answer:** Via a **SIP Trunk Provider** (much cheaper than Twilio!)

### Top SIP Trunk Providers for 2026

| Provider | Cost | Best For |
|----------|------|----------|
| **VoIP.ms** | $0.005/min + $0.85/mo per DID | Budget/hobbyists - extremely cheap |
| **Telnyx** | $0.004-0.01/min + $2/mo per DID | Production - "70% cheaper than Twilio" |
| **Bandwidth** | $0.004/min + $1/mo per DID | Enterprise - high quality |
| **Flowroute** | $0.0084/min + $1.25/mo per DID | Mid-size - good balance |
| **BulkVS** | $0.003/min + $1/mo per DID | Power users - bulk pricing |

**Example Cost Comparison (100 min/month):**
- **Twilio:** ~$50-80/month (SIP trunk + Realtime API usage)
- **Asterisk + Telnyx:** ~$3-5/month (just the SIP trunk) + OpenAI Realtime costs

**You save:** The Twilio platform fees, SIP infrastructure costs, and per-call markup

---

## Architecture Overview

```
┌─────────────────┐
│  Phone Network  │ (PSTN)
│  (Your Number)  │
└────────┬────────┘
         │
         │ SIP Trunk (Telnyx/VoIP.ms)
         │ Cost: ~$0.005/min
         ▼
┌─────────────────┐
│    Asterisk     │ (Your Server)
│  PBX Software   │ - Answers calls
│                 │ - Routes audio
│                 │ - Handles SIP
└────────┬────────┘
         │
         │ ARI (Asterisk REST Interface)
         │ + ExternalMedia channel
         ▼
┌─────────────────┐
│  Python Bridge  │ (Your Code)
│   (RTP ↔ WS)    │ - Converts RTP → PCM
│                 │ - Forwards to OpenAI
└────────┬────────┘
         │
         │ WebSocket
         ▼
┌─────────────────┐
│ OpenAI Realtime │
│      API        │ - GPT-4 voice model
└─────────────────┘
```

**Key Components:**

1. **Asterisk Server** (self-hosted on VPS/local)
   - Ubuntu 22.04/24.04
   - Asterisk 20/22+
   - Public IP or NAT configuration

2. **SIP Trunk** (replaces Twilio)
   - Provides phone number
   - Connects to PSTN
   - Costs ~$0.005/min instead of Twilio's $0.015-0.03/min

3. **Python Bridge Service** (new component)
   - Connects Asterisk to OpenAI Realtime
   - Handles RTP ↔ WebSocket conversion
   - ~200-500ms latency (comparable to Twilio)

4. **OpenAI Realtime API** (unchanged)
   - Same GPT-4 voice model
   - Same low latency
   - Same pricing

---

## Technical Implementation

### Phase 1: Asterisk Setup (Week 1)

**Server Requirements:**
- Ubuntu 22.04/24.04 VPS (DigitalOcean/Linode/AWS: ~$10-20/month)
- 2GB RAM minimum
- Public IP or properly configured NAT
- Open ports: 5060 (SIP), 10000-20000 (RTP), 8088 (ARI)

**Install Asterisk:**
```bash
# Ubuntu 22.04/24.04
sudo apt update
sudo apt install asterisk asterisk-dev
```

**Key Config Files:**
- `pjsip.conf` - SIP trunk configuration
- `extensions.conf` - Call routing dialplan
- `ari.conf` - REST API for external control
- `http.conf` - Enable HTTP for ARI
- `rtp.conf` - RTP port range

### Phase 2: SIP Trunk Configuration (Week 1)

**Example: Telnyx Setup**
1. Sign up at telnyx.com
2. Purchase a phone number (~$2/month)
3. Create SIP credentials
4. Configure in Asterisk's `pjsip.conf`

```ini
[telnyx-trunk]
type=registration
outbound_auth=telnyx-auth
server_uri=sip:sip.telnyx.com
client_uri=sip:YOUR_CONNECTION_ID@sip.telnyx.com

[telnyx-trunk]
type=endpoint
context=inbound
disallow=all
allow=ulaw,alaw
outbound_auth=telnyx-auth
aors=telnyx-trunk
```

### Phase 3: Python Bridge Development (Week 2-3)

**Repository:** [Already exists!](https://github.com/thevysh/AsteriskOpenAIRealtimeAssistant)

**Components:**
- `ari.py` - Asterisk REST Interface client
- `realtime.py` - OpenAI Realtime WebSocket handler
- `rtp.py` - RTP packet handling (PCM16@16kHz, 20ms frames)
- `guardrails.py` - Safety prompts and moderation
- `observability.py` - Prometheus metrics

**Key Flow:**
1. Call arrives → Asterisk answers
2. ARI creates ExternalMedia channel
3. Python bridge connects:
   - Receives RTP audio from Asterisk
   - Converts to PCM and sends to OpenAI via WebSocket
   - Receives PCM from OpenAI
   - Converts to RTP and sends back to Asterisk
4. Asterisk plays audio to caller

### Phase 4: OpenClaw Integration (Week 3-4)

**Adapt Current Amber Architecture:**

Current Amber has:
- `runtime/sip-bridge.js` (Twilio-specific)
- `runtime/openai-realtime.js` (OpenAI connection)
- `runtime/dashboard/` (call monitoring)

New "Asterisk Mode":
- `runtime/asterisk-bridge/` (Python service)
  - `server.py` - Main ARI + Realtime bridge
  - `openclaw.py` - OpenClaw Gateway integration
  - `config.py` - Settings management
- Keep existing dashboard (adapt to read from Asterisk)
- Dual-mode setup wizard (Twilio OR Asterisk)

---

## Comparison: Twilio vs Asterisk

| Feature | Twilio (Current) | Asterisk (Proposed) |
|---------|-----------------|---------------------|
| **Setup Complexity** | Low (5 min) | Medium (2-3 hours) |
| **Monthly Base Cost** | $0 platform | ~$10-20 VPS |
| **Per-Minute Cost** | $0.015-0.03 | $0.003-0.01 |
| **Phone Number** | $1-2/month | $0.85-2/month |
| **Latency** | ~300-500ms | ~200-500ms |
| **Control** | Cloud/limited | Full local control |
| **Privacy** | Data passes through Twilio | Self-hosted option |
| **Scalability** | Infinite | Server-dependent |
| **Maintenance** | Zero | Medium (updates, monitoring) |

**Cost Example (100 hours/month usage):**
- **Twilio:** ~$90-180/month (6000 min × $0.015)
- **Asterisk:** ~$28-80/month ($20 VPS + 6000 min × $0.01)

**Savings:** ~$60-100/month (~50-70% reduction)

---

## Implementation Roadmap

### v5.0 "Asterisk Edition" - 6 Week Timeline

**Week 1-2: Research & Proof of Concept**
- [ ] Set up test Asterisk server (DigitalOcean droplet)
- [ ] Configure Telnyx SIP trunk
- [ ] Test inbound call routing
- [ ] Verify RTP audio quality

**Week 3-4: Python Bridge Development**
- [ ] Fork existing GitHub repo (thevysh/AsteriskOpenAIRealtimeAssistant)
- [ ] Add OpenClaw Gateway integration
- [ ] Implement brain-in-the-loop features
- [ ] Add call logging and monitoring
- [ ] Test with OpenAI Realtime API

**Week 5: Setup Wizard & Documentation**
- [ ] Create dual-mode setup wizard (Twilio OR Asterisk)
- [ ] Environment detection (has server? use Asterisk)
- [ ] Automated Asterisk installation script
- [ ] SIP trunk configuration helper
- [ ] Update SKILL.md with Asterisk instructions

**Week 6: Testing & Release**
- [ ] End-to-end testing (inbound + outbound)
- [ ] Load testing (multiple concurrent calls)
- [ ] NAT traversal testing
- [ ] Documentation polish
- [ ] Release v5.0.0 on ClawHub

---

## Pros & Cons Analysis

### Asterisk Pros ✅

1. **Cost Savings:** 50-90% cheaper than Twilio
2. **Privacy:** Self-hosted, no cloud dependency
3. **Control:** Full access to call logs, audio, configuration
4. **Flexibility:** Can add advanced PBX features (IVR, call queues, voicemail)
5. **No Vendor Lock-in:** Can switch SIP providers anytime
6. **Learning:** Deeper understanding of telephony systems
7. **Existing Infrastructure:** Many users already have Asterisk

### Asterisk Cons ⚠️

1. **Complexity:** Requires server setup, networking knowledge
2. **Maintenance:** You manage updates, security, uptime
3. **NAT Issues:** Can be tricky if behind NAT (solvable but annoying)
4. **Scaling:** Need to provision more servers for high volume
5. **Setup Time:** 2-3 hours vs 5 minutes for Twilio
6. **No Managed Service:** You're on your own for troubleshooting
7. **Initial Learning Curve:** Asterisk configuration syntax takes time

---

## Decision Matrix: When to Use Which

### Choose Twilio (Current) When:
- You want zero maintenance
- You need instant setup (< 5 minutes)
- You're okay with higher costs for convenience
- You don't have server management experience
- You need guaranteed 99.99% uptime (SLA)

### Choose Asterisk (New) When:
- You have existing Asterisk infrastructure
- You want maximum cost savings
- Privacy/data sovereignty matters
- You're comfortable with Linux/servers
- You want full control over telephony
- You plan high call volume (cost savings compound)

### Hybrid Approach:
- **Development:** Use Asterisk (cheap testing)
- **Production:** Start with Twilio, migrate to Asterisk as you scale
- **Or:** Offer both in setup wizard, let users choose

---

## Success Stories & References

### Existing Asterisk + OpenAI Realtime Implementations

1. **FreePBX Community Project**
   - "Reduces latency to ~1 sec, conversation feels natural"
   - Active development (Apr 2025-present)
   - ARI app for pure Asterisk 20

2. **Production Deployments**
   - "I've deployed AI call assistants for a few organizations" - Vishal Shrestha
   - GitHub repo with full production setup
   - Prometheus monitoring, guardrails, DTMF fallback

3. **Community Resources**
   - Asterisk Community: Active threads on OpenAI Realtime integration
   - OpenAI Forums: Troubleshooting SIP header issues (being resolved)
   - Reddit r/Asterisk: Multiple users successfully connecting to OpenAI

---

## Next Steps (Immediate Actions)

### For Abe to Try:

1. **Test Server Setup (This Weekend)**
   ```bash
   # Spin up DigitalOcean droplet (~$10/month)
   # Ubuntu 22.04, 2GB RAM
   # Install Asterisk and test basic SIP
   ```

2. **Get Free Test Number (30 min)**
   - Sign up for Telnyx trial
   - Get a free test number
   - Configure SIP trunk in Asterisk

3. **Clone Working Repo (15 min)**
   ```bash
   git clone https://github.com/thevysh/AsteriskOpenAIRealtimeAssistant
   cd AsteriskOpenAIRealtimeAssistant
   # Follow README
   ```

4. **Test Call Flow (1 hour)**
   - Configure OpenAI API key
   - Place test call to your number
   - Verify audio quality and latency

### For Amber Development:

1. **Document Findings** (Done! ✓ This file)
2. **Create Prototype Branch** (`feature/asterisk-support`)
3. **Build Dual-Mode Setup Wizard**
4. **Write Migration Guide** (Twilio → Asterisk)
5. **Update FEEDBACK.md** with implementation timeline

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| NAT traversal issues | Medium | High | Detailed NAT guide, STUN/TURN fallback |
| Setup complexity scares users | High | Medium | One-click install script, detailed docs |
| Asterisk version compatibility | Low | Medium | Test on Asterisk 20/22/24 |
| SIP trunk reliability varies | Medium | High | Recommend 2-3 tested providers |
| OpenAI SIP header bugs | Low | Low | Already being addressed by OpenAI |
| User expects Twilio-level ease | High | Medium | Clearly set expectations in docs |

---

## Recommendation

**Proceed with Asterisk implementation as v5.0 feature** 🚀

**Rationale:**
1. ✅ **Technically proven** - Multiple working implementations exist
2. ✅ **User demand confirmed** - First feature request we received
3. ✅ **Cost savings significant** - 50-90% reduction appeals to self-hosters
4. ✅ **Differentiation** - No other ClawHub phone skill offers this
5. ✅ **Your interest** - You want to try it yourself (best validation!)

**Approach:**
- Keep Twilio support (don't remove it)
- Add Asterisk as parallel option
- Setup wizard detects: "Do you want to use Twilio (easy) or Asterisk (advanced)?"
- Market as "Amber Pro" or "Amber Self-Hosted Edition"

**Timeline:**
- Prototype: 2 weeks (Abe tests personally)
- Production-ready: 4-6 weeks
- Release v5.0.0 with both options

---

## Open Questions

1. Should we fork the Python bridge or build TypeScript version?
   - **Pro Python:** Working code exists, faster to ship
   - **Pro TypeScript:** Matches Amber's existing codebase

2. One skill or two separate skills?
   - **One skill:** Amber with mode selection in wizard
   - **Two skills:** "Amber" (Twilio) + "Amber Local" (Asterisk)

3. What's the minimum viable feature set for v5.0?
   - Inbound calls only?
   - Or inbound + outbound from day 1?

4. How do we handle the dashboard?
   - Asterisk CDR (Call Detail Records) → same format as Twilio logs?
   - Or new dashboard specifically for Asterisk mode?

---

**Created:** 2026-02-21  
**Status:** Implementation Plan - Pending Approval  
**Next Review:** After Abe's test deployment
