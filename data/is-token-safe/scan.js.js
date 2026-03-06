// scan.js
// 사용법: node scan.js 0x토큰주소

const { ethers } = require("ethers");
const axios = require("axios");

async function main() {
  const token = process.argv[2];

  if (!token || token.length !== 42) {
    console.log("❌ 사용법: node scan.js 0x토큰주소");
    return;
  }

  // Base RPC (공짜)
  const provider = new ethers.JsonRpcProvider("https://mainnet.base.org");

  // 최소 ERC20 ABI
  const abi = [
    "function owner() view returns (address)",
    "function mint(address,uint256)",
    "function isBlacklisted(address) view returns (bool)",
    "function blacklist(address,bool)",
    "function setBlacklist(address,bool)"
  ];

  const contract = new ethers.Contract(token, abi, provider);

  /* =========================
     1️⃣ owner 체크
  ========================= */
  let owner = null;
  let owner_renounced = null;

  try {
    owner = await contract.owner();
    owner_renounced =
      owner.toLowerCase() ===
      "0x0000000000000000000000000000000000000000";
  } catch {
    owner = null;
    owner_renounced = null;
  }

  /* =========================
     2️⃣ mint 가능 여부
  ========================= */
  let mintable = false;
  try {
    contract.interface.getFunction("mint");
    mintable = true;
  } catch {
    mintable = false;
  }

  /* =========================
     3️⃣ blacklist 기능 여부
  ========================= */
  let blacklist_capable = false;

  try {
    contract.interface.getFunction("blacklist");
    blacklist_capable = true;
  } catch {
    try {
      contract.interface.getFunction("setBlacklist");
      blacklist_capable = true;
    } catch {
      blacklist_capable = false;
    }
  }

  /* =========================
     4️⃣ Honeypot / Tax (API)
     ⚠️ 무료 공개 API (데모용)
  ========================= */
  let honeypot = null;
  let buy_tax = null;
  let sell_tax = null;

  try {
    const res = await axios.get(
      `https://api.honeypot.is/v2/IsHoneypot`,
      {
        params: {
          address: token,
          chain: "base"
        }
      }
    );

    honeypot = res.data?.honeypotResult?.isHoneypot ?? null;
    buy_tax = res.data?.simulationResult?.buyTax ?? null;
    sell_tax = res.data?.simulationResult?.sellTax ?? null;
  } catch {
    honeypot = null;
    buy_tax = null;
    sell_tax = null;
  }

  /* =========================
     5️⃣ Risk 간단 평가
  ========================= */
  let risk = "LOW";

  if (honeypot === true) risk = "HIGH";
  if (blacklist_capable) risk = "MEDIUM";
  if (mintable && !owner_renounced) risk = "MEDIUM";

  /* =========================
     6️⃣ 결과 출력
  ========================= */
  const result = {
    token,
    honeypot,
    buy_tax: buy_tax !== null ? `${buy_tax}%` : null,
    sell_tax: sell_tax !== null ? `${sell_tax}%` : null,
    owner,
    owner_renounced,
    mintable,
    blacklist_capable,
    risk
  };

  console.log(JSON.stringify(result, null, 2));
}

main();
