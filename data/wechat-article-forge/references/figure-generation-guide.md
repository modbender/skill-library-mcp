# Figure Generation Guide

> 公众号文章插图生成规范

## Why Figures Matter

WeChat articles are consumed on mobile phones (~375px wide). Walls of text cause readers to bail. **Every article must contain 2–4 inline figures** that break up text and visualize key concepts.

## Primary Method: Scrapbook-Style Illustrations (article-illustrator)

The **article-illustrator** skill generates colorful, hand-drawn scrapbook-style illustrations using AI image generation (OpenRouter `gpt-5-image-mini`). These produce significantly better visual quality for 公众号 than Mermaid diagrams.

### Why Scrapbook Over Mermaid

- **Visual appeal:** Hand-drawn style catches attention in WeChat's content feed
- **Text readability:** AI-generated images can include Chinese text naturally within illustrations
- **Mobile-friendly:** Portrait orientation (1088×1920) works perfectly on phone screens
- **Engagement:** Illustrated articles get 2-3× more shares than diagram-heavy articles

### Generation Process

1. **Analyze the draft** and identify 2–4 anchor points where a figure adds value
2. **Write prompts** — one per figure, describing a scrapbook-style illustration:
   - Include key concepts, labels, and visual metaphors
   - Specify Chinese text to include in the image
   - Reference the article-illustrator's `references/scrapbook-prompt.md` for style guidelines
3. **Save prompts** as `images/fig<N>-<topic>.prompt.txt`
4. **Generate in parallel** (~10–30s each):

   **Primary: Z.AI / GLM-Image (~$0.015/image, 97.9% Chinese text accuracy)**
   ```bash
   SKILL_DIR=<path-to-article-illustrator-skill>
   IMG_DIR=~/.wechat-article-writer/drafts/<slug>/images

   python3 "$SKILL_DIR/scripts/generate.py" \
     --provider zai \
     --prompt "$(cat $IMG_DIR/fig1-topic.prompt.txt)" \
     --output "$IMG_DIR/fig1-topic.png" \
     --orientation portrait &
   python3 "$SKILL_DIR/scripts/generate.py" \
     --provider zai \
     --prompt "$(cat $IMG_DIR/fig2-topic.prompt.txt)" \
     --output "$IMG_DIR/fig2-topic.png" \
     --orientation portrait &
   wait
   ```

   **Fallback: OpenRouter GPT-4o (~$0.12/image, Chinese text 50-90%)**
   ```bash
   python3 "$SKILL_DIR/scripts/generate.py" \
     --provider openrouter \
     --prompt "$(cat $IMG_DIR/fig1-topic.prompt.txt)" \
     --output "$IMG_DIR/fig1-topic.png" \
     --orientation portrait
   ```

   Z.AI is ~8x cheaper with significantly better Chinese text rendering. Use OpenRouter only if Z.AI is unavailable or quota is exhausted.
5. **Insert into draft.md** with Chinese captions:
   ```markdown
   ![图1：系统架构全景 — 六大核心模块](images/fig1-architecture.png)
   ```

### Prompt Writing Tips

- Describe the visual scene, not just the concept: "A colorful hand-drawn bulletin board with sticky notes showing six modules..."
- Include specific Chinese labels: "标注：任务板、日历、记忆库"
- Mention visual style: "scrapbook style, hand-drawn, colorful, with arrows and doodles"
- Keep it under 200 words — overly detailed prompts reduce quality

## Figure Types (by use case)

| Type | When to Use | Illustration Style |
|------|------------|-------------------|
| Architecture overview | Showing system components | Bulletin board with labeled sticky notes |
| Pipeline / Flowchart | Step-by-step processes | Conveyor belt or road map illustration |
| Timeline | Historical progression | Scroll or path with milestones |
| Comparison | Two approaches, before/after | Split-screen or vs. layout |
| Team/Org structure | Relationships between actors | Family tree or org chart with avatars |
| Concept map | Relationships between ideas | Mind map with branches and icons |

## Placement Heuristics

Insert figures:
- **After the first major section** (not at the very top — hook the reader with text first)
- **Between conceptual shifts** — when the article moves to a new idea
- **Before the conclusion** — a summary/recap figure reinforces the message

**Caption format:** `图N：<描述> — <补充说明>` (Chinese figure numbering, em-dash for subtitle)

**Even distribution:** No two figures should appear within 200 characters of each other.

## Image Upload to WeChat CDN

All local images MUST be uploaded to WeChat's CDN before the article can be saved/published. Local file paths do not work.

**Upload process (via CDP):**
```javascript
// For each image file:
const b64 = fs.readFileSync(imagePath).toString('base64');
// From the page context, POST to:
// /cgi-bin/filetransfer?action=upload_material&f=json&scene=8&writetype=doublewrite&groupid=1&token=<token>
// Response: { "cdn_url": "https://mmbiz.qpic.cn/..." }
```

After upload, replace all `images/fig*.png` paths in `formatted.html` with CDN URLs.

## Quality Checks for Figures

| Check | Rule | Severity |
|-------|------|----------|
| FIG-01 | Article has ≥2 inline figures | HIGH |
| FIG-02 | All figure PNGs exist and are ≥10KB (not corrupt) | HIGH |
| FIG-03 | No figure exceeds 2MB (WeChat CDN upload limit) | MEDIUM |
| FIG-04 | Figure captions present and in Chinese | MEDIUM |
| FIG-05 | Prompt files saved alongside PNGs | LOW |
| FIG-06 | Figures evenly distributed (no 2 figures within 200 chars of each other) | LOW |
| FIG-07 | After upload, all img src attributes point to mmbiz.qpic.cn | HIGH |

## Mermaid Fallback

If article-illustrator is unavailable (no `OPENROUTER_API_KEY`, network issues, etc.), fall back to Mermaid diagrams:

### Mobile-First Mermaid Design Rules

1. **Prefer vertical layouts (`TD`/`TB`)** — horizontal (`LR`) only if ≤5 nodes
2. **Max 6–8 nodes per diagram** — split complex diagrams into 2+ figures
3. **Labels ≤8 Chinese characters per node**
4. **Use color coding** — group related nodes with the same fill color
5. **White background** — render with `-b white`
6. **Render width: 900px**
7. **No emoji in node labels** — inconsistent rendering across Android/iOS

### Mermaid Color Palette

```
Primary:    #3498db (blue)     — main concepts
Secondary:  #2ecc71 (green)    — outputs, results
Accent:     #e74c3c (red)      — highlights, entry points
Neutral:    #95a5a6 (grey)     — background items
Emphasis:   #f39c12 (orange)   — human actions
Purple:     #9b59b6 (purple)   — external systems
```

### Mermaid Rendering

```bash
PUPPET='{"args":["--no-sandbox","--disable-setuid-sandbox"]}'
echo "$PUPPET" > /tmp/mmdc-puppet.json
npx @mermaid-js/mermaid-cli \
  -i <input>.mmd -o <output>.png \
  -w 900 -b white \
  -p /tmp/mmdc-puppet.json -q
```

## ImageMagick Last Resort

If both article-illustrator AND mermaid-cli fail, generate simple text-based covers:

```bash
FONT=$(fc-match --format='%{file}' 'Noto Sans CJK SC' 2>/dev/null || \
       fc-match --format='%{file}' 'WenQuanYi' 2>/dev/null || \
       echo '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')

convert -size 900x600 xc:"#1a1a2e" \
  -font "$FONT" \
  -fill "#3498db" -pointsize 36 -gravity North -annotate +0+30 "系统架构" \
  -fill white -pointsize 24 -gravity Center -annotate +0+0 "网关 → 智能体 → 技能" \
  output.png
```
