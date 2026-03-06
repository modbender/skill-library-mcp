import { BufferApi } from '../lib/buffer-api.js';

const api = new BufferApi({
  apiKey: process.env.BUFFER_API_KEY,
  apiUrl: process.env.BUFFER_API_URL || 'https://api.buffer.com/graphql',
});

const post = await api.createPost({
  text: 'Image post example',
  profileIds: ['your-profile-id'],
  queue: false,
  // BLOCKED: Buffer GraphQL upload flow not fully documented in public beta docs.
  media: [{ filePath: './photo.jpg' }],
});

console.log(post);
