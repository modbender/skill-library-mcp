import { promises as fs } from "node:fs";
import os from "node:os";
import path from "node:path";
import { setTimeout as sleep } from "node:timers/promises";
import { ConvexHttpClient } from "convex/browser";
import qrcode from "qrcode-terminal";
import YAML from "yaml";
import { v4 as uuidv4 } from "uuid";

const DEFAULT_GATEWAY_URL = "ws://127.0.0.1:18789";
const FASTCLAW_CONFIG_PATH = path.join(os.homedir(), ".openclaw", "fastclaw", "config.json");
const OPENCLAW_CONFIG_PATH = path.join(os.homedir(), ".openclaw", "config.yaml");

async function exists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

function parseJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

async function readFastclawConfig() {
  if (!(await exists(FASTCLAW_CONFIG_PATH))) return {};
  const raw = await fs.readFile(FASTCLAW_CONFIG_PATH, "utf8");
  return parseJson(raw) ?? {};
}

function pickGatewayTokenFromYaml(config) {
  const candidates = [
    config?.gatewayToken,
    config?.gateway?.token,
    config?.gateway?.auth?.token,
    config?.auth?.gatewayToken,
    config?.openclaw?.gatewayToken,
  ];

  for (const value of candidates) {
    if (typeof value === "string" && value.trim()) return value.trim();
  }

  return null;
}

async function readGatewayToken() {
  const envToken = process.env.OPENCLAW_GATEWAY_TOKEN;
  if (envToken && envToken.trim()) return envToken.trim();

  if (!(await exists(OPENCLAW_CONFIG_PATH))) return null;

  const raw = await fs.readFile(OPENCLAW_CONFIG_PATH, "utf8");
  const parsed = YAML.parse(raw);
  return pickGatewayTokenFromYaml(parsed);
}

async function saveFastclawConfig(config) {
  await fs.mkdir(path.dirname(FASTCLAW_CONFIG_PATH), { recursive: true });
  await fs.writeFile(FASTCLAW_CONFIG_PATH, `${JSON.stringify(config, null, 2)}\n`, "utf8");
}

async function main() {
  const existingConfig = await readFastclawConfig();

  const instanceId = existingConfig.instanceId ?? uuidv4();
  const instanceName =
    existingConfig.instanceName ??
    process.env.FASTCLAW_INSTANCE_NAME ??
    process.env.OPENCLAW_INSTANCE_NAME ??
    os.hostname();
  const convexUrl =
    process.env.FASTCLAW_CONVEX_URL ?? process.env.CONVEX_URL ?? existingConfig.convexUrl ?? null;
  const gatewayUrl = existingConfig.gatewayUrl ?? DEFAULT_GATEWAY_URL;
  const gatewayToken = (await readGatewayToken()) ?? existingConfig.gatewayToken ?? null;

  if (!convexUrl) {
    throw new Error(
      "Missing Convex URL. Set FASTCLAW_CONVEX_URL (or CONVEX_URL) before running pair."
    );
  }

  if (!gatewayToken) {
    throw new Error(
      "Missing gateway token. Set OPENCLAW_GATEWAY_TOKEN or add it to ~/.openclaw/config.yaml."
    );
  }

  const convex = new ConvexHttpClient(convexUrl);

  const { code } = await convex.mutation("pairing:createPairingCode", {
    instanceId,
    instanceName,
  });

  const qrPayload = JSON.stringify({ convexUrl, code });

  console.log("Scan this QR code in the FastClaw iOS app:\n");
  qrcode.generate(qrPayload, { small: true });
  console.log(`\nPairing code: ${code}`);
  console.log("Waiting for device to claim pairing code...");

  while (true) {
    const status = await convex.query("pairing:checkPairingStatus", { code });

    if (status?.status === "claimed") {
      const config = {
        instanceId,
        instanceName,
        convexUrl,
        gatewayUrl,
        gatewayToken,
      };

      await saveFastclawConfig(config);

      const deviceName = status?.deviceName ?? status?.deviceId ?? "Unknown device";
      console.log(`Pairing successful. Connected device: ${deviceName}`);
      console.log(`Saved config to ${FASTCLAW_CONFIG_PATH}`);
      return;
    }

    if (status?.status === "expired") {
      throw new Error("Pairing code expired before being claimed. Run the pair command again.");
    }

    if (status?.status === "not_found") {
      throw new Error("Pairing code not found. Run the pair command again.");
    }

    await sleep(2000);
  }
}

main().catch((err) => {
  console.error(err.message || err);
  process.exitCode = 1;
});
