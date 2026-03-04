# Plan: Add arcee-ai/trinity-large-preview:free Fallback

## Objective
Update freeride-opencode skill (v1.0.0 → v1.1.0) to include arcee-ai/trinity-large-preview:free via OpenRouter as an additional fallback option.

## Steps

### Step 1: Update SKILL.md
- [ ] Bump version from 1.0.0 to 1.1.0
- [ ] Add Trinity Large to Quick Start JSON example
- [ ] Add Trinity Large to Model Selection Guide table
- [ ] Add Trinity Large to Free Models Available table
- [ ] Update Fallback Strategy section with new fallback order
- [ ] Update Complete Example JSON
- [ ] Update Best Practices section if needed

### Step 2: Update references/models.md
- [ ] Add new "Trinity Large Free" section with model details
- [ ] Update Provider Information section (add OpenRouter)
- [ ] Update Rate Limits by Model table
- [ ] Update Performance Comparison table
- [ ] Update Configuration Tips examples
- [ ] Update Model Aliases section
- [ ] Update Migration section (add Trinity mention)

### Step 3: Update references/templates.md
- [ ] Update Minimal Template fallback chain
- [ ] Update Complete Template fallback chain
- [ ] Add new template variant (Trinity-Focused) - optional
- [ ] Update Verifying Configuration section
- [ ] Update Resetting to Defaults section if needed

### Step 4: Version Bump & Publish
- [ ] Update version in SKILL.md header (already done in Step 1)
- [ ] Validate all JSON examples are syntactically correct
- [ ] Update any internal version references
- [ ] Document changes in memory/today's file

## Validation
- All JSON examples parse correctly
- Model IDs follow existing pattern (`openrouter/provider/model:free`)
- Documentation is consistent with existing style
- Backward compatibility maintained

## Estimated Time
- Step 1: 10 minutes
- Step 2: 15 minutes
- Step 3: 10 minutes
- Step 4: 5 minutes
- **Total: ~40 minutes**

## Rollback Plan
If issues arise:
1. Revert SKILL.md to v1.0.0
2. Revert models.md to remove Trinity Large entry
3. Revert templates.md fallback chains
4. No configuration files need changes (skill is documentation-only)