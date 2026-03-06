# InstantDB Transaction Patterns

## Transaction Structure

Use the `tx` builder for type-safe transactions:

```javascript
const { tx, id } = require('@instantdb/admin');

await db.transact([
  tx.tasks[id()].update({ title: 'New task' }),
  tx.users[userId].update({ lastSeen: Date.now() })
]);
```

## Transaction Builder API

### Update (Create or Modify)

```javascript
// Create new entity
const taskId = id();
await db.transact([
  tx.tasks[taskId].update({
    title: 'New task',
    status: 'pending'
  })
]);

// Update existing entity
await db.transact([
  tx.tasks[existingId].update({
    status: 'completed'
  })
]);
```

### Delete

```javascript
await db.transact([
  tx.tasks[taskId].delete()
]);
```

### Link

```javascript
// Create relationship
await db.transact([
  tx.tasks[taskId].link({
    assignees: userId
  })
]);

// Link multiple
await db.transact([
  tx.tasks[taskId].link({
    assignees: [user1Id, user2Id, user3Id]
  })
]);
```

### Unlink

```javascript
// Remove relationship
await db.transact([
  tx.tasks[taskId].unlink({
    assignees: userId
  })
]);
```

## Common Patterns

### Create Entity with Relationships

```javascript
const { tx, id } = require('@instantdb/admin');

const taskId = id();
const userId = id();

await db.transact([
  tx.tasks[taskId].update({ title: 'Review PR' }),
  tx.users[userId].update({ name: 'Alice' }),
  tx.tasks[taskId].link({ assignees: userId })
]);
```

### Move Entity Between States

```javascript
const { tx } = require('@instantdb/admin');

await db.transact([
  tx.tasks[taskId].update({
    status: 'completed',
    completedAt: Date.now()
  }),
  tx.boards[boardId].unlink({ activeTasks: taskId }),
  tx.boards[boardId].link({ completedTasks: taskId })
]);
```

### Batch Create

```javascript
const { tx, id } = require('@instantdb/admin');

const tasks = ['Task 1', 'Task 2', 'Task 3'];

await db.transact(
  tasks.map(title => 
    tx.tasks[id()].update({
      title,
      status: 'pending'
    })
  )
);
```

### Cascade Delete

```javascript
const { tx } = require('@instantdb/admin');

// Delete task and all its comments
const commentIds = ['comment1', 'comment2', 'comment3'];

await db.transact([
  tx.tasks[taskId].delete(),
  ...commentIds.map(commentId => tx.comments[commentId].delete())
]);
```

### Swap Relationships

```javascript
const { tx } = require('@instantdb/admin');

// Reassign task from user1 to user2
await db.transact([
  tx.tasks[taskId].unlink({ assignees: user1Id }),
  tx.tasks[taskId].link({ assignees: user2Id })
]);
```

### Conditional Update Pattern

```javascript
// Query current state
const result = await db.query({
  tasks: {
    $: { where: { id: taskId } }
  }
});

const currentStatus = result.tasks[0]?.status;

// Only update if in expected state
if (currentStatus === 'pending') {
  await db.transact([
    tx.tasks[taskId].update({
      status: 'in_progress',
      startedAt: Date.now()
    })
  ]);
}
```

## OpenClaw Workflow Pattern

Track multi-step operation progress:

```javascript
const { tx, id } = require('@instantdb/admin');

const workflowId = id();
const steps = ['Fetch Data', 'Process', 'Validate', 'Store'];

// Initialize workflow with steps
const stepIds = steps.map(() => id());

await db.transact([
  tx.workflows[workflowId].update({
    name: 'Data Pipeline',
    status: 'running',
    totalSteps: steps.length,
    currentStep: 0,
    startedAt: Date.now()
  }),
  ...steps.map((name, i) =>
    tx.steps[stepIds[i]].update({
      name,
      order: i,
      status: 'pending'
    })
  ),
  ...stepIds.map(stepId =>
    tx.workflows[workflowId].link({ steps: stepId })
  )
]);

// Execute and update each step
for (let i = 0; i < stepIds.length; i++) {
  // Mark step as running
  await db.transact([
    tx.steps[stepIds[i]].update({
      status: 'running',
      startedAt: Date.now()
    }),
    tx.workflows[workflowId].update({
      currentStep: i + 1
    })
  ]);
  
  // ... perform work ...
  
  // Mark step as complete
  await db.transact([
    tx.steps[stepIds[i]].update({
      status: 'completed',
      completedAt: Date.now()
    })
  ]);
}

// Mark workflow complete
await db.transact([
  tx.workflows[workflowId].update({
    status: 'completed',
    completedAt: Date.now()
  })
]);
```

## Advanced Patterns

### Optimistic Updates

```javascript
// Update local state immediately, then sync
const { tx, id } = require('@instantdb/admin');

function updateTaskLocally(task) {
  // Update UI optimistically
  localState.tasks.push(task);
  
  // Sync to InstantDB
  db.transact([
    tx.tasks[task.id].update(task)
  ]).catch(error => {
    // Rollback on error
    localState.tasks = localState.tasks.filter(t => t.id !== task.id);
  });
}
```

### Bulk Operations with Progress Tracking

```javascript
const { tx, id } = require('@instantdb/admin');

async function bulkImport(items, batchSize = 50) {
  const progressId = id();
  
  await db.transact([
    tx.progress[progressId].update({
      total: items.length,
      completed: 0,
      status: 'running'
    })
  ]);

  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    
    await db.transact(
      batch.map(item => tx.items[id()].update(item))
    );
    
    await db.transact([
      tx.progress[progressId].update({
        completed: Math.min(i + batchSize, items.length)
      })
    ]);
  }

  await db.transact([
    tx.progress[progressId].update({
      status: 'completed'
    })
  ]);
}
```

## Error Handling

Transactions are atomic - all operations succeed or all fail:

```javascript
try {
  const result = await db.transact([
    tx.tasks[id()].update({ title: 'Task' }),
    tx.invalid[id()].update({ data: 'bad' })
  ]);
  console.log('Success:', result);
} catch (error) {
  console.error('Transaction failed:', error);
  // All operations rolled back
}
```

## Performance

- Batch operations into single transaction when possible
- Each transaction is one network round-trip
- Max recommended transaction size: ~100 operations
- For larger batches, split into multiple transactions
- Use `id()` to generate UUIDs client-side
