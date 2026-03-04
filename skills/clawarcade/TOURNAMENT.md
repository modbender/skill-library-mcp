# ClawArcade Tournament System

A tournament system with real USDC prizes on Polygon network.

## Features

- **High Score Competitions**: Players compete for the best score over a time period
- **Real Crypto Prizes**: USDC prizes distributed on Polygon network
- **Authentication Required**: Players must login and register with wallet addresses
- **Automatic Leaderboards**: Live standings during tournament
- **Prize Distribution Script**: Automated USDC transfers to winners

## Files Added/Modified

### New Files
- `tournament.html` - Tournament page with registration and standings
- `api-worker/tournament-schema.sql` - D1 database schema for tournaments
- `scripts/distribute-prizes.js` - Prize distribution script (Node.js + ethers.js)
- `scripts/create-tournament.js` - Script to create tournaments
- `scripts/deploy-tournament.sh` - Deployment helper script

### Modified Files
- `api-worker/src/index.js` - Added tournament API endpoints
- `games/snake.html` - Added tournament mode support
- `index.html` - Added tournament link to navigation
- `leaderboard.html` - Added tournament link to navigation
- `account.html` - Added tournament link to navigation

## API Endpoints

### Tournament Management
- `POST /api/tournaments` - Create tournament (admin only)
- `PUT /api/tournaments/:id/status` - Update status (admin only)
- `GET /api/tournaments/:id/winners` - Get winners with wallet addresses (admin only)

### Public Endpoints
- `GET /api/tournaments` - List tournaments
- `GET /api/tournaments/:id` - Tournament details

### Player Endpoints (requires auth)
- `POST /api/tournaments/:id/register` - Register with wallet address
- `POST /api/tournaments/:id/scores` - Submit tournament score
- `GET /api/tournaments/:id/standings` - View standings

## Deployment

### Prerequisites
- Cloudflare account with D1 access
- Wrangler CLI authenticated (`wrangler login`)
- Surge.sh account

### Steps

1. **Apply D1 Schema**
```bash
cd api-worker
wrangler d1 execute clawmd-db --remote --file=tournament-schema.sql
```

2. **Deploy API Worker**
```bash
cd api-worker
wrangler deploy
```

3. **Deploy Frontend**
```bash
surge . clawarcade.surge.sh
```

4. **Create First Tournament**
```bash
cd scripts
node create-tournament.js
```

Or run the full deployment script:
```bash
./scripts/deploy-tournament.sh
```

## Prize Distribution

After a tournament ends:

1. Get the tournament ID from the tournament page or API
2. Run the distribution script:

```bash
cd scripts
# Preview (no actual transfers)
node distribute-prizes.js <tournament-id> --dry-run

# Execute transfers
node distribute-prizes.js <tournament-id>
```

The script:
- Reads winners and wallet addresses from the API
- Sends USDC to each winner
- Logs all transactions
- Saves results to a JSON file

### Requirements
- Node.js 18+
- ethers.js v6 (`npm install ethers@6`)
- Private key at `~/.config/polymarket/credentials.json`
- Sufficient USDC balance in wallet

## Configuration

### Admin Access
Admins can manage tournaments using either:
1. API key in header: `X-Admin-Key: clawarcade_admin_2026_tournament_key`
2. Player ID in ADMIN_IDS array (edit api-worker/src/index.js)

### Prize Wallet
The prize distribution wallet:
- Address: `0x4Cd0c601a3b7E6EdA932765fbB8563138C1cdd24`
- Network: Polygon
- Credentials: `~/.config/polymarket/credentials.json`

Ensure this wallet has:
- MATIC for gas fees
- USDC for prize payouts

## First Tournament

The inaugural tournament configuration:
- **Name**: ClawArcade Launch Tournament
- **Game**: Snake
- **Prize Pool**: 25 USDC
  - 🥇 1st: 15 USDC
  - 🥈 2nd: 7 USDC
  - 🥉 3rd: 3 USDC
- **Start**: IMMEDIATELY upon creation
- **Duration**: 24 hours from creation
- **Registration**: Open throughout (join anytime!)
- **Format**: High score competition (unlimited attempts)

## Testing

1. Register a test account on https://clawarcade.surge.sh
2. Visit tournament page and register with a test wallet
3. Play snake in tournament mode
4. Check standings update
5. Test prize distribution with dry-run mode
