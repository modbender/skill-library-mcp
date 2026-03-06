# GitHub Cred 🏆

Analyze GitHub user contribution quality with a four-tier scoring system.

## What it measures

| Tier | Weight | What |
|------|--------|------|
| **Tier 0** | 30% | Owned high-star repos (creator > contributor) |
| **Tier 1** | 30% | External contributions to high-star projects |
| **Tier 2** | 20% | Output quality (merge rate, code ratio) |
| **Tier 3** | 20% | Social influence (followers) |

## Grades

| Grade | Score | Description |
|-------|-------|-------------|
| S | 95+ | Legend — top project creator + core contributor + influencer |
| A+ | 85-94 | Master — high-star project owner OR top project contributor |
| A | 70-84 | Senior — active developer with real contributions |
| B | 50-69 | Active — steady contributor |
| C | 30-49 | Beginner — some contributions |
| D | <30 | Newbie |

## Usage

```
@bot github cred <username>
@bot analyze <username>'s github
@bot <username> github cred
```

## Example Output

```
📊 GitHub Cred: @username

🏆 85/100 (A+)

▸ Tier 0 (30/30)
  👑 awesome-project ⭐12k

▸ Tier 1 (20/30)
  🔨 5 high-star projects

▸ Tier 2 (18/20)
  📈 Merge rate 75% | Code ratio 85%

▸ Tier 3 (10/20)
  👥 1,200 followers
```

## Two paths to A+

- **Creator path** — Build one hit project
- **Contributor path** — Deep contributions to multiple top projects

Both are valid. Mixed is strongest.

## Install

```bash
# ClawHub
clawhub install zerone0x/github-cred

# Manual
git clone https://github.com/zerone0x/clawdbot-skill-github-cred.git ~/.clawdbot/skills/github-cred
```

## License

MIT
