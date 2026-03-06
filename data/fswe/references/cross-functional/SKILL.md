# Cross-Functional Collaboration

## Technical Spec Template

```markdown
# Feature: Password Reset

## Overview
Brief description of the feature

## Goals
- Allow users to reset forgotten passwords
- Secure token-based verification

## Non-Goals
- Social login (out of scope)
- Password strength analytics (future)

## User Stories
- User requests password reset
- User receives email with link
- User sets new password

## Technical Design

### API Changes
- POST /api/password/reset-request
- POST /api/password/reset-confirm

### Database
- Add `password_reset_token` to users table
- Add `password_reset_expires` to users table

### Security
- Token expires in 1 hour
- Token is cryptographically random

## Timeline
- Development: 2 days
- Testing: 1 day

## Dependencies
- Email service (existing)
```

## Communication Tips

| Situation | Approach |
|-----------|----------|
| Push back | Provide data + alternatives |
| Explain technical | Use analogies |
| Disagree | State concerns + listen |
| Ask help | Be specific about what you need |

## Checklist

- [ ] Write technical specs
- [ ] Communicate blockers early
- [ ] Provide updates regularly
- [ ] Document decisions
- [ ] Share knowledge proactively
