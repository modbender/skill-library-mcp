# Distribution Checklist (ClawHub + awesome-openclaw-skills)

## 1) Preflight

- Ensure skill folder name equals frontmatter `name`.
- Validate frontmatter has only `name` and `description`.
- Remove placeholders/TODO text.
- Run package command:

```bash
python3 /usr/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py \
  /root/.openclaw/workspace/skills/daolv-hotel-booking \
  /root/.openclaw/workspace/dist
```

## 2) Publish to ClawHub

```bash
clawhub login
clawhub publish /root/.openclaw/workspace/skills/daolv-hotel-booking
```

If not logged in, complete browser login first, then rerun publish.

## 3) Publish to awesome-openclaw-skills (GitHub)

1. Fork `awesome-openclaw-skills`.
2. Add one concise entry under the relevant category (travel/hospitality if present).
3. Include:
   - Skill name + 1-line value proposition
   - ClawHub link (or repo link if pending)
4. Open PR with title:
   - `Add daolv-hotel-booking skill`

Recommended commit message:
- `feat: add daolv-hotel-booking to travel skills`

## 4) Post-publish verification

- Install from registry in a clean path and verify:

```bash
mkdir -p /tmp/skill-smoke && cd /tmp/skill-smoke
clawhub install <published-slug>
```

- Run one smoke query:
  - “帮我找下周武汉出差酒店，预算 500/晚，靠近地铁，含早餐。”

## 5) Changelog discipline

For every update, note:
- What changed (workflow, parameters, output format)
- Why it changed (bugfix, better ranking, better UX)
- Compatibility impact (if any)
