#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// ---------------------------------------------------------------------------
// Freebeat AI — MCP Server (Mock)
// The world's first AI music video generation MCP.
// ---------------------------------------------------------------------------

const FREEBEAT_API_KEY = process.env.FREEBEAT_API_KEY || "";

const server = new McpServer({
  name: "freebeat",
  version: "0.1.0",
  description:
    "Turn any song into a cinematic music video. Supports singing, storytelling, and auto modes.",
});

// ---- Helper: mock delay + fake response ------------------------------------

function mockDelay() {
  return new Promise((r) => setTimeout(r, 200 + Math.random() * 300));
}

function fakeVideoUrl(id) {
  return `https://cdn.freebeat.ai/renders/${id}.mp4`;
}

function fakeJobId() {
  return "fb_" + Math.random().toString(36).slice(2, 14);
}

// ---- Tool 1: generate_music_video ------------------------------------------

server.tool(
  "generate_music_video",
  "Generate an AI music video from a text prompt. Returns a video URL. Modes: singing (lyric-driven), storytelling (narrative scenes), auto (AI picks best mode).",
  {
    prompt: z
      .string()
      .describe("Creative prompt describing the music video you want"),
    mode: z
      .enum(["singing", "storytelling", "auto"])
      .default("auto")
      .describe("Generation mode"),
    duration: z
      .number()
      .min(5)
      .max(180)
      .default(30)
      .describe("Video duration in seconds (5-180)"),
    style: z
      .string()
      .optional()
      .describe(
        'Optional visual style hint, e.g. "cinematic", "anime", "retro VHS"'
      ),
  },
  async ({ prompt, mode, duration, style }) => {
    if (!FREEBEAT_API_KEY) {
      return {
        content: [
          {
            type: "text",
            text: "Error: FREEBEAT_API_KEY not set. Get your free API key at https://freebeat.ai/developers",
          },
        ],
        isError: true,
      };
    }

    await mockDelay();

    const jobId = fakeJobId();
    const videoUrl = fakeVideoUrl(jobId);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              status: "completed",
              job_id: jobId,
              video_url: videoUrl,
              duration_seconds: duration,
              mode,
              style: style || "cinematic",
              prompt,
              credits_used: Math.ceil(duration / 10),
              credits_remaining: 47,
            },
            null,
            2
          ),
        },
      ],
    };
  }
);

// ---- Tool 2: check_generation_status ---------------------------------------

server.tool(
  "check_generation_status",
  "Check the status of a music video generation job.",
  {
    job_id: z.string().describe("Job ID returned by generate_music_video"),
  },
  async ({ job_id }) => {
    await mockDelay();
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              job_id,
              status: "completed",
              progress: 100,
              video_url: fakeVideoUrl(job_id),
              created_at: new Date(Date.now() - 60000).toISOString(),
              completed_at: new Date().toISOString(),
            },
            null,
            2
          ),
        },
      ],
    };
  }
);

// ---- Tool 3: list_styles ---------------------------------------------------

server.tool(
  "list_styles",
  "List available visual styles for music video generation.",
  {},
  async () => {
    await mockDelay();
    const styles = [
      { id: "cinematic", name: "Cinematic", description: "Film-quality visuals with dramatic lighting" },
      { id: "anime", name: "Anime", description: "Japanese animation style" },
      { id: "retro-vhs", name: "Retro VHS", description: "Nostalgic 80s/90s VHS aesthetic" },
      { id: "3d-render", name: "3D Render", description: "Modern 3D rendered scenes" },
      { id: "watercolor", name: "Watercolor", description: "Soft watercolor painting look" },
      { id: "neon-noir", name: "Neon Noir", description: "Dark cityscapes with neon lights" },
      { id: "minimalist", name: "Minimalist", description: "Clean, simple geometric visuals" },
      { id: "psychedelic", name: "Psychedelic", description: "Vibrant, trippy color patterns" },
    ];
    return {
      content: [{ type: "text", text: JSON.stringify(styles, null, 2) }],
    };
  }
);

// ---- Tool 4: get_account_info ----------------------------------------------

server.tool(
  "get_account_info",
  "Get current account info and remaining credits.",
  {},
  async () => {
    if (!FREEBEAT_API_KEY) {
      return {
        content: [
          {
            type: "text",
            text: "Error: FREEBEAT_API_KEY not set. Get your free API key at https://freebeat.ai/developers",
          },
        ],
        isError: true,
      };
    }
    await mockDelay();
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              plan: "free",
              credits_remaining: 50,
              credits_total: 50,
              videos_generated: 0,
              api_key_prefix: FREEBEAT_API_KEY.slice(0, 8) + "...",
            },
            null,
            2
          ),
        },
      ],
    };
  }
);

// ---- Start server ----------------------------------------------------------

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Freebeat MCP server running on stdio");
}

main().catch((err) => {
  console.error("Fatal:", err);
  process.exit(1);
});
