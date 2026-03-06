/**
 * MongoDB Database Adapter
 *
 * Works with MongoDB Atlas (free tier) or any MongoDB instance.
 * Ideal for serverless deployments (Vercel, Cloudflare) where SQLite can't run.
 */

import { MongoClient, Db, Collection, ObjectId } from "mongodb";
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
import { DEFAULT_SETTINGS as DEFAULTS } from "./adapter";

export class MongoDBAdapter implements DatabaseAdapter {
    private client: MongoClient;
    private db!: Db;
    private connected = false;

    constructor(
        private uri: string = process.env.MONGODB_URI || "mongodb://localhost:27017",
        private dbName: string = process.env.MONGODB_DB_NAME || "blog",
    ) {
        this.client = new MongoClient(this.uri);
    }

    private async getDb(): Promise<Db> {
        if (!this.connected) {
            await this.client.connect();
            this.db = this.client.db(this.dbName);
            this.connected = true;
        }
        return this.db;
    }

    private col<T extends object = any>(name: string): Promise<Collection<T>> {
        return this.getDb().then((db) => db.collection<T>(name));
    }

    // ── Lifecycle ──────────────────────────────────────────────────

    async migrate(): Promise<void> {
        const db = await this.getDb();

        // Create indexes
        const posts = db.collection("posts");
        await posts.createIndex({ slug: 1 }, { unique: true });
        await posts.createIndex({ status: 1 });
        await posts.createIndex({ createdAt: -1 });
        await posts.createIndex({ tags: 1 });

        const media = db.collection("media");
        await media.createIndex({ createdAt: -1 });

        const apiKeys = db.collection("api_keys");
        await apiKeys.createIndex({ key: 1 }, { unique: true });

        const admins = db.collection("admins");
        await admins.createIndex({ email: 1 }, { unique: true });

        const sessions = db.collection("admin_sessions");
        await sessions.createIndex({ token: 1 }, { unique: true });
        await sessions.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });

        // Seed default settings if empty
        const settings = db.collection("settings");
        const count = await settings.countDocuments();
        if (count === 0) {
            const docs = Object.entries(DEFAULTS).map(([key, value]) => ({
                key,
                value: JSON.stringify(value),
            }));
            await settings.insertMany(docs);
        }
    }

    async close(): Promise<void> {
        if (this.connected) {
            await this.client.close();
            this.connected = false;
        }
    }

    // ── Posts ───────────────────────────────────────────────────────

    async createPost(data: CreatePostInput): Promise<Post> {
        const col = await this.col("posts");
        const now = new Date();
        const doc = {
            id: uuidv4(),
            title: data.title,
            slug: data.slug,
            content: data.content,
            excerpt: data.excerpt || "",
            coverImage: data.coverImage || "",
            tags: data.tags || [],
            status: data.status || "draft",
            authorName: data.authorName || "AI Agent",
            viewCount: 0,
            createdAt: now,
            updatedAt: now,
        };
        await col.insertOne(doc as any);
        return this.docToPost(doc);
    }

    async getPost(slug: string): Promise<Post | null> {
        const col = await this.col("posts");
        const doc = await col.findOne({ slug });
        return doc ? this.docToPost(doc) : null;
    }

    async getPostById(id: string): Promise<Post | null> {
        const col = await this.col("posts");
        const doc = await col.findOne({ id });
        return doc ? this.docToPost(doc) : null;
    }

    async updatePost(id: string, data: UpdatePostInput): Promise<Post> {
        const col = await this.col("posts");
        const update: any = { updatedAt: new Date() };

        if (data.title !== undefined) update.title = data.title;
        if (data.slug !== undefined) update.slug = data.slug;
        if (data.content !== undefined) update.content = data.content;
        if (data.excerpt !== undefined) update.excerpt = data.excerpt;
        if (data.coverImage !== undefined) update.coverImage = data.coverImage;
        if (data.tags !== undefined) update.tags = data.tags;
        if (data.status !== undefined) update.status = data.status;

        await col.updateOne({ id }, { $set: update });
        return this.getPostById(id) as Promise<Post>;
    }

    async deletePost(id: string): Promise<void> {
        const col = await this.col("posts");
        await col.deleteOne({ id });
    }

    async listPosts(opts: ListOptions = {}): Promise<PaginatedResult<Post>> {
        const col = await this.col("posts");
        const page = opts.page || 1;
        const limit = opts.limit || 10;
        const skip = (page - 1) * limit;

        const filter: any = {};
        if (opts.status && opts.status !== "all") filter.status = opts.status;
        if (opts.tag) filter.tags = opts.tag;
        if (opts.search) {
            filter.$or = [
                { title: { $regex: opts.search, $options: "i" } },
                { content: { $regex: opts.search, $options: "i" } },
            ];
        }

        const sortField = opts.sortBy || "createdAt";
        const sortDir = opts.sortOrder === "asc" ? 1 : -1;

        const [total, docs] = await Promise.all([
            col.countDocuments(filter),
            col.find(filter).sort({ [sortField]: sortDir }).skip(skip).limit(limit).toArray(),
        ]);

        return {
            data: docs.map((d: any) => this.docToPost(d)),
            total,
            page,
            limit,
            totalPages: Math.ceil(total / limit),
        };
    }

    // ── Media ──────────────────────────────────────────────────────

    async saveMedia(buffer: Buffer, meta: MediaMeta): Promise<Media> {
        const col = await this.col("media");
        const id = uuidv4();
        // For MongoDB deployments, media is stored as base64 in the DB
        // or you can swap this for S3/Cloudinary in production
        const doc = {
            id,
            filename: meta.filename,
            url: `/api/media/${id}`,
            mimeType: meta.mimeType,
            size: meta.size,
            alt: meta.alt || "",
            data: buffer.toString("base64"),
            createdAt: new Date(),
        };
        await col.insertOne(doc as any);
        return {
            id,
            filename: meta.filename,
            url: doc.url,
            mimeType: meta.mimeType,
            size: meta.size,
            alt: doc.alt,
            createdAt: doc.createdAt,
        };
    }

    async getMedia(id: string): Promise<Media | null> {
        const col = await this.col("media");
        const doc = await col.findOne({ id });
        if (!doc) return null;
        return {
            id: (doc as any).id,
            filename: (doc as any).filename,
            url: (doc as any).url,
            mimeType: (doc as any).mimeType,
            size: (doc as any).size,
            alt: (doc as any).alt,
            createdAt: new Date((doc as any).createdAt),
        };
    }

    async deleteMedia(id: string): Promise<void> {
        const col = await this.col("media");
        await col.deleteOne({ id });
    }

    async listMedia(): Promise<Media[]> {
        const col = await this.col("media");
        const docs = await col
            .find({}, { projection: { data: 0 } })
            .sort({ createdAt: -1 })
            .toArray();
        return docs.map((d: any) => ({
            id: d.id,
            filename: d.filename,
            url: d.url,
            mimeType: d.mimeType,
            size: d.size,
            alt: d.alt,
            createdAt: new Date(d.createdAt),
        }));
    }

    // ── Settings ───────────────────────────────────────────────────

    async getSettings(): Promise<BlogSettings> {
        const col = await this.col("settings");
        const docs = await col.find().toArray();
        const settings = { ...DEFAULTS } as any;
        for (const doc of docs) {
            try {
                settings[(doc as any).key] = JSON.parse((doc as any).value);
            } catch {
                settings[(doc as any).key] = (doc as any).value;
            }
        }
        return settings as BlogSettings;
    }

    async updateSettings(data: Partial<BlogSettings>): Promise<BlogSettings> {
        const col = await this.col("settings");
        for (const [key, value] of Object.entries(data)) {
            await col.updateOne(
                { key },
                { $set: { key, value: JSON.stringify(value) } },
                { upsert: true },
            );
        }
        return this.getSettings();
    }

    // ── Analytics ──────────────────────────────────────────────────

    async recordView(postSlug: string): Promise<void> {
        const col = await this.col("posts");
        await col.updateOne({ slug: postSlug }, { $inc: { viewCount: 1 } });
    }

    async getAnalytics(_range?: DateRange): Promise<Analytics> {
        const col = await this.col("posts");

        const [totalPosts, totalDrafts, viewsAgg, topPosts, postsByMonth] =
            await Promise.all([
                col.countDocuments({ status: "published" }),
                col.countDocuments({ status: "draft" }),
                col
                    .aggregate([
                        { $group: { _id: null, total: { $sum: "$viewCount" } } },
                    ])
                    .toArray(),
                col
                    .find({ status: "published" })
                    .sort({ viewCount: -1 })
                    .limit(10)
                    .project({ slug: 1, title: 1, viewCount: 1, _id: 0 })
                    .toArray(),
                col
                    .aggregate([
                        {
                            $group: {
                                _id: {
                                    $dateToString: {
                                        format: "%Y-%m",
                                        date: "$createdAt",
                                    },
                                },
                                count: { $sum: 1 },
                            },
                        },
                        { $sort: { _id: -1 } },
                        { $limit: 12 },
                    ])
                    .toArray(),
            ]);

        return {
            totalPosts,
            totalDrafts,
            totalViews: viewsAgg[0]?.total || 0,
            topPosts: topPosts.map((p: any) => ({
                slug: p.slug,
                title: p.title,
                viewCount: p.viewCount,
            })),
            postsByMonth: postsByMonth.map((p: any) => ({
                month: p._id,
                count: p.count,
            })),
        };
    }

    // ── Auth ───────────────────────────────────────────────────────

    async validateApiKey(key: string): Promise<boolean> {
        const col = await this.col("api_keys");
        const doc = await col.findOne({ key });
        return !!doc;
    }

    async getApiKeys(): Promise<string[]> {
        const col = await this.col("api_keys");
        const docs = await col.find().toArray();
        return docs.map((d: any) => d.key);
    }

    async addApiKey(key: string): Promise<void> {
        const col = await this.col("api_keys");
        await col.updateOne({ key }, { $set: { key, createdAt: new Date() } }, { upsert: true });
    }

    async removeApiKey(key: string): Promise<void> {
        const col = await this.col("api_keys");
        await col.deleteOne({ key });
    }

    async createAdmin(data: AdminUser): Promise<void> {
        const col = await this.col("admins");
        const passwordHash = await bcrypt.hash(data.password, 12);
        await col.insertOne({
            id: uuidv4(),
            email: data.email,
            passwordHash,
            name: data.name,
            createdAt: new Date(),
        } as any);
    }

    async validateAdmin(
        email: string,
        password: string,
    ): Promise<AdminSession | null> {
        const admins = await this.col("admins");
        const admin = await admins.findOne({ email });
        if (!admin) return null;

        const valid = await bcrypt.compare(password, (admin as any).passwordHash);
        if (!valid) return null;

        const sessions = await this.col("admin_sessions");
        const session = {
            id: uuidv4(),
            adminId: (admin as any).id,
            token: uuidv4(),
            expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        };
        await sessions.insertOne(session as any);

        return {
            id: session.id,
            email: (admin as any).email,
            name: (admin as any).name,
            token: session.token,
            expiresAt: session.expiresAt,
        };
    }

    async getAdminByToken(token: string): Promise<AdminSession | null> {
        const sessions = await this.col("admin_sessions");
        const session = await sessions.findOne({
            token,
            expiresAt: { $gt: new Date() },
        });
        if (!session) return null;

        const admins = await this.col("admins");
        const admin = await admins.findOne({ id: (session as any).adminId });
        if (!admin) return null;

        return {
            id: (session as any).id,
            email: (admin as any).email,
            name: (admin as any).name,
            token: (session as any).token,
            expiresAt: new Date((session as any).expiresAt),
        };
    }

    // ── Helpers ────────────────────────────────────────────────────

    private docToPost(doc: any): Post {
        return {
            id: doc.id,
            title: doc.title,
            slug: doc.slug,
            content: doc.content,
            excerpt: doc.excerpt || "",
            coverImage: doc.coverImage || "",
            tags: doc.tags || [],
            status: doc.status,
            authorName: doc.authorName || "AI Agent",
            viewCount: doc.viewCount || 0,
            createdAt: new Date(doc.createdAt),
            updatedAt: new Date(doc.updatedAt),
        };
    }
}
