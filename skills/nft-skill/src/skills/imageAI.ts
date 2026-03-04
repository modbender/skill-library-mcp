/**
 * AI Image Generation Skill
 * Supports Stability AI and DALL-E as providers, with procedural fallback
 */
import axios from 'axios';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Generate an image from a text prompt using the configured AI provider.
 * Returns the file path of the saved PNG, or null if no AI provider is configured.
 */
export async function generateAIImage(prompt: string, outputDir: string): Promise<string | null> {
  const provider = (process.env.IMAGE_PROVIDER || 'procedural').toLowerCase();

  if (provider === 'procedural' || provider === '') return null;

  const fileName = `ai_art_${Date.now()}.png`;
  const filePath = path.join(outputDir, fileName);

  try {
    if (provider === 'stability') {
      return await generateWithStability(prompt, filePath);
    } else if (provider === 'dalle') {
      return await generateWithDalle(prompt, filePath);
    }
    console.warn(`[ImageAI] Unknown provider "${provider}", falling back to procedural`);
    return null;
  } catch (error: any) {
    console.error(`[ImageAI] ${provider} generation failed: ${error.message}. Falling back to procedural.`);
    return null;
  }
}

async function generateWithStability(prompt: string, filePath: string): Promise<string> {
  const model = process.env.IMAGE_MODEL || 'stable-diffusion-xl-1024-v1-0';
  const apiKey = process.env.STABILITY_API_KEY;
  if (!apiKey) throw new Error('STABILITY_API_KEY is not set');

  const response = await axios.post(
    `https://api.stability.ai/v1/generation/${model}/text-to-image`,
    {
      text_prompts: [{ text: prompt, weight: 1 }],
      cfg_scale: 7,
      height: 1024,
      width: 1024,
      samples: 1,
      steps: 30
    },
    {
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        Accept: 'application/json'
      }
    }
  );

  const base64 = response.data.artifacts[0].base64;
  fs.writeFileSync(filePath, Buffer.from(base64, 'base64'));
  console.log(`[ImageAI] Stability AI image saved: ${filePath}`);
  return filePath;
}

async function generateWithDalle(prompt: string, filePath: string): Promise<string> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error('OPENAI_API_KEY is not set');

  const model = process.env.IMAGE_MODEL || 'dall-e-3';

  const response = await axios.post(
    'https://api.openai.com/v1/images/generations',
    {
      model,
      prompt,
      n: 1,
      size: '1024x1024',
      response_format: 'b64_json'
    },
    {
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    }
  );

  const base64 = response.data.data[0].b64_json;
  fs.writeFileSync(filePath, Buffer.from(base64, 'base64'));
  console.log(`[ImageAI] DALL-E image saved: ${filePath}`);
  return filePath;
}
