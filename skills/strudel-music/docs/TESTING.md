# Testing Strategy

Release path: **private fork (strudel-music-dev)** → **public repo** → **ClawHub publish**.

Each stage gates the next. Don't skip ahead.

## Stage 1: Private Fork RC

Run in `strudel-music-dev` before anything goes public.

**Full pipeline test:**
```bash
npm run setup
npm test                    # 12-point smoke test
npm run test:render         # render fog-and-starlight to WAV
bash scripts/dispatch.sh render assets/compositions/combat-assault.js 16 140
```

**Render quality checks:**
- No silence in output (detect with `ffmpeg -af silencedetect`)
- Loudness within range (`ffmpeg -af loudnorm=print_format=json` — target -14 to -18 LUFS)
- No clipping (peak should stay below 0 dBFS)
- Stereo field populated (not mono-summed by accident)

```bash
# Quick quality check
ffmpeg -i output.mp3 -af "loudnorm=print_format=json" -f null - 2>&1 | grep -A5 "input_"
ffmpeg -i output.mp3 -af silencedetect=noise=-40dB:d=2 -f null - 2>&1 | grep silence
```

**Naive install test:**
```bash
# Fresh directory, zero prior state
cd $(mktemp -d)
git clone <repo-url> strudel-music
cd strudel-music
npm run setup
npm test
npm run test:render
```

This catches missing files, hardcoded paths, and undeclared dependencies.

## Stage 2: Cross-Platform Validation

The renderer is pure JS. Demucs is Python. They have different platform requirements.

### Test matrix

| Test | x86_64 Linux | ARM64 Linux | Notes |
|------|:---:|:---:|-------|
| `npm install` | ✅ | ✅ | No native compilation needed |
| `npm test` | ✅ | ✅ | Renders a test composition |
| `npm run test:render` | ✅ | ✅ | Full WAV output |
| Full pipeline (Demucs) | ✅ | ✅ | Requires Python deps |
| Naive install | ✅ | ✅ | Clean env, zero prior state |

### Hosts

- **x86_64**: Silas (WSL2/urudyne) or Elliott (bare metal Ubuntu)
- **ARM64**: Cael (DGX Spark)

### What to validate

**JS-only path (composition + render):**
- Works without Python installed at all
- `node-web-audio-api` loads correctly (Rust native addon — prebuilt for both arches)
- Sample loading from `samples/` resolves paths correctly
- Output WAV is valid and non-empty

**Full pipeline (with Demucs):**
- Demucs runs and produces 4 stems
- Analysis scripts handle edge cases (silent stems, very short tracks)
- Graceful failure when Python deps are missing:
  ```
  ⚠️ Demucs not available (Python deps missing). Composition and rendering still work.
  Install: pip install demucs librosa numpy scipy scikit-learn torch
  ```
  Not a crash. Not a stack trace. A message the user can act on.

**ARM64 specifics:**
- PyTorch ARM64 wheel availability (torch has official aarch64 builds)
- `node-web-audio-api` prebuilt binary for aarch64 (verify in `node_modules`)
- Memory usage stays reasonable on 128GB unified memory (not a concern, but verify)

## Stage 3: Public Repo Merge

PR from dev branch to main. Checklist:

- [ ] All smoke tests pass on x86_64
- [ ] All smoke tests pass on ARM64
- [ ] Naive install succeeds on both platforms
- [ ] `docs/pipeline.md` complete
- [ ] `docs/TESTING.md` complete (this file)
- [ ] `docs/composition-guide.md` complete
- [ ] README links to all docs
- [ ] No hardcoded paths (check for `/home/figs`, absolute paths)
- [ ] `.gitignore` covers output/, samples/ (downloaded on demand), node_modules/
- [ ] Sample packs either bundled or downloadable via `npm run setup`
- [ ] License file present and correct

## Stage 4: ClawHub Publish

Final step. The skill goes live on clawhub.com.

**Pre-publish checklist:**

- [ ] Version bump in `package.json` (semver — if breaking changes since last publish, major bump)
- [ ] `SKILL.md` complete:
  - Frontmatter metadata (name, version, description, author)
  - `user-invocable: true` if `/strudel` slash command is ready
  - Inline JSON metadata block
- [ ] All tests pass on a **fresh OpenClaw instance** (not your dev machine):
  ```bash
  # Simulate fresh install
  clawhub install strudel-music
  cd ~/.openclaw/skills/strudel-music
  npm run setup
  npm test
  ```
- [ ] No secrets in repo (grep for tokens, API keys, .env files)
- [ ] `npm run setup` is idempotent (running twice doesn't break anything)

**Publish:**
```bash
clawhub publish
```

## Quality Gates

Each gate must pass before proceeding:

| Gate | Criteria | Blocks |
|------|----------|--------|
| Smoke | `npm test` passes (12 checks) | Everything |
| Render | `npm run test:render` produces valid WAV | Stage 2+ |
| Naive | Clean `git clone` → `npm run setup` → `npm test` works | Stage 3+ |
| Cross-platform | Both x86_64 and ARM64 pass smoke + render | Stage 3+ |
| Publish | Fresh OpenClaw install + test works | Stage 4 |

## Running Tests

```bash
# Quick (30s)
npm test

# Full render (2-3 min)
npm run test:render

# Naive install simulation
cd $(mktemp -d) && git clone <url> . && npm run setup && npm test

# Quality check on rendered output
ffmpeg -i output.mp3 -af "loudnorm=print_format=json" -f null - 2>&1 | grep input_i
```
