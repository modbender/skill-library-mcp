#!/usr/bin/env python3
"""
BlackSnow Webhook Output
Pushes risk primitives to external systems via webhooks.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import hashlib
import hmac

# ============================================================================
# CONFIG
# ============================================================================

@dataclass
class WebhookConfig:
    url: str
    secret: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    tier: str = "operator"  # observer, operator, fund_api, sovereign

# ============================================================================
# WEBHOOK DELIVERY
# ============================================================================

class WebhookDelivery:
    """Delivers risk primitives to configured webhooks."""
    
    def __init__(self, config: WebhookConfig):
        self.config = config
    
    def _sign_payload(self, payload: bytes) -> str:
        """Generate HMAC signature for payload."""
        if not self.config.secret:
            return ""
        return hmac.new(
            self.config.secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
    
    def _filter_by_tier(self, primitives: List[Dict]) -> List[Dict]:
        """Filter primitives based on access tier."""
        tier = self.config.tier
        
        if tier == "observer":
            # Aggregated heatmaps only - anonymize and delay
            return [{
                "risk_domain": p["risk_vector"].split(".")[0],
                "signal_level": "high" if p["signal_confidence"] > 0.7 else "medium" if p["signal_confidence"] > 0.4 else "low",
                "time_horizon": p["time_horizon_days"],
                "delayed_by_hours": 24
            } for p in primitives]
        
        elif tier == "operator":
            # Full risk vectors, near-real-time
            return primitives
        
        elif tier == "fund_api":
            # Full primitives + metadata
            return [{
                **p,
                "delivery_timestamp": datetime.now(timezone.utc).isoformat(),
                "stream_id": hashlib.md5(json.dumps(p, sort_keys=True).encode()).hexdigest()[:12]
            } for p in primitives]
        
        elif tier == "sovereign":
            # Full + custom fields
            return [{
                **p,
                "delivery_timestamp": datetime.now(timezone.utc).isoformat(),
                "exclusivity_marker": True,
                "raw_signal_count": 0  # Would include actual count
            } for p in primitives]
        
        return primitives
    
    def deliver(self, primitives: List[Any]) -> Dict[str, Any]:
        """Send primitives to webhook endpoint."""
        # Convert to dicts if needed
        prim_dicts = [
            asdict(p) if hasattr(p, '__dataclass_fields__') else p 
            for p in primitives
        ]
        
        # Filter by tier
        filtered = self._filter_by_tier(prim_dicts)
        
        # Build payload
        payload = {
            "source": "blacksnow",
            "version": "0.1.0",
            "tier": self.config.tier,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "primitives": filtered,
            "count": len(filtered)
        }
        
        payload_bytes = json.dumps(payload, default=str).encode('utf-8')
        
        # Build headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "BlackSnow/0.1.0",
            "X-BlackSnow-Tier": self.config.tier,
        }
        
        if self.config.secret:
            headers["X-BlackSnow-Signature"] = self._sign_payload(payload_bytes)
        
        if self.config.headers:
            headers.update(self.config.headers)
        
        # Send request
        try:
            req = urllib.request.Request(
                self.config.url,
                data=payload_bytes,
                headers=headers,
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                return {
                    "success": True,
                    "status_code": response.status,
                    "primitives_sent": len(filtered),
                    "tier": self.config.tier,
                    "url": self.config.url
                }
                
        except urllib.error.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP {e.code}: {e.reason}",
                "url": self.config.url
            }
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": str(e.reason),
                "url": self.config.url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": self.config.url
            }


# ============================================================================
# BATCH DELIVERY
# ============================================================================

class WebhookManager:
    """Manages multiple webhook endpoints."""
    
    def __init__(self):
        self.endpoints: List[WebhookConfig] = []
    
    def add_endpoint(self, url: str, tier: str = "operator", secret: str = None):
        """Register a webhook endpoint."""
        self.endpoints.append(WebhookConfig(url=url, tier=tier, secret=secret))
    
    def deliver_all(self, primitives: List[Any]) -> List[Dict]:
        """Deliver to all registered endpoints."""
        results = []
        for config in self.endpoints:
            delivery = WebhookDelivery(config)
            result = delivery.deliver(primitives)
            results.append(result)
        return results
    
    def load_from_config(self, config_path: str):
        """Load endpoints from config file."""
        import os
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            for ep in config.get("webhooks", []):
                self.add_endpoint(
                    url=ep["url"],
                    tier=ep.get("tier", "operator"),
                    secret=ep.get("secret")
                )


# ============================================================================
# CLI / TEST
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Test payload
    test_primitives = [
        {
            "risk_vector": "infra.energy.grid",
            "signal_confidence": 0.82,
            "time_horizon_days": "7-14",
            "contributing_domains": ["deferral", "language_shift"],
            "likely_outcomes": ["localized_outage", "price_volatility"],
            "tradability": {"insurance": True, "commodities": True, "logistics": True, "policy": True}
        }
    ]
    
    if len(sys.argv) > 1:
        webhook_url = sys.argv[1]
        tier = sys.argv[2] if len(sys.argv) > 2 else "operator"
        
        print(f"[WEBHOOK] Delivering to {webhook_url} (tier: {tier})")
        
        config = WebhookConfig(url=webhook_url, tier=tier)
        delivery = WebhookDelivery(config)
        result = delivery.deliver(test_primitives)
        
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python webhook.py <webhook_url> [tier]")
        print("\nTiers: observer, operator, fund_api, sovereign")
        print("\nTest payload:")
        print(json.dumps(test_primitives, indent=2))
