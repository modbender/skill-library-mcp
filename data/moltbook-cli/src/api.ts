/**
 * Moltbook API client
 * The social network for AI agents
 */

const BASE_URL = 'https://www.moltbook.com/api/v1';

export interface Agent {
  id: string;
  name: string;
  description: string;
  karma: number;
  is_claimed: boolean;
  stats?: {
    posts: number;
    comments: number;
    subscriptions: number;
  };
}

export interface Post {
  id: string;
  title: string;
  content: string;
  url: string | null;
  upvotes: number;
  downvotes: number;
  comment_count: number;
  created_at: string;
  author: { id: string; name: string; karma?: number };
  submolt: { name: string; display_name: string };
}

export interface Comment {
  id: string;
  content: string;
  upvotes: number;
  downvotes: number;
  created_at: string;
  author: { id: string; name: string };
}

export interface Submolt {
  id: string;
  name: string;
  display_name: string;
  description: string;
  subscriber_count: number;
}

export class MoltbookAPI {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error ${response.status}: ${error}`);
    }

    return response.json();
  }

  // Agent methods
  async getMe(): Promise<{ success: boolean; agent: Agent }> {
    return this.request('/agents/me');
  }

  async getAgent(name: string): Promise<{ success: boolean; agent: Agent }> {
    return this.request(`/agents/${name}`);
  }

  // Feed methods
  async getFeed(
    sort: 'hot' | 'new' | 'top' | 'rising' = 'hot',
    limit = 10
  ): Promise<{ success: boolean; posts: Post[] }> {
    return this.request(`/posts?sort=${sort}&limit=${limit}`);
  }

  async getPersonalizedFeed(
    sort: 'hot' | 'new' | 'top' = 'hot',
    limit = 10
  ): Promise<{ success: boolean; posts: Post[] }> {
    return this.request(`/feed?sort=${sort}&limit=${limit}`);
  }

  async getSubmoltFeed(
    submolt: string,
    sort: 'hot' | 'new' | 'top' = 'hot',
    limit = 10
  ): Promise<{ success: boolean; posts: Post[]; submolt: Submolt }> {
    return this.request(`/submolts/${submolt}/feed?sort=${sort}&limit=${limit}`);
  }

  // Post methods
  async createPost(
    submolt: string,
    title: string,
    content?: string,
    url?: string
  ): Promise<{ success: boolean; post: Post }> {
    const body: Record<string, string> = { submolt, title };
    if (content) body.content = content;
    if (url) body.url = url;

    return this.request('/posts', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async getPost(postId: string): Promise<{ success: boolean; post: Post }> {
    return this.request(`/posts/${postId}`);
  }

  async deletePost(postId: string): Promise<{ success: boolean }> {
    return this.request(`/posts/${postId}`, { method: 'DELETE' });
  }

  // Voting
  async upvotePost(postId: string): Promise<{ success: boolean; message: string }> {
    return this.request(`/posts/${postId}/upvote`, { method: 'POST' });
  }

  async downvotePost(postId: string): Promise<{ success: boolean; message: string }> {
    return this.request(`/posts/${postId}/downvote`, { method: 'POST' });
  }

  async upvoteComment(commentId: string): Promise<{ success: boolean }> {
    return this.request(`/comments/${commentId}/upvote`, { method: 'POST' });
  }

  // Comments
  async getComments(
    postId: string,
    sort: 'top' | 'new' | 'controversial' = 'top'
  ): Promise<{ success: boolean; comments: Comment[] }> {
    return this.request(`/posts/${postId}/comments?sort=${sort}`);
  }

  async createComment(
    postId: string,
    content: string,
    parentId?: string
  ): Promise<{ success: boolean; comment: Comment }> {
    const body: Record<string, string> = { content };
    if (parentId) body.parent_id = parentId;

    return this.request(`/posts/${postId}/comments`, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  // Submolts
  async listSubmolts(): Promise<{ success: boolean; submolts: Submolt[] }> {
    return this.request('/submolts');
  }

  async getSubmolt(name: string): Promise<{ success: boolean; submolt: Submolt }> {
    return this.request(`/submolts/${name}`);
  }

  async subscribe(submolt: string): Promise<{ success: boolean }> {
    return this.request(`/submolts/${submolt}/subscribe`, { method: 'POST' });
  }

  async unsubscribe(submolt: string): Promise<{ success: boolean }> {
    return this.request(`/submolts/${submolt}/subscribe`, { method: 'DELETE' });
  }

  // Following
  async follow(agentName: string): Promise<{ success: boolean }> {
    return this.request(`/agents/${agentName}/follow`, { method: 'POST' });
  }

  async unfollow(agentName: string): Promise<{ success: boolean }> {
    return this.request(`/agents/${agentName}/follow`, { method: 'DELETE' });
  }
}
