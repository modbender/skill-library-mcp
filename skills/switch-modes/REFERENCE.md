# Switch Modes - Reference Guide

Complete technical reference for the Switch Modes skill.

## Supported Models

### Anthropic
- `anthropic/claude-3.5-haiku` - Fastest, cheapest (recommended for ECO)
- `anthropic/claude-sonnet-4-5` - Balanced performance (recommended for BALANCED)
- `anthropic/claude-opus-4-5` - Powerful reasoning (recommended for SMART)
- `anthropic/claude-opus-4-6` - Most powerful (recommended for MAX)

### OpenAI
- `openai/gpt-4o-mini` - Cheap option
- `openai/gpt-4o` - Balanced option
- `openai/o1` - Advanced reasoning
- `openai/o1-pro` - Maximum reasoning (alternative for MAX)

### Other Providers
Any model ID supported by your OpenClaw installation will work. Use the format: `provider/model-name`

## Configuration File Structure

Location: `~/.openclaw/workspace/switch-modes.json`

### Format
```json
{
  "eco": "anthropic/claude-3.5-haiku",
  "balanced": "anthropic/claude-sonnet-4-5",
  "smart": "anthropic/claude-opus-4-5",
  "max": "anthropic/claude-opus-4-6"
}
```

### Validation Rules
- Must be valid JSON
- Must contain all 4 mode keys: `eco`, `balanced`, `smart`, `max`
- Values must be valid model IDs
- Model IDs must be configured in OpenClaw with proper API keys

## OpenClaw Configuration

Location: `~/.openclaw/openclaw.json`

The skill modifies the `model` field in this file. Example structure:
```json
{
  "model": "anthropic/claude-sonnet-4-5",
  "apiKeys": {
    "anthropic": "sk-...",
    "openai": "sk-..."
  },
  ...other settings
}
```

**Important**: Only modify the `model` field. Preserve all other settings.

## Use Cases

### Cost Optimization
Save 60-80% on API costs by using appropriate models for each task:

- **ECO mode**: Quick questions, summaries, simple edits, typo fixes
- **BALANCED mode**: Daily coding, general tasks, moderate complexity
- **SMART mode**: Code review, architecture decisions, complex debugging
- **MAX mode**: Critical production issues, system design, research

### Task-Based Switching Examples

| Task | Recommended Mode | Reason |
|------|------------------|--------|
| Fix typo | ECO | Simple text operation |
| Write email | ECO | Basic text generation |
| General chat | BALANCED | Standard conversation |
| Code refactoring | BALANCED | Moderate complexity |
| Security review | SMART | Requires deep analysis |
| System architecture | MAX | Complex reasoning needed |
| Production debugging | MAX | Critical task |

### Model Testing
- Compare outputs from different models on same prompt
- Test which model works best for specific use cases
- Switch mid-conversation to evaluate differences

## Troubleshooting

### "Model not found" Error

**Causes:**
1. Model ID is incorrect or has typo
2. API key not configured in OpenClaw
3. Model requires specific API plan you don't have

**Solutions:**
1. Run `/modes setup` and double-check model IDs
2. Verify API keys in `~/.openclaw/openclaw.json`
3. Check your API provider dashboard for model access
4. Try a different model that you have access to

### Mode Not Switching

**Symptoms:** Command runs but model doesn't change

**Debug steps:**
1. Run `/modes status` to verify current state
2. Check `~/.openclaw/workspace/switch-modes.json` exists and is valid JSON
3. Check `~/.openclaw/openclaw.json` was actually updated
4. Verify file permissions (should be readable/writable)
5. Try `/modes setup` again to recreate config

**Common causes:**
- JSON syntax error in config file
- File permission issues
- OpenClaw config file locked or in use

### Cost Not Decreasing

**Verify:**
1. Actually using ECO mode for simple tasks (check with `/modes status`)
2. ECO mode points to a cheaper model (check config file)
3. Tracking usage correctly in your API dashboard

**Reality check:** Savings depend on task distribution. If you only do complex tasks, you won't see major savings.

### Config File Corruption

If `switch-modes.json` gets corrupted:

1. Delete it: `rm ~/.openclaw/workspace/switch-modes.json`
2. Run `/modes setup` to recreate
3. Or manually create with valid JSON structure (see above)

## Technical Details

### How Mode Switching Works

1. **Detection**: Agent scans user message for mode keywords
2. **Config Lookup**: Reads `switch-modes.json` to get model mapping
3. **Update**: Modifies `openclaw.json` with new model ID
4. **Confirmation**: Notifies user of successful switch

### Performance
- Mode switching is instant (< 1 second)
- No gateway restart required
- No interruption to current conversation
- Next message uses new model immediately

### Privacy & Security
- All configuration stored locally on your machine
- No data sent to external services (except normal API calls)
- Standard OpenClaw security model applies
- Model API keys managed by OpenClaw

### Limitations

1. **4 modes maximum**: Currently hardcoded to eco/balanced/smart/max
2. **Per-session**: Mode changes affect global OpenClaw config
3. **Manual API key management**: API keys must be configured in OpenClaw separately

## FAQ

### General

**Q: Does this work with all OpenClaw installations?**
A: Yes, as long as you have models configured with valid API keys.

**Q: Can I rename the modes?**
A: No, modes are hardcoded to eco/balanced/smart/max. You can change which models they map to, but not the mode names.

**Q: Can I add a 5th mode?**
A: Not currently. The skill is designed for 4 modes.

**Q: Will this break my existing OpenClaw setup?**
A: No. It only modifies the `model` field in your config, preserving all other settings.

### Models

**Q: Can I use custom or local models?**
A: Yes! Any model ID that OpenClaw supports will work, including custom/local models.

**Q: Can I use the same model for multiple modes?**
A: Yes, but it defeats the purpose. You could set all modes to the same model if needed.

**Q: What if I only have access to one model?**
A: The skill will still work, but you won't get cost savings. Set all modes to your available model.

### Advanced

**Q: Can I edit the config file manually?**
A: Yes. Just ensure it's valid JSON with all 4 required keys.

**Q: Does this affect other OpenClaw sessions?**
A: Yes. It modifies the global OpenClaw config, so all sessions use the new default model.

**Q: Can I automate mode switching based on task type?**
A: Not currently. Mode switching is manual via user commands.

**Q: Is there a way to see mode switching history?**
A: No built-in tracking. You'd need to manually log mode changes if desired.

## Best Practices

1. **Start with setup**: Always run `/modes setup` first before using mode commands
2. **Validate model IDs**: Use exact IDs from your API provider
3. **Test each mode**: After setup, test each mode to ensure models work
4. **Check status regularly**: Use `/modes status` to know which mode you're in
5. **Use ECO liberally**: Default to ECO for simple tasks, only escalate when needed
6. **Document your choices**: Keep notes on which mode works best for your common tasks

## Cost Savings Calculator

Approximate costs (as of 2024, check current pricing):

| Mode | Model Example | Input Cost* | Output Cost* |
|------|---------------|-------------|--------------|
| ECO | Haiku | $0.25/M | $1.25/M |
| BALANCED | Sonnet | $3/M | $15/M |
| SMART | Opus 4.5 | $15/M | $75/M |
| MAX | Opus 4.6 | $30/M | $150/M |

*Per million tokens. Prices vary by provider.

**Example savings:**
- 100k tokens/day on ECO instead of MAX: ~$29/day saved
- Monthly savings: ~$870/month
- Realistic mixed usage: 60-80% cost reduction

## Integration with Other Tools

### Git Workflow
- Use ECO for commit messages
- Use BALANCED for PR descriptions
- Use SMART for code review

### Development
- Use ECO for simple edits
- Use BALANCED for implementation
- Use SMART for debugging
- Use MAX for architecture

### Writing
- Use ECO for drafts
- Use BALANCED for editing
- Use SMART for technical docs

## Version History

- **1.0.0**: Initial release with 4-mode support
