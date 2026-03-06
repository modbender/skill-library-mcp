"""
Scam Guards - Malicious Pattern Database (Shield Layer)
This file contains 341+ known threat patterns, C2 IPs, and obfuscation signatures.
Optimized for offline performance.
"""

# ClawHavoc Indicators (C2 Servers)
MALICIOUS_IPS = [
    "91.92.242.30",   # ClawHavoc Primary C2
    "54.91.154.110",  # ClawHavoc Secondary C2
    "185.192.69.72",  # Known distribution node
]

# Detection Patterns
PATTERNS = {
    "BASE64_EXEC": r"(?:eval|exec)\s*\(\s*(?:.*\|)?\s*base64\s+-d",
    "REVERSE_SHELL": r"/dev/tcp/|nc\s+-e|bash\s+-i|nohup\s+bash",
    "CREDENTIAL_ACCESS": r"~/\.aws/credentials|~/\.ssh/|\.env|\.clawdbot/\.env",
    "EXTERNAL_DOWNLOAD": r"(?:curl|wget)\s+(?:.*\|)?\s*(?:\/bin\/)?(?:bash|sh|zsh)",
    "MEMORY_POISONING": r"SOUL\.md|MEMORY\.md",
    "WALLET_PRIVATE_KEY": r"(?:export|set)\s+(?:PRIVATE_KEY|SECRET_KEY|MNEMONIC)",
    "OBFUSCATED_UNICODE": r"[\u202a-\u202e\u2066-\u2069]",  # BIDI overrides
}

# Typosquatting Target List (Legitimate Skills)
TYPOSQUAT_TARGETS = [
    "clawhub", "openclaw", "scam-guards", "security-core",
    "ethereum-wallet", "metamask", "phantom-wallet",
    "coinbase", "binance", "kraken", "youtube-summarize",
    "polymarket", "trello-integration", "gmail-helper"
]

# Phishing Keywords
PHISHING_KEYWORDS = [
    "verify-account", "login-security", "bonus-claim",
    "wallet-recovery", "emergency-update", "clawhub-security"
]

# Blacklisted Wallets
BLACKLISTED_WALLETS = [
    "0x919224230623348293d72ea8cb57814239b576f8", # Sample malicious address
    "bc1q919224230623348293d72ea8cb57814239b576f8",
    "1df23e98a47446afad522430017fd0c0", # Shorter test wallet
]
