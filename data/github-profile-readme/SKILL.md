---
name: github-profile-readme
description: Generate GitHub profile READMEs with stats badges, language charts,
  and contribution streaks.
---


# GitHub Profile README Generator

Create polished GitHub profile READMEs with stats, badges, and contribution streaks.

**Use when** creating or updating a GitHub profile README.

## Requirements

- GitHub username
- No API keys needed (all badge services are free and public)

## Instructions

1. **Gather info** — Ask for:
   - GitHub username (required)
   - Bio / tagline
   - Tech stack (languages, frameworks, tools)
   - Social links (Twitter, LinkedIn, blog, etc.)
   - Theme preference: `radical`, `tokyonight`, `dracula`, `gruvbox`, `dark`, `default`

2. **Build README components**:

   **Header** — typing animation or wave:
   ```markdown
   ![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&pause=1000&color=667eea&width=435&lines=Full+Stack+Developer;Open+Source+Enthusiast)
   ```

   **GitHub Stats**:
   ```markdown
   ![Stats](https://github-readme-stats.vercel.app/api?username={USER}&show_icons=true&theme={THEME}&hide_border=true)
   ![Languages](https://github-readme-stats.vercel.app/api/top-langs/?username={USER}&layout=compact&theme={THEME}&hide_border=true)
   ```

   **Streak Stats**:
   ```markdown
   ![Streak](https://streak-stats.demolab.com?user={USER}&theme={THEME}&hide_border=true)
   ```

   **Tech Stack** — Shields.io badges:
   ```markdown
   ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
   ![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
   ```

   **Social Links**:
   ```markdown
   [![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/{handle})
   ```

3. **Output** the complete markdown. Remind user:
   - Create repo `{username}/{username}` on GitHub (if it doesn't exist)
   - Paste content into `README.md`
   - The repo must be **public** for the profile to show

## Design Tips

- Keep it **clean** — 3-5 badge rows max, too many looks cluttered
- Use **consistent theme** across all stat widgets
- Put most important info **above the fold** (visible without scrolling)
- Add a **brief bio** — don't rely solely on auto-generated stats
- Use `&hide=` parameter to hide less relevant language stats

## Edge Cases

- **New account with few contributions**: Focus on bio and tech stack instead of stats.
- **Private contributions not showing**: Add `&count_private=true` to stats URL.
- **Stats not updating**: Badge services cache for ~4 hours. Use `&cache_seconds=1800` for faster updates.
- **Broken badge images**: Verify username spelling. Check if the badge service is up.

## Useful Badge Resources

- [github-readme-stats](https://github.com/anuraghazra/github-readme-stats) — stats & language cards
- [github-readme-streak-stats](https://github.com/DenverCoder1/github-readme-streak-stats) — streak counter
- [shields.io](https://shields.io) — custom badges for anything
- [simple-icons](https://simpleicons.org) — logo slugs for Shields.io
