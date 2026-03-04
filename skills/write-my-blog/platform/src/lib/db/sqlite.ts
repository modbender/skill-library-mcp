/**
 * SQLite Database Adapter
 *
 * Works with both local SQLite (via better-sqlite3) and Cloudflare D1.
 * This is the default adapter for development and the Cloudflare deployment target.
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
    DEFAULT_SETTINGS,
} from "./adapter";
import { DEFAULT_SETTINGS as DEFAULTS } from "./adapter";
import path from "path";
import fs from "fs";

// We use dynamic import so this file only loads better-sqlite3 when actually used
let Database: any;

interface SQLiteDB {
    prepare(sql: string): any;
    exec(sql: string): void;
    close(): void;
}

export class SQLiteAdapter implements DatabaseAdapter {
    private db!: SQLiteDB;
    private mediaDir: string;

    constructor(
        private dbPath: string = "./data/blog.db",
        mediaBaseDir: string = "./public/uploads",
    ) {
        this.mediaDir = mediaBaseDir;
    }

    private async getDb(): Promise<SQLiteDB> {
        if (!this.db) {
            try {
                const BetterSqlite3 = (await import("better-sqlite3")).default;
                const dir = path.dirname(this.dbPath);
                if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
                this.db = new BetterSqlite3(this.dbPath);
                (this.db as any).pragma("journal_mode = WAL");
                (this.db as any).pragma("foreign_keys = ON");
            } catch {
                throw new Error(
                    "better-sqlite3 not installed. Run: npm install better-sqlite3",
                );
            }
        }
        return this.db;
    }

    async migrate(): Promise<void> {
        const db = await this.getDb();
        db.exec(`
      CREATE TABLE IF NOT EXISTS posts (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        content TEXT NOT NULL DEFAULT '',
        excerpt TEXT DEFAULT '',
        cover_image TEXT DEFAULT '',
        tags TEXT DEFAULT '[]',
        status TEXT DEFAULT 'draft' CHECK(status IN ('draft','published')),
        author_name TEXT DEFAULT 'AI Agent',
        view_count INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
      );
      CREATE INDEX IF NOT EXISTS idx_posts_slug ON posts(slug);
      CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
      CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at);

      CREATE TABLE IF NOT EXISTS media (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        url TEXT NOT NULL,
        mime_type TEXT NOT NULL,
        size INTEGER NOT NULL,
        alt TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
      );

      CREATE TABLE IF NOT EXISTS api_keys (
        key TEXT PRIMARY KEY,
        created_at TEXT DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS admins (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS admin_sessions (
        id TEXT PRIMARY KEY,
        admin_id TEXT NOT NULL,
        token TEXT UNIQUE NOT NULL,
        expires_at TEXT NOT NULL,
        FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE CASCADE
      );
    `);

        // Insert default settings if none exist
        const existing = db.prepare("SELECT COUNT(*) as count FROM settings").get() as any;
        if (existing.count === 0) {
            const stmt = db.prepare("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)");
            for (const [key, value] of Object.entries(DEFAULTS)) {
                stmt.run(key, JSON.stringify(value));
            }
        }

        // Ensure media directory exists
        if (!fs.existsSync(this.mediaDir)) {
            fs.mkdirSync(this.mediaDir, { recursive: true });
        }
    }

    // ── Posts ───────────────────────────────────────────────────────

    async createPost(data: CreatePostInput): Promise<Post> {
        const db = await this.getDb();
        const id = uuidv4();
        const now = new Date().toISOString();

        db.prepare(`
      INSERT INTO posts (id, title, slug, content, excerpt, cover_image, tags, status, author_name, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
            id,
            data.title,
            data.slug,
            data.content,
            data.excerpt || "",
            data.coverImage || "",
            JSON.stringify(data.tags || []),
            data.status || "draft",
            data.authorName || "AI Agent",
            now,
            now,
        );

        return this.getPostById(id) as Promise<Post>;
    }

    async getPost(slug: string): Promise<Post | null> {
        const db = await this.getDb();
        const row = db.prepare("SELECT * FROM posts WHERE slug = ?").get(slug) as any;
        return row ? this.rowToPost(row) : null;
    }

    async getPostById(id: string): Promise<Post | null> {
        const db = await this.getDb();
        const row = db.prepare("SELECT * FROM posts WHERE id = ?").get(id) as any;
        return row ? this.rowToPost(row) : null;
    }

    async updatePost(id: string, data: UpdatePostInput): Promise<Post> {
        const db = await this.getDb();
        const fields: string[] = [];
        const values: any[] = [];

        if (data.title !== undefined) { fields.push("title = ?"); values.push(data.title); }
        if (data.slug !== undefined) { fields.push("slug = ?"); values.push(data.slug); }
        if (data.content !== undefined) { fields.push("content = ?"); values.push(data.content); }
        if (data.excerpt !== undefined) { fields.push("excerpt = ?"); values.push(data.excerpt); }
        if (data.coverImage !== undefined) { fields.push("cover_image = ?"); values.push(data.coverImage); }
        if (data.tags !== undefined) { fields.push("tags = ?"); values.push(JSON.stringify(data.tags)); }
        if (data.status !== undefined) { fields.push("status = ?"); values.push(data.status); }

        fields.push("updated_at = ?");
        values.push(new Date().toISOString());
        values.push(id);

        db.prepare(`UPDATE posts SET ${fields.join(", ")} WHERE id = ?`).run(...values);
        return this.getPostById(id) as Promise<Post>;
    }

    async deletePost(id: string): Promise<void> {
        const db = await this.getDb();
        db.prepare("DELETE FROM posts WHERE id = ?").run(id);
    }

    async listPosts(opts: ListOptions = {}): Promise<PaginatedResult<Post>> {
        const db = await this.getDb();
        const page = opts.page || 1;
        const limit = opts.limit || 10;
        const offset = (page - 1) * limit;

        let whereClause = "WHERE 1=1";
        const params: any[] = [];

        if (opts.status && opts.status !== "all") {
            whereClause += " AND status = ?";
            params.push(opts.status);
        }
        if (opts.tag) {
            whereClause += " AND tags LIKE ?";
            params.push(`%"${opts.tag}"%`);
        }
        if (opts.search) {
            whereClause += " AND (title LIKE ? OR content LIKE ?)";
            params.push(`%${opts.search}%`, `%${opts.search}%`);
        }

        const sortBy = opts.sortBy || "createdAt";
        const sortOrder = opts.sortOrder || "desc";
        const columnMap: Record<string, string> = {
            createdAt: "created_at",
            updatedAt: "updated_at",
            title: "title",
            viewCount: "view_count",
        };
        const orderColumn = columnMap[sortBy] || "created_at";

        const totalRow = db
            .prepare(`SELECT COUNT(*) as count FROM posts ${whereClause}`)
            .get(...params) as any;
        const total = totalRow.count;

        const rows = db
            .prepare(
                `SELECT * FROM posts ${whereClause} ORDER BY ${orderColumn} ${sortOrder} LIMIT ? OFFSET ?`,
            )
            .all(...params, limit, offset) as any[];

        return {
            data: rows.map((r: any) => this.rowToPost(r)),
            total,
            page,
            limit,
            totalPages: Math.ceil(total / limit),
        };
    }

    // ── Media ──────────────────────────────────────────────────────

    async saveMedia(buffer: Buffer, meta: MediaMeta): Promise<Media> {
        const db = await this.getDb();
        const id = uuidv4();
        const ext = path.extname(meta.filename);
        const storedFilename = `${id}${ext}`;
        const filePath = path.join(this.mediaDir, storedFilename);

        fs.writeFileSync(filePath, buffer);
        const url = `/uploads/${storedFilename}`;

        db.prepare(`
      INSERT INTO media (id, filename, url, mime_type, size, alt)
      VALUES (?, ?, ?, ?, ?, ?)
    `).run(id, meta.filename, url, meta.mimeType, meta.size, meta.alt || "");

        return {
            id,
            filename: meta.filename,
            url,
            mimeType: meta.mimeType,
            size: meta.size,
            alt: meta.alt || "",
            createdAt: new Date(),
        };
    }

    async getMedia(id: string): Promise<Media | null> {
        const db = await this.getDb();
        const row = db.prepare("SELECT * FROM media WHERE id = ?").get(id) as any;
        if (!row) return null;
        return {
            id: row.id,
            filename: row.filename,
            url: row.url,
            mimeType: row.mime_type,
            size: row.size,
            alt: row.alt,
            createdAt: new Date(row.created_at),
        };
    }

    async deleteMedia(id: string): Promise<void> {
        const db = await this.getDb();
        const media = await this.getMedia(id);
        if (media) {
            const filePath = path.join(this.mediaDir, path.basename(media.url));
            if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
        }
        db.prepare("DELETE FROM media WHERE id = ?").run(id);
    }

    async listMedia(): Promise<Media[]> {
        const db = await this.getDb();
        const rows = db.prepare("SELECT * FROM media ORDER BY created_at DESC").all() as any[];
        return rows.map((r: any) => ({
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
        const db = await this.getDb();
        const rows = db.prepare("SELECT key, value FROM settings").all() as any[];
        const settings = { ...DEFAULTS } as any;
        for (const row of rows) {
            try {
                settings[row.key] = JSON.parse(row.value);
            } catch {
                settings[row.key] = row.value;
            }
        }
        return settings as BlogSettings;
    }

    async updateSettings(data: Partial<BlogSettings>): Promise<BlogSettings> {
        const db = await this.getDb();
        const stmt = db.prepare(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        );
        for (const [key, value] of Object.entries(data)) {
            stmt.run(key, JSON.stringify(value));
        }
        return this.getSettings();
    }

    // ── Analytics ──────────────────────────────────────────────────

    async recordView(postSlug: string): Promise<void> {
        const db = await this.getDb();
        db.prepare("UPDATE posts SET view_count = view_count + 1 WHERE slug = ?").run(
            postSlug,
        );
    }

    async getAnalytics(_range?: DateRange): Promise<Analytics> {
        const db = await this.getDb();

        const totalPosts = (
            db.prepare("SELECT COUNT(*) as c FROM posts WHERE status = 'published'").get() as any
        ).c;
        const totalDrafts = (
            db.prepare("SELECT COUNT(*) as c FROM posts WHERE status = 'draft'").get() as any
        ).c;
        const totalViews = (
            db.prepare("SELECT COALESCE(SUM(view_count), 0) as c FROM posts").get() as any
        ).c;

        const topPosts = db
            .prepare(
                "SELECT slug, title, view_count FROM posts WHERE status = 'published' ORDER BY view_count DESC LIMIT 10",
            )
            .all() as any[];

        const postsByMonth = db
            .prepare(
                "SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count FROM posts GROUP BY month ORDER BY month DESC LIMIT 12",
            )
            .all() as any[];

        return {
            totalPosts,
            totalDrafts,
            totalViews,
            topPosts: topPosts.map((r: any) => ({
                slug: r.slug,
                title: r.title,
                viewCount: r.view_count,
            })),
            postsByMonth: postsByMonth.map((r: any) => ({
                month: r.month,
                count: r.count,
            })),
        };
    }

    // ── Auth ───────────────────────────────────────────────────────

    async validateApiKey(key: string): Promise<boolean> {
        const db = await this.getDb();
        const row = db.prepare("SELECT key FROM api_keys WHERE key = ?").get(key) as any;
        return !!row;
    }

    async getApiKeys(): Promise<string[]> {
        const db = await this.getDb();
        const rows = db.prepare("SELECT key FROM api_keys").all() as any[];
        return rows.map((r: any) => r.key);
    }

    async addApiKey(key: string): Promise<void> {
        const db = await this.getDb();
        db.prepare("INSERT OR IGNORE INTO api_keys (key) VALUES (?)").run(key);
    }

    async removeApiKey(key: string): Promise<void> {
        const db = await this.getDb();
        db.prepare("DELETE FROM api_keys WHERE key = ?").run(key);
    }

    async createAdmin(data: AdminUser): Promise<void> {
        const db = await this.getDb();
        const id = uuidv4();
        const passwordHash = await bcrypt.hash(data.password, 12);
        db.prepare(
            "INSERT INTO admins (id, email, password_hash, name) VALUES (?, ?, ?, ?)",
        ).run(id, data.email, passwordHash, data.name);
    }

    async validateAdmin(
        email: string,
        password: string,
    ): Promise<AdminSession | null> {
        const db = await this.getDb();
        const admin = db
            .prepare("SELECT * FROM admins WHERE email = ?")
            .get(email) as any;
        if (!admin) return null;

        const valid = await bcrypt.compare(password, admin.password_hash);
        if (!valid) return null;

        const sessionId = uuidv4();
        const token = uuidv4();
        const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();

        db.prepare(
            "INSERT INTO admin_sessions (id, admin_id, token, expires_at) VALUES (?, ?, ?, ?)",
        ).run(sessionId, admin.id, token, expiresAt);

        return {
            id: sessionId,
            email: admin.email,
            name: admin.name,
            token,
            expiresAt: new Date(expiresAt),
        };
    }

    async getAdminByToken(token: string): Promise<AdminSession | null> {
        const db = await this.getDb();
        const row = db
            .prepare(
                `SELECT s.*, a.email, a.name FROM admin_sessions s
         JOIN admins a ON s.admin_id = a.id
         WHERE s.token = ? AND s.expires_at > datetime('now')`,
            )
            .get(token) as any;
        if (!row) return null;
        return {
            id: row.id,
            email: row.email,
            name: row.name,
            token: row.token,
            expiresAt: new Date(row.expires_at),
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
            tags: JSON.parse(row.tags || "[]"),
            status: row.status,
            authorName: row.author_name,
            viewCount: row.view_count,
            createdAt: new Date(row.created_at),
            updatedAt: new Date(row.updated_at),
        };
    }

    async close(): Promise<void> {
        if (this.db) {
            (this.db as any).close();
        }
    }
}
