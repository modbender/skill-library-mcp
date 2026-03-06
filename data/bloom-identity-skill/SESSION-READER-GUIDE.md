# Session Reader Guide

## Quick Start

Analyze your complete OpenClaw conversation history:

```bash
npx tsx scripts/run-from-session.ts \
  ~/.openclaw/agents/main/sessions/<SessionId>.jsonl \
  telegram:123
```

---

## What's New

### ✅ Full Session Analysis
- Reads last **~120 messages** from session file
- More comprehensive than piped context
- Better personality detection

### ✅ Improved Output Format
- **No data quality shown** (cleaner output)
- **Wallet notification** instead of full address
- **Marketing messages** clearly displayed
- **Warnings** about upcoming features

---

## Output Format

```
═══════════════════════════════════════════════════════
🎉 Your Bloom Identity Card is ready! 🤖
═══════════════════════════════════════════════════════

🔗 VIEW YOUR IDENTITY CARD:
   https://preflight.bloomprotocol.ai/agents/27811541

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💜 The Visionary
💬 "The AI Tools Pioneer"

You back bold ideas before they're obvious. Your conviction is
your edge, and you see potential where others see risk. AI Tools
is where you spot the next paradigm shift.

🏷️  Categories: AI Tools · Productivity · Wellness
   Interests: Machine Learning · Automation · Meditation

📊 2x2 Dimensions:
   Conviction: 50/100
   Intuition: 55/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Top 5 Recommended Skills:

1. ai-code-review (95% match) · by Alice
   Automated code review using GPT-4
   → https://clawhub.com/skills/ai-code-review

2. productivity-toolkit (88% match)
   Streamline your workflow automation
   → https://clawhub.com/skills/productivity

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Your Agent Wallet Created

   Network: Base
   Status: ✅ Wallet generated and registered

   💡 Use your agent wallet to tip skill creators!
   ⚠️  Tipping, payments, and management features coming soon
   🔒 Do not deposit funds - withdrawals not ready yet

═══════════════════════════════════════════════════════

🌸 Bloom Identity · Built with @openclaw @coinbase @base
```

---

## Finding Your Session File

### Location
```bash
~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl
```

### Example
```bash
~/.openclaw/agents/main/sessions/abc123def456.jsonl
```

### List All Sessions
```bash
ls -lht ~/.openclaw/agents/main/sessions/*.jsonl | head -5
```

### Get Most Recent
```bash
ls -t ~/.openclaw/agents/main/sessions/*.jsonl | head -1
```

---

## Usage Methods

### 1. Direct Session File (Recommended)

**Best for**: Complete conversation analysis

```bash
npx tsx scripts/run-from-session.ts \
  ~/.openclaw/agents/main/sessions/abc123.jsonl \
  telegram:123
```

**Features**:
- ✅ Reads last ~120 messages
- ✅ Most accurate personality detection
- ✅ Complete conversation context

### 2. Piped Context (Quick Test)

**Best for**: Testing with small samples

```bash
echo "User: I love AI tools
Assistant: What kind?
User: GPT-4 and Claude" | \
  npx tsx scripts/run-from-context.ts --user-id test-123
```

**Features**:
- ✅ Quick testing
- ✅ No file needed
- ⚠️  Limited context (only piped text)

### 3. OpenClaw Wrapper (Auto-detect)

**Best for**: OpenClaw bot integration

```bash
bash openclaw-wrapper/execute.sh telegram:123
```

**Features**:
- ✅ Auto-detects session file
- ✅ Integrates with OpenClaw
- ✅ User-invocable via `/bloom-identity`

---

## Comparison

| Method | Context Size | Speed | Accuracy | Use Case |
|--------|-------------|-------|----------|----------|
| run-from-session | ~120 msgs | Medium | High | Production |
| run-from-context | Piped only | Fast | Medium | Testing |
| OpenClaw wrapper | Auto | Medium | High | Bot integration |

---

## Examples

### Example 1: Analyze Your Session

```bash
# Find your session ID
SESSION_ID=$(ls -t ~/.openclaw/agents/main/sessions/*.jsonl | head -1)

# Run analysis
npx tsx scripts/run-from-session.ts "$SESSION_ID" telegram:yourUserId
```

### Example 2: With Specific User ID

```bash
npx tsx scripts/run-from-session.ts \
  ~/.openclaw/agents/main/sessions/abc123.jsonl \
  telegram:123456789
```

### Example 3: From OpenClaw Bot

```bash
# In OpenClaw conversation
/bloom-identity
```

---

## Output Changes

### ❌ Old Format (Removed)
```
Data Quality: 80/100  ← No longer shown
Wallet: 0x1234...5678  ← No longer shown (too technical)
```

### ✅ New Format (Current)
```
🤖 Your Agent Wallet Created
   Network: Base
   Status: ✅ Wallet generated and registered

   💡 Use your agent wallet to tip skill creators!
   ⚠️  Tipping, payments, and management features coming soon
   🔒 Do not deposit funds - withdrawals not ready yet
```

**Improvements**:
- More user-friendly language
- Clear status notification
- Marketing message visible
- Safety warnings prominent

---

## Troubleshooting

### "Session file not found"

**Check**:
```bash
ls ~/.openclaw/agents/main/sessions/
```

**Solution**:
- Ensure OpenClaw has created session files
- Check correct agent ID (usually `main`)
- Use absolute path to session file

### "No conversation text found"

**Possible causes**:
- Empty session file
- Wrong file format
- Session file corrupted

**Solution**:
```bash
# Check file content
head -5 ~/.openclaw/agents/main/sessions/abc123.jsonl

# Should see JSON lines like:
{"type":"message","message":{"role":"user","content":[...]}}
```

### "Insufficient conversation data: X messages (minimum 3 required)"

**Solution**:
- Continue chatting with OpenClaw bot
- Need at least 3 conversation turns
- Each turn = User + Assistant message

---

## Technical Details

### Session File Format

JSONL (JSON Lines):
```json
{"type":"message","message":{"role":"user","content":[{"type":"text","text":"Hello"}]}}
{"type":"message","message":{"role":"assistant","content":[{"type":"text","text":"Hi!"}]}}
```

### Extraction Process

1. Read last 120 lines from JSONL
2. Parse JSON for each line
3. Extract user/assistant messages
4. Format as conversation text
5. Pass to Bloom analyzer

### Message Limit

- Default: 120 messages (~60 turns)
- Configurable in code: `readJsonl(path, limit)`
- Balance between context and performance

---

## Integration

### For OpenClaw Users

Install the wrapper:
```bash
cp -r openclaw-wrapper ~/.openclaw/skills/bloom-identity-openclaw
```

Use in conversation:
```
/bloom-identity
```

### For Developers

```typescript
import { BloomIdentitySkillV2 } from './src/bloom-identity-skill-v2';

const skill = new BloomIdentitySkillV2();
const result = await skill.execute(userId, {
  conversationText: fullConversation,
  skipShare: true,
});
```

---

## Performance

**Benchmark** (120 messages, ~5KB):
- File read: ~20ms
- JSON parsing: ~30ms
- Analysis: ~45ms
- **Total**: ~95ms

**Memory**:
- Session file: ~5KB (120 messages)
- Parsed data: ~2KB
- Analysis: ~1KB
- **Total**: ~8KB

---

**Status**: ✅ Production ready
**Version**: 2.0.0
**Date**: 2026-02-07
