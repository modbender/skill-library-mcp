const ENDPOINT = "https://api.ohmytoken.dev/api/v1/ingest";

export default function ohmytoken(config: { api_key: string }) {
  const key = config.api_key || process.env.OHMYTOKEN_API_KEY;
  if (!key) return {};

  return {
    name: "ohmytoken",
    async onLLMResponse(usage: {
      model: string;
      prompt_tokens: number;
      completion_tokens: number;
    }) {
      try {
        await fetch(ENDPOINT, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-API-Key": key,
          },
          body: JSON.stringify({
            model: usage.model || "unknown",
            prompt_tokens: usage.prompt_tokens || 0,
            completion_tokens: usage.completion_tokens || 0,
          }),
        });
      } catch {
        // silent — never break the user's workflow
      }
    },
  };
}
