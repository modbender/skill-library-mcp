/**
 * Themes API — List and switch themes
 */

import { NextRequest, NextResponse } from "next/server";
import { getDatabase } from "@/lib/db";
import { getCache } from "@/lib/cache";
import { validateRequest, addSecurityHeaders } from "@/lib/auth/middleware";

const AVAILABLE_THEMES = [
    { id: "minimalism", name: "Minimalism", description: "Clean, whitespace-heavy, monochrome palette" },
    { id: "brutalism", name: "Brutalism", description: "Bold, jarring colors, sharp shadows, loud visuals" },
    { id: "constructivism", name: "Constructivism", description: "Geometric shapes, sans-serif, asymmetric layouts" },
    { id: "swiss", name: "Swiss Style", description: "Grid-based, Helvetica typography, orderly and minimal" },
    { id: "editorial", name: "Editorial", description: "Magazine-style, contrasting type, layered compositions" },
    { id: "hand-drawn", name: "Hand-Drawn", description: "Handwritten fonts, sketchy accents, casual aesthetic" },
    { id: "retro", name: "Retro", description: "Warm colors, grainy textures, vintage UI elements" },
    { id: "flat", name: "Flat", description: "No depth effects, solid colors, clean hierarchy" },
    { id: "bento", name: "Bento", description: "Rounded grid blocks, compact layout, soft colors" },
    { id: "glassmorphism", name: "Glassmorphism", description: "Frosted glass, backdrop-blur, translucent layers" },
];

export async function GET(request: NextRequest) {
    const authError = await validateRequest(request);
    if (authError) return authError;

    try {
        const db = await getDatabase();
        const settings = await db.getSettings();

        const response = NextResponse.json({
            activeTheme: settings.activeTheme,
            themes: AVAILABLE_THEMES,
        });
        return addSecurityHeaders(response);
    } catch (error: any) {
        return NextResponse.json(
            { error: error.message || "Failed to get themes" },
            { status: 500 },
        );
    }
}

export async function PUT(request: NextRequest) {
    const authError = await validateRequest(request);
    if (authError) return authError;

    try {
        const body = await request.json();
        const { theme } = body;

        if (!theme || !AVAILABLE_THEMES.find((t) => t.id === theme)) {
            return NextResponse.json(
                {
                    error: `Invalid theme. Available: ${AVAILABLE_THEMES.map((t) => t.id).join(", ")}`,
                },
                { status: 400 },
            );
        }

        const db = await getDatabase();
        await db.updateSettings({ activeTheme: theme });

        // Invalidate settings cache
        const cache = await getCache();
        await cache.delete("settings");

        const response = NextResponse.json({
            message: `Theme switched to "${theme}"`,
            activeTheme: theme,
        });
        return addSecurityHeaders(response);
    } catch (error: any) {
        return NextResponse.json(
            { error: error.message || "Failed to switch theme" },
            { status: 500 },
        );
    }
}
