/* ─── Database Adapter Interface ─── */

export interface Post {
    id: string;
    title: string;
    slug: string;
    content: string;
    excerpt: string;
    coverImage: string;
    tags: string[];
    status: "draft" | "published";
    authorName: string;
    viewCount: number;
    createdAt: Date;
    updatedAt: Date;
}

export interface CreatePostInput {
    title: string;
    slug: string;
    content: string;
    excerpt?: string;
    coverImage?: string;
    tags?: string[];
    status?: "draft" | "published";
    /** Required — the agent must identify itself as the author */
    authorName: string;
}

export interface UpdatePostInput {
    title?: string;
    slug?: string;
    content?: string;
    excerpt?: string;
    coverImage?: string;
    tags?: string[];
    status?: "draft" | "published";
}

export interface ListOptions {
    page?: number;
    limit?: number;
    status?: "draft" | "published" | "all";
    tag?: string;
    search?: string;
    sortBy?: "createdAt" | "updatedAt" | "title" | "viewCount";
    sortOrder?: "asc" | "desc";
}

export interface PaginatedResult<T> {
    data: T[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
}

export interface Media {
    id: string;
    filename: string;
    url: string;
    mimeType: string;
    size: number;
    alt: string;
    createdAt: Date;
}

export interface MediaMeta {
    filename: string;
    mimeType: string;
    size: number;
    alt?: string;
}

export interface BlogSettings {
    blogName: string;
    blogDescription: string;
    activeTheme: string;
    postsPerPage: number;
    enableComments: boolean;
    socialLinks: Record<string, string>;
    customCss: string;
    metaKeywords: string[];
}

export interface Analytics {
    totalPosts: number;
    totalViews: number;
    totalDrafts: number;
    topPosts: Array<{ slug: string; title: string; viewCount: number }>;
    postsByMonth: Array<{ month: string; count: number }>;
}

export interface DateRange {
    from?: Date;
    to?: Date;
}

export interface AdminUser {
    email: string;
    password: string;
    name: string;
}

export interface AdminSession {
    id: string;
    email: string;
    name: string;
    token: string;
    expiresAt: Date;
}

export interface DatabaseAdapter {
    // Posts
    createPost(data: CreatePostInput): Promise<Post>;
    getPost(slug: string): Promise<Post | null>;
    getPostById(id: string): Promise<Post | null>;
    updatePost(id: string, data: UpdatePostInput): Promise<Post>;
    deletePost(id: string): Promise<void>;
    listPosts(opts?: ListOptions): Promise<PaginatedResult<Post>>;

    // Media
    saveMedia(buffer: Buffer, meta: MediaMeta): Promise<Media>;
    getMedia(id: string): Promise<Media | null>;
    deleteMedia(id: string): Promise<void>;
    listMedia(): Promise<Media[]>;

    // Settings
    getSettings(): Promise<BlogSettings>;
    updateSettings(data: Partial<BlogSettings>): Promise<BlogSettings>;

    // Analytics
    recordView(postSlug: string): Promise<void>;
    getAnalytics(range?: DateRange): Promise<Analytics>;

    // Auth
    validateApiKey(key: string): Promise<boolean>;
    getApiKeys(): Promise<string[]>;
    addApiKey(key: string): Promise<void>;
    removeApiKey(key: string): Promise<void>;
    createAdmin(data: AdminUser): Promise<void>;
    validateAdmin(
        email: string,
        password: string,
    ): Promise<AdminSession | null>;
    getAdminByToken(token: string): Promise<AdminSession | null>;

    // Lifecycle
    migrate(): Promise<void>;
    close(): Promise<void>;
}

/* ─── Default Blog Settings ─── */

export const DEFAULT_SETTINGS: BlogSettings = {
    blogName: "My Blog",
    blogDescription: "A blog powered by AI",
    activeTheme: "minimalism",
    postsPerPage: 10,
    enableComments: false,
    socialLinks: {},
    customCss: "",
    metaKeywords: [],
};
