import { describe, it, expect, vi, afterEach } from 'vitest';
import jwt from 'jsonwebtoken';
import { publishDraft } from '../ghostPublisher';

describe('publishDraft', () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it('generates valid Ghost JWT and posts draft payload', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        posts: [{ id: 'post_1', url: 'https://blog.example.com/p/post_1/' }],
      }),
    } as Response);
    global.fetch = fetchMock;

    const keyId = 'abcd1234';
    const hexSecret = '00112233445566778899aabbccddeeff';

    const result = await publishDraft(
      {
        url: 'https://blog.example.com/',
        adminKey: `${keyId}:${hexSecret}`,
      },
      'Digest title',
      '<h1>Hello</h1>',
      [{ name: 'security' }],
      'excerpt'
    );

    expect(result.success).toBe(true);
    expect(result.postId).toBe('post_1');

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, options] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('https://blog.example.com/ghost/api/admin/posts/?source=html');
    expect(options.method).toBe('POST');

    const auth = (options.headers as Record<string, string>).Authorization;
    expect(auth.startsWith('Ghost ')).toBe(true);

    const token = auth.replace('Ghost ', '');
    const decoded = jwt.verify(token, Buffer.from(hexSecret, 'hex'), {
      algorithms: ['HS256'],
      audience: '/admin/',
    }) as jwt.JwtPayload;

    expect(decoded.aud).toBe('/admin/');

    const decodedComplete = jwt.decode(token, { complete: true }) as {
      header: { kid: string };
    };
    expect(decodedComplete.header.kid).toBe(keyId);

    const body = JSON.parse(options.body as string) as { posts: Array<{ title: string; status: string; custom_excerpt?: string }> };
    expect(body.posts[0].title).toBe('Digest title');
    expect(body.posts[0].status).toBe('draft');
    expect(body.posts[0].custom_excerpt).toBe('excerpt');
  });

  it('fails gracefully when admin key format is invalid', async () => {
    const result = await publishDraft(
      {
        url: 'https://blog.example.com',
        adminKey: 'invalid-key',
      },
      'Title',
      '<p>Body</p>'
    );

    expect(result.success).toBe(false);
    expect(result.error).toContain('adminKey must be in format');
  });
});
