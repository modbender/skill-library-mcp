#!/usr/bin/env python3
"""
Polymarket News Monitor - ClawHub Skill
Monitors official Polymarket sources for important updates and security alerts

Usage:
    python3 polymarket-monitor.py [--config config.json]
    
Features:
- RSS feed monitoring (The Oracle blog)
- Breaking news detection
- API status checks
- Keyword-based importance scoring
- Alert notifications
"""

import requests
import json
import re
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

# Default configuration
DEFAULT_CONFIG = {
    "data_dir": "./data",
    "check_interval": 1800,  # 30 minutes
    "min_importance": 4,     # Minimum importance to alert
    "max_history": 100,      # Max articles to remember
    "notification": {
        "enabled": False,
        "method": "console",  # console, telegram, email
        "webhook": None
    }
}

# Keywords for importance detection
IMPORTANT_KEYWORDS = [
    "security", "breach", "hack", "exploit", "vulnerability",
    "maintenance", "downtime", "outage", "disruption",
    "update", "upgrade", "migration", "deprecation",
    "api", "endpoint", "breaking change", "sunset",
    "regulation", "compliance", "legal", "restricted",
    "usdc", "withdrawal", "deposit", "settlement",
    "critical", "urgent", "emergency", "alert"
]

SECURITY_ALERTS = [
    "phishing", "scam", "fake", "fraud", "impersonation",
    "private key", "seed phrase", "password", "credential",
    "suspicious", "unauthorized", "attack"
]


class PolymarketMonitor:
    """Monitor Polymarket official sources for important updates"""
    
    def __init__(self, config=None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.data_dir = Path(self.config["data_dir"])
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_file = self.data_dir / "news_state.json"
        self.alert_file = self.data_dir / "alerts.json"
        self.log_file = self.data_dir / "monitor.log"
        
        self.state = self._load_state()
        self.alerts = []
        
    def _load_state(self):
        """Load previous state"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {"last_check": None, "seen_hashes": [], "article_count": 0}
    
    def _save_state(self):
        """Save current state"""
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def _save_alerts(self):
        """Save alerts to file"""
        with open(self.alert_file, "w") as f:
            json.dump(self.alerts, f, indent=2, ensure_ascii=False)
    
    def _log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")
    
    def _hash_content(self, content):
        """Create hash of content for duplicate detection"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_new_content(self, content_hash):
        """Check if content is new"""
        if content_hash in self.state["seen_hashes"]:
            return False
        self.state["seen_hashes"].append(content_hash)
        # Keep only last N hashes
        max_hist = self.config["max_history"]
        self.state["seen_hashes"] = self.state["seen_hashes"][-max_hist:]
        return True
    
    def analyze_importance(self, title, content=""):
        """Analyze importance of news item"""
        text = (title + " " + content).lower()
        
        importance_score = 0
        matched_keywords = []
        
        # Check important keywords
        for keyword in IMPORTANT_KEYWORDS:
            if keyword in text:
                importance_score += 2
                matched_keywords.append(keyword)
        
        # Check security alerts (higher priority)
        for alert in SECURITY_ALERTS:
            if alert in text:
                importance_score += 5
                matched_keywords.append(f"SECURITY:{alert}")
        
        # Detect critical situations
        critical_patterns = [
            r"system.*down",
            r"maintenance.*complete",
            r"security.*incident",
            r"api.*deprecated",
            r"withdrawal.*disabled"
        ]
        
        for pattern in critical_patterns:
            if re.search(pattern, text):
                importance_score += 3
                matched_keywords.append(f"CRITICAL")
        
        return importance_score, matched_keywords
    
    def fetch_oracle_news(self):
        """Fetch news from The Oracle (Substack RSS)"""
        try:
            rss_url = "https://news.polymarket.com/feed"
            headers = {"User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)"}
            
            response = requests.get(rss_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                items = root.findall('.//item')
                
                articles = []
                for item in items[:5]:  # Last 5 articles
                    title = item.find('title')
                    link = item.find('link')
                    pub_date = item.find('pubDate')
                    description = item.find('description')
                    
                    title_text = title.text if title is not None else "No title"
                    link_text = link.text if link is not None else ""
                    desc_text = description.text if description is not None else ""
                    pub_text = pub_date.text if pub_date is not None else "unknown"
                    
                    content_hash = self._hash_content(title_text + desc_text)
                    
                    if self._is_new_content(content_hash):
                        importance, keywords = self.analyze_importance(
                            title_text, desc_text
                        )
                        
                        articles.append({
                            "source": "The Oracle",
                            "title": title_text,
                            "url": link_text,
                            "published": pub_text,
                            "importance": importance,
                            "keywords": keywords,
                            "hash": content_hash
                        })
                
                return articles
            else:
                self._log(f"RSS feed returned status {response.status_code}")
                return []
                
        except Exception as e:
            self._log(f"Error fetching The Oracle: {e}")
            return []
    
    def check_api_status(self):
        """Check Polymarket API status"""
        try:
            response = requests.get(
                "https://clob.polymarket.com/health",
                timeout=5
            )
            
            if response.status_code != 200:
                return [{
                    "source": "API Status",
                    "title": "⚠️ Polymarket API may be unavailable",
                    "url": "https://status.polymarket.com",
                    "published": datetime.now().isoformat(),
                    "importance": 8,
                    "keywords": ["api", "outage", "unavailable"],
                    "hash": self._hash_content(f"api_issue_{datetime.now().strftime('%Y%m%d')}")
                }]
                
        except Exception as e:
            return [{
                "source": "API Status",
                "title": f"⚠️ Polymarket API unavailable: {str(e)[:50]}",
                "url": "https://status.polymarket.com",
                "published": datetime.now().isoformat(),
                "importance": 9,
                "keywords": ["api", "outage", "critical"],
                "hash": self._hash_content(f"api_down_{datetime.now().strftime('%Y%m%d%H')}")
            }]
        
        return []
    
    def format_alert(self, item):
        """Format alert for display"""
        importance = item["importance"]
        if importance >= 7:
            emoji = "🔴"
            level = "HIGH"
        elif importance >= 4:
            emoji = "🟠"
            level = "MEDIUM"
        else:
            emoji = "🟡"
            level = "LOW"
        
        return f"""
{emoji} **Polymarket Alert** ({item["source"]}) - {level}

**{item["title"]}**

🔗 URL: {item["url"]}
📅 Time: {item["published"]}
⚡ Importance: {item["importance"]}/10
🏷️ Keywords: {', '.join(item["keywords"][:5])}

---
"""
    
    def send_notification(self, alert):
        """Send notification based on config"""
        method = self.config["notification"]["method"]
        
        if method == "console":
            print(self.format_alert(alert))
        
        elif method == "webhook" and self.config["notification"]["webhook"]:
            try:
                requests.post(
                    self.config["notification"]["webhook"],
                    json=alert,
                    timeout=5
                )
            except Exception as e:
                self._log(f"Webhook error: {e}")
    
    def run(self):
        """Main monitoring function"""
        self._log("Starting Polymarket News Monitor")
        self._log("=" * 50)
        
        all_items = []
        
        # 1. The Oracle blog
        self._log("Checking The Oracle...")
        oracle_news = self.fetch_oracle_news()
        all_items.extend(oracle_news)
        self._log(f"Found: {len(oracle_news)} new articles")
        
        # 2. API status
        self._log("Checking API status...")
        api_status = self.check_api_status()
        all_items.extend(api_status)
        self._log(f"Found: {len(api_status)} issues")
        
        # Filter important items
        min_imp = self.config["min_importance"]
        important_items = [item for item in all_items if item["importance"] >= min_imp]
        
        self._log("=" * 50)
        self._log(f"Total: {len(all_items)} items, {len(important_items)} important")
        
        # Process alerts
        if important_items:
            self.alerts = important_items
            self._save_alerts()
            
            self._log("🚨 IMPORTANT ALERTS:")
            
            for item in important_items:
                self.send_notification(item)
        else:
            self._log("✅ No important news")
        
        # Save state
        self.state["last_check"] = datetime.now().isoformat()
        self.state["article_count"] = self.state.get("article_count", 0) + len(all_items)
        self._save_state()
        
        self._log(f"State saved: {self.state_file}")
        self._log(f"Alerts saved: {self.alert_file}")
        
        return important_items


def main():
    parser = argparse.ArgumentParser(description="Polymarket News Monitor")
    parser.add_argument("--config", help="Path to config JSON file")
    parser.add_argument("--data-dir", help="Data directory path", default="./data")
    parser.add_argument("--min-importance", type=int, default=4, help="Minimum importance level")
    args = parser.parse_args()
    
    config = {"data_dir": args.data_dir, "min_importance": args.min_importance}
    
    if args.config:
        with open(args.config) as f:
            config.update(json.load(f))
    
    monitor = PolymarketMonitor(config)
    alerts = monitor.run()
    
    # Exit with error code if critical alerts found (for cron)
    critical_count = len([a for a in alerts if a["importance"] >= 7])
    if critical_count > 0:
        exit(1)


if __name__ == "__main__":
    main()
