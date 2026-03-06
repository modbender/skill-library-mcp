import { app, Datastore } from 'codehooks-js';

// Run daily at 9am
app.job('0 9 * * *', async (_, { jobId }) => {
  console.log(`Running daily summary job: ${jobId}`);
  const conn = await Datastore.open();
  const events = await conn.getMany('events', {}).toArray();
  console.log('Daily summary:', events.length, 'events');
});

export default app.init();
