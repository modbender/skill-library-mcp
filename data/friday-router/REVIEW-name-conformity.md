# User-facing name conformity review

**Standard:** **OpenRouterRouter | Codename: Centipede** (and in prose: "OpenRouterRouter (codename: Centipede)").

**Reviewed:** Critical stable repo content (v1.5.0).

---

## Conformant

| Location | User-facing text |
|----------|------------------|
| **README.md** | Title: `# OpenRouterRouter \| Codename: Centipede`; intro "OpenRouterRouter (codename: Centipede)"; step "Run OpenRouterRouter". |
| **SKILL.md** | `displayName: OpenRouterRouter \| Codename: Centipede`; same title and intro. |
| **_meta.json** | `displayName`: "OpenRouterRouter \| Codename: Centipede"; description uses "OpenRouterRouter (codename: Centipede)" and "OpenRouterRouter" throughout. |
| **config.json** | `name`: "OpenRouterRouter \| Codename: Centipede". |
| **scripts/router.py** | Module docstring and CLI banner: "OpenRouterRouter \| Codename: Centipede"; version print "OpenRouterRouter \| Codename: Centipede v1.5.0". |
| **scripts/gateway_watchdog.py** | Docstring: "OpenRouterRouter (codename: Centipede) / friday-router skill"; uses gateway-guard skill for guard script. |

---

## Intentional (not user-facing)

- **Package/skill name:** `friday-router` in `_meta.json` `name`, SKILL frontmatter `name`, and `clawhub install friday-router` — kept for backward compatibility; not a user-facing product name.
- **Paths:** `workspace/skills/friday-router/` in SKILL.md — install path, not product name.
- **Code:** Class name `FridayRouter` in README "In-code usage" and in `router.py` — internal API; no change required for user-facing conformity.

---

## Fix applied during review

- **scripts/router.py** — Module docstring said "Version 1.4.0"; updated to "Version 1.5.0" to match repo version.

---

## Summary

User-facing surfaces consistently use **OpenRouterRouter | Codename: Centipede** (or "OpenRouterRouter (codename: Centipede)" in prose). No leftover "IntentRouter" or "Friday Router" in user-facing copy. One version string in the router docstring was corrected to 1.5.0.
