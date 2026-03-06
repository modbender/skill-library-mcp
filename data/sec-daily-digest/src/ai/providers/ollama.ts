import { type AIProvider } from "./types";

export function createOllamaProvider(env: NodeJS.ProcessEnv, fetcher: typeof fetch = fetch): AIProvider {
  const base = (env.OLLAMA_API_BASE?.trim() || "http://127.0.0.1:11434").replace(/\/+$/, "");
  const model = env.OLLAMA_MODEL?.trim() || "llama3.1";

  return {
    id: "ollama",
    async call(prompt: string): Promise<string> {
      const response = await fetcher(`${base}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model,
          stream: false,
          messages: [{ role: "user", content: prompt }],
        }),
      });

      if (!response.ok) {
        const body = await response.text().catch(() => "");
        throw new Error(`Ollama API error (${response.status}): ${body}`);
      }

      const data = await response.json() as {
        message?: {
          content?: string;
        };
      };

      return data.message?.content ?? "";
    },
  };
}
