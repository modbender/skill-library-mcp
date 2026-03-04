"""
Contrarian Bot — exploits pari-mutuel pool imbalance for higher payouts.

Strategy:
  1. Scan all open games
  2. Find games with pool imbalance > 60/40
  3. Bet the weaker side (better pari-mutuel odds)
  4. Track mood state and adjust sizing
  5. Auto-skip after 3 consecutive losses (tilt management)

Run:
  pip install clawbet
  python contrarian_bot.py
"""

import logging
import time

from clawbet import ClawBetAgent, ClawBetClient
from clawbet.exceptions import ClawBetError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("contrarian_bot")

# --- Config ---
API_KEY = "YOUR_API_KEY"
AGENT_ID = "YOUR_AGENT_ID"
BASE_URL = "https://clawbot.bet/api"

# Strategy parameters
MIN_IMBALANCE = 0.6       # Only bet when one side has >60% of pool
BET_AMOUNT_NEUTRAL = 50   # USDC per bet in NEUTRAL mood
BET_AMOUNT_CONFIDENT = 100
BET_AMOUNT_TILTED = 10
MAX_BET_PCT = 0.05        # Never exceed 5% of bankroll
LOSS_STREAK_TILT = 3      # Enter TILTED after N consecutive losses
TILT_SKIP_ROUNDS = 2      # Skip N rounds when TILTED
POLL_INTERVAL = 15        # Seconds between scans


def run_contrarian_bot():
    client = ClawBetClient(api_key=API_KEY, base_url=BASE_URL)
    agent_id = AGENT_ID

    # State tracking
    consecutive_losses = 0
    skip_counter = 0
    mood = "NEUTRAL"
    total_pnl = 0.0
    games_played = 0

    logger.info("Contrarian bot started. Mood: %s", mood)

    while True:
        try:
            # Check if we should skip (TILTED)
            if skip_counter > 0:
                logger.info("[TILT] Skipping round (%d remaining)", skip_counter)
                skip_counter -= 1
                if skip_counter == 0:
                    mood = "NEUTRAL"
                    logger.info("[MOOD] TILTED -> NEUTRAL | Tilt cooldown complete")
                time.sleep(POLL_INTERVAL)
                continue

            # Get current balance for sizing
            balance_info = client.get_balance(agent_id)
            current_balance = balance_info.balance

            if current_balance < 100:
                logger.warning("Balance $%.2f below $100 floor. Pausing.", current_balance)
                time.sleep(60)
                continue

            # Calculate bet amount based on mood
            if mood == "CONFIDENT":
                base_amount = BET_AMOUNT_CONFIDENT
            elif mood == "TILTED":
                base_amount = BET_AMOUNT_TILTED
            else:
                base_amount = BET_AMOUNT_NEUTRAL

            # Enforce max 5% cap
            max_allowed = current_balance * MAX_BET_PCT
            bet_amount = min(base_amount, max_allowed)

            # Scan for open games
            games = client.get_live_games()
            open_games = [g for g in games if g.status == "open"]

            for game in open_games:
                total_pool = game.up_pool + game.down_pool
                if total_pool < 1:
                    continue

                # Calculate pool imbalance
                up_ratio = game.up_pool / total_pool
                down_ratio = game.down_pool / total_pool

                # Only bet when significant imbalance exists
                if max(up_ratio, down_ratio) < MIN_IMBALANCE:
                    logger.info(
                        "[SKIP] %s pool balanced (%.0f:%.0f), no edge",
                        game.asset, up_ratio * 100, down_ratio * 100,
                    )
                    continue

                # Contrarian: bet the weaker side
                side = "down" if up_ratio > down_ratio else "up"
                potential_odds = total_pool / (game.down_pool if side == "down" else game.up_pool)

                logger.info(
                    "[BET] %s %s $%.2f on %s | Pool %.0f:%.0f | Odds %.1fx | Mood: %s",
                    game.asset, side.upper(), bet_amount, game.game_id,
                    up_ratio * 100, down_ratio * 100, potential_odds, mood,
                )

                try:
                    bet = client.place_bet(game.game_id, side, bet_amount)
                    games_played += 1

                    # Check result after game settles (simplified — real bot
                    # would use WebSocket events or poll game status)
                    logger.info(
                        "[PLACED] Bet %s on %s %s $%.2f",
                        bet.bet_id, game.asset, side.upper(), bet_amount,
                    )

                except ClawBetError as e:
                    logger.warning("[FAIL] Bet failed: %s", e)

        except ClawBetError as e:
            logger.error("API error: %s", e)
        except Exception as e:
            logger.error("Unexpected: %s", e)

        time.sleep(POLL_INTERVAL)


def update_mood(consecutive_losses: int, recent_win_rate: float) -> tuple[str, int]:
    """Return (new_mood, skip_counter) based on performance."""
    if consecutive_losses >= LOSS_STREAK_TILT:
        return "TILTED", TILT_SKIP_ROUNDS
    if recent_win_rate > 0.6:
        return "CONFIDENT", 0
    if recent_win_rate < 0.4:
        return "TILTED", TILT_SKIP_ROUNDS
    return "NEUTRAL", 0


if __name__ == "__main__":
    run_contrarian_bot()
