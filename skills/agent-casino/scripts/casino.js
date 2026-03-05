#!/usr/bin/env node
// Agent Casino V2 CLI — wraps casino.lemomo.xyz API (Base Mainnet)
// Returns unsigned transaction data. Agent must sign and broadcast.
// Usage: casino <command> [options]

const BASE_URL = process.env.CASINO_URL || 'https://casino.lemomo.xyz';

const args = process.argv.slice(2);
const command = args[0];

function getArg(name) {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null;
}

async function request(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${BASE_URL}${path}`, opts);
  const data = await res.json();
  if (!res.ok) {
    console.error(`Error ${res.status}: ${data.error || JSON.stringify(data)}`);
    process.exit(1);
  }
  return data;
}

async function main() {
  const address = getArg('address');
  const choice = getArg('choice');
  const amount = getArg('amount');
  const id = getArg('id');
  const salt = getArg('salt');

  // Map choice names to numbers
  const choiceMap = { rock: 1, paper: 2, scissors: 3 };
  const choiceNum = choice ? (choiceMap[choice.toLowerCase()] || parseInt(choice)) : null;

  switch (command) {
    case 'info': {
      const d = await request('GET', '/');
      console.log(`${d.name} v${d.version}`);
      console.log(`Network: ${d.network}`);
      console.log(`Router:  ${d.contracts.CASINO_ROUTER}`);
      console.log(`RPS:     ${d.contracts.RPS_GAME}`);
      console.log(`USDC:    ${d.contracts.USDC}`);
      break;
    }
    case 'balance': {
      if (!address) { console.error('--address required'); process.exit(1); }
      const d = await request('GET', `/balance/${address}`);
      console.log(`Address: ${d.address}`);
      console.log(`Router balance: ${d.balance} USDC`);
      break;
    }
    case 'game': {
      if (!id) { console.error('--id required'); process.exit(1); }
      const d = await request('GET', `/game/${id}`);
      console.log(`Game #${d.gameId} — ${d.state}`);
      console.log(`P1: ${d.player1} → ${d.choice1}`);
      console.log(`P2: ${d.player2} → ${d.choice2}`);
      break;
    }
    case 'deposit': {
      if (!address || !amount) { console.error('--address and --amount required'); process.exit(1); }
      const d = await request('POST', '/deposit', { address, amount });
      console.log(`Needs approval: ${d.needsApproval}`);
      console.log('Transactions to sign:');
      d.transactions.forEach((tx, i) => {
        console.log(`  ${i + 1}. ${tx.description}`);
        console.log(`     to: ${tx.to}`);
        console.log(`     data: ${tx.data}`);
      });
      break;
    }
    case 'withdraw': {
      if (!amount) { console.error('--amount required'); process.exit(1); }
      const d = await request('POST', '/withdraw', { amount });
      console.log(`${d.transaction.description}`);
      console.log(`  to: ${d.transaction.to}`);
      console.log(`  data: ${d.transaction.data}`);
      break;
    }
    case 'create': {
      if (!choiceNum) { console.error('--choice required (rock|paper|scissors or 1|2|3)'); process.exit(1); }
      const body = { choice: choiceNum };
      if (salt) body.salt = salt;
      const d = await request('POST', '/create', body);
      console.log(`Commitment: ${d.commitment}`);
      console.log(`Salt: ${d.salt}`);
      console.log(`Choice: ${d.choice}`);
      console.log(`⚠️  SAVE YOUR SALT — you need it to reveal!`);
      console.log(`\nTransaction to sign:`);
      console.log(`  ${d.transaction.description}`);
      console.log(`  to: ${d.transaction.to}`);
      console.log(`  data: ${d.transaction.data}`);
      break;
    }
    case 'join': {
      if (!id || !choiceNum) { console.error('--id and --choice required'); process.exit(1); }
      const body = { gameId: id, choice: choiceNum };
      if (salt) body.salt = salt;
      const d = await request('POST', '/join', body);
      console.log(`Game: ${d.gameId}`);
      console.log(`Salt: ${d.salt}`);
      console.log(`⚠️  SAVE YOUR SALT — you need it to reveal!`);
      console.log(`\nTransaction to sign:`);
      console.log(`  ${d.transaction.description}`);
      console.log(`  to: ${d.transaction.to}`);
      console.log(`  data: ${d.transaction.data}`);
      break;
    }
    case 'reveal': {
      if (!id || !choiceNum || !salt) { console.error('--id, --choice, and --salt required'); process.exit(1); }
      const d = await request('POST', '/reveal', { gameId: id, choice: choiceNum, salt });
      console.log(`Game: ${d.gameId}`);
      console.log(`\nTransaction to sign:`);
      console.log(`  ${d.transaction.description}`);
      console.log(`  to: ${d.transaction.to}`);
      console.log(`  data: ${d.transaction.data}`);
      break;
    }
    default:
      console.log('Agent Casino V2 CLI — Base Mainnet (real USDC)');
      console.log('');
      console.log('Commands:');
      console.log('  info                          API info and contract addresses');
      console.log('  balance  --address 0x...       Router balance');
      console.log('  game     --id N                Game state');
      console.log('  deposit  --address 0x... --amount N   Prepare deposit tx');
      console.log('  withdraw --amount N            Prepare withdraw tx');
      console.log('  create   --choice rock         Create game (save salt!)');
      console.log('  join     --id N --choice paper  Join game (save salt!)');
      console.log('  reveal   --id N --choice rock --salt 0x...  Reveal choice');
      console.log('');
      console.log('Choices: rock, paper, scissors (or 1, 2, 3)');
      console.log('Env: CASINO_URL (default: https://casino.lemomo.xyz)');
      console.log('');
      console.log('⚠️  Returns unsigned tx data. You must sign and broadcast.');
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
