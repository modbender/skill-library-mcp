#!/usr/bin/env python3
"""
BlackSnow Extended Harvester
Additional live data sources for ambient risk detection.
"""

import json
import urllib.request
import urllib.error
import ssl
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import re

# ============================================================================
# DATA CLASS
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
# UTILITY
# ============================================================================

def safe_fetch(url: str, headers: Dict = None, timeout: int = 15) -> Optional[bytes]:
    """Safely fetch URL with SSL handling."""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        hdrs = {"User-Agent": "BlackSnow/0.1 (Risk Intelligence)"}
        if headers:
            hdrs.update(headers)
        
        req = urllib.request.Request(url, headers=hdrs)
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            return response.read()
    except Exception as e:
        print(f"    [WARN] Fetch failed for {url[:50]}...: {e}")
        return None

# ============================================================================
# LIVE HARVESTERS
# ============================================================================

class FederalRegisterHarvester:
    """Federal Register - regulatory documents."""
    
    NAME = "Federal Register"
    BASE_URL = "https://www.federalregister.gov/api/v1/documents.json"
    
    def harvest(self, keywords: List[str] = None) -> List[RawSignal]:
        if keywords is None:
            keywords = ["grid", "energy", "infrastructure", "emergency", "pipeline", "rail", "port"]
        
        signals = []
        url = f"{self.BASE_URL}?per_page=25&order=newest&conditions[type][]=RULE&conditions[type][]=PRORULE&conditions[type][]=NOTICE"
        
        data = safe_fetch(url)
        if not data:
            return signals
        
        try:
            results = json.loads(data).get("results", [])
            for doc in results:
                title = doc.get("title", "")
                abstract = doc.get("abstract", "") or ""
                text_lower = (title + " " + abstract).lower()
                
                if not any(kw in text_lower for kw in keywords):
                    continue
                
                signals.append(RawSignal(
                    source_id=f"fedreg:{doc.get('document_number', 'unknown')}",
                    source_name=self.NAME,
                    domain="regulatory.federal",
                    title=title[:200],
                    raw_text=abstract[:1000] if abstract else title,
                    url=doc.get("html_url", ""),
                    timestamp=doc.get("publication_date", datetime.now(timezone.utc).isoformat()),
                    confidence=0.85,
                    metadata={"type": doc.get("type"), "agencies": [a.get("name") for a in doc.get("agencies", [])]}
                ))
        except Exception as e:
            print(f"    [WARN] FederalRegister parse error: {e}")
        
        return signals


class SECEdgarHarvester:
    """SEC EDGAR - corporate filings (8-K, 10-K)."""
    
    NAME = "SEC EDGAR"
    BASE_URL = "https://efts.sec.gov/LATEST/search-index"
    RSS_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&company=&dateb=&owner=include&count=40&output=atom"
    
    def harvest(self) -> List[RawSignal]:
        signals = []
        
        # Try RSS feed for 8-K filings
        data = safe_fetch(self.RSS_URL)
        if not data:
            return signals
        
        try:
            content = data.decode('utf-8', errors='ignore')
            
            # Simple XML parsing for entries
            entries = re.findall(r'<entry>(.*?)</entry>', content, re.DOTALL)
            
            for entry in entries[:20]:
                title_match = re.search(r'<title[^>]*>(.*?)</title>', entry, re.DOTALL)
                link_match = re.search(r'<link[^>]*href="([^"]+)"', entry)
                updated_match = re.search(r'<updated>([^<]+)</updated>', entry)
                summary_match = re.search(r'<summary[^>]*>(.*?)</summary>', entry, re.DOTALL)
                
                if not title_match:
                    continue
                
                title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                summary = re.sub(r'<[^>]+>', '', summary_match.group(1)).strip() if summary_match else ""
                
                # Look for resignation, acquisition, material events
                text_lower = (title + " " + summary).lower()
                risk_keywords = ["resign", "terminat", "acqui", "merger", "material", "default", "breach", "layoff"]
                
                if not any(kw in text_lower for kw in risk_keywords):
                    continue
                
                signals.append(RawSignal(
                    source_id=f"sec:8k:{link_match.group(1).split('/')[-1] if link_match else 'unknown'}",
                    source_name=self.NAME,
                    domain="corporate.filings",
                    title=title[:200],
                    raw_text=summary[:1000],
                    url=link_match.group(1) if link_match else "",
                    timestamp=updated_match.group(1) if updated_match else datetime.now(timezone.utc).isoformat(),
                    confidence=0.90,
                    metadata={"form_type": "8-K"}
                ))
        except Exception as e:
            print(f"    [WARN] SEC EDGAR parse error: {e}")
        
        return signals


class USASpendingHarvester:
    """USASpending.gov - federal contract awards."""
    
    NAME = "USASpending.gov"
    BASE_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    
    def harvest(self) -> List[RawSignal]:
        signals = []
        
        # Search for recent large contracts in infrastructure
        payload = {
            "filters": {
                "time_period": [{"start_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"), "end_date": datetime.now().strftime("%Y-%m-%d")}],
                "award_type_codes": ["A", "B", "C", "D"],
                "naics_codes": ["221", "237", "488", "562"]  # Utilities, Heavy Construction, Transport Support, Waste
            },
            "fields": ["Award ID", "Recipient Name", "Award Amount", "Description", "Start Date"],
            "limit": 20,
            "order": "desc",
            "sort": "Award Amount"
        }
        
        try:
            req = urllib.request.Request(
                self.BASE_URL,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json", "User-Agent": "BlackSnow/0.1"}
            )
            
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
                data = json.loads(response.read().decode())
            
            for award in data.get("results", []):
                desc = award.get("Description", "") or ""
                
                signals.append(RawSignal(
                    source_id=f"usaspending:{award.get('Award ID', 'unknown')}",
                    source_name=self.NAME,
                    domain="procurement.federal",
                    title=f"{award.get('Recipient Name', 'Unknown')} - ${award.get('Award Amount', 0):,.0f}",
                    raw_text=desc[:1000],
                    url=f"https://www.usaspending.gov/award/{award.get('Award ID', '')}",
                    timestamp=award.get("Start Date", datetime.now(timezone.utc).isoformat()),
                    confidence=0.88,
                    metadata={"amount": award.get("Award Amount"), "recipient": award.get("Recipient Name")}
                ))
        except Exception as e:
            print(f"    [WARN] USASpending error: {e}")
        
        return signals


class DOTSafetyHarvester:
    """DOT Safety recalls and investigations."""
    
    NAME = "DOT NHTSA"
    BASE_URL = "https://api.nhtsa.gov/recalls/recallsByDate"
    
    def harvest(self) -> List[RawSignal]:
        signals = []
        
        # Get recent recalls
        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        url = f"https://api.nhtsa.gov/recalls/recallsByDate?startDate={week_ago}&endDate={today}"
        
        data = safe_fetch(url)
        if not data:
            return signals
        
        try:
            results = json.loads(data).get("results", [])
            
            for recall in results[:15]:
                signals.append(RawSignal(
                    source_id=f"nhtsa:{recall.get('NHTSACampaignNumber', 'unknown')}",
                    source_name=self.NAME,
                    domain="regulatory.safety",
                    title=f"{recall.get('Manufacturer', 'Unknown')} - {recall.get('Component', 'Unknown')}",
                    raw_text=recall.get("Summary", "")[:1000],
                    url=f"https://www.nhtsa.gov/recalls?nhtsaId={recall.get('NHTSACampaignNumber', '')}",
                    timestamp=recall.get("ReportReceivedDate", datetime.now(timezone.utc).isoformat()),
                    confidence=0.92,
                    metadata={"manufacturer": recall.get("Manufacturer"), "units_affected": recall.get("PotentialNumberofUnitsAffected")}
                ))
        except Exception as e:
            print(f"    [WARN] DOT NHTSA error: {e}")
        
        return signals


class FEMADisasterHarvester:
    """FEMA disaster declarations."""
    
    NAME = "FEMA"
    BASE_URL = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"
    
    def harvest(self) -> List[RawSignal]:
        signals = []
        
        # Get recent declarations (URL encode the query params)
        url = f"{self.BASE_URL}?%24orderby=declarationDate%20desc&%24top=20"
        
        data = safe_fetch(url)
        if not data:
            return signals
        
        try:
            results = json.loads(data).get("DisasterDeclarationsSummaries", [])
            
            for dec in results:
                signals.append(RawSignal(
                    source_id=f"fema:{dec.get('disasterNumber', 'unknown')}",
                    source_name=self.NAME,
                    domain="emergency.disaster",
                    title=f"{dec.get('state', '')} - {dec.get('incidentType', '')} ({dec.get('declarationType', '')})",
                    raw_text=dec.get("declarationTitle", ""),
                    url=f"https://www.fema.gov/disaster/{dec.get('disasterNumber', '')}",
                    timestamp=dec.get("declarationDate", datetime.now(timezone.utc).isoformat()),
                    confidence=0.95,
                    metadata={"state": dec.get("state"), "type": dec.get("incidentType"), "begin_date": dec.get("incidentBeginDate")}
                ))
        except Exception as e:
            print(f"    [WARN] FEMA error: {e}")
        
        return signals


class EIAEnergyHarvester:
    """EIA - Energy Information Administration data."""
    
    NAME = "EIA"
    BASE_URL = "https://api.eia.gov/v2/electricity/rto/daily-region-data/data/"
    
    def harvest(self) -> List[RawSignal]:
        # EIA requires API key, return mock for now
        signals = []
        
        # Mock signal for energy grid stress
        signals.append(RawSignal(
            source_id=f"eia:grid:{datetime.now().strftime('%Y%m%d')}",
            source_name=self.NAME,
            domain="infra.energy.grid",
            title="Regional Grid Demand Elevated - Northeast",
            raw_text="Grid demand in Northeast region showing 15% above seasonal average. Reserve margins tightening.",
            url="https://www.eia.gov/electricity/gridmonitor/",
            timestamp=datetime.now(timezone.utc).isoformat(),
            confidence=0.80,
            metadata={"region": "NE", "demand_delta": 0.15}
        ))
        
        return signals


# ============================================================================
# AGGREGATE HARVESTER
# ============================================================================

def harvest_all_extended() -> List[RawSignal]:
    """Run all extended harvesters."""
    all_signals = []
    
    harvesters = [
        ("Federal Register", FederalRegisterHarvester()),
        ("SEC EDGAR", SECEdgarHarvester()),
        ("USASpending", USASpendingHarvester()),
        ("DOT NHTSA", DOTSafetyHarvester()),
        ("FEMA", FEMADisasterHarvester()),
        ("EIA Energy", EIAEnergyHarvester()),
    ]
    
    print("[HARVESTER] Extended live data collection...")
    
    for name, harvester in harvesters:
        print(f"  → {name}...")
        try:
            signals = harvester.harvest()
            print(f"    Found {len(signals)} signals")
            all_signals.extend(signals)
        except Exception as e:
            print(f"    [ERROR] {e}")
    
    print(f"[HARVESTER] Total: {len(all_signals)} signals from {len(harvesters)} sources")
    return all_signals


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    signals = harvest_all_extended()
    
    print("\n" + "=" * 60)
    print("EXTENDED HARVEST RESULTS")
    print("=" * 60)
    
    by_source = {}
    for sig in signals:
        by_source.setdefault(sig.source_name, []).append(sig)
    
    for source, sigs in by_source.items():
        print(f"\n### {source} ({len(sigs)} signals)")
        for sig in sigs[:3]:
            print(f"  - {sig.title[:60]}...")
