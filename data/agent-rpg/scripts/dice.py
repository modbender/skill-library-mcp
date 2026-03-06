# Dice Roller

import argparse
import random
import re

def roll(expression):
    # Parse 1d20+5
    match = re.match(r'(\d+)d(\d+)([+-]\d+)?', expression)
    if not match:
        print("Invalid format. Use XdY+Z (e.g., 1d20+5)")
        return

    count = int(match.group(1))
    sides = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0

    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls) + modifier

    print(f"Expression: {expression}")
    print(f"Rolls: {rolls}")
    print(f"Modifier: {modifier:+}")
    print(f"Total: {total}")

    if sides == 20 and count == 1:
        if rolls[0] == 20:
            print("CRITICAL SUCCESS! (Nat 20)")
        elif rolls[0] == 1:
            print("CRITICAL FAILURE! (Nat 1)")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("expression", help="Dice expression (e.g., 1d20+5)")
    args = parser.parse_args()
    roll(args.expression)

if __name__ == "__main__":
    main()
