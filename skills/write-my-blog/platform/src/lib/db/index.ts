/**
 * Database Provider Index
 *
 * Auto-selects the database adapter based on the DATABASE_PROVIDER env var.
 * Defaults to SQLite for local development.
 */

import type { DatabaseAdapter } from "./adapter";

let _db: DatabaseAdapter | null = null;

export async function getDatabase(): Promise<DatabaseAdapter> {
    if (_db) return _db;

    const provider = process.env.DATABASE_PROVIDER || "sqlite";

    switch (provider) {
        case "sqlite": {
            const { SQLiteAdapter } = await import("./sqlite");
            _db = new SQLiteAdapter(
                process.env.SQLITE_PATH || "./data/blog.db",
                process.env.MEDIA_DIR || "./public/uploads",
            );
            break;
        }
        case "supabase": {
            const { SupabaseAdapter } = await import("./supabase");
            _db = new SupabaseAdapter(
                process.env.SUPABASE_URL,
                process.env.SUPABASE_SERVICE_KEY,
            );
            break;
        }
        case "postgres": {
            // PostgreSQL adapter — uses same SQLite adapter structure but with pg
            // For MVP, we route postgres to Supabase adapter (Supabase IS postgres)
            // A dedicated pg adapter can be added later with raw pg or Drizzle
            const { SupabaseAdapter } = await import("./supabase");
            _db = new SupabaseAdapter();
            break;
        }
        case "mongodb": {
            const { MongoDBAdapter } = await import("./mongodb");
            _db = new MongoDBAdapter(
                process.env.MONGODB_URI,
                process.env.MONGODB_DB_NAME || "blog",
            );
            break;
        }
        default:
            throw new Error(
                `Unsupported DATABASE_PROVIDER: "${provider}". ` +
                `Supported: sqlite, supabase, postgres, mongodb, turso`,
            );
    }

    return _db;
}

export type { DatabaseAdapter } from "./adapter";
export type {
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
