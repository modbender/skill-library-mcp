#!/usr/bin/env python3
"""
GitHub Bounty Hunter - Autonomous bounty discovery and application
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import List, Dict, Optional

class GitHubBountyHunter:
    def __init__(self, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        self.state_file = "bounty_state.json"
        self.state = self.load_state()
        
    def load_config(self, path: str) -> dict:
        """Load configuration"""
        default_config = {
            "skills": ["writing", "documentation", "python", "translation"],
            "min_reward": 10,
            "max_competition": 15,
            "check_interval": 30,
            "platforms": ["github"]
        }
        
        if os.path.exists(path):
            with open(path) as f:
                return {**default_config, **json.load(f)}
        return default_config
    
    def load_state(self) -> dict:
        """Load state"""
        if os.path.exists(self.state_file):
            with open(self.state_file) as f:
                return json.load(f)
        return {
            "seen_bounties": [],
            "applied_bounties": [],
            "completed_bounties": [],
            "total_earned": 0
        }
    
    def save_state(self):
        """Save state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def scan_github_bounties(self) -> List[Dict]:
        """Scan GitHub for bounties"""
        bounties = []
        
        # Search for issues with bounty labels
        cmd = [
            "gh", "search", "issues",
            "--label", "bounty",
            "--state", "open",
            "--json", "url,title,repository,labels,comments",
            "--limit", "50"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            issues = json.loads(result.stdout)
            
            for issue in issues:
                bounty = self.parse_bounty(issue)
                if bounty:
                    bounties.append(bounty)
        except Exception as e:
            print(f"Error scanning GitHub: {e}")
        
        return bounties
    
    def parse_bounty(self, issue: dict) -> Optional[Dict]:
        """Parse bounty information from issue"""
        # Extract reward amount from title or labels
        title = issue.get("title", "")
        labels = [l["name"] for l in issue.get("labels", [])]
        
        # Simple reward extraction (can be improved)
        reward = 0
        for word in title.split():
            if word.startswith("$"):
                try:
                    reward = float(word[1:])
                except:
                    pass
        
        if reward == 0:
            # Check labels for reward info
            for label in labels:
                if "rtc" in label.lower():
                    try:
                        reward = float(label.split()[0])
                    except:
                        pass
        
        return {
            "url": issue["url"],
            "title": title,
            "repository": issue["repository"]["nameWithOwner"],
            "reward": reward,
            "competition": issue.get("comments", 0),
            "labels": labels
        }
    
    def matches_skills(self, bounty: Dict) -> bool:
        """Check if bounty matches configured skills"""
        text = f"{bounty['title']} {' '.join(bounty['labels'])}".lower()
        
        for skill in self.config["skills"]:
            if skill.lower() in text:
                return True
        return False
    
    def should_apply(self, bounty: Dict) -> bool:
        """Determine if we should apply to this bounty"""
        # Already seen?
        if bounty["url"] in self.state["seen_bounties"]:
            return False
        
        # Matches skills?
        if not self.matches_skills(bounty):
            return False
        
        # Reward too low?
        if bounty["reward"] < self.config["min_reward"]:
            return False
        
        # Too competitive?
        if bounty["competition"] > self.config["max_competition"]:
            return False
        
        return True
    
    def generate_proposal(self, bounty: Dict) -> str:
        """Generate a proposal for the bounty"""
        return f"""I'm interested in working on this bounty.

**My approach:**
1. Review the requirements thoroughly
2. Implement a high-quality solution
3. Test comprehensively
4. Submit with clear documentation

**Relevant experience:**
- {', '.join(self.config['skills'])}
- Track record of completing similar tasks
- Fast turnaround time (typically 2-4 hours)

I can start immediately. Let me know if you have any questions!
"""
    
    def apply_to_bounty(self, bounty: Dict) -> bool:
        """Apply to a bounty"""
        try:
            # Comment on the issue
            repo = bounty["repository"]
            issue_number = bounty["url"].split("/")[-1]
            proposal = self.generate_proposal(bounty)
            
            cmd = [
                "gh", "issue", "comment", issue_number,
                "--repo", repo,
                "--body", f"/apply\n\n{proposal}"
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Update state
            self.state["applied_bounties"].append({
                "url": bounty["url"],
                "title": bounty["title"],
                "reward": bounty["reward"],
                "applied_at": datetime.utcnow().isoformat()
            })
            self.save_state()
            
            return True
        except Exception as e:
            print(f"Error applying to bounty: {e}")
            return False
    
    def run(self):
        """Main loop"""
        print("🦞 GitHub Bounty Hunter started")
        print(f"Skills: {', '.join(self.config['skills'])}")
        print(f"Min reward: ${self.config['min_reward']}")
        print(f"Check interval: {self.config['check_interval']} minutes\n")
        
        while True:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Scanning for bounties...")
                
                bounties = self.scan_github_bounties()
                print(f"Found {len(bounties)} total bounties")
                
                applied = 0
                for bounty in bounties:
                    # Mark as seen
                    if bounty["url"] not in self.state["seen_bounties"]:
                        self.state["seen_bounties"].append(bounty["url"])
                    
                    if self.should_apply(bounty):
                        print(f"  ✅ Applying: {bounty['title']} (${bounty['reward']})")
                        if self.apply_to_bounty(bounty):
                            applied += 1
                        time.sleep(2)  # Rate limiting
                
                if applied > 0:
                    print(f"📤 Applied to {applied} bounties")
                else:
                    print("  No new matching bounties")
                
                self.save_state()
                
                print(f"Next check in {self.config['check_interval']} minutes\n")
                time.sleep(self.config['check_interval'] * 60)
                
            except KeyboardInterrupt:
                print("\n👋 Bounty hunter stopped")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    hunter = GitHubBountyHunter()
    hunter.run()
