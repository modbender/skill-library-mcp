#!/usr/bin/env python3
"""
Git Federation Searcher
Searches across multiple self-hosted Git instances

Usage:
    /gitsearch [query]              - Search all configured instances
    /gitinstances                   - List configured Git instances
    /gitadd [name] [url] [type]     - Add a Git instance
"""

import json
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, quote

# Data storage
SKILL_DIR = Path("/root/.openclaw/workspace/skills/git-federation-searcher")
CONFIG_FILE = SKILL_DIR / "instances.json"
CACHE_FILE = SKILL_DIR / "search_cache.json"

@dataclass
class GitInstance:
    """Represents a Git instance"""
    name: str
    url: str
    type: str  # gitea, forgejo, gitlab, gogs, sourcehut
    enabled: bool = True
    api_token: str = ""
    search_api: str = "/api/v1/repos/search"
    added_at: str = ""
    
    def __post_init__(self):
        if not self.added_at:
            from datetime import datetime
            self.added_at = datetime.now().isoformat()


# Default instances (well-known public ones)
DEFAULT_INSTANCES = {
    "codeberg": GitInstance(
        name="Codeberg",
        url="https://codeberg.org",
        type="gitea",
        search_api="/api/v1/repos/search"
    ),
    "gitea_com": GitInstance(
        name="Gitea.com",
        url="https://gitea.com",
        type="gitea",
        search_api="/api/v1/repos/search"
    ),
    "opendev": GitInstance(
        name="OpenDev",
        url="https://opendev.org",
        type="gitea",
        search_api="/api/v1/repos/search"
    ),
    "notabug": GitInstance(
        name="NotABug",
        url="https://notabug.org",
        type="gogs",
        search_api="/api/v1/repos/search"
    ),
    "gitdab": GitInstance(
        name="Gitdab",
        url="https://gitdab.com",
        type="forgejo",
        search_api="/api/v1/repos/search"
    ),
}


class GitFederationSearcher:
    """Searches across multiple Git instances"""
    
    def __init__(self):
        self.instances: Dict[str, GitInstance] = {}
        self.load_config()
    
    def load_config(self):
        """Load configured instances"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    for name, inst_data in data.items():
                        self.instances[name] = GitInstance(**inst_data)
            except:
                self.instances = dict(DEFAULT_INSTANCES)
        else:
            self.instances = dict(DEFAULT_INSTANCES)
            self.save_config()
    
    def save_config(self):
        """Save configured instances"""
        SKILL_DIR.mkdir(parents=True, exist_ok=True)
        data = {name: asdict(inst) for name, inst in self.instances.items()}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_instance(self, name: str, url: str, inst_type: str = "gitea", api_token: str = "") -> bool:
        """Add a new Git instance"""
        # Remove trailing slash
        url = url.rstrip('/')
        
        # Detect type from URL if not specified
        if inst_type == "auto":
            inst_type = self._detect_type(url)
        
        instance = GitInstance(
            name=name,
            url=url,
            type=inst_type,
            api_token=api_token
        )
        
        # Test connection
        if self._test_instance(instance):
            self.instances[name.lower().replace(" ", "_")] = instance
            self.save_config()
            return True
        return False
    
    def _detect_type(self, url: str) -> str:
        """Try to detect Git instance type"""
        try:
            result = subprocess.run(
                ["curl", "-s", "-m", "5", f"{url}/api/v1/version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if "version" in data:
                    return "gitea"  # Both Gitea and Forgejo use same API
        except:
            pass
        
        # Try GitLab
        try:
            result = subprocess.run(
                ["curl", "-s", "-m", "5", f"{url}/api/v4/version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return "gitlab"
        except:
            pass
        
        return "gitea"  # Default
    
    def _test_instance(self, instance: GitInstance) -> bool:
        """Test if instance is reachable"""
        try:
            result = subprocess.run(
                ["curl", "-s", "-m", "5", "-o", "/dev/null", "-w", "%{http_code}", 
                 f"{instance.url}/api/v1/version"],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() in ["200", "401", "403"]
        except:
            return False
    
    def search_instance(self, instance: GitInstance, query: str, limit: int = 10) -> List[dict]:
        """Search a single instance"""
        results = []
        
        if not instance.enabled:
            return results
        
        try:
            if instance.type in ["gitea", "forgejo", "gogs"]:
                # Gitea/Forgejo/Gogs API
                encoded_query = quote(query)
                url = f"{instance.url}{instance.search_api}?q={encoded_query}&limit={limit}"
                
                if instance.api_token:
                    url += f"&access_token={instance.api_token}"
                
                result = subprocess.run(
                    ["curl", "-s", "-m", "10", url],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    repos = data.get("data", []) if "data" in data else data
                    
                    for repo in repos[:limit]:
                        results.append({
                            "name": repo.get("full_name", repo.get("name")),
                            "url": repo.get("html_url", repo.get("url")),
                            "description": repo.get("description", "")[:100],
                            "stars": repo.get("stars_count", 0),
                            "forks": repo.get("forks_count", 0),
                            "language": repo.get("language", "-"),
                            "instance": instance.name,
                            "type": instance.type,
                            "updated": repo.get("updated_at", "")[:10]
                        })
            
            elif instance.type == "gitlab":
                # GitLab API
                encoded_query = quote(query)
                url = f"{instance.url}/api/v4/projects?search={encoded_query}&per_page={limit}"
                
                if instance.api_token:
                    url += f"&private_token={instance.api_token}"
                
                result = subprocess.run(
                    ["curl", "-s", "-m", "10", url],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    repos = json.loads(result.stdout)
                    
                    for repo in repos[:limit]:
                        results.append({
                            "name": repo.get("path_with_namespace"),
                            "url": repo.get("web_url"),
                            "description": repo.get("description", "")[:100],
                            "stars": repo.get("star_count", 0),
                            "forks": repo.get("forks_count", 0),
                            "language": repo.get("language", "-"),
                            "instance": instance.name,
                            "type": instance.type,
                            "updated": repo.get("last_activity_at", "")[:10]
                        })
        
        except Exception as e:
            results.append({
                "error": str(e),
                "instance": instance.name
            })
        
        return results
    
    def search_all(self, query: str, limit_per_instance: int = 5) -> Tuple[List[dict], dict]:
        """Search all enabled instances"""
        all_results = []
        stats = {"total": 0, "by_instance": {}, "errors": []}
        
        for name, instance in self.instances.items():
            if not instance.enabled:
                continue
            
            results = self.search_instance(instance, query, limit_per_instance)
            
            if results and "error" not in results[0]:
                all_results.extend(results)
                stats["by_instance"][instance.name] = len(results)
                stats["total"] += len(results)
            elif results:
                stats["errors"].append(f"{instance.name}: {results[0].get('error')}")
        
        # Sort by stars
        all_results.sort(key=lambda x: x.get("stars", 0), reverse=True)
        
        return all_results, stats
    
    def search_with_fallback(self, query: str) -> List[dict]:
        """Search instances, fall back to web search"""
        results, stats = self.search_all(query)
        
        # If no results from instances, try web search
        if not results:
            web_results = self._web_search(query)
            return [{"web_results": web_results}]
        
        return results
    
    def _web_search(self, query: str) -> List[dict]:
        """Fallback web search via SearXNG"""
        results = []
        
        try:
            search_query = f"site:codeberg.org OR site:gitea.com OR site:notabug.org {query}"
            cmd = f'SEARXNG_URL=http://127.0.0.1:8080 python3 /root/.openclaw/workspace/skills/searxng-bangs/scripts/search.py "{search_query}" --num 10'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for res in data.get("results", []):
                    # Determine instance from URL
                    url = res["url"]
                    instance = "unknown"
                    if "codeberg.org" in url:
                        instance = "Codeberg"
                    elif "gitea.com" in url:
                        instance = "Gitea.com"
                    elif "notabug.org" in url:
                        instance = "NotABug"
                    elif "gitdab.com" in url:
                        instance = "Gitdab"
                    
                    results.append({
                        "name": res["title"],
                        "url": res["url"],
                        "description": res["content"][:100],
                        "instance": instance,
                        "type": "web_search"
                    })
        except:
            pass
        
        return results
    
    def list_instances(self) -> List[dict]:
        """List all configured instances"""
        result = []
        for name, inst in self.instances.items():
            result.append({
                "name": inst.name,
                "url": inst.url,
                "type": inst.type,
                "enabled": inst.enabled,
                "status": "✅" if self._test_instance(inst) else "❌"
            })
        return result
    
    def enable_instance(self, name: str) -> bool:
        """Enable an instance"""
        if name in self.instances:
            self.instances[name].enabled = True
            self.save_config()
            return True
        return False
    
    def disable_instance(self, name: str) -> bool:
        """Disable an instance"""
        if name in self.instances:
            self.instances[name].enabled = False
            self.save_config()
            return True
        return False
    
    def remove_instance(self, name: str) -> bool:
        """Remove an instance"""
        if name in self.instances and name not in DEFAULT_INSTANCES:
            del self.instances[name]
            self.save_config()
            return True
        return False


def format_search_results(results: List[dict], query: str) -> str:
    """Format results for display"""
    text = f"🔍 **Git-Suche: \"{query}\"**\n\n"
    
    # Group by instance
    by_instance = {}
    for r in results:
        if "error" in r:
            continue
        inst = r.get("instance", "Unknown")
        if inst not in by_instance:
            by_instance[inst] = []
        by_instance[inst].append(r)
    
    # Format each instance
    for instance, repos in by_instance.items():
        text += f"📦 **{instance}** ({len(repos)} Ergebnisse)\n"
        
        for i, repo in enumerate(repos[:3], 1):  # Max 3 per instance
            text += f"  {i}. [{repo['name']}]({repo['url']})\n"
            if repo.get('description'):
                text += f"     _{repo['description'][:60]}..._\n"
            text += f"     ⭐ {repo.get('stars', 0)} | 🍴 {repo.get('forks', 0)} | {repo.get('language', '-')}\n\n"
    
    return text


# Command line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Git Federation Searcher")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--list", "-l", action="store_true", help="List instances")
    parser.add_argument("--add", nargs=3, metavar=("NAME", "URL", "TYPE"), 
                       help="Add instance: name url type")
    parser.add_argument("--remove", help="Remove instance")
    parser.add_argument("--disable", help="Disable instance")
    parser.add_argument("--enable", help="Enable instance")
    parser.add_argument("--limit", "-n", type=int, default=5, help="Results per instance")
    
    args = parser.parse_args()
    
    searcher = GitFederationSearcher()
    
    if args.list:
        instances = searcher.list_instances()
        print("🌍 Konfigurierte Git-Instanzen:\n")
        for inst in instances:
            status = "✅" if inst["enabled"] else "❌"
            print(f"{status} {inst['name']} ({inst['type']})")
            print(f"   URL: {inst['url']}")
            print(f"   Erreichbar: {inst['status']}\n")
    
    elif args.add:
        name, url, inst_type = args.add
        if searcher.add_instance(name, url, inst_type):
            print(f"✅ Instanz '{name}' hinzugefügt!")
        else:
            print(f"❌ Konnte Instanz '{name}' nicht erreichen")
    
    elif args.remove:
        if searcher.remove_instance(args.remove):
            print(f"✅ Instanz '{args.remove}' entfernt")
        else:
            print(f"❌ Konnte '{args.remove}' nicht entfernen (oder ist Standard)")
    
    elif args.disable:
        if searcher.disable_instance(args.disable):
            print(f"✅ Instanz '{args.disable}' deaktiviert")
        else:
            print(f"❌ Instanz nicht gefunden")
    
    elif args.enable:
        if searcher.enable_instance(args.enable):
            print(f"✅ Instanz '{args.enable}' aktiviert")
        else:
            print(f"❌ Instanz nicht gefunden")
    
    elif args.query:
        results, stats = searcher.search_all(args.query, args.limit)
        
        if results:
            print(format_search_results(results, args.query))
            print(f"\n📊 {stats['total']} Ergebnisse aus {len(stats['by_instance'])} Instanzen")
        else:
            print(f"❌ Keine Ergebnisse für '{args.query}'")
            print("\nVersuche Web-Suche...")
            web = searcher._web_search(args.query)
            if web:
                print(f"🌐 {len(web)} Web-Ergebnisse gefunden")
                for r in web[:3]:
                    print(f"  • {r['name']}")
                    print(f"    {r['url']}\n")
    
    else:
        parser.print_help()
