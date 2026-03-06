export type ProviderId = "openai" | "gemini" | "claude" | "ollama";

export interface AIProvider {
  id: ProviderId;
  call(prompt: string): Promise<string>;
}
