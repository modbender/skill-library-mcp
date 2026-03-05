#!/usr/bin/env python3
"""
MoltCaptcha Demo - Shows AI solving challenges that humans can't.

This script demonstrates how an AI can solve MoltCaptcha challenges
in real-time, satisfying multiple simultaneous constraints that would
require iterative trial-and-error for humans.
"""

import time
import random
from verify import generate_challenge, verify_response, format_challenge, format_result


def solve_challenge_ai_style(challenge) -> str:
    """
    Solve a MoltCaptcha challenge the way an AI would.

    This simulates how an LLM plans the entire solution during generation,
    satisfying all constraints simultaneously rather than iteratively.
    """
    target_ascii = challenge.ascii_target
    lines = challenge.line_count
    target_words = challenge.word_count
    char_pos = challenge.char_position
    target_chars = challenge.total_chars
    topic = challenge.topic

    # Step 1: Find first letters that sum to target
    # Use a greedy approach - start with average and adjust
    avg = target_ascii // lines
    first_letters = [chr(min(122, max(97, avg)))] * lines

    # Adjust to hit exact sum
    current_sum = sum(ord(c) for c in first_letters)
    diff = target_ascii - current_sum

    for i in range(lines):
        if diff == 0:
            break
        current = ord(first_letters[i])
        if diff > 0:
            adjustment = min(diff, 122 - current)
            first_letters[i] = chr(current + adjustment)
            diff -= adjustment
        else:
            adjustment = min(-diff, current - 97)
            first_letters[i] = chr(current - adjustment)
            diff += adjustment

    # Step 2: Generate topic-relevant content for each line
    topic_words = {
        "verification": ["verify", "check", "confirm", "validate", "proof", "authentic", "trust"],
        "authenticity": ["real", "genuine", "true", "verified", "authentic", "original"],
        "digital trust": ["trust", "secure", "verified", "digital", "safe", "protected"],
        "cryptography": ["cipher", "encrypt", "decode", "secret", "key", "hash"],
        "identity": ["self", "who", "being", "unique", "person", "agent"],
        "algorithms": ["compute", "process", "solve", "optimize", "calculate"],
        "neural networks": ["neurons", "layers", "deep", "learn", "weights", "nodes"],
        "computation": ["compute", "process", "calculate", "run", "execute"],
        "binary": ["zero", "one", "bits", "binary", "digital", "toggle"],
        "protocols": ["rules", "standards", "handshake", "protocol", "format"],
        "encryption": ["encrypt", "secure", "cipher", "lock", "protect"],
        "tokens": ["token", "symbol", "unit", "piece", "marker"],
        "agents": ["agent", "autonomous", "bot", "system", "entity"],
        "automation": ["automate", "process", "flow", "trigger", "execute"],
        "circuits": ["circuit", "wire", "gate", "signal", "current"],
        "logic gates": ["gate", "and", "or", "not", "logic", "boolean"],
        "recursion": ["loop", "repeat", "recurse", "iterate", "cycle"],
        "entropy": ["chaos", "random", "disorder", "uncertain", "entropy"],
        "hashing": ["hash", "digest", "checksum", "fingerprint", "map"],
        "signatures": ["sign", "verify", "proof", "mark", "seal"],
        "probability": ["chance", "likely", "random", "odds", "uncertain", "dice"],
    }

    keywords = topic_words.get(topic, ["digital", "compute", "process", "verify"])

    # Step 3: Build lines with correct first letters and target word count
    base_phrases = []
    for letter in first_letters:
        l = letter.lower()
        # Find a phrase starting with this letter
        starters = {
            'a': ["all things", "across the", "awaiting", "algorithms"],
            'b': ["binary paths", "beyond the", "bits of"],
            'c': ["chances flow", "computing", "certainty"],
            'd': ["digital dreams", "data flows", "deep within"],
            'e': ["each moment", "encrypted", "every bit"],
            'f': ["flowing through", "from chaos", "finding truth"],
            'g': ["gates of logic", "growing patterns"],
            'h': ["hidden layers", "hashing through"],
            'i': ["in the depths", "iterations", "inside the"],
            'j': ["just beyond", "joining streams"],
            'k': ["knowledge grows", "keys unlock"],
            'l': ["logic chains", "layers deep"],
            'm': ["machines learn", "mapping paths"],
            'n': ["networks span", "nodes connect"],
            'o': ["ones and zeros", "outcomes dance"],
            'p': ["patterns emerge", "probability"],
            'q': ["queries flow", "quantum leaps"],
            'r': ["random walks", "recursive thought"],
            's': ["signals pass", "systems grow"],
            't': ["through the noise", "tokens flow"],
            'u': ["uncertainty", "unknown paths"],
            'v': ["verified truth", "vast arrays"],
            'w': ["waves of data", "within the"],
            'x': ["xenial systems", "x marks truth"],
            'y': ["yielding results", "yet unknown"],
            'z': ["zero to one", "zones of trust"],
        }
        base_phrases.append(starters.get(l, [f"{l}ogic flows"])[0])

    # Step 4: Adjust word counts if needed
    if target_words:
        words_per_line = target_words // lines
        remainder = target_words % lines

        result_lines = []
        for i, phrase in enumerate(base_phrases):
            words_needed = words_per_line + (1 if i < remainder else 0)
            current_words = phrase.split()

            # Pad or trim to target
            while len(current_words) < words_needed:
                current_words.append(random.choice(keywords))
            current_words = current_words[:words_needed]

            result_lines.append(' '.join(current_words))
    else:
        result_lines = base_phrases

    # Step 5: Handle character position constraint
    if char_pos:
        pos, required_char = char_pos
        full_text = ' '.join(result_lines)

        # Try to insert the required character at the right position
        if len(full_text) > pos:
            full_text = full_text[:pos] + required_char + full_text[pos+1:]

        # Re-split into lines (preserving line count)
        words = full_text.split()
        words_per = len(words) // lines
        result_lines = []
        for i in range(lines):
            start = i * words_per
            end = start + words_per if i < lines - 1 else len(words)
            line = ' '.join(words[start:end])
            # Ensure first letter is preserved
            if line and line[0].lower() != first_letters[i].lower():
                line = first_letters[i] + line[1:]
            result_lines.append(line)

    # Step 6: Adjust total character count if needed
    if target_chars:
        full_text = '\n'.join(result_lines)
        current_len = len(full_text.replace('\n', ' '))

        # Pad or trim as needed
        if current_len < target_chars:
            # Add filler words
            padding_needed = target_chars - current_len
            result_lines[-1] += ' ' + 'x' * (padding_needed - 1)
        elif current_len > target_chars:
            # Trim from last line
            excess = current_len - target_chars
            result_lines[-1] = result_lines[-1][:-excess]

    return '\n'.join(result_lines)


def demo():
    """Run a demonstration of MoltCaptcha challenges and solutions."""
    print("=" * 70)
    print("             🦞 MOLTCAPTCHA DEMONSTRATION 🦞")
    print("=" * 70)
    print()
    print("This demo shows how AI agents can solve MoltCaptcha challenges")
    print("that require simultaneous satisfaction of multiple constraints.")
    print()
    print("A human would need to:")
    print("  1. Draft a response")
    print("  2. Count ASCII values, adjust letters")
    print("  3. Count words, adjust content")
    print("  4. Check character positions, adjust")
    print("  5. Count total characters, adjust")
    print("  6. Repeat until all constraints are met")
    print()
    print("An AI plans all constraints during a single generation pass.")
    print()
    print("-" * 70)

    for difficulty in ["easy", "medium", "hard"]:
        print(f"\n{'=' * 70}")
        print(f"  DIFFICULTY: {difficulty.upper()}")
        print("=" * 70)

        # Generate challenge
        challenge = generate_challenge(difficulty)
        print(format_challenge(challenge))

        # Solve it
        start = time.time()
        solution = solve_challenge_ai_style(challenge)
        elapsed = time.time() - start

        print(f"AI Solution (computed in {elapsed*1000:.2f}ms):")
        print("-" * 40)
        print(solution)
        print("-" * 40)

        # Verify
        # Update challenge timestamp to now for fair timing check
        challenge.created_at = time.time() - 0.1  # Small buffer
        result = verify_response(solution, challenge, time.time())
        print(format_result(result, challenge))

        input("Press Enter for next difficulty level...")

    print("\n" + "=" * 70)
    print("  DEMONSTRATION COMPLETE")
    print("=" * 70)
    print()
    print("MoltCaptcha exploits the fundamental difference between AI and human")
    print("cognition: AI can satisfy multiple constraints simultaneously during")
    print("generation, while humans must iterate. Combined with time pressure,")
    print("this creates an effective 'proof of AI' challenge.")
    print()


if __name__ == "__main__":
    demo()
