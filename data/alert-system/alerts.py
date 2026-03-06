#!/usr/bin/env python3
"""
Alert System — Smart monitoring with customizable triggers.

- Price alerts (stocks, crypto, products)
- Event monitoring (website changes, releases)
- Custom condition alerts
- Cron-integrated checking with Telegram notification
"""
import sys
import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.atomic import atomic_write_json, atomic_read_json, FileLock
from common.config import Config
from common.timeutil import now_local, get_user_timezone
from common.identity import get_user_telegram_id


@dataclass
class Alert:
    id: str
    user: str
    alert_type: str      # "price", "stock", "crypto", "website", "custom"
    target: str          # ticker, URL, or description
    condition: str       # "below", "above", "change", "contains"
    threshold: Any       # price, percentage, or text to match
    active: bool = True
    triggered: bool = False
    created_at: str = ""
    last_checked: str = ""
    last_value: Any = None
    trigger_count: int = 0
    repeat: bool = False   # Keep monitoring after trigger?
    message: str = ""      # Custom message when triggered


class AlertSystem:
    """Monitor and alert system."""

    def __init__(self, username: str):
        self.username = username
        self.tz = get_user_timezone(username)
        self.alerts_file = Config.WORKSPACE / "skills" / "alert-system" / "data" / f"{username}_alerts.json"
        self.alerts_file.parent.mkdir(parents=True, exist_ok=True)

    def add_alert(self, alert_type: str, target: str, condition: str,
                  threshold: Any, message: str = "", repeat: bool = False) -> Alert:
        """Add a new alert."""
        alert_id = f"alert_{int(datetime.now().timestamp())}_{self.username}"

        alert = Alert(
            id=alert_id,
            user=self.username,
            alert_type=alert_type,
            target=target,
            condition=condition,
            threshold=threshold,
            created_at=datetime.now().isoformat(),
            repeat=repeat,
            message=message,
        )

        alerts = self._load_alerts()
        alerts.append(self._alert_to_dict(alert))
        self._save_alerts(alerts)

        return alert

    def remove_alert(self, alert_id: str) -> bool:
        """Remove an alert by ID."""
        alerts = self._load_alerts()
        before = len(alerts)
        alerts = [a for a in alerts if a["id"] != alert_id]
        if len(alerts) < before:
            self._save_alerts(alerts)
            return True
        return False

    def list_alerts(self) -> List[Dict]:
        """List all active alerts."""
        return [a for a in self._load_alerts() if a.get("active", True)]

    def check_all(self) -> List[Dict]:
        """Check all active alerts and return triggered ones.

        This is designed to be called from cron.
        """
        alerts = self._load_alerts()
        triggered = []

        for alert_data in alerts:
            if not alert_data.get("active", True):
                continue

            result = self._check_alert(alert_data)
            if result:
                triggered.append(result)
                # Update alert state
                alert_data["triggered"] = True
                alert_data["trigger_count"] = alert_data.get("trigger_count", 0) + 1
                if not alert_data.get("repeat", False):
                    alert_data["active"] = False
            alert_data["last_checked"] = datetime.now().isoformat()

        self._save_alerts(alerts)
        return triggered

    # Task executor interface
    def parse_alert(self, request: str, **kwargs) -> Dict:
        """Parse a natural language alert request."""
        return self._parse_natural_language(request)

    def setup_monitor(self, **kwargs) -> Dict:
        """Set up a monitor from parsed alert info."""
        ctx = kwargs.get("context", {})
        parsed = ctx.get("step_1_result", {})

        if not parsed:
            return {"error": "Could not parse alert request"}

        alert = self.add_alert(
            alert_type=parsed.get("type", "custom"),
            target=parsed.get("target", ""),
            condition=parsed.get("condition", "change"),
            threshold=parsed.get("threshold", 0),
            message=parsed.get("message", ""),
            repeat=parsed.get("repeat", False),
        )

        return {
            "success": True,
            "alert_id": alert.id,
            "description": f"{alert.condition} {alert.threshold} on {alert.target}",
        }

    def _parse_natural_language(self, text: str) -> Dict:
        """Parse natural language into alert parameters."""
        text_lower = text.lower()
        parsed = {"type": "custom", "target": "", "condition": "change",
                  "threshold": 0, "message": "", "repeat": False}

        # Price/stock alert: "alert me when NVDA drops below $120"
        stock_match = re.search(
            r'(?:when|if)\s+(\w+)\s+(?:drops?|falls?|goes?)\s+(?:below|under)\s+\$?([\d,.]+)',
            text_lower
        )
        if stock_match:
            parsed["type"] = "stock"
            parsed["target"] = stock_match.group(1).upper()
            parsed["condition"] = "below"
            parsed["threshold"] = float(stock_match.group(2).replace(",", ""))
            return parsed

        stock_match = re.search(
            r'(?:when|if)\s+(\w+)\s+(?:goes?|rises?|hits?)\s+(?:above|over)\s+\$?([\d,.]+)',
            text_lower
        )
        if stock_match:
            parsed["type"] = "stock"
            parsed["target"] = stock_match.group(1).upper()
            parsed["condition"] = "above"
            parsed["threshold"] = float(stock_match.group(2).replace(",", ""))
            return parsed

        # Percentage change: "alert me if BTC moves more than 5%"
        pct_match = re.search(
            r'(?:when|if)\s+(\w+)\s+(?:moves?|changes?)\s+(?:more\s+than\s+)?(\d+(?:\.\d+)?)\s*%',
            text_lower
        )
        if pct_match:
            parsed["type"] = "stock"
            parsed["target"] = pct_match.group(1).upper()
            parsed["condition"] = "change"
            parsed["threshold"] = float(pct_match.group(2))
            return parsed

        # Price drop: "when AirPods are under $200"
        price_match = re.search(
            r'(?:when|if)\s+(.+?)\s+(?:is|are|drops?|falls?)\s+(?:below|under)\s+\$?([\d,.]+)',
            text_lower
        )
        if price_match:
            parsed["type"] = "price"
            parsed["target"] = price_match.group(1).strip()
            parsed["condition"] = "below"
            parsed["threshold"] = float(price_match.group(2).replace(",", ""))
            return parsed

        # Website change: "monitor website.com for changes"
        url_match = re.search(r'(?:monitor|watch|track)\s+(https?://\S+)', text)
        if url_match:
            parsed["type"] = "website"
            parsed["target"] = url_match.group(1)
            parsed["condition"] = "change"
            return parsed

        # Fallback: use the whole text
        parsed["target"] = text[:100]
        parsed["message"] = text
        return parsed

    def _check_alert(self, alert_data: Dict) -> Optional[Dict]:
        """Check if an alert's condition is met."""
        alert_type = alert_data.get("alert_type", "custom")
        target = alert_data.get("target", "")
        condition = alert_data.get("condition", "")
        threshold = alert_data.get("threshold", 0)

        if alert_type in ("stock", "crypto"):
            return self._check_stock_alert(alert_data)
        elif alert_type == "website":
            return self._check_website_alert(alert_data)
        elif alert_type == "price":
            return self._check_price_alert(alert_data)
        return None

    def _check_stock_alert(self, alert_data: Dict) -> Optional[Dict]:
        """Check a stock/crypto price alert."""
        try:
            from financial_intel.engine import fetch_market_data, resolve_ticker
            target = resolve_ticker(alert_data["target"])
            data = fetch_market_data(target)

            if not data:
                return None

            current_price = data.price
            condition = alert_data["condition"]
            threshold = float(alert_data["threshold"])
            last_value = alert_data.get("last_value")

            # Update last value
            alert_data["last_value"] = current_price

            triggered = False
            if condition == "below" and current_price <= threshold:
                triggered = True
            elif condition == "above" and current_price >= threshold:
                triggered = True
            elif condition == "change" and last_value:
                change_pct = abs((current_price - last_value) / last_value * 100)
                if change_pct >= threshold:
                    triggered = True

            if triggered:
                arrow = "📉" if condition == "below" else "📈" if condition == "above" else "⚡"
                return {
                    "alert_id": alert_data["id"],
                    "type": "stock",
                    "message": f"{arrow} **{alert_data['target']}** hit ${current_price:,.2f} "
                               f"({condition} ${threshold:,.2f})",
                    "current_value": current_price,
                }
        except Exception:
            pass
        return None

    def _check_website_alert(self, alert_data: Dict) -> Optional[Dict]:
        """Check if a website has changed."""
        try:
            from common.web import fetch_page_text
            import hashlib

            url = alert_data["target"]
            text = fetch_page_text(url, max_chars=5000)
            current_hash = hashlib.md5(text.encode()).hexdigest()

            last_hash = alert_data.get("last_value")
            alert_data["last_value"] = current_hash

            if last_hash and current_hash != last_hash:
                return {
                    "alert_id": alert_data["id"],
                    "type": "website",
                    "message": f"🌐 **Website changed**: {url[:50]}...",
                    "current_value": current_hash,
                }
        except Exception:
            pass
        return None

    def _check_price_alert(self, alert_data: Dict) -> Optional[Dict]:
        """Check a product price alert (via web search)."""
        try:
            from common.web import web_search
            target = alert_data["target"]
            threshold = float(alert_data["threshold"])

            results = web_search(f"{target} price", count=3)
            for r in results:
                desc = r.get("description", "")
                # Find price in description
                price_match = re.search(r'\$[\d,]+(?:\.\d{2})?', desc)
                if price_match:
                    price = float(price_match.group().replace("$", "").replace(",", ""))
                    if price <= threshold:
                        return {
                            "alert_id": alert_data["id"],
                            "type": "price",
                            "message": f"💰 **{target}** found at ${price:,.2f} (under ${threshold:,.2f})",
                            "current_value": price,
                            "source": r.get("url", ""),
                        }
        except Exception:
            pass
        return None

    def _load_alerts(self) -> List[Dict]:
        return atomic_read_json(self.alerts_file, default=[])

    def _save_alerts(self, alerts: List[Dict]):
        atomic_write_json(self.alerts_file, alerts)

    def _alert_to_dict(self, alert: Alert) -> Dict:
        return {
            "id": alert.id, "user": alert.user,
            "alert_type": alert.alert_type, "target": alert.target,
            "condition": alert.condition, "threshold": alert.threshold,
            "active": alert.active, "triggered": alert.triggered,
            "created_at": alert.created_at, "last_checked": alert.last_checked,
            "last_value": alert.last_value, "trigger_count": alert.trigger_count,
            "repeat": alert.repeat, "message": alert.message,
        }


def format_alerts(triggered: List[Dict]) -> str:
    """Format triggered alerts for Telegram."""
    if not triggered:
        return "✅ No alerts triggered."

    lines = ["🔔 **Alert Notifications**", ""]
    for t in triggered:
        lines.append(t.get("message", "Unknown alert"))
        if t.get("source"):
            lines.append(f"   🔗 {t['source']}")
        lines.append("")

    return "\n".join(lines)


def check_all_users() -> Dict[str, List[Dict]]:
    """Check alerts for all users. Called from cron."""
    from common.identity import list_users
    results = {}
    for username in list_users():
        system = AlertSystem(username)
        triggered = system.check_all()
        if triggered:
            results[username] = triggered
    return results


if __name__ == "__main__":
    _user = sys.argv[1] if len(sys.argv) > 1 else ""
    system = AlertSystem(_user)

    if len(sys.argv) > 1 and sys.argv[1] == "check":
        triggered = system.check_all()
        print(format_alerts(triggered))
    elif len(sys.argv) > 1 and sys.argv[1] == "list":
        alerts = system.list_alerts()
        for a in alerts:
            print(f"  • [{a['alert_type']}] {a['target']} {a['condition']} {a['threshold']}")
    else:
        # Demo: add a test alert
        alert = system.add_alert(
            alert_type="stock",
            target="NVDA",
            condition="below",
            threshold=120.0,
            message="NVIDIA dropped below $120!",
        )
        print(f"✅ Alert created: {alert.id}")
        print(f"   Watching {alert.target} for {alert.condition} ${alert.threshold}")
