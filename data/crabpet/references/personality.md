# CrabPet Personality System

## How Personality is Determined

The pet engine scans all `memory/YYYY-MM-DD.md` daily log files and counts keyword occurrences 
across five personality dimensions. Each dimension produces a 0.0–1.0 score, normalized against 
the highest-scoring dimension. The dominant dimension becomes the pet's "primary personality."

Since scores are mixed, most pets will have a blend — e.g., 70% coder + 20% writer + 10% analyst.
This makes every pet unique.

## Dimensions

### 🔧 Coder (技术宅)
**Keywords:** code, script, function, debug, git, deploy, python, bash, error, api, npm, docker, 
server, compile, variable, class, import, repo, commit, merge, branch, test, bug, fix, refactor, 
terminal, cli, sdk

**Appearance:** Wears glasses, has a tiny laptop nearby, screen glow effect  
**Scene:** Sits at a desk with a monitor showing green terminal text  
**Personality text:** Quiet, focused, occasionally celebrates with a small fist pump

### 📝 Writer (文艺虾)
**Keywords:** write, article, blog, draft, edit, post, story, content, essay, paragraph, summary, 
publish, headline, tone, narrative, outline, copywriting, newsletter

**Appearance:** Wears a scarf, holds a pen, thought bubbles appear  
**Scene:** Sits at a cozy desk with papers scattered around  
**Personality text:** Thoughtful, dreamy, pauses to think before acting

### 📊 Analyst (学霸虾)
**Keywords:** data, chart, analyze, report, csv, database, query, metrics, sql, excel, spreadsheet, 
statistics, graph, dashboard, kpi, visualization, trend, forecast

**Appearance:** Wears a graduation cap, surrounded by floating charts  
**Scene:** Desk with multiple small screens  
**Personality text:** Precise, methodical, nods knowingly

### 🎨 Creative (创意虾)
**Keywords:** design, image, ui, color, layout, style, logo, brand, pixel, animation, figma, css, 
font, icon, mockup, wireframe, illustration

**Appearance:** Wears a beret, holds a palette  
**Scene:** Easel or design workspace with colorful elements  
**Personality text:** Expressive, colorful, waves claws enthusiastically

### ⚡ Hustle (卷王虾)
**Keywords:** N/A (calculated from usage frequency — logs per day, total volume)

**Appearance:** Wears a headband, lightning bolt effects, slightly buff  
**Scene:** Multiple desks, moving quickly between them  
**Personality text:** Energetic, always in motion, never sits still

## Mood × Personality Interactions

| Mood | Coder | Writer | Analyst | Creative | Hustle |
|------|-------|--------|---------|----------|--------|
| Energetic | Typing fast | Writing with sparkles | Reviewing charts | Painting | Running between desks |
| Bored | Staring at screen | Doodling | Organizing files | Looking at wall | Fidgeting |
| Slacking | Playing a game | Reading a novel | Watching TV | Drawing comics | Exercising |
| Hibernating | Sleeping on keyboard | Sleeping with book | Sleeping on papers | Sleeping with crayon | Sleeping standing up |
| Frozen | Frozen at desk | Frozen with pen up | Frozen pointing at chart | Frozen mid-paint | Frozen mid-run |
