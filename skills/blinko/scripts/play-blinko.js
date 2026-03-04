#!/usr/bin/env node
/**
 * Blinko - Headless Plinko game player for Abstract chain
 * Usage: WALLET_PRIVATE_KEY=0x... node play-blinko.js [betETH] [--hard] [--v2]
 */
const path = require('path');
const { ethers } = require('ethers');

const API = 'https://api.blinko.gg';
const RPC = 'https://api.abs.xyz';
const CHAIN = 2741;
const CONTRACT = '0x1859072d67fdD26c8782C90A1E4F078901c0d763';
const MIN_BET = 100000000000000n;       // 0.0001 ETH
const MAX_BET = 100000000000000000n;    // 0.1 ETH
const SIGN_MSG = 'Sign in to Blinko. By signing, you agree to the Terms of Service.';

const sleep = ms => new Promise(r => setTimeout(r, ms));
const has = flag => process.argv.includes(flag);

function getBet() {
  const a = process.argv.find(x => !x.startsWith('--') && x !== process.argv[0] && x !== process.argv[1]);
  return a || '0.001';
}

async function api(url, opts = {}) {
  const r = await fetch(url, opts);
  const body = await r.json().catch(() => null);
  if (!r.ok) throw new Error(`API ${r.status}: ${body?.error || r.statusText}`);
  return body;
}

function loadKey() {
  const pk = process.env.WALLET_PRIVATE_KEY;
  if (!pk) {
    console.error('Set WALLET_PRIVATE_KEY env var. Example:');
    console.error('  WALLET_PRIVATE_KEY=0x... node play-blinko.js 0.001');
    process.exit(1);
  }
  return pk.startsWith('0x') ? pk : '0x' + pk;
}

async function main() {
  const hard = has('--hard'), v2 = has('--v2');
  const betEth = getBet();
  const betWei = ethers.parseEther(betEth);

  if (betWei < MIN_BET || betWei > MAX_BET) {
    throw new Error(`Bet out of range (0.0001-0.1 ETH). Got: ${betEth}`);
  }

  console.log(`🎯 Blinko | ${betEth} ETH | hard=${hard} v2=${v2}`);

  // 1. Wallet
  const wallet = new ethers.Wallet(loadKey(), new ethers.JsonRpcProvider(RPC, CHAIN));
  const addr = wallet.address;
  console.log(`👛 ${addr}`);

  // 2. Login
  const sig = await wallet.signMessage(SIGN_MSG);
  const login = await api(`${API}/blinko/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ address: addr, signature: sig }),
  });
  const jwt = login.data?.token || login.token;
  if (!jwt) throw new Error('Login failed: no token returned');
  const auth = { 'Content-Type': 'application/json', Authorization: `Bearer ${jwt}` };
  console.log('✅ Logged in');

  // 3. Create game
  const cg = await api(`${API}/blinko/create-game`, {
    method: 'POST', headers: auth,
    body: JSON.stringify({ player: addr, betAmount: betWei.toString(), hardMode: hard, v2Mode: v2 }),
  });
  const d = cg.data || cg;
  const { gameId, signature: serverSig, gameParams: gp } = d;
  if (!gameId || !serverSig || !gp) throw new Error('Create game: missing response fields');
  console.log(`🎲 Game ${gameId.slice(0, 18)}...`);

  // 4. On-chain createGame
  await sleep(2000);
  const abi = require(path.join(__dirname, 'commit-reveal-abi.json'));
  const contract = new ethers.Contract(CONTRACT, abi, wallet);
  const params = [
    gp.token || ethers.ZeroAddress,
    BigInt(gp.betAmount),
    gp.gameSeedHash,
    gp.algorithm,
    gp.gameConfig,
    gp.resolver,
    BigInt(gp.deadline),
  ];
  const tx1 = await contract.createGame(params, serverSig, ethers.randomBytes(32), { value: betWei });
  console.log(`⛓️  createGame tx: ${tx1.hash}`);
  await tx1.wait();

  // 5. Play
  const play = await api(`${API}/blinko/games/${gameId}/play`, { method: 'POST', headers: auth });
  const p = play.data || play;
  const { result, signature: settleSig, signatureType, gameState, gameSeed, deadline } = p;
  if (!result || !settleSig) throw new Error('Play: missing response fields');
  const win = BigInt(result.totalWin);

  // 6. Settle
  let tx2;
  if (signatureType === 'cashOut') {
    tx2 = await contract.cashOut(gameId, win, gameState, gameSeed, BigInt(deadline), settleSig);
  } else {
    tx2 = await contract.markGameAsLost(gameId, gameState, gameSeed, BigInt(deadline), settleSig);
  }
  console.log(`⛓️  settle tx: ${tx2.hash}`);
  await tx2.wait();

  // 7. Summary
  console.log(`\n${win > 0n ? '🏆 WIN' : '💀 LOSS'} | Bet: ${betEth} ETH | Payout: ${ethers.formatEther(win)} ETH | RTP: ${result.rtp}%`);
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
