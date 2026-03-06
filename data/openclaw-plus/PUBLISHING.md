# Publishing OpenClaw+ to ClawHub

## Quick Fix - Updated Files

✅ **SKILL.md has been updated** with the required `license` field in the YAML frontmatter.

The skill package now includes:
- ✅ Proper YAML frontmatter with `name`, `description`, and `license` fields
- ✅ manifest.json with metadata
- ✅ LICENSE.txt file
- ✅ All documentation and implementation files

## Publishing Steps

### 1. Use the `.skill` file (recommended)

Upload `openclaw-plus.skill` to ClawHub. This is a zip archive with the `.skill` extension that ClawHub recognizes.

### 2. Verify SKILL.md Format

The YAML frontmatter should look like this:
```yaml
---
name: openclaw-plus
description: A modular super-skill combining developer and web capabilities...
license: Complete terms in LICENSE.txt
---
```

### 3. Check File Structure

Your `.skill` file should contain:
```
openclaw-plus/
├── SKILL.md              (Required - with YAML frontmatter)
├── manifest.json         (Required)
├── LICENSE.txt           (Required)
├── README.md
├── CHANGELOG.md
├── QUICKSTART.md
├── REFERENCE.md
├── SUMMARY.md
├── evals/
│   ├── evals.json
│   └── files/
└── scripts/
    └── implementation.py
```

## Troubleshooting

### Issue: "SKILL.md not detected"

**Solution 1: Check YAML Frontmatter**
- Ensure YAML starts and ends with `---`
- Must have `name`, `description`, and `license` fields
- No extra spaces or formatting issues

**Solution 2: Check File Location**
- SKILL.md must be at `openclaw-plus/SKILL.md` (not at root)
- File name must be exactly `SKILL.md` (all caps)

**Solution 3: Use .skill Extension**
- Upload `openclaw-plus.skill` instead of `openclaw-plus.zip`
- ClawHub may prefer the `.skill` extension

### Issue: "Invalid skill format"

**Check:**
1. YAML frontmatter is valid (no syntax errors)
2. manifest.json is valid JSON
3. LICENSE.txt exists
4. All files are inside the `openclaw-plus/` directory

### Issue: "Missing required fields"

**Ensure YAML has:**
```yaml
---
name: openclaw-plus
description: [your description]
license: Complete terms in LICENSE.txt
---
```

### Issue: Upload fails

**Try:**
1. Use the `.skill` file instead of `.zip`
2. Check file size (should be ~60KB compressed)
3. Verify the zip structure with: `unzip -l openclaw-plus.skill`
4. Re-download the file and try again

## Validation Commands

Before uploading, verify the package:

```bash
# Check the file type
file openclaw-plus.skill
# Should output: "Zip archive data"

# List contents
unzip -l openclaw-plus.skill
# Should show openclaw-plus/SKILL.md

# Extract and verify YAML
unzip -p openclaw-plus.skill openclaw-plus/SKILL.md | head -10
# Should show the YAML frontmatter

# Verify manifest
unzip -p openclaw-plus.skill openclaw-plus/manifest.json
# Should show valid JSON
```

## What's Fixed

In this version:
- ✅ Added `license: Complete terms in LICENSE.txt` to SKILL.md frontmatter
- ✅ Created manifest.json with all required fields
- ✅ Included LICENSE.txt file
- ✅ Proper directory structure (files inside openclaw-plus/)
- ✅ Both .zip and .skill files available

## Files to Upload

Choose one:
- **openclaw-plus.skill** (recommended for ClawHub)
- **openclaw-plus.zip** (alternative, but .skill is preferred)

Both contain the exact same content, just different file extensions.

## After Publishing

Once published on ClawHub, users can install with:
```bash
openclaw install openclaw-plus
```

Or:
```bash
openclaw skill add openclaw-plus
```

## Need More Help?

If ClawHub still doesn't detect the skill:
1. Check ClawHub's documentation for required fields
2. Look at other published skills on ClawHub for examples
3. Verify your ClawHub account has publishing permissions
4. Try uploading through ClawHub's web interface vs CLI

## Contact

Author: Shindo957 (choochoocharlese@gmail.com)

---

Good luck with publishing! 🚀
