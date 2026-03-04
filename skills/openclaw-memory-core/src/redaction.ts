import type { RedactionResult, Redactor } from "./types.js";

type Rule = {
  id: string;
  re: RegExp;
  replaceWith: string;
};

// Conservative patterns: detect common secret formats without over-matching.
const RULES: Rule[] = [
  // OpenAI: sk-... (classic) and sk-proj-... / sk-svcacct-... (new org keys)
  { id: "openai_api_key", re: /\bsk-(?:proj-|svcacct-)?[A-Za-z0-9]{20,}\b/g, replaceWith: "[REDACTED:OPENAI_KEY]" },
  // Anthropic: sk-ant-api03-...
  { id: "anthropic_api_key", re: /\bsk-ant-(?:api\d+-)?[A-Za-z0-9\-_]{20,}\b/g, replaceWith: "[REDACTED:ANTHROPIC_KEY]" },
  // Stripe live and test keys
  { id: "stripe_api_key", re: /\bsk_(?:live|test)_[A-Za-z0-9]{20,}\b/g, replaceWith: "[REDACTED:STRIPE_KEY]" },
  { id: "github_pat", re: /\bgithub_pat_[A-Za-z0-9_]{20,}\b/g, replaceWith: "[REDACTED:GITHUB_PAT]" },
  { id: "github_token", re: /\bgh[pous]_[A-Za-z0-9]{30,}\b/g, replaceWith: "[REDACTED:GITHUB_TOKEN]" },
  { id: "google_api_key", re: /\bAIzaSy[A-Za-z0-9_-]{20,}\b/g, replaceWith: "[REDACTED:GOOGLE_KEY]" },
  { id: "aws_access_key", re: /\bAKIA[0-9A-Z]{16}\b/g, replaceWith: "[REDACTED:AWS_ACCESS_KEY]" },
  { id: "aws_secret_key", re: /\b(?:AWS_SECRET_ACCESS_KEY|aws_secret_access_key)\b\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{30,}['\"]?/gi, replaceWith: "AWS_SECRET_ACCESS_KEY=[REDACTED]" },
  // Azure Storage account keys (base64, 88 chars ending in ==)
  { id: "azure_storage_key", re: /\bAccountKey=[A-Za-z0-9+/]{86}==\b/g, replaceWith: "AccountKey=[REDACTED:AZURE_KEY]" },
  // JWT: three base64url segments separated by dots
  { id: "jwt_token", re: /\bey[A-Za-z0-9\-_]{10,}\.[A-Za-z0-9\-_]{10,}\.[A-Za-z0-9\-_]{10,}\b/g, replaceWith: "[REDACTED:JWT]" },
  { id: "private_key_block", re: /-----BEGIN ([A-Z ]+)PRIVATE KEY-----[\s\S]*?-----END \1PRIVATE KEY-----/g, replaceWith: "[REDACTED:PRIVATE_KEY_BLOCK]" },
  // Bearer tokens
  { id: "bearer_token", re: /\bBearer\s+[A-Za-z0-9\-._~+/]+=*/g, replaceWith: "Bearer [REDACTED]" },
  // HashiCorp Vault service tokens
  { id: "vault_token", re: /\bhvs\.[A-Za-z0-9_-]{20,}\b/g, replaceWith: "[REDACTED:VAULT_TOKEN]" },
  // npm automation/granular tokens
  { id: "npm_token", re: /\bnpm_[A-Za-z0-9]{20,}\b/g, replaceWith: "[REDACTED:NPM_TOKEN]" },
  // Slack bot/user/app/workspace tokens
  { id: "slack_token", re: /\bxox[baprs]-[A-Za-z0-9\-]{10,}\b/g, replaceWith: "[REDACTED:SLACK_TOKEN]" },
  // SendGrid API keys
  { id: "sendgrid_api_key", re: /\bSG\.[A-Za-z0-9\-_]{20,}\.[A-Za-z0-9\-_]{20,}\b/g, replaceWith: "[REDACTED:SENDGRID_KEY]" },
  // Twilio account SIDs (prefixed AC + 32 hex chars - specific enough to avoid false positives)
  { id: "twilio_sid", re: /\bAC[0-9a-f]{32}\b/g, replaceWith: "[REDACTED:TWILIO_SID]" },
  // Generic password in common config patterns (key=value / key: value)
  { id: "generic_password", re: /\b(?:password|passwd|secret)\s*[:=]\s*['"]?[^\s'"]{8,}['"]?/gi, replaceWith: "password=[REDACTED]" },
  // HuggingFace tokens
  { id: "huggingface_token", re: /\bhf_[A-Za-z0-9]{20,}\b/g, replaceWith: "[REDACTED:HF_TOKEN]" },
  // Telegram bot tokens: <bot_id>:<35+ char key>
  { id: "telegram_bot_token", re: /\b\d{8,10}:[A-Za-z0-9_-]{35,}\b/g, replaceWith: "[REDACTED:TELEGRAM_TOKEN]" },
  // DB connection strings with embedded credentials
  { id: "db_connection_string", re: /\b(?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql|redis):\/\/[^:@\s]+:[^@\s]+@[^\s]+/gi, replaceWith: "[REDACTED:DB_CONN_STRING]" },
];

export class DefaultRedactor implements Redactor {
  redact(text: string): RedactionResult {
    let out = text;
    const matches: RedactionResult["matches"] = [];

    for (const rule of RULES) {
      const found = out.match(rule.re);
      if (found && found.length > 0) {
        // Store only rule id + count - never the actual matched text.
        matches.push({ rule: rule.id, count: found.length });
        out = out.replace(rule.re, rule.replaceWith);
      }
    }

    return {
      redactedText: out,
      hadSecrets: matches.length > 0,
      matches,
    };
  }
}
