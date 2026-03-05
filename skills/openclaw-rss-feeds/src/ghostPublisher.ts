// @elvatis/openclaw-rss-feeds - Ghost Admin API draft publisher
import jwt from 'jsonwebtoken';
import type { GhostConfig } from './types';

// Generate a Ghost Admin API JWT token (valid for 5 minutes)
function makeGhostToken(adminKey: string): string {
  const colonIdx = adminKey.indexOf(':');
  if (colonIdx === -1) {
    throw new Error('Ghost adminKey must be in format "id:secret" (hex secret)');
  }

  const id = adminKey.substring(0, colonIdx);
  const hexSecret = adminKey.substring(colonIdx + 1);

  const secretBytes = Buffer.from(hexSecret, 'hex');
  const now = Math.floor(Date.now() / 1000);

  const token = jwt.sign(
    {
      iat: now,
      exp: now + 300,
      aud: '/admin/',
    },
    secretBytes,
    {
      algorithm: 'HS256',
      keyid: id,
    }
  );

  return token;
}

export interface GhostPublishResult {
  success: boolean;
  postId?: string;
  postUrl?: string;
  error?: string;
}

export interface GhostTag {
  name: string;
}

export async function publishDraft(
  config: GhostConfig,
  title: string,
  html: string,
  tags: GhostTag[] = [],
  customExcerpt?: string
): Promise<GhostPublishResult> {
  try {
    const token = makeGhostToken(config.adminKey);

    const ghostUrl = config.url.replace(/\/$/, '');
    const endpoint = `${ghostUrl}/ghost/api/admin/posts/?source=html`;

    const payload = {
      posts: [
        {
          title,
          html,
          status: 'draft' as const,
          tags,
          ...(customExcerpt ? { custom_excerpt: customExcerpt } : {}),
        },
      ],
    };

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        Authorization: `Ghost ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(15000),
    });

    if (!response.ok) {
      const errorBody = await response.text().catch(() => '(could not read response body)');
      const truncated = errorBody.substring(0, 500);
      return {
        success: false,
        error: `Ghost API returned ${response.status}: ${truncated}`,
      };
    }

    const data = (await response.json()) as {
      posts: Array<{
        id: string;
        url?: string;
      }>;
    };

    const post = data.posts[0];
    if (!post) {
      return {
        success: false,
        error: 'Ghost API returned empty posts array',
      };
    }

    return {
      success: true,
      postId: post.id,
      postUrl: post.url ?? `${ghostUrl}/ghost/#/posts`,
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return {
      success: false,
      error: `Ghost publish failed: ${message}`,
    };
  }
}
