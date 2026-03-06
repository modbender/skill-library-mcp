#!/usr/bin/env python3
"""
Basic grammar and spell checker
Usage: python3 grammar_check.py "email text here"
"""
import sys
import re

def basic_grammar_check(text):
    """Basic grammar checks without external dependencies"""
    issues = []
    
    # Common spelling errors
    typos = {
        'recieve': 'receive', 'occured': 'occurred', 'seperate': 'separate',
        'definately': 'definitely', 'accomodate': 'accommodate',
        'tommorow': 'tomorrow', 'untill': 'until', 'truely': 'truly',
        'occassion': 'occasion', 'embarass': 'embarrass', 'wierd': 'weird',
        'beleive': 'believe', 'acheive': 'achieve', 'adress': 'address',
        'begining': 'beginning', 'calender': 'calendar', 'collegue': 'colleague',
        'concious': 'conscious', 'dissapoint': 'disappoint', 'enviroment': 'environment',
        'existance': 'existence', 'foriegn': 'foreign', 'goverment': 'government',
        'harrass': 'harass', 'independant': 'independent', 'jewelery': 'jewelry',
        'liason': 'liaison', 'maintainance': 'maintenance', 'neccessary': 'necessary',
        'occurance': 'occurrence', 'persue': 'pursue', 'refered': 'referred',
        'succesful': 'successful', 'wierd': 'weird'
    }
    
    for wrong, right in typos.items():
        if re.search(r'\b' + wrong + r'\b', text, re.IGNORECASE):
            issues.append(f"Spelling: '{wrong}' → '{right}'")
    
    # Basic grammar patterns
    if re.search(r'\bi\s', text):  # lowercase 'i'
        issues.append("Grammar: 'i' should be capitalized to 'I'")
    
    if re.search(r'\s{2,}', text):
        issues.append("Formatting: Multiple spaces detected")
    
    if re.search(r'[.!?]\s*[a-z]', text):
        issues.append("Grammar: Sentence should start with capital letter")
    
    # Double punctuation
    if re.search(r'[.!?]{2,}', text):
        issues.append("Punctuation: Multiple punctuation marks")
    
    # Common grammar mistakes
    if re.search(r'\byour\s+welcome\b', text, re.IGNORECASE):
        issues.append("Grammar: 'your welcome' should be 'you're welcome'")
    
    if re.search(r'\bits\s+a\b', text, re.IGNORECASE):
        issues.append("Grammar: Consider 'it's a' (contraction) vs 'its a'")
    
    if re.search(r'\btheir\s+(going|doing|working)', text, re.IGNORECASE):
        issues.append("Grammar: 'their' should be 'they're' (they are)")
    
    # Check for incomplete sentences (very basic)
    sentences = re.split(r'[.!?]+', text)
    for sent in sentences:
        sent = sent.strip()
        if sent and len(sent.split()) == 1 and len(sent) > 3:
            issues.append(f"Possible fragment: '{sent}'")
    
    return issues

def suggest_improvements(text):
    """Suggest style improvements"""
    suggestions = []
    
    # Passive voice detection (basic)
    passive_patterns = [
        r'\b(was|were|been|being)\s+\w+ed\b',
        r'\b(is|are)\s+\w+ed\b'
    ]
    
    for pattern in passive_patterns:
        if re.search(pattern, text):
            suggestions.append("Style: Consider using active voice instead of passive")
            break
    
    # Wordiness
    wordy_phrases = {
        'in order to': 'to',
        'due to the fact that': 'because',
        'at this point in time': 'now',
        'for the purpose of': 'to',
        'in the event that': 'if',
        'with regard to': 'about',
        'in spite of the fact that': 'although'
    }
    
    for wordy, concise in wordy_phrases.items():
        if wordy in text.lower():
            suggestions.append(f"Conciseness: '{wordy}' → '{concise}'")
    
    return suggestions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 grammar_check.py 'text'")
        print("Example: python3 grammar_check.py 'i recieve your email tommorow'")
        sys.exit(1)
    
    text = sys.argv[1]
    issues = basic_grammar_check(text)
    suggestions = suggest_improvements(text)
    
    if issues:
        print("⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"  • {issue}")
    
    if suggestions:
        print("\n💡 SUGGESTIONS:")
        for suggestion in suggestions:
            print(f"  • {suggestion}")
    
    if not issues and not suggestions:
        print("✅ No basic issues found")
    
    # Exit code: 0 if no issues, 1 if issues found
    sys.exit(1 if issues else 0)
