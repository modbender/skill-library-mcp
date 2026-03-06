/**
 * Settings API
 */

import { NextRequest, NextResponse } from "next/server";
import { getDatabase } from "@/lib/db";
import { getCache } from "@/lib/cache";
import {
    validateRequest,
    sanitizeInput,
    addSecurityHeaders,
} from "@/lib/auth/middleware";

export async function GET(request: NextRequest) {
    const authError = await validateRequest(request);
    if (authError) return authError;

    try {
        const db = await getDatabase();
        const settings = await db.getSettings();
        const response = NextResponse.json(settings);
        return addSecurityHeaders(response);
    } catch (error: any) {
        return NextResponse.json(
            { error: error.message || "Failed to get settings" },
            { status: 500 },
        );
    }
}

export async function PUT(request: NextRequest) {
    const authError = await validateRequest(request);
    if (authError) return authError;

    try {
        const body = await request.json();
        const sanitized = sanitizeInput(body);

        const db = await getDatabase();
        const settings = await db.updateSettings(sanitized as any);

        const cache = await getCache();
        await cache.delete("settings");

        const response = NextResponse.json(settings);
        return addSecurityHeaders(response);
    } catch (error: any) {
        return NextResponse.json(
            { error: error.message || "Failed to update settings" },
            { status: 500 },
        );
    }
}
