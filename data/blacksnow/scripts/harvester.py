#!/usr/bin/env python3
"""
BlackSnow Live Data Harvester
Connects to real public data sources for ambient risk signals.
"""

import json
import hashlib
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import urllib.request
import urllib.error
import ssl

# ============================================================================
# CONFIG
# ============================================================================

SOURCES = {
    "sam_gov": {
        "name": "SAM.gov Federal Opportunities",
        "url": "https://api.sam.gov/opportunities/v2/search",
        "type": "procurement",
        "requires_key": True
    },
    "fedreg": {
        "name": "Federal Register",
        "url": "https://www.federalregister.gov/api/v1/documents.json",
        "type": "regulatory",
        "requires_key": False
    },
    "sec_edgar": {
        "name": "SEC EDGAR Filings",
        "url": "https://efts.sec.gov/LATEST/search-index",
        "type": "corporate",
        "requires_key": False
    }
}

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class RawSignal:
    source_id: str
    source_name: str
    domain: str
    title: str
    raw_text: str
    url: str
    timestamp: str
    confidence: float
    metadata: Dict

# ============================================================================
# HARVESTERS
# ============================================================================

class FederalRegisterHarvester:
    """Harvests from Federal Register API (no key required)."""
    
    BASE_URL = "https://www.federalregister.gov/api/v1/documents.json"
    
    def harvest(self, keywords: List[str] = None, days_back: int = 7) -> List[RawSignal]:
        if keywords is None:
            keywords = ["grid", "energy", "infrastructure", "emergency", "defer"]
        
        signals = []
        
        # Build query
        params = {
            "per_page": 20,
            "order": "newest",
            "conditions[type][]": ["RULE", "PRORULE", "NOTICE"],
        }
        
        query = "&".join([f"{k}={v}" if not isinstance(v, list) else "&".join([f"{k}={x}" for x in v]) for k, v in params.items()])
        url = f"{self.BASE_URL}?{query}"
        
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(url, headers={"User-Agent": "BlackSnow/0.1"})
            with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                data = json.loads(response.read().decode())
                
            for doc in data.get("results", []):
                title = doc.get("title", "")
                abstract = doc.get("abstract", "") or ""
                
                # Check keyword relevance
                text_lower = (title + " " + abstract).lower()
                if not any(kw in text_lower for kw in keywords):
                    continue
                
                signal = RawSignal(
                    source_id=f"fedreg:{doc.get('document_number', 'unknown')}",
                    source_name="Federal Register",
                    domain="regulatory.federal",
                    title=title[:200],
                    raw_text=abstract[:1000] if abstract else title,
                    url=doc.get("html_url", ""),
                    timestamp=doc.get("publication_date", datetime.now(timezone.utc).isoformat()),
                    confidence=0.85,
                    metadata={
                        "type": doc.get("type"),
                        "agencies": [a.get("name") for a in doc.get("agencies", [])],
                        "docket_ids": doc.get("docket_ids", [])
                    }
                )
                signals.append(signal)
                
        except Exception as e:
            print(f"[WARN] FederalRegister harvest failed: {e}")
        
        return signals


class MockProcurementHarvester:
    """Mock harvester for procurement data (SAM.gov requires API key)."""
    
    def harvest(self) -> List[RawSignal]:
        # Return realistic mock data
        return [
            RawSignal(
                source_id="sam:opp:2026-02-07:grid-maint-northeast",
                source_name="SAM.gov",
                domain="procurement.federal",
                title="Emergency Grid Maintenance - Northeast Region",
                raw_text="Solicitation for emergency maintenance services for transmission infrastructure. Expedited timeline due to deferred Q4 maintenance backlog. Critical infrastructure designation.",
                url="https://sam.gov/opp/example",
                timestamp=datetime.now(timezone.utc).isoformat(),
                confidence=0.92,
                metadata={"naics": "237130", "set_aside": "none", "value_range": "1M-5M"}
            ),
            RawSignal(
                source_id="sam:opp:2026-02-06:port-security-upgrade",
                source_name="SAM.gov",
                domain="procurement.federal",
                title="Port Security Infrastructure Upgrade - Gulf Coast",
                raw_text="Request for proposals for security system upgrades at major port facilities. Accelerated timeline requested by DHS.",
                url="https://sam.gov/opp/example2",
                timestamp=datetime.now(timezone.utc).isoformat(),
                confidence=0.88,
                metadata={"naics": "561621", "set_aside": "small_business", "value_range": "500K-1M"}
            )
        ]


class MockLaborHarvester:
    """Mock harvester for labor/union data."""
    
    def harvest(self) -> List[RawSignal]:
        return [
            RawSignal(
                source_id="nlrb:case:2026-02-05:grievance-1923",
                source_name="NLRB",
                domain="labor.union",
                title="Collective Bargaining Grievance - Utility Sector",
                raw_text="Union files grievance regarding mandatory overtime policies and safety protocol modifications at regional power generation facility.",
                url="https://nlrb.gov/case/example",
                timestamp=datetime.now(timezone.utc).isoformat(),
                confidence=0.87,
                metadata={"sector": "utilities", "region": "midwest", "grievance_type": "safety"}
            )
        ]


# ============================================================================
# MAIN
# ============================================================================

def harvest_all_sources() -> List[RawSignal]:
    """Run all harvesters and collect signals."""
    all_signals = []
    
    print("[HARVESTER] Starting live data collection...")
    
    # Federal Register (live)
    print("  → Federal Register...")
    fr_harvester = FederalRegisterHarvester()
    fr_signals = fr_harvester.harvest()
    print(f"    Found {len(fr_signals)} signals")
    all_signals.extend(fr_signals)
    
    # SAM.gov (mock - needs API key)
    print("  → SAM.gov (mock)...")
    proc_harvester = MockProcurementHarvester()
    proc_signals = proc_harvester.harvest()
    print(f"    Found {len(proc_signals)} signals")
    all_signals.extend(proc_signals)
    
    # NLRB (mock)
    print("  → NLRB (mock)...")
    labor_harvester = MockLaborHarvester()
    labor_signals = labor_harvester.harvest()
    print(f"    Found {len(labor_signals)} signals")
    all_signals.extend(labor_signals)
    
    print(f"[HARVESTER] Total: {len(all_signals)} raw signals collected")
    return all_signals


if __name__ == "__main__":
    signals = harvest_all_sources()
    print("\n" + "="*60)
    print("RAW SIGNALS")
    print("="*60)
    for sig in signals:
        print(json.dumps(asdict(sig), indent=2, default=str))
        print()
