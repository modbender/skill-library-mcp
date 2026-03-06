#!/usr/bin/env python3
"""
Email Intelligence Classifier
Analyzes email inbox health using weather metaphors, classification, and debt scoring.
"""

import json
import subprocess
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import re


def run_himalaya_command(folder: str, page_size: int = 200) -> List[Dict[str, Any]]:
    """Run himalaya command and return parsed JSON output."""
    try:
        # Use list form to avoid shell injection via folder names
        cmd = [
            "himalaya", "envelope", "list",
            "-f", str(folder),
            "--page-size", str(int(page_size)),
            "-o", "json"
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            stderr=subprocess.DEVNULL  # Ignore stderr warnings
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            return []
            
        return json.loads(result.stdout.strip())
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        return []


def classify_email(email: Dict[str, Any]) -> str:
    """Classify an email into one of: automated, newsletter, notification, human."""
    sender_addr = email.get('from', {}).get('addr', '').lower()
    sender_name = (email.get('from', {}).get('name') or '').lower()
    subject = email.get('subject', '').lower()
    
    # Automated detection
    automated_patterns = [
        'noreply', 'no-reply', 'donotreply', 'do-not-reply',
        'notifications@', 'alerts@', 'automated@'
    ]
    
    subject_patterns = [
        'unsubscribe', 'automatic', 'auto-generated'
    ]
    
    if any(pattern in sender_addr or pattern in sender_name for pattern in automated_patterns):
        return 'automated'
    if any(pattern in subject for pattern in subject_patterns):
        return 'automated'
    
    # Newsletter detection
    newsletter_patterns = [
        'substack.com', 'email.', 'marketing.', 'updates@',
        'newsletter@', 'campaigns@'
    ]
    
    newsletter_subjects = [
        'newsletter', 'digest', 'weekly', 'monthly', 'roundup'
    ]
    
    if any(pattern in sender_addr for pattern in newsletter_patterns):
        return 'newsletter'
    if any(pattern in subject for pattern in newsletter_subjects):
        return 'newsletter'
    
    # Notification detection
    service_patterns = [
        'github', 'slack', 'jira', 'linear', 'aws', 'amazon',
        'google', 'microsoft', 'apple', 'stripe', 'paypal',
        'zoom', 'calendar', 'notification'
    ]
    
    if any(pattern in sender_addr or pattern in sender_name for pattern in service_patterns):
        return 'notification'
    
    # Everything else is human
    return 'human'


def get_email_age_days(email_date: str) -> int:
    """Calculate age of email in days."""
    try:
        email_dt = datetime.fromisoformat(email_date.replace('Z', '+00:00'))
        now = datetime.now(email_dt.tzinfo)
        return max(0, (now - email_dt).days)
    except:
        return 0


def determine_weather(human_count: int) -> Dict[str, str]:
    """Determine inbox weather based on human email count needing response."""
    weather_levels = {
        'calm': {
            'emoji': '🌊',
            'description': 'Calm Seas - Your inbox is peaceful and manageable'
        },
        'breeze': {
            'emoji': '🍃',
            'description': 'Light Breeze - A few emails need attention, but nothing urgent'
        },
        'choppy': {
            'emoji': '🌬️',
            'description': 'Choppy Waters - Multiple emails require responses'
        },
        'advisory': {
            'emoji': '⛵',
            'description': 'Small Craft Advisory - Many people are waiting for your replies'
        },
        'storm': {
            'emoji': '⛈️',
            'description': 'Storm Warning - Your inbox is overwhelming and needs immediate attention'
        }
    }
    
    if human_count <= 2:
        level = 'calm'
    elif human_count <= 5:
        level = 'breeze'
    elif human_count <= 10:
        level = 'choppy'
    elif human_count <= 20:
        level = 'advisory'
    else:
        level = 'storm'
    
    return {
        'level': level,
        'humanCount': human_count,
        **weather_levels[level]
    }


def calculate_debt_score(inbox_emails: List[Dict[str, Any]]) -> int:
    """Calculate email debt score (0-100) based on unseen human emails."""
    score = 0
    
    for email in inbox_emails:
        # Check if unseen and human
        flags = email.get('flags', [])
        is_unseen = 'Seen' not in flags
        
        if is_unseen and classify_email(email) == 'human':
            age_days = get_email_age_days(email.get('date', ''))
            
            if age_days < 1:
                score += 1
            elif age_days <= 3:
                score += 3
            elif age_days <= 7:
                score += 5
            else:
                score += 10
    
    return min(score, 100)  # Cap at 100


def generate_ghost_report(inbox_emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate ghost report of people waiting for replies."""
    ghosts = []
    
    for email in inbox_emails:
        flags = email.get('flags', [])
        is_unseen = 'Seen' not in flags
        
        if is_unseen and classify_email(email) == 'human':
            sender = email.get('from', {})
            age_days = get_email_age_days(email.get('date', ''))
            
            ghosts.append({
                'senderName': sender.get('name') or sender.get('addr', '').split('@')[0],
                'senderEmail': sender.get('addr', ''),
                'subject': email.get('subject', ''),
                'date': email.get('date', ''),
                'daysWaiting': age_days
            })
    
    # Sort by oldest first and return top 5
    ghosts.sort(key=lambda x: x['daysWaiting'], reverse=True)
    return ghosts[:5]


def calculate_signal_noise_ratio(categories: Dict[str, int]) -> Dict[str, Any]:
    """Calculate signal-to-noise ratio."""
    total = sum(categories.values())
    
    if total == 0:
        return {'ratio': 0, 'percentage': '0%'}
    
    ratio = categories['human'] / total
    percentage = round(ratio * 100)
    
    return {'ratio': ratio, 'percentage': f'{percentage}%'}


def calculate_time_cost(categories: Dict[str, int]) -> Dict[str, Any]:
    """Calculate estimated time cost in minutes."""
    # Time estimates: human=3min, notification=0.5min, newsletter=1min, automated=0min
    minutes = (categories['human'] * 3 + 
               categories['notification'] * 0.5 + 
               categories['newsletter'] * 1 + 
               categories['automated'] * 0)
    
    rounded = round(minutes)
    
    if rounded < 60:
        formatted = f'{rounded} minutes'
    else:
        hours = rounded // 60
        remaining_minutes = rounded % 60
        if remaining_minutes > 0:
            formatted = f'{hours}h {remaining_minutes}m'
        else:
            formatted = f'{hours}h'
    
    return {'minutes': rounded, 'formatted': formatted}


def discover_folders() -> Dict[str, str]:
    """Auto-discover email folders. Returns dict with 'inbox' and 'archive' keys."""
    folders = {'inbox': 'INBOX', 'archive': None, 'sent': None, 'junk': None}
    try:
        result = subprocess.run(
            ["himalaya", "folder", "list", "-o", "json"],
            capture_output=True, text=True, timeout=10, stderr=subprocess.DEVNULL
        )
        if result.returncode == 0 and result.stdout.strip():
            folder_list = json.loads(result.stdout.strip())
            names = [f.get('name', '') for f in folder_list]
            
            # Find inbox (case-insensitive)
            for n in names:
                if n.lower() == 'inbox':
                    folders['inbox'] = n
                    break
            
            # Find archive folder
            archive_patterns = ['archive', 'all mail', '[gmail]/all mail', 'archived']
            for n in names:
                if n.lower() in archive_patterns:
                    folders['archive'] = n
                    break
            
            # Find sent folder
            sent_patterns = ['sent', 'sent messages', 'sent mail', '[gmail]/sent mail']
            for n in names:
                if n.lower() in sent_patterns:
                    folders['sent'] = n
                    break
            
            # Find junk/spam folder
            junk_patterns = ['junk', 'spam', '[gmail]/spam']
            for n in names:
                if n.lower() in junk_patterns:
                    folders['junk'] = n
                    break
    except Exception:
        pass
    return folders


def analyze_emails(days: int = 7) -> Dict[str, Any]:
    """Analyze emails and return intelligence data."""
    # Auto-discover folders
    folders = discover_folders()
    
    # Get emails from discovered folders
    inbox_emails = run_himalaya_command(folders['inbox'], 100)
    archive_emails = run_himalaya_command(folders['archive'], 200) if folders['archive'] else []
    
    all_emails = inbox_emails + archive_emails
    
    # Filter for recent emails (last N days)
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_emails = []
    
    for email in all_emails:
        try:
            email_date = datetime.fromisoformat(email.get('date', '').replace('Z', '+00:00'))
            if email_date >= cutoff_date.replace(tzinfo=email_date.tzinfo):
                recent_emails.append(email)
        except:
            continue
    
    # Classify emails
    categories = {'automated': 0, 'newsletter': 0, 'notification': 0, 'human': 0}
    
    for email in recent_emails:
        category = classify_email(email)
        categories[category] += 1
    
    # Count human emails in INBOX needing response
    inbox_human_count = len([
        email for email in inbox_emails 
        if 'Seen' not in email.get('flags', []) and classify_email(email) == 'human'
    ])
    
    # Generate analysis
    weather = determine_weather(inbox_human_count)
    debt_score = calculate_debt_score(inbox_emails)
    ghost_report = generate_ghost_report(inbox_emails)
    signal_noise_ratio = calculate_signal_noise_ratio(categories)
    time_cost = calculate_time_cost(categories)
    
    return {
        'weather': weather,
        'categories': categories,
        'debtScore': debt_score,
        'ghostReport': ghost_report,
        'signalNoiseRatio': signal_noise_ratio,
        'timeCost': time_cost,
        'totalEmails': len(all_emails),
        'recentEmails': len(recent_emails),
        'timestamp': datetime.now().isoformat()
    }


def format_text_output(data: Dict[str, Any]) -> str:
    """Format data as human-readable text."""
    weather = data['weather']
    categories = data['categories']
    
    output = []
    output.append("📧 EMAIL INTELLIGENCE REPORT")
    output.append("=" * 50)
    output.append("")
    
    # Weather
    output.append(f"🌤️  INBOX WEATHER: {weather['emoji']} {weather['level'].upper()}")
    output.append(f"   {weather['description']}")
    output.append(f"   👥 {weather['humanCount']} humans need responses")
    output.append("")
    
    # Debt Score
    debt_score = data['debtScore']
    debt_status = "🟢 Great!" if debt_score <= 30 else "🟡 Getting busy" if debt_score <= 60 else "🔴 High debt!"
    output.append(f"⚖️  EMAIL DEBT SCORE: {debt_score}/100 {debt_status}")
    output.append("")
    
    # Signal vs Noise
    signal_ratio = data['signalNoiseRatio']['percentage']
    output.append(f"📊 SIGNAL vs NOISE: {signal_ratio} signal")
    output.append(f"   📤 Human: {categories['human']}")
    output.append(f"   🤖 Automated: {categories['automated']}")
    output.append(f"   📰 Newsletter: {categories['newsletter']}")
    output.append(f"   🔔 Notification: {categories['notification']}")
    output.append("")
    
    # Time Cost
    time_cost = data['timeCost']['formatted']
    output.append(f"⏰ TIME INVESTMENT: ~{time_cost} needed")
    output.append("")
    
    # Ghost Report
    if data['ghostReport']:
        output.append("👻 GHOST REPORT - People you're ignoring:")
        for ghost in data['ghostReport']:
            days = ghost['daysWaiting']
            urgent = "🚨" if days > 3 else ""
            output.append(f"   {urgent} {ghost['senderName']} - {days}d waiting")
            output.append(f"      \"{ghost['subject']}\"")
        output.append("")
    
    # Summary
    output.append(f"📈 SUMMARY: {data['recentEmails']} recent emails, {data['totalEmails']} total")
    output.append(f"⏱️  Generated: {data['timestamp']}")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='Analyze email inbox intelligence')
    parser.add_argument('--days', type=int, default=7, help='Days to look back for recent emails')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Output format')
    
    args = parser.parse_args()
    
    try:
        data = analyze_emails(args.days)
        
        if args.format == 'json':
            print(json.dumps(data, indent=2))
        else:
            print(format_text_output(data))
            
    except Exception as e:
        print(f"Error analyzing emails: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()