#!/usr/bin/env python3
"""
Scholar Research - Search Module
Searches across multiple open access academic sources
"""

import requests
import json
import time
from typing import List, Dict, Optional

# Source API endpoints
SOURCES = {
    "arxiv": {
        "base_url": "http://export.arxiv.org/api/query",
        "search_field": "all",
        "max_results": 50
    },
    "pubmed": {
        "base_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        "db": "pubmed"
    },
    "openalex": {
        "base_url": "https://api.openalex.org/works",
        "per_page": 50
    },
    "doaj": {
        "base_url": "https://doaj.org/api/v2/search/articles"
    },
    "core": {
        "base_url": "https://api.core.ac.uk/v3/works"
    },
    "semantic_scholar": {
        "base_url": "https://api.semanticscholar.org/graph/v1/paper/search",
        "limit": 50
    },
    "biorxiv": {
        "base_url": "https://api.biorxiv.org/details/biorxiv"
    },
    "medrxiv": {
        "base_url": "https://api.biorxiv.org/details/medrxiv"
    },
    "crossref": {
        "base_url": "https://api.crossref.org/works"
    },
    "ssrn": {
        "base_url": "https://papers.ssrn.com/sol3/Delivery.cfm"
    }
}


class ScholarSearch:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.results = []
        
    def search_arxiv(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search arXiv for papers"""
        import time
        import urllib.parse
        
        # Try multiple search formats
        search_queries = [
            f"all:{query}",
            f"ti:{query}",  # title
            f"abs:{query}",  # abstract
        ]
        
        for attempt in range(3):  # Retry 3 times
            try:
                for search_query in search_queries[:1]:  # Try main query first
                    params = {
                        "search_query": search_query,
                        "start": 0,
                        "max_results": max_results,
                        "sortBy": "relevance",
                        "sortOrder": "descending"
                    }
                    
                    response = requests.get(
                        SOURCES["arxiv"]["base_url"], 
                        params=params, 
                        timeout=60  # Increased timeout
                    )
                    
                    if response.status_code == 200:
                        return self._parse_arxiv_response(response.text, query)
                    
            except requests.exceptions.Timeout:
                print(f"arXiv timeout, retry {attempt + 1}/3...")
                time.sleep(2)
            except Exception as e:
                print(f"arXiv search error: {e}")
                break
        
        return []
    
    def search_pubmed(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search PubMed for papers"""
        # First search for IDs
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json"
        }
        
        try:
            # Get IDs
            search_resp = requests.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                params=search_params,
                timeout=30
            )
            search_data = search_resp.json()
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                return []
            
            # Fetch details
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(id_list[:max_results]),
                "retmode": "json"
            }
            
            fetch_resp = requests.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                params=fetch_params,
                timeout=30
            )
            
            return self._parse_pubmed_response(fetch_resp.json(), query)
        except Exception as e:
            print(f"PubMed search error: {e}")
            return []
    
    def search_openalex(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search OpenAlex for papers"""
        params = {
            "search": query,
            "per_page": max_results,
            "sort": "relevance_score:desc"
        }
        
        headers = {}
        if self.config.get("api", {}).get("openalex_token"):
            headers["Authorization"] = f"Bearer {self.config['api']['openalex_token']}"
        
        try:
            response = requests.get(
                SOURCES["openalex"]["base_url"],
                params=params,
                headers=headers,
                timeout=30
            )
            return self._parse_openalex_response(response.json(), query)
        except Exception as e:
            print(f"OpenAlex search error: {e}")
            return []
    
    def search_crossref(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search CrossRef for papers"""
        params = {
            "query": query,
            "rows": max_results,
            "select": "DOI,title,author,published,container-title,cited-by-count,license,type"
        }
        
        email = self.config.get("api", {}).get("crossref_email")
        if email:
            params["mailto"] = email
            
        try:
            response = requests.get(
                SOURCES["crossref"]["base_url"],
                params=params,
                timeout=30
            )
            return self._parse_crossref_response(response.json(), query)
        except Exception as e:
            print(f"CrossRef search error: {e}")
            return []
    
    def search_all(self, query: str, sources: List[str] = None) -> List[Dict]:
        """Search all enabled sources"""
        if sources is None:
            sources = self.config.get("sources", {}).get("enabled", 
                ["arxiv", "pubmed", "openalex", "crossref"])
        
        all_results = []
        
        source_map = {
            "arxiv": self.search_arxiv,
            "pubmed": self.search_pubmed,
            "openalex": self.search_openalex,
            "crossref": self.search_crossref,
        }
        
        for source in sources:
            if source in source_map:
                print(f"Searching {source}...")
                results = source_map[source](query)
                all_results.extend(results)
                time.sleep(0.5)  # Rate limiting
        
        # Deduplicate by DOI
        seen = set()
        unique_results = []
        for paper in all_results:
            doi = paper.get("doi", "") or ""
            if doi and doi.lower() not in seen:
                seen.add(doi.lower())
                unique_results.append(paper)
            elif not doi:
                # Keep non-DOI papers
                unique_results.append(paper)
        
        return unique_results
    
    def _parse_arxiv_response(self, xml_text: str, query: str) -> List[Dict]:
        """Parse arXiv ATOM response"""
        # Simplified - would use xml.etree.ElementTree in production
        results = []
        # Return structured list from XML
        return results
    
    def _parse_pubmed_response(self, data: dict, query: str) -> List[Dict]:
        """Parse PubMed response"""
        results = []
        papers = data.get("result", {})
        for pmid in papers:
            if pmid == "uids":
                continue
            paper = papers[pmid]
            results.append({
                "id": pmid,
                "doi": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "title": paper.get("title", ""),
                "authors": paper.get("authors", []),
                "published": paper.get("pubdate", ""),
                "journal": paper.get("source", ""),
                "citations": 0,  # PubMed doesn't provide citation counts in summary
                "pubtype": paper.get("pubtype", []),
                "source": "pubmed"
            })
        return results
    
    def _parse_openalex_response(self, data: dict, query: str) -> List[Dict]:
        """Parse OpenAlex response"""
        results = []
        for work in data.get("results", []):
            # Extract authors
            authors = []
            for a in work.get("authorships", [])[:5]:
                name = a.get("author", {}).get("display_name", "")
                if name:
                    authors.append(name)
            
            # Extract publication date
            pub_date = work.get("publication_date", "")
            
            # Extract citation count
            citations = work.get("cited_by_count", 0)
            if isinstance(citations, str):
                try:
                    citations = int(citations)
                except:
                    citations = 0
            
            # Open access
            oa = work.get("open_access", {})
            is_oa = oa.get("is_oa", False) if isinstance(oa, dict) else False
            
            results.append({
                "id": work.get("id", ""),
                "doi": work.get("doi", ""),
                "title": work.get("title", "Untitled"),
                "authors": authors,
                "published": pub_date,
                "journal": work.get("host_venue", {}).get("display_name", "") if isinstance(work.get("host_venue"), dict) else "",
                "citations": citations,
                "open_access": is_oa,
                "abstract": work.get("abstract", ""),
                "pdf_url": f"https://doi.org/{work.get('doi', '')}" if work.get("doi") else "",
                "source": "openalex"
            })
        return results
    
    def _parse_arxiv_response(self, xml_text: str, query: str) -> List[Dict]:
        """Parse arXiv ATOM XML response"""
        import re
        results = []
        
        try:
            # Extract entries using regex (simpler than full XML parsing)
            entries = re.findall(r'<entry>(.*?)</entry>', xml_text, re.DOTALL)
            
            for entry in entries:
                # Extract title
                title_match = re.search(r'<title>([^<]+)</title>', entry)
                title = title_match.group(1).strip() if title_match else "Untitled"
                
                # Extract abstract/summary
                summary_match = re.search(r'<summary>([^<]+)</summary>', entry)
                abstract = summary_match.group(1).strip() if summary_match else ""
                
                # Extract authors
                authors = re.findall(r'<name>([^<]+)</name>', entry)
                
                # Extract arXiv ID
                id_match = re.search(r'<id>http://arxiv\.org/abs/([^<]+)</id>', entry)
                arxiv_id = id_match.group(1).strip() if id_match else ""
                
                # Extract published date
                date_match = re.search(r'<published>([^<]+)</published>', entry)
                published = date_match.group(1)[:10] if date_match else ""  # Just YYYY-MM-DD
                
                # Extract DOI if available
                doi_match = re.search(r'<arxiv:doi>([^<]+)</arxiv:doi>', entry)
                doi = doi_match.group(1).strip() if doi_match else ""
                
                if title and title != "Untitled":
                    results.append({
                        "id": arxiv_id,
                        "doi": doi,
                        "title": title,
                        "authors": authors[:5],
                        "published": published,
                        "journal": "arXiv",
                        "citations": 0,
                        "open_access": True,
                        "abstract": abstract,
                        "arxiv_id": arxiv_id,
                        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else "",
                        "source": "arxiv"
                    })
                
        except Exception as e:
            print(f"arXiv parsing error: {e}")
        
        return results
    
    def _parse_crossref_response(self, data: dict, query: str) -> List[Dict]:
        """Parse CrossRef response"""
        results = []
        try:
            items = data.get("message", {}).get("items", [])
        except:
            items = []
        
        for item in items:
            # Extract authors properly
            authors = []
            for a in item.get("author", [])[:5]:
                name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                if name:
                    authors.append(name)
            
            # Extract publication date
            pub_date = ""
            if "published" in item:
                date_parts = item["published"].get("date-parts", [[None]])
                if date_parts and date_parts[0]:
                    pub_date = str(date_parts[0][0]) if date_parts[0][0] else ""
            
            # Extract citation count - CrossRef uses "is-referenced-by-count"
            citations = item.get("is-referenced-by-count", 0)
            if isinstance(citations, str):
                try:
                    citations = int(citations)
                except:
                    citations = 0
            
            results.append({
                "doi": item.get("DOI", ""),
                "title": item.get("title", [""])[0] if item.get("title") else "Untitled",
                "authors": authors,
                "published": pub_date,
                "journal": item.get("container-title", [""])[0] if item.get("container-title") else "",
                "citations": citations,
                "type": item.get("type", ""),
                "abstract": item.get("abstract", ""),
                "pdf_url": f"https://doi.org/{item.get('DOI', '')}" if item.get("DOI") else "",
                "source": "crossref"
            })
        return results


if __name__ == "__main__":
    import sys
    searcher = ScholarSearch()
    query = sys.argv[1] if len(sys.argv) > 1 else "machine learning"
    results = searcher.search_all(query)
    print(f"Found {len(results)} papers")
    for r in results[:5]:
        print(f"- {r.get('title', 'No title')[:60]}...")
