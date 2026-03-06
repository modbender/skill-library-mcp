/**
 * Environment Validation
 *
 * Uses Zod to validate all required environment variables at startup.
 */

import { z } from "zod";

const envSchema = z.object({
    // Required
    API_KEY: z.string().min(16, "API_KEY must be at least 16 characters"),

    // Database — at least one must be configured
    DATABASE_PROVIDER: z
        .enum(["sqlite", "postgres", "supabase", "mongodb", "turso"])
        .default("sqlite"),

    // SQLite
    SQLITE_PATH: z.string().optional().default("./data/blog.db"),

    // Supabase
    SUPABASE_URL: z.string().url().optional(),
    SUPABASE_SERVICE_KEY: z.string().optional(),

    // Cache
    CACHE_PROVIDER: z.enum(["memory", "redis"]).default("memory"),
    CACHE_MAX_SIZE: z.string().optional().default("500"),

    // Redis
    REDIS_URL: z.string().optional(),
    UPSTASH_REDIS_REST_URL: z.string().optional(),
    UPSTASH_REDIS_REST_TOKEN: z.string().optional(),

    // Rate limiting
    RATE_LIMIT_RPM: z.string().optional().default("100"),

    // Media
    MEDIA_DIR: z.string().optional().default("./public/uploads"),
});

export type Env = z.infer<typeof envSchema>;

export function validateEnv(): Env {
    try {
        return envSchema.parse(process.env);
    } catch (error) {
        if (error instanceof z.ZodError) {
            const missing = error.issues
                .map((i) => `  - ${i.path.join(".")}: ${i.message}`)
                .join("\n");
            console.error(`\n❌ Invalid environment variables:\n${missing}\n`);
            console.error("Copy templates/env.example to platform/.env.local and fill in values.\n");
        }
        throw error;
    }
}
