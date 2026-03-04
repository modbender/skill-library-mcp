#!/usr/bin/env node
/**
 * Minimal Vapi REST helper.
 *
 * Usage:
 *   VAPI_API_KEY=... node skills/vapi/bin/vapi-api.mjs assistants:list
 */

const BASE = process.env.VAPI_BASE_URL || "https://api.vapi.ai";
const KEY = process.env.VAPI_API_KEY;

if (!KEY) {
  console.error("Missing VAPI_API_KEY env var");
  process.exit(2);
}

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const k = a.slice(2);
      const v = argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[++i] : "true";
      out[k] = v;
    } else {
      out._.push(a);
    }
  }
  return out;
}

async function req(path, { method = "GET", body } = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${KEY}`,
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!res.ok) {
    const msg = typeof data === "string" ? data : JSON.stringify(data, null, 2);
    throw new Error(`${res.status} ${res.statusText}: ${msg}`);
  }

  return data;
}

function print(data) {
  process.stdout.write(`${JSON.stringify(data, null, 2)}\n`);
}

const args = parseArgs(process.argv.slice(2));
const cmd = args._[0];

(async () => {
  switch (cmd) {
    case "assistants:list": {
      // Swagger lists /assistant as the assistants endpoint
      const data = await req("/assistant");
      print(data);
      return;
    }

    case "assistants:get": {
      const id = args.id || args._[1];
      if (!id) throw new Error("Usage: assistants:get --id <assistantId>");
      const data = await req(`/assistant/${encodeURIComponent(id)}`);
      print(data);
      return;
    }

    case "assistants:create": {
      const name = args.name;
      if (!name) throw new Error("Usage: assistants:create --name <name> [--modelProvider ...] [--model ...]");

      // NOTE: Assistant schema can evolve; prefer using swagger / MCP to craft full bodies.
      const body = {
        name,
      };

      // Convenience: allow common flags but don't pretend we cover all fields.
      if (args.modelProvider || args.model) {
        body.model = {
          provider: args.modelProvider || undefined,
          model: args.model || undefined,
        };
      }
      if (args.voiceProvider || args.voiceId) {
        body.voice = {
          provider: args.voiceProvider || undefined,
          voiceId: args.voiceId || undefined,
        };
      }

      const data = await req("/assistant", { method: "POST", body });
      print(data);
      return;
    }

    case "calls:list": {
      const data = await req("/call");
      print(data);
      return;
    }

    case "calls:get": {
      const id = args.id || args._[1];
      if (!id) throw new Error("Usage: calls:get --id <callId>");
      const data = await req(`/call/${encodeURIComponent(id)}`);
      print(data);
      return;
    }

    case "phoneNumbers:list": {
      const data = await req("/phone-number");
      print(data);
      return;
    }

    case "calls:create": {
      const assistantId = args.assistantId;
      const to = args.to;
      const customerId = args.customerId;

      const phoneNumberId = args.phoneNumberId;

      if (!assistantId) {
        throw new Error("Usage: calls:create --assistantId <id> ...");
      }

      if (!phoneNumberId) {
        throw new Error(
          "calls:create requires --phoneNumberId <id> (run: phoneNumbers:list)",
        );
      }

      if (!to && !customerId) {
        throw new Error(
          "calls:create requires either --to <E.164> (transient customer) or --customerId <id>",
        );
      }

      const body = {
        assistantId,
        phoneNumberId,
        ...(customerId ? { customerId } : {}),
        ...(to ? { customer: { number: to } } : {}),
      };

      const data = await req("/call", { method: "POST", body });
      print(data);
      return;
    }

    default: {
      console.error(
        [
          "Unknown command.",
          "Commands:",
          "  assistants:list",
          "  assistants:get --id ...",
          "  assistants:create --name ... [--modelProvider ... --model ... --voiceProvider ... --voiceId ...]",
          "  calls:list",
          "  calls:get --id ...",
          "  phoneNumbers:list",
          "  calls:create --assistantId ... --phoneNumberId ... --to <E.164>",
          "    (or: --customerId <id>)",
        ].join("\n"),
      );
      process.exit(1);
    }
  }
})().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
