/**
 * Analytics API
 */

import { NextRequest, NextResponse } from "next/server";
import { getDatabase } from "@/lib/db";
import { validateRequest, addSecurityHeaders } from "@/lib/auth/middleware";

export async function GET(request: NextRequest) {
    const authError = await validateRequest(request);
    if (authError) return authError;

    try {
        const db = await getDatabase();
        const analytics = await db.getAnalytics();

        const response = NextResponse.json(analytics);
        return addSecurityHeaders(response);
    } catch (error: any) {
        return NextResponse.json(
            { error: error.message || "Failed to get analytics" },
            { status: 500 },
        );
    }
}
