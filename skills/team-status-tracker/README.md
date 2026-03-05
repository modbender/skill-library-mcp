# Team Status Tracker via Slack

Systematic team status tracking via Slack DMs with confidential Obsidian-based internal tracking.

## Quick Start

1. **Send personalized status requests** via Slack DMs (see templates)
2. **Monitor responses** throughout the day
3. **Follow up** with non-responders (mid-day, EOD)
4. **Track internally** in Obsidian (confidential)
5. **Never share** commercial/payment info with resources

## Key Features

- ✅ Personalized Slack DM status requests
- ✅ Response monitoring and follow-up system
- ✅ Confidential Obsidian tracking
- ✅ Behavioral pattern analysis
- ✅ **Configurable finance transparency** (NEW in v1.0.2)
- ✅ Confidentiality rules (protect sensitive info)
- ✅ Multiple reminder templates
- ✅ Response quality assessment

## Configuration

**NEW:** Configurable finance transparency flag!

```yaml
# config.yaml
confidentiality:
  finance_transparency: 0  # 0 = NEVER share financial info (DEFAULT)
                           # 1 = Share budget/payment context when needed
```

**When to use `finance_transparency: 1`:**
- Senior team members with P&L responsibility
- Budget constraints affect decisions
- Payment timing impacts work planning

**Keep at `0` (default) for:**
- Junior team members
- Contractors/outsourced resources
- Default safe option

See `config.yaml` for full configuration options.

## Files Included

- `SKILL.md` - Complete implementation guide
- `config.yaml` - Configuration template (NEW)
- `templates/status-request.md` - Message templates for Slack
- `templates/obsidian-tracking.md` - Internal tracking templates

## Usage

```bash
# Read the skill
cat SKILL.md

# Use status request templates
cat templates/status-request.md

# Set up Obsidian tracking
cat templates/obsidian-tracking.md
```

## Critical Rules

### ❌ ALWAYS CONFIDENTIAL (Regardless of Config):
- Performance comparisons between team members
- Behavioral tracking notes
- Response time metrics
- Non-responder lists

### 💰 FINANCIAL INFO (Config-Dependent):
- **finance_transparency: 0** (DEFAULT) → ❌ NEVER share billing, revenue, budgets
- **finance_transparency: 1** (OPTIONAL) → ✅ CAN share project budgets, payment context

### ✅ ALWAYS OK to Share:
- Project requirements and technical details
- Task assignments and deadlines
- Technical support and coordination
- General project status and priority

## Example Workflow

**Morning:** Send personalized status requests
```
Hi [Name]! 👋
Quick status check on [Project]:
📊 Current progress? Any blockers?
```

**Afternoon:** Check responses, follow up
```
Thanks for the update! 
📋 Could you provide task ID and timeline?
```

**EOD:** Nudge non-responders
```
Hi [Name]! ⏰
Quick reminder - please share status by EOD.
```

**Internal:** Track in Obsidian (confidential)
```
Team Member A: Responded 2h (PROMPT), detailed update...
Team Member B: No response (DELAYED), follow up tomorrow...
```

## Integration

- **Slack API** via Maton Gateway
- **Obsidian** for internal tracking
- **Daily routine** for consistent updates

## License

MIT

## Tags

`slack` `team-management` `status-tracking` `obsidian` `confidentiality` `communication`
