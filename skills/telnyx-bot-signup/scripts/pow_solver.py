#!/usr/bin/env python3
"""Proof of Work solver for Telnyx bot signup challenge."""

import hashlib
import sys


def solve(nonce: str, leading_zero_bits: int, algorithm: str = "sha256") -> int:
    """Find an integer solution where hash(nonce + str(solution)) has the required leading zero bits."""
    hash_fn = getattr(hashlib, algorithm)
    target = 0  # leading_zero_bits leading zeros means the integer value of those bits is 0
    for candidate in range(0, 2**63):
        digest = hash_fn(f"{nonce}{candidate}".encode()).hexdigest()
        # Convert first N bits to int and check if they're all zero
        digest_int = int(digest, 16)
        digest_bits = digest_int.bit_length()
        total_bits = len(digest) * 4  # each hex char = 4 bits
        leading_zeros = total_bits - digest_bits
        if leading_zeros >= leading_zero_bits:
            return candidate
    raise RuntimeError("No solution found")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <nonce> <leading_zero_bits> [algorithm]", file=sys.stderr)
        sys.exit(1)

    nonce = sys.argv[1]
    leading_zero_bits = int(sys.argv[2])
    algorithm = sys.argv[3] if len(sys.argv) > 3 else "sha256"

    solution = solve(nonce, leading_zero_bits, algorithm)
    print(solution)
