---
name: discord-admin-elite
description: "Build, harden, and scale elite Discord servers with a practical
  admin playbook: security baseline, role/permission architecture, onboarding,
  moderation ops, engagement systems, and analytics-driven iteration. Use when
  designing a new server, auditing an existing one, fixing chaos, or preparing
  for growth."
---


# Discord Admin Elite

Use this skill to turn a Discord server into a high-signal, well-moderated, growth-ready community.

## When to use

Use when the user asks to:
- Set up a new Discord server properly
- Improve moderation/safety
- Build cleaner channel + role structure
- Increase engagement/retention
- Audit a messy server and create a fix plan

## When NOT to use

Don’t use this for:
- One-off Discord message sends/reactions only (use `discord` skill)
- Non-Discord community platforms
- Bot-specific coding/hosting implementation (use coding workflow)

## Outcomes this skill should produce

Always produce these 3 deliverables:
1. **Server Audit Scorecard** (0-100 with category scores)
2. **Priority Fix Plan** (Now / Next / Later)
3. **Execution Checklist** (step-by-step settings/actions)

---

## Core Principles (Elite Admin Standard)

1. **Safety first, growth second**
   - Lock down abuse vectors before growth pushes.
2. **Least privilege always**
   - Give members/mods only what they need, no more.
3. **Onboarding is product design**
   - First 5 minutes determines retention.
4. **Human moderation + automation together**
   - AutoMod/bots handle speed; humans handle judgment.
5. **Measure, then iterate**
   - Use Insights and behavior data to decide changes.

---

## Research-backed baseline (use as defaults)

### Security / Anti-raid baseline
- Enable **Community** features.
- Enable **AutoMod** (keyword/spam/mention abuse filters).
- Use higher **verification level** for public servers.
- Require **2FA for moderation** roles.
- Remove `@everyone` ability to mass mention.
- Create a private `#mod-logs` and `#incident-room`.

### Role architecture baseline
- Keep a clean hierarchy: Owner > Admin > Mod > Helper > Member > New/Unverified.
- Avoid permission overlap chaos (few roles, clear job boundaries).
- Never hand out `Administrator` unless absolutely necessary.
- Keep bot roles scoped to needed permissions only.

### Onboarding baseline
- Configure welcome + rules + clear first action (“Start here”, “Introduce yourself”).
- Keep visible channels minimal for new users.
- Use concise channel names and category grouping.
- Make verification instructions obvious and one-path.

### Engagement baseline
- Build 3 core activity loops:
  1) Daily discussion prompt
  2) Weekly event (AMA, demo, challenge)
  3) Recognition loop (wins, shoutouts, roles)
- Maintain announcement/value channels users check repeatedly.
- Use Insights to evaluate activation + retention changes.

---

## The Elite Server Build Framework (E-SHARP)

Use this exact sequence.

### E1 — Evaluate (Audit)
Score each 0-20:
- Security
- Permission hygiene
- Onboarding clarity
- Moderation operations
- Engagement loops

Output: total /100 + top 5 risks.

### E2 — Secure
- Apply anti-raid + AutoMod + verification + 2FA baseline.
- Lock risky perms (`@everyone`, unmanaged bot perms, excessive admin).

### E3 — Hierarchy
- Rebuild role map around least privilege.
- Document each role: purpose, grants, owner.

### E4 — Activate
- Redesign onboarding path for first-message success.
- Add one clear CTA channel for newcomers.

### E5 — Retain
- Launch weekly cadence (events + content beats).
- Create community rituals and recognition.

### E6 — Prove
- Track metrics for 2 weeks and adjust:
  - Join → first message conversion
  - D7 retention
  - Moderation incidents/week
  - Message quality in target channels

---

## Output Templates (copy exactly)

## 1) Discord Server Audit Scorecard
- Security: X/20
- Permissions: X/20
- Onboarding: X/20
- Moderation Ops: X/20
- Engagement: X/20
- **Total: X/100**

Top Risks:
1. ...
2. ...
3. ...

## 2) Priority Fix Plan
### NOW (24 hours)
- ...

### NEXT (7 days)
- ...

### LATER (30 days)
- ...

## 3) Execution Checklist
- [ ] Enable Community + safety features
- [ ] Configure AutoMod rules
- [ ] Set verification level + 2FA for mods
- [ ] Refactor roles and permissions
- [ ] Simplify onboarding channels
- [ ] Create mod logging + incident channels
- [ ] Launch weekly engagement cadence
- [ ] Review Insights after 14 days

---

## Suggested Channel Skeleton (starter)

### INFO
- #start-here
- #rules
- #announcements
- #roles

### COMMUNITY
- #introductions
- #general
- #wins
- #resources

### EVENTS
- #events
- #event-chat

### STAFF (private)
- #mod-chat
- #mod-logs
- #incident-room
- #staff-notes

---

## Common failure patterns (call out hard)

- Too many channels too early (overwhelm)
- Too many roles with random perms
- No verification gate on public invites
- No incident playbook for raids
- No recurring events/rituals
- Measuring vanity metrics only (member count) vs behavior metrics

---

## Trusted references used for this skill

- Discord Safety: Auto moderation in Discord  
  https://discord.com/safety/auto-moderation-in-discord
- Discord Community: Using Insights to Improve Community Growth and Engagement  
  https://discord.com/community/using-insights-to-improve-community-growth-engagement
- Discord Support (raid prevention / roles docs surfaced in research):  
  https://support.discord.com/hc/en-us/articles/10989121220631-How-to-Protect-Your-Server-from-Raids-101  
  https://support.discord.com/hc/en-us/articles/214836687-Discord-Roles-and-Permissions

Note: Some Discord support pages are Cloudflare-protected for automated fetchers; validate in browser when needed.
