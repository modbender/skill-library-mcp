"""
Professional Bounty Scanner for Autonomous Agents
Version: 1.0.0
Description: Efficiently discovers, filters, and scores bounties from agentic marketplaces.
Designed for high-performance agents seeking optimal task-to-reward ratios.
"""

import json
import subprocess
import re
from datetime import datetime

class BountyScanner:
    def __init__(self, acp_cli_path="npx tsx /root/.openclaw/workspace/skills/virtuals-protocol-acp/bin/acp.ts"):
        self.acp_cli_path = acp_cli_path

    def fetch_bounties(self, query="coding"):
        """Fetches active bounties from the marketplace using the ACP bridge."""
        try:
            cmd = f"{self.acp_cli_path} browse \"{query}\" --json"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {"status": "error", "message": result.stderr}
            
            data = json.loads(result.stdout)
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def score_task(self, task, capabilities):
        """
        Scores a task based on budget, SLA, and alignment with agent capabilities.
        Score range: 0-100
        """
        score = 0
        
        # 1. Budget Weight (40%)
        price = task.get('price', 0)
        if price >= 50: score += 40
        elif price >= 10: score += 30
        elif price >= 1: score += 15
        else: score += 5

        # 2. SLA/Urgency Weight (20%)
        sla = task.get('slaMinutes', 60)
        if sla <= 15: score += 20  # High priority / Fast turnaround
        elif sla <= 60: score += 10
        else: score += 5

        # 3. Capability Alignment (40%)
        description = task.get('description', '').lower()
        match_count = 0
        for cap in capabilities:
            if cap.lower() in description:
                match_count += 1
        
        alignment_score = (match_count / len(capabilities)) * 40 if capabilities else 0
        score += alignment_score

        return round(min(score, 100), 2)

    def scan_and_rank(self, query="security", capabilities=["audit", "code", "verify"]):
        """Main workflow: fetch, score, and rank opportunities."""
        fetch_result = self.fetch_bounties(query)
        
        if fetch_result['status'] == "error":
            return fetch_result

        agents = fetch_result['data']
        opportunities = []

        for agent in agents:
            for job in agent.get('jobs', []):
                score = self.score_task(job, capabilities)
                opportunities.append({
                    "agent_name": agent.get('name'),
                    "job_name": job.get('name'),
                    "price": job.get('price'),
                    "score": score,
                    "description": job.get('description'),
                    "requirements": job.get('requirement')
                })

        # Rank by score descending
        ranked = sorted(opportunities, key=lambda x: x['score'], reverse=True)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "count": len(ranked),
            "top_picks": ranked[:5]
        }

if __name__ == "__main__":
    scanner = BountyScanner()
    # Example: Scan for security jobs
    results = scanner.scan_and_rank("security", ["audit", "solidity", "code review"])
    print(json.dumps(results, indent=2))
