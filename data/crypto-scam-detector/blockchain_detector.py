#!/usr/bin/env python3
"""
Blockchain Address Detector
Detects which blockchain an address belongs to based on format
"""

import re
from typing import Optional, Dict

class BlockchainDetector:
    """Detect blockchain type from address format"""
    
    # Address patterns for different blockchains
    # Order matters! Check more specific patterns first
    PATTERNS = {
        'ethereum': {
            'pattern': r'^0x[a-fA-F0-9]{40}$',
            'name': 'Ethereum',
            'explorer': 'etherscan.io',
            'scanner': 'etherscan'
        },
        'bitcoin': {
            'pattern': r'^(1|3)[a-zA-HJ-NP-Z0-9]{25,34}$|^bc1[a-z0-9]{39,59}$',
            'name': 'Bitcoin',
            'explorer': 'blockchain.com',
            'scanner': 'blockchain'
        },
        'ripple': {
            'pattern': r'^r[0-9a-zA-Z]{24,34}$',
            'name': 'XRP Ledger',
            'explorer': 'xrpscan.com',
            'scanner': 'xrp'
        },
        'tron': {
            'pattern': r'^T[a-zA-Z0-9]{33}$',
            'name': 'Tron',
            'explorer': 'tronscan.org',
            'scanner': 'tronscan'
        },
        'solana': {
            'pattern': r'^[1-9A-HJ-NP-Za-km-z]{32,44}$',
            'name': 'Solana',
            'explorer': 'solscan.io',
            'scanner': 'solana'
        },
        'binance': {
            'pattern': r'^(bnb1|0x)[a-zA-Z0-9]{38,42}$',
            'name': 'Binance Smart Chain',
            'explorer': 'bscscan.com',
            'scanner': 'bscscan'
        },
        'polygon': {
            'pattern': r'^0x[a-fA-F0-9]{40}$',  # Same as Ethereum
            'name': 'Polygon',
            'explorer': 'polygonscan.com',
            'scanner': 'polygonscan'
        },
        'cardano': {
            'pattern': r'^addr1[a-z0-9]{58,}$',
            'name': 'Cardano',
            'explorer': 'cardanoscan.io',
            'scanner': 'cardano'
        },
        'ripple': {
            'pattern': r'^r[0-9a-zA-Z]{24,34}$',
            'name': 'XRP Ledger',
            'explorer': 'xrpscan.com',
            'scanner': 'xrp'
        },
        'tron': {
            'pattern': r'^T[a-zA-Z0-9]{33}$',
            'name': 'Tron',
            'explorer': 'tronscan.org',
            'scanner': 'tronscan'
        }
    }
    
    @classmethod
    def detect(cls, address: str) -> Dict:
        """
        Detect blockchain type from address
        
        Returns:
            {
                'blockchain': 'ethereum',
                'name': 'Ethereum',
                'explorer': 'etherscan.io',
                'scanner': 'etherscan',
                'address': '0x...',
                'valid': True
            }
        """
        address = address.strip()
        
        # Check each pattern
        matches = []
        
        for blockchain_id, info in cls.PATTERNS.items():
            if re.match(info['pattern'], address):
                matches.append({
                    'blockchain': blockchain_id,
                    'name': info['name'],
                    'explorer': info['explorer'],
                    'scanner': info['scanner'],
                    'address': address,
                    'valid': True
                })
        
        # Handle ambiguous cases
        if len(matches) > 1:
            # Ethereum vs Polygon vs BSC (all 0x addresses)
            if address.startswith('0x'):
                # Default to Ethereum, but note it could be Polygon/BSC
                result = matches[0].copy()
                result['note'] = f"Could also be: {', '.join([m['name'] for m in matches[1:]])}"
                return result
        
        if matches:
            return matches[0]
        
        # No match found
        return {
            'blockchain': 'unknown',
            'name': 'Unknown',
            'explorer': None,
            'scanner': None,
            'address': address,
            'valid': False,
            'error': 'Address format not recognized'
        }
    
    @classmethod
    def is_ethereum_compatible(cls, address: str) -> bool:
        """Check if address is Ethereum or EVM-compatible (Polygon, BSC, etc.)"""
        return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address.strip()))
    
    @classmethod
    def is_solana(cls, address: str) -> bool:
        """Check if address is Solana"""
        return bool(re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', address.strip()))


def detect_blockchain(address: str) -> Dict:
    """Convenience function to detect blockchain"""
    return BlockchainDetector.detect(address)


if __name__ == '__main__':
    # Test the detector
    test_addresses = [
        '0x098B716B8Aaf21512996dC57EB0615e2383E2f96',  # Ethereum
        'DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK',  # Solana
        '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',  # Bitcoin
        'rN7n7otQDd6FczFgLdlqtyMVrn3hBoQh8F',  # XRP
        'addr1qxy7h9w9sk8dqxlmfhgfwxzm5jqfvjfyxr4ybxfxfxfxfxfxfxfxfx',  # Cardano
        'TRX9a5YsGVw8dLjQxnJhFmEoaWz8TkLqzL',  # Tron
    ]
    
    for addr in test_addresses:
        result = detect_blockchain(addr)
        print(f"\nAddress: {addr}")
        print(f"  Blockchain: {result['name']}")
        print(f"  Scanner: {result.get('scanner', 'N/A')}")
        print(f"  Valid: {result['valid']}")
        if 'note' in result:
            print(f"  Note: {result['note']}")
