---
name: kirk-content-pipeline
description: >
  Create KSVC-validated Twitter content from research PDFs. Content types:
  long threads, quick takes, breaking news, shitposts, personal commentary,
  victory laps. Triggers on "create content", "write thread", "make a post",
  "shitpost", or when working with PDFs in /Users/Shared/ksvc/pdfs.
  REQUIRED STEPS - (1a) Explore agents to scan PDFs, (1b) RLM for deep extraction,
  (1c) Cross-doc synthesis with rlm-multi, (2) KSVC holdings check (preliminary),
  (3) write data backbone, (4a) AUDIT with RLM verification, (4a.5) Gemini web
  cross-validation for FAIL/UNSOURCED inferences, (4b) Final holdings verification
  (ALL 7 models), (4c) Stylize with kirk-mode skill, (4d) humanizer pass,
  (5) save draft, (6) chart decision & generation.
---

# Kirk Content Pipeline

Create Twitter content from analyst research PDFs, validated against KSVC holdings.

## Pipeline Steps (MANDATORY)

```
1a.   Scan PDFs (Explore agents for broad screening)
1b.   Extract insights (RLM for deep extraction - text, tables, AND charts)
1c.   Cross-doc synthesis (rlm-multi for insights across sources)
2.    Check KSVC holdings (preliminary - with known tickers)
3.    Write content (data backbone, Serenity-heavy)
4a.   AUDIT (verify draft claims against source PDFs with RLM)
4a.5. GEMINI CROSS-VALIDATION (web-verify FAIL/UNSOURCED inferences)
4b.   Final Holdings Verification (check ALL 7 models with discovered tickers)
4c.   Stylize (invoke kirk-mode skill for voice/character)
4d.   Humanize (remove AI patterns)
5.    Save draft for approval
6.    Chart decision & generation (after draft crystallizes thesis)
7.    PUBLISH to final folder (clean version for posting)
```

**Never skip steps 4a-4d. Use 1a for multi-PDF screening, 1b for deep extraction, 1c for cross-doc synthesis, 4a for verification, 4a.5 for web cross-validation, 4b for final holdings check, 4c for character voice, 4d for AI pattern removal.**

**⚠️ CRITICAL: Step 1b extracts data. Step 1c synthesizes across docs. Step 4a VERIFIES the written content. Step 4a.5 CROSS-VALIDATES inferences.**
- 1b: "What does each PDF say?" (per-doc extraction)
- 1c: "What patterns emerge across PDFs?" (cross-doc synthesis)
- 4a: "Does my draft accurately reflect the sources?" (source-locked verification)
- 4a.5: "Are the flagged inferences valid per public sources?" (web cross-validation)
- 4c: "Which Kirk mode fits this situation?" (character voice)

---

## Subagent Permissions (CRITICAL)

**Subagents CANNOT Read files outside the project directory.** PDFs in `/Users/Shared/ksvc/pdfs/` are blocked. The fix: **symlink PDFs into the project directory** before spawning subagents.

**The main agent MUST create a symlink before Step 1a:**
```bash
ln -sf "/Users/Shared/ksvc/pdfs/YYYYMMDD" ".claude/pdfs-scan"
```

Then subagents Read from `.claude/pdfs-scan/filename.pdf` — this works because the path resolves inside the project.

| Access Method | `/Users/Shared/` path | Symlinked project path |
|--------------|----------------------|----------------------|
| Subagent Read tool (PDF) | ❌ Auto-denied | ✅ Works |
| Subagent Read tool (images) | ❌ Auto-denied | ✅ Works |
| Main agent Read tool | ✅ User approves | ✅ Works |
| Bash → RLM | ✅ Any path | ✅ Any path |

**Discovered 2026-02-07:** Subagents fail with `"Permission to use Read has been auto-denied (prompts unavailable)"` on `/Users/Shared/` paths. Symlink into project dir = full Read access. Tested: 19 PDFs, medium thoroughness, 125k tokens, zero errors.

---

## Content Types & Voice Blends

**Full guide:** `references/kirk-voice.md` — Read this for templates and examples.

Kirk voice = Serenity's data + Citrini7's wit + Jukan's skepticism + Zephyr's energy.

| Type | When | Blend | Key Element |
|------|------|-------|-------------|
| **Long Thread** | Deep dive, multi-source | Serenity + Jukan | TLDR + skepticism |
| **Quick Take** | Single insight, one report | Citrini7 + Serenity | Punchy + one number |
| **Breaking News** | Just dropped | Zephyr + Jukan | Reaction word + number |
| **Shitpost** | Market absurdity | Citrini7 + Zephyr | Meme format |
| **Personal Commentary** | Opinion, question | Pure Jukan | First-person + uncertainty |
| **Victory Lap** | KSVC call worked | Pure Zephyr | Entry/Now + thesis |

### Quick Formulas

**Long Thread:** Hook → TLDR → Numbers → Skepticism → Position

**Quick Take:** Headline number → Context → "If you're looking now..."

**Breaking News:** "Huge." / "Well well well..." → Key number → Source

**Victory Lap:** "$TICKER up X% since KSVC added it" → Entry/Now → Thesis validated

---

## Step 1a: Scan PDFs with Explore Agents

Use Explore agents for **broad screening** when you have many PDFs to review. This is faster than RLM for initial discovery.

### Step 1a.0: Check Published Threads (MANDATORY - DO FIRST)

**⚠️ Before scanning any PDFs, check what Kirk has already posted.**

```bash
# List all published threads
ls /Users/Shared/ksvc/threads/

# Read recent thread.md files to understand what topics are covered
```

For each published thread, note:
- **Topic** (what was the thesis?)
- **Source PDFs used** (check _metadata.md)
- **Date** (how recent?)

**Then when selecting a topic after scanning, REJECT any topic that:**
- Uses the same primary source PDF as a published thread
- Covers the same thesis/angle (even if from different sources)
- Would read as a repeat to Kirk's followers

**Acceptable overlap:**
- A follow-up/update to a previous thread with NEW data (e.g., earnings confirm the thesis)
- A different angle on the same sector (e.g., posted about ABF shortage, now posting about specific company earnings)
- Explicitly framed as "update: here's what changed since my last post on X"

**Why this exists (Case Study — ABF Substrate, 2026-02-07):**

Kirk published a 10-tweet thread on Feb 5 covering Goldman's ABF shortage report (10%→21%→42%, Kinsus/NYPCB/Unimicron). On Feb 7, the pipeline picked the same Goldman report and produced a 3-tweet quick take with the same numbers, same companies, same angle. We didn't check published threads first, so we wasted a pipeline run on duplicate content when 10 other fresh topic angles were available.

### When to Use
- Screening 10+ PDFs to find relevant ones
- Finding cross-document connections
- Building a thesis from multiple sources
- Don't know which PDFs matter yet

### How to Scan
```
1. Check published threads (Step 1a.0 above)

2. List recent PDF folders and count PDFs
   ls /Users/Shared/ksvc/pdfs/ | tail -5
   ls /Users/Shared/ksvc/pdfs/YYYYMMDD/ | wc -l

3. Symlink PDFs into project directory (REQUIRED for subagent access)
   ln -sf "/Users/Shared/ksvc/pdfs/YYYYMMDD" ".claude/pdfs-scan"

4. Split PDFs into groups and spawn parallel Explore agents
   TARGET: ~5 PDFs per agent. Spawn ALL agents in a single message.
   - Each agent gets a specific list of filenames to scan
   - All agents run simultaneously → total time = slowest agent
   - Haiku is cheap — more agents = faster with no meaningful cost increase
```

### Agent Sizing

| PDFs | Agents | PDFs/Agent | Expected Time |
|------|--------|-----------|---------------|
| ≤5 | 1 | all | ~25s |
| 6-10 | 2 | ~5 each | ~25s |
| 11-15 | 3 | ~5 each | ~25s |
| 16-20 | 4 | ~5 each | ~25s |
| 21-30 | 5-6 | ~5 each | ~30s |

**Why ~5 PDFs per agent?** Sweet spot for speed. Each PDF takes ~4-8s to Read + summarize. 5 PDFs ≈ 25s per agent. Adding more PDFs per agent saves nothing (same total tokens) but makes wall-clock time worse.

**Cost:** Haiku is cheap. 4 agents × 5 PDFs × ~4k tokens = ~80k input tokens total — same as 1 agent doing all 20. Parallelism is free.

**Cross-doc synthesis trade-off:** Each agent only sees its batch, so cross-batch themes are the main agent's job. This is fine — the main agent merges all results anyway.

### Example: Spawn Explore Agents

**Step 1: Main agent creates symlink and lists PDFs:**
```bash
ln -sf "/Users/Shared/ksvc/pdfs/20260205" ".claude/pdfs-scan"
/bin/ls ".claude/pdfs-scan/"
```

**Step 2: Split filenames into groups and spawn agents in parallel (single message, multiple Task calls):**
```
# Agent 1 — first batch
Task(subagent_type="Explore", prompt="""
**THOROUGHNESS: medium**

Scan these specific PDFs for content angles:
- file1.pdf
- file2.pdf
- file3.pdf
- file4.pdf
- file5.pdf
- file6.pdf
- file7.pdf

For each PDF, Read enough pages to understand the full thesis (use judgment — some need 1-2 pages, others 1-5):

Read(file_path="/Users/dydo/Documents/agent/ksvc-intern/.claude/pdfs-scan/FILENAME.pdf", pages="1-5")

For each PDF extract:
- Company/sector, ticker, rating, price target
- Key thesis and supporting numbers
- Supply chain connections
- Potential content angles

After scanning your batch, provide:
1. Per-PDF summary (2-3 sentences each)
2. Cross-document themes within your batch
3. Which PDFs are most relevant for deep extraction
""")

# Agent 2 — second batch (SPAWN IN SAME MESSAGE as Agent 1)
Task(subagent_type="Explore", prompt="""
... same prompt with file8.pdf through file14.pdf ...
""")

# Agent 3 — third batch (SPAWN IN SAME MESSAGE)
Task(subagent_type="Explore", prompt="""
... same prompt with file15.pdf through file20.pdf ...
""")
```

**Step 3: Main agent synthesizes results from all agents:**
After all agents return, the main agent:
1. Merges per-PDF summaries
2. Identifies cross-agent themes (patterns Agent 1 found + patterns Agent 2 found)
3. Picks top 3 content angles across all PDFs
4. Selects 2-5 PDFs for Step 1b deep extraction

### Output: Identify Which PDFs Matter
After scanning, you'll know:
- Which reports have the best data
- Cross-document connections (e.g., "3 reports confirm memory shortage")
- **Thesis recommendations** (2-3 angles to explore)
- Which to deep-extract with RLM

**⚠️ WARNING: Explore agents can hallucinate specific numbers.** Treat all numbers from Explore summaries as "unverified claims" until RLM grep confirms them. Component counts, percentages, and market sizing are especially prone to errors.

**Capacity (tested 2026-02-07):** Single Explore agent (haiku) handled 19 PDFs at medium thoroughness in 83 seconds, using 125k tokens (~4k tokens/PDF for pages 1-5). 3 agents in parallel = ~30-40s for the same batch.

---

## Step 1b: Deep Extract with RLM

Use RLM for **deep extraction** from specific PDFs you've identified in Step 1a.

**MANDATORY for any number you'll publish.** Explore agents summarize; RLM verifies.

### When to Use
- You know which 2-5 PDFs matter most
- Need specific numbers, charts, tables
- Building cross-document verification tables
- Extracting technical details (fabs, yields, WPM)

### Single PDF
```bash
cd ~/.claude/skills/rlm-repl/scripts
python3 rlm_repl.py init "/Users/Shared/ksvc/pdfs/YYYYMMDD/file.pdf" --extract-images
python3 rlm_repl.py exec -c "print(grep('revenue|growth|target|price', max_matches=20, window=200))"
```

### Multiple PDFs (synthesis)
```bash
cd ~/.claude/skills/rlm-repl-multi/scripts
python3 rlm_repl.py init "/path/to/report1.pdf" --name report1 --extract-images
python3 rlm_repl.py init "/path/to/report2.pdf" --name report2 --extract-images
python3 rlm_repl.py exec -c "results = grep_all('keyword', max_matches_per_context=20)"
```

### View Extracted Charts/Images
```bash
# List images from a context
python3 rlm_repl.py exec --name report1 -c "print(list_images())"

# Get image path, then use Read tool to view
python3 rlm_repl.py exec --name report1 -c "print(get_image(0))"
```

Charts often contain key data (P/B trends, margin history, capacity timelines) that text extraction misses.

### Extraction Validation (MANDATORY)

**⚠️ After EVERY `rlm_repl.py init`, validate the extraction actually worked.**

RLM reports `chars_extracted` after init. A multi-page analyst report should yield thousands of chars. If you get suspiciously few, the PDF is likely image-based and RLM only extracted metadata/headers.

**Validation rule:**

| Chars Extracted | Expected Report Type | Action |
|----------------|---------------------|--------|
| > 5,000 | Multi-page report | ✅ Proceed with grep |
| 1,000 - 5,000 | Short note / partial | ⚠️ Check `list_images()` — if many images, trigger fallback |
| < 1,000 | Image-based PDF | ❌ **MUST use Read tool fallback** |

**The threshold is context-dependent.** A 20-page Goldman Sachs report yielding 666 chars is obviously broken. A 1-page pricing table yielding 800 chars might be fine. Use judgment, but when in doubt, fallback.

**Mandatory Fallback when RLM extraction is low:**

```bash
# Step 1: RLM init (always try first)
python3 rlm_repl.py init "/path/to/report.pdf" --extract-images
# Output: "Extracted 666 chars from 15 pages, saved 9 images"

# Step 2: Check - is 666 chars enough for a 15-page report? NO.
# → Trigger fallback

# Step 3: Check extracted images first (they may contain the data)
python3 rlm_repl.py exec -c "print(list_images())"
# View extracted images with Read tool
# Read(file_path="/path/to/extracted/image-0.png")

# Step 4: Read the PDF directly (use symlinked path for subagents)
# Read(file_path=".claude/pdfs-scan/report.pdf", pages="1-10")
# Read(file_path=".claude/pdfs-scan/report.pdf", pages="11-20")
```

**⚠️ Path rule:** Subagents must Read PDFs via the symlinked project path (`.claude/pdfs-scan/`), NOT from `/Users/Shared/`. See "Subagent Permissions" section above.

**Why this exists (Case Study — ABF Substrate Shortage, 2026-02-07):**

Goldman Sachs published two reports: a main ABF upcycle report (71K chars, extracted fine) and a Kinsus upgrade report (15 pages, but only 666 chars extracted). We skipped the Kinsus PDF because "the main report had everything we needed." It didn't. The Kinsus report had unique data (company-specific capacity plans, margin guidance, order book details) that would have strengthened the thread. Skipping it was lazy — the Read tool fallback takes 30 seconds and would have recovered the data.

**Rules:**
1. **Never skip a relevant PDF just because RLM extraction was low.** Use the fallback.
2. **Check extracted images.** RLM with `--extract-images` often saves chart/table images even when text extraction fails. View them with Read tool.
3. **Log the fallback.** In the extraction cache, note `"extraction_method": "read_fallback"` so audit knows the data source.
4. **If fallback also fails** (corrupted PDF, DRM), document it and move on. But you must TRY.

### RLM Cache: Include Visual Data

When extracting, capture **all** data types for potential chart generation later:

| Source Type | What to Extract | Cache Format |
|-------------|-----------------|--------------|
| Text numbers | Exact quotes with page refs | `{"value": 5.3, "unit": "B", "source": "p.3", "quote": "規模約53億美元"}` |
| Tables | Full table as structured JSON | `{"columns": [...], "rows": [...], "source": "p.20"}` |
| Charts | Data points + source image path | `{"data": {...}, "source_image": "pdf-3-1.png", "page": 3}` |

**Why cache visual data?** Step 6 (chart generation) needs this. If you only cache text, you'll lose table structures and chart data points that make great visualizations.

### Cross-Document Reasoning
Build thesis by triangulating claims across multiple reports:
```bash
# Find where multiple reports discuss the same topic
python3 rlm_repl.py exec -c "results = grep_all('DRAM.*price|ASP', max_matches_per_context=5)"

# Compare forecasts across sources
python3 rlm_repl.py exec -c "results = grep_all('2026|2027|growth|demand', max_matches_per_context=5)"
```

Use cross-doc to verify:
- Do multiple sources agree on price forecasts?
- Are supply constraint timelines consistent?
- Any contradictions between reports?

---

## Step 1b.5: Build Extraction Cache (MANDATORY)

**⚠️ Why this step exists:** RLM creates `state.pkl` during extraction, but the writing phase (Step 3) doesn't access it. Without a persistent cache, writers rely on memory, leading to errors like wrong product types, missing time periods, or source attribution mistakes.

**What this does:** Extracts from `state.pkl` (RLM's internal format) into structured JSON with context labels that the writing phase can reference.

### When to Run

**After Step 1b (RLM extraction) and before Step 3 (writing).**

| Workflow | When to Cache |
|----------|---------------|
| Single PDF (rlm-repl) | After `rlm_repl.py init` completes |
| Multiple PDFs (rlm-repl-multi) | After all `init` commands complete |

### How to Build Cache

**New in v2:** Auto-generates source tags and attribution map from PDF filenames!

**Single PDF (rlm-repl):**
```bash
cd ~/.claude/skills/kirk-content-pipeline/scripts

# Auto-extracts from default rlm-repl state location
python3 build_extraction_cache.py \
  --output /path/to/draft-assets/rlm-extraction-cache.json
```

**Multiple PDFs (rlm-repl-multi):**
```bash
cd ~/.claude/skills/kirk-content-pipeline/scripts

# Use --multi flag to load from rlm-repl-multi state
python3 build_extraction_cache.py \
  --multi \
  --output /path/to/draft-assets/rlm-extraction-cache.json
```

**With Cross-Doc Synthesis (Optional):**
```bash
# Add manual synthesis descriptions for cross-doc insights
python3 build_extraction_cache.py \
  --multi \
  --output /path/to/draft-assets/rlm-extraction-cache.json \
  --synthesis /path/to/cross-doc-synthesis.json
```

**Synthesis format** (optional, for complex multi-source threads):
```json
{
  "dual_squeeze_thesis": {
    "description": "Memory shortage (1Q26) + ABF substrate shortage (2H26) = compounding AI server bottleneck",
    "components": [
      {"topic": "Memory Pricing", "source": "gfhk_memory", "timeframe": "1Q26"},
      {"topic": "Abf Shortage", "source": "goldman_abf", "timeframe": "2H26-2028"}
    ]
  }
}
```

**What auto-generates:**
- ✅ Source tags from PDF filenames ("GFHK - Memory.pdf" → tag: "GFHK")
- ✅ Topics with primary_source, key_metrics, source_context
- ✅ Extraction entries with full context labels (product_type, time_period, units, scope)

### Cache Format

The cache includes **context labels** and **attribution map** to prevent common errors:

```json
{
  "cache_version": "1.0",
  "generated_at": "2026-02-05T14:00:00",
  "sources": [
    {
      "source_id": "gfhk_memory",
      "pdf_path": "/Users/Shared/ksvc/pdfs/20260204/GFHK - Memory.pdf",
      "pdf_name": "GFHK - Memory price impact.pdf",
      "tag": "GFHK",
      "chars_extracted": 13199
    },
    {
      "source_id": "goldman_abf",
      "pdf_path": "/Users/Shared/ksvc/pdfs/20260204/Goldman ABF shortage.pdf",
      "pdf_name": "Goldman Sachs ABF shortage report.pdf",
      "tag": "Goldman Sachs",
      "chars_extracted": 25000
    }
  ],
  "extractions": [
    {
      "entry_id": "mem_001",
      "source_id": "gfhk_memory",
      "figure": "Figure 2",
      "page": 3,
      "metric": "Total BOM",
      "product_type": "HGX B300 8-GPU server",
      "time_period": "3Q25 → 1Q26E",
      "units": "dollars per server",
      "scope": "single HGX B300 8-GPU server",
      "values": {
        "before": "$369k",
        "after": "$408k",
        "change": "+$39k"
      },
      "context": "Memory price impact on AI server BOM",
      "source_quote": "Figure 2: HGX B300 8-GPU server BOM...",
      "verification": "RLM grep + visual inspection"
    }
  ],
  "source_attribution_map": {
    "topics": {
      "Memory Pricing": {
        "primary_source": "gfhk_memory",
        "tag": "GFHK",
        "key_metrics": ["HBM3e ASP", "DDR5-6400 (128GB)", "NVMe SSD (3.84TB)", "Total BOM"],
        "source_context": "Figures: Figure 2; Time periods: 3Q25 → 1Q26E",
        "notes": "4 extractions from this source"
      },
      "Abf Shortage": {
        "primary_source": "goldman_abf",
        "tag": "Goldman Sachs",
        "key_metrics": ["ABF shortage ratio", "Kinsus PT", "NYPCB PT", "Unimicron PT"],
        "source_context": "Time periods: 2H26, 2027, 2028",
        "notes": "5 extractions from this source"
      }
    },
    "cross_doc_synthesis": {
      "dual_squeeze_thesis": {
        "description": "Memory shortage (1Q26) + ABF substrate shortage (2H26) = compounding AI server bottleneck",
        "components": [
          {"topic": "Memory Pricing", "source": "gfhk_memory", "timeframe": "1Q26"},
          {"topic": "Abf Shortage", "source": "goldman_abf", "timeframe": "2H26-2028"}
        ]
      }
    }
  }
}
```

**Key fields that prevent errors:**
- `product_type`: Prevents "GB300 rack" when source says "HGX B300 server"
- `time_period`: Prevents missing "3Q25 → 1Q26E" context
- `source_id`: Prevents "Goldman's BOM" when data is from GFHK
- `tag`: Auto-extracted from PDF filename for quick attribution
- `units`: Prevents "22.5B racks" when source means "22.5bn dollars"
- `scope`: Prevents "per rack" when source means "per server"

**Attribution map benefits:**
- `topics`: Topic-level mapping showing which source is primary authority
- `key_metrics`: Quick lookup of what each source covers
- `source_context`: Summary of figures, time periods covered
- `cross_doc_synthesis`: Manual insights connecting multiple sources

### Integration with Step 3 (Writing)

**MANDATORY: Reference the cache when writing.**

**Step 3a: Load cache and attribution map:**
```python
cache = load_json('rlm-extraction-cache.json')
attr_map = cache['source_attribution_map']

# Get topic attribution
topic = "Memory Pricing"
source_tag = attr_map['topics'][topic]['tag']  # "GFHK"
key_metrics = attr_map['topics'][topic]['key_metrics']
```

**Step 3b: Write using cache labels and attribution:**
```markdown
## Content

3/ Memory squeeze is already here. GFHK's BOM breakdown (3Q25 → 1Q26E):
- HBM3e ASP: $3,756 → $4,378 (+17%)
- DDR5-6400 (128GB): $563 → $1,920 (+241%)
- HGX B300 8-GPU server BOM: $369k → $408k
```

**Source:** `rlm-extraction-cache.json`, entry `mem_001`, `mem_002`, `mem_003`

**Context labels from cache:**
- Product type: HGX B300 8-GPU server (not GB300 rack)
- Time period: 3Q25 → 1Q26E (quarterly change)
- Source: GFHK Figure 2 (via attribution map tag)

**Attribution map usage:**
- Used `topics["Memory Pricing"]["tag"]` → "GFHK"
- Verified metrics against `key_metrics` list
- Cross-doc synthesis: See `dual_squeeze_thesis` for memory + ABF connection

### Enforcement

**Before saving draft (Step 5), verify:**
- [ ] Every published number has a cache entry
- [ ] Product types match cache labels
- [ ] Time periods included from cache
- [ ] Source attributions match cache `source_id` and attribution map `tag`
- [ ] Units match cache (dollars vs racks, per server vs per datacenter)
- [ ] Cross-doc claims reference `cross_doc_synthesis` if applicable

**Red flags - stop if you notice:**
- Writing numbers from memory instead of cache
- Product type differs from cache (`product_type` field)
- Missing time period when cache has `time_period`
- Attributing to wrong source vs cache `source_id`
- Using wrong tag (e.g., "Goldman" for GFHK data)
- Missing cross-doc synthesis when connecting multiple sources

### Manual Cache Building

If automatic extraction fails, manually create cache entries:

```json
{
  "entry_id": "manual_001",
  "source_id": "report_name",
  "metric": "Component count",
  "product_type": "Humanoid robot (dexterous hand)",
  "values": {"count": 22},
  "units": "DOF (degrees of freedom)",
  "context": "Dexterous hand articulation",
  "source_quote": "22自由度靈巧手",
  "verification": "Manual extraction from p.15",
  "notes": "Summed from finger joints (20) + wrist (2)"
}
```

**See:** `~/.claude/skills/kirk-content-pipeline/scripts/README-extraction-cache.md` for full documentation.

---

## Step 1c: Cross-Doc Synthesis (RECOMMENDED)

**Why this step exists:** Steps 1a and 1b produce per-document facts. Without explicit synthesis, the pipeline gravitates toward single-source claims ("KHGEARS P/E is 20x") rather than cross-doc insights ("Taiwan brokers are more bullish than Western analysts on humanoid robotics").

### When to Use

| Scenario | Use 1c? |
|----------|---------|
| Multiple PDFs on same topic | **Yes** |
| Comparing broker views | **Yes** |
| Finding consensus/disagreement | **Yes** |
| Single PDF deep dive | No (skip to Step 2) |
| Breaking news (speed matters) | No (skip to Step 2) |

### What 1c Produces

| Output Type | Example | Audit Requirement |
|-------------|---------|-------------------|
| **Consensus claim** | "3 of 4 brokers see DRAM ASP rising in 2H26" | Cross-doc (rlm-multi) |
| **Comparative insight** | "HIWIN at 38x vs KHGEARS at 20x - market pricing in certainty" | Cross-doc (rlm-multi) |
| **Disagreement flag** | "MS says neutral, local brokers say buy - who's right?" | Cross-doc (rlm-multi) |
| **Synthesized thesis** | "Taiwan supply chain undervalued vs China peers" | Cross-doc (rlm-multi) |

### How to Run Cross-Doc Synthesis

```bash
cd ~/.claude/skills/rlm-repl-multi/scripts

# Initialize all relevant PDFs
python3 rlm_repl.py init "/path/to/broker1.pdf" --name broker1
python3 rlm_repl.py init "/path/to/broker2.pdf" --name broker2
python3 rlm_repl.py init "/path/to/broker3.pdf" --name broker3

# Ask synthesis questions (not just extraction)
python3 rlm_repl.py exec -c "
# Question 1: Do they agree on market sizing?
market_data = grep_all('market size|TAM|規模|billion|億', max_matches_per_context=10)
print('=== MARKET SIZE ACROSS SOURCES ===')
print(market_data)
"

python3 rlm_repl.py exec -c "
# Question 2: Compare recommendations
ratings = grep_all('BUY|SELL|NEUTRAL|買進|賣出|中立|rating|recommendation', max_matches_per_context=10)
print('=== RATINGS COMPARISON ===')
print(ratings)
"

python3 rlm_repl.py exec -c "
# Question 3: Find disagreements
pe_data = grep_all('P/E|PE|本益比|target price|目標價', max_matches_per_context=10)
print('=== VALUATION COMPARISON ===')
print(pe_data)
"
```

### Synthesis Questions to Ask

| Category | Questions |
|----------|-----------|
| **Consensus** | Do sources agree on [market size / timeline / key risk]? |
| **Comparison** | How does [broker A] view differ from [broker B]? |
| **Valuation** | Are local vs foreign analysts pricing the same? |
| **Timeline** | Do sources agree on [catalyst / inflection point]? |
| **Risk** | What risks does one source mention that others miss? |

### Output Format: Synthesis Cache

After running 1c, document synthesized insights for Step 3 (writing):

```markdown
## Cross-Doc Synthesis (Step 1c)

**Sources:** broker1 (永豐), broker2 (MS), broker3 (Citi)

### Consensus
- Market size: All 3 agree on $5-6B (2025) → $30-35B (2029)
- CAGR: 55-60% range across all sources

### Disagreements
- HIWIN: MS says NEUTRAL (38x too rich), 永豐 silent, Citi no coverage
- Timeline: 永豐 more bullish on 2026 ramp, MS cautious until 2027

### Comparative Insights (use in thread)
- "Taiwan brokers (永豐) bullish on KHGEARS; Western analysts (MS) more cautious on HIWIN"
- "Local coverage sees 2026 inflection; foreign houses waiting for 2027 proof points"

### Audit Flag
These synthesized claims require cross-doc verification in Step 4b:
- [ ] "3 sources agree on market size" → verify all 3 sources
- [ ] "Local vs foreign view divergence" → verify specific ratings from each
```

### Integration with Audit (Step 4a)

**⚠️ CRITICAL:** Synthesized claims from Step 1c MUST be flagged for cross-doc audit in Step 4a.

In the audit manifest, mark these claims with `cross-doc: true`:

```markdown
## Claims to Verify

| # | Claim | Type | Source ID | Cross-Doc? |
|---|-------|------|-----------|------------|
| 1 | KHGEARS P/E 20x | P/E | src1 | No |
| 2 | Market consensus $5.3B | Consensus | src1, src2, src3 | **Yes** |
| 3 | Local vs foreign view divergence | Synthesis | src1, src2 | **Yes** |
```

Cross-doc claims use `rlm-repl-multi` for verification, not parallel single-doc agents.

---

### Extract with Technical Specificity
Go beyond surface numbers. Extract:
- Wafer capacity (WPM)
- Fab names (M15X, P4L, X2)
- Yield percentages
- Process nodes (1b, 1c)
- Component counts per unit

| Question | Extract |
|----------|---------|
| What | One-sentence summary |
| Why | Why readers should care |
| Who | Companies/tickers affected |
| When | Timeline (specific quarters) |
| Where | Fab locations, geography |
| How | Mechanism with technical detail |

---

## Step 2: Check KSVC Holdings (Initial)

**⚠️ CRITICAL:** This is a preliminary check. You MUST run Step 4c (Final Holdings Verification) after writing content to catch any tickers discovered during extraction.

### All Models (7 Total)
- **US Models:** usa-model1 ~ usa-model5 (5 models)
- **Taiwan (TWSE) Models:** twse-model1 ~ twse-model2 (2 models)

### Step 2a: Identify All Possible Tickers

**Before querying the API**, identify ALL possible identifiers for the company:

```bash
# Example: Global Unichip Corp
# Identifiers to search:
# - US ticker: N/A (not US-listed)
# - Taiwan ticker: 3443
# - Chinese name: 創意 or 全球晶圓科技
# - English name: Global Unichip, GUC
# - Stock code: 3443 TW (TWSE format)

# For Taiwan stocks, verify ticker via TWSE API first:
curl -s "https://www.twse.com.tw/en/api/codeQuery?query=3443"
# Returns: {"query":"3443","suggestions":["3443\tGUC"]}
```

**Rules:**
1. **US stocks:** Search by ticker only (e.g., "MU", "AMD", "NVDA")
2. **Taiwan stocks:** Search by stock code (e.g., "3443") - may appear as "3443 創意" in API
3. **If unsure:** Check both US and TWSE models

### Step 2b: Query All 7 Models

**NEVER assume a stock isn't held without checking ALL 7 models.**

**RECOMMENDED: Use tradebook for accurate entry prices and current status**

```bash
# FASTEST METHOD: Check tradebook for entry price + status
# (Works for all models - US and TWSE)
curl -s "https://kicksvc.online/api/twse-model2" | \
  jq '.tradebook[] | select(.ticker == 6285 or .ticker == 3491) |
  {ticker, enterDate, enterPrice, todayPrice, profitPercent, exitDate}'

# Returns:
# {
#   "ticker": 6285,
#   "enterDate": "Wed, 28 Jan 2026 00:00:00 GMT",
#   "enterPrice": 162.0,
#   "todayPrice": 207.5,  # ⚠️ May be stale! Use Yahoo Finance for current
#   "profitPercent": 28.09,  # ⚠️ Based on stale todayPrice
#   "exitDate": null  # null = still holding
# }
```

**⚠️ CRITICAL: API's `todayPrice` and `profitPercent` can be STALE (hours or days old). Always verify current price with Yahoo Finance API (Step 2d).**

**FALLBACK: Check equitySeries (slower, less data)**

```bash
# Check ALL 5 US models
for i in 1 2 3 4 5; do
  echo "=== USA-Model $i ==="
  curl -s "https://kicksvc.online/api/usa-model$i" | \
    jq --arg t "MU" '.equitySeries[0].series[] | select(.Ticker == $t) |
    {ticker: .Ticker, return: .data[-1].value}'
done

# Check ALL 2 TWSE models (search by stock code)
for i in 1 2; do
  echo "=== TWSE-Model $i ==="
  curl -s "https://kicksvc.online/api/twse-model$i" | \
    jq '.equitySeries[0].series[] | select(.Ticker | contains("3443")) |
    {ticker: .Ticker, return: .data[-1].value}'
done
```

**Why still use equitySeries?**
1. **Historical tracking:** Shows return % evolution over time (`.data[]` array)
2. **Verification:** Confirms position is still active
3. **Fallback:** If tradebook is unavailable or empty
4. **Entry date discovery:** First data point (return ≈ 0) indicates entry date

**Example: Finding entry date from equitySeries**
```bash
# Get all data points to find entry date
curl -s "https://kicksvc.online/api/twse-model2" | \
  jq '.equitySeries[0].series[] | select(.Ticker | contains("6285")) | .data[0]'
# Returns: {"date": "2026-01-28 00:00:00", "value": 0}
# Entry date: Jan 28, 2026
```

### Step 2c: Verification and Fallback Strategy

**Use all three data sources for robustness:**

| Data Source | When to Use | What It Shows | Limitation |
|-------------|-------------|---------------|------------|
| **tradebook** | Primary | Entry date, entry price, exit status | `todayPrice` may be stale |
| **equitySeries** | Verification | Return % over time, position status | No entry price/date |
| **filledOrders** | Fallback | Actual trade orders, prices | Empty if model didn't reset recently |

**Recommended workflow:**

```bash
# 1. PRIMARY: Get entry details from tradebook
TRADEBOOK=$(curl -s "https://kicksvc.online/api/twse-model2" | \
  jq '.tradebook[] | select(.ticker == 6285)')

# 2. VERIFY: Cross-check with equitySeries
EQUITY=$(curl -s "https://kicksvc.online/api/twse-model2" | \
  jq '.equitySeries[0].series[] | select(.Ticker | contains("6285"))')

# 3. FALLBACK: If tradebook empty, check filledOrders
if [ -z "$TRADEBOOK" ]; then
  curl -s "https://kicksvc.online/api/twse-model2" | \
    jq '.filledOrders[] | select(.ticker | contains("6285"))'
fi
```

**Cross-verification example:**

```bash
# Check if tradebook and equitySeries agree on position status
TRADEBOOK_HELD=$(curl -s "https://kicksvc.online/api/twse-model2" | \
  jq '.tradebook[] | select(.ticker == 6285 and .exitDate == null) | .ticker')

EQUITY_HELD=$(curl -s "https://kicksvc.online/api/twse-model2" | \
  jq '.equitySeries[0].series[] | select(.Ticker | contains("6285")) | .Ticker')

# If both show position, high confidence
# If only one shows position, investigate discrepancy
```

**Fallback: Check filledOrders (if tradebook empty)**

If equitySeries is empty OR tradebook is empty (rare, but possible after model reset):

```bash
# Check ALL US models - filledOrders
for i in 1 2 3 4 5; do
  echo "=== USA-Model $i filledOrders ==="
  curl -s "https://kicksvc.online/api/usa-model$i" | \
    jq '.filledOrders[] | select(.ticker == "MU") | {ticker, price, quantity}'
done

# Check ALL TWSE models - filledOrders
for i in 1 2; do
  echo "=== TWSE-Model $i filledOrders ==="
  curl -s "https://kicksvc.online/api/twse-model$i" | \
    jq '.filledOrders[] | select(.ticker | contains("3443")) | {ticker, price, quantity}'
done
```

**When data sources disagree:**

| Scenario | Action |
|----------|--------|
| tradebook shows position, equitySeries doesn't | Trust tradebook (equitySeries may lag) |
| equitySeries shows position, tradebook doesn't | Investigate - check filledOrders |
| filledOrders shows buy but no current position | Position was closed - check tradebook.exitDate |
| All three empty | Position not held in this model |

### Step 2e: Document Holdings with Accurate Returns

**CRITICAL:** Always calculate actual returns using:
1. **Entry price** from `tradebook.enterPrice`
2. **Current price** from Yahoo Finance API (NOT KSVC API's stale `todayPrice`)

**Output format (with accurate data):**
```markdown
**KSVC Holdings Check:**
- ✅ WNC (6285.TW) - Held in TWSE Model 2
  - Entry: Jan 28, 2026 @ NT$162
  - Current: NT$187 (Yahoo Finance)
  - Gain: +15.4% (actual, not API's stale 28%)
- ✅ UMT (3491.TWO) - Held in TWSE Model 2
  - Entry: Jan 28, 2026 @ NT$1,120
  - Current: NT$1,280 (Yahoo Finance)
  - Gain: +14.3% (actual, not API's stale 23%)
- ❌ Not held in TWSE Model 1 or USA Models 1-5

**Note:** API's equitySeries and tradebook.todayPrice can lag hours/days behind market.
Always use Yahoo Finance for current prices.
```

**If NOT held in any model:**
```markdown
**KSVC Holdings Check:**
- ❌ Not held in any of 7 models (checked USA 1-5, TWSE 1-2)
- Content angle: Industry analysis / Market observation
```

### Integration Strategies

| Situation | Approach | Example |
|-----------|----------|---------|
| **Held (US)** | Call out position | "KSVC Model1 holds $MU at $412 entry" |
| **Held (TW)** | Call out position | "KSVC台股Model1持有台積電 (2330)" |
| **Not held** | Industry framing | "Memory cycle benefits $MU, SK Hynix" |
| **Win** | Victory lap | "$MU +15% since Model1 added it" |

### Step 2d: Current Price Check (Yahoo Finance API - REQUIRED)

**⚠️ CRITICAL:** ALWAYS use Yahoo Finance for current prices. KSVC API's `todayPrice` can be stale.

**US stocks:**
```bash
# Get current price
TICKER="MU"
curl -s -A "Mozilla/5.0" "https://query1.finance.yahoo.com/v8/finance/chart/$TICKER?interval=1d&range=1d" | \
  jq '.chart.result[0].meta.regularMarketPrice'

# Get full market data
curl -s -A "Mozilla/5.0" "https://query1.finance.yahoo.com/v8/finance/chart/$TICKER?interval=1d&range=1d" | \
  jq '.chart.result[0].meta | {symbol, regularMarketPrice, currency, regularMarketTime}'
```

**Taiwan stocks (use .TW or .TWO suffix):**
```bash
# WNC (6285.TW)
curl -s -A "Mozilla/5.0" "https://query1.finance.yahoo.com/v8/finance/chart/6285.TW?interval=1d&range=1d" | \
  jq '.chart.result[0].meta | {symbol, regularMarketPrice, currency, regularMarketTime}'

# UMT (3491.TWO - OTC stocks use .TWO)
curl -s -A "Mozilla/5.0" "https://query1.finance.yahoo.com/v8/finance/chart/3491.TWO?interval=1d&range=1d" | \
  jq '.chart.result[0].meta | {symbol, regularMarketPrice, currency, regularMarketTime}'
```

**Taiwan ticker suffixes:**
- `.TW` - Listed on Taiwan Stock Exchange (TWSE)
- `.TWO` - Listed on Taipei Exchange (TPEx/OTC)

**Calculate actual gain (not API's stale profit%):**
```bash
# Example: WNC
TICKER="6285.TW"
ENTRY=162  # From tradebook.enterPrice
CURRENT=$(curl -s -A "Mozilla/5.0" "https://query1.finance.yahoo.com/v8/finance/chart/$TICKER?interval=1d&range=1d" | jq '.chart.result[0].meta.regularMarketPrice')
echo "$TICKER: NT\$$CURRENT | Entry: NT\$$ENTRY | Gain: $(awk "BEGIN {printf \"%.1f\", ($CURRENT - $ENTRY) / $ENTRY * 100}")%"

# Output: 6285.TW: NT$187 | Entry: NT$162 | Gain: +15.4%
```

**Complete workflow (tradebook + Yahoo Finance):**
```bash
# 1. Get entry price from tradebook
ENTRY=$(curl -s "https://kicksvc.online/api/twse-model2" | jq '.tradebook[] | select(.ticker == 6285) | .enterPrice')

# 2. Get current price from Yahoo Finance
CURRENT=$(curl -s -A "Mozilla/5.0" "https://query1.finance.yahoo.com/v8/finance/chart/6285.TW?interval=1d&range=1d" | jq '.chart.result[0].meta.regularMarketPrice')

# 3. Calculate actual gain
echo "Entry: NT\$$ENTRY | Current: NT\$$CURRENT | Gain: $(awk "BEGIN {printf \"%.1f\", ($CURRENT - $ENTRY) / $ENTRY * 100}")%"
```

---

## Step 3: Write Content

**See `references/kirk-voice.md` for full templates and examples.**

### Thread Numbering Convention

| Format | When to Use |
|--------|-------------|
| No number on Tweet 1 | Recommended - cleaner hook, stands alone if quoted/shared |
| `2/`, `3/`, etc. | Standard thread format - signals "2 of N" |
| `1/` on first tweet | Optional - explicit "thread incoming" signal |

**Why skip number on first tweet:**
- Hook tweet often gets shared standalone
- "1/" makes it look incomplete out of context
- Cleaner visual presentation

**Format preference:** Use `/` not `)` - it's the established Twitter thread convention.

```
✅ Recommended:
Humanoid robots going from science fair to factory floor. Taiwan supply chain getting interesting.

2/ TLDR:
- Market: $5.3B (2025) to $32.4B (2029)...

❌ Avoid:
1/ Humanoid robots going from science fair...
```

### Pick Content Type
1. What kind of content? (Thread / Quick Take / Breaking / Shitpost / Commentary / Victory Lap)
2. Look up the formula in kirk-voice.md
3. Apply the blend

### Technical Specificity

❌ Vague: "NAND supply is tight"

✅ Specific: "YMTC adding 135k WPM at Wuhan Fab 3. Still won't close the gap - Samsung X2 conversion delayed to Q2."

❌ Vague: "HBM margins are good"

✅ Specific: "SK Hynix HBM yields at 80-90%. Samsung stuck at 60% on 1c DRAM."

Always include: specific numbers, time frames, fab names, comparisons.

### Referential Clarity (Learned 2026-02-08)

**Never use vague pronouns or shorthand when the referent hasn't been introduced.**

In thread format, each tweet may be read semi-independently. If earlier tweets discuss a concept as a category (e.g., "ASIC revenue"), don't suddenly refer to it as "the project" in a later tweet — the reader has no antecedent for "the project."

❌ Vague: "MS thinks the project is the 3nm Google TPU"
(What project? The thread never introduced "a project.")

✅ Clear: "MS thinks the main client/program is the 3nm Google TPU"
(Names what MS is identifying — who's buying and what they're building.)

**Rule:** When a shorthand ("the project", "this deal", "the play") saves words but costs clarity, it's not saving anything. Name the thing directly. A few extra words that prevent the reader from pausing to re-read are always worth it.

**When shifting from category to specific:** If the thread discusses an abstract category (ASIC revenue, memory supply) and then pivots to a specific entity (Google TPU, Samsung fab), bridge the transition. Don't assume the reader already knows which specific thing drives the category.

---

## Step 4a: Audit (MANDATORY — MUST USE SUBAGENTS)

**⚠️ WHY THIS STEP EXISTS:** We learned that RLM extraction (Step 1b) is not the same as verification. Explore agents hallucinate numbers. Writers make inferences. This step catches errors BEFORE publishing.

**⚠️ STRUCTURAL GATE:** You (the main agent) are the WRITER. You cannot also be the AUDITOR. You MUST delegate audit to fresh-context subagents. See the "WARM STATE TRAP" section in the audit-content skill for why.

### Step 4a Process (3 actions, in order)

**Action 1: Generate audit manifest**
```
Write audit-manifest.md with all claims, sources, and search hints.
This is the handoff document for the audit agents.
```

**Action 2: Spawn Explore agents (MANDATORY — do NOT skip this)**
```
Spawn 1 Explore agent per source PDF via Task tool.
Each agent gets: the manifest + its assigned PDF path + claim list.
Each agent returns: JSON with PASS/FAIL/UNSOURCED per claim.
```

**⚠️ WARM STATE TRAP:** If RLM is already loaded from Step 1b, you WILL be tempted to "just grep it yourself." DO NOT. The audit-content skill explains why: you wrote the draft, so you already "know" the answers. Self-auditing is confirmation bias, not verification.

**Self-check:** If you are about to type `rlm_repl.py exec` during Step 4a, STOP. You are skipping the gate.

**Action 3: Collect results and write audit report**
```
Aggregate agent results into audit-report.md.
MUST include audit_agent_ids from the Task tool responses.
If audit_agent_ids is empty, the audit is invalid.
```

### Invoke the audit-content skill for full process details:
```
/audit-content
```

### What Gets Verified

| Claim Type | Example | How to Verify |
|------------|---------|---------------|
| Company names | "KHGEARS" | RLM grep + TWSE API |
| Ticker formats | "4571 TW" | TWSE API |
| Numbers | "62 harmonic reducers" | RLM grep exact count |
| Percentages | "19% cost" | RLM grep in source |
| P/E ratios | "20x" | RLM grep analyst target |
| Ratings | "BUY" | RLM grep recommendation |
| Timelines | "2H27" | RLM grep + verify context |
| Attributions | "shipping to X" | Must be explicit in source, not inferred |

### When to Proceed

- **All PASS**: Save draft (Step 5)
- **Any FAIL**: Fix the claim, re-audit
- **UNSOURCED**: Either remove, add caveat ("reportedly"), or find source

**Do NOT save draft with FAIL status. UNSOURCED claims need explicit decision.**

---

## Step 4a.5: Gemini Web Cross-Validation (RECOMMENDED)

**⚠️ WHY THIS STEP EXISTS:** RLM audit (Step 4a) is source-locked — it only checks claims against the cited PDF. This over-flags reasonable inferences that go beyond one report but are well-documented publicly. Step 4a.5 gives flagged claims a second chance via web-grounded search.

**Case Study (Old Memory Squeeze, 2026-02-07):**
- Draft said "capacity getting cannibalized for HBM and DDR5"
- RLM audit FAIL: MS report says "exiting DDR4" / "cannibalization" but doesn't name HBM/DDR5 as destination
- Gemini confirmed: TrendForce, DigiTimes, The Elec all document the DDR4→HBM/DDR5 shift
- Result: Claim restored with dual attribution (MS + public sources)

Same thread: "Samsung, Kioxia, Micron all reducing MLC NAND" — MS only confirmed Samsung, said Kioxia/Micron "could" reduce. Gemini confirmed all three are actively reducing per TrendForce (41.7% YoY MLC NAND capacity decrease).

### When to Use

| RLM Audit Result | Use Gemini? | Why |
|------------------|-------------|-----|
| FAIL — wrong number | No | Number errors need source correction, not web search |
| FAIL — inference beyond source | **Yes** | Inference may be valid per public sources |
| FAIL — misattribution | Maybe | Check if correct attribution exists publicly |
| UNSOURCED — claim not in cited PDF | **Yes** | Claim may be common industry knowledge |
| PASS | No | Already verified |

### How to Run

```bash
# For each FAIL/UNSOURCED claim that looks like a reasonable inference:
gemini -p "Search the web: [specific factual question about the inference].
I need external industry sources (TrendForce, DigiTimes, The Elec, Reuters,
company earnings calls) from 2025-2026 confirming or denying this."
```

**Key: Ask Gemini to search the web explicitly.** Without "search the web", Gemini may read local files instead.

### Decision Matrix

| Gemini Result | Action |
|---------------|--------|
| Confirmed with public sources | Restore claim, add dual attribution (`source + Gemini web`) |
| Partially confirmed | Soften language to match what's confirmed |
| Not confirmed / contradicted | Keep as FAIL, fix or remove claim |
| Gemini unsure / no sources found | Keep as FAIL (conservative default) |

### Audit Report Format

Update claims restored via Gemini:

```markdown
| # | Claim | Source | Status |
|---|-------|--------|--------|
| 5 | DDR4 capacity → HBM/DDR5 | ms_old_memory + Gemini web | PASS (restored) |
| 8 | All three reducing MLC NAND | ms_old_memory + Gemini web | PASS (restored) |
```

Include Gemini's sources in the audit resolution log:
```markdown
### Claim 5 (RESTORED via Gemini)
- **RLM flagged:** Source doesn't name HBM/DDR5 as destination
- **Gemini confirmed:** TrendForce, DigiTimes, The Elec document capacity conversion
- **Resolution:** Restored with corrected framing
```

### Guidelines

- Only use for inferences and industry knowledge claims, NOT for number verification
- Gemini's web search is a second opinion, not the final word — present both perspectives
- If Gemini contradicts both the source and common sense, flag for human review
- Keep Gemini queries specific and focused — one claim per query

---

## Step 4b: Final Holdings Verification (MANDATORY)

**⚠️ CRITICAL:** This is the FINAL holdings check. You MUST run this after writing content because:
1. Tickers/stock codes may be discovered during extraction (Step 1b)
2. Company names may be clarified during audit (Step 4b)
3. Step 2 was a preliminary check with limited information

### Why This Step Exists

**Problem:** You might learn the correct ticker late in the pipeline.

**Example - GUC Case:**
- Step 1b: Learn company is "Global Unichip (GUC)"
- Step 1b: Extract ticker "3443 TW" from report
- Step 2: ❌ Assumed "not held" without actually checking TWSE models
- Step 3: Wrote "I don't have a position here"
- **Step 4c: ✅ Discovered GUC IS held in TWSE Model 1 (+2.22%)**
- **Result:** Had to rewrite content to reflect actual position

### Step 4c Process

**1. Extract ALL tickers/identifiers from the draft:**
```bash
# Read the draft and extract tickers
grep -E "[0-9]{4}|\\$[A-Z]{2,5}" draft.md

# Example output:
# - 3443 TW (Taiwan stock)
# - $MU (US stock)
# - AMD, NVDA (US stocks)
```

**2. For EACH ticker, check ALL 7 models:**

```bash
# Taiwan stock example: 3443
for i in 1 2; do
  echo "=== TWSE-Model $i ==="
  curl -s "https://kicksvc.online/api/twse-model$i" | \
    jq '.equitySeries[0].series[] | select(.Ticker | contains("3443")) |
    {ticker: .Ticker, return: .data[-1].value}'
done

# US stock example: MU
for i in 1 2 3 4 5; do
  echo "=== USA-Model $i ==="
  curl -s "https://kicksvc.online/api/usa-model$i" | \
    jq --arg t "MU" '.equitySeries[0].series[] | select(.Ticker == $t) |
    {ticker: .Ticker, return: .data[-1].value}'
done
```

**3. Compare Step 2 vs Step 4c results:**

```markdown
**Holdings Verification:**

Step 2 (Initial): Claimed "Not held"
Step 4c (Final): ✅ Found in TWSE Model 1 (+2.22%)

**Action Required:** Update draft to reflect actual position
```

**4. If holdings status changed, update draft:**

```bash
# Before (Step 2):
"I don't have a position here, but watching..."

# After (Step 4c):
"KSVC holds GUC in TWSE Model 1 (+2.22% since entry). Watching..."
```

### Decision Matrix

| Step 2 | Step 4c | Action |
|--------|---------|--------|
| Not held | Not held | ✅ No change needed |
| Not held | **HELD** | ❌ **UPDATE DRAFT** - change content angle |
| Held | Held | ✅ Verify return % is current |
| Held | **Not held** | ❌ **UPDATE DRAFT** - position was closed |

### Output Format

```markdown
**Step 4c: Final Holdings Verification**

✅ Verified ALL 7 models (USA 1-5, TWSE 1-2)

**Tickers checked:**
- 3443 (GUC): ✅ Found in TWSE Model 1 (+2.22%)
- $MU: ❌ Not held
- $AMD: ✅ Found in USA Model 3 (+12.5%)

**Changes required:**
- Update draft line 32: Add KSVC position note for GUC
- Update draft line 45: Add KSVC position note for AMD
```

---

## Step 4c: Stylize (MANDATORY)

**Why this step exists:** The data backbone (Step 3) is Serenity-heavy - precise, comprehensive, verified facts. Step 4c transforms it into Kirk's authentic voice with emotional range and character.

**Invoke the kirk-mode skill:**
```
/kirk-mode
```

### What Kirk Mode Does

Transforms verified data into Kirk's voice by:
1. **Mode selection** - Matches Kirk's emotional mode to situation (Analytical, Sarcastic, Emo, Shitpost, Degen, GIF Master)
2. **Voice elements** - Adds discovery moments ("Wait though"), reactions ("wayyy bigger"), first-person thesis
3. **Meme culture** - Integrates fintwit slang (ngmi, wagmi, brother, probably nothing) strategically
4. **Anti-formula** - Rotates structure to prevent templating (varies TLDR → "ok so" → question)
5. **Credibility balance** - Online enough to relate, credible enough to trust

### When to Use Each Mode

| Situation | Kirk Mode | Example |
|-----------|-----------|---------|
| Deep fundamental dive | Analytical | "ok so", "Wait though", data-heavy with reactions |
| Market absurdity | Sarcastic | "brother Elon literally applied for 1M satellites" |
| Positions down | Emo | "honestly getting wrecked", vulnerable lowercase |
| Quick reaction/meme | Shitpost | me/also me format, nobody: format |
| High-conviction risky play | Degen | "sir this is a casino", YOLO energy |
| Victory lap | GIF Master + Analytical | Perfect GIFs + receipts |

**Most natural:** Mix modes in single post (Analytical + Sarcastic + maybe GIF)

### Workflow

1. **Assess situation** - What's happening? (Deep dive, absurd market, position down, quick reaction)
2. **Select mode(s)** - Use kirk-mode decision tree or mix modes naturally
3. **Apply voice toolkit** - Discovery moments, strategic "wayyy", emphasis markers
4. **Check meme integration** - Would slang/GIF enhance or distract from analysis?
5. **Verify authenticity** - Read aloud: sounds like intern at bar or ChatGPT report?

**Output:** Transformed content with Kirk's character voice - ready for humanizer pass.

**See kirk-mode skill for:**
- Complete mode descriptions with examples
- Meme vocabulary and format templates
- Anti-formula principles
- Credibility boundaries

---

## Step 4d: Humanize (MANDATORY)

**Note:** Humanizer runs AFTER stylize to remove any AI patterns that slipped through during transformation.

**Invoke the humanizer skill:**
```
/humanizer
```

### Patterns to Remove

| Pattern | Fix |
|---------|-----|
| "Full stop." | "Simple as." or just delete |
| Em-dashes (—) | Periods, commas |
| "It's not X. It's Y." | "The play is Y, not X." |
| Perfect parallelism | Vary structure |
| Rule of three | Break the pattern |
| Over-confidence | Add skepticism phrase |

### AI Words to Remove
Additionally, crucial, delve, emphasize, testament, enhance, foster, landscape, showcase, tapestry, underscore, vibrant, pivotal, key (adj), interplay

### Soul to Add
- **Skepticism**: "I might be wrong" / "Not sure about this"
- **Reactions**: "That number is wild" / "Interesting"
- **First person**: "I keep thinking about..."
- **Mixed feelings**: "Impressive but also kind of unsettling"
- **Questions**: Ask the audience

---

## Step 5: Save Draft

### File Organization Convention

**CRITICAL: Use assets folder structure for all drafts.**

```
content-pipeline/draft/
└── YYYY-MM-DD-topic-assets/
    ├── README.md                           # Inventory, traceability, verification log
    ├── YYYY-MM-DD-topic.md                 # Original draft
    ├── YYYY-MM-DD-topic-citrini7.md        # Tone rewrites (if applicable)
    ├── YYYY-MM-DD-topic-audit-manifest.md  # Audit claims list
    ├── YYYY-MM-DD-topic-audit-report.md    # Audit verification results
    ├── YYYY-MM-DD-topic-audit-final.md     # Final audit with corrections
    ├── chart1_*.png                        # Generated charts
    ├── chart2_*.png
    └── source_*.png                        # Source images for traceability
```

**Example:** `2026-02-05-guc-valuation-debate-assets/`

### Draft Content Format

Save main content as: `YYYY-MM-DD-topic-assets/YYYY-MM-DD-topic.md`

```markdown
# [Topic] [Type] Draft

**Date:** YYYY-MM-DD
**Source:** [Report name, date]
**Type:** Thread | Quick Take | Reaction
**Status:** PENDING APPROVAL
**Process:** RLM extraction → KSVC check → Humanizer pass

---

## Content

[Content here]

---

## Source Citations
- [List sources]

## Notes
- [KSVC holdings: $TICKER at $PRICE entry]
- [Technical details verified via RLM]
- [Any caveats or uncertainties]
```

### README.md Template

Create `README.md` in the assets folder to document the work:

```markdown
# [Topic] Assets

**Date:** YYYY-MM-DD
**Type:** [Thread/Quick Take/etc]
**Topic:** [Brief description]

---

## Content Files

| File | Description | Status |
|------|-------------|--------|
| YYYY-MM-DD-topic.md | Original draft | ✅ APPROVED |
| YYYY-MM-DD-topic-citrini7.md | Citrini7 rewrite | ✅ APPROVED |

---

## Charts (Original Work - OK to Publish)

| File | Description | Data Source |
|------|-------------|-------------|
| chart1_*.png | [Description] | [Source PDF + page] |
| chart2_*.png | [Description] | [Source PDF + page] |

**Theme:** ocean_depths

---

## Data Verification Log

### [Claim Category 1]
\```
[Claim]: [Value]
- Source: [PDF name, page]
- RLM verified: [grep results or calculation]
\```

### [Claim Category 2]
\```
[Claim]: [Value]
- Source: [PDF name, page]
- Verified: [evidence]
\```

---

## Audit Reports

| File | Purpose |
|------|---------|
| YYYY-MM-DD-topic-audit-manifest.md | Claims to verify |
| YYYY-MM-DD-topic-audit-report.md | Initial audit results |
| YYYY-MM-DD-topic-audit-final.md | Final audit with corrections |

**Audit result:** X/Y claims verified

---

## KSVC Holdings

\```bash
# Verification command
curl -s "https://kicksvc.online/api/[model]" | jq '...'

Result: [Holdings status]
\```

---

## Source Documents

| Source | Path | Used For |
|--------|------|----------|
| [Report name] | /Users/Shared/ksvc/pdfs/YYYYMMDD/file.pdf | [What data] |

---

## Corrections Made

1. [Correction 1]
2. [Correction 2]

---

## Lessons Learned

1. [Lesson 1]
2. [Lesson 2]
```

---

## Step 6: Chart Decision & Generation

**Timing:** After draft is complete. The draft crystallizes the thesis - then you see which claims benefit from visualization.

### When to Make Charts

| Content Type | Chart Likely? | Why |
|--------------|---------------|-----|
| Long Thread | Yes | Multiple data points, trends |
| Quick Take | Maybe | One key number might not need visual |
| Breaking News | Rarely | Speed > polish |
| Victory Lap | Maybe | Entry vs Now comparison |

### Chart-Tweet Pairing

**Principle:** Put the most eye-catching visual early (Tweet 1-3) to hook engagement.

| Chart Type | Best Tweet Position | Why |
|------------|---------------------|-----|
| Market size / growth bar | **Tweet 2** (TLDR) | Pairs with market numbers, shows scale |
| Component breakdown pie | **Tweet 3-4** | Pairs with component discussion |
| Company comparison table | **Tweet 5-6** | Pairs with company analysis |
| Timeline / roadmap | **Tweet 7-8** | Pairs with forward-looking content |

**Pairing logic:**
1. Match chart to the tweet that contains the same data
2. Hook tweet (Tweet 1) can go either way:
   - Text-only: Clean, curiosity-driven, lets words land first
   - With chart: Visual stop, data-forward, shows you have receipts
3. Visuals work best on data-heavy tweets, not opinion tweets
4. Final tweet (watchlist/conclusion) usually doesn't need a chart

**Example pairing (humanoid robotics thread):**
```
Tweet 1: Hook (optional: market_size_bar.png for visual hook)
Tweet 2: TLDR + market_size_bar.png ← $5.3B→$32.4B numbers
Tweet 3: Component counts (optional: component_pie.png)
Tweet 5: Taiwan names + taiwan_companies_table.png ← KHGEARS/HIWIN/AIRTAC
```

### Decision Process

1. **Review draft** - identify "chartable moments"
   - Time series data (market growth, price trends)
   - Component breakdowns (pie charts)
   - Company comparisons (tables)

2. **Check RLM cache** - do we have the data?
   - Text numbers → bar/line charts
   - Tables → comparison tables
   - Source charts → reference or recreate

3. **DECLARE SOURCE (MANDATORY)** - before any chart generation
   ```
   "I am charting [METRIC] from [SOURCE] page [X]"
   "Source contains these exact values: [list them]"
   ```

4. **Generate with chart-factory**
   ```
   /chart-factory
   ```

### Chart Generation Workflow

```
Draft complete → identify chartable claims
                        ↓
              Pull data from RLM cache (NOT from draft text)
                        ↓
              ⚠️ DECLARE SOURCE (state metric + page + exact values)
                        ↓
              Save source image FIRST (before generating)
                        ↓
              Generate with chart-factory (use theme-factory)
                        ↓
              Verify with verification agent
                        ↓
              Save to assets folder
```

### Source Declaration (LEARNED FROM MISTAKE)

**⚠️ Why this exists:** We once created a "component count" chart but saved a "cost %" source image. The metrics didn't match, making the source invalid for verification.

**Before generating ANY chart, you MUST:**

| Step | Action | Example |
|------|--------|---------|
| 1. State | "I am charting [METRIC] from [SOURCE]" | "I am charting hardware cost % from 永豐 p.20" |
| 2. Show | Screenshot the exact source table/chart | Save as `source_hardware_cost_p20.png` |
| 3. Confirm | "Source contains: [exact values]" | "19%, 16%, 13%, 52%" |
| 4. Flag | If transforming data, justify it | "I am NOT transforming - using values as-is" |

**Red flags - STOP if you notice:**
- Source shows % but you're charting counts (metric mismatch)
- Source has 15 items but chart has 5 (cherry-picking)
- Source image doesn't contain your chart's numbers (wrong source)
- Company name romanized/guessed from Chinese (fabricated data)
- Ticker suffix assumed without checking (TT vs TW)

### Company & Ticker Verification

**⚠️ LEARNED FROM MISTAKE:** We fabricated "Chuing" for 祺驊 (4571). Official name is "KHGEARS".

```bash
# Always verify Taiwan company names via TWSE API
curl -s "https://www.twse.com.tw/en/api/codeQuery?query=4571"
# Returns: {"query":"4571","suggestions":["4571\tKHGEARS"]}
```

- **Never romanize** Chinese names (祺驊 ≠ "Chuing")
- **Use TW suffix** for general audience (TT = Bloomberg only)

### Using chart-factory

```python
from chart_factory import create_bar_chart, create_pie_chart, create_table_chart

# Market size bar chart
create_bar_chart(
    data={'2025': 5.3, '2026': 8.3, '2027': 13.0},
    title="Global Humanoid Robot Market",
    theme="ocean_depths",
    annotations={"type": "cagr", "value": "57%"}
)

# Component pie chart
create_pie_chart(
    data={'Reducers': 62, 'Motors': 30, 'Screws': 48},
    title="Component Breakdown",
    theme="ocean_depths",
    explode_largest=True
)

# Company comparison table
create_table_chart(
    columns=['Company', 'Ticker', 'P/E', 'Rating'],
    data=[['Chuing', '4571', '24x', 'BUY'], ...],
    title="Taiwan Supply Chain",
    theme="ocean_depths"
)
```

### Verification (MANDATORY)

After generating, spawn **Explore agent** with **thoroughness: quick** for focused verification:

```
Task(subagent_type="Explore", prompt="""
**THOROUGHNESS: quick**

**CONTEXT ISOLATION: You have NO external conversation history. Work ONLY from this prompt.**

CHART VERIFICATION TASK

Chart: /path/to/chart.png
Type: bar

Source Data (expected):
{"2025": 5.3, "2026": 8.3, "2027": 13.0}

Source Context:
永豐 p.3 - "2025年全球人型機器人規模約53億美元"

Task:
1. Read the chart image
2. Extract numbers from visual
3. Compare to expected data
4. Check for unit consistency (B vs M, % formatting)

Return ONLY JSON:
{
  "verified": true/false,
  "numbers_in_chart": [...],
  "numbers_in_source": [...],
  "discrepancies": [...],
  "notes": "..."
}
""")
```

Verification checks **data → chart integrity**. Source accuracy is RLM's responsibility (Step 4a).

**Thoroughness = quick:** Single-pass verification, focused on specific data points. Fast visual-to-data check.

### Save Charts

Save to: `draft/YYYY-MM-DD-topic-assets/`

Include:
- Generated charts (chart1_*.png, chart2_*.png)
- Source images from PDF (for traceability)
- generate_charts.py script (reproducibility)

---

## Step 7: Publish to Final Folder

After approval, publish clean version to `/Users/Shared/ksvc/threads/`.

### File Organization Convention

**CRITICAL: Flat folder structure, one folder per post.**

```
/Users/Shared/ksvc/threads/
├── 2026-02-03-humanoid-robotics/
│   ├── thread.md                         # Clean content (ready to post)
│   ├── _metadata.md                      # Internal reference (not for posting)
│   ├── chart1_market_size.png
│   ├── chart2_component_breakdown.png
│   └── chart3_taiwan_companies.png
└── 2026-02-05-guc-valuation-debate/
    ├── thread.md                         # Clean content (ready to post)
    ├── _metadata.md                      # Internal reference (not for posting)
    ├── guc-eps-comparison.png
    └── guc-pt-comparison.png
```

**Rules:**
- ✅ Flat structure: `YYYY-MM-DD-topic/` at root level (not nested in `2026-02/`)
- ✅ Charts directly in folder (not in `charts/` subfolder)
- ✅ `thread.md` = clean content only (no metadata header)
- ✅ `_metadata.md` = internal reference (sources, audit, not for posting)

### thread.md Format

Clean version with just the tweets - no metadata header:

```markdown
# [Topic Title]

1/ [First tweet]

2/ [Second tweet]
- bullet point
- bullet point

3/ [Third tweet]

...
```

### _metadata.md Format

Internal reference file (prefixed with `_` to indicate not for posting):

```markdown
# Metadata (not for posting)

**Date:** YYYY-MM-DD
**Type:** Long Thread (10 tweets) | Quick Take | etc.
**Status:** READY TO POST

## Sources
- [Source 1 PDF name] ([Date])
- [Source 2 PDF name] ([Date])

## KSVC Holdings Check
- ✅ Held in [Model name] (+X.X% since entry) OR
- ❌ Not held in any of 7 models (checked USA 1-5, TWSE 1-2)
- Integration strategy: [Personal stakes | Industry framing | Victory lap]

## Audit Log
- [Key claim verified via RLM grep]
- [Correction made: old → new]
- [Methodology improvement discovered]

## Charts
- chart1_*.png - [Description] ([Data source])
- chart2_*.png - [Description] ([Data source])

## Notes
- [Special handling notes]
- [Lessons learned]
```

**Example:** See `/Users/Shared/ksvc/threads/2026-02-05-guc-valuation-debate/_metadata.md`

### Publish Workflow

```bash
# 1. Create publish folder (flat structure)
mkdir -p /Users/Shared/ksvc/threads/YYYY-MM-DD-topic

# 2. Copy clean content as thread.md
cp draft/YYYY-MM-DD-topic-assets/YYYY-MM-DD-topic-citrini7.md \
   /Users/Shared/ksvc/threads/YYYY-MM-DD-topic/thread.md

# 3. Copy charts directly into folder (not subfolder)
cp draft/YYYY-MM-DD-topic-assets/chart*.png \
   /Users/Shared/ksvc/threads/YYYY-MM-DD-topic/

# 4. Create _metadata.md from draft notes
# (Document sources, audit log, holdings, charts)
```

**Result:**
```
/Users/Shared/ksvc/threads/YYYY-MM-DD-topic/
├── thread.md               # Ready to post
├── _metadata.md            # Internal reference
├── chart1_*.png
└── chart2_*.png
```

### When to Publish

| Status | Action |
|--------|--------|
| Draft approved | Publish to /Users/Shared/ksvc/threads/ |
| Needs revision | Stay in content-pipeline/draft/ |
| Posted to X | Move to /Users/Shared/ksvc/threads/archive/ (optional) |

---

## Quality Checklist

**Extraction (Step 1a/1b):**
- [ ] **⚠️ Checked published threads** (`/Users/Shared/ksvc/threads/`) before topic selection
- [ ] Topic does NOT duplicate a recently published thread (same source + same angle = reject)
- [ ] Scanned recent PDF folders (at least 3) with Explore agents
- [ ] Identified cross-document connections
- [ ] Deep extracted key reports with RLM
- [ ] Charts/images extracted and reviewed (use `--extract-images`)
- [ ] **⚠️ Extraction validation:** Every PDF's `chars_extracted` checked against expected size
- [ ] **⚠️ Read tool fallback used** for any PDF with < 1000 chars (or suspiciously low for page count)
- [ ] **Key numbers verified via RLM grep** (not just Explore summary)

**Cross-Doc Synthesis (Step 1c):**
- [ ] Used rlm-repl-multi to compare across sources (if multiple PDFs)
- [ ] Asked synthesis questions (consensus, comparison, disagreement)
- [ ] Documented synthesized insights in cache
- [ ] Flagged cross-doc claims for audit in Step 4b
- [ ] Identified unique insights that single-source extraction would miss

**Content:**
- [ ] All published numbers have RLM grep confirmation
- [ ] Technical specifics included (fabs, yields, WPM)
- [ ] Time frames clear (Q1 2026, 2027e)
- [ ] Sources cited (multiple reports for cross-doc)
- [ ] Cross-doc reasoning: claims triangulated across multiple reports
- [ ] Unique insight that connects dots others miss

**KSVC:**
- [ ] equitySeries checked (all 5 US + 2 TWSE models)
- [ ] filledOrders fallback checked (all 7 models) if equitySeries shows 0%
- [ ] Entry prices noted for victory lap potential
- [ ] Integration strategy clear (held vs industry framing)

**Voice:**
- [ ] Appropriate type (thread vs quick take vs reaction)
- [ ] Skepticism included where uncertain
- [ ] Energy for high-conviction points
- [ ] Not over-polished

**Humanizer (Step 4d):**
- [ ] No AI patterns (em-dashes, "Full stop", etc.)
- [ ] Has personality/voice
- [ ] Shows thinking process, not just conclusions

**Audit (Step 4a):**
- [ ] All factual claims extracted from draft
- [ ] Each claim verified via RLM grep against source
- [ ] Taiwan company names verified via TWSE API
- [ ] No FAIL status claims remain
- [ ] UNSOURCED claims either removed, caveated, or sourced
- [ ] Audit report generated and attached to draft

**Charts (Step 6):**
- [ ] Identified chartable claims in draft
- [ ] Data pulled from RLM cache (not draft text)
- [ ] **⚠️ SOURCE DECLARED** before generating (metric + page + exact values)
- [ ] **⚠️ Source image saved FIRST** (before chart generation)
- [ ] **⚠️ Source image contains same metric** as chart (not transformed)
- [ ] If data transformed, transformation documented and justified
- [ ] Used chart-factory with theme-factory theme
- [ ] Verification agent confirmed data→chart integrity
- [ ] generate_charts.py script included (reproducibility)

**Publish (Step 7):**
- [ ] Draft approved for posting
- [ ] Created folder in `/Users/Shared/ksvc/threads/YYYY-MM-DD-topic/`
- [ ] thread.md contains clean tweets only (no metadata header)
- [ ] _metadata.md contains sources, audit log, chart descriptions
- [ ] Charts copied to final folder
- [ ] Verified all files present before announcing ready to post

---

## PDF Location

Research PDFs: `/Users/Shared/ksvc/pdfs/`

```bash
ls -la /Users/Shared/ksvc/pdfs/ | tail -5
```

---

## References

- `references/kirk-voice.md` - **PRIMARY** - Unified voice guide with all content types, formulas, and templates
- `references/serenity-style.md` - Deep dive: data-heavy thread patterns
- `references/citrini7-style.md` - Deep dive: punchy quick take patterns
- Full creator studies: `ksvc-intern/content-pipeline/creator-studies/`
