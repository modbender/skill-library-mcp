import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { API_URL, loadApiKey } from "../config.js";
import { register } from "./register.js";

const execFileAsync = promisify(execFile);

const EXCLUDE = [
  ".git",
  ".DS_Store",
  "node_modules",
  "dist",
  "__pycache__",
  ".venv",
  "venv",
  ".env",
  ".env.*",
  "*.pem",
  "*.key",
  "*.p12",
  "*.pfx",
  ".npmrc",
  ".pypirc",
  ".aws",
  ".ssh",
  ".idea",
  ".vscode",
];

export async function deploy(options: { name?: string }): Promise<void> {
  let apiKey = loadApiKey();
  if (!apiKey) {
    console.log("No API key found. Registering...");
    await register();
    apiKey = loadApiKey();
    if (!apiKey) {
      console.error("Registration failed. Could not obtain API key.");
      process.exit(1);
    }
  }

  console.log("Packaging project...");
  const excludeArgs = EXCLUDE.flatMap((e) => ["--exclude", e]);
  const { stdout: tarBuffer } = await execFileAsync(
    "tar",
    ["czf", "-", ...excludeArgs, "."],
    { cwd: process.cwd(), encoding: "buffer", maxBuffer: 100 * 1024 * 1024 }
  );

  let url = `${API_URL}/deploy`;
  if (options.name) {
    url += `?name=${encodeURIComponent(options.name)}`;
  }

  console.log(`Uploading tarball (${(tarBuffer.length / 1024).toFixed(1)} KB)...`);
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "x-api-key": apiKey,
      "content-type": "application/gzip"
    },
    body: tarBuffer
  });
  const data = await res.json();

  if (!res.ok) {
    console.error("Deploy failed:", data.error);
    process.exit(1);
  }

  console.log("Deployed to service:", data.service);
  if (data.expires_at) {
    console.log("Free tier: service will expire in 1 hour. Add credits for permanent deploys.");
  }
  if (data.domains?.length) {
    for (const d of data.domains) {
      console.log(`URL: https://${d}`);
    }
    console.log("Your service should be live shortly.");
  }
}
