#!/usr/bin/env python3
"""
ClawBack Unified Authentication Utility
Handles complete E*TRADE OAuth flow including token refresh and error recovery.
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from clawback.etrade_adapter import ETradeAdapter


class AuthUtility:
    """Unified authentication utility for E*TRADE OAuth flow"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with config path"""
        if config_path is None:
            config_path = os.path.expanduser('~/.clawback/config.json')
        
        self.config_path = config_path
        self.config = self._load_config()
        self.adapter = None
        self.tokens_file = os.path.expanduser('~/.clawback/.access_tokens.json')
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _save_tokens(self, tokens: Dict[str, Any]) -> None:
        """Save tokens to file with metadata"""
        tokens['saved_at'] = datetime.now().isoformat()
        tokens['config_path'] = self.config_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.tokens_file), exist_ok=True)
        
        with open(self.tokens_file, 'w') as f:
            json.dump(tokens, f, indent=2)
        
        print(f"✅ Tokens saved to {self.tokens_file}")
    
    def _load_tokens(self) -> Optional[Dict[str, Any]]:
        """Load tokens from file"""
        if not os.path.exists(self.tokens_file):
            return None
        
        try:
            with open(self.tokens_file, 'r') as f:
                tokens = json.load(f)
            
            # Check if tokens are expired
            if 'expires_at' in tokens:
                expires_at = datetime.fromisoformat(tokens['expires_at'])
                if datetime.now() > expires_at:
                    print("⚠️  Tokens have expired")
                    return None
            
            return tokens
        except Exception as e:
            print(f"❌ Error loading tokens: {e}")
            return None
    
    def _create_adapter(self) -> ETradeAdapter:
        """Create E*TRADE adapter instance"""
        if self.adapter is None:
            self.adapter = ETradeAdapter(self.config)
        return self.adapter
    
    def check_auth_status(self) -> Dict[str, Any]:
        """Check current authentication status"""
        print("\n🔍 Checking authentication status...")
        
        status = {
            'config_exists': os.path.exists(self.config_path),
            'tokens_exist': os.path.exists(self.tokens_file),
            'config_valid': False,
            'tokens_valid': False,
            'broker_connected': False
        }
        
        # Check config
        if status['config_exists']:
            try:
                self.config = self._load_config()
                status['config_valid'] = True
                print(f"✅ Config loaded from {self.config_path}")
                print(f"   Environment: {self.config.get('broker', {}).get('environment', 'unknown')}")
            except Exception as e:
                print(f"❌ Config invalid: {e}")
        
        # Check tokens
        tokens = self._load_tokens()
        if tokens:
            status['tokens_valid'] = True
            print(f"✅ Tokens found (saved: {tokens.get('saved_at', 'unknown')})")
            
            if 'access_token' in tokens:
                print(f"   Access token: {tokens['access_token'][:30]}...")
            
            if 'expires_at' in tokens:
                expires_at = datetime.fromisoformat(tokens['expires_at'])
                time_left = expires_at - datetime.now()
                print(f"   Expires in: {time_left}")
        
        return status
    
    def start_auth_flow(self) -> bool:
        """Start new OAuth authentication flow"""
        print("\n🚀 Starting OAuth authentication flow...")
        
        try:
            adapter = self._create_adapter()
            
            # Get authorization URL
            print("\n1. Getting authorization URL...")
            auth_url = adapter.get_auth_url()
            
            if not auth_url:
                print("❌ Failed to get authorization URL")
                return False
            
            print(f"✅ Authorization URL generated")
            print(f"\n📋 Please visit this URL in your browser:")
            print(f"   {auth_url}")
            print("\n🔐 After authorizing, you'll get a verification code.")
            
            # Get verification code from user
            print("\n" + "="*60)
            verification_code = input("Enter verification code: ").strip()
            
            if not verification_code:
                print("❌ Verification code required")
                return False
            
            print(f"\n2. Exchanging code for tokens...")
            success = adapter.authenticate(verification_code)
            
            if not success:
                print("❌ Authentication failed")
                print("   Possible issues:")
                print("   - Incorrect verification code")
                print("   - Authorization expired")
                print("   - Network issues")
                return False
            
            print("✅ Authentication successful!")
            
            # Save tokens
            tokens = {
                'access_token': adapter.access_token,
                'access_secret': adapter.access_secret,
                'request_token': adapter.request_token,
                'request_secret': adapter.request_secret,
                'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            self._save_tokens(tokens)
            
            # Test connection
            print("\n3. Testing broker connection...")
            try:
                accounts = adapter.get_accounts()
                if accounts:
                    print(f"✅ Connected! Found {len(accounts)} account(s)")
                    for account in accounts:
                        print(f"   - {account.get('accountId', 'Unknown')}: {account.get('accountMode', 'Unknown')}")
                else:
                    print("⚠️  Connected but no accounts found")
            except Exception as e:
                print(f"⚠️  Connection test warning: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Authentication flow failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def refresh_tokens(self) -> bool:
        """Refresh expired tokens"""
        print("\n🔄 Attempting to refresh tokens...")
        
        tokens = self._load_tokens()
        if not tokens:
            print("❌ No tokens found to refresh")
            return False
        
        # Check if refresh is possible
        if 'refresh_token' not in tokens:
            print("⚠️  No refresh token available")
            print("   Starting new authentication flow...")
            return self.start_auth_flow()
        
        try:
            adapter = self._create_adapter()
            
            # Set existing tokens for refresh
            adapter.access_token = tokens.get('access_token')
            adapter.access_secret = tokens.get('access_secret')
            
            # Attempt refresh (implementation depends on E*TRADE API)
            print("⚠️  Token refresh not fully implemented")
            print("   Starting new authentication flow...")
            return self.start_auth_flow()
            
        except Exception as e:
            print(f"❌ Token refresh failed: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test broker connection with current tokens"""
        print("\n🔌 Testing broker connection...")
        
        tokens = self._load_tokens()
        if not tokens:
            print("❌ No tokens found")
            return False
        
        try:
            adapter = self._create_adapter()
            
            # Set tokens
            adapter.access_token = tokens.get('access_token')
            adapter.access_secret = tokens.get('access_secret')
            
            # Test connection
            accounts = adapter.get_accounts()
            
            if accounts:
                print(f"✅ Connection successful!")
                print(f"   Found {len(accounts)} account(s)")
                
                # Get account balance if account ID is configured
                account_id = self.config.get('trading', {}).get('accountId')
                if account_id:
                    try:
                        balance = adapter.get_account_balance(account_id)
                        print(f"   Account {account_id} balance: ${balance:,.2f}")
                    except Exception as e:
                        print(f"⚠️  Could not get balance: {e}")
                
                return True
            else:
                print("⚠️  Connected but no accounts found")
                return False
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def interactive_mode(self) -> None:
        """Interactive authentication mode"""
        print("\n" + "="*60)
        print("ClawBack Authentication Utility")
        print("="*60)
        
        while True:
            print("\nOptions:")
            print("1. Check authentication status")
            print("2. Start new authentication")
            print("3. Test broker connection")
            print("4. Refresh tokens")
            print("5. Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                self.check_auth_status()
            elif choice == '2':
                self.start_auth_flow()
            elif choice == '3':
                self.test_connection()
            elif choice == '4':
                self.refresh_tokens()
            elif choice == '5':
                print("\n👋 Exiting...")
                break
            else:
                print("❌ Invalid choice")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ClawBack Authentication Utility')
    parser.add_argument('--check', action='store_true', help='Check authentication status')
    parser.add_argument('--auth', action='store_true', help='Start authentication flow')
    parser.add_argument('--test', action='store_true', help='Test broker connection')
    parser.add_argument('--refresh', action='store_true', help='Refresh tokens')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--config', help='Path to config file')
    
    args = parser.parse_args()
    
    try:
        utility = AuthUtility(args.config)
        
        if args.check:
            utility.check_auth_status()
        elif args.auth:
            utility.start_auth_flow()
        elif args.test:
            utility.test_connection()
        elif args.refresh:
            utility.refresh_tokens()
        elif args.interactive:
            utility.interactive_mode()
        else:
            # Default: check status
            status = utility.check_auth_status()
            
            if not status['tokens_valid']:
                print("\n⚠️  Authentication required")
                print("   Run: python scripts/auth_utility.py --auth")
            elif not status['broker_connected']:
                print("\n⚠️  Connection test recommended")
                print("   Run: python scripts/auth_utility.py --test")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())