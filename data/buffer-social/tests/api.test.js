import { describe, it, expect, vi } from 'vitest';
import {
  BufferApi,
  CREATE_POST_MUTATION,
  GET_SCHEDULED_POSTS_QUERY,
  CREATE_IDEA_MUTATION,
  GET_IDEAS_QUERY,
} from '../lib/buffer-api.js';

describe('BufferApi', () => {
  it('returns profiles from GraphQL response', async () => {
    const post = vi.fn().mockResolvedValue({
      data: {
        data: {
          profiles: [{ id: 'p1', service: 'twitter', username: 'learnopenclaw' }],
        },
      },
    });

    const api = new BufferApi(
      { apiKey: 'valid_api_key_12345', apiUrl: 'https://api.buffer.com/graphql' },
      { post }
    );

    const profiles = await api.getProfiles();
    expect(profiles).toHaveLength(1);
    expect(profiles[0].id).toBe('p1');
  });

  it('creates a post with GraphQL mutation', async () => {
    const post = vi.fn().mockResolvedValue({
      data: {
        data: {
          createPost: {
            id: 'post_123',
            text: 'Hello Buffer',
            scheduledAt: '2026-03-03T14:00:00Z',
            profiles: [{ id: 'p1', service: 'twitter' }],
          },
        },
      },
    });

    const api = new BufferApi(
      { apiKey: 'valid_api_key_12345', apiUrl: 'https://api.buffer.com/graphql' },
      { post }
    );

    const input = { text: 'Hello Buffer', profileIds: ['p1'] };
    const result = await api.createPost(input);

    expect(result.id).toBe('post_123');
    expect(post).toHaveBeenCalledWith('', {
      query: CREATE_POST_MUTATION,
      variables: { input },
    });
  });

  it('gets scheduled posts with optional profileId filter', async () => {
    const post = vi.fn().mockResolvedValue({
      data: {
        data: {
          scheduledPosts: [
            {
              id: 'sched_1',
              text: 'Upcoming launch update',
              scheduledAt: '2026-03-04T09:00:00Z',
              profiles: [{ service: 'twitter', username: 'learnopenclaw' }],
            },
          ],
        },
      },
    });

    const api = new BufferApi(
      { apiKey: 'valid_api_key_12345', apiUrl: 'https://api.buffer.com/graphql' },
      { post }
    );

    const result = await api.getScheduledPosts('profile_1');
    expect(result).toHaveLength(1);
    expect(post).toHaveBeenCalledWith('', {
      query: GET_SCHEDULED_POSTS_QUERY,
      variables: { profileId: 'profile_1' },
    });
  });

  it('creates an idea with GraphQL mutation', async () => {
    const post = vi.fn().mockResolvedValue({
      data: {
        data: {
          createIdea: {
            id: 'idea_123',
            text: 'Draft post idea',
          },
        },
      },
    });

    const api = new BufferApi(
      { apiKey: 'valid_api_key_12345', apiUrl: 'https://api.buffer.com/graphql' },
      { post }
    );

    const input = { text: 'Draft post idea', profileIds: ['p1'] };
    const result = await api.createIdea(input);

    expect(result.id).toBe('idea_123');
    expect(post).toHaveBeenCalledWith('', {
      query: CREATE_IDEA_MUTATION,
      variables: { input },
    });
  });

  it('gets ideas list', async () => {
    const post = vi.fn().mockResolvedValue({
      data: {
        data: {
          ideas: [{ id: 'idea_1', text: 'Ship launch post', createdAt: '2026-03-02T22:00:00Z' }],
        },
      },
    });

    const api = new BufferApi(
      { apiKey: 'valid_api_key_12345', apiUrl: 'https://api.buffer.com/graphql' },
      { post }
    );

    const result = await api.getIdeas();
    expect(result).toHaveLength(1);
    expect(post).toHaveBeenCalledWith('', {
      query: GET_IDEAS_QUERY,
      variables: {},
    });
  });

  it('maps 401/403 to auth-friendly error', async () => {
    const post = vi.fn().mockRejectedValue({
      message: 'Request failed with status code 401',
      response: { status: 401 },
    });

    const api = new BufferApi(
      { apiKey: 'bad_key_12345', apiUrl: 'https://api.buffer.com/graphql' },
      { post }
    );

    await expect(api.getProfiles()).rejects.toThrow(/Authentication failed/);
    await expect(api.getProfiles()).rejects.toThrow(/Fix:/);
  });

  it('maps 429 to rate-limit error with retry guidance', async () => {
    const post = vi.fn().mockRejectedValue({
      message: 'Request failed with status code 429',
      response: { status: 429 },
    });
    const api = new BufferApi(
      { apiKey: 'key_1234567890', apiUrl: 'https://api.buffer.com/graphql' },
      { post }
    );

    await expect(api.getProfiles()).rejects.toThrow(/Rate limit exceeded/);
    await expect(api.getProfiles()).rejects.toThrow(/Wait about 60 seconds/);
  });

  it('maps generic network error to actionable message', async () => {
    const post = vi.fn().mockRejectedValue({ message: 'connect ETIMEDOUT' });
    const api = new BufferApi(
      { apiKey: 'key_1234567890', apiUrl: 'https://api.buffer.com/graphql' },
      { post }
    );

    await expect(api.getProfiles()).rejects.toThrow(/network call/);
    await expect(api.getProfiles()).rejects.toThrow(/Check internet connectivity/);
  });

  it('maps GraphQL errors to actionable validation guidance', async () => {
    const post = vi.fn().mockResolvedValue({
      data: {
        errors: [{ message: 'Validation failed: profileIds is required' }],
      },
    });
    const api = new BufferApi(
      { apiKey: 'key_1234567890', apiUrl: 'https://api.buffer.com/graphql' },
      { post }
    );

    await expect(api.createPost({ text: 'hello', profileIds: [] })).rejects.toThrow(
      /Buffer GraphQL request/
    );
    await expect(api.createPost({ text: 'hello', profileIds: [] })).rejects.toThrow(
      /Verify your input values/
    );
  });

  it('maps non-auth HTTP errors with retry guidance', async () => {
    const post = vi.fn().mockRejectedValue({
      message: 'Request failed with status code 500',
      response: { status: 500 },
    });
    const api = new BufferApi(
      { apiKey: 'key_1234567890', apiUrl: 'https://api.buffer.com/graphql' },
      { post }
    );

    await expect(api.getProfiles()).rejects.toThrow(/Buffer API request \(500\)/);
    await expect(api.getProfiles()).rejects.toThrow(/Retry in a moment/);
  });
});
