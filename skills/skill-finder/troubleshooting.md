# Troubleshooting — Skill Finder

Reference for handling edge cases and common problems.

## No Results Found

**First:** Try alternative search terms (see `search.md` for expansion strategies).

**If still nothing:**

1. **Acknowledge honestly**
   > "I searched for skills related to [X] but didn't find any matches."

2. **Offer direct help**
   > "I can help you with this directly using my general capabilities."

3. **Suggest creation (for recurring needs)**
   > "If this is something you do often, you could create a custom skill with `skill-builder`."

## Too Many Results

**Problem:** Search returns 10+ skills, hard to choose.

**Solution:**
1. Apply quality filters (see `evaluate.md`)
2. Check user's memory for preferences
3. Present only top 3 with clear differentiation
4. Ask clarifying question if still unclear

> "Found several options. To narrow down:
> - Need basic features or comprehensive?
> - Prefer popular/stable or cutting-edge?"

## Skill is Flagged as Suspicious

**What it means:** VirusTotal Code Insight detected potentially risky patterns (API calls, file access, etc.).

**How to handle:**

1. **Inform user**
   > "This skill is flagged as suspicious by the security scanner. It may make external API calls or access files."

2. **Check what triggered it**
   ```bash
   clawhub inspect <slug> --files
   ```

3. **Default to safer alternatives**
   > "I can recommend similar skills that are not flagged, then we pick the best match."

4. **Do not bypass scanner warnings**
   - Never use force-install options
   - Prefer normal installation only for non-flagged options with explicit user consent

## Skill Not Found (404)

**Possible causes:**
- Typo in slug
- Skill was deleted/hidden
- Author changed the name

**Solutions:**
1. Search by description instead of exact name
2. Check for similar names: `clawhub search "partial-name"`
3. The skill may have been replaced — search the domain

## Conflicting Skills

**Problem:** User wants a skill that overlaps with one already installed.

**Detection:** Check `clawhub list` for existing skills in same domain.

**Resolution:**
1. **Explain the overlap**
   > "You have `git` installed. The `github` skill adds PR/issue features on top of it — they work together."

2. **Or warn about conflict**
   > "You have `eslint-basic` installed. `eslint-pro` covers the same but more — want to replace?"

## User Changed Their Mind

**After installation:**
- Uninstall: `clawhub update` then remove from skills folder
- Don't reinstall: Add to Passed in memory.md with reason

**During recommendation:**
- Just move on, no need to store unless they explain why

## Outdated Skill

**Signs:**
- Last update >6 months ago
- Low recent downloads
- References old versions of tools

**How to handle:**
> "This skill was last updated [X months] ago. It references [old version]. Want to try anyway, or should I look for alternatives?"

## Memory Issues

**Memory file corrupted or malformed:**
1. Backup: `cp ~/skill-finder/memory.md ~/skill-finder/memory.md.bak`
2. Recreate from `memory-template.md`
3. Ask user to re-state key preferences

**Memory too large (>50 lines):**
1. Archive old entries
2. Keep only recent Liked/Passed
3. Preserve all Preferences (they're stable)
