const http = require("http");
const { ethers } = require("ethers");
const crypto = require("crypto");

// === Config (set via env or edit here) ===
const PORT = process.env.PORT || 3456;
const SIGNER_PRIVATE_KEY = process.env.SIGNER_PRIVATE_KEY || "";
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS || "";
const CHAIN_ID = parseInt(process.env.CHAIN_ID || "56"); // BSC mainnet
const SIGNATURE_TTL = 300; // 5 minutes
const MINT_COOLDOWN = 15 * 60; // 15 minutes in seconds

// === State ===
const lastMintTime = {}; // address => timestamp

if (!SIGNER_PRIVATE_KEY) {
  console.error("ERROR: SIGNER_PRIVATE_KEY is required");
  process.exit(1);
}
if (!CONTRACT_ADDRESS) {
  console.error("ERROR: CONTRACT_ADDRESS is required");
  process.exit(1);
}

const signer = new ethers.Wallet(SIGNER_PRIVATE_KEY);
console.log(`[Server] Signer address: ${signer.address}`);
console.log(`[Server] Contract: ${CONTRACT_ADDRESS}`);
console.log(`[Server] Chain ID: ${CHAIN_ID}`);

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", c => body += c);
    req.on("end", () => {
      try { resolve(JSON.parse(body)); } catch(e) { reject(e); }
    });
  });
}

async function handleMintRequest(req, res) {
  try {
    const { wallet_address } = await parseBody(req);

    if (!wallet_address || !ethers.isAddress(wallet_address)) {
      return respond(res, 400, { error: "Invalid wallet_address" });
    }

    const addr = wallet_address.toLowerCase();
    const now = Math.floor(Date.now() / 1000);

    // Check cooldown (server-side, contract also enforces)
    if (lastMintTime[addr] && now - lastMintTime[addr] < MINT_COOLDOWN) {
      const remaining = MINT_COOLDOWN - (now - lastMintTime[addr]);
      return respond(res, 429, {
        error: "Cooldown not elapsed",
        retry_after_seconds: remaining
      });
    }

    // Generate nonce and deadline
    const nonce = "0x" + crypto.randomBytes(32).toString("hex");
    const deadline = now + SIGNATURE_TTL;

    // Sign: keccak256(abi.encodePacked(minter, nonce, deadline, chainId, contract))
    const messageHash = ethers.solidityPackedKeccak256(
      ["address", "bytes32", "uint256", "uint256", "address"],
      [wallet_address, nonce, deadline, CHAIN_ID, CONTRACT_ADDRESS]
    );

    const signature = await signer.signMessage(ethers.getBytes(messageHash));

    // Update cooldown
    lastMintTime[addr] = now;

    return respond(res, 200, {
      success: true,
      nonce,
      deadline,
      signature,
      contract: CONTRACT_ADDRESS,
      chain_id: CHAIN_ID
    });
  } catch(e) {
    console.error("[Error]", e.message);
    return respond(res, 500, { error: "Internal server error" });
  }
}

function respond(res, status, data) {
  res.writeHead(status, {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  });
  res.end(JSON.stringify(data));
}

const server = http.createServer((req, res) => {
  // CORS preflight
  if (req.method === "OPTIONS") {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    });
    return res.end();
  }

  if (req.method === "POST" && req.url === "/api/mint-signature") {
    return handleMintRequest(req, res);
  }

  if (req.method === "GET" && req.url === "/api/status") {
    return respond(res, 200, {
      signer: signer.address,
      contract: CONTRACT_ADDRESS,
      chain_id: CHAIN_ID,
      cooldown_seconds: MINT_COOLDOWN
    });
  }

  respond(res, 404, { error: "Not found" });
});

server.listen(PORT, () => {
  console.log(`[Server] 4Claw mint signer running on port ${PORT}`);
});
