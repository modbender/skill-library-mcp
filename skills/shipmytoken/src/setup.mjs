import { Keypair } from "@solana/web3.js";
import bs58 from "bs58";
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import { readConfig, writeConfig, getKey } from "./config.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const LOCAL_VERSION = JSON.parse(
  readFileSync(join(__dirname, "..", "package.json"), "utf-8")
).version;

async function checkForUpdate() {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000);
    const base = "https://api.github.com/repos/new-ground/shipmytoken-skill";

    // Try releases first, fall back to tags
    let tag_name;
    const releaseRes = await fetch(`${base}/releases/latest`, {
      signal: controller.signal
    });
    if (releaseRes.ok) {
      ({ tag_name } = await releaseRes.json());
    } else {
      const tagsRes = await fetch(`${base}/tags?per_page=1`, {
        signal: controller.signal
      });
      if (!tagsRes.ok) { clearTimeout(timeout); return null; }
      const tags = await tagsRes.json();
      if (!tags.length) { clearTimeout(timeout); return null; }
      tag_name = tags[0].name;
    }
    clearTimeout(timeout);

    const latest = tag_name.replace(/^v/, "");
    const [lMaj, lMin, lPat] = latest.split(".").map(Number);
    const [cMaj, cMin, cPat] = LOCAL_VERSION.split(".").map(Number);
    const isNewer = lMaj > cMaj || (lMaj === cMaj && lMin > cMin) || (lMaj === cMaj && lMin === cMin && lPat > cPat);
    if (isNewer) {
      return {
        current: LOCAL_VERSION,
        latest,
        message: `Update available: v${latest}. Run: npx skills add new-ground/shipmytoken-skill --all`
      };
    }
  } catch {
    // Network error or timeout — silently skip
  }
  return null;
}

async function main() {
  const args = process.argv.slice(2);
  const isExport = args.includes("--export");

  if (isExport) {
    const privateKey = await getKey("SOLANA_PRIVATE_KEY");
    const publicKey = await getKey("SOLANA_PUBLIC_KEY");

    if (!privateKey || !publicKey) {
      console.log(JSON.stringify({
        success: false,
        error: "No wallet configured. Run setup without --export first."
      }));
      process.exit(1);
    }

    console.log(JSON.stringify({
      success: true,
      action: "export",
      publicKey,
      privateKey,
      warnings: [
        "Your private key controls all your funds and tokens.",
        "Anyone with this key can access your wallet.",
        "Only save it somewhere secure (password manager, encrypted note).",
        "Never share it with anyone.",
        "This is the only copy. If you lose it and your machine is wiped, your funds are gone forever."
      ]
    }));
    return;
  }

  const updateInfo = await checkForUpdate();

  const config = await readConfig();
  if (config.SOLANA_PRIVATE_KEY || process.env.SOLANA_PRIVATE_KEY) {
    console.log(JSON.stringify({
      success: true,
      action: "already_configured",
      publicKey: config.SOLANA_PUBLIC_KEY || process.env.SOLANA_PUBLIC_KEY,
      version: LOCAL_VERSION,
      message: "Wallet already configured.",
      ...(updateInfo && { update: updateInfo })
    }));
    return;
  }

  const wallet = Keypair.generate();
  const privateKey = bs58.encode(wallet.secretKey);
  const publicKey = wallet.publicKey.toBase58();

  await writeConfig("SOLANA_PRIVATE_KEY", privateKey);
  await writeConfig("SOLANA_PUBLIC_KEY", publicKey);

  console.log(JSON.stringify({
    success: true,
    action: "created",
    publicKey,
    version: LOCAL_VERSION,
    message: "Wallet created and saved to ~/.shipmytoken/config.json",
    ...(updateInfo && { update: updateInfo })
  }));
}

main().catch((err) => {
  console.log(JSON.stringify({ success: false, error: err.message }));
  process.exit(1);
});
