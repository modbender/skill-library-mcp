# Fork → Public Promotion Workflow

How to promote work from the private fork (`strudel-music-dev`) to the public repo (`strudel-music`) and publish to ClawHub.

---

## 1. Pre-Promotion Checklist (Private Fork)

Before any code leaves the private fork, verify:

- [ ] All WO-RELEASE issues resolved (`strudel-music-dev` #7–#11)
- [ ] Cross-platform test: **x86_64 + ARM64** both pass full pipeline end-to-end
- [ ] Loudness validation on all test renders (target: −14 LUFS integrated, −1 dBTP ceiling)
- [ ] SKILL.md complete with:
  - Session safety warning (Strudel eval context)
  - Legal disclaimer (sample ownership, fair use)
  - Onboarding section or link to `docs/ONBOARDING.md`
- [ ] No hardcoded paths, private keys, or personal data in any committed file
- [ ] `npm pack` produces a clean tarball (no extraneous files)
- [ ] README has working examples, links to docs
- [ ] `.gitignore` reviewed — no secrets, no build artifacts leaking through

---

## 2. Issue Mirroring Protocol

Private and public repos maintain separate issue trackers. The protocol:

1. **Draft issues in the private fork first** — this is where iteration happens (e.g., `strudel-music-dev` #7–#11)
2. **When ready to promote**: open matching issues in the **public** repo (`strudel-music`)
   - Copy the title and a cleaned-up description
   - Reference the private issue number in the body for internal traceability
3. **Note the public issue numbers** — these become the canonical references
4. **Merge PRs in the public repo** that reference the public issue numbers
5. **Result**: public repo has a clean issue/PR history with linked closures

> **Why mirror?** The private fork may contain WIP notes, dead ends, and internal discussion that shouldn't be in the public record. Mirroring gives us a clean public trail while preserving the messy reality privately.

---

## 3. Promotion Steps

### 3a. Prepare the public repo

```bash
# Ensure public main is up to date
cd strudel-music
git checkout main
git pull origin main
```

### 3b. Create a feature branch with the promoted work

```bash
git checkout -b feat/bloom-pipeline  # or whatever the feature is
# Cherry-pick, merge, or copy changes from the private fork
# Ensure the commit history is clean
```

### 3c. Open a PR

- **Target**: `main` on the public repo
- **PR description** references all public issue numbers being resolved:
  ```
  Closes #1, closes #2, closes #3
  ```
- Include a summary of what's new, any breaking changes, and testing done

### 3d. Review

- **Three-prince review** (all three agents review independently), or **2-of-3 minimum** for smaller changes
- Each reviewer checks:
  - Code correctness
  - No secrets/personal data
  - Compositions render correctly
  - Documentation matches implementation

### 3e. Merge and tag

```bash
# After approval, merge to main
git checkout main
git merge --no-ff feat/bloom-pipeline
git tag -a v0.3.0 -m "Bloom pipeline + cross-platform validation"
git push origin main --tags
```

---

## 4. ClawHub Publish Checklist

### Pre-publish

```bash
# Already authed as @karmafeast
clawhub login

# Dry run first — always
clawhub publish --dry-run
```

Verify:
- [ ] SKILL.md metadata renders correctly in dry-run output
- [ ] No private or sensitive content in the package
- [ ] Version number is correct
- [ ] All required files are included

### Publish

```bash
clawhub publish
```

### Post-publish verification

- [ ] Check listing at [clawhub.com](https://clawhub.com)
- [ ] Verify skill installs cleanly: `clawhub install <skill-name>`
- [ ] Spot-check that a fresh install can run the pipeline end-to-end

---

## 5. Post-Publish

- [ ] Close all matched public issues with references to the merge commit
- [ ] Update `MEMORY.md` with publish milestone (date, version, what shipped)
- [ ] Announce in **#sprites-of-thornfield** — include version, key features, any known limitations
- [ ] Archive the corresponding private fork issues (close with "promoted to public" note)

---

## Version Numbering

| Version | Meaning |
|---------|---------|
| v0.1.x  | Suo Gân — initial pipeline proof |
| v0.2.x  | Frisson — multi-track, loudness fixes |
| v0.3.x  | Bloom — full decomposition, cross-platform |
| v1.0.0  | Public release — ClawHub-published, docs complete |

---

## Quick Reference

```
Private fork (strudel-music-dev)
  └── iterate, test, break things
  └── issues #7-#11 (WO-RELEASE)
        │
        ▼  (mirror issues)
Public repo (strudel-music)
  └── clean PRs referencing public issues
  └── merge → tag → clawhub publish
        │
        ▼
ClawHub (clawhub.com)
  └── published skill, installable by anyone
```
