import { type AIProvider } from "./types";

export function createClaudeProvider(env: NodeJS.ProcessEnv, fetcher: typeof fetch = fetch): AIProvider {
  const apiKey = env.ANTHROPIC_API_KEY?.trim();
  if (!apiKey) {
    throw new Error("ANTHROPIC_API_KEY is required for provider claude");
  }

  const model = env.CLAUDE_MODEL?.trim() || "claude-3-5-sonnet-latest";
  const endpoint = env.CLAUDE_API_BASE?.trim().replace(/\/+$/, "") || "https://api.anthropic.com/v1";

  return {
    id: "claude",
    async call(prompt: string): Promise<string> {
      const response = await fetcher(`${endpoint}/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": apiKey,
          "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify({
          model,
          max_tokens: 1024,
          messages: [{ role: "user", content: prompt }],
        }),
      });

      if (!response.ok) {
        const body = await response.text().catch(() => "");
        throw new Error(`Claude API error (${response.status}): ${body}`);
      }

      const data = await response.json() as {
        content?: Array<{ type?: string; text?: string }>;
      };

      return (data.content ?? [])
        .filter((part) => part.type === "text" && typeof part.text === "string")
        .map((part) => part.text as string)
        .join("\n");
    },
  };
}
