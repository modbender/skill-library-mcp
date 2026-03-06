#!/usr/bin/env python3
"""
Background Worker - Syncs address data from Etherscan to local database
Runs continuously or as a cron job
"""

import asyncio
import httpx
import time
import argparse
from datetime import datetime
from typing import Optional, Dict, List
from database import CryptoDatabase
from secure_key_manager import get_api_key

class EtherscanSyncer:
    """Syncs address data from Etherscan API to local database"""
    
    def __init__(self, api_key: str, db: CryptoDatabase):
        self.api_key = api_key
        self.db = db
        self.base_url = "https://api.etherscan.io/v2/api"
        
    async def fetch_address_info(self, address: str) -> Optional[Dict]:
        """Fetch address info from Etherscan API"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get transaction count
                tx_response = await client.get(
                    f"{self.base_url}?chainid=1&module=proxy&action=eth_getTransactionCount"
                    f"&address={address}&tag=latest&apikey={self.api_key}"
                )
                
                # Get balance
                balance_response = await client.get(
                    f"{self.base_url}?chainid=1&module=account&action=balance"
                    f"&address={address}&tag=latest&apikey={self.api_key}"
                )
                
                # Get transaction list (last 100)
                tx_list_response = await client.get(
                    f"{self.base_url}?chainid=1&module=account&action=txlist"
                    f"&address={address}&startblock=0&endblock=99999999"
                    f"&page=1&offset=100&sort=desc&apikey={self.api_key}"
                )
                
                # Check if it's a contract
                code_response = await client.get(
                    f"{self.base_url}?chainid=1&module=proxy&action=eth_getCode"
                    f"&address={address}&tag=latest&apikey={self.api_key}"
                )
                
                return {
                    'tx_count': tx_response.json(),
                    'balance': balance_response.json(),
                    'transactions': tx_list_response.json(),
                    'code': code_response.json()
                }
                
        except Exception as e:
            print(f"❌ Error fetching from Etherscan: {e}")
            return None
    
    def decode_hex_message(self, hex_data: str) -> Optional[str]:
        """Decode hex input data to UTF-8 if possible"""
        try:
            if not hex_data or hex_data == '0x':
                return None
            
            # Remove 0x prefix
            hex_clean = hex_data[2:] if hex_data.startswith('0x') else hex_data
            
            # Convert hex to bytes
            data_bytes = bytes.fromhex(hex_clean)
            
            # Try UTF-8 decode
            message = data_bytes.decode('utf-8', errors='ignore')
            
            # Filter out non-printable characters
            message = ''.join(char for char in message if char.isprintable() or char in '\n\r\t')
            
            return message.strip() if message.strip() else None
            
        except Exception:
            return None
    
    def analyze_transaction_message(self, message: str) -> tuple[bool, Optional[str]]:
        """
        Analyze decoded transaction message for suspicious content
        Returns (is_suspicious, reason)
        """
        if not message:
            return False, None
        
        message_lower = message.lower()
        
        # Suspicious keywords
        suspicious_keywords = [
            'lazarus', 'vanguard', 'hack', 'exploit', 'breach', 'ronin',
            'orbit bridge', 'phishing', 'scam', 'rug pull', 'honeypot',
            'private key', 'seed phrase', 'metamask support', 'wallet recovery',
            'urgent', 'verify your wallet', 'claim reward', 'airdrop winner'
        ]
        
        for keyword in suspicious_keywords:
            if keyword in message_lower:
                return True, f"Suspicious keyword detected: '{keyword}'"
        
        # Check for URLs to common scam domains
        scam_domains = ['metamask-support', 'wallet-verify', 'claim-eth', 'free-crypto']
        for domain in scam_domains:
            if domain in message_lower:
                return True, f"Suspicious domain in message: '{domain}'"
        
        return False, None
    
    def calculate_risk_score(self, address_data: Dict, transactions: List[Dict]) -> int:
        """
        Calculate risk score based on multiple factors
        Returns 0-100
        """
        risk_score = 0
        
        # Check for suspicious transactions
        suspicious_tx_count = sum(1 for tx in transactions if tx.get('is_suspicious'))
        if suspicious_tx_count > 0:
            risk_score += min(50, suspicious_tx_count * 25)
        
        # Check transaction patterns
        tx_count = address_data.get('transaction_count', 0)
        
        if tx_count == 0:
            risk_score += 10  # Very new address
        elif tx_count < 5:
            risk_score += 5   # Low activity
        
        # Check balance patterns
        balance_eth = address_data.get('balance_eth', 0)
        if balance_eth > 100:
            # Large balance with suspicious activity
            if suspicious_tx_count > 0:
                risk_score += 20
        
        # Unverified contracts are risky
        if address_data.get('is_contract') and not address_data.get('is_verified'):
            risk_score += 30
        
        return min(100, risk_score)
    
    async def sync_address(self, address: str) -> bool:
        """Sync a single address from Etherscan to database"""
        try:
            print(f"🔄 Syncing {address}...")
            
            # Fetch from Etherscan
            data = await self.fetch_address_info(address)
            if not data:
                return False
            
            # Parse transaction count
            tx_count_hex = data['tx_count'].get('result', '0x0')
            tx_count = int(tx_count_hex, 16) if tx_count_hex else 0
            
            # Parse balance
            balance_wei = data['balance'].get('result', '0')
            balance_eth = int(balance_wei) / 1e18 if balance_wei else 0
            
            # Check if contract
            code = data['code'].get('result', '0x')
            is_contract = code != '0x' and code != '0x0'
            
            # Parse transactions
            tx_list = data['transactions'].get('result', [])
            if isinstance(tx_list, str):  # API error
                tx_list = []
            
            suspicious_transactions = []
            
            # Analyze transactions for suspicious content
            for tx in tx_list[:20]:  # Analyze last 20 transactions
                input_data = tx.get('input', '0x')
                
                # Decode message if present
                decoded_message = self.decode_hex_message(input_data)
                
                if decoded_message:
                    is_suspicious, reason = self.analyze_transaction_message(decoded_message)
                    
                    if is_suspicious:
                        tx_data = {
                            'tx_hash': tx.get('hash'),
                            'address': address,
                            'block_number': int(tx.get('blockNumber', 0)),
                            'timestamp': int(tx.get('timeStamp', 0)),
                            'from_address': tx.get('from'),
                            'to_address': tx.get('to'),
                            'value': tx.get('value'),
                            'input_data': input_data[:1000],  # Store first 1000 chars
                            'decoded_message': decoded_message[:1000],
                            'is_suspicious': True,
                            'suspicion_reason': reason
                        }
                        
                        suspicious_transactions.append(tx_data)
                        
                        # Save to database
                        self.db.add_transaction(tx_data)
                        
                        # Add scam indicator
                        self.db.add_scam_indicator(
                            address, 
                            'suspicious_transaction',
                            reason,
                            80,  # High confidence
                            'etherscan_analysis'
                        )
            
            # Calculate risk score
            address_data = {
                'transaction_count': tx_count,
                'balance_eth': balance_eth,
                'is_contract': is_contract,
                'is_verified': False  # Would need additional API call to check
            }
            
            risk_score = self.calculate_risk_score(address_data, suspicious_transactions)
            
            # Determine risk level
            if risk_score >= 80:
                risk_level = 'critical'
            elif risk_score >= 50:
                risk_level = 'high'
            elif risk_score >= 20:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            # Store in database
            address_record = {
                'address': address,
                'chain': 'ethereum',
                'risk_score': risk_score,
                'risk_level': risk_level,
                'is_known_scam': risk_score >= 80,
                'is_contract': is_contract,
                'is_verified': False,
                'balance_wei': balance_wei,
                'balance_eth': balance_eth,
                'transaction_count': tx_count,
                'first_seen_block': int(tx_list[0]['blockNumber']) if tx_list else None,
                'last_seen_block': int(tx_list[-1]['blockNumber']) if tx_list else None,
                'synced': True,
                'metadata': {
                    'suspicious_tx_count': len(suspicious_transactions),
                    'last_sync': datetime.utcnow().isoformat()
                }
            }
            
            self.db.upsert_address(address_record)
            
            print(f"✅ Synced {address} - Risk: {risk_score}/100 ({risk_level})")
            
            if suspicious_transactions:
                print(f"   ⚠️  Found {len(suspicious_transactions)} suspicious transactions")
            
            return True
            
        except Exception as e:
            print(f"❌ Error syncing {address}: {e}")
            return False
    
    async def run_worker(self, max_jobs: int = None, delay: float = 1.5):
        """
        Run background worker continuously
        
        Args:
            max_jobs: Maximum jobs to process (None = infinite)
            delay: Delay between API calls (respect rate limits)
        """
        print("🚀 Starting Etherscan sync worker...")
        print(f"   API Key: {self.api_key[:10]}...")
        print(f"   Database: {self.db.db_path}")
        print()
        
        jobs_processed = 0
        
        while True:
            # Get next job from queue
            job = self.db.get_next_sync_job()
            
            if not job:
                print("⏸️  No pending jobs. Waiting...")
                await asyncio.sleep(10)
                continue
            
            address = job['address']
            
            # Sync address
            success = await self.sync_address(address)
            
            if success:
                self.db.update_sync_status(address, 'completed')
                jobs_processed += 1
            else:
                error_msg = "Failed to fetch from Etherscan"
                self.db.update_sync_status(address, 'failed', error_msg)
            
            # Check if we've hit max jobs
            if max_jobs and jobs_processed >= max_jobs:
                print(f"\n✅ Completed {jobs_processed} jobs. Stopping.")
                break
            
            # Rate limit delay
            await asyncio.sleep(delay)


async def main():
    parser = argparse.ArgumentParser(description='Etherscan Sync Worker')
    parser.add_argument('--max-jobs', type=int, help='Maximum jobs to process')
    parser.add_argument('--delay', type=float, default=1.5, 
                       help='Delay between API calls (seconds)')
    parser.add_argument('--add-address', type=str, 
                       help='Add a single address to sync queue')
    parser.add_argument('--stats', action='store_true', 
                       help='Show database statistics')
    
    args = parser.parse_args()
    
    # Initialize database
    db = CryptoDatabase()
    
    # Show stats if requested
    if args.stats:
        print("📊 Database Statistics")
        print("=" * 50)
        stats = db.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        return
    
    # Add address to queue if requested
    if args.add_address:
        db.add_to_sync_queue(args.add_address, priority=10)
        print(f"✅ Added {args.add_address} to sync queue")
        return
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        print("❌ No Etherscan API key configured!")
        print("   Set ETHERSCAN_API_KEY environment variable or run: ./setup.sh")
        return
    
    # Create syncer
    syncer = EtherscanSyncer(api_key, db)
    
    # Run worker
    await syncer.run_worker(max_jobs=args.max_jobs, delay=args.delay)


if __name__ == "__main__":
    asyncio.run(main())
