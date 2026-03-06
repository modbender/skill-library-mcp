# Sanitization Checklist

**Run this BEFORE any publish.** Public skills are permanent.

## Personal Data

Remove or genericize:
- [ ] Names (your name, team members, company)
- [ ] Email addresses
- [ ] Usernames, handles, IDs
- [ ] Phone numbers
- [ ] Addresses, locations
- [ ] URLs to private resources
- [ ] Internal project names
- [ ] Client/customer references

## Credentials & Secrets

**NEVER include:**
- [ ] API keys, tokens, passwords
- [ ] Environment variable VALUES (names are ok)
- [ ] Private URLs with auth params
- [ ] Database connection strings
- [ ] SSH keys, certificates

## Model-Specific References

Remove references to specific models that won't apply to all users:
- [ ] "Claude" → "the agent" or "the model"
- [ ] "GPT" → generic term
- [ ] Specific model versions
- [ ] Provider-specific features

## Internal References

Remove:
- [ ] References to your specific file paths
- [ ] Your workspace structure
- [ ] Your tool configurations
- [ ] Internal documentation links
- [ ] Team-specific workflows

## Dangerous Patterns

Check for:
- [ ] Commands that could damage systems
- [ ] Patterns that encourage unsafe behavior
- [ ] Hardcoded paths that won't work elsewhere
- [ ] Assumptions about user's environment

## Genericize Examples

Replace specific with generic:
- `~/my-company/project` → `~/projects/example`
- `john@company.com` → `user@example.com`
- `api.mycompany.com` → `api.example.com`
- Internal tool names → generic descriptions

## Final Check

Before publishing, read entire skill asking:
- "Would I be comfortable if this were public forever?"
- "Could this expose anything about me/my company?"
- "Would this work for someone with zero context about me?"

## If Unsure

**Ask the user:**
> "I found [X] which might be personal/internal. Should I remove, genericize, or keep it?"

Better to ask than to publish something private.
