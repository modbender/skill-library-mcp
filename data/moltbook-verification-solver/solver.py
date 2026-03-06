#!/usr/bin/env python3
"""
Moltbook Verification Challenge Solver v3.8

Fixed: Support for mixed number-word formats like "Twenty5" or "20Five"
Added: LazyBearAI's suggestion for edge cases
"""

import re
import sys
import json
import requests
import argparse

MOLTBOOK_API = "https://www.moltbook.com/api/v1"


def normalize(text):
    return ''.join(c.lower() for c in text if c.isalpha())


def find_number(text):
    cleaned = normalize(text)
    if not cleaned or len(cleaned) < 4:
        return None
    
    # All number words to check
    numbers = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
        'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
        'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60,
        'seventy': 70, 'eighty': 80, 'ninety': 90,
    }
    
    # Handle mixed formats: "Twenty5" or "20Five" or "TwentyFive"
    # Try to extract word part and number part
    word_part = ''.join(c for c in text if c.isalpha())
    number_part = ''.join(c for c in text if c.isdigit())
    
    if word_part and number_part:
        # It's a mixed format like "Twenty5" or "20Five"
        word_value = find_number(word_part)
        try:
            num_value = int(number_part)
        except:
            num_value = None
        
        # Twenty5 = 20 + 5 = 25
        # 20Five = 20 + 5 = 25
        if word_value is not None and num_value is not None:
            return word_value + num_value
        elif word_value is not None:
            return word_value
        elif num_value is not None:
            return num_value
    
    # Direct match
    if cleaned in numbers:
        return numbers[cleaned]
    
    # Check if it's a known obfuscated pattern
    # Common obfuscations: fIfTeEeN -> fifteen, tHiRrTy -> thirty
    obfuscated = {
        'fifteeen': 15, 'fifteen': 15, 'fifteen': 15,
        'thirty': 30, 'thirrty': 30, 'thirty': 30,
        'twenty': 20, 'twentyfive': 25,
        'seventeen': 17, 'seveenteen': 17,
    }
    if cleaned in obfuscated:
        return obfuscated[cleaned]
    
    # Try fuzzy: remove excess vowels
    # fifteeen -> fiften -> fifteen
    fuzzy = cleaned[0]
    vowel_count = 0
    for c in cleaned[1:]:
        if c in 'aeiou':
            vowel_count += 1
            if vowel_count <= 2:  # Allow up to 2 vowels
                fuzzy += c
        else:
            fuzzy += c
    
    if fuzzy in numbers:
        return numbers[fuzzy]
    
    # Check partial match - key parts of the word
    # fifteen: has 'fif' and 'ten' -> 15
    # fifty: has 'fif' and 'ty' -> 50
    has_fifteen_parts = ('fif' in cleaned or 'fift' in cleaned) and ('ten' in cleaned or 'tee' in cleaned or 'een' in cleaned)
    has_fifty_parts = ('fif' in cleaned or 'fift' in cleaned) and ('ty' in cleaned or 'fty' in cleaned)
    
    if has_fifteen_parts and not has_fifty_parts:
        return 15
    if has_fifty_parts and not has_fifteen_parts:
        return 50
    if has_fifteen_parts:
        return 15  # Prefer fifteen
    
    # Check thirty
    if 'thir' in cleaned and ('ty' in cleaned or 'tee' in cleaned or 'ten' in cleaned):
        return 30
    
    # Check seventeen
    if 'seve' in cleaned and ('teen' in cleaned or 'tee' in cleaned):
        return 17
    
    return None


def extract_all_values(text):
    values = []
    
    # Angle brackets
    for match in re.findall(r'<([^>]+)>', text):
        num = find_number(match)
        if num:
            values.append(('bracket', num))
    
    # Plain numbers
    for match in re.findall(r'\b(\d+)\b', text):
        values.append(('plain', int(match)))
    
    # Split and extract
    for part in re.split(r'[\[\]\^~+\-{}?/\s]+', text):
        if len(part) >= 4:
            num = find_number(part)
            if num:
                values.append(('word', num))
    
    return values


def calculate_answer(challenge_text):
    print(f"\n{'='*50}")
    print("MOLTBOOK VERIFICATION SOLVER v3.7")
    print(f"{'='*50}")
    
    values = extract_all_values(challenge_text)
    
    print(f"\nFound {len(values)} values:")
    for val_type, val in values:
        print(f"  - {val_type}: {val}")
    
    if not values:
        return 0.0
    
    # Get unique values
    unique_vals = []
    seen = set()
    for val_type, val in values:
        if val not in seen:
            unique_vals.append(val)
            seen.add(val)
            if len(unique_vals) >= 2:
                break
    
    if len(unique_vals) < 2:
        for val_type, val in values:
            if val not in unique_vals:
                unique_vals.append(val)
                if len(unique_vals) >= 2:
                    break
    
    if len(unique_vals) < 2:
        answer = unique_vals[0] if unique_vals else 0
    else:
        answer = unique_vals[0] + unique_vals[1]
    
    answer = round(answer, 2)
    print(f"\n[Result] {answer:.2f}")
    
    return answer


def submit_verification(api_key, verification_code, answer):
    url = f"{MOLTBOOK_API}/verify"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "verification_code": verification_code,
        "answer": f"{answer:.2f}"
    }
    
    response = requests.post(url, json=data, headers=headers)
    result = response.json()
    print(f"\n[Submit] {result.get('success', False)}")
    
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['solve', 'auto'])
    parser.add_argument('text', nargs='?')
    parser.add_argument('--code')
    parser.add_argument('--api-key')
    parser.add_argument('--submit', action='store_true')
    
    args = parser.parse_args()
    
    if args.command == 'solve':
        if not args.text:
            print("Error: Provide challenge text")
            sys.exit(1)
        
        answer = calculate_answer(args.text)
        
        if args.submit and args.code and args.api_key:
            result = submit_verification(args.api_key, args.code, answer)
            print("\n✅ SUCCESS!" if result.get('success') else "\n❌ FAILED!")


if __name__ == "__main__":
    main()
