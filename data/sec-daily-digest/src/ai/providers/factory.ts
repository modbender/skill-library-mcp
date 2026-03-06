import { createClaudeProvider } from "./claude";
import { createGeminiProvider } from "./gemini";
import { createOllamaProvider } from "./ollama";
import { createOpenAIProvider } from "./openai";
import { type AIProvider, type ProviderId } from "./types";

export function createProvider(
  provider: ProviderId | undefined,
  env: NodeJS.ProcessEnv,
  fetcher: typeof fetch = fetch,
): AIProvider {
  const selected = provider ?? "openai";

  switch (selected) {
    case "openai":
      return createOpenAIProvider(env, fetcher);
    case "gemini":
      return createGeminiProvider(env, fetcher);
    case "claude":
      return createClaudeProvider(env, fetcher);
    case "ollama":
      return createOllamaProvider(env, fetcher);
    default:
      throw new Error(`Unsupported provider: ${selected}`);
  }
}
