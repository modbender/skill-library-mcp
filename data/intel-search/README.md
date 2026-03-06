# Intel Search

Search news, earthquakes, Iran, tech, finance, layoffs. Bilingual (EN/中文). No API key.

---

## Install (3 steps)

1. **Clone into Clawbot skills**

```bash
cd ~/.openclaw/skills
git clone https://github.com/oscarka/intel-search.git
cd intel-search
```

2. **Install dependencies**

```bash
npm install
npm run setup
```

3. **Fetch data (first run)**

```bash
node scripts/fetch.mjs
```

Done. Restart Clawbot and the Agent can use it.

---

## Usage

**Update data**: `node scripts/fetch.mjs`

**Query manually**: `node scripts/query.mjs [topic] [time]`

| Example | Description |
|---------|-------------|
| `node scripts/query.mjs` | Full overview |
| `node scripts/query.mjs iran 3h` | Iran, last 3 hours |
| `node scripts/query.mjs earthquake` | Earthquakes |
| `node scripts/query.mjs layoffs` | Layoffs |
| `node scripts/query.mjs oil` | Keyword: oil |

**Topics**: iran/伊朗, earthquake/地震, tech/科技, finance/财经, layoffs/裁员

**Time**: 30min, 1h, 3h, 2d, 1w, or omit for all

---

## Data path

Default: `~/.openclaw/intel-data/`. Override with `INTEL_DATA_DIR`.
