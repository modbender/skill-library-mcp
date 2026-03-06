# gank api — examples

all examples use `GANK_API_KEY` from env or `~/.openclaw/openclaw.json`.

base url: `https://gank.dev/api/v2`

---

## example 1 — launch a token end-to-end

```typescript
import fetch from 'node-fetch'
import FormData from 'form-data'
import fs from 'fs'

const API = 'https://gank.dev/api/v2'
const KEY = process.env.GANK_API_KEY

const headers = {
  'Authorization': `Bearer ${KEY}`,
  'Content-Type': 'application/json',
}

async function launchToken() {
  // step 1: Reserve a vanity mint address (optional)
  const mintRes = await fetch(`${API}/launch/reserve-mint`, {
    method: 'POST',
    headers,
  }).then(r => r.json())
  console.log('Reserved mint:', mintRes.address)

  // step 2: Upload image + metadata to IPFS
  const form = new FormData()
  form.append('file', fs.createReadStream('./token-image.png'))
  form.append('name', 'My Token')
  form.append('symbol', 'MTK')
  form.append('description', 'The best token on Solana')
  form.append('twitter', 'https://x.com/mytoken')
  form.append('telegram', 'https://t.me/mytoken')

  const ipfsRes = await fetch(`${API}/ipfs/upload`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${KEY}` },
    body: form,
  }).then(r => r.json())
  console.log('IPFS metadata URI:', ipfsRes.metadata_uri)

  // step 3: Launch on pump.fun
  const launchRes = await fetch(`${API}/launch`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      token_name: 'My Token',
      token_ticker: 'MTK',
      metadata_uri: ipfsRes.metadata_uri,
      dev_wallet_address: 'YourDevWalletAddress...',
      dev_buy_sol: 0.5,
      jito_tip: 0.0003,
      reserved_mint_keypair: mintRes.keypair,
      // Optional: bundle wallets buy at launch
      regular_wallets: [
        { wallet_address: 'RegularWallet1...', amount: 0.1 },
        { wallet_address: 'RegularWallet2...', amount: 0.15 },
      ],
    }),
  }).then(r => r.json())

  console.log('Launch ID:', launchRes.launch_id)
  console.log('Token mint:', launchRes.token_mint)
  console.log('TX:', launchRes.tx_signature)

  // step 4: Poll status
  let status
  do {
    await new Promise(r => setTimeout(r, 3000))
    status = await fetch(`${API}/launch/${launchRes.launch_id}`, { headers }).then(r => r.json())
    console.log('Status:', status.status)
  } while (status.status === 'pending' || status.status === 'processing')

  return launchRes.token_mint
}

launchToken().catch(console.error)
```

---

## example 2 — Swarm buy a token

```typescript
const API = 'https://gank.dev/api/v2'
const KEY = process.env.GANK_API_KEY
const headers = { 'Authorization': `Bearer ${KEY}`, 'Content-Type': 'application/json' }

async function swarmBuy(tokenMint: string) {
  // get swarm wallets
  const walletsRes = await fetch(`${API}/wallets/user`, { headers }).then(r => r.json())
  const swarmWallets = walletsRes.swarm || []

  if (swarmWallets.length === 0) {
    throw new Error('No swarm wallets found. Create some in the GANK dashboard.')
  }

  // check balances
  const balRes = await fetch(`${API}/wallets/balances`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ addresses: swarmWallets.map((w: any) => w.wallet_address) }),
  }).then(r => r.json())

  // filter wallets with enough SOL
  const funded = swarmWallets.filter((w: any) => {
    const bal = balRes.balances?.[w.wallet_address] || 0
    return bal >= 0.05
  })

  console.log(`Using ${funded.length} funded swarm wallets`)

  // execute swarm buy
  const buyRes = await fetch(`${API}/phases/swarm/buy`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      token_mint: tokenMint,
      wallets: funded.map((w: any) => ({
        wallet_address: w.wallet_address,
        amount_sol: 0.05,
      })),
      slippage_bps: 500,
    }),
  }).then(r => r.json())

  console.log('Swarm buy result:', buyRes)
  return buyRes
}
```

---

## example 3 — Volume bot session

```typescript
const API = 'https://gank.dev/api/v2'
const KEY = process.env.GANK_API_KEY
const headers = { 'Authorization': `Bearer ${KEY}`, 'Content-Type': 'application/json' }

async function runVolumeBot(tokenMint: string, durationMinutes = 60) {
  // get volume wallets
  const walletsRes = await fetch(`${API}/wallets/user`, { headers }).then(r => r.json())
  const volumeWallets = (walletsRes.volume || []).map((w: any) => w.wallet_address)

  if (volumeWallets.length === 0) {
    throw new Error('No volume wallets found.')
  }

  // start volume bot
  const startRes = await fetch(`${API}/phases/volume/start`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      token_mint: tokenMint,
      wallet_addresses: volumeWallets,
      sol_per_trade: 0.001,
      duration_minutes: durationMinutes,
      intensity: 'medium', // "low" | "medium" | "high"
    }),
  }).then(r => r.json())

  console.log('Volume bot started. Session ID:', startRes.session_id)

  // stop after duration
  setTimeout(async () => {
    const stopRes = await fetch(`${API}/phases/volume/stop`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ session_id: startRes.session_id }),
    }).then(r => r.json())
    console.log('Volume bot stopped:', stopRes)
  }, durationMinutes * 60 * 1000)

  return startRes.session_id
}
```

---

## example 4 — Recover funds from all swarm wallets

```typescript
const API = 'https://gank.dev/api/v2'
const KEY = process.env.GANK_API_KEY
const headers = { 'Authorization': `Bearer ${KEY}`, 'Content-Type': 'application/json' }

async function recoverAllFunds(destinationWallet: string) {
  // get all swarm wallets
  const walletsRes = await fetch(`${API}/wallets/user`, { headers }).then(r => r.json())
  const swarmAddresses = (walletsRes.swarm || []).map((w: any) => w.wallet_address)

  if (swarmAddresses.length === 0) {
    console.log('No swarm wallets to recover from.')
    return
  }

  // vamp all: sells tokens + closes accounts + sweeps sol
  const vampRes = await fetch(`${API}/wallets/vamp-all`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      source_wallets: swarmAddresses,
      destination_wallet: destinationWallet,
    }),
  }).then(r => r.json())

  console.log('Recovery complete:', vampRes)
  return vampRes
}
```

---

## example 5 — Monitor positions and sell on target

```typescript
const API = 'https://gank.dev/api/v2'
const KEY = process.env.GANK_API_KEY
const headers = { 'Authorization': `Bearer ${KEY}`, 'Content-Type': 'application/json' }

async function monitorAndSell(targetMultiplier = 2.0) {
  const posRes = await fetch(`${API}/user/positions`, { headers }).then(r => r.json())
  const positions = posRes.positions || []

  for (const pos of positions) {
    const currentMultiplier = pos.current_value_sol / pos.cost_basis_sol
    console.log(`${pos.token_symbol}: ${currentMultiplier.toFixed(2)}x`)

    if (currentMultiplier >= targetMultiplier) {
      console.log(`Selling ${pos.token_symbol} at ${currentMultiplier.toFixed(2)}x`)
      const sellRes = await fetch(`${API}/phases/regular/sell`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          wallet_address: pos.wallet_address,
          token_mint: pos.token_mint,
          sell_percentage: 100,
          slippage_bps: 500,
        }),
      }).then(r => r.json())
      console.log('Sell result:', sellRes)
    }
  }
}

// poll every 30 seconds
setInterval(monitorAndSell, 30_000)
```

---

## example 6 — full launch + swarm + volume pipeline

```typescript
const API = 'https://gank.dev/api/v2'
const KEY = process.env.GANK_API_KEY
const headers = { 'Authorization': `Bearer ${KEY}`, 'Content-Type': 'application/json' }

async function fullLaunchPipeline() {
  // 1. Reserve mint
  const { keypair, address } = await fetch(`${API}/launch/reserve-mint`, {
    method: 'POST', headers,
  }).then(r => r.json())
  console.log('CA:', address)

  // 2. Upload metadata (assumes image already uploaded separately)
  const { metadata_uri } = await fetch(`${API}/ipfs/upload`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${KEY}` },
    body: (() => {
      const f = new (require('form-data'))()
      f.append('file', require('fs').createReadStream('./image.png'))
      f.append('name', 'GANK')
      f.append('symbol', 'GANK')
      f.append('description', 'the trading terminal for degens')
      return f
    })(),
  }).then(r => r.json())

  // 3. Get wallets
  const { swarm, volume, dev } = await fetch(`${API}/wallets/user`, { headers }).then(r => r.json())
  const devWallet = dev[0]?.wallet_address
  const swarmAddresses = swarm.slice(0, 10).map((w: any) => w.wallet_address)
  const volumeAddresses = volume.map((w: any) => w.wallet_address)

  // 4. Launch with swarm wallets as regular buyers
  const { launch_id, token_mint } = await fetch(`${API}/launch`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      token_name: 'GANK',
      token_ticker: 'GANK',
      metadata_uri,
      dev_wallet_address: devWallet,
      dev_buy_sol: 1.0,
      jito_tip: 0.0005,
      reserved_mint_keypair: keypair,
      regular_wallets: swarmAddresses.map(addr => ({ wallet_address: addr, amount: 0.1 })),
    }),
  }).then(r => r.json())

  console.log('Launched:', token_mint)

  // 5. Wait for launch to confirm
  await new Promise(r => setTimeout(r, 10_000))

  // 6. Start volume bot
  const { session_id } = await fetch(`${API}/phases/volume/start`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      token_mint,
      wallet_addresses: volumeAddresses,
      sol_per_trade: 0.002,
      duration_minutes: 120,
      intensity: 'high',
    }),
  }).then(r => r.json())

  console.log('Volume bot running. Session:', session_id)
  console.log('Token:', token_mint)
  console.log('Done.')
}

fullLaunchPipeline().catch(console.error)
```
