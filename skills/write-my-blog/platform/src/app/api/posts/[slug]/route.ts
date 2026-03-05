/**
 * Single Post API — GET, PUT, DELETE by slug
 */

import { NextRequest, NextResponse } from "next/server";
import { getDatabase } from "@/lib/db";
import { getCache } from "@/lib/cache";
import {
    validateRequest,
    sanitizeInput,
    addSecurityHeaders,
} from "@/lib/auth/middleware";

interface Params {
    params: { slug: string };
}

export async function GET(request: NextRequest, { params }: Params) {
    const authError = await validateRequest(request);
    if (authError) return authError;

    try {
        const { slug } = params;
        const cache = await getCache();
        const cacheKey = `posts:single:${slug}`;

        const cached = await cache.get(cacheKey);
        if (cached) {
            return addSecurityHeaders(NextResponse.json(cached));
        }

        const db = await getDatabase();
        const post = await db.getPost(slug);

        if (!post) {
            return NextResponse.json({ error: "Post not found" }, { status: 404 });
        }

        // Record view
        await db.recordView(slug);

        await cache.set(cacheKey, post, 120);

        const response = NextResponse.json(post);
        return addSecurityHeaders(response);
    } catch (error: any) {
        return NextResponse.json(
            { error: error.message || "Failed to get post" },
            { status: 500 },
        );
    }
}

export async function PUT(request: NextRequest, { params }: Params) {
    const authError = await validateRequest(request);
    if (authError) return authError;

    try {
        const { slug } = params;
        const body = await request.json();
        const sanitized = sanitizeInput(body);

        const db = await getDatabase();
        const existing = await db.getPost(slug);

        if (!existing) {
            return NextResponse.json({ error: "Post not found" }, { status: 404 });
        }

        const post = await db.updatePost(existing.id, {
            title: sanitized.title as string | undefined,
            slug: sanitized.slug as string | undefined,
            content: sanitized.content as string | undefined,
            excerpt: sanitized.excerpt as string | undefined,
            coverImage: sanitized.coverImage as string | undefined,
            tags: sanitized.tags as string[] | undefined,
            status: sanitized.status as "draft" | "published" | undefined,
        });

        // Invalidate caches
        const cache = await getCache();
        await cache.delete(`posts:single:${slug}`);
        await cache.invalidatePattern("posts:list:*");

        const response = NextResponse.json(post);
        return addSecurityHeaders(response);
    } catch (error: any) {
        return NextResponse.json(
            { error: error.message || "Failed to update post" },
            { status: 500 },
        );
    }
}

export async function DELETE(request: NextRequest, { params }: Params) {
    const authError = await validateRequest(request);
    if (authError) return authError;

    try {
        const { slug } = params;
        const db = await getDatabase();
        const existing = await db.getPost(slug);

        if (!existing) {
            return NextResponse.json({ error: "Post not found" }, { status: 404 });
        }

        await db.deletePost(existing.id);

        // Invalidate caches
        const cache = await getCache();
        await cache.delete(`posts:single:${slug}`);
        await cache.invalidatePattern("posts:list:*");

        const response = NextResponse.json({ message: "Post deleted" });
        return addSecurityHeaders(response);
    } catch (error: any) {
        return NextResponse.json(
            { error: error.message || "Failed to delete post" },
            { status: 500 },
        );
    }
}
