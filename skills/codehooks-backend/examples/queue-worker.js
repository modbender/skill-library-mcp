import { app, Datastore } from 'codehooks-js';

app.worker('processTask', async (req, res) => {
  const { task } = req.body.payload;
  console.log('Processing task:', task.id);

  const conn = await Datastore.open();
  await conn.updateOne('tasks', { _id: task.id }, { $set: { status: 'completed' } });

  res.end();
});

// Endpoint to enqueue tasks
app.post('/tasks', async (req, res) => {
  const conn = await Datastore.open();
  const task = await conn.insertOne('tasks', {
    ...req.body,
    status: 'pending',
    createdAt: new Date()
  });
  await conn.enqueue('processTask', { task });
  res.json(task);
});

export default app.init();
