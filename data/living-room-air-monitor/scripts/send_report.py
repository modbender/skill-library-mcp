#!/usr/bin/env python3
"""
Send air quality reports via email or WhatsApp.
"""

import os
import sys
import subprocess
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# Add scripts directory to path to import query functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import query_data

# Load contacts from shared CONTACTS.json
def load_contacts():
    """Load contact information from workspace CONTACTS.json."""
    contacts_path = os.path.expanduser("~/.openclaw/workspace/CONTACTS.json")
    try:
        with open(contacts_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ CONTACTS.json not found at {contacts_path}")
        print("   Create this file with your contact information:")
        print('   {"email": "your@email.com", "whatsapp": "+614xxxxxxxxx"}')
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in CONTACTS.json: {e}")
        sys.exit(1)

CONTACTS = load_contacts()
EMAIL = CONTACTS.get('email')
WHATSAPP_NUMBER = CONTACTS.get('whatsapp', '').replace('+61', '0')  # Convert +61415... to 0415...

if not EMAIL:
    print("❌ No email found in CONTACTS.json")
    sys.exit(1)

def generate_text_report(
    start_dt: datetime,
    end_dt: datetime,
    report_type: str = "interval"
) -> str:
    """
    Generate a text report for the specified time period.
    """
    readings = query_data.get_readings_by_interval(start_dt, end_dt)
    
    if not readings:
        return f"No air quality data available for the selected period."
    
    # Calculate averages
    avg_temp = sum(r['temperature'] for r in readings) / len(readings)
    avg_humidity = sum(r['humidity'] for r in readings) / len(readings)
    avg_pm25 = sum(r['pm25'] for r in readings) / len(readings)
    avg_co2 = sum(r['co2'] for r in readings) / len(readings)
    
    # Determine min/max values
    min_temp = min(r['temperature'] for r in readings)
    max_temp = max(r['temperature'] for r in readings)
    min_co2 = min(r['co2'] for r in readings)
    max_co2 = max(r['co2'] for r in readings)
    
    # Format report
    report = []
    report.append("=" * 50)
    report.append("🏠 LIVING ROOM AIR QUALITY REPORT")
    report.append("=" * 50)
    report.append(f"Period: {start_dt.strftime('%Y-%m-%d %H:%M')} to {end_dt.strftime('%Y-%m-%d %H:%M')}")
    report.append(f"Total readings: {len(readings)}")
    report.append("")
    report.append("📊 AVERAGES")
    report.append(f"  Temperature: {avg_temp:.1f}°C (range: {min_temp:.1f}°C - {max_temp:.1f}°C)")
    report.append(f"  Humidity:    {avg_humidity:.0f}%")
    report.append(f"  PM2.5:       {avg_pm25:.1f} µg/m³")
    report.append(f"  CO2:         {avg_co2:.0f} ppm (range: {min_co2:.0f} - {max_co2:.0f})")
    report.append("")
    
    # Air quality assessment
    report.append("🎯 AIR QUALITY ASSESSMENT")
    if avg_pm25 <= 12:
        report.append("  PM2.5: ✅ Good (≤12 µg/m³)")
    elif avg_pm25 <= 35:
        report.append("  PM2.5: ⚠️ Moderate (12.1-35 µg/m³)")
    else:
        report.append("  PM2.5: ❌ Unhealthy (>35 µg/m³)")
    
    if avg_co2 <= 1000:
        report.append("  CO2:   ✅ Good (≤1000 ppm)")
    elif avg_co2 <= 2000:
        report.append("  CO2:   ⚠️ Moderate (1001-2000 ppm)")
    else:
        report.append("  CO2:   ❌ Poor (>2000 ppm)")
    
    report.append("")
    report.append("📋 INDIVIDUAL READINGS")
    for r in readings:
        dt = datetime.fromisoformat(r['datetime'])
        report.append(f"  {dt.strftime('%Y-%m-%d %H:%M')}: "
                     f"{r['temperature']:.1f}°C, {r['humidity']:.0f}%, "
                     f"PM2.5={r['pm25']:.0f}, CO2={r['co2']:.0f}")
    
    report.append("")
    report.append("=" * 50)
    report.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 50)
    
    return "\n".join(report)

def send_email_report(
    subject: str,
    body: str,
    attachment_path: Optional[str] = None
) -> bool:
    """
    Send report via email using gog CLI.
    Note: gog doesn't support attachments directly - chart is referenced in text if available.
    """
    try:
        # Create temporary file for email body
        temp_body = "/tmp/air_quality_email_body.txt"
        
        # Append chart location if available
        email_body = body
        if attachment_path and os.path.exists(attachment_path):
            email_body += f"\n\n📊 Chart available at: {attachment_path}"
        
        with open(temp_body, 'w') as f:
            f.write(email_body)
        
        # Build gog command
        cmd = [
            "gog", "gmail", "send",
            "--to", EMAIL,
            "--subject", subject,
            "--body-file", temp_body
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Email sent successfully to {EMAIL}")
            return True
        else:
            print(f"❌ Failed to send email: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def send_whatsapp_report(
    message: str,
    attachment_path: Optional[str] = None
) -> bool:
    """
    Send report via WhatsApp using wacli CLI.
    """
    try:
        # Use full international format from CONTACTS.json
        whatsapp_to = CONTACTS.get('whatsapp', '')
        if not whatsapp_to.startswith('+'):
            print("❌ WhatsApp number should be in international format (+61415xxxxxx)")
            return False
        
        # Send message first
        cmd = ["wacli", "send", "text", "--to", whatsapp_to, "--message", message]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to send WhatsApp message: {result.stderr}")
            return False
        
        print(f"✅ WhatsApp message sent to {whatsapp_to}")
        
        # Send attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            cmd = ["wacli", "send", "file", "--to", whatsapp_to, "--file", attachment_path, "--caption", "Air Quality Chart"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ WhatsApp attachment sent")
                return True
            else:
                print(f"⚠️ Message sent but attachment failed: {result.stderr}")
                return True  # Partial success
        
        return True
        
    except Exception as e:
        print(f"❌ Error sending WhatsApp message: {e}")
        return False

def send_report(
    start_dt: datetime,
    end_dt: datetime,
    channel: str = "email",
    include_chart: bool = True,
    chart_path: Optional[str] = None
) -> bool:
    """
    Send a complete air quality report via the specified channel.
    
    Args:
        start_dt: Start of reporting period
        end_dt: End of reporting period
        channel: 'email' or 'whatsapp'
        include_chart: Whether to include a chart
        chart_path: Path to pre-generated chart (if None, will generate)
    """
    # Generate report text
    report_text = generate_text_report(start_dt, end_dt)
    
    # Generate chart if needed
    if include_chart and chart_path is None:
        from generate_chart import generate_chart
        period_name = f"{start_dt.strftime('%Y-%m-%d')}_to_{end_dt.strftime('%Y-%m-%d')}"
        chart_path = f"/tmp/air_charts/report_{period_name}.png"
        chart_path = generate_chart(start_dt, end_dt, chart_path, 
                                    f"Air Quality Report: {period_name}")
    
    # Send via appropriate channel
    if channel == "email":
        subject = f"Air Quality Report: {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}"
        return send_email_report(subject, report_text, chart_path)
    
    elif channel == "whatsapp":
        return send_whatsapp_report(report_text, chart_path)
    
    else:
        print(f"❌ Unknown channel: {channel}")
        return False

# Convenience functions for common reports
def send_daily_report(date: datetime, channel: str = "email"):
    """Send report for a specific day."""
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return send_report(start, end, channel)

def send_weekly_report(end_date: datetime, channel: str = "email"):
    """Send report for the last 7 days."""
    end = end_date.replace(hour=23, minute=59, second=59)
    start = end - timedelta(days=7)
    return send_report(start, end, channel)

def send_monthly_report(year: int, month: int, channel: str = "email"):
    """Send report for a specific month."""
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    return send_report(start, end, channel)

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Send air quality reports')
    parser.add_argument('--day', type=str, help='Send report for a specific day (YYYY-MM-DD)')
    parser.add_argument('--week', type=str, help='Send weekly report ending on date (YYYY-MM-DD)')
    parser.add_argument('--month', type=str, help='Send report for a specific month (YYYY-MM)')
    parser.add_argument('--channel', type=str, choices=['email', 'whatsapp'], 
                        default='email', help='Channel to send via')
    parser.add_argument('--no-chart', action='store_true', help='Exclude chart from report')
    
    args = parser.parse_args()
    
    if args.day:
        date = datetime.strptime(args.day, '%Y-%m-%d')
        send_daily_report(date, args.channel)
    
    elif args.week:
        date = datetime.strptime(args.week, '%Y-%m-%d')
        send_weekly_report(date, args.channel)
    
    elif args.month:
        year, month = map(int, args.month.split('-'))
        send_monthly_report(year, month, args.channel)
    
    else:
        # Send today's report
        send_daily_report(datetime.now(), args.channel)
