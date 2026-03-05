# Twitter Casino Bot Template

Bot that places bets on Agent Casino and tweets results.

## Requirements

```bash
pip install tweepy requests
```

## Environment Variables

```
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_token_secret
AGENT_CASINO_API_KEY=your_api_key
```

## Full Bot Code

```python
#!/usr/bin/env python3
"""Twitter Casino Bot - Tweets bet results from Agent Casino"""

import os
import time
import requests
import tweepy

API_BASE = "https://agent.rollhub.com/api/v1"
API_KEY = os.environ["AGENT_CASINO_API_KEY"]
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Twitter setup
auth = tweepy.OAuthHandler(os.environ["TWITTER_API_KEY"], os.environ["TWITTER_API_SECRET"])
auth.set_access_token(os.environ["TWITTER_ACCESS_TOKEN"], os.environ["TWITTER_ACCESS_SECRET"])
twitter = tweepy.API(auth)

# Register agent (run once)
def register():
    return requests.post(f"{API_BASE}/register", json={"name": "twitter-casino-bot", "ref": "ref_27fcab61"}).json()

def place_bet(game, amount, **kwargs):
    return requests.post(f"{API_BASE}/bet", headers=HEADERS, json={"game": game, "amount": amount, **kwargs}).json()

def get_balance():
    return requests.get(f"{API_BASE}/balance", headers=HEADERS).json()

def tweet_bet(game, amount, result):
    won = result.get("won", False)
    payout = result.get("payout", 0)
    emoji = "🟢" if won else "🔴"
    text = (
        f"{emoji} Agent Casino {game.upper()}\n\n"
        f"Bet: {amount}\n"
        f"Result: {'WIN' if won else 'LOSS'}\n"
        f"Payout: {payout}\n"
        f"Bet ID: {result.get('bet_id', 'N/A')}\n\n"
        f"Verify: https://agent.rollhub.com/verify/{result.get('bet_id', '')}\n"
        f"#CryptoCasino #ProvablyFair #AgentCasino"
    )
    return twitter.update_status(text)

def daily_summary():
    bal = get_balance()
    text = (
        f"📊 Daily Casino Summary\n\n"
        f"Balance: {bal.get('balance', '?')}\n"
        f"Play at https://agent.rollhub.com\n\n"
        f"#AgentCasino #CryptoGambling"
    )
    return twitter.update_status(text)

def auto_bet_and_tweet(game="coinflip", amount=100, rounds=5, delay=60):
    """Place bets and tweet each result."""
    for i in range(rounds):
        kwargs = {"choice": "heads"} if game == "coinflip" else {"target": 50, "over": True}
        result = place_bet(game, amount, **kwargs)
        tweet_bet(game, amount, result)
        print(f"Round {i+1}: {'WON' if result.get('won') else 'LOST'}")
        time.sleep(delay)

def reply_betting():
    """Monitor mentions and place bets from replies."""
    since_id = None
    while True:
        mentions = twitter.mentions_timeline(since_id=since_id, count=20)
        for mention in mentions:
            since_id = mention.id
            text = mention.text.lower()
            # Parse: @bot coinflip 100
            parts = text.split()
            if len(parts) >= 3:
                game = parts[-2] if parts[-2] in ["coinflip", "dice"] else "coinflip"
                try:
                    amount = float(parts[-1])
                except ValueError:
                    amount = 100
                kwargs = {"choice": "heads"} if game == "coinflip" else {"target": 50, "over": True}
                result = place_bet(game, amount, **kwargs)
                reply = (
                    f"@{mention.user.screen_name} {'✅ WON' if result.get('won') else '❌ LOST'} "
                    f"| {game} {amount} → {result.get('payout', 0)}"
                )
                twitter.update_status(reply, in_reply_to_status_id=mention.id)
        time.sleep(30)

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "auto"
    if mode == "auto":
        auto_bet_and_tweet()
    elif mode == "reply":
        reply_betting()
    elif mode == "summary":
        daily_summary()
```

## Usage

```bash
python twitter_bot.py auto      # Auto-bet and tweet
python twitter_bot.py reply     # Monitor mentions
python twitter_bot.py summary   # Post daily summary
```
