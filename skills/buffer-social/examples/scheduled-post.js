import { BufferApi } from '../lib/buffer-api.js';

const api = new BufferApi({
  apiKey: process.env.BUFFER_API_KEY,
  apiUrl: process.env.BUFFER_API_URL || 'https://api.buffer.com/graphql',
});

const post = await api.createPost({
  text: 'Scheduled post example',
  profileIds: ['your-profile-id'],
  scheduledAt: new Date(Date.now() + 60 * 60 * 1000).toISOString(),
  queue: false,
});

console.log(post);
