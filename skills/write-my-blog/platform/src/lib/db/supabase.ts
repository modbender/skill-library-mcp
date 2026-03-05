/**
 * Supabase Database Adapter
 *
 * Leverages Supabase's managed Postgres, Auth, Storage, and Realtime features.
 * Provides the richest feature set of all adapters.
 */

import { v4 as uuidv4 } from "uuid";
import bcrypt from "bcryptjs";
import type {
    DatabaseAdapter,
    Post,
    CreatePostInput,
    UpdatePostInput,
    ListOptions,
    PaginatedResult,
    Media,
    MediaMeta,
    BlogSettings,
    Analytics,
    DateRange,
    AdminUser,
    AdminSession,
} from "./adapter";
import { DEFAULT_SETTINGS } from "./adapter";

let createClient: any;

export class SupabaseAdapter implements DatabaseAdapter {
    private client: any;

    constructor(
        private supabaseUrl: string = process.env.SUPABASE_URL || "",
        private supabaseKey: string = process.env.SUPABASE_SERVICE_KEY || "",
    ) { }

    private async getClient() {
        if (!this.client) {
            try {
                const mod = await import("@supabase/supabase-js");
                createClient = mod.createClient;
                this.client = createClient(this.supabaseUrl, this.supabaseKey);
            } catch {
                throw new Error(
                    "@supabase/supabase-js not installed. Run: npm install @supabase/supabase-js",
                );
            }
        }
        return this.client;
    }

    async migrate(): Promise<void> {
        const client = await this.getClient();

        // Create tables via raw SQL (requires service key with DDL permissions)
        const { error } = await client.rpc("exec_sql", {
            query: `
        CREATE TABLE IF NOT EXISTS posts (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          title TEXT NOT NULL,
          slug TEXT UNIQUE NOT NULL,
          content TEXT NOT NULL DEFAULT '',
          excerpt TEXT DEFAULT '',
          cover_image TEXT DEFAULT '',
          tags JSONB DEFAULT '[]'::jsonb,
          status TEXT DEFAULT 'draft' CHECK(status IN ('draft','published')),
          author_name TEXT DEFAULT 'AI Agent',
          view_count INTEGER DEFAULT 0,
          created_at TIMESTAMPTZ DEFAULT NOW(),
          updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_posts_slug ON posts(slug);
        CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);

        CREATE TABLE IF NOT EXISTS media (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          filename TEXT NOT NULL,
          url TEXT NOT NULL,
          mime_type TEXT NOT NULL,
          size INTEGER NOT NULL,
          alt TEXT DEFAULT '',
          created_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS settings (
          key TEXT PRIMARY KEY,
          value JSONB NOT NULL
        );

        CREATE TABLE IF NOT EXISTS api_keys (
          key TEXT PRIMARY KEY,
          created_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS admins (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          email TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL,
          name TEXT NOT NULL,
          created_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS admin_sessions (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          admin_id UUID NOT NULL REFERENCES admins(id) ON DELETE CASCADE,
          token TEXT UNIQUE NOT NULL,
          expires_at TIMESTAMPTZ NOT NULL
        );

        -- Enable Row Level Security
        ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
        ALTER TABLE media ENABLE ROW LEVEL SECURITY;
        ALTER TABLE settings ENABLE ROW LEVEL SECURITY;

        -- Allow service role full access
        CREATE POLICY IF NOT EXISTS "service_all_posts" ON posts FOR ALL USING (true);
        CREATE POLICY IF NOT EXISTS "service_all_media" ON media FOR ALL USING (true);
        CREATE POLICY IF NOT EXISTS "service_all_settings" ON settings FOR ALL USING (true);

        -- Public read access for published posts
        CREATE POLICY IF NOT EXISTS "public_read_posts" ON posts FOR SELECT USING (status = 'published');
      `,
        });

        if (error) {
            // Tables might already exist or rpc might not exist; try direct table inserts
            console.warn("Migration via RPC failed, tables may already exist:", error.message);
        }

        // Insert default settings
        for (const [key, value] of Object.entries(DEFAULT_SETTINGS)) {
            await client
                .from("settings")
                .upsert({ key, value: JSON.stringify(value) }, { onConflict: "key" });
        }

        // Create storage bucket for media
        await client.storage.createBucket("blog-media", {
            public: true,
            fileSizeLimit: 10 * 1024 * 1024, // 10MB
        });
    }

    // ── Posts ───────────────────────────────────────────────────────

    async createPost(data: CreatePostInput): Promise<Post> {
        const client = await this.getClient();
        const { data: post, error } = await client
            .from("posts")
            .insert({
                title: data.title,
                slug: data.slug,
                content: data.content,
                excerpt: data.excerpt || "",
                cover_image: data.coverImage || "",
                tags: data.tags || [],
                status: data.status || "draft",
                author_name: data.authorName || "AI Agent",
            })
            .select()
            .single();

        if (error) throw new Error(`Failed to create post: ${error.message}`);
        return this.rowToPost(post);
    }

    async getPost(slug: string): Promise<Post | null> {
        const client = await this.getClient();
        const { data, error } = await client
            .from("posts")
            .select("*")
            .eq("slug", slug)
            .single();

        if (error || !data) return null;
        return this.rowToPost(data);
    }

    async getPostById(id: string): Promise<Post | null> {
        const client = await this.getClient();
        const { data, error } = await client
            .from("posts")
            .select("*")
            .eq("id", id)
            .single();

        if (error || !data) return null;
        return this.rowToPost(data);
    }

    async updatePost(id: string, data: UpdatePostInput): Promise<Post> {
        const client = await this.getClient();
        const updateData: any = { updated_at: new Date().toISOString() };

        if (data.title !== undefined) updateData.title = data.title;
        if (data.slug !== undefined) updateData.slug = data.slug;
        if (data.content !== undefined) updateData.content = data.content;
        if (data.excerpt !== undefined) updateData.excerpt = data.excerpt;
        if (data.coverImage !== undefined) updateData.cover_image = data.coverImage;
        if (data.tags !== undefined) updateData.tags = data.tags;
        if (data.status !== undefined) updateData.status = data.status;

        const { data: post, error } = await client
            .from("posts")
            .update(updateData)
            .eq("id", id)
            .select()
            .single();

        if (error) throw new Error(`Failed to update post: ${error.message}`);
        return this.rowToPost(post);
    }

    async deletePost(id: string): Promise<void> {
        const client = await this.getClient();
        await client.from("posts").delete().eq("id", id);
    }

    async listPosts(opts: ListOptions = {}): Promise<PaginatedResult<Post>> {
        const client = await this.getClient();
        const page = opts.page || 1;
        const limit = opts.limit || 10;
        const from = (page - 1) * limit;
        const to = from + limit - 1;

        let query = client.from("posts").select("*", { count: "exact" });

        if (opts.status && opts.status !== "all") {
            query = query.eq("status", opts.status);
        }
        if (opts.tag) {
            query = query.contains("tags", [opts.tag]);
        }
        if (opts.search) {
            query = query.or(`title.ilike.%${opts.search}%,content.ilike.%${opts.search}%`);
        }

        const sortBy = opts.sortBy || "createdAt";
        const sortOrder = opts.sortOrder || "desc";
        const columnMap: Record<string, string> = {
            createdAt: "created_at",
            updatedAt: "updated_at",
            title: "title",
            viewCount: "view_count",
        };

        query = query
            .order(columnMap[sortBy] || "created_at", { ascending: sortOrder === "asc" })
            .range(from, to);

        const { data, count, error } = await query;
        if (error) throw new Error(`Failed to list posts: ${error.message}`);

        return {
            data: (data || []).map((r: any) => this.rowToPost(r)),
            total: count || 0,
            page,
            limit,
            totalPages: Math.ceil((count || 0) / limit),
        };
    }

    // ── Media ──────────────────────────────────────────────────────

    async saveMedia(buffer: Buffer, meta: MediaMeta): Promise<Media> {
        const client = await this.getClient();
        const id = uuidv4();
        const ext = meta.filename.split(".").pop() || "bin";
        const storedPath = `${id}.${ext}`;

        // Upload to Supabase Storage
        const { error: uploadError } = await client.storage
            .from("blog-media")
            .upload(storedPath, buffer, { contentType: meta.mimeType });

        if (uploadError) throw new Error(`Upload failed: ${uploadError.message}`);

        const {
            data: { publicUrl },
        } = client.storage.from("blog-media").getPublicUrl(storedPath);

        const { data, error } = await client
            .from("media")
            .insert({
                id,
                filename: meta.filename,
                url: publicUrl,
                mime_type: meta.mimeType,
                size: meta.size,
                alt: meta.alt || "",
            })
            .select()
            .single();

        if (error) throw new Error(`Failed to save media record: ${error.message}`);

        return {
            id: data.id,
            filename: data.filename,
            url: data.url,
            mimeType: data.mime_type,
            size: data.size,
            alt: data.alt,
            createdAt: new Date(data.created_at),
        };
    }

    async getMedia(id: string): Promise<Media | null> {
        const client = await this.getClient();
        const { data } = await client.from("media").select("*").eq("id", id).single();
        if (!data) return null;
        return {
            id: data.id,
            filename: data.filename,
            url: data.url,
            mimeType: data.mime_type,
            size: data.size,
            alt: data.alt,
            createdAt: new Date(data.created_at),
        };
    }

    async deleteMedia(id: string): Promise<void> {
        const client = await this.getClient();
        const media = await this.getMedia(id);
        if (media) {
            const storedPath = media.url.split("/").pop();
            if (storedPath) {
                await client.storage.from("blog-media").remove([storedPath]);
            }
        }
        await client.from("media").delete().eq("id", id);
    }

    async listMedia(): Promise<Media[]> {
        const client = await this.getClient();
        const { data } = await client
            .from("media")
            .select("*")
            .order("created_at", { ascending: false });
        return (data || []).map((r: any) => ({
            id: r.id,
            filename: r.filename,
            url: r.url,
            mimeType: r.mime_type,
            size: r.size,
            alt: r.alt,
            createdAt: new Date(r.created_at),
        }));
    }

    // ── Settings ───────────────────────────────────────────────────

    async getSettings(): Promise<BlogSettings> {
        const client = await this.getClient();
        const { data } = await client.from("settings").select("key, value");
        const settings = { ...DEFAULT_SETTINGS } as any;
        for (const row of data || []) {
            try {
                settings[row.key] = JSON.parse(row.value);
            } catch {
                settings[row.key] = row.value;
            }
        }
        return settings as BlogSettings;
    }

    async updateSettings(data: Partial<BlogSettings>): Promise<BlogSettings> {
        const client = await this.getClient();
        for (const [key, value] of Object.entries(data)) {
            await client
                .from("settings")
                .upsert({ key, value: JSON.stringify(value) }, { onConflict: "key" });
        }
        return this.getSettings();
    }

    // ── Analytics ──────────────────────────────────────────────────

    async recordView(postSlug: string): Promise<void> {
        const client = await this.getClient();
        await client.rpc("increment_view_count", { post_slug: postSlug });
    }

    async getAnalytics(_range?: DateRange): Promise<Analytics> {
        const client = await this.getClient();

        const { count: totalPosts } = await client
            .from("posts")
            .select("*", { count: "exact", head: true })
            .eq("status", "published");

        const { count: totalDrafts } = await client
            .from("posts")
            .select("*", { count: "exact", head: true })
            .eq("status", "draft");

        const { data: viewData } = await client.rpc("get_total_views");
        const totalViews = viewData?.[0]?.total || 0;

        const { data: topPostsData } = await client
            .from("posts")
            .select("slug, title, view_count")
            .eq("status", "published")
            .order("view_count", { ascending: false })
            .limit(10);

        return {
            totalPosts: totalPosts || 0,
            totalDrafts: totalDrafts || 0,
            totalViews,
            topPosts: (topPostsData || []).map((r: any) => ({
                slug: r.slug,
                title: r.title,
                viewCount: r.view_count,
            })),
            postsByMonth: [],
        };
    }

    // ── Auth ───────────────────────────────────────────────────────

    async validateApiKey(key: string): Promise<boolean> {
        const client = await this.getClient();
        const { data } = await client.from("api_keys").select("key").eq("key", key).single();
        return !!data;
    }

    async getApiKeys(): Promise<string[]> {
        const client = await this.getClient();
        const { data } = await client.from("api_keys").select("key");
        return (data || []).map((r: any) => r.key);
    }

    async addApiKey(key: string): Promise<void> {
        const client = await this.getClient();
        await client.from("api_keys").upsert({ key }, { onConflict: "key" });
    }

    async removeApiKey(key: string): Promise<void> {
        const client = await this.getClient();
        await client.from("api_keys").delete().eq("key", key);
    }

    async createAdmin(data: AdminUser): Promise<void> {
        const client = await this.getClient();
        const passwordHash = await bcrypt.hash(data.password, 12);
        await client.from("admins").insert({
            email: data.email,
            password_hash: passwordHash,
            name: data.name,
        });
    }

    async validateAdmin(
        email: string,
        password: string,
    ): Promise<AdminSession | null> {
        const client = await this.getClient();
        const { data: admin } = await client
            .from("admins")
            .select("*")
            .eq("email", email)
            .single();

        if (!admin) return null;

        const valid = await bcrypt.compare(password, admin.password_hash);
        if (!valid) return null;

        const token = uuidv4();
        const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

        const { data: session } = await client
            .from("admin_sessions")
            .insert({
                admin_id: admin.id,
                token,
                expires_at: expiresAt.toISOString(),
            })
            .select()
            .single();

        return {
            id: session.id,
            email: admin.email,
            name: admin.name,
            token,
            expiresAt,
        };
    }

    async getAdminByToken(token: string): Promise<AdminSession | null> {
        const client = await this.getClient();
        const { data } = await client
            .from("admin_sessions")
            .select("*, admins(email, name)")
            .eq("token", token)
            .gt("expires_at", new Date().toISOString())
            .single();

        if (!data) return null;
        return {
            id: data.id,
            email: data.admins.email,
            name: data.admins.name,
            token: data.token,
            expiresAt: new Date(data.expires_at),
        };
    }

    // ── Helpers ────────────────────────────────────────────────────

    private rowToPost(row: any): Post {
        return {
            id: row.id,
            title: row.title,
            slug: row.slug,
            content: row.content,
            excerpt: row.excerpt,
            coverImage: row.cover_image,
            tags: Array.isArray(row.tags) ? row.tags : JSON.parse(row.tags || "[]"),
            status: row.status,
            authorName: row.author_name,
            viewCount: row.view_count,
            createdAt: new Date(row.created_at),
            updatedAt: new Date(row.updated_at),
        };
    }

    async close(): Promise<void> {
        // Supabase client doesn't need explicit close
    }
}
