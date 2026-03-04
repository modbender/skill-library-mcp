# Scrapling Skill - Quick Start

## 🎯 What Is This?

A web scraping skill for OpenClaw that bypasses anti-bot protection and handles JavaScript-heavy websites.

## 📦 Installation

### Via Gateway UI (Recommended):
1. Open OpenClaw Gateway (run `openclaw status` to get URL)
2. Navigate to **Skills** section
3. Find **"Scrapling Web Scraper"**
4. Click **Install**
5. Wait 5 minutes (downloads browsers)

### Via CLI (Fast):
```bash
cd ~/.openclaw/skills/scrapling
pip install -r requirements.txt
scrapling install
```

## ⚡ Quick Examples

**Scrape a static site:**
```bash
python scrape.py --url "https://example.com" --selector ".product"
```

**Bypass Cloudflare:**
```bash
python scrape.py --url "https://protected-site.com" --stealth --selector ".content"
```

**JavaScript-rendered page:**
```bash
python scrape.py --url "https://react-app.com" --dynamic --selector ".item"
```

**Extract structured data:**
```bash
python scrape.py --url "https://news.ycombinator.com" \
  --selector ".athing" \
  --fields "title:.titleline>a::text,link:.titleline>a::attr(href)" \
  --output stories.json
```

## 🤖 Use in OpenClaw Chat

Just ask:
```
"Use the scrapling skill to scrape https://quotes.toscrape.com 
and extract all quotes and their authors"
```

The agent will:
1. Read SKILL.md
2. Run the scrape.py command
3. Return the results

## 📁 Files

- `SKILL.md` - Full documentation
- `scrape.py` - Main tool
- `examples/` - Working examples
- `INSTALLATION_GUIDE.md` - Detailed setup

## 🆘 Help

**Skill not working?**
```bash
# Reinstall dependencies
cd ~/.openclaw/skills/scrapling
pip install -r requirements.txt
scrapling install
```

**Need more examples?**
Check `examples/` directory or read `SKILL.md`

---

**That's it!** You're ready to scrape the modern web. 🚀
