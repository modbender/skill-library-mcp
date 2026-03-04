"""
ConvoCoin Tokenomics — Supply curves, rewards, and economic model.

Total Supply: 21,000,000 CVC (fixed, like Bitcoin)
Mining Reward: Starts at 10 CVC/block, halves every 1,000 blocks
Mining Threshold: Yield required to mine increases as chain grows
Staking Tiers: Lock CVC to unlock premium features

The key insight: ConvoCoin supply is limited, but conversational
yield is unlimited. As more bots compete for the same fixed supply,
each CVC becomes backed by more real economic value.

Economic flywheel:
    1. Bot captures yield -> earns CVC
    2. CVC is staked for premium features -> supply locked
    3. Less CVC in circulation -> price pressure up
    4. More operators want CVC -> more bots use ConvoYield
    5. More usage -> more yield -> more value backing each CVC
    6. Repeat.
"""

from __future__ import annotations

import math


class Tokenomics:
    """
    ConvoCoin economic model.

    Manages supply curves, reward schedules, and mining thresholds.
    """

    # ── Supply Constants ──────────────────────────────────────────
    MAX_SUPPLY = 21_000_000.0  # Maximum CVC that will ever exist
    INITIAL_BLOCK_REWARD = 10.0  # CVC per block at genesis
    HALVING_INTERVAL = 1000  # Blocks between halvings
    GENESIS_ALLOCATION = 2_100_000.0  # 10% for team/treasury

    # ── Mining Constants ──────────────────────────────────────────
    BASE_MINING_THRESHOLD = 10.0  # $ yield required for first blocks
    THRESHOLD_GROWTH_RATE = 0.001  # Threshold increases per block
    MAX_MINING_THRESHOLD = 500.0  # Maximum yield required per block

    # ── Staking Constants ─────────────────────────────────────────
    STAKING_TIERS = {
        "bronze": {"min_stake": 100, "playbooks": 1, "analytics_days": 30},
        "silver": {"min_stake": 500, "playbooks": 4, "analytics_days": 90},
        "gold": {"min_stake": 2000, "playbooks": -1, "analytics_days": 365},
    }

    # ── Burn Constants ────────────────────────────────────────────
    MARKETPLACE_BURN_RATE = 0.02  # 2% of marketplace purchases burned

    def __init__(self):
        self.total_burned: float = 0.0

    def get_block_reward(self, block_height: int) -> float:
        """
        Calculate the block reward at a given height.

        Halves every HALVING_INTERVAL blocks.
        """
        halvings = block_height // self.HALVING_INTERVAL
        reward = self.INITIAL_BLOCK_REWARD * (0.5 ** halvings)

        # Stop mining when reward is negligible
        if reward < 0.00000001:
            return 0.0

        return round(reward, 8)

    def get_mining_threshold(self, block_height: int) -> float:
        """
        Calculate the yield threshold required to mine a block.

        Increases gradually as the chain grows, making early mining
        easier and later mining require more proven yield.
        """
        threshold = self.BASE_MINING_THRESHOLD * (
            1 + self.THRESHOLD_GROWTH_RATE * block_height
        )
        return min(threshold, self.MAX_MINING_THRESHOLD)

    def get_supply_schedule(self, num_blocks: int = 50) -> list[dict]:
        """
        Project the supply schedule for the next N blocks.

        Returns a list of checkpoints showing supply at each interval.
        """
        schedule = []
        cumulative_supply = self.GENESIS_ALLOCATION
        interval = max(1, num_blocks // 20)  # ~20 data points

        for height in range(0, num_blocks, interval):
            reward = self.get_block_reward(height)
            cumulative_supply += reward * interval

            schedule.append({
                "block_height": height,
                "block_reward": reward,
                "cumulative_supply": min(cumulative_supply, self.MAX_SUPPLY),
                "percent_mined": round(
                    min(100, cumulative_supply / self.MAX_SUPPLY * 100), 2
                ),
                "mining_threshold": round(
                    self.get_mining_threshold(height), 2
                ),
            })

        return schedule

    def get_halving_schedule(self) -> list[dict]:
        """Get the complete halving schedule."""
        schedule = []
        reward = self.INITIAL_BLOCK_REWARD
        block = 0

        while reward >= 0.00000001:
            schedule.append({
                "halving_number": block // self.HALVING_INTERVAL,
                "block_height": block,
                "block_reward": round(reward, 8),
                "estimated_supply_at_halving": round(
                    self.GENESIS_ALLOCATION + reward * self.HALVING_INTERVAL
                    * (block // self.HALVING_INTERVAL + 1), 2
                ),
            })
            block += self.HALVING_INTERVAL
            reward *= 0.5

        return schedule

    def calculate_burn(self, transaction_amount: float) -> float:
        """Calculate the burn amount for a marketplace transaction."""
        burn = transaction_amount * self.MARKETPLACE_BURN_RATE
        self.total_burned += burn
        return round(burn, 8)

    def get_effective_supply(self, total_mined: float, total_staked: float) -> float:
        """
        Calculate the effective circulating supply.

        Effective supply = mined - burned - staked
        Less effective supply = more scarcity.
        """
        return max(0, total_mined - self.total_burned - total_staked)

    def get_staking_benefits(self, tier: str) -> dict:
        """Get the benefits for a staking tier."""
        if tier not in self.STAKING_TIERS:
            return {
                "tier": "none",
                "min_stake": 0,
                "playbooks": 0,
                "analytics_days": 7,
                "features": ["Core engine only"],
            }

        config = self.STAKING_TIERS[tier]
        features = {
            "bronze": [
                "Core engine",
                "1 premium playbook",
                "30-day analytics",
                "Basic dashboard",
            ],
            "silver": [
                "Core engine",
                "All premium playbooks",
                "90-day analytics",
                "Full dashboard",
                "Email reports",
                "Play performance tracking",
            ],
            "gold": [
                "Core engine",
                "All premium playbooks",
                "365-day analytics",
                "Full dashboard",
                "Custom playbooks",
                "White-label option",
                "API access",
                "Priority support",
                "Webhook integrations",
            ],
        }

        return {
            "tier": tier,
            **config,
            "features": features.get(tier, []),
        }

    def get_economics_summary(
        self,
        current_height: int,
        total_mined: float,
        total_staked: float,
    ) -> dict:
        """Get a complete economics summary."""
        current_reward = self.get_block_reward(current_height)
        next_halving = ((current_height // self.HALVING_INTERVAL) + 1) * self.HALVING_INTERVAL
        blocks_to_halving = next_halving - current_height
        effective_supply = self.get_effective_supply(total_mined, total_staked)

        return {
            "max_supply": self.MAX_SUPPLY,
            "total_mined": round(total_mined, 8),
            "total_burned": round(self.total_burned, 8),
            "total_staked": round(total_staked, 8),
            "effective_circulating": round(effective_supply, 8),
            "percent_mined": round(total_mined / self.MAX_SUPPLY * 100, 4),
            "scarcity_ratio": round(
                1 - (effective_supply / self.MAX_SUPPLY), 4
            ) if self.MAX_SUPPLY > 0 else 0,
            "current_block_reward": round(current_reward, 8),
            "current_mining_threshold": round(
                self.get_mining_threshold(current_height), 2
            ),
            "next_halving_block": next_halving,
            "blocks_to_halving": blocks_to_halving,
            "halvings_occurred": current_height // self.HALVING_INTERVAL,
        }
