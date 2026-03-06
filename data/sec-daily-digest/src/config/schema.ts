export type ProviderId = "openai" | "gemini" | "claude" | "ollama";
export type OpmlProfile = "tiny" | "full";

export interface SecDigestConfig {
  provider: ProviderId;
  opml_profile: OpmlProfile;
  time_range_hours: number;
  top_n: number;
  output_language: "bilingual_zh_en";
  weights: {
    security: number;
    ai: number;
  };
}

export const DEFAULT_CONFIG: SecDigestConfig = {
  provider: "openai",
  opml_profile: "tiny",
  time_range_hours: 48,
  top_n: 20,
  output_language: "bilingual_zh_en",
  weights: {
    security: 0.5,
    ai: 0.5,
  },
};

export type ConfigPatch = Partial<SecDigestConfig>;
