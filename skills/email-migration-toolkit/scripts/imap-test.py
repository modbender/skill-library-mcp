#!/usr/bin/env python3
"""
IMAP Connectivity Test Script
Tests IMAP connection to any email provider
Usage: python3 imap-test.py [--server SERVER] [--port PORT] [--username USER] [--password PASS] [--ssl]
"""

import imaplib
import argparse
import sys
import ssl
import socket
from getpass import getpass

def test_imap_connection(server, port, username, password, use_ssl=True, timeout=30):
    """Test IMAP connection with given parameters"""
    
    print(f"Testing IMAP connection to {server}:{port}")
    print(f"Username: {username}")
    print(f"SSL/TLS: {'Enabled' if use_ssl else 'Disabled'}")
    print(f"Timeout: {timeout} seconds")
    print("-" * 50)
    
    try:
        # Set socket timeout
        socket.setdefaulttimeout(timeout)
        
        # Create IMAP connection
        if use_ssl:
            print("Connecting with SSL/TLS...")
            if port == 993:
                imap = imaplib.IMAP4_SSL(server, port)
            else:
                # STARTTLS connection
                print("Using STARTTLS on non-standard port...")
                imap = imaplib.IMAP4(server, port)
                imap.starttls()
        else:
            print("Connecting without encryption (not recommended)...")
            imap = imaplib.IMAP4(server, port)
        
        print("✅ Connected successfully")
        
        # Test authentication
        print(f"Authenticating as {username}...")
        result = imap.login(username, password)
        print(f"✅ Authentication successful: {result[0]}")
        
        # List mailboxes
        print("Listing mailboxes...")
        result, mailboxes = imap.list()
        if result == 'OK':
            print(f"✅ Found {len(mailboxes)} mailboxes")
            
            # Show first few mailboxes
            print("Sample mailboxes:")
            for i, mailbox in enumerate(mailboxes[:5]):
                decoded_mailbox = mailbox.decode('utf-8')
                print(f"  {i+1}. {decoded_mailbox}")
            
            if len(mailboxes) > 5:
                print(f"  ... and {len(mailboxes) - 5} more")
        
        # Test selecting INBOX
        print("Selecting INBOX...")
        result, data = imap.select('INBOX')
        if result == 'OK':
            message_count = int(data[0])
            print(f"✅ INBOX selected successfully - {message_count} messages")
        else:
            print(f"❌ Failed to select INBOX: {result}")
        
        # Test search functionality
        print("Testing search functionality...")
        result, data = imap.search(None, 'ALL')
        if result == 'OK':
            message_ids = data[0].split() if data[0] else []
            print(f"✅ Search successful - found {len(message_ids)} message IDs")
        else:
            print(f"❌ Search failed: {result}")
        
        # Logout
        imap.logout()
        print("✅ Logged out successfully")
        print("\n🎉 All tests passed! IMAP connection is working correctly.")
        return True
        
    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP Error: {e}")
        return False
    except ssl.SSLError as e:
        print(f"❌ SSL Error: {e}")
        print("💡 Try with --no-ssl flag or check certificate settings")
        return False
    except socket.timeout:
        print(f"❌ Connection timeout after {timeout} seconds")
        print("💡 Try increasing timeout or check firewall settings")
        return False
    except socket.gaierror as e:
        print(f"❌ DNS Error: {e}")
        print("💡 Check server address and DNS settings")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def get_provider_presets():
    """Return common provider presets"""
    return {
        'gmail': {
            'server': 'imap.gmail.com',
            'port': 993,
            'ssl': True,
            'note': 'Requires app password if 2FA is enabled'
        },
        'yahoo': {
            'server': 'imap.mail.yahoo.com', 
            'port': 993,
            'ssl': True,
            'note': 'Requires app password'
        },
        'outlook': {
            'server': 'outlook.office365.com',
            'port': 993, 
            'ssl': True,
            'note': 'Works for both personal and business accounts'
        },
        'icloud': {
            'server': 'imap.mail.me.com',
            'port': 993,
            'ssl': True,
            'note': 'Requires app-specific password'
        },
        'zoho': {
            'server': 'imap.zoho.com',
            'port': 993,
            'ssl': True,
            'note': 'Regular password usually works'
        }
    }

def main():
    parser = argparse.ArgumentParser(
        description='Test IMAP connectivity to email providers',
        epilog='Examples:\n'
               '  python3 imap-test.py gmail\n'
               '  python3 imap-test.py --server imap.gmail.com --username user@gmail.com\n'
               '  python3 imap-test.py custom --server mail.company.com --port 143 --no-ssl',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('preset', nargs='?', help='Provider preset (gmail, yahoo, outlook, icloud, zoho, custom)')
    parser.add_argument('--server', help='IMAP server address')
    parser.add_argument('--port', type=int, help='IMAP port (default: 993 for SSL, 143 for plain)')
    parser.add_argument('--username', help='Email username/address')
    parser.add_argument('--password', help='Password (will prompt if not provided)')
    parser.add_argument('--no-ssl', action='store_true', help='Disable SSL/TLS encryption')
    parser.add_argument('--timeout', type=int, default=30, help='Connection timeout in seconds')
    parser.add_argument('--list-presets', action='store_true', help='List available provider presets')
    
    args = parser.parse_args()
    
    # List presets and exit
    if args.list_presets:
        presets = get_provider_presets()
        print("Available provider presets:")
        for name, config in presets.items():
            print(f"\n{name}:")
            print(f"  Server: {config['server']}:{config['port']}")
            print(f"  SSL: {config['ssl']}")
            print(f"  Note: {config['note']}")
        return
    
    # Get provider preset if specified
    presets = get_provider_presets()
    if args.preset and args.preset in presets:
        preset = presets[args.preset]
        server = args.server or preset['server']
        port = args.port or preset['port']
        use_ssl = not args.no_ssl and preset['ssl']
        print(f"Using {args.preset} preset")
        print(f"Note: {preset['note']}")
        print()
    else:
        # Use command line arguments or defaults
        server = args.server
        port = args.port or (993 if not args.no_ssl else 143)
        use_ssl = not args.no_ssl
        
        if not server:
            print("Error: Server address required")
            print("Use --server SERVER or choose a preset (gmail, yahoo, outlook, icloud, zoho)")
            print("Use --list-presets to see available presets")
            sys.exit(1)
    
    # Get username
    username = args.username
    if not username:
        username = input("Email address: ").strip()
    
    # Get password
    password = args.password
    if not password:
        password = getpass("Password (or app password): ")
    
    # Run the test
    success = test_imap_connection(server, port, username, password, use_ssl, args.timeout)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()