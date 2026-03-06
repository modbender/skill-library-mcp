#!/usr/bin/env python3
"""
Mailbox Size Estimation Script
Estimates mailbox size and message counts via IMAP
Usage: python3 mailbox-size.py [--server SERVER] [--username USER] [--password PASS]
"""

import imaplib
import argparse
import sys
import ssl
import socket
import re
from getpass import getpass
from datetime import datetime, timedelta

def format_bytes(bytes_count):
    """Format bytes in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"

def estimate_mailbox_size(server, port, username, password, use_ssl=True, timeout=30):
    """Connect to mailbox and estimate size"""
    
    print(f"Connecting to {server}:{port} as {username}")
    print("-" * 60)
    
    try:
        # Set socket timeout
        socket.setdefaulttimeout(timeout)
        
        # Create IMAP connection
        if use_ssl:
            imap = imaplib.IMAP4_SSL(server, port)
        else:
            imap = imaplib.IMAP4(server, port)
        
        # Login
        imap.login(username, password)
        print("✅ Connected and authenticated successfully\n")
        
        # Get list of all mailboxes
        result, mailboxes = imap.list()
        if result != 'OK':
            print("❌ Failed to list mailboxes")
            return False
        
        total_messages = 0
        total_size_estimate = 0
        folder_stats = []
        
        print(f"📁 Found {len(mailboxes)} folders:")
        print()
        
        for mailbox_line in mailboxes:
            try:
                # Parse mailbox line to extract folder name
                mailbox_decoded = mailbox_line.decode('utf-8')
                # Extract folder name (handle quoted folder names)
                match = re.search(r'"([^"]*)"$|([^\s]+)$', mailbox_decoded)
                if match:
                    folder_name = match.group(1) or match.group(2)
                else:
                    continue
                
                # Select the folder
                try:
                    result, data = imap.select(f'"{folder_name}"', readonly=True)
                    if result != 'OK':
                        print(f"⚠️  Skipped {folder_name} (access denied)")
                        continue
                    
                    # Get message count
                    message_count = int(data[0]) if data[0] else 0
                    
                    if message_count == 0:
                        print(f"📂 {folder_name:<30} {message_count:>6} messages")
                        folder_stats.append((folder_name, message_count, 0))
                        continue
                    
                    # Sample a few messages to estimate average size
                    sample_size = min(10, message_count)
                    sample_total_size = 0
                    
                    if sample_size > 0:
                        # Get recent message IDs for sampling
                        result, data = imap.search(None, 'ALL')
                        if result == 'OK' and data[0]:
                            message_ids = data[0].split()
                            
                            # Sample from different parts of the mailbox
                            sample_indices = []
                            if len(message_ids) > sample_size:
                                step = len(message_ids) // sample_size
                                sample_indices = [i * step for i in range(sample_size)]
                            else:
                                sample_indices = list(range(len(message_ids)))
                            
                            for idx in sample_indices[:sample_size]:
                                if idx < len(message_ids):
                                    msg_id = message_ids[idx]
                                    try:
                                        result, data = imap.fetch(msg_id, 'RFC822.SIZE')
                                        if result == 'OK' and data[0]:
                                            # Parse size from response
                                            size_match = re.search(r'RFC822\.SIZE (\d+)', data[0].decode('utf-8'))
                                            if size_match:
                                                sample_total_size += int(size_match.group(1))
                                    except:
                                        continue
                    
                    # Calculate average and estimate total
                    if sample_size > 0 and sample_total_size > 0:
                        avg_size = sample_total_size / sample_size
                        folder_size_estimate = int(avg_size * message_count)
                    else:
                        # Fallback estimate: 50KB average per message
                        avg_size = 50 * 1024
                        folder_size_estimate = int(avg_size * message_count)
                    
                    total_messages += message_count
                    total_size_estimate += folder_size_estimate
                    folder_stats.append((folder_name, message_count, folder_size_estimate))
                    
                    print(f"📂 {folder_name:<30} {message_count:>6} messages  {format_bytes(folder_size_estimate):>8}")
                    
                except Exception as e:
                    print(f"⚠️  Error processing {folder_name}: {str(e)[:50]}")
                    continue
                    
            except Exception as e:
                print(f"⚠️  Error parsing mailbox line: {str(e)[:50]}")
                continue
        
        print("\n" + "=" * 60)
        print("📊 MAILBOX SUMMARY")
        print("=" * 60)
        print(f"Total folders scanned: {len(folder_stats)}")
        print(f"Total messages: {total_messages:,}")
        print(f"Estimated total size: {format_bytes(total_size_estimate)}")
        
        if total_messages > 0:
            avg_msg_size = total_size_estimate / total_messages
            print(f"Average message size: {format_bytes(avg_msg_size)}")
        
        print("\n📈 LARGEST FOLDERS:")
        # Sort by size and show top 5
        folder_stats.sort(key=lambda x: x[2], reverse=True)
        for i, (folder, count, size) in enumerate(folder_stats[:5]):
            print(f"{i+1}. {folder:<25} {count:>6} msgs  {format_bytes(size):>8}")
        
        # Migration time estimates
        print("\n⏱️  MIGRATION TIME ESTIMATES:")
        print("(Based on typical IMAP transfer rates)")
        
        # Estimates based on common speeds
        speed_estimates = [
            ("Fast IMAP (1000 msg/hour)", 1000),
            ("Medium IMAP (500 msg/hour)", 500),
            ("Slow IMAP (200 msg/hour)", 200),
        ]
        
        for desc, msgs_per_hour in speed_estimates:
            if total_messages > 0:
                hours = total_messages / msgs_per_hour
                if hours < 1:
                    time_str = f"{hours * 60:.0f} minutes"
                elif hours < 24:
                    time_str = f"{hours:.1f} hours"
                else:
                    days = hours / 24
                    time_str = f"{days:.1f} days"
                print(f"  {desc:<25} {time_str}")
        
        # Storage requirements
        print("\n💾 STORAGE REQUIREMENTS:")
        print(f"Source mailbox: {format_bytes(total_size_estimate)}")
        print(f"Backup space needed: {format_bytes(total_size_estimate * 1.2)} (with 20% buffer)")
        print(f"Temporary space: {format_bytes(total_size_estimate * 0.5)} (for staging)")
        
        # Age analysis
        print("\n📅 ANALYZING MESSAGE DATES...")
        try:
            imap.select('INBOX', readonly=True)
            
            # Check for very old messages (5+ years)
            old_date = (datetime.now() - timedelta(days=5*365)).strftime("%d-%b-%Y")
            result, data = imap.search(None, f'BEFORE {old_date}')
            old_count = len(data[0].split()) if result == 'OK' and data[0] else 0
            
            # Check for recent messages (last 30 days)  
            recent_date = (datetime.now() - timedelta(days=30)).strftime("%d-%b-%Y")
            result, data = imap.search(None, f'SINCE {recent_date}')
            recent_count = len(data[0].split()) if result == 'OK' and data[0] else 0
            
            print(f"Messages older than 5 years: {old_count:,}")
            print(f"Messages from last 30 days: {recent_count:,}")
            
            if old_count > 0:
                print("\n💡 Consider archiving very old messages to speed up migration")
            
        except Exception as e:
            print(f"⚠️  Could not analyze message dates: {str(e)[:50]}")
        
        # Logout
        imap.logout()
        print("\n✅ Analysis complete!")
        return True
        
    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP Error: {e}")
        return False
    except ssl.SSLError as e:
        print(f"❌ SSL Error: {e}")
        return False
    except socket.timeout:
        print(f"❌ Connection timeout after {timeout} seconds")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def get_provider_presets():
    """Return common provider presets"""
    return {
        'gmail': {'server': 'imap.gmail.com', 'port': 993},
        'yahoo': {'server': 'imap.mail.yahoo.com', 'port': 993},
        'outlook': {'server': 'outlook.office365.com', 'port': 993},
        'icloud': {'server': 'imap.mail.me.com', 'port': 993},
        'zoho': {'server': 'imap.zoho.com', 'port': 993}
    }

def main():
    parser = argparse.ArgumentParser(
        description='Estimate mailbox size via IMAP',
        epilog='Examples:\n'
               '  python3 mailbox-size.py gmail\n'
               '  python3 mailbox-size.py --server imap.gmail.com --username user@gmail.com',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('preset', nargs='?', help='Provider preset (gmail, yahoo, outlook, icloud, zoho)')
    parser.add_argument('--server', help='IMAP server address')
    parser.add_argument('--port', type=int, default=993, help='IMAP port (default: 993)')
    parser.add_argument('--username', help='Email username/address')
    parser.add_argument('--password', help='Password (will prompt if not provided)')
    parser.add_argument('--no-ssl', action='store_true', help='Disable SSL/TLS encryption')
    parser.add_argument('--timeout', type=int, default=60, help='Connection timeout in seconds')
    
    args = parser.parse_args()
    
    # Get provider preset if specified
    presets = get_provider_presets()
    if args.preset and args.preset in presets:
        preset = presets[args.preset]
        server = args.server or preset['server']
        port = args.port if args.server else preset['port']
    else:
        server = args.server
        port = args.port
        
        if not server:
            print("Error: Server address required")
            print("Use --server SERVER or choose a preset (gmail, yahoo, outlook, icloud, zoho)")
            sys.exit(1)
    
    # Get username
    username = args.username
    if not username:
        username = input("Email address: ").strip()
    
    # Get password
    password = args.password
    if not password:
        password = getpass("Password (or app password): ")
    
    use_ssl = not args.no_ssl
    
    # Run the analysis
    success = estimate_mailbox_size(server, port, username, password, use_ssl, args.timeout)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()