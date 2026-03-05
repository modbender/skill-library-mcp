// ========================
// SDK 配置 (交易脚本专用)
// ========================
//
// 仅交易脚本 import 此文件
// 需要 bun install 安装 @opinion-labs/opinion-clob-sdk

import {
  Client,
  CHAIN_ID_BNB_MAINNET,
  DEFAULT_API_HOST,
  OrderSide,
  OrderType,
} from "@opinion-labs/opinion-clob-sdk";

const PRIVATE_KEY = process.env.PRIVATE_KEY;
const MULTI_SIG_ADDRESS = process.env.MULTI_SIG_ADDRESS;
const API_KEY = process.env.API_KEY;
const BSC_RPC = process.env.BSC_RPC || "https://bsc-dataseed.binance.org";
const SDK_API_HOST = DEFAULT_API_HOST;

function getClient(): Client {
  if (!PRIVATE_KEY) {
    console.error("Error: set PRIVATE_KEY in .env");
    process.exit(1);
  }
  if (!MULTI_SIG_ADDRESS) {
    console.error("Error: set MULTI_SIG_ADDRESS in .env");
    process.exit(1);
  }
  if (!API_KEY) {
    console.error("Error: set API_KEY in .env");
    process.exit(1);
  }
  return new Client({
    host: SDK_API_HOST,
    apiKey: API_KEY,
    chainId: CHAIN_ID_BNB_MAINNET,
    rpcUrl: BSC_RPC,
    privateKey: PRIVATE_KEY as `0x${string}`,
    multiSigAddress: MULTI_SIG_ADDRESS as `0x${string}`,
  });
}

export {
  getClient,
  SDK_API_HOST,
  BSC_RPC,
  PRIVATE_KEY,
  MULTI_SIG_ADDRESS,
  API_KEY,
  OrderSide,
  OrderType,
  CHAIN_ID_BNB_MAINNET,
};
