/**
 * OpenClaw Plugin: Lunara Voice AI
 * ================================
 * Full integration with Lunara Voice AI External API v1 + ClawBot History & Analytics API.
 *
 * === Core Tools (External API) ===
 *   lunara_health          — API health check
 *   lunara_key_create      — Create API key (session auth)
 *   lunara_key_list        — List API keys  (session auth)
 *   lunara_key_revoke      — Revoke API key (session auth)
 *   lunara_key_delete      — Delete API key (session auth)
 *   lunara_agents_list     — List voice agents
 *   lunara_agent_get       — Get agent details
 *   lunara_agent_update    — Update agent config
 *   lunara_campaign_create — Create call campaign
 *   lunara_campaign_list   — List campaigns
 *   lunara_campaign_get    — Get campaign status
 *   lunara_campaign_start  — Start campaign call loop
 *   lunara_campaign_stop   — Stop running campaign
 *   lunara_call_single     — Make single outbound call
 *   lunara_docs            — Fetch API documentation
 *
 * === History & Analytics Tools (ClawBot API) ===
 *   lunara_history_health      — ClawBot History API health check
 *   lunara_history_list        — Get paginated call history with filters
 *   lunara_history_detail      — Get full call detail with transcript
 *   lunara_history_search      — Search call transcripts by text
 *   lunara_export_single       — Export single conversation (LLM format)
 *   lunara_export_bulk         — Bulk export conversations for LLM training
 *   lunara_analytics_dashboard — Get analytics dashboard with metrics
 *   lunara_analytics_save      — Save/update analytics for a conversation
 *   lunara_analytics_batch     — Batch save analytics for multiple conversations
 *   lunara_tags_add            — Add tags to a conversation
 *   lunara_tags_remove         — Remove a tag from a conversation
 *   lunara_webhook_create      — Create webhook subscription
 *   lunara_webhook_list        — List all webhooks
 *   lunara_webhook_update      — Update webhook settings
 *   lunara_webhook_delete      — Delete a webhook
 *   lunara_webhook_test        — Test webhook connectivity
 *   lunara_webhook_deliveries  — Get webhook delivery log
 *   lunara_clawbot_docs        — Fetch ClawBot API documentation
 */

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

interface PluginConfig {
  apiBaseUrl: string;
  apiKey: string;
  userEmail?: string;
}

function getConfig(api: any): PluginConfig {
  const cfg = api.config?.plugins?.entries?.["lunara-voice"]?.config;
  if (!cfg || !cfg.apiBaseUrl || !cfg.apiKey) {
    throw new Error(
      "Lunara Voice plugin is not configured. Set plugins.entries.lunara-voice.config with apiBaseUrl and apiKey.",
    );
  }
  return cfg as PluginConfig;
}

function baseUrl(cfg: PluginConfig): string {
  return cfg.apiBaseUrl.replace(/\/+$/, "") + "/api/v1";
}

/** ClawBot History API base URL. */
function clawbotUrl(cfg: PluginConfig): string {
  return cfg.apiBaseUrl.replace(/\/+$/, "") + "/api/v1/clawbot";
}

/** Standard Bearer-token headers. */
function bearerHeaders(cfg: PluginConfig): Record<string, string> {
  return {
    Authorization: `Bearer ${cfg.apiKey}`,
    "Content-Type": "application/json",
  };
}

/** Session headers (X-User-Email) for key management endpoints. */
function sessionHeaders(cfg: PluginConfig): Record<string, string> {
  if (!cfg.userEmail) {
    throw new Error(
      "userEmail is required for API key management. Set plugins.entries.lunara-voice.config.userEmail",
    );
  }
  return {
    "X-User-Email": cfg.userEmail,
    "Content-Type": "application/json",
  };
}

type ToolResult = { content: Array<{ type: "text"; text: string }> };

function textResult(text: string): ToolResult {
  return { content: [{ type: "text", text }] };
}

function jsonResult(data: unknown): ToolResult {
  return textResult(typeof data === "string" ? data : JSON.stringify(data, null, 2));
}

async function apiCall(
  url: string,
  options: RequestInit,
): Promise<{ status: number; body: any }> {
  try {
    const res = await fetch(url, options);
    let body: any;
    try {
      body = await res.json();
    } catch {
      body = { raw: await res.text() };
    }
    return { status: res.status, body };
  } catch (err: any) {
    return {
      status: 0,
      body: { success: false, error: `Network error: ${err.message || err}` },
    };
  }
}

const ALLOWED_VOICES = [
  "alloy",
  "ash",
  "ballad",
  "coral",
  "echo",
  "sage",
  "shimmer",
  "verse",
  "marin",
  "cedar",
] as const;

// ---------------------------------------------------------------------------
// Plugin entry point
// ---------------------------------------------------------------------------

export default function register(api: any) {
  const log = api.logger ?? console;

  // -----------------------------------------------------------------------
  // 1. lunara_health
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_health",
    description:
      "Check Lunara Voice AI API health status. No parameters required. Returns service status and timestamp.",
    parameters: { type: "object", properties: {}, required: [] },
    async execute() {
      const cfg = getConfig(api);
      const { body } = await apiCall(`${baseUrl(cfg)}/health`, { method: "GET" });
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 2. lunara_key_create
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_key_create",
    description:
      "Create a new Lunara API key. Requires userEmail in plugin config. The returned key is shown ONCE — save it immediately.",
    parameters: {
      type: "object",
      properties: {
        name: { type: "string", description: "Human-readable key name (max 200 chars)" },
        assistant_id: {
          type: "string",
          description: "Optional: bind key to a specific assistant ID",
        },
      },
      required: ["name"],
    },
    async execute(_id: string, params: { name: string; assistant_id?: string }) {
      const cfg = getConfig(api);
      const { status, body } = await apiCall(`${baseUrl(cfg)}/keys`, {
        method: "POST",
        headers: sessionHeaders(cfg),
        body: JSON.stringify({
          name: params.name,
          assistant_id: params.assistant_id || "",
        }),
      });
      if (body.success && body.api_key) {
        return textResult(
          `✅ API Key created!\n\n` +
            `🔑 Key: ${body.api_key}\n` +
            `📛 Name: ${body.name}\n` +
            `🆔 Key ID: ${body.key_id}\n\n` +
            `⚠️ SAVE THIS KEY NOW — it will NOT be shown again.`,
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 3. lunara_key_list
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_key_list",
    description:
      "List all API keys for the authenticated Lunara user. Shows key IDs, names, status, scopes.",
    parameters: { type: "object", properties: {}, required: [] },
    async execute() {
      const cfg = getConfig(api);
      const { body } = await apiCall(`${baseUrl(cfg)}/keys`, {
        method: "GET",
        headers: sessionHeaders(cfg),
      });
      if (body.success && body.keys) {
        const lines = body.keys.map(
          (k: any) =>
            `• ${k.prefix} | Name: ${k.name} | Status: ${k.status} | Env: ${k.env} | Created: ${k.created_at}`,
        );
        return textResult(
          `📋 API Keys (${body.count}/${body.limit} limit):\n\n${lines.join("\n")}`,
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 4. lunara_key_revoke
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_key_revoke",
    description: "Revoke (soft-delete) a Lunara API key by key_id. The key becomes inactive.",
    parameters: {
      type: "object",
      properties: {
        key_id: { type: "string", description: "The key_id (12-char hex) to revoke" },
      },
      required: ["key_id"],
    },
    async execute(_id: string, params: { key_id: string }) {
      const cfg = getConfig(api);
      const { body } = await apiCall(`${baseUrl(cfg)}/keys/${params.key_id}/revoke`, {
        method: "POST",
        headers: sessionHeaders(cfg),
      });
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 5. lunara_key_delete
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_key_delete",
    description: "Permanently delete a Lunara API key. This action cannot be undone.",
    parameters: {
      type: "object",
      properties: {
        key_id: { type: "string", description: "The key_id to delete permanently" },
      },
      required: ["key_id"],
    },
    async execute(_id: string, params: { key_id: string }) {
      const cfg = getConfig(api);
      const { body } = await apiCall(`${baseUrl(cfg)}/keys/${params.key_id}`, {
        method: "DELETE",
        headers: sessionHeaders(cfg),
      });
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 6. lunara_agents_list
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_agents_list",
    description:
      "List all voice agents (assistants) on the Lunara platform. Shows ID, name, voice, language, SIP config.",
    parameters: { type: "object", properties: {}, required: [] },
    async execute() {
      const cfg = getConfig(api);
      const { body } = await apiCall(`${baseUrl(cfg)}/agents`, {
        method: "GET",
        headers: bearerHeaders(cfg),
      });
      if (body.success && body.agents) {
        if (body.agents.length === 0) {
          return textResult("No agents found. Create one in the Lunara dashboard first.");
        }
        const lines = body.agents.map(
          (a: any) =>
            `• [${a.index}] ID: ${a.id}\n` +
            `  Name: ${a.name} | Voice: ${a.voice} | Lang: ${a.language}\n` +
            `  SIP: ${a.has_sip ? `${a.sip_provider} → ${a.sip_uri}` : "not configured"}`,
        );
        return textResult(`🤖 Voice Agents (${body.agents.length}):\n\n${lines.join("\n\n")}`);
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 7. lunara_agent_get
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_agent_get",
    description:
      "Get detailed info about a specific Lunara voice agent — prompt, voice, greeting, SIP config, minute balance.",
    parameters: {
      type: "object",
      properties: {
        assistant_id: { type: "string", description: "The assistant/agent ID" },
      },
      required: ["assistant_id"],
    },
    async execute(_id: string, params: { assistant_id: string }) {
      const cfg = getConfig(api);
      const { body } = await apiCall(`${baseUrl(cfg)}/agents/${params.assistant_id}`, {
        method: "GET",
        headers: bearerHeaders(cfg),
      });
      if (body.success && body.agent) {
        const a = body.agent;
        return textResult(
          `🤖 Agent: ${a.name}\n` +
            `🆔 ID: ${a.id}\n` +
            `🗣️ Voice: ${a.voice} | Language: ${a.language}\n` +
            `⏱️ Minutes balance: ${a.minutes_balance}\n` +
            `📞 SIP: ${a.has_sip ? `${a.sip_provider} → ${a.sip_uri}` : "not configured"}\n` +
            `👋 Greeting: ${a.greeting || "(none)"}\n` +
            `📝 Prompt (first 500 chars): ${(a.prompt || "").substring(0, 500)}${(a.prompt || "").length > 500 ? "..." : ""}`,
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 8. lunara_agent_update
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_agent_update",
    description:
      "Update a Lunara voice agent. Can change: prompt, greeting, voice (" +
      ALLOWED_VOICES.join(", ") +
      "), language, name, sip_provider, sip_uri, sip_headers. Only pass fields you want to change.",
    parameters: {
      type: "object",
      properties: {
        assistant_id: { type: "string", description: "The agent ID to update" },
        prompt: { type: "string", description: "New system prompt (max 50000 chars)" },
        greeting: { type: "string", description: "Greeting message when call connects" },
        voice: {
          type: "string",
          enum: [...ALLOWED_VOICES],
          description: "Voice model: " + ALLOWED_VOICES.join(", "),
        },
        language: { type: "string", description: "Language code (en, ru, es, etc.)" },
        name: { type: "string", description: "Display name" },
        sip_provider: { type: "string", description: "SIP connection type" },
        sip_uri: { type: "string", description: "SIP URI for outbound" },
        sip_headers: {
          type: "object",
          description: "Custom SIP headers (key-value object)",
          additionalProperties: { type: "string" },
        },
      },
      required: ["assistant_id"],
    },
    async execute(
      _id: string,
      params: {
        assistant_id: string;
        prompt?: string;
        greeting?: string;
        voice?: string;
        language?: string;
        name?: string;
        sip_provider?: string;
        sip_uri?: string;
        sip_headers?: Record<string, string>;
      },
    ) {
      const cfg = getConfig(api);

      // Client-side voice validation
      if (params.voice && !ALLOWED_VOICES.includes(params.voice as any)) {
        return textResult(
          `❌ Invalid voice "${params.voice}". Allowed: ${ALLOWED_VOICES.join(", ")}`,
        );
      }

      // Client-side prompt length validation
      if (params.prompt && params.prompt.length > 50000) {
        return textResult(
          `❌ Prompt too long (${params.prompt.length} chars). Maximum is 50000.`,
        );
      }

      // Build update payload — only changed fields
      const updateBody: Record<string, any> = {};
      const fields = [
        "prompt",
        "greeting",
        "voice",
        "language",
        "name",
        "sip_provider",
        "sip_uri",
        "sip_headers",
      ] as const;
      for (const f of fields) {
        if ((params as any)[f] !== undefined) {
          updateBody[f] = (params as any)[f];
        }
      }

      if (Object.keys(updateBody).length === 0) {
        return textResult("❌ No fields provided to update. Pass at least one field.");
      }

      const { body } = await apiCall(`${baseUrl(cfg)}/agents/${params.assistant_id}`, {
        method: "PATCH",
        headers: bearerHeaders(cfg),
        body: JSON.stringify(updateBody),
      });

      if (body.success) {
        return textResult(
          `✅ Agent ${params.assistant_id} updated.\n` +
            `Changed fields: ${body.message || Object.keys(updateBody).join(", ")}`,
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 9. lunara_campaign_create
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_campaign_create",
    description:
      "Create a call campaign on Lunara. Provide contacts as an array of phone numbers (strings) or objects " +
      'with {phone_number, name?, metadata?}. Max 10000 contacts per upload. Phone format: 7-15 digits, optional leading "+".',
    parameters: {
      type: "object",
      properties: {
        assistant_id: { type: "string", description: "Agent ID to use for calls" },
        name: { type: "string", description: "Campaign name (optional)" },
        contacts: {
          type: "array",
          description:
            'Array of phone numbers (strings) or objects {phone_number: string, name?: string, metadata?: object}. Example: ["+1234567890", "+0987654321"] or [{"phone_number": "+1234567890", "name": "John"}]',
          items: {
            oneOf: [
              { type: "string" },
              {
                type: "object",
                properties: {
                  phone_number: { type: "string" },
                  name: { type: "string" },
                  metadata: { type: "object" },
                },
                required: ["phone_number"],
              },
            ],
          },
        },
      },
      required: ["assistant_id", "contacts"],
    },
    async execute(
      _id: string,
      params: {
        assistant_id: string;
        name?: string;
        contacts: Array<string | { phone_number: string; name?: string; metadata?: object }>;
      },
    ) {
      const cfg = getConfig(api);

      if (!params.contacts || params.contacts.length === 0) {
        return textResult("❌ Contacts list is empty.");
      }
      if (params.contacts.length > 10000) {
        return textResult(
          `❌ Too many contacts (${params.contacts.length}). Maximum is 10000 per upload.`,
        );
      }

      const { body } = await apiCall(`${baseUrl(cfg)}/campaigns`, {
        method: "POST",
        headers: bearerHeaders(cfg),
        body: JSON.stringify({
          assistant_id: params.assistant_id,
          name: params.name || "OpenClaw Campaign",
          contacts: params.contacts,
        }),
      });

      if (body.success) {
        let msg =
          `✅ Campaign created!\n` +
          `🆔 Campaign ID: ${body.campaign_id}\n` +
          `📊 Valid contacts: ${body.total_contacts}\n` +
          `⚠️ Skipped (invalid): ${body.invalid_skipped}`;
        if (body.errors && body.errors.length > 0) {
          msg += `\n\nErrors:\n${body.errors.join("\n")}`;
        }
        msg += `\n\n💡 Use lunara_campaign_start with this campaign_id to begin calling.`;
        return textResult(msg);
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 10. lunara_campaign_list
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_campaign_list",
    description: "List all call campaigns for the authenticated Lunara user.",
    parameters: { type: "object", properties: {}, required: [] },
    async execute() {
      const cfg = getConfig(api);
      const { body } = await apiCall(`${baseUrl(cfg)}/campaigns`, {
        method: "GET",
        headers: bearerHeaders(cfg),
      });
      if (body.success && body.campaigns) {
        if (body.campaigns.length === 0) {
          return textResult("No campaigns found.");
        }
        const lines = body.campaigns.map(
          (c: any) =>
            `• ${c.name} (${c.status})\n` +
            `  ID: ${c.id}\n` +
            `  Progress: ${c.processed}/${c.total_contacts} | ✅ ${c.successful} | ❌ ${c.failed}\n` +
            `  Created: ${c.created_at}`,
        );
        return textResult(`📋 Campaigns (${body.campaigns.length}):\n\n${lines.join("\n\n")}`);
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 11. lunara_campaign_get
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_campaign_get",
    description:
      "Get detailed status of a specific Lunara campaign — progress, success/fail counts, status.",
    parameters: {
      type: "object",
      properties: {
        campaign_id: { type: "string", description: "Campaign UUID" },
      },
      required: ["campaign_id"],
    },
    async execute(_id: string, params: { campaign_id: string }) {
      const cfg = getConfig(api);
      const { body } = await apiCall(`${baseUrl(cfg)}/campaigns/${params.campaign_id}`, {
        method: "GET",
        headers: bearerHeaders(cfg),
      });
      if (body.success && body.campaign) {
        const c = body.campaign;
        const pct =
          c.total_contacts > 0
            ? ((c.processed / c.total_contacts) * 100).toFixed(1)
            : "0";
        const statusEmoji: Record<string, string> = {
          pending: "⏳",
          running: "▶️",
          paused: "⏸️",
          completed: "✅",
          failed: "❌",
          error: "🚨",
        };
        return textResult(
          `${statusEmoji[c.status] || "❓"} Campaign: ${c.name}\n` +
            `🆔 ID: ${c.id}\n` +
            `📊 Status: ${c.status.toUpperCase()}\n` +
            `👤 Agent: ${c.assistant_id}\n\n` +
            `Progress: ${c.processed}/${c.total_contacts} (${pct}%)\n` +
            `  ✅ Successful: ${c.successful}\n` +
            `  ❌ Failed: ${c.failed}\n` +
            `  ⏳ Remaining: ${c.total_contacts - c.processed}\n\n` +
            `Created: ${c.created_at}\n` +
            `Updated: ${c.updated_at}`,
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 12. lunara_campaign_start
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_campaign_start",
    description:
      "Start the call loop for a Lunara campaign. The system will begin calling contacts sequentially. " +
      "Returns 402 if the agent has insufficient minute balance.",
    parameters: {
      type: "object",
      properties: {
        campaign_id: { type: "string", description: "Campaign UUID to start" },
      },
      required: ["campaign_id"],
    },
    async execute(_id: string, params: { campaign_id: string }) {
      const cfg = getConfig(api);
      const { status, body } = await apiCall(
        `${baseUrl(cfg)}/campaigns/${params.campaign_id}/start`,
        {
          method: "POST",
          headers: bearerHeaders(cfg),
        },
      );
      if (status === 402) {
        return textResult(
          "⚠️ Insufficient minutes on agent balance. Top up minutes before starting the campaign.",
        );
      }
      if (body.success) {
        return textResult(
          `▶️ Campaign started!\n` +
            `🆔 ID: ${body.campaign_id}\n\n` +
            `💡 Use lunara_campaign_get to monitor progress.\n` +
            `💡 Use lunara_campaign_stop to pause if needed.`,
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 13. lunara_campaign_stop
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_campaign_stop",
    description: "Stop (pause) a running Lunara campaign. Can be restarted later.",
    parameters: {
      type: "object",
      properties: {
        campaign_id: { type: "string", description: "Campaign UUID to stop" },
      },
      required: ["campaign_id"],
    },
    async execute(_id: string, params: { campaign_id: string }) {
      const cfg = getConfig(api);
      const { body } = await apiCall(
        `${baseUrl(cfg)}/campaigns/${params.campaign_id}/stop`,
        {
          method: "POST",
          headers: bearerHeaders(cfg),
        },
      );
      if (body.success) {
        return textResult(`⏸️ Campaign stop signal sent. Status will change to "paused".`);
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 14. lunara_call_single
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_call_single",
    description:
      'Make a single outbound call via Lunara. Phone format: 7-15 digits with optional leading "+". ' +
      "Returns 402 if agent minute balance is zero.",
    parameters: {
      type: "object",
      properties: {
        to_number: {
          type: "string",
          description: 'Phone number to call (e.g. "+12125551234")',
        },
        assistant_id: {
          type: "string",
          description: "Agent ID to handle the call",
        },
      },
      required: ["to_number", "assistant_id"],
    },
    async execute(_id: string, params: { to_number: string; assistant_id: string }) {
      const cfg = getConfig(api);
      const { status, body } = await apiCall(`${baseUrl(cfg)}/calls/single`, {
        method: "POST",
        headers: bearerHeaders(cfg),
        body: JSON.stringify({
          to_number: params.to_number,
          assistant_id: params.assistant_id,
        }),
      });
      if (status === 402) {
        return textResult(
          "⚠️ Cannot place call — insufficient minutes on agent balance. Please top up.",
        );
      }
      if (body.success) {
        const sid = body.call_sid || body.sid || body.uniqueid || "N/A";
        return textResult(
          `📞 Call initiated!\n` +
            `📱 To: ${params.to_number}\n` +
            `🤖 Agent: ${params.assistant_id}\n` +
            `🆔 Call SID: ${sid}`,
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 15. lunara_docs
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_docs",
    description: "Fetch the full Lunara API documentation as structured JSON from the server.",
    parameters: { type: "object", properties: {}, required: [] },
    async execute() {
      const cfg = getConfig(api);
      const { body } = await apiCall(`${baseUrl(cfg)}/docs`, { method: "GET" });
      return jsonResult(body);
    },
  });

  // =======================================================================
  // ClawBot History & Analytics API Tools
  // =======================================================================

  // -----------------------------------------------------------------------
  // 16. lunara_history_health
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_history_health",
    description:
      "Check ClawBot History & Analytics API health status. Returns service status, available features, and timestamp.",
    parameters: { type: "object", properties: {}, required: [] },
    async execute() {
      const cfg = getConfig(api);
      const { body } = await apiCall(`${clawbotUrl(cfg)}/health`, { method: "GET" });
      if (body.status === "ok") {
        return textResult(
          `✅ ClawBot History API: ONLINE\n` +
            `🕐 ${body.timestamp}\n` +
            `📦 Features: ${(body.features || []).join(", ")}`,
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 17. lunara_history_list
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_history_list",
    description:
      "Get paginated call history for a Lunara voice agent. Supports filtering by date range, direction (inbound/outbound), " +
      "caller number, DID, duration range, audio availability, sentiment, resolution status, and tags. " +
      "Returns conversations with metadata, sentiment, summary, and pagination info.",
    parameters: {
      type: "object",
      properties: {
        assistant_id: { type: "string", description: "The agent/assistant ID to get history for" },
        page: { type: "number", description: "Page number (default 1)" },
        page_size: { type: "number", description: "Results per page, max 100 (default 50)" },
        date_from: { type: "string", description: "Start date filter (ISO 8601, e.g. 2026-01-01T00:00:00Z)" },
        date_to: { type: "string", description: "End date filter (ISO 8601)" },
        direction: { type: "string", enum: ["inbound", "outbound"], description: "Filter by call direction" },
        caller: { type: "string", description: "Filter by caller number (partial match)" },
        did: { type: "string", description: "Filter by DID number (partial match)" },
        min_duration: { type: "number", description: "Minimum call duration in seconds" },
        max_duration: { type: "number", description: "Maximum call duration in seconds" },
        has_audio: { type: "boolean", description: "Filter for calls with/without audio recording" },
        sentiment: {
          type: "string",
          enum: ["positive", "neutral", "negative", "mixed"],
          description: "Filter by sentiment label",
        },
        resolution_status: {
          type: "string",
          enum: ["resolved", "unresolved", "escalated", "pending"],
          description: "Filter by resolution status",
        },
        tags: {
          type: "string",
          description: "Comma-separated tags to filter by (e.g. 'vip,urgent')",
        },
        mask_pii: { type: "boolean", description: "Mask PII in results (default true)" },
      },
      required: ["assistant_id"],
    },
    async execute(
      _id: string,
      params: {
        assistant_id: string;
        page?: number;
        page_size?: number;
        date_from?: string;
        date_to?: string;
        direction?: string;
        caller?: string;
        did?: string;
        min_duration?: number;
        max_duration?: number;
        has_audio?: boolean;
        sentiment?: string;
        resolution_status?: string;
        tags?: string;
        mask_pii?: boolean;
      },
    ) {
      const cfg = getConfig(api);
      const qp = new URLSearchParams();
      if (params.page) qp.set("page", String(params.page));
      if (params.page_size) qp.set("page_size", String(params.page_size));
      if (params.date_from) qp.set("date_from", params.date_from);
      if (params.date_to) qp.set("date_to", params.date_to);
      if (params.direction) qp.set("direction", params.direction);
      if (params.caller) qp.set("caller", params.caller);
      if (params.did) qp.set("did", params.did);
      if (params.min_duration !== undefined) qp.set("min_duration", String(params.min_duration));
      if (params.max_duration !== undefined) qp.set("max_duration", String(params.max_duration));
      if (params.has_audio !== undefined) qp.set("has_audio", String(params.has_audio));
      if (params.sentiment) qp.set("sentiment", params.sentiment);
      if (params.resolution_status) qp.set("resolution_status", params.resolution_status);
      if (params.tags) qp.set("tags", params.tags);
      if (params.mask_pii !== undefined) qp.set("mask_pii", String(params.mask_pii));

      const qs = qp.toString();
      const url = `${clawbotUrl(cfg)}/history/${params.assistant_id}${qs ? "?" + qs : ""}`;
      const { body } = await apiCall(url, {
        method: "GET",
        headers: bearerHeaders(cfg),
      });

      if (body.success && body.data) {
        const pg = body.pagination || {};
        const lines = body.data.map(
          (c: any) =>
            `• ${c.created_at} | ${c.direction || "?"} | ${c.caller || "unknown"}\n` +
            `  ID: ${c.id}\n` +
            `  Duration: ${c.call_duration_seconds ?? "?"}s | Messages: ${c.message_count ?? "?"}\n` +
            `  Sentiment: ${c.sentiment_label || "n/a"} | Summary: ${(c.summary || "n/a").substring(0, 120)}`,
        );
        return textResult(
          `📋 Call History (page ${pg.page}/${pg.total_pages}, ${pg.total_records} total):\n\n` +
            lines.join("\n\n") +
            (pg.has_next ? `\n\n💡 More results available — use page=${pg.page + 1}` : ""),
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 18. lunara_history_detail
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_history_detail",
    description:
      "Get full details of a specific call including complete transcript, tags, sentiment analysis, summary, " +
      "quality score, and all metadata. Use this after lunara_history_list to drill into a specific conversation.",
    parameters: {
      type: "object",
      properties: {
        assistant_id: { type: "string", description: "The agent/assistant ID" },
        conversation_id: { type: "string", description: "The conversation ID to get details for" },
        include_transcript: { type: "boolean", description: "Include full message transcript (default true)" },
        mask_pii: { type: "boolean", description: "Mask PII in results (default true)" },
      },
      required: ["assistant_id", "conversation_id"],
    },
    async execute(
      _id: string,
      params: {
        assistant_id: string;
        conversation_id: string;
        include_transcript?: boolean;
        mask_pii?: boolean;
      },
    ) {
      const cfg = getConfig(api);
      const qp = new URLSearchParams();
      if (params.include_transcript !== undefined)
        qp.set("include_transcript", String(params.include_transcript));
      if (params.mask_pii !== undefined) qp.set("mask_pii", String(params.mask_pii));

      const qs = qp.toString();
      const url = `${clawbotUrl(cfg)}/history/${params.assistant_id}/${params.conversation_id}${qs ? "?" + qs : ""}`;
      const { body } = await apiCall(url, {
        method: "GET",
        headers: bearerHeaders(cfg),
      });

      if (body.success && body.conversation) {
        const c = body.conversation;
        let output =
          `📞 Call Detail: ${c.id}\n` +
          `🕐 ${c.created_at} | ${c.direction || "?"} | Duration: ${c.call_duration_seconds ?? "?"}s\n` +
          `📱 Caller: ${c.caller || "unknown"} → DID: ${c.did || "unknown"}\n` +
          `🎭 Sentiment: ${c.sentiment_label || "n/a"} (${c.sentiment_score ?? "n/a"})\n` +
          `📊 Quality: ${c.quality_score ?? "n/a"} | Resolution: ${c.resolution_status || "n/a"}\n` +
          `📝 Summary: ${c.summary || "n/a"}\n` +
          `🏷️ Topics: ${(c.topics || []).join(", ") || "none"}\n` +
          `🔖 Tags: ${(body.tags || []).map((t: any) => t.tag).join(", ") || "none"}`;

        if (body.transcript && body.transcript.length > 0) {
          output += `\n\n💬 Transcript (${body.transcript.length} messages):\n`;
          for (const msg of body.transcript) {
            const role = msg.role === "assistant" ? "🤖" : "👤";
            output += `${role} [${msg.timestamp || ""}] ${msg.content}\n`;
          }
        }
        return textResult(output);
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 19. lunara_history_search
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_history_search",
    description:
      "Search through call transcripts by text content. Finds conversations where messages contain the search query. " +
      "Useful for finding specific calls by topic, keyword, or phrase mentioned during the conversation.",
    parameters: {
      type: "object",
      properties: {
        assistant_id: { type: "string", description: "The agent/assistant ID" },
        search_text: { type: "string", description: "Text to search for in call transcripts" },
        page: { type: "number", description: "Page number (default 1)" },
        page_size: { type: "number", description: "Results per page (default 20)" },
        date_from: { type: "string", description: "Start date filter (ISO 8601)" },
        date_to: { type: "string", description: "End date filter (ISO 8601)" },
      },
      required: ["assistant_id", "search_text"],
    },
    async execute(
      _id: string,
      params: {
        assistant_id: string;
        search_text: string;
        page?: number;
        page_size?: number;
        date_from?: string;
        date_to?: string;
      },
    ) {
      const cfg = getConfig(api);
      const qp = new URLSearchParams();
      qp.set("search_text", params.search_text);
      if (params.page) qp.set("page", String(params.page));
      if (params.page_size) qp.set("page_size", String(params.page_size));
      if (params.date_from) qp.set("date_from", params.date_from);
      if (params.date_to) qp.set("date_to", params.date_to);

      const url = `${clawbotUrl(cfg)}/history/${params.assistant_id}?${qp.toString()}`;
      const { body } = await apiCall(url, {
        method: "GET",
        headers: bearerHeaders(cfg),
      });

      if (body.success && body.data) {
        const pg = body.pagination || {};
        if (body.data.length === 0) {
          return textResult(`🔍 No calls found matching "${params.search_text}".`);
        }
        const lines = body.data.map(
          (c: any) =>
            `• ${c.created_at} | ${c.caller || "unknown"}\n` +
            `  ID: ${c.id} | Duration: ${c.call_duration_seconds ?? "?"}s\n` +
            `  Summary: ${(c.summary || "n/a").substring(0, 150)}`,
        );
        return textResult(
          `🔍 Search results for "${params.search_text}" (${pg.total_records} found):\n\n` +
            lines.join("\n\n"),
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 20. lunara_export_single
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_export_single",
    description:
      "Export a single conversation in LLM-ready format. Formats: 'openai' (Chat Completions messages array), " +
      "'training' (JSONL fine-tuning format), 'raw' (full JSON with all data). " +
      "Useful for preparing call data for AI analysis or model training.",
    parameters: {
      type: "object",
      properties: {
        assistant_id: { type: "string", description: "The agent/assistant ID" },
        conversation_id: { type: "string", description: "The conversation ID to export" },
        format: {
          type: "string",
          enum: ["openai", "training", "raw"],
          description: "Export format: openai (default), training, or raw",
        },
        mask_pii: { type: "boolean", description: "Mask PII in export (default true)" },
      },
      required: ["assistant_id", "conversation_id"],
    },
    async execute(
      _id: string,
      params: {
        assistant_id: string;
        conversation_id: string;
        format?: string;
        mask_pii?: boolean;
      },
    ) {
      const cfg = getConfig(api);
      const qp = new URLSearchParams();
      if (params.format) qp.set("format", params.format);
      if (params.mask_pii !== undefined) qp.set("mask_pii", String(params.mask_pii));

      const qs = qp.toString();
      const url = `${clawbotUrl(cfg)}/export/${params.assistant_id}/${params.conversation_id}${qs ? "?" + qs : ""}`;
      const { body } = await apiCall(url, {
        method: "GET",
        headers: bearerHeaders(cfg),
      });

      if (body.success) {
        const fmt = body.format || params.format || "openai";
        const msgCount = body.messages?.length || body.example?.messages?.length || 0;
        return textResult(
          `📤 Export (${fmt}) — ${params.conversation_id}\n` +
            `Messages: ${msgCount}\n` +
            (body.metadata
              ? `Duration: ${body.metadata.duration_seconds ?? "?"}s | Sentiment: ${body.metadata.sentiment || "n/a"}\n`
              : "") +
            `\n${JSON.stringify(body, null, 2)}`,
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 21. lunara_export_bulk
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_export_bulk",
    description:
      "Bulk export multiple conversations for LLM training or analysis. Returns an array of formatted conversations. " +
      "Supports same filters as history_list. Max 10000 records per export.",
    parameters: {
      type: "object",
      properties: {
        assistant_id: { type: "string", description: "The agent/assistant ID" },
        format: {
          type: "string",
          enum: ["openai", "training", "raw"],
          description: "Export format (default: openai)",
        },
        limit: { type: "number", description: "Max conversations to export (default 100, max 10000)" },
        mask_pii: { type: "boolean", description: "Mask PII in export (default true)" },
        date_from: { type: "string", description: "Start date filter (ISO 8601)" },
        date_to: { type: "string", description: "End date filter (ISO 8601)" },
        direction: { type: "string", enum: ["inbound", "outbound"], description: "Filter by direction" },
        sentiment: { type: "string", description: "Filter by sentiment" },
        tags: { type: "string", description: "Comma-separated tags filter" },
      },
      required: ["assistant_id"],
    },
    async execute(
      _id: string,
      params: {
        assistant_id: string;
        format?: string;
        limit?: number;
        mask_pii?: boolean;
        date_from?: string;
        date_to?: string;
        direction?: string;
        sentiment?: string;
        tags?: string;
      },
    ) {
      const cfg = getConfig(api);
      const reqBody: any = {
        format: params.format || "openai",
        limit: params.limit || 100,
        mask_pii: params.mask_pii !== undefined ? params.mask_pii : true,
        filters: {} as Record<string, any>,
      };
      if (params.date_from) reqBody.filters.date_from = params.date_from;
      if (params.date_to) reqBody.filters.date_to = params.date_to;
      if (params.direction) reqBody.filters.direction = params.direction;
      if (params.sentiment) reqBody.filters.sentiment = params.sentiment;
      if (params.tags) reqBody.filters.tags = params.tags.split(",").map((t: string) => t.trim());

      const { body } = await apiCall(`${clawbotUrl(cfg)}/export/${params.assistant_id}/bulk`, {
        method: "POST",
        headers: bearerHeaders(cfg),
        body: JSON.stringify(reqBody),
      });

      if (body.success) {
        return textResult(
          `📤 Bulk Export Complete\n` +
            `Format: ${body.format}\n` +
            `Exported: ${body.exported} / ${body.total_available} available\n\n` +
            JSON.stringify(body.data, null, 2),
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 22. lunara_analytics_dashboard
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_analytics_dashboard",
    description:
      "Get a comprehensive analytics dashboard for a voice agent. Includes: total/inbound/outbound call counts, " +
      "average/min/max duration, sentiment distribution, resolution rates, top topics, " +
      "daily call breakdown, message statistics, quality scores, and top tags.",
    parameters: {
      type: "object",
      properties: {
        assistant_id: { type: "string", description: "The agent/assistant ID" },
        date_from: { type: "string", description: "Start date (ISO 8601)" },
        date_to: { type: "string", description: "End date (ISO 8601)" },
      },
      required: ["assistant_id"],
    },
    async execute(
      _id: string,
      params: { assistant_id: string; date_from?: string; date_to?: string },
    ) {
      const cfg = getConfig(api);
      const qp = new URLSearchParams();
      if (params.date_from) qp.set("date_from", params.date_from);
      if (params.date_to) qp.set("date_to", params.date_to);

      const qs = qp.toString();
      const url = `${clawbotUrl(cfg)}/analytics/${params.assistant_id}${qs ? "?" + qs : ""}`;
      const { body } = await apiCall(url, {
        method: "GET",
        headers: bearerHeaders(cfg),
      });

      if (body.success && body.statistics) {
        const s = body.statistics;
        const sentDist = s.sentiment_distribution || {};
        const resDist = s.resolution_distribution || {};
        const topics = (s.top_topics || []).slice(0, 10);
        const tags = (s.top_tags || []).slice(0, 10);

        let output =
          `📊 Analytics Dashboard — Agent: ${params.assistant_id}\n` +
          `📅 Period: ${body.period?.from || "all time"} → ${body.period?.to || "now"}\n\n` +
          `📞 Calls: ${s.total_calls} total (📥 ${s.inbound_calls} in / 📤 ${s.outbound_calls} out)\n` +
          `⏱️ Duration: avg ${s.avg_duration_seconds}s | min ${s.min_duration_seconds}s | max ${s.max_duration_seconds}s | total ${s.total_duration_seconds}s\n` +
          `🎙️ Audio recordings: ${s.calls_with_audio}\n` +
          `⭐ Avg quality score: ${s.avg_quality_score}\n\n` +
          `🎭 Sentiment: ${Object.entries(sentDist).map(([k, v]) => `${k}: ${v}`).join(" | ") || "n/a"}\n` +
          `✅ Resolution: ${Object.entries(resDist).map(([k, v]) => `${k}: ${v}`).join(" | ") || "n/a"}\n\n`;

        if (topics.length > 0) {
          output += `🔥 Top Topics:\n${topics.map((t: any) => `  • ${t.topic} (${t.count})`).join("\n")}\n\n`;
        }
        if (tags.length > 0) {
          output += `🏷️ Top Tags:\n${tags.map((t: any) => `  • ${t.tag} (${t.count})`).join("\n")}\n\n`;
        }

        const ms = s.message_stats || {};
        output +=
          `💬 Messages: ${ms.total_messages} total (👤 ${ms.user_messages} user / 🤖 ${ms.assistant_messages} assistant)\n` +
          `📏 Avg message length: ${ms.avg_message_length} chars`;

        if (body.hourly_distribution && body.hourly_distribution.length > 0) {
          const peak = body.hourly_distribution.reduce((a: any, b: any) =>
            a.count > b.count ? a : b,
          );
          output += `\n🕐 Peak hour: ${peak.hour}:00 (${peak.count} calls)`;
        }

        return textResult(output);
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 23. lunara_analytics_save
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_analytics_save",
    description:
      "Save or update analytics data for a specific conversation. Use this to record AI analysis results " +
      "like sentiment scores, summaries, topics, quality scores, and resolution status. " +
      "Can be called after analyzing a call transcript to persist the analysis.",
    parameters: {
      type: "object",
      properties: {
        assistant_id: { type: "string", description: "The agent/assistant ID" },
        conversation_id: { type: "string", description: "The conversation ID to save analytics for" },
        sentiment_score: {
          type: "number",
          description: "Sentiment score from -1.0 (negative) to 1.0 (positive)",
        },
        sentiment_label: {
          type: "string",
          enum: ["positive", "neutral", "negative", "mixed"],
          description: "Overall sentiment label",
        },
        topics: {
          type: "array",
          items: { type: "string" },
          description: "List of topics discussed in the call",
        },
        summary: { type: "string", description: "Human-readable summary of the conversation" },
        quality_score: {
          type: "number",
          description: "Quality score from 0.0 to 1.0",
        },
        resolution_status: {
          type: "string",
          enum: ["resolved", "unresolved", "escalated", "pending"],
          description: "How the call was resolved",
        },
        tags: {
          type: "array",
          items: { type: "string" },
          description: "Tags to associate with this analysis",
        },
        custom_metadata: {
          type: "object",
          description: "Any additional custom metadata as key-value pairs",
        },
      },
      required: ["assistant_id", "conversation_id"],
    },
    async execute(
      _id: string,
      params: {
        assistant_id: string;
        conversation_id: string;
        sentiment_score?: number;
        sentiment_label?: string;
        topics?: string[];
        summary?: string;
        quality_score?: number;
        resolution_status?: string;
        tags?: string[];
        custom_metadata?: Record<string, any>;
      },
    ) {
      const cfg = getConfig(api);
      const data: Record<string, any> = {};
      if (params.sentiment_score !== undefined) data.sentiment_score = params.sentiment_score;
      if (params.sentiment_label) data.sentiment_label = params.sentiment_label;
      if (params.topics) data.topics = params.topics;
      if (params.summary) data.summary = params.summary;
      if (params.quality_score !== undefined) data.quality_score = params.quality_score;
      if (params.resolution_status) data.resolution_status = params.resolution_status;
      if (params.tags) data.tags = params.tags;
      if (params.custom_metadata) data.custom_metadata = params.custom_metadata;

      const { body } = await apiCall(
        `${clawbotUrl(cfg)}/analytics/${params.assistant_id}/${params.conversation_id}`,
        {
          method: "PUT",
          headers: bearerHeaders(cfg),
          body: JSON.stringify(data),
        },
      );

      if (body.success) {
        return textResult(
          `✅ Analytics saved for conversation ${params.conversation_id}\n` +
            `Fields: ${Object.keys(data).join(", ")}`,
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 24. lunara_analytics_batch
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_analytics_batch",
    description:
      "Batch save analytics for multiple conversations at once. Each item needs a conversation_id and any analytics fields. " +
      "Max 500 items per batch. Useful for bulk post-processing of call data.",
    parameters: {
      type: "object",
      properties: {
        assistant_id: { type: "string", description: "The agent/assistant ID" },
        analyses: {
          type: "array",
          description:
            "Array of analytics objects. Each must have conversation_id plus optional: " +
            "sentiment_score, sentiment_label, topics, summary, quality_score, resolution_status, tags, custom_metadata",
          items: {
            type: "object",
            properties: {
              conversation_id: { type: "string" },
              sentiment_score: { type: "number" },
              sentiment_label: { type: "string" },
              topics: { type: "array", items: { type: "string" } },
              summary: { type: "string" },
              quality_score: { type: "number" },
              resolution_status: { type: "string" },
            },
            required: ["conversation_id"],
          },
        },
      },
      required: ["assistant_id", "analyses"],
    },
    async execute(
      _id: string,
      params: { assistant_id: string; analyses: any[] },
    ) {
      const cfg = getConfig(api);
      const { body } = await apiCall(
        `${clawbotUrl(cfg)}/analytics/${params.assistant_id}/batch`,
        {
          method: "POST",
          headers: bearerHeaders(cfg),
          body: JSON.stringify({ analyses: params.analyses }),
        },
      );

      if (body.success) {
        let msg = `✅ Batch analytics saved: ${body.saved} conversations processed`;
        if (body.errors && body.errors.length > 0) {
          msg += `\n⚠️ Errors (${body.errors.length}):\n${body.errors.join("\n")}`;
        }
        return textResult(msg);
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 25. lunara_tags_add
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_tags_add",
    description:
      "Add one or more tags to a conversation. Tags help categorize and filter calls. " +
      "Source can be 'manual' (user-assigned), 'auto' (system), or 'ai' (AI-generated). Max 50 tags per call.",
    parameters: {
      type: "object",
      properties: {
        assistant_id: { type: "string", description: "The agent/assistant ID" },
        conversation_id: { type: "string", description: "The conversation ID to tag" },
        tags: {
          type: "array",
          items: { type: "string" },
          description: "Array of tag strings to add (e.g. ['vip', 'follow-up', 'interested'])",
        },
        source: {
          type: "string",
          enum: ["manual", "auto", "ai"],
          description: "Tag source: manual (default), auto, or ai",
        },
      },
      required: ["assistant_id", "conversation_id", "tags"],
    },
    async execute(
      _id: string,
      params: {
        assistant_id: string;
        conversation_id: string;
        tags: string[];
        source?: string;
      },
    ) {
      const cfg = getConfig(api);
      const { body } = await apiCall(
        `${clawbotUrl(cfg)}/tags/${params.assistant_id}/${params.conversation_id}`,
        {
          method: "POST",
          headers: bearerHeaders(cfg),
          body: JSON.stringify({
            tags: params.tags,
            source: params.source || "manual",
          }),
        },
      );

      if (body.success) {
        return textResult(
          `🏷️ Tags added to ${params.conversation_id}: ${params.tags.join(", ")}`,
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 26. lunara_tags_remove
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_tags_remove",
    description: "Remove a specific tag from a conversation.",
    parameters: {
      type: "object",
      properties: {
        assistant_id: { type: "string", description: "The agent/assistant ID" },
        conversation_id: { type: "string", description: "The conversation ID" },
        tag: { type: "string", description: "The tag to remove" },
      },
      required: ["assistant_id", "conversation_id", "tag"],
    },
    async execute(
      _id: string,
      params: { assistant_id: string; conversation_id: string; tag: string },
    ) {
      const cfg = getConfig(api);
      const { body } = await apiCall(
        `${clawbotUrl(cfg)}/tags/${params.assistant_id}/${params.conversation_id}/${encodeURIComponent(params.tag)}`,
        {
          method: "DELETE",
          headers: bearerHeaders(cfg),
        },
      );

      if (body.success) {
        return textResult(`🏷️ Tag "${params.tag}" removed from ${params.conversation_id}`);
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 27. lunara_webhook_create
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_webhook_create",
    description:
      "Create a webhook subscription to receive real-time notifications for call events. " +
      "Supported events: call.started, call.completed, call.failed, analysis.completed, " +
      "campaign.started, campaign.completed, campaign.failed. URL must be HTTPS. " +
      "Returns a signing secret — save it to verify webhook payloads.",
    parameters: {
      type: "object",
      properties: {
        url: {
          type: "string",
          description: "Webhook endpoint URL (must be HTTPS)",
        },
        events: {
          type: "array",
          items: { type: "string" },
          description:
            "Events to subscribe to. Options: call.started, call.completed, call.failed, " +
            "analysis.completed, campaign.started, campaign.completed, campaign.failed",
        },
        assistant_id: {
          type: "string",
          description: "Optional: filter events for a specific agent only",
        },
      },
      required: ["url"],
    },
    async execute(
      _id: string,
      params: { url: string; events?: string[]; assistant_id?: string },
    ) {
      const cfg = getConfig(api);
      const reqBody: any = { url: params.url };
      if (params.events) reqBody.events = params.events;
      if (params.assistant_id) reqBody.assistant_id = params.assistant_id;

      const { body } = await apiCall(`${clawbotUrl(cfg)}/webhooks`, {
        method: "POST",
        headers: bearerHeaders(cfg),
        body: JSON.stringify(reqBody),
      });

      if (body.success && body.webhook) {
        const w = body.webhook;
        return textResult(
          `✅ Webhook created!\n` +
            `🆔 ID: ${w.id}\n` +
            `🔗 URL: ${w.url}\n` +
            `📡 Events: ${(w.events || []).join(", ")}\n` +
            `🔑 Secret: ${w.secret}\n\n` +
            `⚠️ SAVE THE SECRET — it signs webhook payloads (X-ClawBot-Signature header).`,
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 28. lunara_webhook_list
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_webhook_list",
    description: "List all webhook subscriptions for the authenticated user.",
    parameters: { type: "object", properties: {}, required: [] },
    async execute() {
      const cfg = getConfig(api);
      const { body } = await apiCall(`${clawbotUrl(cfg)}/webhooks`, {
        method: "GET",
        headers: bearerHeaders(cfg),
      });

      if (body.success && body.webhooks) {
        if (body.webhooks.length === 0) {
          return textResult("No webhooks configured.");
        }
        const lines = body.webhooks.map(
          (w: any) =>
            `• ${w.status === "active" ? "🟢" : w.status === "paused" ? "🟡" : "🔴"} ${w.url}\n` +
            `  ID: ${w.id} | Status: ${w.status}\n` +
            `  Events: ${(w.events || []).join(", ")}\n` +
            `  Failures: ${w.failure_count} | Last triggered: ${w.last_triggered || "never"}`,
        );
        return textResult(`📡 Webhooks (${body.webhooks.length}):\n\n${lines.join("\n\n")}`);
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 29. lunara_webhook_update
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_webhook_update",
    description:
      "Update webhook settings. Can change URL, events, status (active/paused/disabled), or assistant_id filter.",
    parameters: {
      type: "object",
      properties: {
        webhook_id: { type: "string", description: "Webhook UUID to update" },
        url: { type: "string", description: "New webhook URL (must be HTTPS)" },
        events: {
          type: "array",
          items: { type: "string" },
          description: "Updated event list",
        },
        status: {
          type: "string",
          enum: ["active", "paused", "disabled"],
          description: "New webhook status",
        },
        assistant_id: { type: "string", description: "Filter for specific agent" },
      },
      required: ["webhook_id"],
    },
    async execute(
      _id: string,
      params: {
        webhook_id: string;
        url?: string;
        events?: string[];
        status?: string;
        assistant_id?: string;
      },
    ) {
      const cfg = getConfig(api);
      const updates: Record<string, any> = {};
      if (params.url) updates.url = params.url;
      if (params.events) updates.events = params.events;
      if (params.status) updates.status = params.status;
      if (params.assistant_id) updates.assistant_id = params.assistant_id;

      if (Object.keys(updates).length === 0) {
        return textResult("❌ No fields to update. Provide at least one: url, events, status, or assistant_id.");
      }

      const { body } = await apiCall(`${clawbotUrl(cfg)}/webhooks/${params.webhook_id}`, {
        method: "PATCH",
        headers: bearerHeaders(cfg),
        body: JSON.stringify(updates),
      });

      if (body.success) {
        return textResult(`✅ Webhook ${params.webhook_id} updated: ${Object.keys(updates).join(", ")}`);
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 30. lunara_webhook_delete
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_webhook_delete",
    description: "Permanently delete a webhook subscription.",
    parameters: {
      type: "object",
      properties: {
        webhook_id: { type: "string", description: "Webhook UUID to delete" },
      },
      required: ["webhook_id"],
    },
    async execute(_id: string, params: { webhook_id: string }) {
      const cfg = getConfig(api);
      const { body } = await apiCall(`${clawbotUrl(cfg)}/webhooks/${params.webhook_id}`, {
        method: "DELETE",
        headers: bearerHeaders(cfg),
      });

      if (body.success) {
        return textResult(`✅ Webhook ${params.webhook_id} deleted.`);
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 31. lunara_webhook_test
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_webhook_test",
    description:
      "Send a test event to a webhook to verify connectivity and proper response. " +
      "Returns the delivery result including response code and body.",
    parameters: {
      type: "object",
      properties: {
        webhook_id: { type: "string", description: "Webhook UUID to test" },
      },
      required: ["webhook_id"],
    },
    async execute(_id: string, params: { webhook_id: string }) {
      const cfg = getConfig(api);
      const { body } = await apiCall(`${clawbotUrl(cfg)}/webhooks/${params.webhook_id}/test`, {
        method: "POST",
        headers: bearerHeaders(cfg),
      });

      if (body.success && body.test_result) {
        const t = body.test_result;
        return textResult(
          `${t.delivered ? "✅" : "❌"} Webhook test ${t.delivered ? "PASSED" : "FAILED"}\n` +
            `Response code: ${t.response_code || "N/A"}\n` +
            `Response: ${t.response_body || "N/A"}`,
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 32. lunara_webhook_deliveries
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_webhook_deliveries",
    description:
      "Get the delivery log for a webhook — see recent event deliveries, response codes, and success status.",
    parameters: {
      type: "object",
      properties: {
        webhook_id: { type: "string", description: "Webhook UUID" },
        limit: { type: "number", description: "Max deliveries to return (default 50, max 100)" },
      },
      required: ["webhook_id"],
    },
    async execute(_id: string, params: { webhook_id: string; limit?: number }) {
      const cfg = getConfig(api);
      const qp = new URLSearchParams();
      if (params.limit) qp.set("limit", String(params.limit));

      const qs = qp.toString();
      const url = `${clawbotUrl(cfg)}/webhooks/${params.webhook_id}/deliveries${qs ? "?" + qs : ""}`;
      const { body } = await apiCall(url, {
        method: "GET",
        headers: bearerHeaders(cfg),
      });

      if (body.success && body.deliveries) {
        if (body.deliveries.length === 0) {
          return textResult("No deliveries recorded for this webhook yet.");
        }
        const lines = body.deliveries.map(
          (d: any) =>
            `• ${d.success ? "✅" : "❌"} ${d.event_type} — ${d.delivered_at}\n` +
            `  Code: ${d.response_code || "N/A"}`,
        );
        return textResult(
          `📋 Webhook Deliveries (${body.deliveries.length}):\n\n${lines.join("\n")}`,
        );
      }
      return jsonResult(body);
    },
  });

  // -----------------------------------------------------------------------
  // 33. lunara_clawbot_docs
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "lunara_clawbot_docs",
    description:
      "Fetch the full ClawBot History & Analytics API documentation (OpenAPI 3.0 spec) as structured JSON.",
    parameters: { type: "object", properties: {}, required: [] },
    async execute() {
      const cfg = getConfig(api);
      const { body } = await apiCall(`${clawbotUrl(cfg)}/docs`, { method: "GET" });
      return jsonResult(body);
    },
  });

  log.info("[lunara-voice] Plugin registered — 33 tools available (15 core + 18 history/analytics)");
}
