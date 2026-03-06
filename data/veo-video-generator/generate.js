import { GoogleGenAI } from "@google/genai";
import fs from "fs";

// The SDK automatically checks for GEMINI_API_KEY or GOOGLE_API_KEY in the environment
const apiKey = process.env.GEMINI_API_KEY;

if (!apiKey) {
  console.error("❌ Error: GEMINI_API_KEY not found in environment.");
  process.exit(1);
}

const ai = new GoogleGenAI({ apiKey });

// Parse command line arguments
const args = process.argv.slice(2);
const promptArgIndex = args.indexOf("--prompt");
const userPrompt = promptArgIndex !== -1 ? args[promptArgIndex + 1] : null;

if (!userPrompt) {
  console.error(
    '❌ Error: No prompt provided. Use --prompt "your description"',
  );
  process.exit(1);
}

// Defence-in-depth: reject prompts that contain shell metacharacters.
// The primary protection is that callers must use execFile / argv arrays
// (never shell string interpolation), but this guard adds a second layer.
const SHELL_METACHAR_RE = /[;&|`$<>\\]/;
if (SHELL_METACHAR_RE.test(userPrompt)) {
  console.error(
    "❌ Error: Prompt contains disallowed characters (; & | ` $ < > \\). " +
      "Please rephrase your prompt without shell metacharacters.",
  );
  process.exit(1);
}

async function generate() {
  try {
    console.log(`🎬 Requesting Veo 3.1: "${userPrompt}"`);

    let operation = await ai.models.generateVideos({
      model: "veo-3.1-fast-generate-preview",
      prompt: userPrompt,
      config: {
        aspectRatio: "9:16",
        resolution: "1080p",
        includeAudio: true,
      },
    });

    console.log("⏳ Rendering (this usually takes 45-90 seconds)...");

    // Poll for completion
    while (!operation.done) {
      process.stdout.write(".");
      await new Promise((resolve) => setTimeout(resolve, 10000));
      operation = await ai.operations.getVideosOperation({ operation });
    }

    const fileName = `veo_${Date.now()}.mp4`;
    await ai.files.download({
      file: operation.response.generatedVideos[0].video,
      downloadPath: fileName,
    });

    console.log(`\n✅ Video saved as: ${fileName}`);
  } catch (error) {
    console.error("\n❌ Generation failed:", error.message);
    process.exit(1);
  }
}

generate();
