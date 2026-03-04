#!/usr/bin/env python3
"""
Generate a morning briefing from Whoop data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from whoop_client import WhoopClient

def get_morning_briefing():
    """Generate morning briefing"""
    client = WhoopClient()
    
    # Get recent recovery, cycle, and sleep data
    recovery_data = client.get_recovery(limit=1)
    cycle_data = client.get_cycle(limit=1)
    sleep_data = client.get_sleep(limit=1)
    
    if not recovery_data.get('records') or not cycle_data.get('records'):
        return "❌ No Whoop data available yet. Make sure your Whoop is synced!"
    
    recovery = recovery_data['records'][0]
    cycle = cycle_data['records'][0]
    sleep = sleep_data['records'][0] if sleep_data.get('records') else None
    
    # Extract recovery metrics
    rec_score = recovery['score']
    recovery_pct = rec_score.get('recovery_score', 0)
    hrv = rec_score.get('hrv_rmssd_milli', 0)
    rhr = rec_score.get('resting_heart_rate', 0)
    spo2 = rec_score.get('spo2_percentage', 0)
    skin_temp = rec_score.get('skin_temp_celsius', 0)
    
    # Extract strain metrics
    strain_score = cycle['score']
    strain = strain_score.get('strain', 0)
    calories = strain_score.get('kilojoule', 0) / 4.184  # Convert to kcal
    avg_hr = strain_score.get('average_heart_rate', 0)
    max_hr = strain_score.get('max_heart_rate', 0)
    
    # Determine recovery status
    if recovery_pct >= 67:
        rec_status = "🟢 GREEN"
        rec_msg = "Your body is well-recovered and ready for high strain!"
    elif recovery_pct >= 34:
        rec_status = "🟡 YELLOW"
        rec_msg = "Moderate recovery. Go for moderate intensity today."
    else:
        rec_status = "🔴 RED"
        rec_msg = "Your body needs rest. Prioritize recovery today."
    
    # Sleep metrics
    sleep_info = ""
    if sleep:
        sleep_score = sleep.get('score', {})
        stage_summary = sleep_score.get('stage_summary', {})
        total_bed = stage_summary.get('total_in_bed_time_milli', 0)
        hours = total_bed / (1000 * 60 * 60) if total_bed else 0
        perf = sleep_score.get('sleep_performance_percentage', 0)
        quality = sleep_score.get('sleep_quality_percentage', 0)
        
        sleep_info = f"""
**😴 Last Night's Sleep:**
• Duration: {hours:.1f} hours
• Performance: {perf:.0f}%
• Quality: {quality:.0f}%
"""
    
    # Build briefing
    briefing = f"""
🔥 **Good Morning! Here's Your Whoop Briefing**

**🔋 RECOVERY: {recovery_pct:.0f}%** {rec_status}
{rec_msg}

**📊 Key Metrics:**
• HRV: {hrv:.1f} ms
• Resting HR: {rhr:.0f} bpm
• SpO2: {spo2:.1f}%
• Skin Temp: {skin_temp:.1f}°C
{sleep_info}
**💪 Yesterday's Strain: {strain:.1f}**
• Calories: {calories:.0f} kcal
• Avg HR: {avg_hr:.0f} bpm
• Max HR: {max_hr:.0f} bpm

**💡 Recommendation:**
"""
    
    # Add recommendation based on recovery
    if recovery_pct >= 67:
        briefing += "Perfect day for a challenging workout or important meeting. Your body is primed!"
    elif recovery_pct >= 50:
        briefing += "Solid recovery. You can handle moderate intensity work and exercise."
    elif recovery_pct >= 34:
        briefing += "Recovery is adequate but not optimal. Consider lighter activities."
    else:
        briefing += "Focus on recovery today - light movement, good nutrition, and extra sleep tonight."
    
    return briefing

if __name__ == "__main__":
    try:
        print(get_morning_briefing())
    except Exception as e:
        print(f"Error generating briefing: {e}", file=sys.stderr)
        sys.exit(1)
