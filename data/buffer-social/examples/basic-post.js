import { BufferApi } from '../lib/buffer-api.js';

const api = new BufferApi({
  apiKey: process.env.BUFFER_API_KEY,
  apiUrl: process.env.BUFFER_API_URL || 'https://api.buffer.com/graphql',
});

const post = await api.createPost({
  text: 'Hello from Buffer basic example',
  profileIds: ['your-profile-id'],
  queue: false,
});

console.log(post);
