# Tasks: Implement arcee-ai/trinity-large-preview:free Fallback

## Task Checklist

### Phase 1: Update SKILL.md
- [ ] **T1.1**: Update version header: `version: 1.1.0`
- [ ] **T1.2**: Update Quick Start JSON example with new fallback
- [ ] **T1.3**: Add Trinity Large to Model Selection Guide table
- [ ] **T1.4**: Add Trinity Large to Free Models Available table
- [ ] **T1.5**: Update Fallback Strategy section with new order
- [ ] **T1.6**: Update Complete Example JSON with Trinity Large

### Phase 2: Update references/models.md
- [ ] **T2.1**: Add "### Trinity Large Free" section with full details
- [ ] **T2.2**: Add OpenRouter to Provider Information section
- [ ] **T2.3**: Update Rate Limits by Model table (add Trinity row)
- [ ] **T2.4**: Update Performance Comparison table (add Trinity row)
- [ ] **T2.5**: Update Configuration Tips examples with Trinity
- [ ] **T2.6**: Update Model Aliases section with Trinity entry

### Phase 3: Update references/templates.md
- [ ] **T3.1**: Update Minimal Template fallback chain
- [ ] **T3.2**: Update Complete Template fallback chain
- [ ] **T3.3**: Update Verifying Configuration section

### Phase 4: Finalize
- [ ] **T4.1**: Validate all JSON examples
- [ ] **T4.2**: Update memory file with changes summary
- [ ] **T4.3**: Final review of all modifications

---

## Implementation Details

### Model ID Format
```
openrouter/arcee-ai/trinity-large-preview:free
```

### Alias
```
Trinity Large
```

### Updated Fallback Order (by priority)
1. opencode/minimax-m2.1-free (Primary)
2. opencode/kimi-k2.5-free (Fallback 1)
3. openrouter/arcee-ai/trinity-large-preview:free ← NEW
4. opencode/glm-4.7-free
5. opencode/gpt-5-nano

### Files Modified
- `/root/.openclaw/workspace/skills/freeride-opencode/SKILL.md`
- `/root/.openclaw/workspace/skills/freeride-opencode/references/models.md`
- `/root/.openclaw/workspace/skills/freeride-opencode/references/templates.md`