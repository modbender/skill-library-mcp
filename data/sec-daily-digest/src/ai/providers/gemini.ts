import { type AIProvider } from "./types";

export function createGeminiProvider(env: NodeJS.ProcessEnv, fetcher: typeof fetch = fetch): AIProvider {
  const apiKey = env.GEMINI_API_KEY?.trim();
  if (!apiKey) {
    throw new Error("GEMINI_API_KEY is required for provider gemini");
  }

  const model = env.GEMINI_MODEL?.trim() || "gemini-2.0-flash";
  const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;

  return {
    id: "gemini",
    async call(prompt: string): Promise<string> {
      const response = await fetcher(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: {
            temperature: 0.2,
            topP: 0.8,
          },
        }),
      });

      if (!response.ok) {
        const body = await response.text().catch(() => "");
        throw new Error(`Gemini API error (${response.status}): ${body}`);
      }

      const data = await response.json() as {
        candidates?: Array<{
          content?: {
            parts?: Array<{ text?: string }>;
          };
        }>;
      };

      return data.candidates?.[0]?.content?.parts?.[0]?.text ?? "";
    },
  };
}
