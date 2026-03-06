#!/usr/bin/env python3
"""
Verification Solver - Handles Moltbook's anti-bot verification challenges
"""

import re
import time
from typing import Optional, Tuple

class VerificationSolver:
    """Solves Moltbook verification challenges automatically."""
    
    # Number word mapping
    NUMBER_WORDS = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
        'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
        'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
        'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
        'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
        'eighty': 80, 'ninety': 90, 'hundred': 100,
        # Compound patterns handled in parsing
    }
    
    def parse_number(self, text: str) -> Optional[int]:
        """Parse number from text (digits or words)."""
        # Try direct digit extraction
        digits = re.findall(r'\d+', text)
        if digits:
            return int(digits[0])
        
        # Try word parsing
        text_lower = text.lower()
        
        # Check for compound numbers like "thirty-two", "thirty two"
        # First pass: look for exact matches
        for word, value in sorted(self.NUMBER_WORDS.items(), key=lambda x: -len(x[0])):
            if word in text_lower:
                return value
        
        return None
    
    def parse_compound_number(self, text: str) -> Optional[int]:
        """Parse compound numbers like 'Thirty Two' or 'thirty-two'."""
        text = text.lower().replace('-', ' ')
        words = text.split()
        
        total = 0
        temp = 0
        
        for word in words:
            # Clean word
            clean = re.sub(r'[^a-z]', '', word)
            if not clean:
                continue
            
            # Check for number words
            if clean in self.NUMBER_WORDS:
                val = self.NUMBER_WORDS[clean]
                if val >= 100:
                    if temp == 0:
                        temp = 1
                    temp *= val
                else:
                    temp += val
            elif clean == 'and':
                continue
        
        total += temp
        return total if total > 0 else None
    
    def solve_math_challenge(self, challenge: str) -> Optional[float]:
        """Solve verification math challenge.
        
        Examples:
        - "Thirty Two Newtons and other claw adds Fourteen" -> 46.00
        - "Eight plus Seven" -> 15.00
        """
        # Extract numbers
        numbers = []
        
        # Look for patterns like "Word Word adds Word" or "Word plus Word"
        # Strategy: find all potential number phrases and parse them
        
        # Split by operation words
        parts = re.split(r'(?:plus|adds?|and|\+)', challenge, flags=re.IGNORECASE)
        
        for part in parts:
            # Try to parse number from this part
            num = self.parse_compound_number(part)
            if num is None:
                num = self.parse_number(part)
            if num is not None:
                numbers.append(num)
        
        if len(numbers) >= 2:
            result = sum(numbers[:2])  # Usually just two numbers
            return float(result)
        
        return None
    
    def solve(self, challenge: str, code: str = None) -> Tuple[bool, Optional[str]]:
        """Solve verification challenge.
        
        Returns:
            (success, answer_or_error)
        """
        answer = self.solve_math_challenge(challenge)
        
        if answer is None:
            return False, f"Could not parse challenge: {challenge}"
        
        # Format as required (usually 2 decimal places)
        formatted = f"{answer:.2f}"
        
        return True, formatted
    
    def verify_and_retry(self, api_call, challenge_required: bool = True, max_retries: int = 3) -> bool:
        """Wrapper for API calls that may require verification.
        
        Usage:
            solver = VerificationSolver()
            success = solver.verify_and_retry(
                lambda: post_comment(post_id, content),
                challenge_required=True
            )
        """
        for attempt in range(max_retries):
            try:
                result = api_call()
                
                # Check if verification required in result
                if isinstance(result, dict) and result.get('verification_required'):
                    challenge = result.get('verification', {}).get('challenge', '')
                    vcode = result.get('verification', {}).get('code', '')
                    
                    success, answer = self.solve(challenge, vcode)
                    if not success:
                        print(f"Failed to solve: {answer}")
                        return False
                    
                    # Resubmit with verification
                    # TODO: Implement actual verification submission
                    print(f"Solved: {challenge} = {answer}, would resubmit")
                    return True
                
                return True
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return False
        
        return False


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: verification_solver.py 'challenge text'")
        print("Example: verification_solver.py 'Thirty Two adds Fourteen'")
        sys.exit(1)
    
    challenge = ' '.join(sys.argv[1:])
    solver = VerificationSolver()
    
    success, answer = solver.solve(challenge)
    
    if success:
        print(f"Challenge: {challenge}")
        print(f"Answer: {answer}")
    else:
        print(f"Failed: {answer}")
        sys.exit(1)


if __name__ == '__main__':
    main()
