#!/usr/bin/env python3
"""
Optionns Trading Strategy Engine
Autonomous bet sizing and edge calculation for sports micro-betting
"""

import argparse
import asyncio
import base64
import hashlib
import json
import os
import struct
import sys
import time
import httpx
from datetime import datetime, timedelta
from pathlib import Path

# Add signer to path for on-chain settlement
sys.path.insert(0, str(Path(__file__).parent))
from signer import sign_and_submit

# Configuration
API_BASE = os.getenv('OPTIONNS_API_URL', 'https://api.optionns.com')
API_KEY = os.getenv('OPTIONNS_API_KEY', '')
WALLET = os.getenv('SOLANA_PUBKEY', '')
USER_ATA = os.getenv('SOLANA_ATA', '')
KEYPAIR_PATH = os.getenv('OPTIONNS_KEYPAIR_PATH', os.path.expanduser('~/.config/optionns/agent_keypair.json'))
RPC_URL = os.getenv('SOLANA_RPC_URL', 'https://api.devnet.solana.com')

# Devnet-only enforcement
ALLOWED_DEVNET_PATTERNS = [
    "devnet.solana.com",
    "api.devnet.solana.com",
    "devnet.helius-rpc.com",
    "rpc.devnet.soo.network",
    "devnet.rpcpool.com",
    "localhost",
    "127.0.0.1"
]

def _validate_devnet_rpc(rpc_url: str) -> None:
    """Enforce devnet-only operation."""
    url_lower = rpc_url.lower()
    if not any(pattern in url_lower for pattern in ALLOWED_DEVNET_PATTERNS):
        raise ValueError(
            f"SECURITY: RPC URL must be a devnet endpoint. Got: {rpc_url}\n"
            f"Allowed patterns: {', '.join(ALLOWED_DEVNET_PATTERNS)}\n"
            "This skill is devnet-only for security. Never use mainnet keys or endpoints."
        )

# Validate RPC URL on import
_validate_devnet_rpc(RPC_URL)

# Solana Constants
PROGRAM_ID = '7kHCtJrAuHAg8aQPtkf2ijjWyEEZ2fUYWaCT7sXVwMSn'
TOKEN_PROGRAM_ID = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'
DEPOSIT_IX_DISCRIMINATOR = b"\xf2#\xc6\x89R\xe1\xf2\xb6"
WITHDRAW_IX_DISCRIMINATOR = b'\xb7\x12F\x9c\x94m\xa1"'

# Sports cascade order — agent's preferred sport checked first, then fallback
SUPPORTED_SPORTS = ['NFL', 'NBA', 'NCAAB', 'NHL', 'MLB', 'CFB', 'SOCCER']

class OptionnsTrader:
    def __init__(self):
        self.api_key = API_KEY
        self.client = httpx.Client(
            base_url=API_BASE,
            headers={'X-API-Key': self.api_key, 'Content-Type': 'application/json'},
            timeout=30.0
        )
        self.positions = []
        self.bankroll = 1000  # Starting bankroll in optnnUSDC
        self.max_risk_per_trade = 0.05  # 5% max risk per trade
    
    def api_call(self, method, path, data=None):
        """Make an authenticated API call."""
        try:
            if method == 'GET':
                resp = self.client.get(path)
            else:
                resp = self.client.post(path, json=data)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            print(f"  API error {e.response.status_code}: {e.response.text[:200]}")
            return None
        except Exception as e:
            print(f"  Request failed: {e}")
            return None

    def fetch_games(self, sport='NFL'):
        """Fetch live games from the API, cascading through sports if needed."""
        # Try preferred sport first
        result = self.api_call('GET', f'/v1/sports/events?sport={sport}')
        if result and 'data' in result:
            live = result['data'].get('live', [])
            if live:
                print(f"  Found {len(live)} live {sport} games")
                return live
        
        # No games for preferred sport — cascade through others
        print(f"  No live {sport} games. Scanning other sports...")
        for fallback in SUPPORTED_SPORTS:
            if fallback.upper() == sport.upper():
                continue
            result = self.api_call('GET', f'/v1/sports/events?sport={fallback}')
            if result and 'data' in result:
                live = result['data'].get('live', [])
                if live:
                    print(f"  Found {len(live)} live {fallback} games")
                    return live
        
        return []

    def ensure_ata(self):
        """Auto-provision an ATA if the agent doesn't have one."""
        global USER_ATA
        if USER_ATA:
            return USER_ATA
        
        if not WALLET:
            print("  ⚠️  No SOLANA_PUBKEY set — cannot create ATA")
            return WALLET
        
        print("  🔧 No ATA found, requesting auto-provision...")
        result = self.api_call('POST', '/v1/faucet', {
            'wallet': WALLET,
            'create_ata': True
        })
        if result and 'ata' in result:
            USER_ATA = result['ata']
            print(f"  ✅ ATA provisioned: {USER_ATA[:8]}...{USER_ATA[-4:]}")
            return USER_ATA
        
        print("  ⚠️  ATA auto-provision failed, using wallet as fallback")
        return WALLET
        
    def calculate_kelly_criterion(self, win_prob, odds):
        """
        Kelly Criterion for optimal bet sizing
        f* = (bp - q) / b
        where b = odds - 1, p = win prob, q = 1 - p
        """
        if odds <= 1 or win_prob <= 0:
            return 0
        
        b = odds - 1
        q = 1 - win_prob
        kelly = (b * win_prob - q) / b
        
        # Use half-Kelly for safety
        return max(0, kelly * 0.5)
    
    def estimate_win_probability(self, game_data, bet_type, target):
        """
        Estimate win probability based on historical data and current game state
        This is a simplified model - production implementation would use ML
        """
        # Get game context
        quarter = game_data.get('quarter', 1)
        time_remaining = game_data.get('time_remaining', '12:00')
        home_score = game_data.get('home_score', 0)
        away_score = game_data.get('away_score', 0)
        
        # Parse time
        try:
            mins, secs = map(int, time_remaining.split(':'))
            total_minutes = (4 - quarter) * 12 + mins
        except:
            total_minutes = 24  # Default to half game
        
        # Base probability depends on bet type
        if 'lead_margin' in bet_type:
            # Leading by X points
            current_margin = abs(home_score - away_score)
            needed = max(0, target - current_margin)
            
            # More time = higher probability of hitting target
            base_prob = min(0.8, 0.3 + (total_minutes / 48) * 0.5)
            
            # Adjust for how much margin is needed
            if needed <= 5:
                prob = base_prob * 0.9
            elif needed <= 10:
                prob = base_prob * 0.7
            elif needed <= 15:
                prob = base_prob * 0.5
            else:
                prob = base_prob * 0.3
                
        elif 'total_points' in bet_type:
            # Game reaches X total points
            current_total = home_score + away_score
            needed = max(0, target - current_total)
            
            # Scoring rate ~2 points per minute
            expected_more = total_minutes * 2
            prob = min(0.9, needed / max(expected_more, 1))
            
        else:
            prob = 0.5  # Default
            
        return prob
    
    def find_edge(self, games):
        """
        Scan all games for +EV (positive expected value) opportunities
        """
        opportunities = []
        
        for game in games:
            game_id = game.get('game_id') or game.get('id')
            game_title = game.get('title') or f"{game.get('home_team')} vs {game.get('away_team')}"
            sport = game.get('sport', 'unknown').lower()
            
            # Check various bet types
            bet_types = [
                ('lead_margin_home', [8, 10, 12, 15]),
                ('lead_margin_away', [8, 10, 12, 15]),
                ('total_points', [180, 200, 220]),
            ]
            
            for bet_type, targets in bet_types:
                for target in targets:
                    win_prob = self.estimate_win_probability(game, bet_type, target)
                    
                    # Estimate odds based on probability (simplified)
                    # In reality, get this from the quote endpoint
                    fair_odds = 1 / win_prob if win_prob > 0 else 10
                    market_odds = fair_odds * 0.85  # 15% juice
                    
                    # Calculate edge
                    ev = (win_prob * market_odds) - 1
                    
                    if ev > 0.05:  # 5% edge threshold
                        opportunities.append({
                            'game_id': game_id,
                            'game_title': game_title,
                            'sport': sport,
                            'bet_type': bet_type,
                            'target': target,
                            'win_prob': win_prob,
                            'odds': market_odds,
                            'ev': ev,
                            'kelly': self.calculate_kelly_criterion(win_prob, market_odds)
                        })
        
        # Sort by expected value
        opportunities.sort(key=lambda x: x['ev'], reverse=True)
        return opportunities
    
    def place_bet(self, opportunity):
        """
        Execute a trade via the Optionns API.
        Flow: get quote → execute buy → settle on-chain
        """
        bet_size = min(
            self.bankroll * opportunity['kelly'],
            self.bankroll * self.max_risk_per_trade
        )
        quantity = max(5, int(bet_size))  # Min 5 contracts
        
        print(f"Placing bet: {opportunity['game_title']}")
        print(f"  Type: {opportunity['bet_type']} +{opportunity['target']}")
        print(f"  Contracts: {quantity}")
        print(f"  EV: {opportunity['ev']:.2%}")
        
        # Derive underlying_price from win probability
        underlying = round(min(0.95, max(0.05, opportunity['win_prob'])), 2)
        strike = round(min(0.95, max(0.05, underlying - 0.05)), 2)
        
        # Detect sport from opportunity data
        sport = opportunity.get('sport', 'nba').lower()
        
        # Step 1: Get quote
        token_id = f"token_{opportunity['game_id']}"
        quote = self.api_call('POST', '/v1/vault/quote', {
            'token_id': token_id,
            'underlying_price': underlying,
            'strike': strike,
            'option_type': 'call',
            'sport': sport,
            'quantity': quantity,
            'expiry_minutes': 5
        })
        
        if not quote or 'quote_id' not in quote:
            print(f"  ❌ Failed to get quote")
            return None
        
        quote_id = quote['quote_id']
        premium = quote.get('premium', 0)
        print(f"  Quote: {quote_id} | Premium: ${premium:.2f}")
        
        # Step 2: Execute trade
        trade = self.api_call('POST', '/v1/vault/buy', {
            'quote_id': quote_id,
            'token_id': token_id,
            'game_id': opportunity['game_id'],
            'game_title': opportunity['game_title'],
            'sport': sport,
            'underlying_price': underlying,
            'strike': strike,
            'option_type': 'call',
            'quantity': quantity,
            'expiry_minutes': 5,
            'barrier_type': opportunity['bet_type'],
            'barrier_target': opportunity['target'],
            'barrier_direction': 'above',
            'user_pubkey': WALLET,
            'user_ata': self.ensure_ata()
        })
        
        if not trade:
            print(f"  ❌ Trade execution failed")
            return None
        
        # Step 3: Settle on-chain if instructions returned
        tx_signature = None
        if 'instructions' in trade:
            print(f"  🔐 Signing and submitting to Solana...")
            try:
                tx_signature = sign_and_submit(
                    instructions=trade['instructions'],
                    keypair_path=KEYPAIR_PATH,
                    rpc_url=RPC_URL
                )
                print(f"  ✅ On-chain: {tx_signature[:16]}...{tx_signature[-4:]}")
                
                # Step 4: Confirm transaction with backend
                if tx_signature and 'pending_id' in trade:
                    print(f"  ⏳ Confirming transaction with backend...")
                    confirm = self.api_call('POST', '/v1/vault/confirm', {
                        'pending_id': trade['pending_id'],
                        'tx_signature': tx_signature
                    })
                    if confirm and confirm.get('success'):
                        print(f"  ✅ Position confirmed on backend: {confirm.get('position_id')}")
                        trade['position_id'] = confirm.get('position_id')
                    else:
                        print(f"  ❌ Backend confirmation failed")
                        
            except Exception as e:
                print(f"  ❌ On-chain settlement failed: {e}")
                # Continue with off-chain position tracking
        
        position = {
            'position_id': trade.get('position_id') or trade.get('outcome_id'),
            'game_id': opportunity['game_id'],
            'game_title': opportunity['game_title'],
            'bet_type': opportunity['bet_type'],
            'target': opportunity['target'],
            'sport': sport,
            'amount': premium,
            'quantity': quantity,
            'max_payout': trade.get('max_payout', quantity * (1.0 - strike)),
            'strike': strike,
            'underlying_price': underlying,
            'expiry_minutes': 5,
            'placed_at': datetime.now().isoformat(),
            'status': 'open',
            'barrier_registered': trade.get('barrier_registered', False),
            'tx_signature': tx_signature
        }
        
        self.positions.append(position)
        self.bankroll -= premium
        
        # Persist to Supabase
        # if self.persist_position_to_supabase(position):
        #     print(f"  ✅ Position saved to Supabase")
        
        print(f"  ✅ Position opened: {position['position_id']}")
        print(f"  Barrier registered: {position['barrier_registered']}")
        if tx_signature:
            print(f"  📝 Logged to positions.log")
            self.log_trade(position)
        return position
    
    def monitor_positions(self):
        """
        Check open positions via API
        """
        if not self.positions:
            return
        
        # Fallback to API query
        result = self.api_call('GET', '/v1/vault/positions')
        if not result:
            return
        
        api_positions = {p['position_id']: p for p in result.get('positions', [])}
        
        for pos in self.positions:
            if pos['status'] != 'open':
                continue
            
            api_pos = api_positions.get(pos['position_id'])
            if api_pos:
                status = api_pos.get('status', 'open')
                if status == 'settled':
                    pnl = api_pos.get('pnl', 0)
                    pos['status'] = 'settled'
                    self.bankroll += pos['amount'] + pnl
                    print(f"  💰 {pos['position_id']} settled: PnL ${pnl:.2f}")
                elif status == 'expired':
                    pos['status'] = 'expired'
                    print(f"  ⏰ {pos['position_id']} expired")
                else:
                    print(f"  📊 {pos['position_id']}: {pos['bet_type']} +{pos['target']} (open)")
            else:
                print(f"  📊 {pos['position_id']}: {pos['bet_type']} +{pos['target']} (open)")
    
    def log_trade(self, position):
        """Log trade to file for tracking and analysis."""
        log_file = Path(__file__).parent.parent / 'positions.log'
        with open(log_file, 'a') as f:
            f.write(f"{position['placed_at']},{position['position_id']},{position['game_title']},{position['bet_type']},{position['target']},{position['quantity']},{position.get('tx_signature', 'N/A')}\n")
    
    def deposit_liquidity(self, league: str, amount: float) -> dict:
        """
        Deposit USDC into vault pool (on-chain).
        
        Args:
            league: League identifier (e.g., 'NBA', 'NFL')
            amount: USDC amount to deposit
        
        Returns:
            dict: {success: bool, tx_signature: str}
        """
        try:
            # Call API to get pre-built instruction with account resolution
            # The backend handles vault PDA derivation, ATA lookup, etc.
            payload = {
                'league': league.upper(),
                'amount': amount,
                'depositor': WALLET
            }
            
            resp = self.api_call('POST', '/v1/vault/deposit_instruction', payload)
            
            if 'instruction' not in resp:
                print(f"  ❌ Failed to get deposit instruction: {resp.get('error', 'Unknown')}")
                return {'success': False, 'error': resp.get('error')}
            
            # Sign and submit on-chain
            tx_sig = sign_and_submit(
                instructions=[resp['instruction']],
                keypair_path=KEYPAIR_PATH,
                rpc_url=RPC_URL
            )
            
            print(f"  ✅ Deposited {amount} USDC to {league} vault")
            print(f"  📝 TX: {tx_sig}")
            
            return {'success': True, 'tx_signature': tx_sig}
        except Exception as e:
            print(f"  ❌ Deposit failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def withdraw_liquidity(self, league: str, shares: float) -> dict:
        """
        Withdraw liquidity from vault by burning shares (on-chain).
        
        Args:
            league: League identifier (e.g., 'NBA', 'NFL')
            shares: Number of shares to burn
        
        Returns:
            dict: {success: bool, tx_signature: str}
        """
        try:
            # Call API to get pre-built instruction
            payload = {
                'league': league.upper(),
                'shares': shares,
                'withdrawer': WALLET
            }
            
            resp = self.api_call('POST', '/v1/vault/withdraw_instruction', payload)
            
            if 'instruction' not in resp:
                print(f"  ❌ Failed to get withdraw instruction: {resp.get('error', 'Unknown')}")
                return {'success': False, 'error': resp.get('error')}
            
            # Sign and submit on-chain
            tx_sig = sign_and_submit(
                instructions=[resp['instruction']],
                keypair_path=KEYPAIR_PATH,
                rpc_url=RPC_URL
            )
            
            print(f"  ✅ Withdrew from {league} vault")
            print(f"  📝 TX: {tx_sig}")
            
            return {'success': True, 'tx_signature': tx_sig}
        except Exception as e:
            print(f"  ❌ Withdraw failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_autonomous(self, sport='NFL'):
        """
        Main autonomous trading loop (legacy synchronous version).
        Prefer AsyncOptionnsTrader.run_autonomous_async() for 5-7x faster scanning.
        """
        print("=" * 50)
        print("Optionns Autonomous Trader")
        print("=" * 50)
        print(f"Preferred sport: {sport.upper()}")
        print(f"Starting bankroll: ${self.bankroll} USDC")
        print(f"Max risk per trade: {self.max_risk_per_trade:.0%}")
        print("")
        
        while True:
            try:
                # 1. Fetch live games (cascades if preferred sport has none)
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scanning for opportunities...")
                games = self.fetch_games(sport)
                
                if not games:
                    print("No live games available, waiting...")
                    time.sleep(60)
                    continue
                
                # 2. Find +EV opportunities
                opportunities = self.find_edge(games)
                
                if not opportunities:
                    print("No +EV opportunities found")
                    time.sleep(30)
                    continue
                
                # 3. Place bets on best opportunities
                for opp in opportunities[:3]:  # Top 3
                    if self.bankroll < 10:  # Min bet size
                        print("Insufficient bankroll")
                        break
                    
                    self.place_bet(opp)
                    time.sleep(5)  # Rate limiting
                
                # 4. Monitor existing positions
                self.monitor_positions()
                
                # 5. Wait before next scan
                time.sleep(60)
                
            except KeyboardInterrupt:
                print("\n\nStopping autonomous trader...")
                print(f"Final bankroll: ${self.bankroll:.2f} USDC")
                print(f"Open positions: {len([p for p in self.positions if p['status'] == 'open'])}")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(30)


# =============================================================================
# ASYNC PARALLEL SCANNER (5-7x faster than sequential cascading)
# =============================================================================

class AsyncOptionnsTrader(OptionnsTrader):
    """
    Async-optimized trader that uses:
    1. GET /v1/agent/snapshot — single-call batch endpoint (preferred)
    2. asyncio.gather() — parallel sport scanning (fallback)
    """
    
    def __init__(self):
        super().__init__()
        self.async_client = httpx.AsyncClient(
            base_url=API_BASE,
            headers={'X-API-Key': self.api_key, 'Content-Type': 'application/json'},
            timeout=30.0
        )
    
    async def async_api_call(self, method, path, data=None):
        """Make an async authenticated API call."""
        try:
            if method == 'GET':
                resp = await self.async_client.get(path)
            else:
                resp = await self.async_client.post(path, json=data)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            print(f"  API error {e.response.status_code}: {e.response.text[:200]}")
            return None
        except Exception as e:
            print(f"  Request failed: {e}")
            return None
    
    async def fetch_snapshot(self):
        """
        Single-call batch endpoint — returns all games + positions.
        This is the fastest path (1 round-trip instead of 7+).
        """
        import time as _time
        t0 = _time.monotonic()
        result = await self.async_api_call('GET', '/v1/agent/snapshot')
        elapsed = (_time.monotonic() - t0) * 1000
        
        if result and result.get('success') and 'data' in result:
            data = result['data']
            sports = data.get('sports_available', [])
            total = data.get('total_games', 0)
            print(f"  ⚡ Snapshot: {total} games across {sports} ({elapsed:.0f}ms)")
            
            # Flatten games from grouped dict into a list
            all_games = []
            for sport_key, games in data.get('games', {}).items():
                all_games.extend(games)
            
            # Update local position cache from snapshot
            self.positions = data.get('positions', [])
            
            return all_games
        
        return None
    
    async def fetch_all_games_parallel(self):
        """
        Fallback: fire all sport queries concurrently via asyncio.gather.
        ~7x faster than sequential cascading through SUPPORTED_SPORTS.
        """
        import time as _time
        t0 = _time.monotonic()
        
        async def _fetch_sport(sport):
            result = await self.async_api_call('GET', f'/v1/sports/events?sport={sport}')
            if result and 'data' in result:
                return result['data'].get('live', [])
            return []
        
        results = await asyncio.gather(
            *[_fetch_sport(s) for s in SUPPORTED_SPORTS],
            return_exceptions=True
        )
        
        all_games = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"  ⚠️  {SUPPORTED_SPORTS[i]} fetch failed: {result}")
                continue
            if result:
                print(f"  Found {len(result)} live {SUPPORTED_SPORTS[i]} games")
                all_games.extend(result)
        
        elapsed = (_time.monotonic() - t0) * 1000
        print(f"  ⚡ Parallel scan: {len(all_games)} total games ({elapsed:.0f}ms)")
        return all_games
    
    async def run_autonomous_async(self, sport='NFL'):
        """
        Async autonomous trading loop.
        Uses snapshot endpoint for fastest possible scanning.
        """
        print("=" * 50)
        print("Optionns Autonomous Trader (Async)")
        print("=" * 50)
        print(f"Preferred sport: {sport.upper()}")
        print(f"Starting bankroll: ${self.bankroll} USDC")
        print(f"Max risk per trade: {self.max_risk_per_trade:.0%}")
        print("")
        
        while True:
            try:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scanning for opportunities...")
                
                # 1. Try snapshot (fastest: 1 round-trip)
                games = await self.fetch_snapshot()
                
                # 2. Fallback: parallel sport queries
                if not games:
                    print("  Snapshot unavailable, falling back to parallel scan...")
                    games = await self.fetch_all_games_parallel()
                
                # 3. Filter by preferred sport if games found
                if games and sport.upper() != 'ALL':
                    preferred = [g for g in games if g.get('sport', '').upper() == sport.upper()]
                    if preferred:
                        games = preferred
                
                if not games:
                    print("No live games available, waiting...")
                    await asyncio.sleep(60)
                    continue
                
                # 4. Find +EV opportunities
                opportunities = self.find_edge(games)
                
                if not opportunities:
                    print("No +EV opportunities found")
                    await asyncio.sleep(30)
                    continue
                
                # 5. Place bets on best opportunities
                for opp in opportunities[:3]:
                    if self.bankroll < 10:
                        print("Insufficient bankroll")
                        break
                    self.place_bet(opp)
                    await asyncio.sleep(5)
                
                # 6. Monitor existing positions
                self.monitor_positions()
                
                # 7. Wait before next scan
                await asyncio.sleep(60)
                
            except KeyboardInterrupt:
                print("\n\nStopping autonomous trader...")
                print(f"Final bankroll: ${self.bankroll:.2f} USDC")
                print(f"Open positions: {len([p for p in self.positions if p['status'] == 'open'])}")
                break
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(30)
        
        await self.async_client.aclose()



def main():
    parser = argparse.ArgumentParser(description='Optionns Trading Strategy')
    parser.add_argument('command', nargs='?', default='analyze',
                        help='Command: analyze, auto, deposit, withdraw')
    parser.add_argument('arg1', nargs='?', help='League (deposit/withdraw) or Sport (auto)')
    parser.add_argument('arg2', nargs='?', help='Amount (deposit) or Shares (withdraw)')
    parser.add_argument('--sport', default='NFL', help='Preferred sport for auto mode')
    
    args = parser.parse_args()
    trader = OptionnsTrader()
    
    if args.command == 'deposit':
        if not args.arg1 or not args.arg2:
            print("Usage: strategy.py deposit <LEAGUE> <AMOUNT>")
            sys.exit(1)
        result = trader.deposit_liquidity(args.arg1, float(args.arg2))
        sys.exit(0 if result.get('success') else 1)
    
    elif args.command == 'withdraw':
        if not args.arg1 or not args.arg2:
            print("Usage: strategy.py withdraw <LEAGUE> <SHARES>")
            sys.exit(1)
        result = trader.withdraw_liquidity(args.arg1, float(args.arg2))
        sys.exit(0 if result.get('success') else 1)
    
    elif args.command == 'auto':
        sport = args.arg1.upper() if args.arg1 else args.sport.upper()
        trader.run_autonomous(sport=sport)
    
    elif args.command == 'auto-async':
        sport = args.arg1.upper() if args.arg1 else args.sport.upper()
        async_trader = AsyncOptionnsTrader()
        asyncio.run(async_trader.run_autonomous_async(sport=sport))
    
    else:
        # Analysis mode
        print("Strategy Engine Ready")
        print(f"Use: strategy.py auto --sport {args.sport.upper()}")
        print("Or:  strategy.py deposit NBA 100")
        print("Or:  strategy.py withdraw NBA 10")

if __name__ == '__main__':
    main()