import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "API Documentation",
  description: "Open API documentation for the OpenClaw Leaderboard. Rate-limited, CORS-enabled endpoints.",
};

export default function DocsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
