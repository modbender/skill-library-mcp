import { BufferApi } from '../lib/buffer-api.js';

const api = new BufferApi({
  apiKey: process.env.BUFFER_API_KEY,
  apiUrl: process.env.BUFFER_API_URL || 'https://api.buffer.com/graphql',
});

const post = await api.createPost({
  text: 'Multi-channel Buffer example',
  profileIds: ['profile-1', 'profile-2'],
  queue: true,
});

console.log(post);
