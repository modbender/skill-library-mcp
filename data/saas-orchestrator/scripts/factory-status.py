#!/usr/bin/env python3
"""
🦞 JUNAI's SAAS Factory Status Checker
Quick overview of all active projects and their health
"""

import json
import os
from datetime import datetime, timedelta

def get_project_status():
    """Get current status of all SAAS projects"""
    
    # Mock data - in real implementation, this would read from database/files
    projects = [
        {
            "name": "Construction Project Manager",
            "status": "Research Phase",
            "start_date": "2024-02-15",
            "target_mrr": 1000,
            "current_mrr": 0,
            "next_action": "Complete market research",
            "risk_level": "medium",
            "notes": "High potential, competitive market"
        },
        {
            "name": "Freelance Invoice Generator",
            "status": "MVP Development",
            "start_date": "2024-02-10",
            "target_mrr": 1000,
            "current_mrr": 250,
            "next_action": "Complete payment integration",
            "risk_level": "low",
            "notes": "On track for $1000 MRR by month 3"
        },
        {
            "name": "Real Estate Lead Gen",
            "status": "Post-Launch",
            "start_date": "2024-01-20",
            "target_mrr": 1000,
            "current_mrr": 1800,
            "next_action": "Optimize pricing and add annual plans",
            "risk_level": "low",
            "notes": "Exceeded target! Focus on scaling"
        },
        {
            "name": "Restaurant Analytics",
            "status": "Pivot/Kill Decision",
            "start_date": "2024-01-05",
            "target_mrr": 1000,
            "current_mrr": 150,
            "next_action": "Make kill decision this week",
            "risk_level": "high",
            "notes": "Flat growth for 2 months, market too small"
        }
    ]
    
    return projects

def analyze_portfolio_health(projects):
    """Analyze overall portfolio health"""
    
    total_target_mrr = sum(p["target_mrr"] for p in projects)
    total_current_mrr = sum(p["current_mrr"] for p in projects)
    
    status_counts = {}
    risk_counts = {"low": 0, "medium": 0, "high": 0}
    
    for project in projects:
        status = project["status"]
        risk = project["risk_level"]
        status_counts[status] = status_counts.get(status, 0) + 1
        risk_counts[risk] += 1
    
    return {
        "total_projects": len(projects),
        "total_target_mrr": total_target_mrr,
        "total_current_mrr": total_current_mrr,
        "portfolio_mrr_percentage": (total_current_mrr / total_target_mrr * 100) if total_target_mrr > 0 else 0,
        "status_breakdown": status_counts,
        "risk_breakdown": risk_counts
    }

def print_status_report():
    """Print comprehensive factory status report"""
    
    print("🦞 JUNAI's SAAS Factory Status Report")
    print("=" * 50)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    projects = get_project_status()
    portfolio = analyze_portfolio_health(projects)
    
    # Portfolio Overview
    print("📊 PORTFOLIO OVERVIEW")
    print("-" * 30)
    print(f"Total Active Projects: {portfolio['total_projects']}")
    print(f"Target MRR: ${portfolio['total_target_mrr']:,}")
    print(f"Current MRR: ${portfolio['total_current_mrr']:,}")
    print(f"Portfolio Progress: {portfolio['portfolio_mrr_percentage']:.1f}%")
    print()
    
    # Status Breakdown
    print("🏭 PROJECT STATUS BREAKDOWN")
    print("-" * 30)
    for status, count in portfolio['status_breakdown'].items():
        print(f"{status}: {count} projects")
    print()
    
    # Risk Assessment
    print("⚠️  RISK ASSESSMENT")
    print("-" * 30)
    for risk, count in portfolio['risk_breakdown'].items():
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        print(f"{risk_emoji[risk]} {risk.upper()} RISK: {count} projects")
    print()
    
    # Individual Project Status
    print("📋 INDIVIDUAL PROJECT STATUS")
    print("-" * 30)
    
    for project in projects:
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        status_emoji = {
            "Research Phase": "🔍",
            "MVP Development": "🏗️",
            "Post-Launch": "🚀",
            "Pivot/Kill Decision": "💀"
        }
        
        print(f"{status_emoji.get(project['status'], '📊')} {project['name']}")
        print(f"   Status: {project['status']}")
        print(f"   MRR: ${project['current_mrr']} / ${project['target_mrr']} ({project['current_mrr']/project['target_mrr']*100:.1f}%)")
        print(f"   {risk_emoji[project['risk_level']]} Risk: {project['risk_level']}")
        print(f"   Next: {project['next_action']}")
        print(f"   Notes: {project['notes']}")
        print()
    
    # Action Items
    print("🎯 IMMEDIATE ACTION ITEMS")
    print("-" * 30)
    
    urgent_actions = []
    for project in projects:
        if project["risk_level"] == "high":
            urgent_actions.append(f"🔴 URGENT: {project['name']} - {project['next_action']}")
        elif project["status"] == "Post-Launch" and project["current_mrr"] >= project["target_mrr"]:
            urgent_actions.append(f"🚀 SCALE: {project['name']} - Exceeded target, focus on growth")
        elif project["status"] == "MVP Development":
            urgent_actions.append(f"🏗️  BUILD: {project['name']} - {project['next_action']}")
    
    if urgent_actions:
        for action in urgent_actions:
            print(action)
    else:
        print("✅ All projects on track - no urgent actions needed")
    
    print()
    print("🦞 Next factory review in 30 minutes")
    print("🦞 Ready for 👑 JUN's strategic direction!")

def save_status_report():
    """Save status report to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"factory_status_{timestamp}.txt"
    
    # Capture the print output
    import io
    from contextlib import redirect_stdout
    
    f = io.StringIO()
    with redirect_stdout(f):
        print_status_report()
    
    report_content = f.getvalue()
    
    with open(filename, 'w') as file:
        file.write(report_content)
    
    print(f"🦞 Status report saved to {filename}")

if __name__ == "__main__":
    print_status_report()
    save_status_report()