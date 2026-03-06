# Pre-Release Testing Checklist

Testing strategy for moving the private fork RC to public repo and ClawHub publish.

> **📖 See also:** [Pipeline Guide](./pipeline-guide.md) for full pipeline documentation.

---

## Audio Quality

- [ ] **All compositions render without errors** — Every `.js` file in `assets/compositions/` and `src/compositions/` produces a valid WAV via `node src/runtime/chunked-render.mjs`
- [ ] **No silence gaps >2s** — Except designed endings/outros. Verify with RMS windowed analysis or manual listening pass
- [ ] **Loudness within -16 to -14 LUFS** — Check with `ffmpeg -i output.wav -af loudnorm=print_format=json -f null -`
- [ ] **True peak below -1 dBTP** — No clipping. Check with `ffmpeg -i output.wav -af astats=measure_overall=Peak_level -f null -`
- [ ] **No DC offset or low-frequency rumble** — High-pass at 20Hz if needed before final render

## Runtime Stability

- [ ] **No `ended` event listener leaks** — After rendering 1000+ haps, check heap: `node --expose-gc --max-old-space-size=512` and verify no unbounded growth. Known risk area: `AudioBufferSourceNode.onended` callbacks
- [ ] **Chunked renderer handles edge cases** — Test with: 1 cycle, 100 cycles, empty pattern, pattern with only rests
- [ ] **No unhandled promise rejections** — Run full render suite with `--unhandled-rejections=throw`
- [ ] **Clean exit** — Process exits with code 0 after render completes (no dangling timers or open handles)

## Sample Integrity

- [ ] **Pitched sample maps validate** — `strudel.json` present in each sample directory, and every referenced WAV path exists
- [ ] **All WAVs are valid PCM** — No truncated files, correct headers. Quick check: `soxi samples/**/*.wav 2>&1 | grep -i error`
- [ ] **Sample rate consistency** — All WAVs at 44100Hz stereo. Mixed rates cause pitch/timing drift
- [ ] **No empty samples** — Every WAV has >0.1s of non-silent audio (unless it's a hallucinated stem that should have been pruned)

## Output Compatibility

- [ ] **MP3 playable in browser** — Test in Chrome, Firefox, Safari (AAC fallback if MP3 fails on Safari)
- [ ] **MP3 playable in Discord** — Upload as attachment, verify inline player works
- [ ] **MP3 playable in standard players** — VLC, mpv, QuickTime, Windows Media Player
- [ ] **WAV intermediate is valid** — Correct RIFF headers, no corruption from chunk concatenation
- [ ] **ffmpeg conversion succeeds** — `ffmpeg -i output.wav -c:a libmp3lame -q:a 2 output.mp3` exits 0

## Documentation

- [ ] **README.md links to pipeline-guide.md** — Pipeline section present with working relative link
- [ ] **Pipeline guide is accurate** — Stage descriptions match current code; timings are realistic
- [ ] **Composition guide present** — Mini-notation footguns documented (e.g., `clip(1)` for sample playback, `setcpm()` vs `cps()` confusion)
- [ ] **SKILL.md is current** — Slash command descriptions match actual behavior
- [ ] **No stale references** — No mentions of deprecated browser renderer, removed compositions, or old file paths

## Security & Privacy

- [ ] **License headers on all source files** — MIT header in `.js` and `.mjs` files
- [ ] **No private paths in committed files** — No `/home/figs/`, `/Users/`, `C:\Users\` hardcoded anywhere. Search: `grep -rn '/home/\|/Users/\|C:\\Users' --include='*.js' --include='*.mjs' --include='*.sh' --include='*.md'`
- [ ] **No API keys or tokens** — Search: `grep -rn 'sk-\|token\|secret\|password\|DISCORD_BOT_TOKEN=' --include='*.js' --include='*.mjs' --include='*.json' --include='*.env'`
- [ ] **No personal data** — No email addresses (except git commit metadata), real names, or private URLs in source files
- [ ] **`.gitignore` covers sensitive paths** — `samples/` (large binaries), `.env`, `node_modules/`, output WAVs/MP3s
- [ ] **Security notes in SKILL.md** — Pattern execution warning present (compositions are evaluated JS)

## Packaging

- [ ] **`npm pack` produces clean tarball** — Run `npm pack --dry-run` and verify only intended files are included
- [ ] **No `node_modules/` in tarball** — Check with `tar tzf strudel-music-*.tgz | grep node_modules` (should be empty)
- [ ] **`package.json` metadata correct** — name, version, description, repository, license fields
- [ ] **`npm install` from clean state works** — Delete `node_modules/`, run `npm install`, then `npm test`
- [ ] **`npm run setup` is idempotent** — Running it twice doesn't break anything or re-download samples

## ClawHub Publishing

- [ ] **ClawHub publish dry-run succeeds** — Verify the skill registers correctly with OpenClaw's skill system
- [ ] **Skill metadata validates** — `SKILL.md` front matter parses without errors
- [ ] **Install hooks work** — `npm install && bash scripts/download-samples.sh` completes on a fresh system
- [ ] **No missing dependencies** — All `require()`/`import` paths resolve after fresh install
- [ ] **Skill installs on target platforms** — At minimum, test on the publishing host

## Cross-Platform

- [ ] **ARM64 (DGX Spark)** — Full pipeline: Demucs + analysis + render + MP3
- [ ] **x86_64 + NVIDIA (Silas)** — Full pipeline with GPU-accelerated Demucs
- [ ] **x86_64 + Intel (Elliott)** — Full pipeline CPU-only
- [ ] **At least 2 of 3 pass** — Fleet coverage minimum before publish

> **Note:** Cross-platform testing should use `sessions_spawn` on each fleet member. See the [Pipeline Guide session management warning](./pipeline-guide.md#-critical-session-management) — never run inline.

---

## Test Execution

### Quick Smoke Test (5 minutes)

```bash
cd /path/to/strudel-music
npm test                  # 12-point smoke test
npm run test:render       # Render one composition to WAV
```

### Full Render Suite (30–60 minutes)

Render every composition and check output:

```bash
for comp in assets/compositions/*.js src/compositions/*.js; do
  name=$(basename "$comp" .js)
  echo "Rendering: $name"
  node src/runtime/chunked-render.mjs "$comp" "/tmp/$name.wav" 8 4 2>&1
  if [ $? -ne 0 ]; then
    echo "FAIL: $name"
  else
    # Check loudness
    ffmpeg -i "/tmp/$name.wav" -af loudnorm=print_format=json -f null - 2>&1 | grep input_i
  fi
done
```

### Pipeline End-to-End (15–20 minutes per track)

Must run via sub-agent. Provide a test MP3 and verify:
1. Demucs produces 4 stems
2. Hallucination detection correctly discards empty stems
3. BPM/key detection returns plausible values
4. Slicing produces expected number of WAV files
5. `strudel.json` is valid and complete
6. Composition renders without errors
7. Final MP3 passes loudness and true peak checks

---

## Sign-Off

| Area              | Tester | Date | Pass? |
|-------------------|--------|------|-------|
| Audio Quality     |        |      |       |
| Runtime Stability |        |      |       |
| Sample Integrity  |        |      |       |
| Output Compat     |        |      |       |
| Documentation     |        |      |       |
| Security/Privacy  |        |      |       |
| Packaging         |        |      |       |
| ClawHub Publish    |        |      |       |
| Cross-Platform    |        |      |       |
