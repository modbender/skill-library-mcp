import { type AIProvider } from "./types";

const OPENAI_DEFAULT_BASE = "https://api.openai.com/v1";
const OPENAI_DEFAULT_MODEL = "gpt-4o-mini";

function normalizeBase(base: string): string {
  return base.replace(/\/+$/, "");
}

export function createOpenAIProvider(env: NodeJS.ProcessEnv, fetcher: typeof fetch = fetch): AIProvider {
  const apiKey = env.OPENAI_API_KEY?.trim();
  if (!apiKey) {
    throw new Error("OPENAI_API_KEY is required for provider openai");
  }

  const apiBase = normalizeBase(env.OPENAI_API_BASE?.trim() || OPENAI_DEFAULT_BASE);
  const model = env.OPENAI_MODEL?.trim() || OPENAI_DEFAULT_MODEL;

  return {
    id: "openai",
    async call(prompt: string): Promise<string> {
      const response = await fetcher(`${apiBase}/chat/completions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          model,
          messages: [{ role: "user", content: prompt }],
          temperature: 0.2,
        }),
      });

      if (!response.ok) {
        const body = await response.text().catch(() => "");
        throw new Error(`OpenAI API error (${response.status}): ${body}`);
      }

      const data = await response.json() as {
        choices?: Array<{
          message?: {
            content?: string | Array<{ type?: string; text?: string }>;
          };
        }>;
      };

      const content = data.choices?.[0]?.message?.content;
      if (typeof content === "string") {
        return content;
      }

      if (Array.isArray(content)) {
        return content
          .filter((part) => part.type === "text" && typeof part.text === "string")
          .map((part) => part.text)
          .join("\n");
      }

      return "";
    },
  };
}
