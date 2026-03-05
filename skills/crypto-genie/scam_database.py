"""
Scam Database
Maintains a database of known scam addresses and patterns
"""

import json
from typing import Dict, Optional, Set
from datetime import datetime


class ScamDatabase:
    """Database of known crypto scams"""
    
    def __init__(self):
        self.scam_addresses: Dict[str, Dict] = {}
        self.scam_domains: Set[str] = set()
        self.load_database()
    
    def load_database(self):
        """Load known scams from database"""
        # Known scam addresses (examples for demo)
        self.scam_addresses = {
            "0x1234567890abcdef1234567890abcdef12345678": {
                "type": "phishing",
                "reported": "2026-01-15",
                "description": "Fake MetaMask support phishing site",
                "reporter": "community"
            },
            "0xabcdef1234567890abcdef1234567890abcdef12": {
                "type": "ponzi",
                "reported": "2026-02-01",
                "description": "Ponzi scheme smart contract",
                "reporter": "security_researcher"
            },
            "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef": {
                "type": "rug_pull",
                "reported": "2026-02-10",
                "description": "Rug pulled token contract - liquidity removed",
                "reporter": "community"
            },
            "0x0000000000000000000000000000000000000001": {
                "type": "honeypot",
                "reported": "2026-01-20",
                "description": "Honeypot contract - accepts deposits but blocks withdrawals",
                "reporter": "security_audit"
            },
            # Add more known scam addresses
            "0x1111111111111111111111111111111111111111": {
                "type": "phishing",
                "reported": "2026-02-15",
                "description": "Impersonating Uniswap router",
                "reporter": "community"
            },
            "0x2222222222222222222222222222222222222222": {
                "type": "fake_ico",
                "reported": "2026-02-18",
                "description": "Fake ICO collection address",
                "reporter": "verified_user"
            }
        }
        
        # Known scam domains
        self.scam_domains = {
            "eth-giveaway-official.com",
            "metamask-verify.com",
            "coinbase-support-verify.com",
            "binance-security-check.com",
            "uniswap-claim.com",
            "opensea-nft-claim.com",
            "wallet-connect-verify.com"
        }
    
    def check_address(self, address: str) -> Optional[Dict]:
        """
        Check if an address is a known scam
        
        Args:
            address: Address to check
            
        Returns:
            Scam info if found, None otherwise
        """
        return self.scam_addresses.get(address.lower())
    
    def check_domain(self, domain: str) -> bool:
        """
        Check if a domain is a known scam
        
        Args:
            domain: Domain to check
            
        Returns:
            True if known scam, False otherwise
        """
        return domain.lower() in self.scam_domains
    
    def add_scam_address(
        self,
        address: str,
        scam_type: str,
        description: str,
        reporter: str = "user"
    ):
        """Add a new scam address to the database"""
        self.scam_addresses[address.lower()] = {
            "type": scam_type,
            "reported": datetime.now().strftime("%Y-%m-%d"),
            "description": description,
            "reporter": reporter
        }
    
    def add_scam_domain(self, domain: str):
        """Add a new scam domain to the database"""
        self.scam_domains.add(domain.lower())
    
    def get_size(self) -> Dict[str, int]:
        """Get database size statistics"""
        return {
            "addresses": len(self.scam_addresses),
            "domains": len(self.scam_domains)
        }
    
    def get_scam_types(self) -> Dict[str, int]:
        """Get count of each scam type"""
        types = {}
        for scam_info in self.scam_addresses.values():
            scam_type = scam_info.get('type', 'unknown')
            types[scam_type] = types.get(scam_type, 0) + 1
        return types
    
    def search_by_type(self, scam_type: str) -> Dict[str, Dict]:
        """Get all scams of a specific type"""
        return {
            addr: info
            for addr, info in self.scam_addresses.items()
            if info.get('type') == scam_type
        }


# Example usage
if __name__ == "__main__":
    db = ScamDatabase()
    
    print("Scam Database Statistics:")
    print(json.dumps(db.get_size(), indent=2))
    
    print("\nScam Types:")
    print(json.dumps(db.get_scam_types(), indent=2))
    
    # Test address check
    test_addr = "0x1234567890abcdef1234567890abcdef12345678"
    result = db.check_address(test_addr)
    
    if result:
        print(f"\n⚠️ Address {test_addr} is a known scam!")
        print(f"Type: {result['type']}")
        print(f"Description: {result['description']}")
    else:
        print(f"\n✅ Address {test_addr} not in scam database")

