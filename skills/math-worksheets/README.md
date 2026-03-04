# math-worksheets — OpenClaw Skill

**v2.0.0** · [Changelog](#changelog)

Generate professional math practice worksheets, answer keys, and study guides for K-12 students. Three PDFs every time: worksheet → answer key → skills summary cheat sheet.

## Features

- **Three documents per request** — worksheet, step-by-step answer key, skills summary with formula boxes and mini examples
- **LaTeX quality** — coordinate planes, geometric figures, tables, multi-part problems via tectonic (no TeX installation required)
- **SymPy verification** — answers are verified with a computer algebra system before compiling; incorrect answers are caught before reaching students
- **Auto reasoning-model detection** — automatically uses the best available model (DeepThink, o1/o3, DeepSeek R1, Claude Opus) for math generation; shows setup guidance if none configured. All detection is local — no network calls.
- **Channel mirroring** — sends back via the same channel the request came from (Telegram, iMessage, email)
- **K-12 coverage** — Pre-Algebra through Pre-Calculus (see `references/problem-library.md` for full topic menu)

## Install

```bash
openclaw skills install math-worksheets
```

Or download `math-worksheets.skill` from [ClawhHub](https://clawhub.com) and install locally.

**Prerequisites:**
```bash
brew install tectonic   # LaTeX compiler — auto-downloads packages on first use
```

**Python 3** is also required (standard on macOS). The skill uses it for model detection and answer verification.

**sympy** is required for answer verification:
```bash
pip3 install sympy
```

## Usage

Just ask naturally:

> *"Make Lucy a 20-problem worksheet on exponents and roots"*
> *"Leo needs practice on graphing polynomials — use his homework photo as a guide"*
> *"Factoring trinomials worksheet for an 8th grader, 15 problems"*

The skill handles everything: model selection, problem generation, SymPy verification, compile, and delivery.

## Skill Contents

```
math-worksheets/
├── SKILL.md                          ← workflow and instructions
├── scripts/
│   ├── check_reasoning_model.sh     ← auto-detects best available model (local only)
│   ├── compile.sh                   ← tectonic PDF compiler wrapper
│   ├── run_verify.sh                ← gates compilation on SymPy pass
│   └── verify.py                   ← SymPy verification template
└── references/
    ├── latex-templates.md           ← LaTeX patterns (coordinate planes, figures, answer key)
    ├── problem-library.md           ← K-12 problem type menu by course
    ├── model-rankings.md            ← human-readable model guidance
    └── model-rankings.json          ← bundled model ranking reference
```

## Changelog

### v2.0.0 — 2026-02-23
- **Security:** Eliminated RCE surface — verification no longer generates or executes AI-written Python code. The AI now writes a structured JSON data file (`verify_TOPIC_DATE.json`); the fixed, auditable `scripts/verify.py` evaluates it using SymPy. No user input is ever executed as code.
- **Security:** Removed `fetch_model_config.sh` — skill no longer makes any network requests at runtime
- **Security:** Removed auto-`pip install` from `run_verify.sh`; sympy must be installed as a prerequisite (`pip3 install sympy`)
- **Security:** `check_reasoning_model.sh` is now fully local; reads OpenClaw config optionally with graceful fallback to bundled defaults
- `references/model-rankings.json` remains bundled as a static reference

### v1.0.0 — 2026-02-22
- Initial release
- Three documents per request: worksheet, answer key, skills summary
- SymPy verification gate (exit 0/1/2)
- Auto reasoning-model detection
- LaTeX compilation via tectonic
- Channel-matched delivery (Telegram, iMessage)

## License

MIT
