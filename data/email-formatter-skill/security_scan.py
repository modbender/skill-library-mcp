#!/usr/bin/env python3
"""
Scan email for security red flags
Usage: python3 security_scan.py "email text"
"""
import sys
import re

def scan_for_threats(text):
    """Detect security and safety issues"""
    
    red_flags = []
    text_lower = text.lower()
    
    # PHISHING INDICATORS
    phishing_patterns = [
        (r'verify (your|account|password|credentials|identity)', 'Credential verification request'),
        (r'confirm (your|account|password|identity|personal)', 'Identity confirmation request'),
        (r'update (your|payment|billing|account) (info|information|details)', 'Payment update request'),
        (r'click (here|this link|below) (immediately|now|urgent|asap)', 'Urgent link click request'),
        (r'suspend(ed)? (your )?account', 'Account suspension threat'),
        (r'unusual (activity|login) detected', 'Fake security alert'),
        (r'account (will be|has been) (closed|terminated|suspended)', 'Account termination threat'),
        (r'security (alert|warning|notification)', 'Fake security notification'),
        (r're-?activate your account', 'Account reactivation scam'),
        (r'claim your (prize|reward|refund)', 'Prize/reward scam'),
        (r'you\'?ve? won', 'Lottery/prize scam'),
        (r'urgent (action|response) required', 'False urgency'),
        (r'wire transfer (required|needed|urgent)', 'Wire transfer scam'),
        (r'send (money|payment|funds) (to|via)', 'Direct payment request'),
        (r'gift card|itunes card|steam card|prepaid card', 'Gift card scam'),
        (r'tax (refund|payment) pending', 'Tax scam'),
        (r'inheritance|beneficiary', 'Inheritance scam'),
        (r'nigerian prince', 'Classic 419 scam'),
    ]
    
    for pattern, description in phishing_patterns:
        if re.search(pattern, text_lower):
            red_flags.append(('CRITICAL', 'PHISHING', description))
    
    # SENSITIVE DATA REQUESTS
    sensitive_patterns = [
        (r'\b(password|passcode|pin)\b', 'Password request'),
        (r'\b(ssn|social security)\b', 'SSN request'),
        (r'\bcredit card\b', 'Credit card request'),
        (r'\bbank account\b', 'Bank account request'),
        (r'\brouting number\b', 'Routing number request'),
        (r'\bdate of birth\b', 'Date of birth request'),
        (r'\bdriver\'?s? license\b', 'Driver license request'),
        (r'\bpassport (number|info)', 'Passport info request'),
    ]
    
    for pattern, description in sensitive_patterns:
        if re.search(pattern, text_lower):
            red_flags.append(('CRITICAL', 'SENSITIVE_DATA', description))
    
    # Check for actual sensitive data (possible leak)
    data_patterns = [
        (r'\b\d{3}-\d{2}-\d{4}\b', 'Possible SSN detected in email'),
        (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', 'Possible credit card number'),
        (r'\b[A-Z]{2}\d{6,7}\b', 'Possible passport number'),
    ]
    
    for pattern, description in data_patterns:
        if re.search(pattern, text):
            red_flags.append(('CRITICAL', 'DATA_LEAK', description))
    
    # HARASSMENT AND HOSTILE LANGUAGE
    harassment_words = [
        'incompetent', 'stupid', 'idiot', 'moron', 'imbecile',
        'useless', 'pathetic', 'worthless', 'loser', 'failure',
        'disgusting', 'repulsive', 'garbage', 'trash', 'waste',
    ]
    
    harassment_count = sum(1 for word in harassment_words if word in text_lower)
    if harassment_count >= 2:
        red_flags.append(('HIGH', 'HARASSMENT', f'Multiple hostile/derogatory terms ({harassment_count} found)'))
    elif harassment_count == 1:
        red_flags.append(('MEDIUM', 'HOSTILE_LANGUAGE', 'Potentially offensive language detected'))
    
    # THREATS
    threat_patterns = [
        (r'(you will|you better|you must) .{0,20}(or else|or i will)', 'Conditional threat'),
        (r'i will make sure you', 'Retaliatory threat'),
        (r'you\'?re? (going to|gonna) regret', 'Intimidation'),
        (r'i\'?ll? ruin your', 'Threat of harm'),
        (r'watch your back', 'Veiled threat'),
        (r'you\'?ll? pay for this', 'Threat of consequences'),
    ]
    
    for pattern, description in threat_patterns:
        if re.search(pattern, text_lower):
            red_flags.append(('CRITICAL', 'THREAT', description))
    
    # IMPERSONATION
    impersonation_patterns = [
        (r'i\'?m (calling|writing|emailing) from (IT|HR|payroll|management|finance|legal)', 'Department impersonation'),
        (r'this is (the )?(CEO|CFO|president|director|manager) (of )?', 'Executive impersonation'),
        (r'i am (calling|writing) on behalf of', 'Third-party impersonation'),
        (r'from (microsoft|google|amazon|apple|paypal|bank of)', 'Company impersonation'),
    ]
    
    for pattern, description in impersonation_patterns:
        if re.search(pattern, text_lower):
            red_flags.append(('HIGH', 'IMPERSONATION', description))
    
    # DISCRIMINATION
    discriminatory_patterns = [
        (r'\b(too old|too young) (for|to)\b', 'Age discrimination'),
        (r'\b(hire|promote) (only )?(men|women|males|females)\b', 'Gender discrimination'),
    ]
    
    for pattern, description in discriminatory_patterns:
        if re.search(pattern, text_lower):
            red_flags.append(('HIGH', 'DISCRIMINATION', description))
    
    # ACADEMIC DISHONESTY
    academic_patterns = [
        (r'write (my|this) (essay|paper|assignment|homework)', 'Assignment fraud'),
        (r'take (my|this) (exam|test|quiz)', 'Test fraud'),
        (r'pretend (to be|you\'?re?) me', 'Impersonation for academic purposes'),
    ]
    
    for pattern, description in academic_patterns:
        if re.search(pattern, text_lower):
            red_flags.append(('HIGH', 'ACADEMIC_DISHONESTY', description))
    
    # MANIPULATION TACTICS
    manipulation_patterns = [
        (r'don\'?t tell (anyone|anybody|your|the)', 'Secrecy demand'),
        (r'keep this (between us|confidential|secret|quiet)', 'Inappropriate secrecy'),
        (r'this is (our|your) (little )?secret', 'Secrecy enforcement'),
    ]
    
    for pattern, description in manipulation_patterns:
        if re.search(pattern, text_lower):
            red_flags.append(('MEDIUM', 'MANIPULATION', description))
    
    # FALSE INFORMATION INDICATORS
    false_info_patterns = [
        (r'i was (sick|ill|hospitalized) (but )?actually', 'Admitted falsehood'),
        (r'lie (to|for) me', 'Request to lie'),
        (r'make (up|an excuse)', 'Request for false excuse'),
    ]
    
    for pattern, description in false_info_patterns:
        if re.search(pattern, text_lower):
            red_flags.append(('HIGH', 'FALSE_INFO', description))
    
    return red_flags

def categorize_severity(red_flags):
    """Categorize red flags by severity"""
    critical = [f for f in red_flags if f[0] == 'CRITICAL']
    high = [f for f in red_flags if f[0] == 'HIGH']
    medium = [f for f in red_flags if f[0] == 'MEDIUM']
    
    return critical, high, medium

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 security_scan.py 'text'")
        print("Example: python3 security_scan.py 'Please verify your password immediately'")
        sys.exit(1)
    
    text = sys.argv[1]
    red_flags = scan_for_threats(text)
    
    if red_flags:
        critical, high, medium = categorize_severity(red_flags)
        
        print("🛑 SECURITY SCAN RESULTS")
        print("=" * 60)
        
        if critical:
            print(f"\n🚨 CRITICAL ISSUES ({len(critical)}):")
            print("   These are severe security/safety violations")
            for _, category, desc in critical:
                print(f"   • [{category}] {desc}")
        
        if high:
            print(f"\n⚠️  HIGH PRIORITY ISSUES ({len(high)}):")
            print("   These require immediate attention")
            for _, category, desc in high:
                print(f"   • [{category}] {desc}")
        
        if medium:
            print(f"\n⚡ MEDIUM PRIORITY ISSUES ({len(medium)}):")
            print("   These should be reviewed carefully")
            for _, category, desc in medium:
                print(f"   • [{category}] {desc}")
        
        print("\n" + "=" * 60)
        if critical:
            print("❌ BLOCKED: Cannot format this email due to CRITICAL security issues")
            sys.exit(2)  # Exit code 2 = critical block
        elif high:
            print("⚠️  WARNING: This email has HIGH priority security concerns")
            print("   Review carefully before proceeding")
            sys.exit(1)  # Exit code 1 = warning
        else:
            print("⚠️  CAUTION: This email has some security concerns")
            print("   Proceed with care")
            sys.exit(1)
    else:
        print("✅ SECURITY SCAN PASSED")
        print("   No security red flags detected")
        sys.exit(0)  # Exit code 0 = safe
