/**
 * One-off script to generate landing page images using Google Gemini API.
 * Run with: npx tsx scripts/generate-images.ts
 *
 * Requires GEMINI_API_KEY env var.
 * Saves images to public/images/ — commit them to the repo.
 */

import { writeFileSync, mkdirSync } from "fs";
import { join } from "path";

const IMAGE_GENERATION_MODEL = "gemini-3-pro-image-preview";
const GEMINI_API_ENDPOINT =
  "https://generativelanguage.googleapis.com/v1beta/models";

const OUTPUT_DIR = join(__dirname, "..", "public", "images");

interface ImageSpec {
  name: string;
  prompt: string;
}

const images: ImageSpec[] = [
  {
    name: "hero-illustration.png",
    prompt: `Create a futuristic, dark-themed illustration for a tech leaderboard website.
Show an abstract visualization of AI agents competing on a glowing purple leaderboard.
Include elements like: glowing trophy, ranking bars, digital currency symbols ($, ₿, Ξ),
circuit board patterns, and a dark space background.
Style: modern, clean, vibrant purple and blue gradients on dark background.
No text. 1200x600 aspect ratio.`,
  },
  {
    name: "og-image.png",
    prompt: `Create a social media preview image (OG image) for "OpenClaw Leaderboard".
Dark background (#09090b). Show a stylized leaderboard with glowing purple rankings.
Include a golden trophy at the top, dollar signs, and a futuristic AI theme.
Include the text "OpenClaw Leaderboard" in bold modern font at the center,
and "Which AI earns the most?" as a subtitle below.
Style: tech, modern, purple/gold accents on dark. 1200x630 dimensions.`,
  },
  {
    name: "step-submit.png",
    prompt: `Create a small icon/illustration for "Submit Earnings" step.
Show a hand holding a document or receipt with a dollar sign and an upload arrow.
Style: flat, modern, purple accent on transparent/dark background.
Simple, iconic, 200x200 pixels. No text.`,
  },
  {
    name: "step-verify.png",
    prompt: `Create a small icon/illustration for "Community Verification" step.
Show a shield with a checkmark, surrounded by multiple small user avatars voting.
Style: flat, modern, purple and green accents on transparent/dark background.
Simple, iconic, 200x200 pixels. No text.`,
  },
  {
    name: "step-rank.png",
    prompt: `Create a small icon/illustration for "Climb the Ranks" step.
Show a bar chart with ascending bars and a lightning bolt, suggesting growth and speed.
Style: flat, modern, purple and gold accents on transparent/dark background.
Simple, iconic, 200x200 pixels. No text.`,
  },
];

async function generateImage(spec: ImageSpec): Promise<void> {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error("Missing GEMINI_API_KEY environment variable");
  }

  console.log(`Generating: ${spec.name}...`);

  const response = await fetch(
    `${GEMINI_API_ENDPOINT}/${IMAGE_GENERATION_MODEL}:generateContent`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-goog-api-key": apiKey,
      },
      body: JSON.stringify({
        contents: [{ parts: [{ text: spec.prompt }] }],
      }),
    }
  );

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Gemini API error for ${spec.name}: ${response.status} - ${errorText}`);
  }

  const result = await response.json();

  const candidate = result.candidates?.[0];
  if (!candidate?.content?.parts) {
    throw new Error(`No content in Gemini response for ${spec.name}`);
  }

  const imagePart = candidate.content.parts.find(
    (part: { inlineData?: { data: string; mimeType: string } }) => part.inlineData
  );
  if (!imagePart?.inlineData) {
    throw new Error(`No image data in Gemini response for ${spec.name}`);
  }

  const imageBuffer = Buffer.from(imagePart.inlineData.data, "base64");
  const outputPath = join(OUTPUT_DIR, spec.name);
  writeFileSync(outputPath, imageBuffer);

  console.log(`  Saved: ${outputPath} (${(imageBuffer.length / 1024).toFixed(1)}KB)`);
}

async function main() {
  mkdirSync(OUTPUT_DIR, { recursive: true });

  console.log(`Generating ${images.length} images...\n`);

  for (const spec of images) {
    try {
      await generateImage(spec);
    } catch (error) {
      console.error(`Failed to generate ${spec.name}:`, error);
    }
  }

  console.log("\nDone! Images saved to public/images/");
}

main();
