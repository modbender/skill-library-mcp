#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const GOLDSKY_ENDPOINT =
  "https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-core-base/prod/gn";
const DAPP_BASE = "https://www.aavegotchi.com";

const COLLATERAL_MAP = {
  Eth: ["0x20d3922b4a1a8560e1ac99fba4fade0c849e2142"],
  Aave: [
    "0x823cd4264c1b951c9209ad0deaea9988fe8429bf",
    "0x1d2a0e5ec8e5bbdca5cb219e649b565d8e5c3360"
  ],
  Dai: [
    "0xe0b22e0037b130a9f56bbb537684e6fa18192341",
    "0x27f8d03b3a2196956ed754badc28d73be8830a6e"
  ],
  USDC: [
    "0x1a13f4ca1d028320a707d99520abfefca3998b7f",
    "0x9719d867a500ef117cc201206b8ab51e794d3f82"
  ],
  Link: ["0x98ea609569bd25119707451ef982b90e3eb719cd"],
  USDT: [
    "0xdae5f1590db13e3b40423b5b5c5fbf175515910b",
    "0x60d55f02a771d515e077c9c2403a1ef324885cec"
  ],
  TUSD: ["0xf4b8888427b00d7caf21654408b7cba2ecf4ebd9"],
  Uni: ["0x8c8bdbe9cee455732525086264a4bf9cf821c498"],
  Yfi: ["0xe20f7d1f0ec39c4d5db01f53554f2ef54c71f613"],
  Polygon: ["0x8df3aad3a84da6b69a4da8aec3ea40d9091b2ac4"],
  wEth: ["0x28424507fefb6f7f8e9d3860f56504e4e5f5f390"],
  wBTC: ["0x5c2ed810328349100a66b82b78a1791b101c9d61"]
};

function parseArgs(argv) {
  const args = {
    tokenId: null,
    inventoryUrl: null,
    outDir: "/tmp"
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = argv[i + 1];

    if (arg === "--token-id" && next) {
      args.tokenId = Number(next);
      i += 1;
      continue;
    }
    if (arg === "--inventory-url" && next) {
      args.inventoryUrl = next;
      i += 1;
      continue;
    }
    if (arg === "--out-dir" && next) {
      args.outDir = next;
      i += 1;
      continue;
    }
    if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }

  return args;
}

function printHelp() {
  console.log(`Usage:
  node scripts/render-gotchi-bypass.mjs --token-id <id> [--out-dir /tmp]
  node scripts/render-gotchi-bypass.mjs --inventory-url "<url>" [--out-dir /tmp]

Options:
  --token-id       Numeric gotchi token id
  --inventory-url  Inventory URL containing id=<tokenId>
  --out-dir        Output folder for JSON and PNG files (default: /tmp)
`);
}

function tokenIdFromInventoryUrl(urlValue) {
  try {
    const parsed = new URL(urlValue);
    const id = parsed.searchParams.get("id");
    return id ? Number(id) : null;
  } catch {
    return null;
  }
}

function mapCollateral(address) {
  const normalized = String(address || "").toLowerCase();
  for (const [name, values] of Object.entries(COLLATERAL_MAP)) {
    if (values.includes(normalized)) return name;
  }
  return "Eth";
}

function deriveEyeShape(collateralAddress, numericTraits, hauntId) {
  const t4 = Number(numericTraits?.[4] ?? 0);
  const h = Number(hauntId ?? 1);

  if (t4 === 0) return h === 1 ? "MythicalLow1_H1" : "MythicalLow1_H2";
  if (t4 === 1) return h === 1 ? "MythicalLow2_H1" : "MythicalLow2_H2";
  if (t4 >= 2 && t4 <= 4) return "RareLow1";
  if (t4 >= 5 && t4 <= 6) return "RareLow2";
  if (t4 >= 7 && t4 <= 9) return "RareLow3";
  if (t4 >= 10 && t4 <= 14) return "UncommonLow1";
  if (t4 >= 15 && t4 <= 19) return "UncommonLow2";
  if (t4 >= 20 && t4 <= 24) return "UncommonLow3";
  if (t4 >= 25 && t4 <= 41) return "Common1";
  if (t4 >= 42 && t4 <= 57) return "Common2";
  if (t4 >= 58 && t4 <= 74) return "Common3";
  if (t4 >= 75 && t4 <= 79) return "UncommonHigh1";
  if (t4 >= 80 && t4 <= 84) return "UncommonHigh2";
  if (t4 >= 85 && t4 <= 89) return "UncommonHigh3";
  if (t4 >= 90 && t4 <= 92) return "RareHigh1";
  if (t4 >= 93 && t4 <= 94) return "RareHigh2";
  if (t4 >= 95 && t4 <= 97) return "RareHigh3";

  const collateral = mapCollateral(collateralAddress);
  const shapeByCollateral = {
    Eth: "ETH",
    Aave: "AAVE",
    Dai: "DAI",
    Uni: "UNI",
    Polygon: "POLYGON",
    Link: "LINK",
    wEth: "wETH",
    Yfi: "YFI",
    wBTC: "wBTC",
    TUSD: "TUSD",
    USDC: "USDC",
    USDT: "USDT"
  };
  return shapeByCollateral[collateral] || "ETH";
}

function deriveEyeColor(numericTraits) {
  const t5 = Number(numericTraits?.[5] ?? 0);
  if (t5 >= 0 && t5 <= 1) return "Mythical_Low";
  if (t5 >= 2 && t5 <= 9) return "Rare_Low";
  if (t5 >= 10 && t5 <= 24) return "Uncommon_Low";
  if (t5 >= 25 && t5 <= 74) return "Common";
  if (t5 >= 75 && t5 <= 90) return "Uncommon_High";
  if (t5 >= 91 && t5 <= 97) return "Rare_High";
  if (t5 >= 98 && t5 <= 99) return "Mythical_High";
  return "Common";
}

function deriveHash(gotchi) {
  const collateral = mapCollateral(gotchi.collateral);
  const eyeShape = deriveEyeShape(gotchi.collateral, gotchi.numericTraits, gotchi.hauntId);
  const eyeColor = deriveEyeColor(gotchi.numericTraits);

  const wearables = Array.isArray(gotchi.equippedWearables)
    ? gotchi.equippedWearables.slice(0, 7)
    : [];
  while (wearables.length < 7) wearables.push(0);

  const body = Number(wearables[0] || 0);
  const face = Number(wearables[1] || 0);
  const eyes = Number(wearables[2] || 0);
  const head = Number(wearables[3] || 0);
  const rightHand = Number(wearables[4] || 0);
  const leftHand = Number(wearables[5] || 0);
  const pet = Number(wearables[6] || 0);

  return [collateral, eyeShape, eyeColor, body, face, eyes, head, leftHand, rightHand, pet].join("-");
}

async function postJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  const text = await response.text();
  let json = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    json = null;
  }
  return { response, json, text };
}

async function downloadFile(url, filePath) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to download ${url} (${response.status})`);
  }
  const bytes = Buffer.from(await response.arrayBuffer());
  fs.writeFileSync(filePath, bytes);
  return filePath;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  let tokenId = options.tokenId;

  if (!Number.isInteger(tokenId) && options.inventoryUrl) {
    tokenId = tokenIdFromInventoryUrl(options.inventoryUrl);
  }
  if (!Number.isInteger(tokenId) || tokenId < 0) {
    printHelp();
    throw new Error("Provide --token-id <id> or --inventory-url with id=<tokenId>.");
  }

  fs.mkdirSync(options.outDir, { recursive: true });

  const graphQuery = {
    query:
      "query($ids:[String!]!){aavegotchis(where:{id_in:$ids}){id collateral hauntId numericTraits equippedWearables}}",
    variables: { ids: [String(tokenId)] }
  };
  const graphResult = await postJson(GOLDSKY_ENDPOINT, graphQuery);
  if (!graphResult.response.ok) {
    throw new Error(
      `Goldsky query failed (${graphResult.response.status}): ${graphResult.text.slice(0, 500)}`
    );
  }

  const gotchi = graphResult.json?.data?.aavegotchis?.[0];
  if (!gotchi) {
    throw new Error(`Gotchi ${tokenId} not found in Goldsky response.`);
  }

  const hash = deriveHash(gotchi);

  const batchPayload = {
    hashes: [hash],
    renderTypes: ["PNG_Full", "PNG_Headshot", "GLB_3DModel"],
    verify: true
  };
  const batchResult = await postJson(`${DAPP_BASE}/api/renderer/batch`, batchPayload);
  if (!batchResult.response.ok) {
    throw new Error(
      `Renderer batch failed (${batchResult.response.status}): ${batchResult.text.slice(0, 500)}`
    );
  }

  const batchJsonPath = path.join(options.outDir, `gotchi-${tokenId}-render-batch.json`);
  fs.writeFileSync(batchJsonPath, JSON.stringify(batchResult.json, null, 2));

  const firstResult = batchResult.json?.data?.results?.[0] || {};
  const proxyUrls = firstResult.proxyUrls || {};
  const artifacts = {};

  if (proxyUrls.PNG_Full) {
    const fullUrl = proxyUrls.PNG_Full.startsWith("http")
      ? proxyUrls.PNG_Full
      : `${DAPP_BASE}${proxyUrls.PNG_Full}`;
    artifacts.fullPngPath = path.join(options.outDir, `gotchi-${tokenId}-full.png`);
    await downloadFile(fullUrl, artifacts.fullPngPath);
    artifacts.fullPngUrl = fullUrl;
  }

  if (proxyUrls.PNG_Headshot) {
    const headshotUrl = proxyUrls.PNG_Headshot.startsWith("http")
      ? proxyUrls.PNG_Headshot
      : `${DAPP_BASE}${proxyUrls.PNG_Headshot}`;
    artifacts.headshotPngPath = path.join(options.outDir, `gotchi-${tokenId}-headshot.png`);
    await downloadFile(headshotUrl, artifacts.headshotPngPath);
    artifacts.headshotPngUrl = headshotUrl;
  }

  const summary = {
    tokenId,
    hash,
    goldskyStatus: graphResult.response.status,
    batchStatus: batchResult.response.status,
    responseFile: batchJsonPath,
    glb: firstResult?.availability?.GLB_3DModel || null,
    artifacts
  };

  console.log(JSON.stringify(summary, null, 2));
}

main().catch((error) => {
  console.error(error.message || error);
  process.exit(1);
});
