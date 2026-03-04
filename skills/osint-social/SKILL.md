---
name: osint-social
description: >
  Investigate a username across 1000+ social media platforms and websites using social-analyzer.
  Use this skill whenever the user wants to look up, investigate, trace, or find where a specific
  username exists online — including OSINT research, background checks on online handles,
  verifying if someone uses the same username across platforms, or checking their own digital
  footprint. Triggers on phrases like "查一下这个用户名", "帮我找 X 在哪些平台", "investigate username",
  "OSINT lookup", "social media footprint", "trace this account", "find all accounts for X".
  Always use this skill when a username investigation is requested, even if the user just says
  "look up [name]" or "check if [name] exists on social media".
metadata:
  openclaw:
    requires:
      bins: ["python3", "pip3"]
---

# OSINT Social Analyzer Skill

Cross-platform username investigation using [social-analyzer](https://github.com/qeeqbox/social-analyzer).
Searches 1000+ platforms and returns a natural language summary of findings.

## Setup (first run only)

```bash
pip3 install social-analyzer --break-system-packages
```

Verify it works:
```bash
python3 -m social-analyzer --username "testuser" --top 10 --output json --filter "good"
```

---

## Running an Investigation

### Standard lookup (recommended default)
```bash
python3 -m social-analyzer \
  --username "{USERNAME}" \
  --metadata \
  --output json \
  --filter "good" \
  --top 100
```

### Deep lookup (slower, more thorough)
```bash
python3 -m social-analyzer \
  --username "{USERNAME}" \
  --metadata \
  --extract \
  --output json \
  --filter "good,maybe" \
  --top 300
```

### Platform-specific lookup
```bash
# Specific websites
python3 -m social-analyzer --username "{USERNAME}" --websites "youtube twitter instagram tiktok github"

# By content type
python3 -m social-analyzer --username "{USERNAME}" --type "music"

# By country
python3 -m social-analyzer --username "{USERNAME}" --countries "us uk"
```

### Multiple usernames (variants)
```bash
python3 -m social-analyzer --username "{NAME1},{NAME2},{NAME3}" --metadata --top 100
```

---

## Parsing and Summarizing Results

After running the command, parse the JSON output and produce a **conversational summary** — do NOT dump raw JSON to the user.

### What to extract from results

From each detected profile:
- `website` — platform name
- `url` — direct link
- `rate` — confidence score (0–100)
- `status` — "good" / "maybe" / "bad"
- `metadata.name` — display name if available
- `metadata.bio` — bio/description if available
- `metadata.followers` — follower count if available

### Summary format (conversational, natural language)

Structure the response like this:

```
找到 [N] 个账号，以下是主要发现：

**高置信度账号（rate ≥ 80）：**
- GitHub (rate: 95): github.com/username — 显示名 "John"，有 234 个 follower
- Twitter (rate: 88): twitter.com/username
- Instagram (rate: 82): instagram.com/username — 简介：摄影爱好者

**中等置信度（rate 50–79）：**
- Reddit (rate: 65): reddit.com/u/username

共扫描了 100 个平台，[M] 个请求失败（网络超时等），不影响主要结果。
```

### Confidence tiers
- **rate ≥ 80** → 高置信度，几乎确定是同一人
- **rate 50–79** → 中等，值得关注但需人工确认
- **rate < 50** → 低，通常跳过，除非用户要求显示全部

---

## Handling Edge Cases

**No results found:**
> 在扫描的 100 个平台中未找到该用户名的公开账号。可能原因：用户名拼写不同、账号已删除、或平台设置了隐私保护。

**Command takes too long (>5 min):**
Reduce scope: `--top 50` or specify `--websites` explicitly.

**pip install fails:**
```bash
pip3 install social-analyzer
# or
pip install social-analyzer --user
```

**Rate limiting from platforms:**
Some platforms block rapid scanning. Use `--mode slow` for more polite requests:
```bash
python3 -m social-analyzer --username "{USERNAME}" --mode slow --top 50
```

---

## Privacy & Ethics Reminder

This tool only accesses **publicly available information**.

Always remind the user:
- Results are public data only — no private messages, emails, or passwords
- Intended for legitimate use: self-auditing, security research, journalism, law enforcement support
- Do not use to stalk, harass, or violate anyone's privacy
- Different jurisdictions have different laws around OSINT — use responsibly

Include a one-line reminder at the end of every investigation summary:
> ⚠️ 以上均为公开信息，请合法合理使用。

---

---

## Chinese Platform Lookup (cn_lookup.py)

For Chinese social media platforms, use the dedicated script instead of social-analyzer.

### Supported platforms

| 平台 | 覆盖情况 | 备注 |
|------|---------|------|
| Bilibili 哔哩哔哩 | ✅ 用户名搜索 + 主页信息 | 最可靠 |
| 知乎 Zhihu | ✅ 用户名/URL token 搜索 | 需精确匹配 |
| 微博 Weibo | ⚠️ 移动端降级搜索 | 仅存在性检测 |
| 小红书 / 抖音 / 微信 | ❌ 不支持 | 强制登录，无公开接口 |

### Running cn_lookup

```bash
python3 skills/osint-social/scripts/cn_lookup.py "{USERNAME}"
```

### When to use cn_lookup vs social-analyzer

- User mentions Chinese platforms, Bilibili, 知乎, 微博 → use `cn_lookup.py`
- User mentions username is Chinese or used on Chinese internet → run **both**
- General global lookup → use social-analyzer only

### Combined workflow (recommended for thorough investigation)

```bash
# Step 1: Global platforms
python3 -m social-analyzer --username "{USERNAME}" --metadata --output json --filter "good" --top 100

# Step 2: Chinese platforms
python3 skills/osint-social/scripts/cn_lookup.py "{USERNAME}"
```

Then combine and summarize both outputs together in a single natural language response.

---

## Reference Files

- `references/platforms.md` — Notable platforms covered and their categories
- `references/platforms.md` — Notable platforms covered and their categories
- `scripts/run_osint.sh` — Shell wrapper for global platform lookup
- `scripts/cn_lookup.py` — Chinese platform lookup (Bilibili, Zhihu, Weibo)
