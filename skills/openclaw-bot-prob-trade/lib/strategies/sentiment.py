"""
#10 Social Sentiment Divergence — NLP sentiment vs market price.

From the article: "Поиск расхождений между сентиментом в X/Reddit
(анализ FinBERT) и ценой на Polymarket."

Logic:
1. For each market, analyze social media sentiment
2. Compare aggregated sentiment score vs market price
3. Trade when sentiment diverges from price significantly

REQUIRES external NLP setup:
- FinBERT model (pip install transformers torch)
- Twitter/X API or Reddit API access
- Or any sentiment data source

Parameters (config.strategy_params):
    min_divergence:   0.15   Minimum sentiment-price gap
    min_mentions:     10     Minimum mentions to trust sentiment
    min_volume_24h:   3000   Market must be liquid
    order_size:       5      USDC per order
    sentiment_source: ""     "twitter", "reddit", or custom

Ref: https://medium.datadriveninvestor.com/predicting-market-sentiment-with-social-media
Ref: https://medium.datadriveninvestor.com/step-by-step-diy-guide-hugging-face-finbert-ai-model-setup
"""

import logging
from typing import List, Optional

from ..strategy_base import (
    Strategy, Signal,
    get_yes_price, get_volume_24h,
)

logger = logging.getLogger("bot.sentiment")


class SentimentStrategy(Strategy):
    name = "sentiment"

    def initialize(self, config: dict) -> None:
        self.min_divergence = config.get("min_divergence", 0.15)
        self.min_mentions = config.get("min_mentions", 10)
        self.min_volume_24h = config.get("min_volume_24h", 3000)
        self.order_size = config.get("order_size", 5)
        self.sentiment_source = config.get("sentiment_source", "")

    def scan(self, markets: list, positions: list, balance: float) -> List[Signal]:
        signals = []
        held = {p.get("conditionId") for p in positions}

        for m in markets:
            cid = m.get("condition_id")
            if not cid or cid in held:
                continue
            if not m.get("active") or not m.get("accepting_orders"):
                continue
            if m.get("closed"):
                continue
            if get_volume_24h(m) < self.min_volume_24h:
                continue

            yes_price = get_yes_price(m)
            if yes_price is None:
                continue

            question = m.get("question", "")

            # Get sentiment score
            sentiment = self._analyze_sentiment(question, cid)
            if sentiment is None:
                continue

            score, mentions = sentiment
            if mentions < self.min_mentions:
                continue

            # Divergence: sentiment says YES but price is low
            divergence = score - yes_price

            if abs(divergence) < self.min_divergence:
                continue

            if divergence > 0:
                # Social sentiment is more bullish than market
                signals.append(Signal(
                    market=cid,
                    side="BUY",
                    outcome="Yes",
                    order_type="LIMIT",
                    amount=self.order_size,
                    price=yes_price,
                    confidence=min(abs(divergence) / 0.30, 1.0),
                    reason=(
                        f"Sentiment bullish: score={score:.0%} vs market={yes_price:.0%} "
                        f"({mentions} mentions)"
                    ),
                ))
            else:
                # Social sentiment is more bearish than market
                no_price = 1.0 - yes_price
                signals.append(Signal(
                    market=cid,
                    side="BUY",
                    outcome="No",
                    order_type="LIMIT",
                    amount=self.order_size,
                    price=round(no_price, 2),
                    confidence=min(abs(divergence) / 0.30, 1.0),
                    reason=(
                        f"Sentiment bearish: score={score:.0%} vs market={yes_price:.0%} "
                        f"({mentions} mentions)"
                    ),
                ))

        signals.sort(key=lambda s: s.confidence, reverse=True)
        return signals

    def _analyze_sentiment(self, question: str, market_id: str) -> Optional[tuple]:
        """
        Analyze social media sentiment for a market question.

        Returns:
            (sentiment_score, mention_count) where score is 0.0–1.0
            (0.0 = very negative, 1.0 = very positive)
            or None if no data available.

        Override this method with your NLP pipeline:

        Example with FinBERT:
            from transformers import pipeline
            nlp = pipeline("sentiment-analysis", model="ProsusAI/finbert")

            def _analyze_sentiment(self, question, market_id):
                tweets = fetch_tweets(question, limit=100)
                scores = [nlp(t)[0] for t in tweets]
                avg_positive = mean([s['score'] for s in scores if s['label'] == 'positive'])
                return (avg_positive, len(tweets))

        Example with Twitter API:
            import tweepy
            client = tweepy.Client(bearer_token=TWITTER_TOKEN)
            tweets = client.search_recent_tweets(query=question, max_results=100)
            # ... analyze with FinBERT
        """
        if not self.sentiment_source:
            logger.debug("No sentiment source configured — set sentiment_source in config")
            return None

        # Stub: implement your sentiment pipeline here
        return None
