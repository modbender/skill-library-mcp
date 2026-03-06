# InstantDB Query Syntax Reference

## Basic Query Structure

```javascript
{
  namespace: {
    $: {
      // Query options
    },
    // Nested relationships
  }
}
```

## Query Options

### Where Clauses

Filter entities by attribute values:

```javascript
{
  tasks: {
    $: {
      where: {
        status: 'active',
        priority: { in: ['high', 'urgent'] },
        createdAt: { gt: Date.now() - 86400000 }
      }
    }
  }
}
```

Operators:
- Equality: `attr: value`
- In set: `attr: { in: [val1, val2] }`
- Greater than: `attr: { gt: value }`
- Less than: `attr: { lt: value }`
- Greater/equal: `attr: { gte: value }`
- Less/equal: `attr: { lte: value }`

### Limit and Offset

Paginate results:

```javascript
{
  tasks: {
    $: {
      limit: 10,
      offset: 20
    }
  }
}
```

### Order

Sort results:

```javascript
{
  tasks: {
    $: {
      order: {
        createdAt: 'desc',
        priority: 'asc'
      }
    }
  }
}
```

## Relationships

### Forward Links

Query related entities:

```javascript
{
  tasks: {
    assignees: {
      // User entities linked as assignees
    },
    comments: {
      $: {
        where: { archived: false }
      }
    }
  }
}
```

### Reverse Links

Query entities that link to this one:

```javascript
{
  users: {
    tasks: {
      $: {
        via: 'assignees'  // Tasks where this user is an assignee
      }
    }
  }
}
```

## Complex Queries

### Multi-level Nesting

```javascript
{
  projects: {
    tasks: {
      assignees: {
        // Users assigned to tasks in projects
      },
      comments: {
        author: {
          // Authors of comments on tasks
        }
      }
    }
  }
}
```

### Multiple Namespaces

```javascript
{
  tasks: {
    $: { where: { status: 'active' } }
  },
  users: {
    $: { where: { role: 'admin' } }
  }
}
```

## Optimization

### Selective Fields

InstantDB returns all attributes by default. Structure queries to only traverse needed relationships:

```javascript
// Good: Only get what you need
{
  tasks: {
    assignees: {}  // Just assignee data
  }
}

// Avoid: Deep nesting when not needed
{
  tasks: {
    assignees: {
      teams: {
        organization: {}  // Unnecessary depth
      }
    }
  }
}
```

## Common Patterns

### Active Items

```javascript
{
  tasks: {
    $: {
      where: {
        status: { in: ['todo', 'in_progress'] },
        deletedAt: null
      }
    }
  }
}
```

### Recent Items

```javascript
{
  posts: {
    $: {
      where: {
        createdAt: { gt: Date.now() - 86400000 }  // Last 24h
      },
      order: { createdAt: 'desc' },
      limit: 20
    }
  }
}
```

### Items with Relationships

```javascript
{
  tasks: {
    $: {
      where: { hasAssignees: true }
    },
    assignees: {}
  }
}
```

## Using with InstantDB Admin SDK

```javascript
const { init } = require('@instantdb/admin');

const db = init({ 
  appId: process.env.INSTANTDB_APP_ID,
  adminToken: process.env.INSTANTDB_ADMIN_TOKEN
});

const result = await db.query({
  tasks: {
    $: {
      where: { status: 'active' },
      limit: 10
    },
    assignees: {}
  }
});

console.log(result.tasks);
```
