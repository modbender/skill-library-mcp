import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import {
  createCli,
  formatProfiles,
  formatPostSuccess,
  formatQueuePosts,
  formatIdeas,
  formatIdeaSuccess,
} from '../buffer.js';

describe('buffer CLI', () => {
  let logSpy;
  let errSpy;

  beforeEach(() => {
    logSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    errSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('formats connected profiles output', () => {
    const output = formatProfiles([
      { id: 'abc123', service: 'Twitter', username: 'learnopenclaw' },
    ]);
    expect(output).toContain('Connected Profiles');
    expect(output).toContain('abc123');
    expect(output).toContain('Twitter');
  });

  it('executes profiles command', async () => {
    const getProfiles = vi
      .fn()
      .mockResolvedValue([{ id: '1', service: 'LinkedIn', username: 'ahmad' }]);
    const cli = createCli({ api: { getProfiles } });

    await cli.parseAsync(['node', 'buffer', 'profiles']);

    expect(getProfiles).toHaveBeenCalled();
    expect(logSpy).toHaveBeenCalledWith(expect.stringContaining('Connected Profiles'));
  });

  it('creates a post with --profile', async () => {
    const createPost = vi.fn().mockResolvedValue({
      id: 'post_1',
      text: 'Hello world',
      profiles: [{ service: 'twitter' }],
    });
    const cli = createCli({ api: { createPost } });

    await cli.parseAsync([
      'node',
      'buffer',
      'post',
      'Hello world',
      '--profile',
      'twitter_profile_id',
    ]);

    expect(createPost).toHaveBeenCalledWith({
      text: 'Hello world',
      profileIds: ['twitter_profile_id'],
      queue: false,
    });
    expect(logSpy).toHaveBeenCalledWith(expect.stringContaining('Post created successfully'));
  });

  it('creates a post with --profiles and --time', async () => {
    const createPost = vi.fn().mockResolvedValue({
      id: 'post_2',
      text: 'Scheduled',
      scheduledAt: '2026-03-03T14:00:00.000Z',
      profiles: [{ service: 'twitter' }, { service: 'linkedin' }],
    });
    const cli = createCli({ api: { createPost } });

    await cli.parseAsync([
      'node',
      'buffer',
      'post',
      'Scheduled',
      '--profiles',
      'twitter_id,linkedin_id',
      '--time',
      '2026-03-03T14:00:00Z',
    ]);

    expect(createPost).toHaveBeenCalledWith({
      text: 'Scheduled',
      profileIds: ['twitter_id', 'linkedin_id'],
      queue: false,
      scheduledAt: '2026-03-03T14:00:00.000Z',
    });
  });

  it('creates a post with --image when file exists', async () => {
    const dir = mkdtempSync(join(tmpdir(), 'buffer-cli-image-'));
    const imagePath = join(dir, 'photo.jpg');
    writeFileSync(imagePath, 'fake-image-bytes');

    const createPost = vi.fn().mockResolvedValue({
      id: 'post_22',
      text: 'With image',
      profiles: [{ service: 'twitter' }],
    });
    const cli = createCli({ api: { createPost } });

    await cli.parseAsync([
      'node',
      'buffer',
      'post',
      'With image',
      '--profile',
      'twitter_id',
      '--image',
      imagePath,
    ]);

    expect(createPost).toHaveBeenCalledWith({
      text: 'With image',
      profileIds: ['twitter_id'],
      queue: false,
      media: [{ filePath: imagePath }],
    });

    rmSync(dir, { recursive: true, force: true });
  });

  it('uses all connected profiles with --all', async () => {
    const getProfiles = vi.fn().mockResolvedValue([{ id: 'p1' }, { id: 'p2' }]);
    const createPost = vi
      .fn()
      .mockResolvedValue({ id: 'post_3', text: 'All profiles', profiles: [] });
    const cli = createCli({ api: { getProfiles, createPost } });

    await cli.parseAsync(['node', 'buffer', 'post', 'All profiles', '--all', '--queue']);

    expect(getProfiles).toHaveBeenCalled();
    expect(createPost).toHaveBeenCalledWith({
      text: 'All profiles',
      profileIds: ['p1', 'p2'],
      queue: true,
    });
  });

  it('executes queue command with profile + limit', async () => {
    const getScheduledPosts = vi.fn().mockResolvedValue([
      {
        id: 'sched_1',
        text: 'A scheduled post',
        scheduledAt: '2026-03-03T14:00:00.000Z',
        profiles: [{ service: 'Twitter', username: 'learnopenclaw' }],
      },
      {
        id: 'sched_2',
        text: 'Another scheduled post',
        scheduledAt: '2026-03-03T15:00:00.000Z',
        profiles: [{ service: 'LinkedIn', username: 'ahmad' }],
      },
    ]);

    const cli = createCli({ api: { getScheduledPosts } });
    await cli.parseAsync(['node', 'buffer', 'queue', '--profile', 'profile_1', '--limit', '1']);

    expect(getScheduledPosts).toHaveBeenCalledWith('profile_1');
    expect(logSpy).toHaveBeenCalledWith(expect.stringContaining('Upcoming Posts (1)'));
  });

  it('creates an idea when --draft is passed', async () => {
    const createIdea = vi.fn().mockResolvedValue({ id: 'idea_1', text: 'Draft idea' });
    const cli = createCli({ api: { createIdea } });

    await cli.parseAsync([
      'node',
      'buffer',
      'post',
      'Draft idea',
      '--profile',
      'twitter_profile_id',
      '--draft',
    ]);

    expect(createIdea).toHaveBeenCalledWith({
      text: 'Draft idea',
      profileIds: ['twitter_profile_id'],
    });
    expect(logSpy).toHaveBeenCalledWith(expect.stringContaining('Idea saved successfully'));
  });

  it('rejects conflicting post target options', async () => {
    const createPost = vi.fn();
    const cli = createCli({ api: { createPost } });

    await cli.parseAsync(['node', 'buffer', 'post', 'Hello', '--profile', 'p1', '--all']);

    expect(createPost).not.toHaveBeenCalled();
    expect(errSpy).toHaveBeenCalledWith(expect.stringContaining('Choose only one target option'));
  });

  it('rejects invalid schedule time for post command', async () => {
    const createPost = vi.fn();
    const cli = createCli({ api: { createPost } });

    await cli.parseAsync([
      'node',
      'buffer',
      'post',
      'Hello',
      '--profile',
      'p1',
      '--time',
      'not-a-date',
    ]);

    expect(createPost).not.toHaveBeenCalled();
    expect(errSpy).toHaveBeenCalledWith(expect.stringContaining('Invalid schedule time'));
  });

  it('rejects non-positive queue limit', async () => {
    const getScheduledPosts = vi.fn().mockResolvedValue([]);
    const cli = createCli({ api: { getScheduledPosts } });

    await cli.parseAsync(['node', 'buffer', 'queue', '--limit', '0']);

    expect(errSpy).toHaveBeenCalledWith(expect.stringContaining('Invalid --limit value'));
  });

  it('executes ideas command with limit', async () => {
    const getIdeas = vi.fn().mockResolvedValue([
      { id: 'idea_1', text: 'Idea one', createdAt: '2026-03-02T12:00:00.000Z' },
      { id: 'idea_2', text: 'Idea two', createdAt: '2026-03-02T13:00:00.000Z' },
    ]);
    const cli = createCli({ api: { getIdeas } });

    await cli.parseAsync(['node', 'buffer', 'ideas', '--limit', '1']);

    expect(getIdeas).toHaveBeenCalled();
    expect(logSpy).toHaveBeenCalledWith(expect.stringContaining('Saved Ideas (1)'));
  });

  it('formats queue output', () => {
    const output = formatQueuePosts([
      {
        text: 'This is a long scheduled post that should be rendered cleanly in output',
        scheduledAt: '2026-03-03T14:00:00.000Z',
        profiles: [{ service: 'Twitter' }, { service: 'LinkedIn' }],
      },
    ]);

    expect(output).toContain('Upcoming Posts (1)');
    expect(output).toContain('Twitter, LinkedIn');
    expect(output).toContain('Scheduled:');
  });

  it('formats post success output', () => {
    const output = formatPostSuccess({
      id: 'post_123',
      text: 'Hello Buffer',
      scheduledAt: '2026-03-03T14:00:00.000Z',
      profiles: [{ service: 'Twitter' }],
    });

    expect(output).toContain('Post created successfully');
    expect(output).toContain('post_123');
    expect(output).toContain('Twitter');
    expect(output).toContain('Next step: Run "buffer queue --limit 5"');
  });

  it('formats idea success output', () => {
    const output = formatIdeaSuccess({ id: 'idea_123', text: 'Ship weekly update post' });

    expect(output).toContain('Idea saved successfully');
    expect(output).toContain('idea_123');
    expect(output).toContain('Next step: Use "buffer ideas --limit 10"');
  });

  it('formats ideas output', () => {
    const output = formatIdeas([
      { id: 'idea_1', text: 'New campaign concept', createdAt: '2026-03-02T10:00:00.000Z' },
    ]);

    expect(output).toContain('Saved Ideas (1)');
    expect(output).toContain('New campaign concept');
  });

  it('runs end-to-end workflow across profiles, post, queue, draft, and ideas', async () => {
    const api = {
      getProfiles: vi
        .fn()
        .mockResolvedValueOnce([{ id: 'p1', service: 'Twitter', username: 'learnopenclaw' }])
        .mockResolvedValueOnce([{ id: 'p1', service: 'Twitter', username: 'learnopenclaw' }]),
      createPost: vi.fn().mockResolvedValue({
        id: 'post_e2e_1',
        text: 'Ship it',
        profiles: [{ service: 'Twitter' }],
      }),
      getScheduledPosts: vi.fn().mockResolvedValue([
        {
          id: 'sched_e2e_1',
          text: 'Ship it',
          scheduledAt: '2026-03-03T14:00:00.000Z',
          profiles: [{ service: 'Twitter', username: 'learnopenclaw' }],
        },
      ]),
      createIdea: vi.fn().mockResolvedValue({ id: 'idea_e2e_1', text: 'Future campaign' }),
      getIdeas: vi
        .fn()
        .mockResolvedValue([
          { id: 'idea_e2e_1', text: 'Future campaign', createdAt: '2026-03-02T10:00:00.000Z' },
        ]),
    };

    await createCli({ api }).parseAsync(['node', 'buffer', 'profiles']);
    await createCli({ api }).parseAsync(['node', 'buffer', 'post', 'Ship it', '--all']);
    await createCli({ api }).parseAsync(['node', 'buffer', 'queue', '--limit', '1']);
    await createCli({ api }).parseAsync([
      'node',
      'buffer',
      'post',
      'Future campaign',
      '--profile',
      'p1',
      '--draft',
    ]);
    await createCli({ api }).parseAsync(['node', 'buffer', 'ideas', '--limit', '1']);

    expect(api.getProfiles).toHaveBeenCalledTimes(2);
    expect(api.createPost).toHaveBeenCalledWith({
      text: 'Ship it',
      profileIds: ['p1'],
      queue: false,
    });
    expect(api.getScheduledPosts).toHaveBeenCalledWith(undefined);
    expect(api.createIdea).toHaveBeenCalledWith({ text: 'Future campaign', profileIds: ['p1'] });
    expect(api.getIdeas).toHaveBeenCalledTimes(1);
    expect(logSpy).toHaveBeenCalledWith(expect.stringContaining('Connected Profiles'));
    expect(logSpy).toHaveBeenCalledWith(expect.stringContaining('Post created successfully'));
    expect(logSpy).toHaveBeenCalledWith(expect.stringContaining('Upcoming Posts (1)'));
    expect(logSpy).toHaveBeenCalledWith(expect.stringContaining('Idea saved successfully'));
    expect(logSpy).toHaveBeenCalledWith(expect.stringContaining('Saved Ideas (1)'));
  });
});
