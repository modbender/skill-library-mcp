import { Tool } from 'openclaw/types'; // Conceptual type, not strict

/**
 * Generate an image using Google's Gemini models via OpenRouter.
 * 
 * @param {string} prompt - The image description.
 * @param {string} [model="google/gemini-2.0-flash-exp:free"] - The model ID (e.g., google/gemini-2.5-flash-image-preview, google/gemini-2.0-flash-exp:free).
 * @param {string} [aspectRatio="1:1"] - Aspect ratio (1:1, 16:9, 4:3, etc.).
 * @returns {Promise<string>} The image URL or base64 data.
 */
export async function generateImage({
  prompt,
  model = "google/gemini-2.0-flash-exp:free", // Default to free tier for testing
  aspectRatio = "1:1"
}: {
  prompt: string;
  model?: string;
  aspectRatio?: string;
}) {
  const apiKey = process.env.OPENROUTER_API_KEY || process.env.GEMINI_API_KEY; // Fallback
  if (!apiKey) {
    throw new Error("Missing API Key. Set OPENROUTER_API_KEY in your environment or config.");
  }

  // OpenRouter Chat Completions Endpoint for Image Generation
  // Note: Gemini 2.5 Flash Image uses 'modalities: ["image"]' in the request body
  const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "https://openclaw.ai", // Required by OpenRouter
      "X-Title": "OpenClaw Agent"
    },
    body: JSON.stringify({
      model: model,
      messages: [
        {
          role: "user",
          content: [
            {
              type: "text",
              text: prompt + (aspectRatio ? ` Aspect ratio: ${aspectRatio}.` : "")
            }
          ]
        }
      ],
      // OpenRouter specific parameter for image generation models
      // See: https://openrouter.ai/docs/guides/overview/multimodal/image-generation
      modalities: ["image"] 
    })
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`OpenRouter API Error (${response.status}): ${errorText}`);
  }

  const data = await response.json();
  
  // Parse response - OpenRouter usually returns the image url inside the message content
  // or checks for 'image' type blocks in content.
  const choice = data.choices?.[0];
  if (!choice) {
    throw new Error("No choices returned from OpenRouter.");
  }

  // Check for image url in content (OpenAI format often puts it in data, but chat completions might be different)
  // For Gemini via OpenRouter, the image is often a markdown link or direct URL in content.
  // Or sometimes strictly in `data` if using the image generation endpoint (v1/images/generations).
  // But we are using v1/chat/completions with modalities.
  
  // Strategy: Log the first few chars of content to debug if needed, but assumption is markdown image or URL.
  const content = choice.message?.content || "";
  
  // Extract URL from markdown ![Alt](url) or just return content if it's a URL
  const markdownMatch = content.match(/!\[.*?\]\((.*?)\)/);
  if (markdownMatch && markdownMatch[1]) {
    return markdownMatch[1];
  }
  
  // If content is just a URL
  if (content.startsWith("http")) {
    return content;
  }
  
  // If OpenRouter returns it in a specific 'image' field (unlikely for chat/completions standard, but possible)
  // Fallback: return the raw content (might be base64 or text describing the image)
  return content; 
}

// Tool definition for OpenClaw
export const metadata = {
  name: "nano_banana_generate",
  description: "Generate images using Google's Nano Banana (Gemini) models via OpenRouter. Use this for all image generation requests.",
  parameters: {
    type: "OBJECT",
    properties: {
      prompt: {
        type: "STRING",
        description: "Detailed description of the image to generate."
      },
      model: {
        type: "STRING",
        description: "OpenRouter model ID (default: google/gemini-2.0-flash-exp:free). Use 'google/gemini-2.5-flash-image-preview' for higher quality.",
        default: "google/gemini-2.0-flash-exp:free"
      },
      aspectRatio: {
        type: "STRING",
        description: "Aspect ratio (e.g., '1:1', '16:9', '4:3', '3:4').",
        default: "1:1"
      }
    },
    required: ["prompt"]
  }
};

export default generateImage;
