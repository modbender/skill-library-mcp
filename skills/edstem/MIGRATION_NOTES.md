# Migration Notes: v1.0.0 → v1.1.0

## For Users Upgrading from v1.0.0

### What Changed

The EdStem skill has been completely refactored to be **institution-agnostic**. It now works with any school using EdStem, not just Columbia.

### Breaking Changes

#### 1. Command-Line Interface
**Old (v1.0.0):**
```bash
python3 fetch-edstem.py 92041  # Used hardcoded course mapping
```

**New (v1.1.0):**
```bash
python3 fetch-edstem.py 92041 ./output-dir --course-name "Your Course"
```

#### 2. Output Directory
**Old:**
- Hardcoded to `/home/axel/.openclaw/workspace/school/courses/<course-dir>/edstem/`
- Required course ID to be in predefined mapping

**New:**
- Defaults to `./edstem-<course_id>` in current directory
- Can be customized via positional argument
- No predefined mappings required

#### 3. Course Mappings Removed
The `course_dirs` dictionary in the Python script has been removed:
```python
# REMOVED:
course_dirs = {
    92041: "machine-learning",
    94832: "advanced-rl",
    93717: "applied-ml"
}
```

Now pass directories explicitly or use the default.

### Migration Steps

#### For Automated Scripts

**Old script:**
```bash
#!/bin/bash
for course_id in 92041 94832 93717; do
    python3 fetch-edstem.py $course_id
done
```

**Updated script:**
```bash
#!/bin/bash
# Define course mappings in your script
declare -A courses=(
    [92041]="machine-learning"
    [94832]="advanced-rl"
    [93717]="applied-ml"
)

for course_id in "${!courses[@]}"; do
    course_name="${courses[$course_id]}"
    python3 fetch-edstem.py $course_id ~/courses/$course_name --course-name "$course_name"
done
```

#### For Direct Usage

**Option 1: Keep old directory structure**
```bash
# Replicate old behavior manually
python3 fetch-edstem.py 92041 \
    ~/.openclaw/workspace/school/courses/machine-learning/edstem \
    --course-name "Machine Learning"
```

**Option 2: Use new default structure**
```bash
# Use new defaults (simpler)
cd ~/courses/machine-learning
python3 fetch-edstem.py 92041
```

### New Features in v1.1.0

1. **Flexible output directory:**
   ```bash
   python3 fetch-edstem.py 92041 ./any/path/you/want
   ```

2. **Course name specification:**
   ```bash
   python3 fetch-edstem.py 92041 --course-name "CS229 Machine Learning"
   ```

3. **Configurable thread limit:**
   ```bash
   python3 fetch-edstem.py 92041 --limit 25  # Fetch 25 threads instead of 10
   ```

4. **Auto-detection of course name:**
   If you don't specify `--course-name`, the script fetches it from the API automatically.

5. **Better error handling:**
   Handles missing user data gracefully instead of crashing.

### Configuration Changes

#### Authentication Token

No changes to authentication. The `ED_TOKEN` is still in the same location:
- **File:** `scripts/fetch-edstem.py`
- **Line:** ~20

Update it the same way as before.

#### File Locations

**Scripts:**
- ✅ `scripts/fetch-edstem.py` (updated)
- ✅ `scripts/fetch-edstem.sh` (updated)

**Documentation:**
- ✅ `SKILL.md` (completely rewritten)
- 🆕 `README.md` (new)
- 🆕 `CHANGELOG.md` (new)
- 🆕 `VERSION` (new)

### Examples for Different Institutions

The skill now works with any EdStem institution:

```bash
# Stanford
python3 fetch-edstem.py 12345 ~/stanford/cs229

# MIT
python3 fetch-edstem.py 67890 ~/mit/6.7920

# Your school
python3 fetch-edstem.py <your_course_id> ~/path/to/course
```

### Backward Compatibility

**None.** This is a breaking change requiring updates to any automated scripts or workflows using v1.0.0.

However, the migration is straightforward:
1. Add output directory parameter
2. Add course name if desired
3. Update any hardcoded path expectations

### Testing Your Migration

After updating, test with:
```bash
# Test help
python3 fetch-edstem.py --help

# Test fetch (dry run - check what it would do)
python3 fetch-edstem.py 92041 /tmp/test-edstem --limit 1

# Verify output
ls -la /tmp/test-edstem/
```

### Getting Help

- Review `README.md` for full usage examples
- Check `SKILL.md` for detailed documentation
- See `CHANGELOG.md` for complete list of changes
- Open an issue if you encounter problems

### Rollback to v1.0.0

If needed, you can rollback:
```bash
cd ~/.openclaw/workspace/skills/edstem
git checkout b9895a1  # v1.0.0 commit
```

However, we recommend migrating to v1.1.0 for better flexibility and ongoing support.
