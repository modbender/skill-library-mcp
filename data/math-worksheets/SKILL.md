---
name: math-worksheets
description: Generate professional math practice worksheets and full answer keys as PDFs. Compiles LaTeX to PDF using tectonic (free, no account needed). Supports any math topic from elementary through high school (Pre-Algebra, Algebra 1/2, Geometry, Pre-Calc). Handles coordinate plane grids, geometric figures, tables, and multi-part problems. Use when a user asks for a math worksheet, practice problems, homework help sheet, or answer key for any K-12 math topic.
---

# Math Worksheet Generator

Generate a student worksheet PDF + full step-by-step answer key PDF for any K-12 math topic. Compiles LaTeX with `tectonic` (no TeX installation required — it auto-downloads packages).

## Model Selection (Automatic)

This skill auto-detects the best available reasoning model and uses it for problem generation. Reasoning models (o1, o3, DeepSeek R1, Gemini DeepThink) work through math step-by-step and make significantly fewer errors than standard models.

Model rankings are kept fresh via a three-layer fallback:
1. **Hosted JSON** (fetched from GitHub, 7-day cache) — updated by maintainers as models ship
2. **Bundled JSON** (`references/model-rankings.json`) — updated with each skill release on ClawhHub
3. **Hardcoded defaults** in the script — last-resort, never stale enough to cause failures

To update rankings without waiting for a skill release: edit the hosted JSON at the GitHub URL in `references/model-rankings.md`. The skill picks it up within 7 days.

**Step 0 — run model detection before anything else:**

```bash
SKILL_DIR="$(dirname "$0")"
result=$(bash "$SKILL_DIR/scripts/check_reasoning_model.sh")
status=$(echo "$result" | awk '{print $1}')   # FOUND, FALLBACK, or NONE
model_alias=$(echo "$result" | awk '{print $2}')
model_full=$(echo "$result" | awk '{print $3}')
```

Then branch on the status:

**`FOUND_REASONING`** (o3, o1, DeepThink, DeepSeek R1) — best case, use for problem generation:
```
sessions_spawn(task="<problem generation prompt>", model=model_alias)
```
No warning needed. Sub-agent writes the .tex files + verify script, announces completion.

**`FOUND_STRONG`** (Claude Opus) — excellent quality, use it without alarming the user:
```
sessions_spawn(task="<generation prompt>", model=model_alias)
```
Optionally add a quiet note: *"Using Opus — solid math accuracy and excellent LaTeX. For the hardest Algebra 2 problems, a reasoning model (DeepThink/o1) would be marginally better."*

**`NONE`** — standard model only; proceed but surface a clear recommendation:
```
⚠️ No reasoning model or Opus detected. Worksheet generated with [current model].
For best accuracy, especially on multi-step problems, configure one of:
  • Gemini 2.5 Pro DeepThink  — google.generativeai.com (free tier available)
  • o1 / o3                   — platform.openai.com
  • DeepSeek R1               — platform.deepseek.com (very affordable)
  • Claude Opus               — console.anthropic.com
SymPy verification will catch most errors regardless.
```

| Status | Model examples | Action |
|---|---|---|
| `FOUND_REASONING` | DeepThink, o1, o3, R1 | Spawn silently, no warning |
| `FOUND_STRONG` | Claude Opus 4.x | Spawn silently, optional quiet note |
| `NONE` | Sonnet, Flash, GPT-4o | Use current model + show recommendation |

## Prerequisites

```bash
brew install tectonic   # macOS/Linux — downloads packages on demand
```

Output directory (create if needed): `~/Documents/Worksheets/`

## Workflow

### 1. Gather requirements

Ask (or infer from context):
- **Student**: name, grade, course (e.g. "8th grade, Pre-Algebra")
- **Topic**: e.g. "factoring trinomials", "solving two-step equations"
- **Problem count**: default 10 if not specified
- **Format preference**: timed quiz, homework practice, mixed difficulty, or topic drill

**Photo input shortcut**: If the user sends a photo of homework or a textbook page, use the `image` tool to extract problem types, format, and difficulty — then mirror that style exactly.

### 2. Design problems

Design problems appropriate to the student's level. Increase difficulty gradually across the set. Every problem must be mathematically correct — verify your own solutions.

See `references/problem-library.md` for topic-specific problem type menus.

### 3. Write LaTeX source

Write **three** `.tex` files to `/tmp/`:
- `ws_TOPIC_DATE.tex` — student worksheet (blank work areas)
- `ak_TOPIC_DATE.tex` — answer key (full step-by-step solutions)
- `ss_TOPIC_DATE.tex` — skills summary / study guide (cheat sheet)

The **skills summary** is a 1–2 page reference card the student can use while working through the worksheet or when studying. It contains:
- One section per distinct skill tested (2–5 sections typical)
- A **formula/rule box** (blue) per skill — the key facts and formulas
- A **mini worked example** (green) per skill — brief pattern demonstration, simpler than worksheet problems
- An optional **watch-out box** (orange) — common mistakes worth flagging
- Optional **key vocabulary** section at the bottom

See `references/latex-templates.md` → "Skills Summary / Study Guide Template" for the full shell and box macros.

See `references/latex-templates.md` for document templates, coordinate planes, tables, geometric figures, and answer key patterns.

**Required packages** (include in every document):
```latex
\usepackage[margin=1in, top=0.75in, bottom=0.75in]{geometry}
\usepackage{amsmath, amssymb}
\usepackage{tikz, pgfplots}
\usepackage{enumitem, fancyhdr, multicol, array, booktabs}
\pgfplotsset{compat=1.18}
```

**Work space defaults**: `\vspace{5cm}` per problem; `8cm` for multi-step; `10cm+` for graphs.

### 4. Write and run the verification file

Before compiling, write `/tmp/verify_TOPIC_DATE.json` — a structured data file describing each problem and its expected answer. The bundled `scripts/verify.py` evaluates this using SymPy. No generated code is ever executed.

```bash
bash "$SKILL_DIR/scripts/run_verify.sh" /tmp/verify_TOPIC_DATE.json
```

**JSON format:**
```json
{
  "topic": "graphing polynomials",
  "problems": [
    {"id": 1, "type": "solve",  "expr": "x**2 - 5*x + 6",      "expected": [2, 3]},
    {"id": 2, "type": "factor", "expr": "x**2 - 7*x + 12",     "expected": "(x-3)*(x-4)"},
    {"id": 3, "type": "eval",   "expr": "(x-1)*(x+2)", "at": {"x": 0}, "expected": -2},
    {"id": 4, "type": "zeros",  "expr": "x*(x-3)**2",           "expected": [0, 3]},
    {"id": 5, "type": "expand", "expr": "(x+2)**2",             "expected": "x**2 + 4*x + 4"},
    {"id": 6, "type": "manual", "desc": "Graph sketch — verify visually"}
  ]
}
```

**Type reference:**

| Type | Verifiable? | What it checks |
|---|---|---|
| `solve` | ✅ | Roots of expr=0 match expected list |
| `factor` | ✅ | Factored form matches expected |
| `expand` | ✅ | Expanded form matches expected |
| `eval` | ✅ | expr evaluated at given values matches expected |
| `zeros` | ✅ | Zeros of expr match expected list |
| `manual` | 👁 | Flagged for human review — never fails automatically |

Use `manual` for: graph sketches, sign charts, word problem setups, proofs.

**If verification fails (exit 1):** fix the LaTeX answer key and re-run. Do not compile until the answer key is correct.

### 5. Compile

```bash
SKILL_DIR="$(dirname "$0")"
bash "$SKILL_DIR/scripts/compile.sh" /tmp/ws_TOPIC_DATE.tex ~/Documents/Worksheets/
bash "$SKILL_DIR/scripts/compile.sh" /tmp/ak_TOPIC_DATE.tex ~/Documents/Worksheets/
bash "$SKILL_DIR/scripts/compile.sh" /tmp/ss_TOPIC_DATE.tex ~/Documents/Worksheets/
```

### 5. Deliver

Send all three PDFs via the same channel the request came from:
- **Telegram** → `message` tool with `filePath` (copy to `~/.openclaw/media/outbound/` first)
- **iMessage/SMS** → `imsg` skill
- **Email** → `gog` skill (send all three as attachments)

Suggested send order: skills summary first (study guide), then worksheet, then answer key.

**Printing**: Do NOT print unless explicitly asked. If asked, print worksheet + skills summary (not answer key, unless requested). Use `lpr -P <printer_name>`.

## Quality Checklist

Before compiling, verify each problem:
- [ ] Mathematically correct (you checked the solution)
- [ ] Unambiguous problem statement
- [ ] Appropriate difficulty for the student's level
- [ ] Sufficient work space
- [ ] Diagrams/graphs/tables included where needed
- [ ] Problems vary across the set (not all the same sub-type)

## File Naming

```
ws_algebra2_factoring_2026-02-22.pdf   ← worksheet
ak_algebra2_factoring_2026-02-22.pdf   ← answer key
ss_algebra2_factoring_2026-02-22.pdf   ← skills summary / study guide
```

Prefix with student name when known: `leo_ws_...`, `leo_ak_...`, `leo_ss_...`

## Troubleshooting

| Problem | Fix |
|---|---|
| `tectonic` not found | `brew install tectonic` |
| Slow first compile | Downloading packages from CTAN — wait 30–60s, faster after |
| LaTeX error on line N | Check paired `$...$`, matching `\begin{}/\end{}` |
| pgfplots not rendering | Ensure `\pgfplotsset{compat=1.18}` is in preamble |
| PDF not created | Read full tectonic output for the specific error |
