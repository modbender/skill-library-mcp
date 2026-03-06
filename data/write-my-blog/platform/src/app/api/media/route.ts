/**
 * Media Upload API
 */

import { NextRequest, NextResponse } from "next/server";
import { getDatabase } from "@/lib/db";
import { validateRequest, addSecurityHeaders } from "@/lib/auth/middleware";

const ALLOWED_TYPES = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
    "application/pdf",
];
const MAX_SIZE = 10 * 1024 * 1024; // 10MB

export async function POST(request: NextRequest) {
    const authError = await validateRequest(request);
    if (authError) return authError;

    try {
        const formData = await request.formData();
        const file = formData.get("file") as File | null;
        const alt = (formData.get("alt") as string) || "";

        if (!file) {
            return NextResponse.json({ error: "No file provided" }, { status: 400 });
        }

        if (!ALLOWED_TYPES.includes(file.type)) {
            return NextResponse.json(
                { error: `File type "${file.type}" not allowed. Allowed: ${ALLOWED_TYPES.join(", ")}` },
                { status: 400 },
            );
        }

        if (file.size > MAX_SIZE) {
            return NextResponse.json(
                { error: `File too large. Max size: ${MAX_SIZE / 1024 / 1024}MB` },
                { status: 400 },
            );
        }

        const buffer = Buffer.from(await file.arrayBuffer());
        const db = await getDatabase();

        const media = await db.saveMedia(buffer, {
            filename: file.name,
            mimeType: file.type,
            size: file.size,
            alt,
        });

        const response = NextResponse.json(media, { status: 201 });
        return addSecurityHeaders(response);
    } catch (error: any) {
        return NextResponse.json(
            { error: error.message || "Failed to upload media" },
            { status: 500 },
        );
    }
}

export async function GET(request: NextRequest) {
    const authError = await validateRequest(request);
    if (authError) return authError;

    try {
        const db = await getDatabase();
        const media = await db.listMedia();
        const response = NextResponse.json(media);
        return addSecurityHeaders(response);
    } catch (error: any) {
        return NextResponse.json(
            { error: error.message || "Failed to list media" },
            { status: 500 },
        );
    }
}
