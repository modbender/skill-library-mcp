# OpenClaw Skill Improvements

## Summary

Fixed critical issues with conversation data handling based on agent feedback. The skill now **requires minimum 3 messages** and uses **explicit errors** instead of silent fallbacks.

## Changes Made

### 1. Minimum Message Requirement ✅

**Before:**
```typescript
// Silent fallback to empty data
if (analysis.messageCount === 0) {
  console.log('⚠️  No conversation history found, using empty data');
  return { topics: [], interests: [], preferences: [], history: [] };
}
```

**After:**
```typescript
// Explicit error with clear message
if (analysis.messageCount < 3) {
  throw new Error(
    `Insufficient conversation data: ${analysis.messageCount} messages found (minimum 3 required). ` +
    `Please continue chatting with OpenClaw to build conversation history.`
  );
}
```

### 2. Data Quality Check ✅

**Before:**
```typescript
hasSufficientData(userData: UserData): boolean {
  return userData.sources.length > 0;  // ❌ Too permissive
}
```

**After:**
```typescript
hasSufficientData(userData: UserData): boolean {
  // Must have conversation with ≥3 messages
  if (!userData.conversationMemory) return false;
  if (userData.conversationMemory.messageCount < 3) return false;
  return true;
}
```

### 3. OpenClaw Integration ✅

**Before:**
```bash
# Only accepted positional arguments
USER_ID="$1"
npx tsx src/index.ts --user-id "$USER_ID"
```

**After:**
```bash
# Forwards all arguments correctly
npx tsx src/index.ts "$@"
```

Now compatible with OpenClaw's execution format:
```json
{
  "execution": {
    "type": "script",
    "entrypoint": "scripts/generate.sh",
    "args": ["--user-id", "$OPENCLAW_USER_ID"]
  }
}
```

### 4. Interface Update ✅

Added `messageCount` to `ConversationMemory`:
```typescript
export interface ConversationMemory {
  topics: string[];
  interests: string[];
  preferences: string[];
  history: string[];
  messageCount: number;  // ⭐ NEW: Required for validation
}
```

## Key Principles (from Agent Feedback)

1. ✅ **Use correct userId** - Must match OpenClaw session (telegram:<id>, discord:<id>)
2. ✅ **Read current session** - Not empty/stale sessions
3. ✅ **Explicit errors** - No silent fallbacks to mock data
4. ✅ **Minimum validation** - Requires ≥3 messages
5. ✅ **Twitter optional** - Conversation is primary (85%), Twitter is secondary (15%)

## User Experience

**Before:**
- ❌ Skill silently used empty/mock data
- ❌ User got generic results without knowing why
- ❌ No guidance on how to get better results

**After:**
- ✅ Clear error: "Insufficient conversation data: 1 messages found (minimum 3 required)"
- ✅ Actionable guidance: "Please continue chatting with OpenClaw"
- ✅ Real data or explicit failure (no silent degradation)

## Documentation Updates

Updated `SKILL.md` to reflect:
- Minimum 3 messages requirement
- Explicit error handling
- Clear rules for data collection

## Testing

Test with insufficient data:
```bash
# Should fail with clear error
bash scripts/generate.sh --user-id test-user-with-2-messages
```

Expected output:
```
❌ Insufficient conversation data: 2 messages found (minimum 3 required).
   Please continue chatting with OpenClaw to build conversation history.
```

Test with sufficient data:
```bash
# Should succeed
bash scripts/generate.sh --user-id test-user-with-10-messages
```

## Files Modified

1. `src/analyzers/data-collector-enhanced.ts`
   - `collectConversationMemory()` - Throws error if < 3 messages
   - `hasSufficientData()` - Validates messageCount ≥ 3
   - `ConversationMemory` interface - Added messageCount field

2. `scripts/generate.sh`
   - Changed from positional args to `"$@"` forwarding
   - Compatible with OpenClaw's `--user-id` flag

3. `SKILL.md`
   - Documented minimum 3 messages requirement
   - Clarified data collection rules
   - Added explicit error handling notes

## Next Steps

- [x] Fix conversation data validation
- [x] Add minimum message requirement
- [x] Update OpenClaw argument handling
- [x] Document changes
- [ ] Test with real OpenClaw session
- [ ] Verify userId format (telegram:<id>, discord:<id>)
- [ ] Deploy to ClawHub registry

---

**Built by**: Bloom Protocol
**Date**: 2026-02-07
