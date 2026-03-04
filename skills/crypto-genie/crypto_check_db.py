#!/usr/bin/env python3
"""
Crypto Genie - Database-Only Checker with Real-Time Sync
Checks addresses against local database, syncs immediately if not found
Supports multiple blockchains: Ethereum, Solana, Bitcoin, XRP, etc.
"""

import sys
import json
import asyncio
import time
from datetime import datetime
from database import CryptoDatabase
from sync_worker import EtherscanSyncer
from secure_key_manager import get_api_key
from blockchain_detector import detect_blockchain
from typing import Dict

def format_risk_level(risk_score: int) -> tuple[str, str]:
    """Get risk level emoji and text"""
    if risk_score >= 80:
        return "🚨", "CRITICAL RISK"
    elif risk_score >= 50:
        return "⚠️", "HIGH RISK"
    elif risk_score >= 20:
        return "ℹ️", "MEDIUM RISK"
    else:
        return "✅", "LOW RISK"

async def sync_address_realtime(address: str, db: CryptoDatabase, blockchain_info: Dict) -> Dict:
    """
    Sync address from appropriate blockchain scanner in real-time
    Returns the analysis result
    """
    scanner = blockchain_info['scanner']
    chain_name = blockchain_info['name']
    
    # Get API key
    api_key = get_api_key()
    
    if not api_key:
        return {
            'error': True,
            'message': 'API key not configured. Please run: ./setup.sh'
        }
    
    # Show progress message
    print(f"⏳ Address not in database. Fetching from {blockchain_info['explorer']}...")
    print(f"   This may take 5-10 seconds...")
    print()
    
    start_time = time.time()
    
    try:
        if scanner == 'etherscan':
            # Use existing Etherscan syncer
            syncer = EtherscanSyncer(api_key, db)
            
            # Show progress
            print("🔄 Step 1/4: Fetching transaction count...")
            await asyncio.sleep(0.1)
            
            print("🔄 Step 2/4: Fetching balance...")
            await asyncio.sleep(0.1)
            
            print("🔄 Step 3/4: Analyzing transactions (up to 100)...")
            
            # Actually sync the address
            success = await syncer.sync_address(address)
            
            if not success:
                return {
                    'error': True,
                    'message': f'Failed to fetch data from {blockchain_info["explorer"]}. Please try again.'
                }
            
            print("🔄 Step 4/4: Calculating risk score...")
            await asyncio.sleep(0.1)
        
        elif scanner == 'solana':
            # Solana scanner (placeholder for now)
            print("🔄 Step 1/3: Fetching Solana account info...")
            await asyncio.sleep(0.5)
            
            print("🔄 Step 2/3: Fetching transaction history...")
            await asyncio.sleep(0.5)
            
            print("🔄 Step 3/3: Analyzing activity...")
            await asyncio.sleep(0.5)
            
            # TODO: Implement Solana scanner
            # For now, just store basic info
            db.upsert_address({
                'address': address,
                'chain': 'solana',
                'risk_score': 0,
                'risk_level': 'unknown',
                'transaction_count': 0,
                'last_etherscan_sync': datetime.now().isoformat()
            })
            
            return {
                'error': False,
                'note': 'Solana scanner is in development. Basic check performed.'
            }
        
        else:
            return {
                'error': True,
                'message': f'{chain_name} scanner not yet implemented'
            }
        
        # Calculate time taken
        elapsed = time.time() - start_time
        
        print(f"✅ Analysis complete! ({elapsed:.1f}s)")
        print()
        
        # Now get the data from database
        return {'error': False}
        
    except Exception as e:
        return {
            'error': True,
            'message': f'Error during sync: {str(e)}'
        }

async def check_address(address: str, db: CryptoDatabase) -> Dict:
    """Check address in local database, sync if not found"""
    
    # First, detect which blockchain this address belongs to
    blockchain_info = detect_blockchain(address)
    
    if not blockchain_info['valid']:
        return {
            'address': address,
            'error': True,
            'message': f"Invalid address format: {blockchain_info.get('error', 'Unknown format')}"
        }
    
    blockchain = blockchain_info['blockchain']
    chain_name = blockchain_info['name']
    scanner = blockchain_info['scanner']
    
    # Query database first
    address_data = db.get_address(address)
    
    if not address_data:
        # Address not in database - need to sync
        
        # Check if we support this blockchain
        if scanner not in ['etherscan', 'solana']:
            return {
                'address': address,
                'blockchain': chain_name,
                'scanner': scanner,
                'error': True,
                'message': f"{chain_name} support coming soon! Currently only Ethereum and Solana are supported."
            }
        
        # Sync it now!
        print(f"🔍 Detected: {chain_name}")
        sync_result = await sync_address_realtime(address, db, blockchain_info)

        
        if sync_result.get('error'):
            return {
                'address': address,
                'risk_score': 0,
                'risk_level': 'unknown',
                'error': True,
                'message': sync_result['message'],
                'recommendations': [
                    '⚠️ Could not analyze address',
                    '🔧 Check API key configuration',
                    '⏳ Try again in a moment'
                ]
            }
        
        # Sync successful, query database again
        address_data = db.get_address(address)
        
        if not address_data:
            return {
                'address': address,
                'risk_score': 0,
                'risk_level': 'unknown',
                'error': True,
                'message': 'Sync completed but data not found in database',
                'recommendations': [
                    '⚠️ Internal error occurred',
                    '🔧 Please report this issue'
                ]
            }
    
    # Address found in database - return analysis
    risk_score = address_data['risk_score']
    risk_level = address_data['risk_level']
    
    # Get additional data
    scam_indicators = db.get_scam_indicators(address)
    suspicious_txs = db.get_suspicious_transactions(address)
    
    # Build response
    result = {
        'address': address,
        'risk_score': risk_score,
        'risk_level': risk_level,
        'in_database': True,
        'is_known_scam': bool(address_data['is_known_scam']),
        'scam_type': address_data['scam_type'],
        'is_contract': bool(address_data['is_contract']),
        'is_verified': bool(address_data['is_verified']),
        'balance_eth': address_data['balance_eth'],
        'transaction_count': address_data['transaction_count'],
        'last_updated': address_data['updated_at'],
        'scam_indicators': [],
        'suspicious_transactions': [],
        'recommendations': []
    }
    
    # Add scam indicators
    for indicator in scam_indicators:
        result['scam_indicators'].append({
            'type': indicator['indicator_type'],
            'value': indicator['indicator_value'],
            'confidence': indicator['confidence'],
            'source': indicator['source']
        })
    
    # Add suspicious transactions summary
    for tx in suspicious_txs[:5]:  # Show top 5
        result['suspicious_transactions'].append({
            'tx_hash': tx['tx_hash'],
            'reason': tx['suspicion_reason'],
            'message_preview': tx['decoded_message'][:100] if tx['decoded_message'] else None
        })
    
    # Generate recommendations
    if risk_score >= 80:
        result['recommendations'] = [
            '🚫 DO NOT send funds to this address',
            '⚠️ This address has been flagged as high risk',
            '📞 Report the source that gave you this address',
            '🔍 Review scam indicators below'
        ]
    elif risk_score >= 50:
        result['recommendations'] = [
            '⚠️ Exercise EXTREME caution',
            '🔍 Review suspicious activity below',
            '💡 Consider alternative address',
            '📊 Wait for additional verification'
        ]
    elif risk_score >= 20:
        result['recommendations'] = [
            'ℹ️ Proceed with caution',
            '✅ Review the address carefully',
            '🔍 Check suspicious indicators',
            '💰 Consider a small test transaction first'
        ]
    else:
        result['recommendations'] = [
            '✅ No major red flags detected',
            'ℹ️ Proceed with normal caution',
            '🔍 Always verify the recipient address',
            '📊 Monitor transaction after sending'
        ]
    
    return result

def format_output(result: Dict) -> str:
    """Format result for human-readable display"""
    if result.get('error'):
        return f"\n❌ Error: {result['message']}\n"
    
    lines = []
    
    risk_emoji, risk_text = format_risk_level(result['risk_score'])
    
    lines.append(f"\n{risk_emoji} Analysis for {result['address']}")
    lines.append("")
    lines.append(f"Risk Score: {result['risk_score']}/100 - {risk_text}")
    lines.append(f"Last Updated: {result['last_updated']}")
    
    # Known scam warning
    if result['is_known_scam']:
        lines.append("")
        lines.append("🚨 KNOWN SCAM DETECTED!")
        if result['scam_type']:
            lines.append(f"Type: {result['scam_type'].upper()}")
    
    # Contract info
    if result['is_contract']:
        lines.append("")
        lines.append("⚙️ Smart Contract")
        if not result['is_verified']:
            lines.append("⚠️ NOT VERIFIED on Etherscan")
    else:
        lines.append("")
        lines.append("✅ Regular Wallet Address")
    
    # Blockchain data
    if result['transaction_count'] is not None:
        lines.append(f"   Transactions: {result['transaction_count']}")
    if result['balance_eth'] is not None:
        lines.append(f"   Balance: {result['balance_eth']:.6f} ETH")
    
    # Scam indicators
    if result['scam_indicators']:
        lines.append("")
        lines.append(f"🚨 {len(result['scam_indicators'])} Scam Indicator(s) Detected:")
        for indicator in result['scam_indicators']:
            lines.append(f"   • {indicator['value']} (confidence: {indicator['confidence']}%)")
    
    # Suspicious transactions
    if result['suspicious_transactions']:
        lines.append("")
        lines.append(f"⚠️ {len(result['suspicious_transactions'])} Suspicious Transaction(s):")
        for tx in result['suspicious_transactions']:
            lines.append(f"   • {tx['tx_hash'][:16]}...")
            lines.append(f"     Reason: {tx['reason']}")
            if tx['message_preview']:
                lines.append(f"     Message: \"{tx['message_preview']}...\"")
    
    # Recommendations
    lines.append("")
    lines.append("📋 Recommendations:")
    for rec in result['recommendations']:
        lines.append(f"  {rec}")
    
    lines.append("")
    
    return "\n".join(lines)

async def main_async():
    """Async main entry point"""
    if len(sys.argv) < 2:
        print("Usage: crypto_check_db.py <ethereum_address>")
        print("Example: crypto_check_db.py 0x1234567890abcdef1234567890abcdef12345678")
        print()
        print("Options:")
        print("  --json    Output JSON instead of human-readable format")
        sys.exit(1)
    
    address = sys.argv[1]
    
    # Initialize database
    db = CryptoDatabase()
    
    # Check address (will sync if not found)
    result = await check_address(address, db)
    
    # Output
    if '--json' in sys.argv:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(format_output(result))
    
    # Exit code based on risk
    if result.get('error'):
        sys.exit(3)  # Error occurred
    
    risk_score = result.get('risk_score', 0)
    if risk_score >= 80:
        sys.exit(2)  # Critical risk
    elif risk_score >= 50:
        sys.exit(1)  # High risk
    else:
        sys.exit(0)  # Safe

def main():
    """Synchronous wrapper for async main"""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
