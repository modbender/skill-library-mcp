# Example Daily Memory Files

These are sample daily memory files to demonstrate the extraction process.

---

## Example 1: System Configuration (2026-02-20.md)

```markdown
# 2026-02-20

## Model Configuration Update
- Added new model alias `gpt4-turbo` for `openai/gpt-4-turbo-preview`
- Tested with subagent call, response time ~2s
- Updated openclaw.json with new provider config
- Backup created: openclaw.json.bak-20260220
```

**Expected Extraction**:
- Category: System
- Facts:
  - Added new model alias `gpt4-turbo` for `openai/gpt-4-turbo-preview`
  - Updated openclaw.json with new provider config

---

## Example 2: Skill Installation (2026-02-21.md)

```markdown
# 2026-02-21

## New Skills Installed
- **weather**: Installed via `npx skills add app/skills@weather`
- **pdf**: PDF processing skill with OCR support
- Both skills tested and working

## Configuration Notes
- Weather skill uses default location: UTC
- PDF skill requires tesseract for OCR (already installed)
```

**Expected Extraction**:
- Category: Skill
- Facts:
  - weather: Installed via `npx skills add app/skills@weather`
  - pdf: PDF processing skill with OCR support

---

## Example 3: Project Decision (2026-02-22.md)

```markdown
# 2026-02-22

## A-Share Strategy Decision
- Decided to focus on value investing approach
- Token limit optimization: Python pre-filtering (turnover, market cap, non-ST)
- AI analyzes top 20 candidates from pre-filtered list
- Backtest scheduled for weekend

## Action Items
- [ ] Write Python filtering script
- [ ] Set up backtest framework
- [ ] Document strategy parameters
```

**Expected Extraction**:
- Category: Project
- Facts:
  - Token limit optimization: Python pre-filtering (turnover, market cap, non-ST)
  - AI analyzes top 20 candidates from pre-filtered list

---

## Example 4: Environment Setup (2026-02-23.md)

```markdown
# 2026-02-23

## Workspace Cleanup
- Identified temp directories: bin/, downloads/, projects/
- Added to .gitignore to prevent accidental commits
- Created backup script for config files

## UV Policy Enforcement
- All Python execution must use /root/.local/bin/uv
- Created venv for isolated skill dependencies
- Documented in TOOLS.md
```

**Expected Extraction**:
- Category: Environment
- Facts:
  - Added to .gitignore to prevent accidental commits
  - All Python execution must use /root/.local/bin/uv

---

## Example 5: Communication Config (2026-02-24.md)

```markdown
# 2026-02-24

## Discord Channel Setup
- Created #a 股实验室📈 channel for investment discussions
- Channel ID: 1473185274774159486
- Configured bot to route A-share topics there

## Telegram Bot
- Updated webhook URL
- Added inline button support
```

**Expected Extraction**:
- Category: Comm
- Facts:
  - Created #a 股实验室📈 channel for investment discussions
  - Channel ID: 1473185274774159486

---

## Example 6: Security Policy (2026-02-25.md)

```markdown
# 2026-02-25

## Credential Storage
- API keys stored in environment variables only
- No plaintext credentials in .md files
- Database encryption considered for future

## Access Control
- .md files readable but not executable
- Database write access restricted to extraction script
```

**Expected Extraction**:
- Category: Security
- Facts:
  - API keys stored in environment variables only
  - No plaintext credentials in .md files

---

## Testing Extraction

Run extraction on these examples:

```bash
# Copy to memory directory
cp examples/sample_memories/*.md /home/node/.openclaw/workspace/memory/

# Run extraction (preview)
python3 scripts/extract_memory.py --review

# Run extraction (execute)
python3 scripts/extract_memory.py

# Verify results
python3 scripts/db_query.py --stats
```
