/**
 * Configuration schema and types for OpenClaw Avatar
 */

export interface AvatarConfig {
  id: string;
  name: string;
  faceId: string;
  voiceId: string;
  default?: boolean;
  zoom?: number;
  top?: number;
}

export interface LanguageConfig {
  code: string;
  name: string;
  flag: string;
  default?: boolean;
}

export interface FillerConfig {
  [language: string]: {
    [category: string]: string[];
  };
}

export interface StreamDeckColors {
  blue: string;
  green: string;
  orange: string;
  teal: string;
  purple: string;
  indigo: string;
  slate: string;
  red: string;
  slack: string;
  dark: string;
}

export interface StreamDeckButtonPrompt {
  [action: string]: string;
}

export interface SlackIntegrationConfig {
  enabled: boolean;
  dmTargets?: string[];
  alertChannel?: string;
}

export interface EmailIntegrationConfig {
  enabled: boolean;
  recipient?: string;
}

export interface StreamDeckIntegrationConfig {
  enabled: boolean;
  colors?: Partial<StreamDeckColors>;
  buttonPrompts?: StreamDeckButtonPrompt;
}

export interface IntegrationsConfig {
  slack: SlackIntegrationConfig;
  email: EmailIntegrationConfig;
  streamDeck: StreamDeckIntegrationConfig;
}

export interface AppConfig {
  name: string;
  port: number;
}

export interface OpenClawConfig {
  gatewayUrl: string;
}

export interface SecretsConfig {
  simliApiKey: string;
  elevenLabsApiKey: string;
  elevenLabsVoiceId?: string;
  slackBotToken?: string;
  openclawToken?: string;
}

export interface Config {
  app: AppConfig;
  openclaw: OpenClawConfig;
  avatars: AvatarConfig[];
  languages: LanguageConfig[];
  fillers: FillerConfig;
  integrations: IntegrationsConfig;
  secrets: SecretsConfig;
}

export interface ClientConfig {
  app: AppConfig;
  avatars: AvatarConfig[];
  languages: LanguageConfig[];
  fillers: FillerConfig;
  simliApiKey: string;
}

/**
 * Validate that required configuration values are present
 */
export function validateConfig(config: Config): void {
  const errors: string[] = [];

  // Required secrets
  if (!config.secrets.simliApiKey) {
    errors.push('SIMLI_API_KEY environment variable is required');
  }
  if (!config.secrets.elevenLabsApiKey) {
    errors.push('ELEVENLABS_API_KEY environment variable is required');
  }

  // Must have at least one avatar
  if (!config.avatars || config.avatars.length === 0) {
    errors.push('At least one avatar must be configured');
  }

  // Must have at least one language
  if (!config.languages || config.languages.length === 0) {
    errors.push('At least one language must be configured');
  }

  // Validate avatars have required fields
  config.avatars?.forEach((avatar, i) => {
    if (!avatar.id) errors.push(`Avatar ${i}: id is required`);
    if (!avatar.name) errors.push(`Avatar ${i}: name is required`);
    if (!avatar.faceId) errors.push(`Avatar ${i}: faceId is required`);
    if (!avatar.voiceId) errors.push(`Avatar ${i}: voiceId is required`);
  });

  // Validate languages have required fields
  config.languages?.forEach((lang, i) => {
    if (!lang.code) errors.push(`Language ${i}: code is required`);
    if (!lang.name) errors.push(`Language ${i}: name is required`);
  });

  if (errors.length > 0) {
    throw new Error(`Configuration errors:\n  - ${errors.join('\n  - ')}`);
  }
}
