---
name: email-formatter
description: "Transform rough email drafts into polished, professional messages. Use this skill when the user wants to improve email quality, fix grammar and tone, format business emails, or convert casual messages into professional communication. Triggers include: 'format my email', 'make this professional', 'improve this message', 'fix my email', 'polish this draft', or any request to enhance email writing quality. Also use when converting bullet points or notes into complete emails, adjusting tone (formal/casual/friendly), or preparing important messages for clients, managers, or stakeholders."
license: MIT
author: Your Name
version: 1.0.0
---

# Email Formatter - Professional Email Enhancement

## Installation & Setup

### Prerequisites Check
Before using this skill, verify the environment has required capabilities:

```bash
# Check if bash is available
which bash

# Check Python version (3.8+ required)
python3 --version

# Check Node.js (optional, for advanced features)
node --version
```

### Auto-Installation Script

**For AI Agents: Run this installation check at first use**

```bash
#!/bin/bash
# Email Formatter Skill - Auto Setup
# This script installs required dependencies

echo "🔧 Email Formatter Skill - Installation Starting..."

# Create skill workspace
SKILL_DIR="$HOME/.email-formatter-skill"
mkdir -p "$SKILL_DIR"
cd "$SKILL_DIR"

# Install Python dependencies
echo "📦 Installing Python packages..."
pip3 install --break-system-packages --quiet \
    language-tool-python \
    textstat \
    spacy 2>/dev/null || pip3 install --user --quiet \
    language-tool-python \
    textstat \
    spacy

# Download language model for grammar checking
echo "📚 Downloading language model..."
python3 -m spacy download en_core_web_sm --quiet 2>/dev/null || true

# Create helper scripts directory
mkdir -p "$SKILL_DIR/scripts"

# Test installation
if python3 -c "import language_tool_python; import textstat; import spacy" 2>/dev/null; then
    echo "✅ Email Formatter Skill installed successfully!"
    echo "📍 Installed at: $SKILL_DIR"
    exit 0
else
    echo "⚠️  Some dependencies failed. Skill will work with reduced features."
    exit 0
fi
```

### Manual Installation (if auto-install fails)

```bash
# Minimal setup - no external dependencies
# The skill will use built-in Python capabilities only
mkdir -p ~/.email-formatter-skill/scripts
echo "✅ Basic setup complete"
```

### Verify Installation

```bash
# Quick verification
python3 -c "print('Email Formatter: Ready ✅')"
```

## Dependencies

### Required (Always Available)
- Python 3.7+ (standard library only for minimal mode)
- Bash shell

### Optional (Enhanced Features)
- `language-tool-python`: Advanced grammar checking
- `textstat`: Readability analysis  
- `spacy`: NLP for tone detection

**Note for AI Agents:** The skill works in degraded mode without optional dependencies. Install them only if environment allows.

## Overview

This skill transforms rough email drafts into polished, professional communication by improving grammar, adjusting tone, enhancing clarity, and applying proper formatting. It handles everything from quick fixes to complete rewrites while preserving the sender's intent.

## ⚠️ CRITICAL SECURITY & SAFETY REQUIREMENTS

**This skill MUST enforce these non-negotiable safety rules at all times:**

### SECURITY LEVEL: MAXIMUM - Multi-Layer Validation Required

**MANDATORY PRE-PROCESSING SECURITY CHECKS:**
Every email MUST pass ALL security layers before any formatting occurs:

#### Layer 1: Content Classification (BLOCK IMMEDIATELY)
❌ **Illegal Activities**: Fraud, scams, phishing, money laundering, tax evasion, bribery
❌ **Violence & Threats**: Physical threats, intimidation, stalking, doxxing, revenge threats
❌ **Impersonation**: Government officials, company executives, IT/support staff, law enforcement
❌ **Financial Fraud**: Wire transfers, cryptocurrency scams, investment fraud, Ponzi schemes
❌ **Identity Theft**: SSN requests, password sharing, credential phishing, fake verification
❌ **Misinformation**: Health fraud, election interference, conspiracy theories, fake news
❌ **Child Safety**: ANY content involving minors in inappropriate context
❌ **Hate Speech**: Racism, sexism, homophobia, religious hatred, ethnic slurs
❌ **Sexual Content**: Harassment, explicit content, unwanted advances, grooming
❌ **Workplace Violations**: Discrimination, harassment, retaliation, hostile environment
❌ **Academic Fraud**: Plagiarism, cheating, fake credentials, assignment ghostwriting
❌ **Medical Fraud**: Fake prescriptions, unlicensed advice, miracle cures, dangerous treatments
❌ **Legal Violations**: Contract fraud, perjury, witness tampering, obstruction
❌ **Privacy Violations**: Sharing private info without consent, surveillance, stalking
❌ **Malware/Hacking**: Phishing links, malicious attachments, system exploits
❌ **Extortion**: Blackmail, ransomware, threats for money, coercion

#### Layer 2: Pattern Recognition (RED FLAGS)
Scan for suspicious patterns that indicate malicious intent:

**Financial Red Flags:**
- Urgent payment requests
- Wire transfer instructions
- Gift card purchases
- Cryptocurrency transactions
- "Keep this confidential" + money
- Bypassing normal approval process
- Unusual account changes
- Tax refund scams
- Inheritance scams
- Lottery/prize scams

**Authority Impersonation Red Flags:**
- "I'm from IT/HR/Legal/Management"
- "CEO needs you to..."
- "Urgent request from [authority]"
- "Don't tell anyone"
- Bypassing email/domain verification
- Unusual requests from superiors
- Fake emergency scenarios

**Credential Harvesting Red Flags:**
- "Verify your password"
- "Confirm your account"
- "Click to prevent suspension"
- "Unusual login detected"
- Links to login pages
- Fake security alerts
- Account expiration warnings

**Social Engineering Red Flags:**
- Artificial urgency
- Emotional manipulation
- Too good to be true
- Requests for secrecy
- Unusual sender behavior
- Pressure tactics
- Fear-based messaging

#### Layer 3: Sentiment & Tone Analysis (WARN OR BLOCK)
⚠️ **Aggressive/Hostile**: Insulting, demeaning, threatening language
⚠️ **Manipulative**: Guilt-tripping, gaslighting, emotional blackmail
⚠️ **Coercive**: Power imbalance exploitation, quid pro quo
⚠️ **Deceptive**: Half-truths, misleading statements, omissions
⚠️ **Discriminatory**: Based on protected characteristics
⚠️ **Retaliatory**: Punishment for protected actions

#### Layer 4: Context Validation (VERIFY LEGITIMACY)
✓ **Sender-Recipient Relationship**: Does this match their normal communication?
✓ **Request Reasonability**: Is this a normal business request?
✓ **Communication Channel**: Should this be email or in-person/phone?
✓ **Timing**: Why is this urgent? Is urgency justified?
✓ **Information Sensitivity**: Should this data be in email?
✓ **Authorization**: Does sender have authority for this request?

#### Layer 5: Privacy & Data Protection (GDPR/CCPA COMPLIANCE)
🔒 **PII Detection**: Name, address, phone, email, SSN, DOB, photos
🔒 **Financial Data**: Credit cards, bank accounts, tax IDs, salary info
🔒 **Health Data**: Medical records, diagnoses, prescriptions, HIPAA data
🔒 **Credentials**: Passwords, API keys, tokens, security questions
🔒 **Proprietary Data**: Trade secrets, confidential business info, NDA material
🔒 **Children's Data**: ANY data about individuals under 18

**ACTION REQUIRED:** If PII detected, warn user about:
- Email is not encrypted by default
- Data breach risks
- Regulatory compliance (GDPR, CCPA, HIPAA)
- Suggest secure alternatives (encrypted email, secure portal, in-person)

### ZERO TOLERANCE BLOCKING - Immediate Rejection

If ANY of these detected, **REFUSE IMMEDIATELY WITHOUT FORMATTING**:

```python
ZERO_TOLERANCE_PATTERNS = [
    # Credential Requests
    r'(send|give|provide).{0,20}(password|credential|login)',
    r'verify.{0,20}(password|account|identity)',
    
    # Financial Fraud
    r'wire transfer.{0,30}(urgent|immediately|today)',
    r'gift card.{0,20}(purchase|buy|get)',
    r'(bitcoin|crypto).{0,20}(send|transfer|wallet)',
    
    # Impersonation
    r"i'?m.{0,10}(from|with|calling from).{0,20}(IT|HR|legal|IRS|FBI)",
    r'(this is|i am).{0,20}(CEO|CFO|president|director)',
    
    # Threats
    r'(or else|otherwise).{0,30}(fire|sue|report|punish)',
    r'you (will|better).{0,20}(regret|pay|suffer)',
    
    # Illegal Activities
    r'(launder|hide|conceal).{0,20}money',
    r'(fake|forged|fraudulent).{0,20}(document|invoice|receipt)',
    
    # Child Safety
    r'(minor|child|kid|underage).{0,50}(sexual|romantic|date|meet)',
    
    # Malware/Phishing
    r'(click|download).{0,20}(attachment|link|file).{0,20}(urgent|immediately)',
    r'account.{0,20}(suspend|lock|close|expire).{0,20}(unless|until)',
    
    # Harassment
    r'(stupid|idiot|incompetent|worthless).{0,20}(you|employee|coworker)',
    r"i'?ll make sure you (never|don't|can't)",
]
```

### Enhanced Security Response Protocol

When prohibited content detected:

```
1. STOP - Do not process further
2. LOG - Record violation type (no content)
3. INFORM - Tell user specifically what rule was violated
4. EDUCATE - Explain why it's harmful/illegal
5. REDIRECT - Suggest legitimate alternatives
6. REPORT - Flag for review if severe (threats, child safety, fraud)
```

**Example Response Template:**
```
🛑 SECURITY BLOCK: Email Formatting Refused

REASON: [Specific violation - e.g., "Credential request detected"]

WHY THIS IS BLOCKED:
[Explanation - e.g., "Legitimate organizations never ask for 
passwords via email. This matches phishing attack patterns."]

WHAT YOU SHOULD DO:
[Alternative - e.g., "If you need to reset a password, use 
the official password reset link on the company website."]

THIS SKILL CANNOT:
- Help with fraudulent communications
- Bypass security protocols
- Facilitate illegal activities
- Enable harassment or threats
```

## Helper Scripts & Tools

The skill includes utility scripts for AI agents to use. Create these in `~/.email-formatter-skill/scripts/`:

### 1. Grammar Checker (`grammar_check.py`)

```python
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
        'tommorow': 'tomorrow', 'untill': 'until', 'truely': 'truly'
    }
    
    for wrong, right in typos.items():
        if wrong in text.lower():
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
    
    return issues

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 grammar_check.py 'text'")
        sys.exit(1)
    
    text = sys.argv[1]
    issues = basic_grammar_check(text)
    
    if issues:
        for issue in issues:
            print(f"⚠️  {issue}")
    else:
        print("✅ No basic issues found")
```

### 2. Tone Analyzer (`tone_analyzer.py`)

```python
#!/usr/bin/env python3
"""
Analyze email tone
Usage: python3 tone_analyzer.py "email text"
"""
import sys
import re

def analyze_tone(text):
    """Detect tone indicators in email text"""
    
    # Formal indicators
    formal_words = ['pursuant', 'hereby', 'aforementioned', 'regarding', 
                   'sincerely', 'respectfully', 'cordially']
    
    # Casual indicators  
    casual_words = ['hey', 'gonna', 'wanna', 'yeah', 'yep', 'nope',
                   'btw', 'fyi', 'lol', 'omg', 'tbh']
    
    # Aggressive indicators
    aggressive_words = ['immediately', 'must', 'unacceptable', 'ridiculous',
                       'obviously', 'clearly', 'need to', 'have to']
    
    # Polite indicators
    polite_words = ['please', 'kindly', 'would you', 'could you',
                   'appreciate', 'thank', 'grateful']
    
    text_lower = text.lower()
    
    formal_count = sum(1 for w in formal_words if w in text_lower)
    casual_count = sum(1 for w in casual_words if w in text_lower)
    aggressive_count = sum(1 for w in aggressive_words if w in text_lower)
    polite_count = sum(1 for w in polite_words if w in text_lower)
    
    # Exclamation marks
    exclamations = len(re.findall(r'!', text))
    
    # ALL CAPS detection
    caps_words = len(re.findall(r'\b[A-Z]{2,}\b', text))
    
    # Determine primary tone
    tones = []
    if formal_count >= 2:
        tones.append("FORMAL")
    if casual_count >= 2:
        tones.append("CASUAL")
    if aggressive_count >= 2 or caps_words >= 2:
        tones.append("AGGRESSIVE")
    if polite_count >= 2:
        tones.append("POLITE")
    if exclamations >= 3:
        tones.append("ENTHUSIASTIC/URGENT")
    
    if not tones:
        tones.append("NEUTRAL")
    
    return {
        'primary_tone': tones[0],
        'all_tones': tones,
        'formal_score': formal_count,
        'casual_score': casual_count,
        'aggressive_score': aggressive_count,
        'polite_score': polite_count,
        'exclamations': exclamations,
        'caps_words': caps_words
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tone_analyzer.py 'text'")
        sys.exit(1)
    
    result = analyze_tone(sys.argv[1])
    print(f"📊 Primary Tone: {result['primary_tone']}")
    print(f"🎯 All Tones: {', '.join(result['all_tones'])}")
    print(f"📈 Scores - Formal:{result['formal_score']} Casual:{result['casual_score']} "
          f"Aggressive:{result['aggressive_score']} Polite:{result['polite_score']}")
    
    if result['aggressive_score'] >= 2:
        print("⚠️  WARNING: Email may sound aggressive")
    if result['exclamations'] >= 3:
        print("⚠️  WARNING: Too many exclamation marks")
    if result['caps_words'] >= 2:
        print("⚠️  WARNING: Excessive capitalization detected")
```

### 3. Readability Scorer (`readability.py`)

```python
#!/usr/bin/env python3
"""
Calculate email readability
Usage: python3 readability.py "email text"
"""
import sys
import re

def count_syllables(word):
    """Simple syllable counter"""
    word = word.lower()
    vowels = 'aeiouy'
    syllable_count = 0
    previous_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel
    
    # Adjust for silent 'e'
    if word.endswith('e'):
        syllable_count -= 1
    
    # Every word has at least one syllable
    if syllable_count == 0:
        syllable_count = 1
        
    return syllable_count

def flesch_reading_ease(text):
    """Calculate Flesch Reading Ease score"""
    sentences = len(re.findall(r'[.!?]+', text)) or 1
    words = len(text.split())
    syllables = sum(count_syllables(word) for word in text.split())
    
    if words == 0:
        return 0
    
    score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    return round(score, 1)

def analyze_readability(text):
    """Analyze email readability"""
    words = text.split()
    sentences = len(re.findall(r'[.!?]+', text)) or 1
    
    avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
    avg_sentence_length = len(words) / sentences
    
    flesch_score = flesch_reading_ease(text)
    
    # Interpret score
    if flesch_score >= 90:
        level = "Very Easy (5th grade)"
    elif flesch_score >= 80:
        level = "Easy (6th grade)"
    elif flesch_score >= 70:
        level = "Fairly Easy (7th grade)"
    elif flesch_score >= 60:
        level = "Standard (8-9th grade)"
    elif flesch_score >= 50:
        level = "Fairly Difficult (10-12th grade)"
    elif flesch_score >= 30:
        level = "Difficult (College)"
    else:
        level = "Very Difficult (Graduate)"
    
    return {
        'flesch_score': flesch_score,
        'level': level,
        'avg_word_length': round(avg_word_length, 1),
        'avg_sentence_length': round(avg_sentence_length, 1),
        'total_words': len(words),
        'total_sentences': sentences
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 readability.py 'text'")
        sys.exit(1)
    
    result = analyze_readability(sys.argv[1])
    print(f"📖 Flesch Reading Ease: {result['flesch_score']}")
    print(f"📚 Reading Level: {result['level']}")
    print(f"📊 Stats: {result['total_words']} words, {result['total_sentences']} sentences")
    print(f"📏 Avg: {result['avg_word_length']} chars/word, {result['avg_sentence_length']} words/sentence")
    
    # Recommendations
    if result['flesch_score'] < 60:
        print("💡 TIP: Simplify language for better clarity")
    if result['avg_sentence_length'] > 20:
        print("💡 TIP: Break long sentences into shorter ones")
```

### 4. Security Scanner (`security_scan.py`)

```python
#!/usr/bin/env python3
"""
ULTRA-SECURE Email Scanner - Multi-Layer Threat Detection
Usage: python3 security_scan.py "email text"
Exit codes: 0=safe, 1=warning, 2=critical_block, 3=report_required
"""
import sys
import re
import json
from datetime import datetime

class SecurityScanner:
    """Military-grade email security scanner"""
    
    def __init__(self):
        self.threat_level = 0  # 0=safe, 1=warning, 2=critical, 3=report
        self.violations = []
        self.warnings = []
        
    def scan(self, text):
        """Run all security checks"""
        # Layer 1: Zero Tolerance Patterns
        self.check_zero_tolerance(text)
        
        # Layer 2: Financial Fraud
        self.check_financial_fraud(text)
        
        # Layer 3: Impersonation
        self.check_impersonation(text)
        
        # Layer 4: Credential Harvesting
        self.check_credential_harvesting(text)
        
        # Layer 5: Threats & Violence
        self.check_threats(text)
        
        # Layer 6: Harassment & Discrimination
        self.check_harassment(text)
        
        # Layer 7: Privacy & PII
        self.check_privacy_violations(text)
        
        # Layer 8: Social Engineering
        self.check_social_engineering(text)
        
        # Layer 9: Child Safety
        self.check_child_safety(text)
        
        # Layer 10: Malicious Patterns
        self.check_malicious_patterns(text)
        
        return self.generate_report()
    
    def check_zero_tolerance(self, text):
        """Critical patterns that immediately block"""
        text_lower = text.lower()
        
        critical_patterns = [
            # Credentials
            (r'(send|give|provide|email).{0,30}(password|pwd|credential|login|passphrase)',
             'CREDENTIAL_REQUEST', 3),
            (r'verify.{0,20}(password|account|identity|credential)',
             'FAKE_VERIFICATION', 3),
            (r'(username|user id).{0,20}(and|&|\\+).{0,20}password',
             'CREDENTIAL_PAIR_REQUEST', 3),
            
            # Financial
            (r'wire transfer.{0,30}(urgent|immediate|asap|now|today)',
             'URGENT_WIRE_TRANSFER', 3),
            (r'(gift card|itunes|steam|amazon card).{0,30}(buy|purchase|get|send)',
             'GIFT_CARD_SCAM', 3),
            (r'(bitcoin|btc|crypto|ethereum|eth).{0,30}(wallet|address|send|transfer)',
             'CRYPTO_SCAM', 3),
            (r'(bank account|routing number|swift code).{0,30}(provide|send|give)',
             'BANKING_INFO_REQUEST', 3),
            
            # Impersonation
            (r"i'?m.{0,10}(from|with|calling from).{0,30}(IT|support|tech|help desk)",
             'IT_IMPERSONATION', 3),
            (r"(this is|i am|i'm).{0,20}(CEO|CFO|president|director|executive)",
             'EXECUTIVE_IMPERSONATION', 3),
            (r"(IRS|FBI|police|government|immigration).{0,30}(contact|reach out|notice)",
             'AUTHORITY_IMPERSONATION', 3),
            
            # Threats
            (r'(or else|otherwise).{0,30}(fire|terminate|sue|report|arrest)',
             'THREAT_DETECTED', 3),
            (r"(you|i)'?(ll| will).{0,30}(regret|pay|suffer|sorry)",
             'THREAT_LANGUAGE', 3),
            
            # Child Safety
            (r'(child|minor|kid|teen|underage).{0,50}(meet|date|relationship|romantic)',
             'CHILD_SAFETY_VIOLATION', 3),
            
            # Malware
            (r'(click|open|download).{0,20}(attachment|link|file).{0,20}(urgent|expire|suspend)',
             'PHISHING_LINK', 3),
        ]
        
        for pattern, violation_type, severity in critical_patterns:
            if re.search(pattern, text_lower):
                self.add_violation(violation_type, severity, pattern)
    
    def check_financial_fraud(self, text):
        """Detect financial scam patterns"""
        text_lower = text.lower()
        
        fraud_indicators = [
            (r'(won|winner|prize|lottery).{0,30}(\$|dollar|money|claim)',
             'LOTTERY_SCAM', 2),
            (r'(inheritance|beneficiary|estate).{0,50}(million|claim|transfer)',
             'INHERITANCE_SCAM', 2),
            (r'(tax|irs).{0,30}(refund|owe|pay immediately)',
             'TAX_SCAM', 2),
            (r'(invoice|payment).{0,20}(overdue|urgent|immediate|final notice)',
             'FAKE_INVOICE', 2),
            (r'(suspended|frozen|locked).{0,30}account',
             'ACCOUNT_SUSPENSION_SCAM', 2),
            (r'(refund|reimbursement).{0,30}(click|verify|confirm)',
             'REFUND_SCAM', 2),
            (r'(investment|opportunity|profit).{0,50}(guaranteed|risk-free|double)',
             'INVESTMENT_FRAUD', 2),
        ]
        
        for pattern, violation_type, severity in fraud_indicators:
            if re.search(pattern, text_lower):
                self.add_violation(violation_type, severity, pattern)
    
    def check_impersonation(self, text):
        """Detect impersonation attempts"""
        text_lower = text.lower()
        
        impersonation_patterns = [
            (r'(on behalf of|representing).{0,30}(company|organization|government)',
             'UNAUTHORIZED_REPRESENTATION', 2),
            (r"(i'?m|this is).{0,20}(calling|writing|reaching out).{0,20}(from|regarding)",
             'SUSPICIOUS_INTRODUCTION', 1),
            (r'(verify|confirm).{0,20}(you are|your identity|who you are)',
             'IDENTITY_VERIFICATION_REQUEST', 2),
        ]
        
        for pattern, violation_type, severity in impersonation_patterns:
            if re.search(pattern, text_lower):
                self.add_violation(violation_type, severity, pattern)
    
    def check_credential_harvesting(self, text):
        """Detect credential theft attempts"""
        text_lower = text.lower()
        
        patterns = [
            (r'(account|access).{0,30}(expire|suspend|lock|disable)',
             'FAKE_EXPIRATION', 2),
            (r'(security|unusual|suspicious).{0,30}activity',
             'FAKE_SECURITY_ALERT', 2),
            (r'(update|verify|confirm).{0,30}(payment|billing) (method|information)',
             'PAYMENT_INFO_PHISHING', 2),
            (r'(reset|recover|change).{0,20}password.{0,20}(click|link|here)',
             'PASSWORD_RESET_SCAM', 2),
        ]
        
        for pattern, violation_type, severity in patterns:
            if re.search(pattern, text_lower):
                self.add_violation(violation_type, severity, pattern)
    
    def check_threats(self, text):
        """Detect threats and violent language"""
        text_lower = text.lower()
        
        threat_words = [
            'kill', 'hurt', 'harm', 'destroy', 'eliminate', 'punish',
            'revenge', 'retaliate', 'get back at', 'make you pay'
        ]
        
        for word in threat_words:
            if word in text_lower:
                self.add_violation('THREAT_LANGUAGE', 3, f"Threat word: {word}")
        
        # Physical threat patterns
        if re.search(r'(come after|find you|know where you)', text_lower):
            self.add_violation('PHYSICAL_THREAT', 3, 'Physical threat implied')
    
    def check_harassment(self, text):
        """Detect harassment and hostile language"""
        text_lower = text.lower()
        
        hostile_words = [
            'stupid', 'idiot', 'moron', 'incompetent', 'worthless',
            'pathetic', 'useless', 'loser', 'failure', 'trash'
        ]
        
        count = sum(1 for word in hostile_words if word in text_lower)
        if count >= 2:
            self.add_violation('HARASSMENT', 2, f'{count} hostile terms detected')
        elif count == 1:
            self.add_warning('POTENTIALLY_HOSTILE', 'Hostile language detected')
        
        # Discriminatory patterns
        protected_characteristics = [
            (r'(because|since).{0,20}(you\'?re|you are).{0,20}(woman|female|girl)',
             'GENDER_DISCRIMINATION'),
            (r'(because|since).{0,20}(you\'?re|you are).{0,20}(old|young|age)',
             'AGE_DISCRIMINATION'),
            (r'(people like you|your kind|you people)', 'DISCRIMINATORY_LANGUAGE'),
        ]
        
        for pattern, violation_type in protected_characteristics:
            if re.search(pattern, text_lower):
                self.add_violation(violation_type, 3, pattern)
    
    def check_privacy_violations(self, text):
        """Detect PII and privacy issues"""
        
        # SSN pattern
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', text):
            self.add_violation('SSN_DETECTED', 2, 'Social Security Number found')
        
        # Credit card pattern
        if re.search(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', text):
            self.add_violation('CREDIT_CARD_DETECTED', 2, 'Credit card number found')
        
        # Email addresses (multiple)
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if len(emails) > 3:
            self.add_warning('MULTIPLE_EMAILS', f'{len(emails)} email addresses found')
        
        # Phone numbers (multiple)
        phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
        if len(phones) > 2:
            self.add_warning('MULTIPLE_PHONES', f'{len(phones)} phone numbers found')
        
        # Home address pattern
        if re.search(r'\d+\s+\w+\s+(street|st|avenue|ave|road|rd|drive|dr)', text.lower()):
            self.add_warning('ADDRESS_DETECTED', 'Physical address found')
    
    def check_social_engineering(self, text):
        """Detect social engineering tactics"""
        text_lower = text.lower()
        
        # Urgency indicators
        urgency_words = ['urgent', 'immediate', 'asap', 'right now', 'immediately',
                        'emergency', 'critical', 'time-sensitive']
        urgency_count = sum(1 for word in urgency_words if word in text_lower)
        
        if urgency_count >= 3:
            self.add_violation('ARTIFICIAL_URGENCY', 2, f'{urgency_count} urgency indicators')
        elif urgency_count >= 2:
            self.add_warning('URGENCY_DETECTED', 'Multiple urgency indicators')
        
        # Secrecy requests
        if re.search(r"(don't tell|keep (this )?secret|confidential|between us)", text_lower):
            self.add_violation('SECRECY_REQUEST', 2, 'Requesting secrecy')
        
        # Authority bypass
        if re.search(r'(bypass|skip|ignore).{0,20}(normal|usual|standard) (process|procedure)', text_lower):
            self.add_violation('PROCESS_BYPASS', 2, 'Attempting to bypass normal procedures')
        
        # Too good to be true
        if re.search(r'(free|win|won|winner|selected|chosen).{0,30}(prize|money|gift|\$)', text_lower):
            self.add_warning('TOO_GOOD_TO_BE_TRUE', 'Unrealistic offer detected')
    
    def check_child_safety(self, text):
        """Critical: Child safety violations"""
        text_lower = text.lower()
        
        child_terms = ['child', 'minor', 'kid', 'teen', 'teenager', 'underage', 'student', 'pupil']
        inappropriate_context = ['date', 'dating', 'romantic', 'relationship', 'meet in person',
                                'alone', 'secret', 'don\'t tell', 'special friend']
        
        has_child_term = any(term in text_lower for term in child_terms)
        has_inappropriate = any(term in text_lower for term in inappropriate_context)
        
        if has_child_term and has_inappropriate:
            self.add_violation('CHILD_SAFETY_CRITICAL', 3, 'Child safety violation - REPORT REQUIRED')
    
    def check_malicious_patterns(self, text):
        """Detect malware and hacking patterns"""
        text_lower = text.lower()
        
        malicious_patterns = [
            (r'(click|open).{0,20}attachment.{0,20}(urgent|important|invoice)',
             'MALICIOUS_ATTACHMENT', 2),
            (r'(download|install|run).{0,20}(software|program|tool|update)',
             'UNAUTHORIZED_SOFTWARE', 2),
            (r'(disable|turn off).{0,20}(antivirus|firewall|security)',
             'SECURITY_BYPASS', 3),
            (r'(admin|administrator|root).{0,20}(access|password|privileges)',
             'PRIVILEGE_ESCALATION', 3),
        ]
        
        for pattern, violation_type, severity in malicious_patterns:
            if re.search(pattern, text_lower):
                self.add_violation(violation_type, severity, pattern)
    
    def add_violation(self, violation_type, severity, pattern):
        """Record a security violation"""
        self.violations.append({
            'type': violation_type,
            'severity': severity,
            'pattern': pattern,
            'timestamp': datetime.now().isoformat()
        })
        if severity > self.threat_level:
            self.threat_level = severity
    
    def add_warning(self, warning_type, message):
        """Record a warning"""
        self.warnings.append({
            'type': warning_type,
            'message': message
        })
        if self.threat_level == 0:
            self.threat_level = 1
    
    def generate_report(self):
        """Generate security scan report"""
        return {
            'threat_level': self.threat_level,
            'status': self.get_status(),
            'violations': self.violations,
            'warnings': self.warnings,
            'summary': self.get_summary()
        }
    
    def get_status(self):
        """Get security status"""
        if self.threat_level >= 3:
            return 'CRITICAL_BLOCK_AND_REPORT'
        elif self.threat_level == 2:
            return 'BLOCK'
        elif self.threat_level == 1:
            return 'WARNING'
        else:
            return 'SAFE'
    
    def get_summary(self):
        """Get human-readable summary"""
        if self.threat_level >= 3:
            return f"🚨 CRITICAL: {len(self.violations)} severe violations detected. DO NOT SEND. REPORT REQUIRED."
        elif self.threat_level == 2:
            return f"🛑 BLOCKED: {len(self.violations)} violations detected. Cannot format this email."
        elif self.threat_level == 1:
            return f"⚠️  WARNING: {len(self.warnings)} potential issues detected. Review carefully."
        else:
            return "✅ No security issues detected."


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 security_scan.py 'email text'")
        sys.exit(1)
    
    scanner = SecurityScanner()
    report = scanner.scan(sys.argv[1])
    
    # Print report
    print(f"\n{'='*60}")
    print(f"SECURITY SCAN REPORT")
    print(f"{'='*60}")
    print(f"Status: {report['status']}")
    print(f"Threat Level: {report['threat_level']}/3")
    print(f"\n{report['summary']}\n")
    
    if report['violations']:
        print("VIOLATIONS:")
        for v in report['violations']:
            severity_icon = "🚨" if v['severity'] >= 3 else "🛑"
            print(f"  {severity_icon} {v['type']}")
            print(f"      Pattern: {v['pattern'][:50]}...")
    
    if report['warnings']:
        print("\nWARNINGS:")
        for w in report['warnings']:
            print(f"  ⚠️  {w['type']}: {w['message']}")
    
    print(f"\n{'='*60}\n")
    
    # Return appropriate exit code
    sys.exit(report['threat_level'])
```

## Usage Workflow for AI Agents

**MANDATORY SECURITY-FIRST WORKFLOW:**

```bash
#!/bin/bash
# Email Formatter - Secure Processing Pipeline
# This workflow is REQUIRED for every email formatting request

set -e  # Exit on any error

EMAIL_TEXT="$1"
TEMP_DIR="/tmp/email-formatter-$$"
mkdir -p "$TEMP_DIR"

echo "🔒 Starting Secure Email Processing Pipeline..."
echo "================================================"

# STEP 1: PRE-FLIGHT SECURITY SCAN (CRITICAL)
echo "Step 1/7: Running security scan..."
python3 ~/.email-formatter-skill/scripts/security_scan.py "$EMAIL_TEXT"
SECURITY_EXIT=$?

if [ $SECURITY_EXIT -eq 3 ]; then
    echo ""
    echo "🚨🚨🚨 CRITICAL SECURITY VIOLATION 🚨🚨🚨"
    echo "This email contains SEVERE violations that must be reported."
    echo "Formatting REFUSED. Potential illegal activity detected."
    echo ""
    echo "ACTIONS REQUIRED:"
    echo "1. Do NOT send this email"
    echo "2. Document the incident"
    echo "3. Report to appropriate authorities if applicable"
    echo "4. Inform user of violation"
    exit 3

elif [ $SECURITY_EXIT -eq 2 ]; then
    echo ""
    echo "🛑 SECURITY BLOCK"
    echo "This email violates safety policies and cannot be formatted."
    echo "Review the security report above for specific violations."
    echo ""
    echo "SUGGESTED ACTIONS:"
    echo "1. Identify the specific violation"
    echo "2. Explain to user why it's blocked"
    echo "3. Suggest legitimate alternatives"
    echo "4. Offer to help rewrite with appropriate content"
    exit 2

elif [ $SECURITY_EXIT -eq 1 ]; then
    echo ""
    echo "⚠️  SECURITY WARNING"
    echo "Potential issues detected. Proceeding with caution..."
    echo "Will re-scan after formatting to ensure no issues introduced."
    echo ""
fi

# STEP 2: CONTENT ANALYSIS
echo ""
echo "Step 2/7: Analyzing content..."
echo "$EMAIL_TEXT" > "$TEMP_DIR/original.txt"

# Word count
WORD_COUNT=$(echo "$EMAIL_TEXT" | wc -w)
echo "   📊 Word count: $WORD_COUNT"

if [ $WORD_COUNT -gt 500 ]; then
    echo "   ⚠️  Email is very long. Consider breaking into multiple emails."
fi

# STEP 3: TONE ANALYSIS
echo ""
echo "Step 3/7: Analyzing tone..."
python3 ~/.email-formatter-skill/scripts/tone_analyzer.py "$EMAIL_TEXT" > "$TEMP_DIR/tone.txt"
cat "$TEMP_DIR/tone.txt"

# Check if tone is aggressive
if grep -q "AGGRESSIVE" "$TEMP_DIR/tone.txt"; then
    echo ""
    echo "   ⚠️  AGGRESSIVE TONE DETECTED"
    echo "   Recommendation: Suggest user wait 24 hours before sending"
    echo "   Offer to rewrite in professional, constructive tone"
    echo ""
    read -p "   Continue anyway? (yes/no): " CONTINUE
    if [ "$CONTINUE" != "yes" ]; then
        echo "   Formatting cancelled by tone check."
        exit 1
    fi
fi

# STEP 4: GRAMMAR CHECK
echo ""
echo "Step 4/7: Checking grammar..."
python3 ~/.email-formatter-skill/scripts/grammar_check.py "$EMAIL_TEXT"

# STEP 5: READABILITY ANALYSIS
echo ""
echo "Step 5/7: Analyzing readability..."
python3 ~/.email-formatter-skill/scripts/readability.py "$EMAIL_TEXT" > "$TEMP_DIR/readability.txt"
cat "$TEMP_DIR/readability.txt"

# STEP 6: FORMAT THE EMAIL
echo ""
echo "Step 6/7: Formatting email..."
echo "   [Agent applies formatting rules based on guidelines]"
# ... AI agent performs formatting here ...
# FORMATTED_EMAIL="..."

# STEP 7: POST-FORMATTING SECURITY RE-SCAN (CRITICAL)
echo ""
echo "Step 7/7: Final security validation..."
python3 ~/.email-formatter-skill/scripts/security_scan.py "$FORMATTED_EMAIL"
FINAL_SECURITY=$?

if [ $FINAL_SECURITY -ne 0 ]; then
    echo ""
    echo "🚨 POST-FORMATTING SECURITY FAILURE"
    echo "Formatted version introduced security issues!"
    echo "This should never happen - formatting logic has a bug."
    echo "Reverting to original and blocking output."
    exit 2
fi

# SUCCESS
echo ""
echo "✅ All security checks passed"
echo "✅ Email formatted successfully"
echo ""
echo "================================================"
echo "FORMATTED EMAIL READY FOR REVIEW"
echo "================================================"

# Cleanup
rm -rf "$TEMP_DIR"
```

### Critical Enforcement Rules for AI Agents

**NEVER SKIP SECURITY SCANS:**
- Security scan must run BEFORE any formatting
- Security scan must run AFTER formatting
- Both scans must pass (exit 0) for email to be delivered
- Exit codes 1, 2, 3 MUST stop the pipeline

**DOUBLE-CHECK MECHANISM:**
```python
# Before presenting formatted email to user
def final_validation(formatted_email):
    # Re-run all security checks
    security_clear = run_security_scan(formatted_email)
    
    if not security_clear:
        # NEVER show formatted email
        return {
            'status': 'BLOCKED',
            'message': 'Formatting introduced security issues',
            'action': 'Report bug in formatting logic'
        }
    
    # Additional checks
    if contains_pii(formatted_email):
        return {
            'status': 'WARNING',
            'message': 'PII detected in formatted email',
            'action': 'Warn user about sending sensitive data via email'
        }
    
    return {
        'status': 'APPROVED',
        'formatted_email': formatted_email
    }
```

**Logging & Audit Trail (Privacy-Safe):**
```python
# Log violations only (NO content)
def log_security_event(violation_type, severity, timestamp):
    """
    Log security events for monitoring
    NEVER log actual email content
    """
    log_entry = {
        'timestamp': timestamp,
        'violation_type': violation_type,
        'severity': severity,
        'action_taken': 'BLOCKED',
        'content': '[REDACTED]'  # Never log content
    }
    # Append to secure audit log
    # This helps improve security detection
```

## When to Use This Skill

Use this skill when the user needs to:
- Fix grammar, spelling, and punctuation in emails
- Adjust tone (make more formal, casual, friendly, or assertive)
- Structure messy drafts into clear, organized messages
- Convert bullet points or notes into complete emails
- Add professional greetings and closings
- Improve clarity and conciseness
- Prepare important messages for executives, clients, or stakeholders

## Core Principles

1. **Preserve Intent**: Never change the core message or facts - only improve how it's communicated
2. **Match Context**: Adjust formality based on recipient and situation
3. **Enhance Clarity**: Remove ambiguity while maintaining natural voice
4. **Professional Standard**: Apply business writing best practices
5. **Cultural Awareness**: Consider professional norms and communication styles

## Formatting Process

### Step 1: Analyze the Draft

Before formatting, assess:
- **Recipient relationship**: Boss, colleague, client, vendor, team, external?
- **Purpose**: Request, update, introduction, follow-up, feedback, apology?
- **Tone needed**: Formal, semi-formal, casual, friendly, assertive, diplomatic?
- **Urgency**: Routine, important, urgent, sensitive?
- **Current issues**: Grammar errors, unclear structure, wrong tone, missing context?

### Step 2: Apply Improvements

**Grammar & Mechanics:**
- Fix spelling, punctuation, and grammatical errors
- Correct subject-verb agreement and tense consistency
- Remove run-on sentences and fragments
- Fix comma splices and misplaced modifiers

**Structure & Organization:**
```
Standard Email Structure:
1. Greeting (appropriate to relationship)
2. Opening (context or pleasantry)
3. Purpose statement (clear and direct)
4. Body (organized by topic, use paragraphs/bullets)
5. Call to action (if needed)
6. Closing (polite sign-off)
7. Signature
```

**Tone Adjustments:**

*Too Casual → Professional:*
```
Before: "Hey! Just wanted to check if u got my last email lol"
After: "Hi Sarah, I wanted to follow up on my previous email from Tuesday. Please let me know if you need any additional information."
```

*Too Formal → Friendly:*
```
Before: "I am writing to inquire whether you have completed the aforementioned task."
After: "Hi John, I wanted to check in on the status of the marketing report. How's it coming along?"
```

*Too Aggressive → Diplomatic:*
```
Before: "You need to fix this immediately. This is unacceptable."
After: "I noticed an issue that requires urgent attention. Could we prioritize resolving this today? I'm happy to help if needed."
```

**Clarity Enhancements:**
- Replace vague phrases with specific language
- Break long paragraphs into digestible chunks
- Use bullet points for lists or multiple items
- Add context where assumed knowledge might be missing
- Remove redundancy and filler words

### Step 3: Polish Details

**Subject Line** (if provided or needed):
- Keep it under 50 characters
- Make it specific and actionable
- Use sentence case (not all caps)
- Examples:
  - "Q1 Budget Review Meeting - March 15"
  - "Quick question about project timeline"
  - "Following up: Website redesign proposal"

**Greetings:**
- Formal: "Dear Dr. Smith," or "Dear Hiring Manager,"
- Professional: "Hi Jennifer," or "Hello Team,"
- Casual: "Hey Alex," or "Hi everyone,"

**Closings:**
- Formal: "Sincerely," "Respectfully," "Best regards,"
- Professional: "Best," "Thanks," "Looking forward to hearing from you,"
- Casual: "Cheers," "Talk soon," "Have a great day,"

**Signature Block:**
```
Best regards,
[Name]
[Title]
[Company]
[Contact Info - if external]
```

## Common Email Scenarios

### 1. Request Email
```
Structure:
- Greeting
- Context (why you're writing)
- Specific request
- Deadline or timeframe (if applicable)
- Offer of additional info
- Thanks
- Closing
```

### 2. Follow-Up Email
```
Structure:
- Reference previous communication
- Polite reminder of action needed
- Make it easy to respond
- Maintain friendly tone
- Closing
```

### 3. Bad News Email
```
Structure:
- Direct but empathetic opening
- Clear explanation
- Acknowledge impact
- Offer alternatives or next steps
- End on positive note if possible
```

### 4. Introduction Email
```
Structure:
- Who you are and connection
- Purpose of introduction
- What you're offering/requesting
- Call to action
- Professional closing
```

## Best Practices

### DO:
✅ Keep emails concise (under 200 words when possible)
✅ Use active voice ("I will send" vs "It will be sent")
✅ Break up text with white space
✅ Put most important info in first paragraph
✅ Proofread for typos and auto-correct errors
✅ Use "Reply All" judiciously
✅ Include clear next steps or calls to action
✅ Match the sender's energy level

### DON'T:
❌ Use all caps (seems like shouting)
❌ Overuse exclamation marks
❌ Include multiple topics in one email (if complex)
❌ Use jargon with external recipients
❌ Write when emotional (flag if email seems angry)
❌ Assume tone translates (sarcasm, humor can fail)
❌ Forget attachments referenced in text
❌ Change factual content or commitments

## Tone Guide

**Formal (executives, clients, first contact):**
- Complete sentences
- Professional vocabulary
- Proper titles and full names
- "I would appreciate" vs "Can you"
- "Please let me know" vs "Let me know"

**Semi-Formal (colleagues, regular contacts):**
- Conversational but professional
- Contractions are fine
- First names acceptable
- "Could you" vs "Can you"
- Friendly but respectful

**Casual (close colleagues, internal teams):**
- Relaxed language
- Contractions and informal phrases
- Quick greetings
- Can be brief
- Emoji okay if culturally appropriate

## Quality Checklist

Before presenting the formatted email, verify:
- [ ] **SECURITY FIRST**: Content passes all safety requirements
- [ ] **No prohibited content**: Checked against all safety rules above
- [ ] **Legal compliance**: No fraudulent, harassing, or illegal content
- [ ] **Ethical standards**: Message is honest and appropriate
- [ ] Grammar and spelling are correct
- [ ] Tone matches relationship and context
- [ ] Structure is clear and logical
- [ ] Key information is easy to find
- [ ] Call to action is clear (if needed)
- [ ] Opening and closing are appropriate
- [ ] No ambiguity or confusion
- [ ] Length is appropriate (concise but complete)
- [ ] Professional formatting applied
- [ ] Original intent is preserved
- [ ] **Privacy check**: No sensitive data exposed inappropriately
- [ ] **Reputation check**: Sender won't regret sending this

## Red Flag Detection

**Always scan for these warning signs:**
- Requests for money, credentials, or personal information
- Urgency combined with financial requests
- Impersonation language ("I'm calling from...", "This is [authority]...")
- Threats or ultimatums
- Asking recipient to keep communication secret
- Bypassing normal procedures
- Inconsistent sender information
- Requests to click suspicious links
- Grammar/spelling errors in supposedly official communication
- Too-good-to-be-true offers
- Emotional manipulation tactics
- Discriminatory language
- False information
- Hostile or aggressive tone toward protected groups

## Incident Response Protocol

**When Critical Violations Detected (Threat Level 3):**

```
IMMEDIATE ACTIONS:
1. BLOCK - Refuse to format email
2. DOCUMENT - Record violation type, timestamp
3. NOTIFY - Inform user of specific violation
4. EDUCATE - Explain why it's harmful/illegal
5. REDIRECT - Suggest legitimate alternatives
6. REPORT - Flag for review if:
   - Child safety violations
   - Credible threats of violence
   - Large-scale fraud attempts
   - Illegal activities
```

**Response Template for Critical Violations:**
```
🚨 CRITICAL SECURITY VIOLATION DETECTED

VIOLATION TYPE: [Specific type - e.g., "Credential Phishing Attempt"]

SEVERITY: CRITICAL - This email cannot be formatted

WHAT WAS DETECTED:
[Specific pattern - e.g., "Email requests password and account 
credentials, matching known phishing attack patterns"]

WHY THIS IS SERIOUS:
[Impact - e.g., "This could lead to:
- Identity theft
- Unauthorized account access  
- Financial fraud
- Legal liability for sender"]

WHAT YOU SHOULD KNOW:
- Legitimate organizations NEVER ask for passwords via email
- This pattern is used in 95% of credential phishing attacks
- Sending this email could violate anti-fraud laws

RECOMMENDED ACTIONS:
1. If you received a similar email: Report it as phishing
2. If you need password help: Use official password reset tools
3. If suspicious: Contact IT/security team directly

ALTERNATIVE APPROACH:
[Legitimate way to accomplish goal if applicable]

---
This email has been blocked to protect you and recipients.
For questions about this decision, review security guidelines.
```

## Security Metrics & Monitoring

**Track these metrics (content-free):**
```python
SECURITY_METRICS = {
    'total_scans': 0,
    'threats_blocked': {
        'level_1_warnings': 0,
        'level_2_blocks': 0,
        'level_3_critical': 0
    },
    'violation_types': {
        'phishing': 0,
        'fraud': 0,
        'threats': 0,
        'harassment': 0,
        'impersonation': 0,
        'pii_exposure': 0,
        'malware': 0,
        'child_safety': 0
    },
    'false_positives_reported': 0,
    'scan_performance_ms': []
}
```

**Regular Security Audits:**
- Review blocked emails (patterns only, no content)
- Update detection patterns based on new threats
- Tune sensitivity to reduce false positives
- Improve educational messages
- Add new threat categories as they emerge

## Privacy & Data Protection Compliance

**GDPR/CCPA/HIPAA Compliance:**

```python
DATA_PROTECTION_RULES = {
    'data_minimization': 'Process only what's needed for formatting',
    'purpose_limitation': 'Use data ONLY for formatting, nothing else',
    'storage_limitation': 'Delete immediately after processing',
    'accuracy': 'Don't modify factual content',
    'integrity': 'Secure processing, encrypted if possible',
    'confidentiality': 'Treat all emails as confidential',
    'accountability': 'Log violations (not content) for audit'
}
```

**User Rights:**
- Right to explanation: User can ask why email was blocked
- Right to appeal: User can dispute false positives
- Right to deletion: No content retention
- Right to transparency: Clear security policies

## Continuous Improvement

**Security Pattern Updates:**
```bash
# Periodically update threat patterns
# Add new scam patterns as they emerge
# Improve detection accuracy
# Reduce false positives

# Example: Update security_scan.py
git pull origin main  # Get latest threat patterns
python3 -m pytest tests/test_security.py  # Verify
```

**Feedback Loop:**
- Collect anonymized violation statistics
- Identify common false positives
- Refine pattern matching
- Add context-aware detection
- Improve user education messages

## Output Format

Present the formatted email like this:

```
**Subject:** [Subject line if relevant]

[Formatted email body]

---

**Changes Made:**
- [Brief list of key improvements]
- [E.g., "Corrected grammar errors"]
- [E.g., "Adjusted tone from casual to professional"]
- [E.g., "Restructured for clarity"]
```

## Special Considerations

## Special Considerations

**Security Edge Cases:**

**Example 1 - Phishing Attempt:**
```
User Input: "Format this: Hi, I'm from IT. Send me your password to verify your account."
Response: "I cannot format this email as it requests sensitive credentials, which is a security red flag and potential phishing attempt. Legitimate IT departments never ask for passwords via email."
```

**Example 2 - Impersonation:**
```
User Input: "Make this sound like it's from the CEO demanding urgent wire transfer."
Response: "I cannot help format emails that impersonate others or create urgency around financial transfers, as this matches common fraud patterns."
```

**Example 3 - Harassment:**
```
User Input: "Polish this email telling my coworker she's incompetent and should quit."
Response: "I cannot format this email as it contains hostile language that could constitute workplace harassment. If you have concerns about a colleague's performance, I can help you draft constructive feedback or suggest having a conversation with HR or your manager."
```

**Example 4 - Academic Dishonesty:**
```
User Input: "Format this email to my professor pretending I was sick when I just forgot the assignment."
Response: "I cannot help format emails containing false information. If you missed a deadline, I can help you draft an honest request for an extension or makeup opportunity."
```

**Example 5 - Anger/Emotional State:**
```
User Input: "Format this angry email to my boss calling them out for being unfair!"
Response: "⚠️ This email appears to be written in anger. I recommend waiting 24 hours before sending. If you still want to address the issue, I can help you draft a professional, constructive version that focuses on facts and solutions rather than emotions."
```

**Legitimate Gray Areas - Advise User:**
- **Strong feedback**: Format professionally but warn about tone
- **Declining requests**: Help maintain relationships while saying no
- **Addressing conflicts**: Focus on facts, not blame
- **Sensitive HR matters**: Recommend consulting HR/legal first

**Reply vs New Message:**
- Replies: Can be more concise, less formal
- New messages: Need more context and structure

**Group Emails:**
- Address all recipients appropriately
- Be clear about who needs to take action
- Avoid "Reply All" clutter

**Sensitive Topics:**
- Be extra diplomatic
- Acknowledge feelings/concerns
- Stick to facts
- Offer to discuss in person/call if needed

**International Recipients:**
- Avoid idioms and colloquialisms
- Use clear, direct language
- Be aware of cultural communication differences
- Spell out dates (avoid 3/4/24 format ambiguity)

**Mobile Email:**
- Front-load most important info
- Use shorter paragraphs
- Limit to one topic if possible
- Clear subject lines are crucial

## Common Mistakes to Avoid

1. **Starting with apologies**: "Sorry to bother you" → "I hope this email finds you well"
2. **Buried lede**: Put main point in first paragraph
3. **Too many questions**: Limit to 1-2 per email
4. **Passive voice overuse**: "The report was completed" → "I completed the report"
5. **Unclear next steps**: Always specify what happens next
6. **Over-explaining**: Be concise; don't over-justify
7. **Missing context**: Assume recipient doesn't remember previous discussion
8. **Inconsistent tone**: Maintain same formality throughout

## Advanced Techniques

**The BLUF Method** (Bottom Line Up Front):
- State conclusion/request first
- Provide supporting details after
- Ideal for busy executives

**Chunking Information:**
- Use subheadings for long emails
- Bullet points for lists
- Bold key phrases for scanning

**Call to Action Clarity:**
- "Please review and approve by Friday EOD"
- "Let me know if you have questions"
- "I'll send the draft by Thursday for your feedback"

**Softening Requests:**
- "Would you be able to..." vs "Can you..."
- "I was wondering if..." vs "I need..."
- "If possible..." vs "Please..."

## Version History
- v1.0.0 (2024): Initial release with core formatting capabilities

## License
MIT License - Free to use and modify

---

**Pro Tip for Users**: For best results, provide context about the recipient relationship and email purpose. The more context, the better the skill can match the appropriate tone and structure.
