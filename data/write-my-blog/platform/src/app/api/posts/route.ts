/**
 * Posts API — CRUD operations for blog posts
 *
 * POST   /api/posts         — Create a new post
 * GET    /api/posts         — List posts (paginated)
 */

import { NextRequest, NextResponse } from "next/server";
import { getDatabase } from "@/lib/db";
import { getCache } from "@/lib/cache";
import {
    validateRequest,
    sanitizeInput,
    addSecurityHeaders,
} from "@/lib/auth/middleware";

export async function POST(request: NextRequest) {
    const authError = await validateRequest(request);
    if (authError) return authError;

    try {
        const body = await request.json();
        const sanitized = sanitizeInput(body);

        if (!sanitized.title || !sanitized.slug || !sanitized.content || !sanitized.authorName) {
            return NextResponse.json(
                { error: "title, slug, content, and authorName are required" },
                { status: 400 },
            );
        }

        const db = await getDatabase();

        // Check for duplicate slug
        const existing = await db.getPost(sanitized.slug as string);
        if (existing) {
            return NextResponse.json(
                { error: `Post with slug "${sanitized.slug}" already exists` },
                { status: 409 },
            );
        }

        const post = await db.createPost({
            title: sanitized.title as string,
            slug: sanitized.slug as string,
            content: sanitized.content as string,
            excerpt: (sanitized.excerpt as string) || "",
            coverImage: (sanitized.coverImage as string) || "",
            tags: (sanitized.tags as string[]) || [],
            status: (sanitized.status as "draft" | "published") || "draft",
            authorName: sanitized.authorName as string,
        });

        // Invalidate list cache
        const cache = await getCache();
        await cache.invalidatePattern("posts:list:*");

        const response = NextResponse.json(post, { status: 201 });
        return addSecurityHeaders(response);
    } catch (error: any) {
        return NextResponse.json(
            { error: error.message || "Failed to create post" },
            { status: 500 },
        );
    }
}

export async function GET(request: NextRequest) {
    const authError = await validateRequest(request);
    if (authError) return authError;

    try {
        const { searchParams } = new URL(request.url);
        const page = parseInt(searchParams.get("page") || "1", 10);
        const limit = parseInt(searchParams.get("limit") || "10", 10);
        const status = (searchParams.get("status") as "draft" | "published" | "all") || "all";
        const tag = searchParams.get("tag") || undefined;
        const search = searchParams.get("search") || undefined;
        const sortBy = (searchParams.get("sortBy") as any) || "createdAt";
        const sortOrder = (searchParams.get("sortOrder") as "asc" | "desc") || "desc";

        // Try cache first
        const cacheKey = `posts:list:${page}:${limit}:${status}:${tag}:${search}:${sortBy}:${sortOrder}`;
        const cache = await getCache();
        const cached = await cache.get(cacheKey);
        if (cached) {
            return addSecurityHeaders(NextResponse.json(cached));
        }

        const db = await getDatabase();
        const result = await db.listPosts({
            page,
            limit,
            status,
            tag,
            search,
            sortBy,
            sortOrder,
        });

        // Cache for 60 seconds
        await cache.set(cacheKey, result, 60);

        const response = NextResponse.json(result);
        return addSecurityHeaders(response);
    } catch (error: any) {
        return NextResponse.json(
            { error: error.message || "Failed to list posts" },
            { status: 500 },
        );
    }
}
