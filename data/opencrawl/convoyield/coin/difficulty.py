"""
Mining Difficulty Adjustment — Dynamic hash target, like Bitcoin.

Bitcoin adjusts difficulty every 2016 blocks to maintain a
10-minute average block time. If blocks come too fast, difficulty
increases. Too slow, it decreases.

ConvoCoin does the same, but with a twist:
- Target block time: 60 seconds (faster than Bitcoin)
- Adjustment interval: every 100 blocks
- Difficulty = how many leading zero bits the block hash needs
- But: you also need proof-of-yield (real captured value)

So mining ConvoCoin requires BOTH:
1. Captured conversational yield (proof-of-yield)
2. A hash below the difficulty target (proof-of-work, lightweight)

The proof-of-work component is intentionally light — it exists to
rate-limit block creation and make the chain tamper-resistant,
not to burn electricity. The real "work" is the yield capture.
"""

from __future__ import annotations

import hashlib
import time


class DifficultyAdjuster:
    """
    Manages mining difficulty for the ConvoCoin chain.

    Difficulty is expressed as a target: the block hash must be
    below this target to be valid. Lower target = harder mining.
    """

    TARGET_BLOCK_TIME = 60.0    # Target: 1 block per minute
    ADJUSTMENT_INTERVAL = 100   # Adjust every 100 blocks
    MAX_ADJUSTMENT_FACTOR = 4.0 # Max 4x change per adjustment
    MIN_DIFFICULTY = 1          # Minimum difficulty (1 leading zero bit)
    MAX_DIFFICULTY = 32         # Maximum difficulty (32 leading zero bits)
    INITIAL_DIFFICULTY = 4      # Start with 4 leading zero bits

    def __init__(self):
        self.current_difficulty = self.INITIAL_DIFFICULTY
        self._block_timestamps: list[float] = []

    def record_block(self, timestamp: float):
        """Record a block's timestamp for difficulty calculation."""
        self._block_timestamps.append(timestamp)

    def should_adjust(self, block_height: int) -> bool:
        """Check if difficulty should be adjusted at this height."""
        return (
            block_height > 0 and
            block_height % self.ADJUSTMENT_INTERVAL == 0
        )

    def adjust(self, block_height: int) -> int:
        """
        Recalculate difficulty based on recent block times.

        If blocks are coming too fast -> increase difficulty
        If blocks are coming too slow -> decrease difficulty

        Returns the new difficulty level.
        """
        if not self.should_adjust(block_height):
            return self.current_difficulty

        # Get the timestamps for the last adjustment interval
        recent = self._block_timestamps[-self.ADJUSTMENT_INTERVAL:]
        if len(recent) < 2:
            return self.current_difficulty

        # Calculate actual time for the interval
        actual_time = recent[-1] - recent[0]
        expected_time = self.TARGET_BLOCK_TIME * (len(recent) - 1)

        if actual_time <= 0 or expected_time <= 0:
            return self.current_difficulty

        # Ratio: >1 means blocks are too slow, <1 means too fast
        ratio = actual_time / expected_time

        # Clamp the adjustment factor
        ratio = max(1 / self.MAX_ADJUSTMENT_FACTOR,
                     min(self.MAX_ADJUSTMENT_FACTOR, ratio))

        # Adjust difficulty
        if ratio < 0.75:
            # Blocks too fast — increase difficulty
            self.current_difficulty = min(
                self.MAX_DIFFICULTY,
                self.current_difficulty + 1,
            )
        elif ratio > 1.5:
            # Blocks too slow — decrease difficulty
            self.current_difficulty = max(
                self.MIN_DIFFICULTY,
                self.current_difficulty - 1,
            )

        return self.current_difficulty

    def get_target(self) -> str:
        """
        Get the current hash target as a hex string.

        The block hash must be less than this target.
        Difficulty N means the first N bits must be zero.
        """
        # Target = 2^(256 - difficulty) - expressed as hex
        target_int = (1 << (256 - self.current_difficulty)) - 1
        return format(target_int, "064x")

    def check_hash(self, block_hash: str) -> bool:
        """Check if a hash meets the current difficulty target."""
        target = self.get_target()
        return block_hash < target

    def mine_block_hash(
        self,
        block_header: str,
        max_nonce: int = 1_000_000,
    ) -> tuple[int, str] | None:
        """
        Find a nonce that produces a hash below the target.

        This is the proof-of-work component. It's intentionally
        lightweight — ConvoCoin's primary proof is yield, not work.

        Args:
            block_header: The block header data to hash
            max_nonce: Maximum nonces to try before giving up

        Returns:
            (nonce, hash) if found, None if max_nonce exceeded
        """
        target = self.get_target()

        for nonce in range(max_nonce):
            data = f"{block_header}:{nonce}"
            hash_result = hashlib.sha256(data.encode()).hexdigest()

            if hash_result < target:
                return nonce, hash_result

        return None  # Failed to find valid nonce within limit

    def get_stats(self) -> dict:
        """Get difficulty statistics."""
        avg_block_time = 0.0
        if len(self._block_timestamps) >= 2:
            recent = self._block_timestamps[-20:]
            intervals = [
                recent[i] - recent[i - 1]
                for i in range(1, len(recent))
            ]
            avg_block_time = sum(intervals) / len(intervals) if intervals else 0

        return {
            "current_difficulty": self.current_difficulty,
            "target": self.get_target()[:16] + "...",
            "target_block_time": self.TARGET_BLOCK_TIME,
            "avg_block_time": round(avg_block_time, 2),
            "adjustment_interval": self.ADJUSTMENT_INTERVAL,
            "blocks_until_adjustment": (
                self.ADJUSTMENT_INTERVAL -
                (len(self._block_timestamps) % self.ADJUSTMENT_INTERVAL)
            ),
            "total_blocks_recorded": len(self._block_timestamps),
        }

    def get_hashrate_estimate(self) -> float:
        """
        Estimate the network hashrate (hashes per second).

        Based on current difficulty and observed block times.
        """
        if len(self._block_timestamps) < 2:
            return 0.0

        recent = self._block_timestamps[-10:]
        if len(recent) < 2:
            return 0.0

        avg_time = (recent[-1] - recent[0]) / (len(recent) - 1)
        if avg_time <= 0:
            return 0.0

        # Expected hashes = 2^difficulty
        expected_hashes = 2 ** self.current_difficulty
        return expected_hashes / avg_time
