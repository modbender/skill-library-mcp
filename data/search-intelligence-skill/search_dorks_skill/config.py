"""
Configuration: 90+ SearXNG engines, operator support, dork templates,
intent keyword maps, and engine-category routing tables.
"""

# ─── SearXNG engine → category mapping ───────────────────────────────────────

ENGINE_CATEGORIES: dict[str, list[str]] = {
    # General search
    "general": [
        "google", "bing", "duckduckgo", "brave", "qwant", "startpage",
        "mojeek", "yandex", "yahoo", "presearch", "wiby", "stract", "yep",
        "right_dao", "mwmbl", "ask", "search_ch", "naver", "baidu",
    ],
    # IT / Developer
    "it": [
        "github", "stackoverflow", "gitlab", "npm", "pypi", "dockerhub",
        "arch_linux_wiki", "gentoo", "askubuntu", "superuser", "serverfault",
        "codeberg", "crates_io", "hex", "hackage", "hoogle", "lib_rs",
        "manjaro_wiki", "nixos_wiki", "packagist", "pkg_go_dev", "pub_dev",
        "rubygems", "void_linux", "bitbucket", "sourcehut",
    ],
    # Science / Academic
    "science": [
        "arxiv", "google_scholar", "semantic_scholar", "crossref", "pubmed",
        "base", "openalex", "core", "inspire", "wolfram_alpha", "pdbe",
        "openretractions", "fatcat",
    ],
    # News
    "news": [
        "google_news", "bing_news", "yahoo_news", "brave_news", "wikinews",
        "duckduckgo_news", "qwant_news", "presearch_news", "yandex_news",
        "bing_news", "tagesschau", "npr", "reuters",
    ],
    # Social
    "social_media": [
        "reddit", "lemmy", "mastodon", "hacker_news", "lobsters",
        "piped", "sepiasearch", "9gag", "habrahabr",
    ],
    # Images
    "images": [
        "google_images", "bing_images", "brave_images", "duckduckgo_images",
        "qwant_images", "flickr", "unsplash", "deviantart", "openverse",
        "wallhaven", "imgur", "pinterest", "tineye",
    ],
    # Videos
    "videos": [
        "youtube", "google_videos", "bing_videos", "brave_videos",
        "duckduckgo_videos", "dailymotion", "vimeo", "piped",
        "sepiasearch", "rumble", "odysee", "peertube",
    ],
    # Files
    "files": [
        "piratebay", "1337x", "nyaa", "kickass", "solidtorrents",
        "bt4g", "btdigg", "annas_archive", "z_library", "library_genesis",
    ],
    # Music
    "music": [
        "bandcamp", "genius", "mixcloud", "radio_browser",
        "soundcloud", "youtube_music", "invidious",
    ],
    # Maps
    "map": [
        "openstreetmap", "apple_maps", "google_maps", "photon",
    ],
    # Wikis
    "wikis": [
        "wikipedia", "wikidata", "wikimedia_commons", "wikibooks",
        "wikiquote", "wikisource", "wikispecies", "wikiversity",
        "wikivoyage", "wiktionary",
    ],
    # Translation / Language
    "language": [
        "dictzone", "lingva", "mymemory", "wordnik", "etymonline",
    ],
    # Currency / Finance
    "finance": [
        "currency", "yahoo_finance", "wallstreetzen",
    ],
}

# Flat set of all known engines
ALL_ENGINES: set[str] = set()
for _engines in ENGINE_CATEGORIES.values():
    ALL_ENGINES.update(_engines)


# ─── Operator support per engine family ───────────────────────────────────────

OPERATOR_SUPPORT: dict[str, dict[str, str]] = {
    "google": {
        "site": "site:{value}",
        "filetype": "filetype:{value}",
        "intitle": "intitle:{value}",
        "allintitle": "allintitle:{value}",
        "inurl": "inurl:{value}",
        "allinurl": "allinurl:{value}",
        "intext": "intext:{value}",
        "allintext": "allintext:{value}",
        "inanchor": "inanchor:{value}",
        "cache": "cache:{value}",
        "related": "related:{value}",
        "info": "info:{value}",
        "define": "define:{value}",
        "around": "AROUND({value})",
        "before": "before:{value}",
        "after": "after:{value}",
        "exact": '"{value}"',
        "exclude": "-{value}",
        "or": "{a} OR {b}",
        "wildcard": "*",
        "numrange": "{a}..{b}",
    },
    "bing": {
        "site": "site:{value}",
        "filetype": "filetype:{value}",
        "intitle": "intitle:{value}",
        "inurl": "inurl:{value}",
        "inbody": "inbody:{value}",
        "contains": "contains:{value}",
        "ip": "ip:{value}",
        "language": "language:{value}",
        "loc": "loc:{value}",
        "prefer": "prefer:{value}",
        "feed": "feed:{value}",
        "exact": '"{value}"',
        "exclude": "-{value}",
        "or": "{a} OR {b}",
        "near": "NEAR:{value}",
    },
    "duckduckgo": {
        "site": "site:{value}",
        "filetype": "filetype:{value}",
        "intitle": "intitle:{value}",
        "inurl": "inurl:{value}",
        "exact": '"{value}"',
        "exclude": "-{value}",
        "or": "{a} OR {b}",
    },
    "yandex": {
        "site": "site:{value}",
        "mime": "mime:{value}",
        "title": "title:{value}",
        "inurl": "inurl:{value}",
        "host": "host:{value}",
        "domain": "domain:{value}",
        "lang": "lang:{value}",
        "date": "date:{value}",
        "exact": '"{value}"',
        "exclude": "-{value}",
        "or": "{a} | {b}",
    },
    "brave": {
        "site": "site:{value}",
        "filetype": "filetype:{value}",
        "intitle": "intitle:{value}",
        "inurl": "inurl:{value}",
        "exact": '"{value}"',
        "exclude": "-{value}",
        "or": "{a} OR {b}",
    },
}

# Operator aliases for cross-engine translation
OPERATOR_ALIASES: dict[str, dict[str, str]] = {
    "filetype": {"yandex": "mime"},
    "intitle":  {"yandex": "title"},
    "intext":   {"bing": "inbody"},
}


# ─── Intent keyword scoring ──────────────────────────────────────────────────

INTENT_SIGNALS: dict[str, dict[str, float]] = {
    "security": {
        "keywords": 1.0,
        "_keywords": [
            "vulnerability", "vulnerabilities", "vuln", "cve", "exploit",
            "exposed", "leak", "leaked", "breach", "hack", "pentest",
            "penetration", "injection", "xss", "sqli", "rce", "lfi", "rfi",
            "ssrf", "csrf", "bug bounty", "admin panel", "login page",
            "directory listing", "index of", "open port", "shodan",
            "sensitive", "credentials", "api key", "secret key",
            "private key", "password", "database dump", "backup file",
            ".env", ".git", ".svn", ".htaccess", "robots.txt",
            "misconfiguration", "insecure", "unprotected",
        ],
    },
    "seo": {
        "keywords": 1.0,
        "_keywords": [
            "seo", "backlink", "backlinks", "serp", "ranking", "indexed",
            "indexation", "sitemap", "canonical", "noindex", "nofollow",
            "hreflang", "meta description", "title tag", "keyword density",
            "domain authority", "page authority", "organic traffic",
            "competitor analysis", "content audit", "technical seo",
            "schema markup", "structured data", "core web vitals",
            "search console", "crawl", "robots.txt",
        ],
    },
    "osint": {
        "keywords": 1.0,
        "_keywords": [
            "osint", "investigate", "investigation", "dox", "doxx",
            "who is", "whois", "lookup", "find person", "track",
            "trace", "identify", "reconnaissance", "recon",
            "social media", "profile", "footprint", "digital footprint",
            "email lookup", "phone lookup", "username", "real name",
            "background check", "public records", "linkedin",
        ],
    },
    "academic": {
        "keywords": 1.0,
        "_keywords": [
            "research", "paper", "papers", "journal", "arxiv", "doi",
            "citation", "cite", "peer reviewed", "study", "thesis",
            "dissertation", "abstract", "methodology", "findings",
            "literature review", "meta-analysis", "experiment",
            "hypothesis", "scholar", "academic", "university",
            "conference", "proceedings", "publication", "dataset",
        ],
    },
    "code": {
        "keywords": 1.0,
        "_keywords": [
            "github", "gitlab", "code", "repository", "repo", "library",
            "framework", "package", "module", "npm", "pypi", "pip",
            "crate", "gem", "api", "sdk", "documentation", "docs",
            "stackoverflow", "stack overflow", "programming", "developer",
            "bug", "issue", "pull request", "commit", "open source",
            "implementation", "algorithm", "function", "class",
        ],
    },
    "files": {
        "keywords": 1.0,
        "_keywords": [
            "download", "file", "filetype", "pdf", "doc", "docx",
            "spreadsheet", "csv", "excel", "powerpoint", "pptx",
            "ebook", "epub", "torrent", "archive", "zip", "rar",
            "dataset", "database", "dump", "backup",
        ],
    },
    "news": {
        "keywords": 1.0,
        "_keywords": [
            "news", "latest", "breaking", "today", "yesterday",
            "this week", "current", "recent", "update", "announcement",
            "press release", "report", "headline", "developing",
            "happening", "trend", "trending",
        ],
    },
    "images": {
        "keywords": 1.0,
        "_keywords": [
            "image", "images", "photo", "photos", "picture", "pictures",
            "wallpaper", "screenshot", "logo", "icon", "illustration",
            "infographic", "meme", "visual", "gallery",
        ],
    },
    "videos": {
        "keywords": 1.0,
        "_keywords": [
            "video", "videos", "watch", "youtube", "tutorial",
            "how to", "walkthrough", "demo", "demonstration",
            "stream", "clip", "movie", "documentary",
        ],
    },
    "social": {
        "keywords": 1.0,
        "_keywords": [
            "reddit", "twitter", "mastodon", "forum", "discussion",
            "thread", "community", "subreddit", "hashtag", "post",
            "comment", "opinion", "review", "feedback",
        ],
    },
    "shopping": {
        "keywords": 1.0,
        "_keywords": [
            "buy", "price", "cheap", "deal", "discount", "coupon",
            "shop", "store", "product", "review", "comparison",
            "best", "top", "vs", "versus", "alternative",
        ],
    },
    "legal": {
        "keywords": 1.0,
        "_keywords": [
            "law", "legal", "court", "case", "statute", "regulation",
            "compliance", "patent", "trademark", "copyright",
            "license", "terms of service", "privacy policy", "gdpr",
        ],
    },
    "medical": {
        "keywords": 1.0,
        "_keywords": [
            "medical", "health", "disease", "symptom", "treatment",
            "diagnosis", "clinical", "trial", "drug", "medication",
            "patient", "pubmed", "ncbi", "nih",
        ],
    },
}


# ─── Engine routing for each intent category ─────────────────────────────────

INTENT_ENGINE_MAP: dict[str, dict] = {
    "general": {
        "engines": ["google", "bing", "duckduckgo", "brave"],
        "categories": ["general"],
        "fallback_engines": ["qwant", "startpage", "mojeek"],
    },
    "security": {
        "engines": ["google", "bing", "duckduckgo", "brave"],
        "categories": ["general", "it"],
        "fallback_engines": ["yandex", "startpage"],
    },
    "seo": {
        "engines": ["google", "bing", "brave", "yandex"],
        "categories": ["general"],
        "fallback_engines": ["duckduckgo", "qwant"],
    },
    "osint": {
        "engines": ["google", "bing", "duckduckgo", "brave", "yandex"],
        "categories": ["general", "social_media"],
        "fallback_engines": ["startpage", "qwant"],
    },
    "academic": {
        "engines": ["google_scholar", "arxiv", "semantic_scholar", "crossref",
                     "pubmed", "base", "openalex", "core"],
        "categories": ["science", "general"],
        "fallback_engines": ["google", "bing"],
    },
    "code": {
        "engines": ["github", "stackoverflow", "gitlab", "npm", "pypi",
                     "dockerhub", "crates_io", "packagist", "pkg_go_dev"],
        "categories": ["it", "general"],
        "fallback_engines": ["google", "bing", "duckduckgo"],
    },
    "files": {
        "engines": ["google", "bing", "annas_archive", "z_library",
                     "piratebay", "1337x", "solidtorrents"],
        "categories": ["general", "files"],
        "fallback_engines": ["duckduckgo", "brave"],
    },
    "news": {
        "engines": ["google_news", "bing_news", "brave_news",
                     "duckduckgo_news", "yahoo_news", "wikinews"],
        "categories": ["news"],
        "fallback_engines": ["google", "bing"],
    },
    "images": {
        "engines": ["google_images", "bing_images", "brave_images",
                     "duckduckgo_images", "flickr", "unsplash", "openverse"],
        "categories": ["images"],
        "fallback_engines": ["qwant_images"],
    },
    "videos": {
        "engines": ["youtube", "google_videos", "bing_videos",
                     "brave_videos", "dailymotion", "vimeo", "piped"],
        "categories": ["videos"],
        "fallback_engines": ["duckduckgo_videos", "sepiasearch"],
    },
    "social": {
        "engines": ["reddit", "lemmy", "mastodon", "hacker_news", "lobsters"],
        "categories": ["social_media", "general"],
        "fallback_engines": ["google", "bing"],
    },
    "shopping": {
        "engines": ["google", "bing", "brave", "duckduckgo"],
        "categories": ["general"],
        "fallback_engines": ["yahoo", "qwant"],
    },
    "legal": {
        "engines": ["google", "bing", "duckduckgo"],
        "categories": ["general"],
        "fallback_engines": ["brave", "startpage"],
    },
    "medical": {
        "engines": ["pubmed", "google_scholar", "google", "bing"],
        "categories": ["science", "general"],
        "fallback_engines": ["duckduckgo", "semantic_scholar"],
    },
}


# ─── Dork templates organized by intent.subcategory ──────────────────────────

DORK_TEMPLATES: dict[str, dict[str, list[str]]] = {
    "security": {
        "exposed_files": [
            'site:{domain} filetype:env',
            'site:{domain} filetype:env "DB_PASSWORD" OR "SECRET_KEY" OR "API_KEY"',
            'site:{domain} filetype:log',
            'site:{domain} filetype:sql "password"',
            'site:{domain} filetype:bak OR filetype:old OR filetype:backup',
            'site:{domain} filetype:conf OR filetype:cfg OR filetype:ini',
            'site:{domain} filetype:pem OR filetype:key',
            'site:{domain} filetype:json "api_key" OR "secret"',
        ],
        "directory_listing": [
            'site:{domain} intitle:"index of"',
            'site:{domain} intitle:"directory listing"',
            'site:{domain} "parent directory" "size" "last modified"',
            'site:{domain} intitle:"index of" "backup"',
        ],
        "admin_panels": [
            'site:{domain} inurl:admin',
            'site:{domain} inurl:login OR inurl:signin',
            'site:{domain} inurl:dashboard',
            'site:{domain} intitle:"admin" OR intitle:"login" OR intitle:"panel"',
            'site:{domain} inurl:wp-admin OR inurl:wp-login',
            'site:{domain} inurl:phpmyadmin OR inurl:adminer',
            'site:{domain} inurl:cpanel OR inurl:webmail',
        ],
        "sensitive_data": [
            'site:{domain} "password" filetype:txt OR filetype:log',
            'site:{domain} "-----BEGIN RSA PRIVATE KEY-----"',
            'site:{domain} "-----BEGIN OPENSSH PRIVATE KEY-----"',
            'site:{domain} "AWS_ACCESS_KEY_ID" OR "AKIA"',
            'site:{domain} "DATABASE_URL" OR "MONGO_URI" OR "REDIS_URL"',
            'site:{domain} "smtp" "password" filetype:cfg OR filetype:conf',
        ],
        "exposed_apis": [
            'site:{domain} inurl:"/api/" filetype:json',
            'site:{domain} inurl:swagger OR inurl:api-docs',
            'site:{domain} filetype:yaml "openapi" OR "swagger"',
            'site:{domain} inurl:graphql OR inurl:graphiql',
            'site:{domain} intitle:"API" "endpoints" OR "documentation"',
        ],
        "subdomains": [
            'site:*.{domain} -www.{domain}',
            '"{domain}" -site:{domain}',
            'inurl:{domain} -site:{domain}',
        ],
        "git_exposed": [
            'site:{domain} inurl:".git"',
            'site:{domain} inurl:".git/config"',
            'site:{domain} inurl:".svn"',
            'site:{domain} inurl:".hg"',
            'site:{domain} intitle:"index of" ".git"',
        ],
        "technology_stack": [
            'site:{domain} "powered by" OR "built with"',
            'site:{domain} filetype:xml "<?xml"',
            'site:{domain} "X-Powered-By" OR "Server:"',
            'site:{domain} "wp-content" OR "wp-includes"',
        ],
        "general": [
            '"{keyword}" vulnerability OR exploit OR CVE',
            '"{keyword}" "proof of concept" OR "PoC"',
            '"{keyword}" site:exploit-db.com',
            '"{keyword}" site:cve.mitre.org OR site:nvd.nist.gov',
            '"{keyword}" "security advisory"',
        ],
    },
    "seo": {
        "indexation": [
            'site:{domain}',
            'site:{domain} -www',
            'site:{domain} inurl:blog',
            'site:{domain} inurl:tag OR inurl:category',
            'site:{domain} filetype:xml inurl:sitemap',
        ],
        "backlinks": [
            '"{domain}" -site:{domain}',
            '"a href" "{domain}" -site:{domain}',
            'inanchor:"{keyword}" site:{domain}',
            'link:{domain}',
        ],
        "competitors": [
            'related:{domain}',
            '"{keyword}" -site:{domain}',
            'intitle:"{keyword}" -{domain}',
            'inurl:"{keyword}" -site:{domain}',
        ],
        "content_audit": [
            'site:{domain} intitle:"{keyword}"',
            'site:{domain} inurl:"{keyword}"',
            'site:{domain} "{keyword}"',
        ],
        "technical_seo": [
            'site:{domain} filetype:xml',
            'site:{domain} inurl:robots.txt',
            'site:{domain} "noindex"',
            'site:{domain} "canonical"',
            'site:{domain} "hreflang"',
            'site:{domain} "rel=alternate"',
        ],
        "general": [
            'site:{domain}',
            '"{domain}" -site:{domain}',
            'related:{domain}',
        ],
    },
    "osint": {
        "person": [
            '"{name}" site:linkedin.com',
            '"{name}" site:twitter.com OR site:x.com',
            '"{name}" site:facebook.com',
            '"{name}" site:instagram.com',
            '"{name}" site:github.com',
            '"{name}" site:medium.com',
            '"{name}" filetype:pdf',
            '"{name}" inurl:about OR inurl:profile OR inurl:bio',
            '"{name}" "email" OR "@"',
            '"{name}" "resume" OR "cv" filetype:pdf',
            '"{name}" "phone" OR "tel:" OR "contact"',
        ],
        "email": [
            '"{email}"',
            '"{email}" -site:{email_domain}',
            '"{email}" filetype:pdf OR filetype:doc OR filetype:xls',
            '"{email}" site:linkedin.com',
            '"{email}" site:github.com',
            '"@{email_domain}" site:linkedin.com',
            '"{email}" "password" OR "leak" OR "breach"',
        ],
        "username": [
            '"{username}" site:github.com',
            '"{username}" site:reddit.com',
            '"{username}" site:twitter.com OR site:x.com',
            '"{username}" site:instagram.com',
            '"{username}" site:youtube.com',
            '"{username}" site:keybase.io',
            '"{username}" site:medium.com',
            '"{username}" site:stackoverflow.com',
            'inurl:"{username}"',
        ],
        "domain_recon": [
            'site:{domain}',
            'site:*.{domain} -www',
            '"{domain}" -site:{domain}',
            '"{domain}" whois',
            '"{domain}" site:shodan.io',
            '"{domain}" "dns" OR "nameserver" OR "mx"',
            '"{domain}" "ssl" OR "certificate"',
            '"{domain}" site:censys.io OR site:crt.sh',
        ],
        "company": [
            '"{company}" site:linkedin.com/company',
            '"{company}" site:crunchbase.com',
            '"{company}" site:glassdoor.com',
            '"{company}" filetype:pdf "annual report"',
            '"{company}" "SEC filing" OR "10-K" OR "10-Q"',
            '"{company}" employees site:linkedin.com',
            '"{company}" "privacy policy"',
            '"{company}" site:github.com',
            '"{company}" "data breach" OR "incident"',
        ],
        "phone": [
            '"{phone}"',
            '"{phone}" "name" OR "address"',
            '"{phone}" site:whitepages.com OR site:truecaller.com',
            '"{phone}" site:facebook.com',
        ],
        "ip_address": [
            '"{ip}"',
            '"{ip}" site:shodan.io',
            '"{ip}" "abuse" OR "blacklist"',
            '"{ip}" "open port" OR "service"',
            '"{ip}" whois',
        ],
        "general": [
            '"{keyword}"',
            '"{keyword}" site:linkedin.com',
            '"{keyword}" "contact" OR "email" OR "phone"',
        ],
    },
    "academic": {
        "papers": [
            '"{keyword}" site:arxiv.org',
            '"{keyword}" filetype:pdf "abstract" "references"',
            '"{keyword}" "doi:" filetype:pdf',
            '"{keyword}" site:researchgate.net',
            '"{keyword}" site:academia.edu',
            '"{keyword}" "et al" filetype:pdf',
            '"{keyword}" site:*.edu filetype:pdf',
        ],
        "datasets": [
            '"{keyword}" filetype:csv',
            '"{keyword}" filetype:json "dataset"',
            '"{keyword}" site:kaggle.com',
            '"{keyword}" site:huggingface.co/datasets',
            '"{keyword}" site:zenodo.org',
            '"{keyword}" "dataset" "download"',
        ],
        "authors": [
            '"{author}" site:scholar.google.com',
            '"{author}" site:orcid.org',
            '"{author}" site:researchgate.net',
            '"{author}" "publications" OR "bibliography"',
        ],
        "general": [
            '"{keyword}" site:arxiv.org OR site:scholar.google.com',
            '"{keyword}" filetype:pdf "abstract"',
            '"{keyword}" "peer reviewed" OR "journal"',
        ],
    },
    "code": {
        "repositories": [
            '"{keyword}" site:github.com',
            '"{keyword}" site:gitlab.com',
            '"{keyword}" site:bitbucket.org',
            '"{keyword}" site:codeberg.org',
            '"{keyword}" site:sourcehut.org',
        ],
        "packages": [
            '"{keyword}" site:npmjs.com',
            '"{keyword}" site:pypi.org',
            '"{keyword}" site:crates.io',
            '"{keyword}" site:rubygems.org',
            '"{keyword}" site:packagist.org',
            '"{keyword}" site:pkg.go.dev',
        ],
        "documentation": [
            '"{keyword}" site:readthedocs.io',
            '"{keyword}" "documentation" OR "API reference"',
            '"{keyword}" "README" site:github.com',
            '"{keyword}" site:docs.*',
        ],
        "issues_bugs": [
            '"{keyword}" "bug" OR "issue" site:github.com',
            '"{keyword}" site:stackoverflow.com',
            '"{keyword}" "error" OR "exception" site:stackoverflow.com',
        ],
        "general": [
            '"{keyword}" site:github.com OR site:stackoverflow.com',
            '"{keyword}" "library" OR "framework" OR "package"',
        ],
    },
    "files": {
        "documents": [
            '"{keyword}" filetype:pdf',
            '"{keyword}" filetype:doc OR filetype:docx',
            '"{keyword}" filetype:ppt OR filetype:pptx',
            '"{keyword}" filetype:xls OR filetype:xlsx',
        ],
        "data": [
            '"{keyword}" filetype:csv',
            '"{keyword}" filetype:json',
            '"{keyword}" filetype:xml',
            '"{keyword}" filetype:sql',
        ],
        "media": [
            '"{keyword}" filetype:mp4 OR filetype:mkv',
            '"{keyword}" filetype:mp3 OR filetype:flac',
            '"{keyword}" filetype:jpg OR filetype:png OR filetype:svg',
        ],
        "archives": [
            '"{keyword}" filetype:zip OR filetype:rar OR filetype:7z',
            '"{keyword}" filetype:tar.gz OR filetype:tgz',
        ],
        "config": [
            '"{keyword}" filetype:yaml OR filetype:yml',
            '"{keyword}" filetype:toml',
            '"{keyword}" filetype:ini OR filetype:conf',
            '"{keyword}" filetype:env',
        ],
        "general": [
            '"{keyword}" filetype:pdf OR filetype:doc',
            '"{keyword}" "download"',
        ],
    },
    "news": {
        "recent": [
            '"{keyword}"',
        ],
        "analysis": [
            '"{keyword}" "analysis" OR "opinion" OR "editorial"',
            '"{keyword}" site:medium.com OR site:substack.com',
        ],
        "general": [
            '"{keyword}"',
        ],
    },
    "general": {
        "general": [
            '"{keyword}"',
            '{keyword}',
        ],
    },
}


# ─── Search strategy definitions ─────────────────────────────────────────────

STRATEGY_DEFINITIONS: dict[str, dict] = {
    "quick": {
        "description": "Single optimized query across best engines",
        "max_steps": 1,
        "max_queries_per_step": 2,
        "engines_per_step": 4,
    },
    "broad_to_narrow": {
        "description": "Start wide, refine based on results",
        "max_steps": 3,
        "max_queries_per_step": 3,
        "engines_per_step": 4,
    },
    "multi_angle": {
        "description": "Same topic from multiple query formulations",
        "max_steps": 2,
        "max_queries_per_step": 5,
        "engines_per_step": 4,
    },
    "deep_dive": {
        "description": "Exhaustive dork coverage for specific content types",
        "max_steps": 4,
        "max_queries_per_step": 6,
        "engines_per_step": 6,
    },
    "osint_chain": {
        "description": "Progressive OSINT — each step informs the next",
        "max_steps": 5,
        "max_queries_per_step": 8,
        "engines_per_step": 5,
    },
    "verify": {
        "description": "Cross-reference claims across multiple sources",
        "max_steps": 3,
        "max_queries_per_step": 4,
        "engines_per_step": 6,
    },
    "file_hunt": {
        "description": "Targeted file type search across all engines",
        "max_steps": 2,
        "max_queries_per_step": 8,
        "engines_per_step": 4,
    },
    "temporal": {
        "description": "Search across time periods for trend analysis",
        "max_steps": 4,
        "max_queries_per_step": 2,
        "engines_per_step": 3,
    },
}


# ─── Credibility scoring signals ─────────────────────────────────────────────

CREDIBILITY_BOOSTS: dict[str, float] = {
    # Trusted domains get score boosts
    ".gov": 1.5,
    ".edu": 1.4,
    ".org": 1.1,
    "wikipedia.org": 1.3,
    "arxiv.org": 1.4,
    "github.com": 1.2,
    "stackoverflow.com": 1.2,
    "scholar.google.com": 1.4,
    "pubmed.ncbi.nlm.nih.gov": 1.5,
    "reuters.com": 1.3,
    "apnews.com": 1.3,
}

CREDIBILITY_PENALTIES: dict[str, float] = {
    # Suspicious patterns get score penalties
    "spam": 0.3,
    "click here": 0.5,
    "free download": 0.6,
    "buy now": 0.7,
}