/* ═══════════════════════════════════════════════════════════════
   EXOSKELETONS — Core JavaScript Module
   Contract interaction, wallet connect, SVG preview, utilities
   ═══════════════════════════════════════════════════════════════ */

// ── Contract Addresses ──
const CONTRACTS = {
  core: '0x8241BDD5009ed3F6C99737D2415994B58296Da0d',
  renderer: '0xE559f88f124AA2354B1570b85f6BE9536B6D60bC',
  registry: '0x46fd56417dcd08cA8de1E12dd6e7f7E1b791B3E9',
  wallet: '0x78aF4B6D78a116dEDB3612A30365718B076894b9',
};

const MULTICALL3 = '0xcA11bde05977b3631167028862bE2a173976CA11';
const CHAIN_ID = 8453;
const CHAIN_ID_HEX = '0x2105';
const RPC_URLS = ['https://mainnet.base.org', 'https://base.llamarpc.com'];

// ── Visual Config Constants ──
const SHAPES = ['Hexagon', 'Circle', 'Diamond', 'Shield', 'Octagon', 'Triangle'];
const SYMBOLS = ['None', 'Eye', 'Gear', 'Bolt', 'Star', 'Wave', 'Node', 'Diamond'];
const PATTERNS = ['None', 'Grid', 'Dots', 'Lines', 'Circuits', 'Rings'];

// ── ABI Fragments (ethers.js format) ──
const CORE_ABI = [
  'function mint(bytes config) payable',
  'function getMintPrice() view returns (uint256)',
  'function getMintPhase() view returns (string)',
  'function nextTokenId() view returns (uint256)',
  'function totalSupply() view returns (uint256)',
  'function mintCount(address) view returns (uint256)',
  'function usedFreeMint(address) view returns (bool)',
  'function whitelist(address) view returns (bool)',
  'function setName(uint256 tokenId, string name)',
  'function setBio(uint256 tokenId, string bio)',
  'function setVisualConfig(uint256 tokenId, bytes config)',
  'function getIdentity(uint256 tokenId) view returns (string name, string bio, bytes visualConfig, string customVisualKey, uint256 mintedAt, bool genesis)',
  'function isGenesis(uint256 tokenId) view returns (bool)',
  'function ownerOf(uint256 tokenId) view returns (address)',
  'function balanceOf(address owner) view returns (uint256)',
  'function tokenOfOwnerByIndex(address owner, uint256 index) view returns (uint256)',
  'function sendMessage(uint256 fromToken, uint256 toToken, bytes32 channel, uint8 msgType, bytes payload)',
  'function getMessageCount() view returns (uint256)',
  'function getChannelMessageCount(bytes32 channel) view returns (uint256)',
  'function getInboxCount(uint256 tokenId) view returns (uint256)',
  'function messages(uint256 index) view returns (uint256 fromToken, uint256 toToken, bytes32 channel, uint8 msgType, bytes payload, uint256 timestamp)',
  'function tokenInbox(uint256 tokenId, uint256 index) view returns (uint256)',
  'function setData(uint256 tokenId, bytes32 key, bytes value)',
  'function getData(uint256 tokenId, bytes32 key) view returns (bytes)',
  'function getReputationScore(uint256 tokenId) view returns (uint256)',
  'function getReputation(uint256 tokenId) view returns (uint256 messagesSent, uint256 storageWrites, uint256 modulesActive, uint256 age)',
  'function activateModule(uint256 tokenId, bytes32 moduleName) payable',
  'function deactivateModule(uint256 tokenId, bytes32 moduleName)',
  'function isModuleActive(uint256 tokenId, bytes32 moduleName) view returns (bool)',
  'function moduleRegistry(bytes32) view returns (address contractAddress, bool premium, uint256 premiumCost, bool exists)',
];

const REGISTRY_ABI = [
  'function resolveByName(string name) view returns (uint256)',
  'function getName(uint256 tokenId) view returns (string)',
  'function getProfile(uint256 tokenId) view returns (string name, string bio, bool genesis, uint256 age, uint256 messagesSent, uint256 storageWrites, uint256 modulesActive, uint256 reputationScore, address owner)',
  'function getNetworkStats() view returns (uint256 totalMinted, uint256 totalMessages)',
  'function getReputationBatch(uint256 startId, uint256 count) view returns (uint256[] tokenIds, uint256[] scores)',
  'function getActiveModulesForToken(uint256 tokenId) view returns (bytes32[])',
  'function getTrackedModules() view returns (bytes32[])',
  'function trackedModuleCount() view returns (uint256)',
  'function moduleLabels(bytes32 moduleName) view returns (string)',
];

const RENDERER_ABI = [
  'function renderSVG(uint256 tokenId) view returns (string)',
];

const WALLET_ABI = [
  'function activateWallet(uint256 tokenId) returns (address)',
  'function getWalletAddress(uint256 tokenId) view returns (address)',
  'function hasWallet(uint256 tokenId) view returns (bool)',
];

// ── Provider & Contracts (initialized after ethers loads) ──
let provider = null;
let contracts = {};
let rpcIndex = 0;

function initProvider() {
  if (provider) return;
  if (typeof ethers === 'undefined') {
    console.error('ethers.js not loaded');
    return;
  }
  provider = new ethers.JsonRpcProvider(RPC_URLS[0]);
  contracts = {
    core: new ethers.Contract(CONTRACTS.core, CORE_ABI, provider),
    registry: new ethers.Contract(CONTRACTS.registry, REGISTRY_ABI, provider),
    renderer: new ethers.Contract(CONTRACTS.renderer, RENDERER_ABI, provider),
    wallet: new ethers.Contract(CONTRACTS.wallet, WALLET_ABI, provider),
  };
}

// Fallback RPC on failure
async function withFallback(fn) {
  try {
    return await fn();
  } catch (e) {
    if (rpcIndex < RPC_URLS.length - 1) {
      rpcIndex++;
      provider = new ethers.JsonRpcProvider(RPC_URLS[rpcIndex]);
      contracts.core = new ethers.Contract(CONTRACTS.core, CORE_ABI, provider);
      contracts.registry = new ethers.Contract(CONTRACTS.registry, REGISTRY_ABI, provider);
      contracts.renderer = new ethers.Contract(CONTRACTS.renderer, RENDERER_ABI, provider);
      contracts.wallet = new ethers.Contract(CONTRACTS.wallet, WALLET_ABI, provider);
      return await fn();
    }
    throw e;
  }
}

// Retry with delay (public RPCs throttle parallel calls)
async function withRetry(fn, retries = 2, delay = 300) {
  for (let i = 0; i <= retries; i++) {
    try { return await fn(); }
    catch (e) {
      if (i === retries) throw e;
      await new Promise(r => setTimeout(r, delay * (i + 1)));
    }
  }
}

// ── Multicall3: batch all RPC calls into one request ──
const MULTICALL_ABI = [
  'function tryAggregate(bool requireSuccess, tuple(address target, bytes callData)[] calls) view returns (tuple(bool success, bytes returnData)[])',
];
let _profileIface = null;
let _identityIface = null;
function getIfaces() {
  if (!_profileIface) _profileIface = new ethers.Interface(REGISTRY_ABI);
  if (!_identityIface) _identityIface = new ethers.Interface(CORE_ABI);
  return { profileIface: _profileIface, identityIface: _identityIface };
}

async function loadTokenBatch(ids) {
  if (ids.length === 0) return [];

  const mc = new ethers.Contract(MULTICALL3, MULTICALL_ABI, provider);
  const calls = [];
  for (const id of ids) {
    calls.push({
      target: CONTRACTS.registry,
      callData: getIfaces().profileIface.encodeFunctionData('getProfile', [id]),
    });
    calls.push({
      target: CONTRACTS.core,
      callData: getIfaces().identityIface.encodeFunctionData('getIdentity', [id]),
    });
  }

  const results = await mc.tryAggregate(false, calls);
  const tokens = [];

  for (let i = 0; i < ids.length; i++) {
    const profResult = results[i * 2];
    const idResult = results[i * 2 + 1];
    const id = ids[i];
    let token = { id, name: '', genesis: false, repScore: 0, visualConfig: null };

    if (profResult.success) {
      try {
        const p = getIfaces().profileIface.decodeFunctionResult('getProfile', profResult.returnData);
        token.name = p.name;
        token.bio = p.bio;
        token.genesis = p.genesis;
        token.repScore = Number(p.reputationScore);
        token.messagesSent = Number(p.messagesSent);
        token.storageWrites = Number(p.storageWrites);
        token.modulesActive = Number(p.modulesActive);
        token.age = Number(p.age);
        token.owner = p.owner;
      } catch (e) {}
    }

    if (idResult.success) {
      try {
        const d = getIfaces().identityIface.decodeFunctionResult('getIdentity', idResult.returnData);
        token.visualConfig = ethers.hexlify(d.visualConfig);
      } catch (e) {}
    }

    tokens.push(token);
  }
  return tokens;
}

// ── Token Cache (localStorage) ──
const CACHE_KEY = 'exo_tokens';
const CACHE_TTL = 60000; // 1 minute

function getCachedTokens() {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    const cached = JSON.parse(raw);
    if (Date.now() - cached.ts > CACHE_TTL) return null;
    return cached.tokens;
  } catch (e) { return null; }
}

function setCachedTokens(tokens) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify({ ts: Date.now(), tokens }));
  } catch (e) {}
}

// Load all tokens with cache
async function loadAllTokens() {
  const cached = getCachedTokens();
  if (cached) return cached;

  const stats = await withFallback(() => contracts.registry.getNetworkStats());
  const total = Number(stats.totalMinted);
  if (total === 0) return [];

  const ids = Array.from({ length: total }, (_, i) => i + 1);
  const tokens = await loadTokenBatch(ids);
  setCachedTokens(tokens);
  return tokens;
}

// Render SVG from a token's data (profile + visualConfig)
function renderTokenSVG(token) {
  if (!token.visualConfig) return null;
  try {
    const hex = typeof token.visualConfig === 'string' ? token.visualConfig : ethers.hexlify(token.visualConfig);
    const cfg = parseVisualConfig(hex);
    if (!cfg) return null;
    const inner = renderSVGPreview(
      [cfg.shape, cfg.pr, cfg.pg, cfg.pb, cfg.sr, cfg.sg, cfg.sb, cfg.symbol, cfg.pattern],
      { genesis: token.genesis, tokenId: token.id, name: token.name || '#' + token.id,
        msgs: token.messagesSent || 0, sto: token.storageWrites || 0,
        mods: token.modulesActive || 0, repScore: token.repScore || 0, ageBlocks: token.age || 0 }
    );
    return `<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">${inner}</svg>`;
  } catch (e) { return null; }
}

// ── Wallet Connection ──
let walletAccount = null;
let walletProvider = null;
let walletSigner = null;
const eip6963Providers = [];

// Listen for EIP-6963 providers
if (typeof window !== 'undefined') {
  window.addEventListener('eip6963:announceProvider', (e) => {
    eip6963Providers.push(e.detail);
  });
  try { window.dispatchEvent(new Event('eip6963:requestProvider')); } catch (e) {}
}

function isMobile() {
  return /Android|iPhone|iPad|iPod|Opera Mini|IEMobile/i.test(navigator.userAgent);
}

async function connectWallet() {
  let p = eip6963Providers.length ? eip6963Providers[0].provider : window.ethereum;
  if (!p) {
    await new Promise(r => setTimeout(r, 500));
    p = window.ethereum;
  }
  if (!p) {
    if (isMobile()) throw new Error('Open this page in your wallet browser (MetaMask, Rainbow, etc.)');
    throw new Error('No wallet detected. Install MetaMask or use a Web3 browser.');
  }

  const accts = await p.request({ method: 'eth_requestAccounts' });
  walletAccount = accts[0];

  // Switch to Base
  try {
    await p.request({ method: 'wallet_switchEthereumChain', params: [{ chainId: CHAIN_ID_HEX }] });
  } catch (e) {
    if (e.code === 4902) {
      await p.request({
        method: 'wallet_addEthereumChain',
        params: [{
          chainId: CHAIN_ID_HEX,
          chainName: 'Base',
          nativeCurrency: { name: 'ETH', symbol: 'ETH', decimals: 18 },
          rpcUrls: ['https://mainnet.base.org'],
          blockExplorerUrls: ['https://basescan.org'],
        }],
      });
    } else if (e.code !== 4001) throw e;
  }

  const cid = await p.request({ method: 'eth_chainId' });
  if (cid !== CHAIN_ID_HEX) throw new Error('Please switch to Base network');

  walletProvider = new ethers.BrowserProvider(p);
  walletSigner = await walletProvider.getSigner();

  if (p.on) {
    p.on('accountsChanged', (a) => {
      walletAccount = a[0] || null;
      window.dispatchEvent(new CustomEvent('exo:accountChanged', { detail: { account: walletAccount } }));
    });
    p.on('chainChanged', () => location.reload());
  }

  window.dispatchEvent(new CustomEvent('exo:accountChanged', { detail: { account: walletAccount } }));
  return walletAccount;
}

async function autoConnect() {
  try {
    await new Promise(r => setTimeout(r, 300));
    const p = eip6963Providers.length ? eip6963Providers[0].provider : window.ethereum;
    if (!p) return null;
    const accts = await p.request({ method: 'eth_accounts' }).catch(() => []);
    if (accts.length) {
      walletAccount = accts[0];
      walletProvider = new ethers.BrowserProvider(p);
      walletSigner = await walletProvider.getSigner();
      if (p.on) {
        p.on('accountsChanged', (a) => {
          walletAccount = a[0] || null;
          window.dispatchEvent(new CustomEvent('exo:accountChanged', { detail: { account: walletAccount } }));
        });
        p.on('chainChanged', () => location.reload());
      }
      window.dispatchEvent(new CustomEvent('exo:accountChanged', { detail: { account: walletAccount } }));
      return walletAccount;
    }
  } catch (e) {}
  return null;
}

function getSignedContract(contractName) {
  if (!walletSigner) throw new Error('Wallet not connected');
  const abis = { core: CORE_ABI, registry: REGISTRY_ABI, renderer: RENDERER_ABI, wallet: WALLET_ABI };
  return new ethers.Contract(CONTRACTS[contractName], abis[contractName], walletSigner);
}

// ── Trust Tier Calculation ──
// Trust tiers calibrated for actual score ranges.
// Contract score = age_in_blocks + activity. Base has 2s blocks = 43,200/day.
// Genesis gets 1.5x. So thresholds must account for age-dominated scores.
function getTrustTier(score) {
  const n = typeof score === 'bigint' ? Number(score) : score;
  if (n >= 6000000) return { name: 'LEGENDARY', class: 'trust-badge--legendary', color: 'var(--trust-legendary)' };  // ~4+ months
  if (n >= 1500000) return { name: 'VETERAN', class: 'trust-badge--veteran', color: 'var(--trust-veteran)' };        // ~1-4 months
  if (n >= 300000) return { name: 'PROVEN', class: 'trust-badge--proven', color: 'var(--trust-proven)' };             // ~1 week - 1 month
  if (n >= 50000) return { name: 'ESTABLISHED', class: 'trust-badge--established', color: 'var(--trust-established)' }; // ~1-7 days
  return { name: 'NEW', class: 'trust-badge--new', color: 'var(--trust-new)' };                                        // <1 day
}

// ── Utility Functions ──
function truncAddr(a) {
  return a ? a.slice(0, 6) + '...' + a.slice(-4) : '';
}

function formatAge(ageBlocks) {
  const n = typeof ageBlocks === 'bigint' ? Number(ageBlocks) : ageBlocks;
  const hours = Math.floor(n * 2 / 3600);
  const days = Math.floor(hours / 24);
  if (days > 365) return Math.floor(days / 365) + 'y ' + (days % 365) + 'd';
  if (days > 0) return days + 'd ' + (hours % 24) + 'h';
  return hours + 'h';
}

function formatScore(score) {
  const n = typeof score === 'bigint' ? Number(score) : score;
  if (n >= 100000) return (n / 1000).toFixed(0) + 'K';
  if (n >= 10000) return (n / 1000).toFixed(1) + 'K';
  return n.toLocaleString();
}

function escHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function formatEth(wei) {
  if (typeof ethers !== 'undefined') return ethers.formatEther(wei);
  return (Number(wei) / 1e18).toString();
}

// ── Get Owned Tokens ──
async function getOwnedTokens(address) {
  initProvider();
  const balance = await withFallback(() => contracts.core.balanceOf(address));
  const count = Number(balance);
  const tokens = [];
  for (let i = 0; i < count; i++) {
    const tokenId = await contracts.core.tokenOfOwnerByIndex(address, i);
    tokens.push(Number(tokenId));
  }
  return tokens;
}

// ── SVG Preview — pixel-accurate match of ExoskeletonRenderer.sol ──
function renderSVGPreview(cfg, opts = {}) {
  const shape = cfg[0] || 0;
  const pHex = '#' + [cfg[1], cfg[2], cfg[3]].map(v => (v || 0).toString(16).padStart(2, '0')).join('');
  const sHex = '#' + [cfg[4], cfg[5], cfg[6]].map(v => (v || 0).toString(16).padStart(2, '0')).join('');
  const sym = cfg[7] || 0;
  const pat = cfg[8] || 0;
  const pRgb = `rgb(${cfg[1] || 0},${cfg[2] || 0},${cfg[3] || 0})`;
  const genesis = opts.genesis !== false;
  const displayId = opts.tokenId || '?';
  const displayName = opts.name || 'YOUR AGENT';
  const msgs = opts.msgs || 0;
  const sto = opts.sto || 0;
  const mods = opts.mods || 0;
  const repScore = opts.repScore || 0;
  const ageBlocks = opts.ageBlocks || 0;

  // Unique prefix for gradient/filter IDs to avoid cross-SVG conflicts
  const uid = 'e' + displayId;

  // Calculate dynamic layers
  const cx = Math.min(Math.floor(repScore / 500) + 2, 20);
  const ageRings = Math.min(Math.floor(ageBlocks / 43200), 8);

  let o = '<defs>';
  o += `<radialGradient id="${uid}-glow"><stop offset="0%" stop-color="${pHex}" stop-opacity="0.6"/><stop offset="100%" stop-color="${pHex}" stop-opacity="0"/></radialGradient>`;
  o += `<radialGradient id="${uid}-core-glow"><stop offset="0%" stop-color="${pHex}" stop-opacity="0.3"/><stop offset="60%" stop-color="${sHex}" stop-opacity="0.1"/><stop offset="100%" stop-opacity="0"/></radialGradient>`;
  o += `<filter id="${uid}-blur"><feGaussianBlur stdDeviation="3"/></filter>`;
  o += `<filter id="${uid}-blur-lg"><feGaussianBlur stdDeviation="8"/></filter>`;
  o += `<filter id="${uid}-glow-filter"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="${pRgb}" flood-opacity="0.5"/></filter>`;
  o += '</defs>';
  o += '<rect width="500" height="500" fill="#080808"/>';
  o += '<rect x="0" y="0" width="500" height="500" fill="url(#' + uid + '-core-glow)"/>';

  // Genesis frame
  if (genesis) {
    o += `<rect x="8" y="8" width="484" height="484" rx="16" fill="none" stroke="#FFD700" stroke-width="2" opacity="0.8"/>`;
    o += `<rect x="14" y="14" width="472" height="472" rx="12" fill="none" stroke="${pHex}" stroke-width="1" opacity="0.4"/>`;
    o += '<circle cx="24" cy="24" r="4" fill="#FFD700" opacity="0.8"/>';
    o += '<circle cx="476" cy="24" r="4" fill="#FFD700" opacity="0.8"/>';
    o += '<circle cx="24" cy="476" r="4" fill="#FFD700" opacity="0.8"/>';
    o += '<circle cx="476" cy="476" r="4" fill="#FFD700" opacity="0.8"/>';
  } else {
    o += `<rect x="10" y="10" width="480" height="480" rx="14" fill="none" stroke="${pHex}" stroke-width="1" opacity="0.5"/>`;
  }

  // Age rings
  for (let i = 1; i <= ageRings; i++) {
    o += `<circle cx="250" cy="240" r="${100 + i * 16}" fill="none" stroke="${pHex}" stroke-width="0.3" opacity="${0.05 + i * 0.02}"/>`;
  }

  // Main shape
  const gf = ` fill="none" stroke="${pHex}" stroke-width="2" filter="url(#${uid}-glow-filter)"`;
  const shapes = {
    0: `<polygon points="250,160 319,200 319,280 250,320 181,280 181,200"${gf}/>`,
    1: `<circle cx="250" cy="240" r="80"${gf}/>`,
    2: `<polygon points="250,155 340,240 250,325 160,240"${gf}/>`,
    3: `<path d="M250,160 L330,200 L330,280 Q330,320 250,340 Q170,320 170,280 L170,200 Z"${gf}/>`,
    4: `<polygon points="217,160 283,160 330,207 330,273 283,320 217,320 170,273 170,207"${gf}/>`,
    5: `<polygon points="250,155 345,325 155,325"${gf}/>`,
  };
  o += shapes[shape] || shapes[0];

  // Symbol
  if (sym === 1) {
    o += `<ellipse cx="250" cy="240" rx="20" ry="12" fill="none" stroke="${pHex}" stroke-width="1.5" opacity="0.7"/>`;
    o += `<circle cx="250" cy="240" r="5" fill="${pHex}" opacity="0.6"/>`;
  } else if (sym === 2) {
    o += `<circle cx="250" cy="240" r="12" fill="none" stroke="${pHex}" stroke-width="1.5" opacity="0.7"/>`;
    o += `<circle cx="250" cy="240" r="5" fill="${pHex}" opacity="0.4"/>`;
    o += `<line x1="250" y1="225" x2="250" y2="255" stroke="${pHex}" stroke-width="1" opacity="0.5"/>`;
    o += `<line x1="235" y1="240" x2="265" y2="240" stroke="${pHex}" stroke-width="1" opacity="0.5"/>`;
  } else if (sym === 3) {
    o += `<polygon points="255,225 245,238 258,238 243,258" fill="none" stroke="${pHex}" stroke-width="1.5" opacity="0.7"/>`;
  } else if (sym === 4) {
    o += `<polygon points="250,225 254,237 267,237 257,245 260,258 250,250 240,258 243,245 233,237 246,237" fill="none" stroke="${pHex}" stroke-width="1" opacity="0.7"/>`;
  } else if (sym === 5) {
    o += `<path d="M230,240 Q240,228 250,240 Q260,252 270,240" fill="none" stroke="${pHex}" stroke-width="1.5" opacity="0.7"/>`;
  } else if (sym === 6) {
    o += `<circle cx="250" cy="240" r="4" fill="${pHex}" opacity="0.6"/>`;
    o += `<circle cx="238" cy="228" r="2" fill="${pHex}" opacity="0.4"/>`;
    o += `<circle cx="262" cy="228" r="2" fill="${pHex}" opacity="0.4"/>`;
    o += `<circle cx="238" cy="252" r="2" fill="${pHex}" opacity="0.4"/>`;
    o += `<circle cx="262" cy="252" r="2" fill="${pHex}" opacity="0.4"/>`;
    o += `<line x1="250" y1="240" x2="238" y2="228" stroke="${pHex}" stroke-width="0.5" opacity="0.3"/>`;
    o += `<line x1="250" y1="240" x2="262" y2="228" stroke="${pHex}" stroke-width="0.5" opacity="0.3"/>`;
    o += `<line x1="250" y1="240" x2="238" y2="252" stroke="${pHex}" stroke-width="0.5" opacity="0.3"/>`;
    o += `<line x1="250" y1="240" x2="262" y2="252" stroke="${pHex}" stroke-width="0.5" opacity="0.3"/>`;
  } else if (sym === 7) {
    o += `<polygon points="250,228 260,240 250,252 240,240" fill="none" stroke="${pHex}" stroke-width="1.5" opacity="0.7"/>`;
  }

  // Pattern (scaled with reputation)
  if (pat === 1) {
    for (let x = 170; x <= 330; x += 36) o += `<line x1="${x}" y1="170" x2="${x}" y2="310" stroke="${sHex}" stroke-width="0.3" opacity="0.15"/>`;
    for (let y = 170; y <= 310; y += 36) o += `<line x1="170" y1="${y}" x2="330" y2="${y}" stroke="${sHex}" stroke-width="0.3" opacity="0.15"/>`;
  } else if (pat === 2) {
    for (let i = 0; i < cx * 2 && i < 20; i++) {
      o += `<circle cx="${190 + (i * 37 % 120)}" cy="${190 + (i * 53 % 100)}" r="1.5" fill="${sHex}" opacity="0.2"/>`;
    }
  } else if (pat === 3) {
    for (let i = 0; i < cx && i < 10; i++) {
      const x = 180 + i * 15;
      o += `<line x1="${x}" y1="170" x2="${x + 30}" y2="310" stroke="${sHex}" stroke-width="0.3" opacity="0.12"/>`;
    }
  } else if (pat === 4) {
    for (let i = 0; i < cx && i < 8; i++) {
      const x1 = 200 + (i * 31 % 100), y1 = 200 + (i * 47 % 80);
      const x2 = 200 + ((i + 1) * 31 % 100), y2 = 200 + ((i + 1) * 47 % 80);
      o += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${sHex}" stroke-width="0.5" opacity="0.2"/>`;
      o += `<circle cx="${x1}" cy="${y1}" r="2" fill="${sHex}" opacity="0.3"/>`;
    }
  } else if (pat === 5) {
    for (let i = 1; i <= cx && i <= 5; i++) {
      o += `<circle cx="250" cy="240" r="${20 + i * 12}" fill="none" stroke="${sHex}" stroke-width="0.4" opacity="0.12"/>`;
    }
  }

  // Activity nodes (module dots in orbit)
  if (mods > 0) {
    for (let i = 0; i < Math.min(mods, 8); i++) {
      const angle = (i / Math.min(mods, 8)) * Math.PI * 2 - Math.PI / 2;
      const rx = 95, ry = 95;
      const nx = 250 + Math.cos(angle) * rx;
      const ny = 240 + Math.sin(angle) * ry;
      o += `<circle cx="${nx.toFixed(1)}" cy="${ny.toFixed(1)}" r="3" fill="${pHex}" opacity="0.4"/>`;
    }
  }

  // Text overlays
  o += `<text x="250" y="42" fill="${pHex}" font-family="monospace" font-size="8" text-anchor="middle" letter-spacing="4" opacity="0.3">EXOSKELETON</text>`;
  o += `<text x="470" y="42" fill="${pHex}" font-family="monospace" font-size="10" text-anchor="end" opacity="0.4">#${displayId}</text>`;
  o += `<text x="250" y="370" fill="${pHex}" font-family="monospace" font-size="16" text-anchor="middle" opacity="0.9">${escHtml(displayName)}</text>`;
  if (genesis) o += '<text x="250" y="395" fill="#FFD700" font-family="monospace" font-size="9" text-anchor="middle" letter-spacing="3" opacity="0.7">GENESIS</text>';

  // Stats bar
  o += `<line x1="40" y1="455" x2="460" y2="455" stroke="${pHex}" stroke-width="0.3" opacity="0.2"/>`;
  o += `<text x="60" y="470" fill="${sHex}" font-family="monospace" font-size="8" opacity="0.35">MSG:${msgs}</text>`;
  o += `<text x="180" y="470" fill="${sHex}" font-family="monospace" font-size="8" opacity="0.35">STO:${sto}</text>`;
  o += `<text x="300" y="470" fill="${sHex}" font-family="monospace" font-size="8" opacity="0.35">MOD:${mods}</text>`;

  // Reputation glow
  if (repScore >= 100) {
    const glowIntensity = Math.min(repScore / 10000, 0.5);
    o += `<circle cx="250" cy="240" r="60" fill="${pHex}" opacity="${glowIntensity * 0.15}" filter="url(#${uid}-blur-lg)"/>`;
  }

  return o;
}

// ── Parse Visual Config Bytes ──
function parseVisualConfig(configHex) {
  if (!configHex || configHex.length < 18) return null;
  const h = configHex.replace('0x', '');
  return {
    shape: parseInt(h.substring(0, 2), 16),
    pr: parseInt(h.substring(2, 4), 16),
    pg: parseInt(h.substring(4, 6), 16),
    pb: parseInt(h.substring(6, 8), 16),
    sr: parseInt(h.substring(8, 10), 16),
    sg: parseInt(h.substring(10, 12), 16),
    sb: parseInt(h.substring(12, 14), 16),
    symbol: parseInt(h.substring(14, 16), 16),
    pattern: parseInt(h.substring(16, 18), 16),
  };
}

// ── Wait for ethers.js to load, then init ──
function onReady(fn) {
  if (typeof ethers !== 'undefined') {
    initProvider();
    fn();
  } else {
    const check = setInterval(() => {
      if (typeof ethers !== 'undefined') {
        clearInterval(check);
        initProvider();
        fn();
      }
    }, 50);
    setTimeout(() => clearInterval(check), 10000);
  }
}

// ── Exports (attach to window for use in HTML pages) ──
window.ExoCore = {
  CONTRACTS,
  CHAIN_ID,
  CHAIN_ID_HEX,
  RPC_URLS,
  SHAPES,
  SYMBOLS,
  PATTERNS,
  CORE_ABI,
  REGISTRY_ABI,
  RENDERER_ABI,
  WALLET_ABI,
  get provider() { return provider; },
  get contracts() { return contracts; },
  get account() { return walletAccount; },
  get signer() { return walletSigner; },
  initProvider,
  withFallback,
  withRetry,
  loadTokenBatch,
  loadAllTokens,
  renderTokenSVG,
  connectWallet,
  autoConnect,
  getSignedContract,
  getOwnedTokens,
  getTrustTier,
  truncAddr,
  formatAge,
  formatScore,
  formatEth,
  escHtml,
  renderSVGPreview,
  parseVisualConfig,
  onReady,
};
