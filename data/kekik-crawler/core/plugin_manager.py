import importlib.util
from pathlib import Path
from types import SimpleNamespace


def _fallback_extract(url: str, html: str, tree):
    return {"title": None, "text": "", "links": []}


class PluginManager:
    SEARCH_DOMAINS = {
        "duckduckgo.com",
        "html.duckduckgo.com",
        "www.bing.com",
        "search.yahoo.com",
        "search.brave.com",
    }

    def __init__(self, plugin_dir: Path):
        self.plugin_dir = plugin_dir
        self.default = self._load(plugin_dir / "default.py", "default") or SimpleNamespace(extract=_fallback_extract)
        self.search_results = self._load(plugin_dir / "search_results.py", "search_results")
        self.cache = {}

    def _load(self, path: Path, name: str):
        if not path.exists():
            return None
        spec = importlib.util.spec_from_file_location(f"plugins.{name}", path)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def for_domain(self, domain: str):
        domain = domain.lower()
        if domain in self.cache:
            return self.cache[domain]
        if domain in self.SEARCH_DOMAINS and self.search_results:
            self.cache[domain] = self.search_results
            return self.search_results
        mod = self._load(self.plugin_dir / f"{domain}.py", domain) or self.default
        self.cache[domain] = mod
        return mod
