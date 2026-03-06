import { readFileSync } from "fs";
import { join } from "path";
import { NextResponse } from "next/server";

export async function GET() {
  const skillPath = join(process.cwd(), "openclaw-skill", "SKILL.md");
  const content = readFileSync(skillPath, "utf-8");

  return new NextResponse(content, {
    headers: {
      "Content-Type": "text/markdown; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
    },
  });
}
