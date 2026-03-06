import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SECFiling:
    accession_number: str
    form: str
    filed_date: str
    report_date: Optional[str]
    primary_doc_url: str
    description: str

class SECFilingsClient:
    """Client for fetching SEC EDGAR filings."""
    
    BASE_URL = "https://www.sec.gov/Archives/edgar/daily-index"
    HEADERS = {
        "User-Agent": "BoringLife-FinanceSkill contact@boringlife.io"
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def get_cik(self, ticker: str) -> Optional[str]:
        """Convert ticker symbol to CIK."""
        url = "https://www.sec.gov/files/company_tickers.json"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            for entry in data.values():
                if entry["ticker"].upper() == ticker.upper():
                    return str(entry["cik_str"]).zfill(10)
            return None
        except Exception as e:
            print(f"Error fetching CIK: {e}")
            return None
    
    def get_recent_filings(
        self, 
        ticker: str, 
        form: Optional[str] = None,
        limit: int = 10,
        days_back: int = 365
    ) -> List[SECFiling]:
        """
        Get recent SEC filings for a ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")
            form: Specific form type (e.g., "10-K", "10-Q", "8-K")
            limit: Maximum number of filings to return
            days_back: How many days back to search
        """
        cik = self.get_cik(ticker)
        if not cik:
            return []
        
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Get submissions data for actual filings
            sub_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            sub_response = self.session.get(sub_url, timeout=15)
            sub_response.raise_for_status()
            sub_data = sub_response.json()
            
            filings = []
            recent = sub_data.get("filings", {}).get("recent", {})
            
            forms = recent.get("form", [])
            dates = recent.get("filingDate", [])
            acc_nums = recent.get("accessionNumber", [])
            descriptions = recent.get("primaryDocDescription", [])
            
            for i in range(len(forms)):  # Check all filings, not just first N
                if len(filings) >= limit:
                    break
                    
                if i >= len(forms):
                    break
                    
                filing_date = dates[i] if i < len(dates) else None
                
                # Check date range
                if filing_date:
                    try:
                        file_dt = datetime.strptime(filing_date, "%Y-%m-%d")
                        cutoff = datetime.now() - timedelta(days=days_back)
                        if file_dt < cutoff:
                            continue
                    except:
                        pass
                
                # Filter by form type if specified
                if form and forms[i] != form:
                    continue
                
                acc_num = acc_nums[i] if i < len(acc_nums) else ""
                acc_num_clean = acc_num.replace("-", "")
                
                doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_num_clean}/{acc_num}-index.htm"
                
                filing = SECFiling(
                    accession_number=acc_num,
                    form=forms[i],
                    filed_date=filing_date,
                    report_date=None,
                    primary_doc_url=doc_url,
                    description=descriptions[i] if i < len(descriptions) else ""
                )
                filings.append(filing)
                
                if len(filings) >= limit:
                    break
            
            return filings
            
        except Exception as e:
            print(f"Error fetching filings: {e}")
            return []
    
    def get_latest_10k_summary(self, ticker: str) -> Optional[Dict]:
        """Get summary of latest 10-K filing."""
        filings = self.get_recent_filings(ticker, form="10-K", limit=1)
        if not filings:
            return None
        
        filing = filings[0]
        return {
            "ticker": ticker.upper(),
            "form": filing.form,
            "filed_date": filing.filed_date,
            "document_url": filing.primary_doc_url,
            "description": filing.description
        }


def get_recent_filings(ticker: str, form: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """Convenience function to get recent filings as dicts."""
    client = SECFilingsClient()
    filings = client.get_recent_filings(ticker, form, limit)
    return [
        {
            "accession_number": f.accession_number,
            "form": f.form,
            "filed_date": f.filed_date,
            "document_url": f.primary_doc_url,
            "description": f.description
        }
        for f in filings
    ]


def get_latest_10k(ticker: str) -> Optional[Dict]:
    """Get latest 10-K filing summary."""
    client = SECFilingsClient()
    return client.get_latest_10k_summary(ticker)


if __name__ == "__main__":
    # Test
    print("Testing SEC filings for AAPL...")
    filings = get_recent_filings("AAPL", limit=5)
    for f in filings:
        print(f"{f['form']} filed on {f['filed_date']}: {f['document_url']}")
