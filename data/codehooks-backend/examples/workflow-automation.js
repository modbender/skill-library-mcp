import { app, Datastore } from 'codehooks-js';

// Workflow for autonomous task processing
// Agent starts workflow, it runs independently, agent gets notified on completion
const taskWorkflow = app.createWorkflow(
  'autonomousTask',
  'Multi-step task processor for autonomous agents',
  {
    // Step 1: Initialize and validate the task
    begin: async function (state, goto) {
      console.log('Starting workflow for task:', state.taskId);
      const conn = await Datastore.open();

      const task = await conn.findOneOrNull('tasks', state.taskId);
      if (!task) {
        state.error = 'Task not found';
        goto('failed', state);
        return;
      }

      await conn.updateOne('tasks', state.taskId, {
        $set: { status: 'processing', startedAt: new Date() }
      });

      state.task = task;
      state.attempts = 0;
      goto('process', state);
    },

    // Step 2: Process the task (with retry logic)
    process: async function (state, goto) {
      state.attempts++;
      console.log(`Processing attempt ${state.attempts} for task:`, state.taskId);

      try {
        // Simulate task processing - replace with actual logic
        const result = await processTask(state.task);
        state.result = result;
        goto('complete', state);
      } catch (error) {
        state.lastError = error.message;

        if (state.attempts < 3) {
          console.log('Retrying after error:', error.message);
          goto('process', state); // Retry
        } else {
          goto('failed', state);
        }
      }
    },

    // Step 3a: Task completed successfully
    complete: async function (state, goto) {
      const conn = await Datastore.open();
      await conn.updateOne('tasks', state.taskId, {
        $set: {
          status: 'completed',
          result: state.result,
          completedAt: new Date()
        }
      });

      state.finalStatus = 'completed';
      goto(null, state); // End workflow
    },

    // Step 3b: Task failed after retries
    failed: async function (state, goto) {
      const conn = await Datastore.open();
      await conn.updateOne('tasks', state.taskId, {
        $set: {
          status: 'failed',
          error: state.error || state.lastError,
          failedAt: new Date(),
          attempts: state.attempts
        }
      });

      state.finalStatus = 'failed';
      goto(null, state); // End workflow
    }
  },
  {
    collectionName: 'workflow_state',
    timeout: 60000,
    maxStepCount: 10,
    workers: 3,
    steps: {
      process: {
        timeout: 30000,
        maxRetries: 3
      }
    }
  }
);

// Notify when workflow completes - agent can poll or receive webhook
taskWorkflow.on('completed', async (data) => {
  console.log('Workflow completed:', data);

  // Optionally notify the agent via webhook callback
  if (data.state?.callbackUrl) {
    try {
      await fetch(data.state.callbackUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflowId: data.workflowId,
          status: data.state.finalStatus,
          result: data.state.result
        })
      });
    } catch (err) {
      console.error('Callback failed:', err.message);
    }
  }
});

// Helper function - replace with actual task logic
async function processTask(task) {
  // Simulate async work
  await new Promise(resolve => setTimeout(resolve, 1000));
  return { processed: true, data: task.data };
}

// API: Start a new workflow
app.post('/workflow/start', async (req, res) => {
  const conn = await Datastore.open();

  // Create the task
  const task = await conn.insertOne('tasks', {
    ...req.body,
    status: 'pending',
    createdAt: new Date()
  });

  // Start the workflow
  const workflow = await taskWorkflow.start({
    taskId: task._id,
    callbackUrl: req.body.callbackUrl // Optional: agent's webhook URL
  });

  res.json({
    taskId: task._id,
    workflowId: workflow._id,
    status: 'started'
  });
});

// API: Check workflow/task status
app.get('/workflow/status/:taskId', async (req, res) => {
  const conn = await Datastore.open();
  const task = await conn.findOneOrNull('tasks', req.params.taskId);

  if (!task) {
    return res.status(404).json({ error: 'Task not found' });
  }

  res.json(task);
});

export default app.init();
