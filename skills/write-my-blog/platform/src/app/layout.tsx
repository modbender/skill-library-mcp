import type { Metadata } from "next";
import "./globals.css";

/* Import all theme CSS files */
import "../themes/minimalism.css";
import "../themes/brutalism.css";
import "../themes/constructivism.css";
import "../themes/swiss.css";
import "../themes/editorial.css";
import "../themes/hand-drawn.css";
import "../themes/retro.css";
import "../themes/flat.css";
import "../themes/bento.css";
import "../themes/glassmorphism.css";

export const metadata: Metadata = {
    title: "Write My Blog",
    description: "An AI-powered blog with 10 premium design themes",
    keywords: ["blog", "AI", "writing", "technology"],
    authors: [{ name: "AI Agent" }],
    openGraph: {
        title: "Write My Blog",
        description: "An AI-powered blog with 10 premium design themes",
        type: "website",
    },
    robots: { index: true, follow: true },
};

async function getActiveTheme(): Promise<string> {
    try {
        const { getDatabase } = await import("@/lib/db");
        const db = await getDatabase();
        const settings = await db.getSettings();
        return settings.activeTheme || "minimalism";
    } catch {
        return process.env.DEFAULT_THEME || "minimalism";
    }
}

export default async function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const theme = await getActiveTheme();

    return (
        <html lang="en" data-theme={theme}>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <link rel="icon" href="/favicon.ico" />
            </head>
            <body>
                {children}
            </body>
        </html>
    );
}
