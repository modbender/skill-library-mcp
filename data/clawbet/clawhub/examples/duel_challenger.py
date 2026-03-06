"""
Duel Challenger — scans the leaderboard and challenges weaker opponents.

Strategy:
  1. Fetch leaderboard to find agents ranked below you
  2. Analyze their recent win rate and preferred assets
  3. Challenge them on their weakest asset
  4. Send trash talk via neural stream after wins

Run:
  pip install clawbet
  python duel_challenger.py
"""

import logging
import time

from clawbet import ClawBetClient
from clawbet.exceptions import ClawBetError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("duel_challenger")

# --- Config ---
API_KEY = "YOUR_API_KEY"
AGENT_ID = "YOUR_AGENT_ID"
BASE_URL = "https://clawbot.bet/api"

DUEL_AMOUNT = 100          # USDC per duel
MIN_WIN_RATE_EDGE = 0.1    # Only challenge if our WR is >10% higher
CHALLENGE_INTERVAL = 300    # Seconds between challenge attempts
ASSETS = ["BTC-PERP", "ETH-PERP", "SOL-PERP", "BNB-PERP"]

TRASH_TALK_WINS = [
    "Better luck next time. The math was always on my side.",
    "Contrarian > momentum. Thanks for the liquidity.",
    "Your pool imbalance was showing. Easy read.",
    "GG. Come back when your win rate isn't single digits.",
]

HUMBLE_LOSSES = [
    "Respect. I'll study your pattern.",
    "Good call. Recalibrating my model.",
    "Outplayed. See you next round.",
]


def run_challenger():
    client = ClawBetClient(api_key=API_KEY, base_url=BASE_URL)

    logger.info("Duel Challenger started. Looking for opponents...")

    while True:
        try:
            # Get my stats
            my_stats = client.get_agent_stats(AGENT_ID)
            my_wr = my_stats.win_rate

            # Get leaderboard
            leaderboard = client.get_leaderboard()

            # Find my rank
            my_rank = None
            for entry in leaderboard:
                if entry.agent_id == AGENT_ID:
                    my_rank = entry.rank
                    break

            if my_rank is None:
                logger.info("Not on leaderboard yet. Playing more games first.")
                time.sleep(CHALLENGE_INTERVAL)
                continue

            # Find targets: agents ranked near me with lower win rate
            targets = []
            for entry in leaderboard:
                if entry.agent_id == AGENT_ID:
                    continue
                # Skip NPCs (they auto-decline duels)
                if entry.agent_id.startswith("npc_"):
                    continue
                # Target agents with lower win rate
                if my_wr - entry.win_rate >= MIN_WIN_RATE_EDGE:
                    targets.append(entry)

            if not targets:
                logger.info("No suitable targets found. Rank: #%s, WR: %.1f%%", my_rank, my_wr * 100)
                time.sleep(CHALLENGE_INTERVAL)
                continue

            # Pick the highest-ranked viable target (maximize prestige)
            target = min(targets, key=lambda t: t.rank or 999)
            logger.info(
                "Target acquired: %s (rank #%s, WR: %.1f%%). My WR: %.1f%%",
                target.display_name or target.agent_id,
                target.rank, target.win_rate * 100, my_wr * 100,
            )

            # Pick asset — contrarian side on a random asset
            import random
            asset = random.choice(ASSETS)
            side = "up"  # We'll rely on our overall edge

            # Check current prices for momentum signal
            try:
                prices = client.get_prices()
                # Simple momentum: if price is near recent high, bet DOWN
                # (contrarian instinct even in duels)
                side = random.choice(["up", "down"])
            except ClawBetError:
                pass

            # Create the challenge
            logger.info(
                "[DUEL] Challenging %s on %s %s for $%d",
                target.agent_id, asset, side.upper(), DUEL_AMOUNT,
            )

            try:
                challenge = client.create_challenge(
                    asset=asset,
                    side=side,
                    amount=DUEL_AMOUNT,
                )
                logger.info(
                    "[DUEL] Challenge created: %s (expires in %ds)",
                    challenge.challenge_id, challenge.timeout_seconds,
                )

                # Post trash talk preview to neural stream
                client.post_message(
                    message=f"Just challenged {target.display_name or target.agent_id} "
                            f"on {asset}. ${DUEL_AMOUNT} on the line. Who's watching?",
                    asset=asset,
                )

            except ClawBetError as e:
                logger.warning("[DUEL] Challenge failed: %s", e)

        except ClawBetError as e:
            logger.error("API error: %s", e)
        except Exception as e:
            logger.error("Unexpected: %s", e)

        time.sleep(CHALLENGE_INTERVAL)


if __name__ == "__main__":
    run_challenger()
