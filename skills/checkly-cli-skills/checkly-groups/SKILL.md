---
name: checkly-groups
description: Organize checks with CheckGroups for shared configuration, settings inheritance, and logical organization. Use when managing multiple related checks, setting group-level defaults, or organizing monitoring by service/team. Triggers on check group, organize checks, shared configuration, group settings.
---

# checkly groups

Organize checks with shared configuration.

## Basic check group

```typescript
import { CheckGroup } from 'checkly/constructs'

export const apiChecks = new CheckGroup('api-checks', {
  name: 'API Monitoring',
  activated: true,
  locations: ['us-east-1', 'eu-west-1'],
  frequency: 5,
  tags: ['api', 'backend'],
  environmentVariables: [
    { key: 'API_BASE_URL', value: 'https://api.example.com' },
  ],
})
```

## Assign checks to group

```typescript
import { ApiCheck } from 'checkly/constructs'
import { apiChecks } from './groups'

new ApiCheck('status-check', {
  name: 'API Status',
  group: apiChecks,  // Inherits group settings
  request: {
    url: '{{API_BASE_URL}}/status',
  },
})
```

## Hierarchical configuration

Group settings override global defaults:

```
1. Check properties (highest priority)
2. CheckGroup properties
3. checkly.config.ts defaults
4. Account defaults (lowest priority)
```

## Alert channels per group

```typescript
import { CheckGroup, EmailAlertChannel } from 'checkly/constructs'

const emailChannel = new EmailAlertChannel('team-email', {
  address: 'team@example.com',
})

export const criticalGroup = new CheckGroup('critical', {
  name: 'Critical Services',
  alertChannels: [emailChannel],
  frequency: 1,
})
```

## Related Skills

- See `checkly-checks` for creating checks
- See `checkly-config` for global defaults
