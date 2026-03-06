# Sefaria "Powered by Sefaria" Submission

**Submission URL:** https://sefaria.formstack.com/forms/powered_by_sefaria_submission_form

---

## Project Information

**Project Name:** Torah Scholar

**Project URL:** https://clawhub.com (search: torah-scholar)

**GitHub URL:** [To be created]

**Project Description:**

Torah Scholar is an AI agent skill (OpenClaw/MCP format) that gives AI assistants instant access to the Sefaria library. It enables natural language interaction with Jewish texts for research, study, and content creation.

**How it uses Sefaria:**

The skill integrates with multiple Sefaria API endpoints:
- `/api/texts/<ref>` — Retrieve verses with Hebrew and English translations
- `/api/search-wrapper/es6` — Full-text search across the library
- `/api/links/<ref>` — Fetch commentaries and cross-references
- `/api/related/<ref>` — Find related texts and topics
- `/api/calendars` — Get daily learning schedules (Daf Yomi, Parsha, etc.)

**Key Features:**
1. **Search** — Full-text search across Tanach, Talmud, Mishnah, Midrash, and more
2. **Verse Lookup** — Get any text in Hebrew + English by reference
3. **Commentary Finder** — Access Rashi, Ramban, Ibn Ezra, Sforno, and hundreds of other commentators
4. **Daily Learning** — Check this week's parsha and Daf Yomi
5. **Dvar Torah Generator** — Generate structured Torah insights with cited sources

**Target Audience:**
- Torah scholars and students
- Rabbis preparing divrei Torah
- Jewish educators
- Developers building Torah applications
- Researchers studying Jewish texts

**Technical Details:**
- Language: Python + Bash
- Format: OpenClaw skill / MCP-compatible
- No API key required (uses public Sefaria endpoints)
- MIT licensed

**Example Usage:**
```bash
torah search "love your neighbor"
torah verse "Genesis 1:1"
torah verse "Berakhot 2a"
torah links "Leviticus 19:18"
torah dvar ref "Esther 4:14"
```

**Why This Project:**

AI agents are becoming the primary interface for research and productivity. By creating an easy-to-use skill that wraps the Sefaria API, we're making Jewish texts accessible to the AI-native generation and enabling new workflows for Torah study.

**Contact:**
- Name: Abe Perl
- Email: [your email]

---

## Email Template (Alternative)

**To:** developers@sefaria.org

**Subject:** "Powered by Sefaria" Submission — Torah Scholar (AI Agent Skill)

**Body:**

Hi Sefaria Team,

I'd like to submit **Torah Scholar** for your "Powered by Sefaria" directory.

Torah Scholar is an AI agent skill that gives AI assistants (via OpenClaw/MCP) instant access to the Sefaria library. Users can search texts, retrieve verses in Hebrew and English, find commentaries, and generate dvar Torah outlines — all through simple commands.

**Key integrations:**
- Texts API for verse retrieval
- Search API for full-text search
- Links API for commentaries
- Calendars API for daily learning

**Links:**
- ClawHub: torah-scholar
- GitHub: [link]

The project is free, open-source (MIT), and properly attributes Sefaria in all documentation.

Thank you for building such an incredible resource for the Jewish community. Happy to provide any additional information.

Best,
Abe Perl
