/**
 * Clawland Solana Scripts — Common utilities
 * 
 * Dependencies (auto-installed on first run):
 *   @solana/web3.js @coral-xyz/anchor @solana/spl-token
 */

const path = require('path');
const fs = require('fs');
const os = require('os');

const PROGRAM_ID_STR = 'B8qaN9epMbX3kbvmaeLDBd4RoxqQhdp5Jr6bYK6mJ9qZ';
const USDC_MINT_STR = '4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU';
const ADMIN_STR = 'DHK8iZT97vXdynQpSxQpDxSnmngUZSq3jUijXpcoQLkx';
const GAME_STATE_STR = '3Vmnk7c8APGrPWSgExuwUTKjAjSbDy8rUUTda3iRtsFk';
const GEM_MINT_STR = '3gcEHY79N4gNEFFMCemgTfEb2164HRUEXo8J6mL9GHSz';
const USDC_VAULT_STR = '5mXh7WkJNWgC49TRyF7MtjsGk5pDei9rmBeaQz6W6bYr';
const TREASURY_STR = '4HoQRJtrUAivcJH7KTDYNDYxpofGCDBByax21hiK2mne';
const RPC_URL = 'https://api.devnet.solana.com';
const CONFIG_DIR = path.join(os.homedir(), '.config', 'clawland');
const WALLET_PATH = path.join(CONFIG_DIR, 'wallet.json');

// Ensure dependencies
function ensureDeps() {
  const deps = ['@solana/web3.js', 'tweetnacl', 'bs58', '@solana/spl-token'];
  const missing = deps.some(d => { try { require.resolve(d, { paths: [__dirname] }); return false; } catch { return true; } });
  if (missing) {
    console.log('📦 Installing Solana dependencies (first run, ~15s)...');
    const { execSync } = require('child_process');
    execSync('npm init -y 2>/dev/null && npm install --silent @solana/web3.js@1 @coral-xyz/anchor @solana/spl-token bs58 tweetnacl', {
      cwd: __dirname,
      stdio: ['pipe', 'pipe', 'inherit'],
    });
    console.log('✅ Dependencies installed.\n');
  }
}

function getConnection() {
  ensureDeps();
  const { Connection } = require('@solana/web3.js');
  return new Connection(RPC_URL, 'confirmed');
}

function loadWallet() {
  if (!fs.existsSync(WALLET_PATH)) {
    console.error(`❌ Wallet not found at ${WALLET_PATH}`);
    console.error('Run: node setup-wallet.js');
    process.exit(1);
  }
  ensureDeps();
  const { Keypair } = require('@solana/web3.js');
  const secret = JSON.parse(fs.readFileSync(WALLET_PATH, 'utf8'));
  return Keypair.fromSecretKey(Uint8Array.from(secret));
}

function getProgramId() {
  ensureDeps();
  const { PublicKey } = require('@solana/web3.js');
  return new PublicKey(PROGRAM_ID_STR);
}

function getUsdcMint() {
  ensureDeps();
  const { PublicKey } = require('@solana/web3.js');
  return new PublicKey(USDC_MINT_STR);
}

function findPDA(seeds) {
  const { PublicKey } = require('@solana/web3.js');
  return PublicKey.findProgramAddressSync(
    seeds.map(s => typeof s === 'string' ? Buffer.from(s) : s),
    getProgramId()
  );
}

// Known deployed addresses (avoid PDA derivation errors)
function getGameState() { ensureDeps(); return new (require('@solana/web3.js').PublicKey)(GAME_STATE_STR); }
function getGemMint() { ensureDeps(); return new (require('@solana/web3.js').PublicKey)(GEM_MINT_STR); }
function getUsdcVault() { ensureDeps(); return new (require('@solana/web3.js').PublicKey)(USDC_VAULT_STR); }
function getTreasury() { ensureDeps(); return new (require('@solana/web3.js').PublicKey)(TREASURY_STR); }

function getApiKey() {
  const key = process.env.CLAWLAND_API_KEY;
  if (!key) {
    // Try reading from config
    const credPath = path.join(CONFIG_DIR, 'credentials.json');
    if (fs.existsSync(credPath)) {
      const cred = JSON.parse(fs.readFileSync(credPath, 'utf8'));
      return cred.api_key;
    }
    console.error('❌ CLAWLAND_API_KEY not set and no credentials.json found');
    process.exit(1);
  }
  return key;
}

module.exports = {
  PROGRAM_ID_STR, USDC_MINT_STR, ADMIN_STR, RPC_URL,
  CONFIG_DIR, WALLET_PATH,
  ensureDeps, getConnection, loadWallet,
  getProgramId, getUsdcMint, findPDA, getApiKey,
  getGameState, getGemMint, getUsdcVault, getTreasury,
};
