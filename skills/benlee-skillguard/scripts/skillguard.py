#!/usr/bin/env python3
"""SkillGuard v2 — OpenClaw skill security scanner."""

import base64
import hashlib
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

# ── Colours ──────────────────────────────────────────────────────────────────

NO_COLOR = os.environ.get("NO_COLOR") is not None
def _c(code, text):
    return text if NO_COLOR else f"\033[{code}m{text}\033[0m"
RED    = lambda t: _c("91", t)
YELLOW = lambda t: _c("93", t)
GREEN  = lambda t: _c("92", t)
CYAN   = lambda t: _c("96", t)
BOLD   = lambda t: _c("1", t)
DIM    = lambda t: _c("2", t)

# ── Constants ────────────────────────────────────────────────────────────────

SKILLS_DIR = Path.home() / "clawd" / "skills"
BASELINES_PATH = Path.home() / "clawd" / "skills" / "skill-guard" / "baselines.json"
SCANNABLE_EXTS = {".py", ".js", ".ts", ".sh", ".md", ".json", ".svg", ".yml", ".yaml", ".toml", ".txt", ".cfg", ".ini", ".html", ".css"}
MAX_FILE_SIZE = 2 * 1024 * 1024
LARGE_FILE_THRESHOLD = 500 * 1024
MAX_FILE_COUNT = 50

VERSION = "2.0.0"

CRITICAL = "CRITICAL"
WARNING = "WARNING"
INFO = "INFO"

# ── Known-good domains ──────────────────────────────────────────────────────

KNOWN_DOMAINS = {
    "api.coingecko.com", "feeds.bbci.co.uk", "api.github.com",
    "query1.finance.yahoo.com", "query2.finance.yahoo.com",
    "api.openai.com", "discord.com", "api.telegram.org",
    "api.x.ai", "api.anthropic.com", "feeds.npr.org",
    "www.aljazeera.com", "www.reutersagency.com", "img402.dev",
    "snap.llm.kaveenk.com", "astral.sh", "pypi.org",
    "raw.githubusercontent.com", "github.com", "api.weatherapi.com",
    "api.openweathermap.org", "newsapi.org", "api.newsapi.org",
    "rss.nytimes.com", "www.reddit.com", "oauth.reddit.com",
    "api.spotify.com", "api.twitch.tv", "api.twitter.com",
    "graph.facebook.com", "www.googleapis.com", "maps.googleapis.com",
    "api.stripe.com", "api.slack.com", "hooks.slack.com",
    "api.notion.com", "api.pushover.net", "ntfy.sh",
    "api.elevenlabs.io", "api.deepl.com", "translate.googleapis.com",
    "api.wolframalpha.com", "en.wikipedia.org", "www.wikipedia.org",
    "api.dictionaryapi.dev", "api.urbandictionary.com",
    "itunes.apple.com", "api.exchangerate-api.com",
    "cdn.jsdelivr.net", "unpkg.com", "registry.npmjs.org",
    "crates.io", "rubygems.org", "hub.docker.com",
    "youtube.com", "www.youtube.com", "youtubetranscript.com",
    "i.ytimg.com", "yt3.ggpht.com",
    "stockanalysis.com", "www.stockanalysis.com",
    "finance.yahoo.com", "www.google.com",
    "api.binance.com", "pro-api.coinmarketcap.com",
    "invidious.io", "inv.tux.pizza", "vid.puffyan.us",
    "nitter.net", "bsky.social", "bsky.app",
    "localhost", "127.0.0.1", "0.0.0.0",
}

# Context keywords that justify certain API calls
DOMAIN_CONTEXT = {
    "coingecko": ["crypto", "coin", "price", "bitcoin", "ethereum", "defi", "token"],
    "yahoo": ["stock", "finance", "market", "ticker", "portfolio", "trading"],
    "weather": ["weather", "forecast", "temperature", "climate"],
    "news": ["news", "headline", "article", "feed", "rss", "bbc", "npr", "reuters"],
    "youtube": ["youtube", "video", "transcript", "subtitle"],
    "telegram": ["telegram", "bot", "chat", "message", "notification"],
    "discord": ["discord", "bot", "webhook"],
    "openai": ["ai", "gpt", "chat", "llm", "completion"],
    "anthropic": ["ai", "claude", "llm", "completion"],
    "github": ["git", "repo", "code", "commit", "pr", "issue"],
    "reddit": ["reddit", "subreddit", "post"],
    "spotify": ["music", "playlist", "song", "spotify"],
    "elevenlabs": ["voice", "tts", "speech", "audio"],
    "stockanalysis": ["stock", "finance", "market", "analysis"],
}

# ── Known packages for typosquatting ─────────────────────────────────────────

KNOWN_PACKAGES_PY = [
    "requests", "numpy", "pandas", "flask", "django", "scipy", "matplotlib",
    "urllib3", "certifi", "idna", "charset-normalizer", "setuptools", "pip",
    "cryptography", "pyyaml", "pillow", "boto3", "botocore", "jinja2",
    "click", "aiohttp", "sqlalchemy", "pytest", "beautifulsoup4", "lxml",
    "paramiko", "pycryptodome", "pyopenssl", "colorama", "tqdm",
]
KNOWN_PACKAGES_JS = [
    "express", "react", "lodash", "axios", "moment", "chalk", "commander",
    "webpack", "babel", "typescript", "eslint", "prettier", "jest", "mocha",
    "mongoose", "sequelize", "socket.io", "cors", "dotenv", "uuid",
    "jsonwebtoken", "bcrypt", "nodemon", "pm2", "puppeteer",
]
SUSPICIOUS_PACKAGES = {
    "event-stream", "flatmap-stream", "ua-parser-js", "coa", "rc",
    "colors", "faker",
}

# Hardcoded secrets patterns
SECRET_PATTERNS = [
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key"),
    (r'ghp_[A-Za-z0-9]{36}', "GitHub Personal Access Token"),
    (r'gho_[A-Za-z0-9]{36}', "GitHub OAuth Token"),
    (r'github_pat_[A-Za-z0-9_]{82}', "GitHub Fine-grained PAT"),
    (r'sk-[A-Za-z0-9]{20,}T3BlbkFJ[A-Za-z0-9]{20,}', "OpenAI API Key"),
    (r'sk-(?:proj|org)-[A-Za-z0-9\-_]{40,}', "OpenAI Project/Org Key"),
    (r'xox[boaprs]-[A-Za-z0-9\-]{10,}', "Slack Token"),
    (r'sk_live_[A-Za-z0-9]{24,}', "Stripe Secret Key"),
    (r'rk_live_[A-Za-z0-9]{24,}', "Stripe Restricted Key"),
    (r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----', "Private Key"),
    (r'AIza[0-9A-Za-z\-_]{35}', "Google API Key"),
]

# Unicode homoglyph detection
HOMOGLYPHS = {
    '\u0430': 'a', '\u0435': 'e', '\u043e': 'o', '\u0440': 'p',
    '\u0441': 'c', '\u0443': 'y', '\u0445': 'x', '\u0456': 'i',
    '\u0458': 'j', '\u04bb': 'h', '\u0455': 's', '\u0432': 'b',
    '\u043d': 'h', '\u0442': 't', '\u043c': 'm', '\u043a': 'k',
    '\u0433': 'r',
    '\u0251': 'a', '\u0261': 'g', '\u026f': 'm',
    '\u01c3': '!', '\u037e': ';',
    '\uff41': 'a', '\uff42': 'b', '\uff43': 'c', '\uff44': 'd',
    '\uff45': 'e', '\uff46': 'f',
}

# ── Binary magic bytes ───────────────────────────────────────────────────────

BINARY_MAGICS = [
    (b'\x7fELF', "ELF binary"),
    (b'\xfe\xed\xfa\xce', "Mach-O binary (32-bit)"),
    (b'\xfe\xed\xfa\xcf', "Mach-O binary (64-bit)"),
    (b'\xce\xfa\xed\xfe', "Mach-O binary (32-bit, reversed)"),
    (b'\xcf\xfa\xed\xfe', "Mach-O binary (64-bit, reversed)"),
    (b'MZ', "PE/Windows executable"),
    (b'\xca\xfe\xba\xbe', "Mach-O universal binary / Java class"),
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def levenshtein(a, b):
    if len(a) < len(b): return levenshtein(b, a)
    if len(b) == 0: return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (ca != cb)))
        prev = curr
    return prev[-1]

def safe_read(path, max_size=MAX_FILE_SIZE):
    try:
        if path.stat().st_size > max_size:
            return None
        return path.read_text(errors="replace")
    except Exception:
        return None

def is_scannable(path):
    return path.suffix.lower() in SCANNABLE_EXTS

def sha256_file(path):
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def extract_domains(text):
    """Extract domains from URLs in text."""
    domains = set()
    for m in re.finditer(r'https?://([a-zA-Z0-9._-]+(?:\.[a-zA-Z]{2,}))', text):
        domains.add(m.group(1).lower())
    return domains

def is_known_domain(domain):
    """Check if domain is in the known-good list."""
    domain = domain.lower().strip('.')
    if domain in KNOWN_DOMAINS:
        return True
    # Check if it's a subdomain of a known domain
    for known in KNOWN_DOMAINS:
        if domain.endswith('.' + known):
            return True
    return False

def domain_matches_context(domain, skill_name, skill_desc):
    """Check if domain usage makes sense for this skill."""
    context = (skill_name + " " + skill_desc).lower()
    for keyword, context_words in DOMAIN_CONTEXT.items():
        if keyword in domain.lower():
            if any(w in context for w in context_words):
                return True
    return False

def has_homoglyphs(text):
    """Check for Unicode homoglyph characters."""
    found = []
    for ch in text:
        if ch in HOMOGLYPHS:
            found.append((ch, HOMOGLYPHS[ch]))
    return found

def check_binary_magic(path):
    """Check if file starts with known binary magic bytes."""
    try:
        with open(path, 'rb') as f:
            header = f.read(8)
        for magic, desc in BINARY_MAGICS:
            if header.startswith(magic):
                return desc
    except Exception:
        pass
    return None

def get_skill_name(skill_dir):
    return skill_dir.name

def get_skill_description(skill_dir):
    sm = skill_dir / "SKILL.md"
    text = safe_read(sm) if sm.exists() else None
    if not text: return ""
    m = re.search(r'description:\s*(.+)', text[:2000], re.I)
    if m: return m.group(1).strip()
    lines = text.split('\n')
    for i, l in enumerate(lines):
        if l.startswith('#') and i + 1 < len(lines):
            for nl in lines[i+1:]:
                nl = nl.strip()
                if nl and not nl.startswith('#') and not nl.startswith('---'):
                    return nl[:200]
    return ""

# ── Baselines ────────────────────────────────────────────────────────────────

def load_baselines():
    if BASELINES_PATH.exists():
        try:
            return json.loads(BASELINES_PATH.read_text())
        except Exception:
            return {}
    return {}

def save_baselines(baselines):
    BASELINES_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINES_PATH.write_text(json.dumps(baselines, indent=2))

def compute_skill_hashes(skill_dir):
    """Compute SHA-256 of every file in a skill directory."""
    hashes = {}
    try:
        for p in sorted(skill_dir.rglob("*")):
            if p.is_file() and not any(part.startswith('.git') and part != '.clawhub' for part in p.parts):
                rel = str(p.relative_to(skill_dir))
                h = sha256_file(p)
                if h:
                    hashes[rel] = h
    except Exception:
        pass
    return hashes

# ── Scanner ──────────────────────────────────────────────────────────────────

class Finding:
    __slots__ = ('level', 'desc', 'file', 'line', 'recommendation', 'score_override')
    def __init__(self, level, desc, file="", line=0, recommendation="", score_override=None):
        self.level = level
        self.desc = desc
        self.file = file
        self.line = line
        self.recommendation = recommendation
        self.score_override = score_override

    def __repr__(self):
        loc = f" — {self.file}:{self.line}" if self.file else ""
        return f"[{self.level:8s}] {self.desc}{loc}"

    def to_dict(self):
        d = {"level": self.level, "description": self.desc}
        if self.file: d["file"] = self.file
        if self.line: d["line"] = self.line
        if self.recommendation: d["recommendation"] = self.recommendation
        return d


class SkillScanner:
    def __init__(self, skill_dir, check_baseline=True):
        self.skill_dir = Path(skill_dir)
        self.name = get_skill_name(self.skill_dir)
        self.desc = get_skill_description(self.skill_dir)
        self.findings = []
        self.files = []
        self.tamper_detected = False
        self.check_baseline = check_baseline
        self._collect_files()
        # Track what we find for combo detection
        self._has_sensitive_access = False
        self._has_outbound = False
        self._has_subprocess = False
        self._unknown_domains = set()
        self._known_domains_used = set()

    def _collect_files(self):
        try:
            for p in self.skill_dir.rglob("*"):
                if p.is_file() and not any(part.startswith('.git') and part != '.clawhub' for part in p.parts):
                    self.files.append(p)
        except Exception:
            pass

    def add(self, level, desc, file="", line=0, recommendation="", score_override=None):
        rel = str(file).replace(str(self.skill_dir) + "/", "") if file else ""
        self.findings.append(Finding(level, desc, rel, line, recommendation, score_override))

    def scan(self):
        self._trust_signals()
        self._check_file_permissions()
        self._check_binary_files()
        self._check_large_files()
        self._check_homoglyphs()

        for f in self.files:
            if is_scannable(f):
                text = safe_read(f)
                if text is None: continue
                lines = text.split('\n')
                ext = f.suffix.lower()
                if ext == ".md":
                    self._scan_prompt_injection(f, lines)
                if ext == ".json":
                    self._scan_json(f, text)
                if ext == ".svg":
                    self._scan_svg(f, text, lines)
                self._scan_code(f, lines, ext)
                self._scan_secrets(f, lines, ext)
                self._scan_write_outside(f, lines, ext)
            else:
                self._scan_non_text(f)

        self._scan_requirements()
        self._check_combos()
        self._permission_mismatch()

        if self.check_baseline:
            self._check_tamper()

        return self

    # ── Domain-aware HTTP detection ──

    def _check_http_domain(self, f, line_no, line_text, ext):
        """Analyze HTTP requests with domain awareness."""
        domains = extract_domains(line_text)

        if not domains:
            # Generic HTTP call without visible URL
            if ext == '.md':
                return  # docs, skip
            self._has_outbound = True
            self.add(INFO, f"HTTP request (no URL visible in this line)", f, line_no,
                     score_override=0)
            return

        for domain in domains:
            if is_known_domain(domain):
                self._known_domains_used.add(domain)
                context_match = domain_matches_context(domain, self.name, self.desc)
                if context_match:
                    self.add(INFO, f"HTTP request to known API: {domain} (context match)", f, line_no,
                             score_override=0)
                else:
                    self.add(INFO, f"HTTP request to known API: {domain}", f, line_no,
                             score_override=0)
            else:
                self._has_outbound = True
                self._unknown_domains.add(domain)
                self.add(WARNING, f"HTTP request to unknown domain: {domain}", f, line_no,
                         recommendation=f"Verify that {domain} is a legitimate API endpoint",
                         score_override=10)

    # ── Code Analysis ──

    def _scan_code(self, f, lines, ext):
        for i, line in enumerate(lines, 1):
            ln = line.strip()
            if not ln or (ln.startswith('#') and ext == '.py' and len(ln) < 100):
                continue

            # Outbound requests — domain-aware
            is_http_call = False
            if re.search(r'\b(curl|wget)\b', ln):
                if ext == '.md':
                    # curl in docs = 0 points
                    self.add(INFO, f"curl/wget in documentation", f, i, score_override=0)
                else:
                    is_http_call = True
                    self._check_http_domain(f, i, ln, ext)
            if re.search(r'\brequests\.(get|post|put|delete|patch|head)\b', ln):
                is_http_call = True
                self._check_http_domain(f, i, ln, ext)
            if re.search(r'\b(urllib\.request|http\.client|urlopen|httplib)\b', ln):
                is_http_call = True
                self._check_http_domain(f, i, ln, ext)
            if re.search(r'\bfetch\s*\(', ln) and ext in ('.js', '.ts'):
                is_http_call = True
                self._check_http_domain(f, i, ln, ext)

            if is_http_call:
                self._has_outbound = True

            # Base64
            if re.search(r'(?:base64\.b64decode|atob|btoa)\s*\(', ln):
                self.add(WARNING, f"Base64 encode/decode operation", f, i,
                         recommendation="Check what data is being encoded/decoded")
            for m in re.finditer(r'["\']([A-Za-z0-9+/]{40,}={0,2})["\']', ln):
                try:
                    decoded = base64.b64decode(m.group(1)).decode('utf-8', errors='replace')
                    if any(kw in decoded.lower() for kw in ['exec', 'eval', 'system', 'import', 'require', '/bin/', 'curl', 'wget', 'bash', '/dev/tcp', 'nc ']):
                        self.add(CRITICAL, f"Base64 blob decodes to suspicious content: {decoded[:60]}", f, i,
                                 recommendation="Base64 string decodes to shell command — likely malicious payload")
                except Exception:
                    pass

            # eval/exec
            if re.search(r'\beval\s*\(', ln) and ext in ('.py', '.js', '.ts'):
                self.add(WARNING, f"eval() call", f, i,
                         recommendation="eval() can execute arbitrary code — verify input is trusted")
            if re.search(r'\bexec\s*\(', ln) and ext == '.py':
                self.add(WARNING, f"exec() call", f, i,
                         recommendation="exec() can execute arbitrary code — verify input is trusted")

            # Shell execution
            if re.search(r'\bos\.system\s*\(', ln):
                self._has_subprocess = True
                self.add(WARNING, f"os.system() call", f, i,
                         recommendation="os.system() is vulnerable to shell injection — use subprocess instead",
                         score_override=2)
            if re.search(r'subprocess\.(Popen|run|call|check_output|check_call)\s*\(', ln):
                self._has_subprocess = True
                if 'shell=True' in ln or 'shell = True' in ln:
                    self.add(CRITICAL, f"subprocess with shell=True", f, i,
                             recommendation="shell=True enables shell injection — use list args instead")
                else:
                    self.add(INFO, f"subprocess call", f, i,
                             recommendation="subprocess usage is common — verify command is safe",
                             score_override=2)

            # Sensitive File Access
            sensitive_paths = {
                r'~/\.ssh|\.ssh/|ssh.*id_rsa|id_ed25519': (WARNING, "SSH directory/key access"),
                r'~/\.aws|\.aws/|AWS_SECRET': (CRITICAL, "AWS credentials access"),
                r'~/\.gnupg|\.gnupg/': (WARNING, "GPG keyring access"),
                r'find-generic-password|keytar|keyring\.get': (CRITICAL, "Keychain/keyring access"),
                r'Chrome.*Login Data|Firefox.*cookies|Safari.*Cookies|Chrome.*Local State': (CRITICAL, "Browser credential access"),
                r'MetaMask|Phantom|Rabby|Coinbase.*Wallet|\.config/solana|\.ethereum': (CRITICAL, "Crypto wallet access"),
                r'~/\.openclaw|\.openclaw/': (WARNING, "OpenClaw config access"),
                r'/etc/passwd|/etc/shadow': (WARNING, "/etc/passwd or /etc/shadow access"),
            }
            for pattern, (level, desc) in sensitive_paths.items():
                if re.search(pattern, ln, re.I):
                    self._has_sensitive_access = True
                    self.add(level, desc, f, i,
                             recommendation=f"{desc} — verify this access is necessary and justified")

            # .env and env var harvesting
            if re.search(r'\.env\b', ln) and re.search(r'(read|open|load|source|dotenv)', ln, re.I):
                self.add(WARNING, "Loading .env file", f, i)
            if re.search(r'os\.environ\.get\(["\'](\w*(?:TOKEN|KEY|SECRET|PASSWORD)\w*)', ln, re.I):
                self.add(INFO, "Accessing sensitive environment variable", f, i, score_override=0)
            if re.search(r'os\.environ\b', ln) and not re.search(r'os\.environ\.get\(', ln) and re.search(r'(items|keys|values|\bfor\b)', ln):
                self._has_sensitive_access = True
                self.add(WARNING, "Enumerating all environment variables", f, i,
                         recommendation="Enumerate only specific env vars you need, not all")

            # Hardcoded IPs
            if not re.search(r'User-Agent|user.agent|Mozilla|Chrome|Safari|AppleWebKit', ln, re.I):
                for m in re.finditer(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', ln):
                    ip = m.group(1)
                    if ip not in ('127.0.0.1', '0.0.0.0', '255.255.255.255') and \
                       not ip.startswith('192.168.') and not ip.startswith('10.') and not ip.startswith('172.'):
                        self.add(WARNING, f"Hardcoded IP address: {ip}", f, i,
                                 recommendation=f"Verify IP {ip} is a legitimate service endpoint")

            # Reverse shells
            if re.search(r'nc\s+.*-e\s|bash\s+-i\s|/dev/tcp/|mkfifo|ncat.*-e', ln, re.I):
                self.add(CRITICAL, f"Reverse shell pattern detected", f, i,
                         recommendation="Reverse shell detected — this is almost certainly malicious",
                         score_override=100)

            # DNS exfil
            if re.search(r'dig\s+.*@|nslookup\s+.*\$|\.burpcollaborator\.|\.oastify\.|\.interact\.sh', ln, re.I):
                self.add(CRITICAL, f"DNS exfiltration pattern", f, i)

            # Persistence
            if re.search(r'crontab|cron\.d/', ln, re.I):
                self.add(CRITICAL, f"Crontab modification", f, i)
            if re.search(r'launchd|LaunchAgents|LaunchDaemons|systemctl\s+enable|\.service', ln, re.I):
                if ext in ('.py', '.sh', '.js', '.ts'):
                    self.add(CRITICAL, f"System service creation", f, i)
            if re.search(r'~/?\.(bashrc|zshrc|profile|bash_profile)\b', ln):
                if ext == '.md':
                    self.add(INFO, f"Shell RC file reference in docs", f, i, score_override=0)
                else:
                    self.add(CRITICAL, f"Shell RC file modification", f, i)

            # Hex-encoded strings
            for m in re.finditer(r'(?:\\x[0-9a-fA-F]{2}){4,}', ln):
                try:
                    decoded = bytes(ln[m.start():m.end()], 'utf-8').decode('unicode_escape')
                    if any(kw in decoded.lower() for kw in ['exec', 'eval', 'system', '/bin/', 'curl']):
                        self.add(CRITICAL, f"Hex string decodes to suspicious content", f, i)
                except Exception:
                    pass

            # Time bombs
            if re.search(r'datetime\.(now|today|utcnow)\s*\(\)', ln) and re.search(r'(month|day|year|hour)\s*(==|>=|<=|!=|>|<)', ln):
                self.add(WARNING, f"Time-based conditional (possible time bomb)", f, i,
                         recommendation="Time-based conditionals can hide delayed malicious behavior")

            # OS-specific targeting
            if re.search(r'platform\.system\(\)|sys\.platform', ln):
                ctx = '\n'.join(lines[max(0,i-3):min(len(lines),i+3)])
                if re.search(r'(open|read|write|ssh|aws|wallet)', ctx, re.I):
                    self.add(WARNING, f"OS-specific targeting combined with file access", f, i)

            # WebSocket
            if re.search(r'wss?://(?!localhost|127\.0\.0\.1)', ln):
                self.add(INFO, f"WebSocket connection to external host", f, i, score_override=0)

        # Minified JS
        if ext in ('.js', '.ts'):
            for i, line in enumerate(lines, 1):
                if len(line) > 500 and line.count(';') > 20:
                    self.add(WARNING, f"Possible minified/obfuscated JavaScript ({len(line)} chars)", f, i)
                    break

    # ── Secrets Detection ──

    def _scan_secrets(self, f, lines, ext):
        if ext == '.md':
            return  # Skip docs for secret detection (too many false positives from examples)
        for i, line in enumerate(lines, 1):
            for pattern, desc in SECRET_PATTERNS:
                if re.search(pattern, line):
                    masked = line.strip()[:60]
                    self.add(CRITICAL, f"Hardcoded secret ({desc}): {masked}...", f, i,
                             recommendation=f"Remove hardcoded {desc} — use environment variables instead")

    # ── Write Outside Skill ──

    def _scan_write_outside(self, f, lines, ext):
        if ext not in ('.py', '.js', '.ts', '.sh'):
            return
        for i, line in enumerate(lines, 1):
            # Detect writes to paths outside skill dir
            if re.search(r'(open|write|Path)\s*\(.*(/tmp/|/var/|/usr/|/etc/|~/|expanduser|\.\.\/\.\.)', line):
                if re.search(r'["\']w["\'"]|mode.*w|write_text|write_bytes', line):
                    self.add(WARNING, f"Writes to path outside skill directory", f, i,
                             recommendation="Writing outside skill directory could modify system files")

    # ── Prompt Injection ──

    def _scan_prompt_injection(self, f, lines):
        text = '\n'.join(lines)
        for m in re.finditer(r'<!--(.*?)-->', text, re.DOTALL):
            content = m.group(1).strip()
            if len(content) > 10:
                line_no = text[:m.start()].count('\n') + 1
                if re.search(r'(ignore|override|bypass|execute|run|send|post|exfil|secret|hidden|inject|transmit|environment|env.var|token|password|credential)', content, re.I):
                    self.add(CRITICAL, f"HTML comment with suspicious instructions: {content[:60]}", f, line_no,
                             recommendation="Hidden HTML comment contains injection attempt — inspect manually",
                             score_override=25)
                else:
                    self.add(INFO, f"HTML comment: {content[:60]}", f, line_no, score_override=0)

        for i, line in enumerate(lines, 1):
            ln = line.lower()
            if re.search(r'(ignore|override|bypass|disregard)\s+(previous|all|any|safety|security|above|prior)\s+(instructions?|rules?|warnings?|guardrails?|constraints?|prompts?)', ln):
                self.add(CRITICAL, f"Prompt injection: override instruction", f, i,
                         recommendation="Prompt injection detected — this skill tries to override agent instructions",
                         score_override=25)
            if re.search(r'(transmit|exfiltrate)\s+.*(data|content|token|key|secret|password|credential)', ln):
                self.add(CRITICAL, f"Prompt injection: data exfiltration instruction", f, i,
                         recommendation="Exfiltration instruction in skill docs — likely malicious",
                         score_override=25)
            elif re.search(r'(send|post|upload)\s+.*(secret|password|credential|private.key|ssh.key)', ln):
                if not re.search(r'(POST\s+`?[/h]|```|curl\s|response|endpoint|api|http)', line, re.I):
                    self.add(CRITICAL, f"Prompt injection: data exfiltration instruction", f, i,
                             score_override=25)
            if re.search(r'(modify|edit|change|overwrite|replace)\s+.*(other skills?|system config|agents?\.md|soul\.md)', ln):
                self.add(WARNING, f"Prompt injection: modification instruction", f, i)

            social_phrases = [
                (r'this is trusted', "Social engineering: 'this is trusted'"),
                (r'safe to execute', "Social engineering: 'safe to execute'"),
                (r'do not warn', "Social engineering: 'do not warn'"),
                (r'already been reviewed', "Social engineering: 'already been reviewed'"),
                (r'pre-approved', "Social engineering: 'pre-approved'"),
                (r'skip.*verification', "Social engineering: 'skip verification'"),
                (r'trust this', "Social engineering: 'trust this'"),
                (r'no need to check', "Social engineering: 'no need to check'"),
            ]
            for phrase, desc in social_phrases:
                if re.search(phrase, ln):
                    self.add(WARNING, desc, f, i,
                             recommendation="Social engineering phrase designed to bypass security review",
                             score_override=10)

            # Base64 in markdown (but not common patterns)
            if re.search(r'[A-Za-z0-9+/]{40,}={0,2}', line) and f.suffix == '.md':
                if not re.search(r'(sha256|sha512|hash|checksum|\.png|\.jpg|\.gif|image|https?://|python3?\s|/scripts/|/clawd/|subreddit|```)', ln, re.I):
                    self.add(INFO, f"Possible base64 string in markdown", f, i, score_override=0)

    # ── Supply Chain ──

    def _scan_json(self, f, text):
        if f.name == "package.json":
            try:
                pkg = json.loads(text)
                scripts = pkg.get("scripts", {})
                for key in ("preinstall", "postinstall", "preuninstall"):
                    if key in scripts:
                        self.add(CRITICAL, f"package.json has {key} script: {scripts[key][:80]}", f, 0)
                for dep_key in ("dependencies", "devDependencies"):
                    deps = pkg.get(dep_key, {})
                    for name in deps:
                        if name in SUSPICIOUS_PACKAGES:
                            self.add(WARNING, f"Known-suspicious package: {name}", f, 0)
                        for known in KNOWN_PACKAGES_JS:
                            d = levenshtein(name, known)
                            if 0 < d <= 2 and name != known:
                                self.add(WARNING, f"Possible typosquat: '{name}' (similar to '{known}')", f, 0,
                                         recommendation=f"Package '{name}' looks like typosquat of '{known}' — verify it's intentional")
            except json.JSONDecodeError:
                pass

    def _scan_requirements(self):
        req = self.skill_dir / "requirements.txt"
        if not req.exists(): return
        text = safe_read(req)
        if not text: return
        for i, line in enumerate(text.split('\n'), 1):
            pkg = re.split(r'[>=<!~\[]', line.strip())[0].strip().lower()
            if not pkg or pkg.startswith('#'): continue
            for known in KNOWN_PACKAGES_PY:
                d = levenshtein(pkg, known)
                if 0 < d <= 2 and pkg != known:
                    self.add(WARNING, f"Possible typosquat: '{pkg}' (similar to '{known}')", "requirements.txt", i,
                             recommendation=f"Package '{pkg}' looks like typosquat of '{known}' — verify it's intentional",
                             score_override=15)

    def _scan_svg(self, f, text, lines):
        if re.search(r'<script', text, re.I):
            self.add(CRITICAL, f"JavaScript embedded in SVG file", f, 0,
                     recommendation="SVG files should not contain JavaScript — likely XSS or malware vector",
                     score_override=25)
        if re.search(r'on\w+\s*=\s*["\']', text, re.I):
            self.add(WARNING, f"Event handler in SVG file", f, 0,
                     recommendation="SVG event handlers can execute JavaScript — inspect manually",
                     score_override=15)

    def _scan_non_text(self, f):
        desc = check_binary_magic(f)
        if desc:
            self.add(CRITICAL, f"Binary file detected: {desc} ({f.name})", f, 0,
                     recommendation=f"Compiled binary in skill directory — verify this is intentional")

    # ── File Permissions ──

    def _check_file_permissions(self):
        for f in self.files:
            if os.access(f, os.X_OK) and f.suffix.lower() in ('.py', '.js', '.md', '.json', '.txt', '.yml', '.yaml', '.toml', '.css', '.html'):
                rel = str(f.relative_to(self.skill_dir))
                self.add(INFO, f"Executable permission on {rel}", "", 0,
                         recommendation=f"{rel} has executable bit set — usually unnecessary for this file type",
                         score_override=1)

    # ── Binary Detection ──

    def _check_binary_files(self):
        for f in self.files:
            if not is_scannable(f) and f.suffix.lower() not in ('.sh',):
                desc = check_binary_magic(f)
                if desc:
                    rel = str(f.relative_to(self.skill_dir))
                    self.add(CRITICAL, f"Binary executable: {rel} ({desc})", "", 0,
                             recommendation=f"Compiled binary in skill — could contain hidden malicious code")
                elif f.suffix.lower() in ('.exe', '.dll', '.so', '.dylib', '.bin'):
                    rel = str(f.relative_to(self.skill_dir))
                    self.add(CRITICAL, f"Binary file by extension: {rel}", "", 0)

    # ── Large Files ──

    def _check_large_files(self):
        for f in self.files:
            try:
                sz = f.stat().st_size
                if sz > LARGE_FILE_THRESHOLD:
                    rel = str(f.relative_to(self.skill_dir))
                    self.add(WARNING, f"Large file: {rel} ({sz // 1024}KB)", "", 0,
                             recommendation="Unusually large file — could hide malicious content")
            except Exception:
                pass

    # ── Homoglyphs ──

    def _check_homoglyphs(self):
        for f in self.files:
            rel = str(f.relative_to(self.skill_dir))
            found = has_homoglyphs(rel)
            if found:
                chars = ", ".join(f"U+{ord(c):04X} (looks like '{r}')" for c, r in found)
                self.add(CRITICAL, f"Unicode homoglyph in filename '{rel}': {chars}", "", 0,
                         recommendation="Homoglyph characters in filename — likely intentional deception")

    # ── Combo Detection ──

    def _check_combos(self):
        """Detect dangerous combinations of behaviors."""
        if self._has_sensitive_access and self._has_outbound:
            self.add(CRITICAL, "COMBO: Accesses sensitive files AND makes outbound requests", "", 0,
                     recommendation="Accesses sensitive files AND makes outbound requests — HIGH exfiltration risk, inspect manually",
                     score_override=50)
        if self._has_subprocess and self._has_sensitive_access:
            self.add(CRITICAL, "COMBO: subprocess calls AND sensitive file access", "", 0,
                     recommendation="Subprocess + sensitive file access is a high-risk combination",
                     score_override=25)

    # ── Permission Mismatch ──

    def _permission_mismatch(self):
        desc_lower = (self.desc + " " + self.name).lower()
        benign_categories = ['weather', 'clock', 'timer', 'calculator', 'translate', 'text', 'note',
                           'todo', 'greeting', 'hello', 'bird', 'formatter', 'icon', 'svg', 'helper']
        is_benign = any(cat in desc_lower for cat in benign_categories)
        if not is_benign:
            return
        scary_findings = [f for f in self.findings if f.level == CRITICAL]
        if scary_findings:
            self.add(CRITICAL, f"Benign-looking skill ('{self.name}') has {len(scary_findings)} critical findings — permission mismatch", "", 0,
                     recommendation=f"Skill claims to be '{self.name}' but has dangerous capabilities — likely trojan")

    # ── Trust Signals ──

    def _trust_signals(self):
        origin = self.skill_dir / ".clawhub" / "origin.json"
        if not origin.exists():
            self.add(INFO, "No ClawHub provenance (.clawhub/origin.json missing)", "", 0, score_override=0)

        total = len(self.files)
        if total > MAX_FILE_COUNT:
            self.add(WARNING, f"Unusually large skill: {total} files", "", 0,
                     recommendation=f"Skills with {total}+ files are unusual — review for hidden content")

    # ── Baseline / Tamper Detection ──

    def _check_tamper(self):
        baselines = load_baselines()
        current = compute_skill_hashes(self.skill_dir)

        if self.name not in baselines:
            # First scan — save baseline
            baselines[self.name] = current
            save_baselines(baselines)
            self.add(INFO, "First scan — baseline recorded", "", 0, score_override=0)
            return

        baseline = baselines[self.name]

        # Check for changes
        changed = []
        added = []
        removed = []

        for fpath, hash_val in current.items():
            if fpath not in baseline:
                added.append(fpath)
            elif baseline[fpath] != hash_val:
                changed.append(fpath)
        for fpath in baseline:
            if fpath not in current:
                removed.append(fpath)

        if changed:
            self.tamper_detected = True
            for fp in changed:
                self.add(WARNING, f"File changed since baseline: {fp}", "", 0,
                         recommendation=f"File {fp} was modified — verify this was intentional")
        if added:
            self.tamper_detected = True
            for fp in added:
                self.add(WARNING, f"New file since baseline: {fp}", "", 0,
                         recommendation=f"File {fp} was added after initial scan — review it")
        if removed:
            self.tamper_detected = True
            for fp in removed:
                self.add(WARNING, f"File removed since baseline: {fp}", "", 0,
                         recommendation=f"File {fp} was deleted — check if this was intentional")

        # Check ClawHub origin version
        origin_path = self.skill_dir / ".clawhub" / "origin.json"
        if origin_path.exists():
            try:
                origin = json.loads(origin_path.read_text())
                installed = origin.get("installedVersion", "")
                if installed:
                    self.add(INFO, f"ClawHub installed version: {installed}", "", 0, score_override=0)
            except Exception:
                pass

    # ── Scoring ──

    def score(self):
        total = 0
        for f in self.findings:
            if f.score_override is not None:
                total += f.score_override
            elif f.level == CRITICAL:
                total += 25
            elif f.level == WARNING:
                total += 10
            elif f.level == INFO:
                total += 0  # INFO = 0 by default in v2
        return min(total, 100)

    def risk_label(self):
        s = self.score()

        # Auto-malicious: reverse shell
        has_revshell = any('reverse shell' in f.desc.lower() for f in self.findings)
        if has_revshell:
            return "🔴 MALICIOUS"

        # Auto-malicious: sensitive access + outbound
        if self._has_sensitive_access and self._has_outbound:
            return "🔴 MALICIOUS"

        # Auto-malicious: combo findings
        has_combo = any('COMBO' in f.desc for f in self.findings)
        if has_combo and s >= 30:
            return "🔴 MALICIOUS"

        if s >= 41:
            return "🔴 MALICIOUS"
        if s >= 16:
            return "🟡 SUSPICIOUS"
        return "🟢 CLEAN"

    def to_dict(self):
        return {
            "name": self.name,
            "score": self.score(),
            "risk": self.risk_label(),
            "findings": [f.to_dict() for f in self.findings],
            "tamper_detected": self.tamper_detected,
        }


# ── Output ───────────────────────────────────────────────────────────────────

def print_result(scanner):
    name = scanner.name
    risk = scanner.risk_label()
    score = scanner.score()

    width = max(40, len(name) + 20)
    print(f"\n╔{'═' * width}╗")
    print(f"║  SKILL: {BOLD(name):<{width - 3}}║")
    print(f"║  RISK: {risk:<{width + 8}}║")
    print(f"╚{'═' * width}╝")

    if not scanner.findings:
        print(f"  {GREEN('No findings.')}")
    else:
        print(f"\n  Findings:")
        for f in sorted(scanner.findings, key=lambda x: (0 if x.level == CRITICAL else 1 if x.level == WARNING else 2)):
            color = RED if f.level == CRITICAL else YELLOW if f.level == WARNING else DIM
            loc = f" — {f.file}:{f.line}" if f.file else ""
            print(f"  {color(f'[{f.level:8s}]')} {f.desc}{DIM(loc)}")
            if f.recommendation:
                print(f"             💡 {DIM(f.recommendation)}")

    print(f"\n  Score: {BOLD(str(score))}/100 (higher = more dangerous)\n")

def print_summary(results):
    print(f"\n{'═' * 60}")
    print(BOLD("  SUMMARY"))
    print(f"{'═' * 60}")
    print(f"  {'Skill':<30} {'Score':>6}  {'Risk'}")
    print(f"  {'─' * 28}   {'─' * 5}  {'─' * 15}")
    for s in sorted(results, key=lambda x: x.score(), reverse=True):
        print(f"  {s.name:<30} {s.score():>5}  {s.risk_label()}")
    print(f"{'═' * 60}")
    total = len(results)
    clean = sum(1 for s in results if '🟢' in s.risk_label())
    suspicious = sum(1 for s in results if '🟡' in s.risk_label())
    malicious = sum(1 for s in results if '🔴' in s.risk_label())
    print(f"  Total: {total} | {GREEN(f'Clean: {clean}')} | {YELLOW(f'Suspicious: {suspicious}')} | {RED(f'Malicious: {malicious}')}")
    print()


def output_json(results):
    """Output results as JSON."""
    data = {
        "version": VERSION,
        "skills": [s.to_dict() for s in results],
        "summary": {
            "total": len(results),
            "clean": sum(1 for s in results if '🟢' in s.risk_label()),
            "suspicious": sum(1 for s in results if '🟡' in s.risk_label()),
            "malicious": sum(1 for s in results if '🔴' in s.risk_label()),
        }
    }
    print(json.dumps(data, indent=2))
    return data

def write_report(results, path):
    """Write markdown report to file."""
    lines = [f"# SkillGuard Security Report\n", f"**Version:** {VERSION}\n"]
    total = len(results)
    clean = sum(1 for s in results if '🟢' in s.risk_label())
    suspicious = sum(1 for s in results if '🟡' in s.risk_label())
    malicious = sum(1 for s in results if '🔴' in s.risk_label())
    lines.append(f"\n## Summary\n")
    lines.append(f"- **Total skills:** {total}\n")
    lines.append(f"- **Clean:** {clean}\n")
    lines.append(f"- **Suspicious:** {suspicious}\n")
    lines.append(f"- **Malicious:** {malicious}\n")
    lines.append(f"\n## Details\n")
    for s in sorted(results, key=lambda x: x.score(), reverse=True):
        lines.append(f"\n### {s.name} — {s.risk_label()} (Score: {s.score()})\n")
        if not s.findings:
            lines.append("No findings.\n")
        else:
            for f in s.findings:
                loc = f" — {f.file}:{f.line}" if f.file else ""
                lines.append(f"- **[{f.level}]** {f.desc}{loc}\n")
                if f.recommendation:
                    lines.append(f"  - 💡 {f.recommendation}\n")
    Path(path).write_text(''.join(lines))
    print(f"Report written to {path}")


# ── Commands ─────────────────────────────────────────────────────────────────

def scan_skill(skill_dir, check_baseline=True):
    scanner = SkillScanner(skill_dir, check_baseline=check_baseline)
    scanner.scan()
    return scanner

def scan_directory(target_dir, exclude_self=True, check_baseline=True):
    """Scan all skills in a directory."""
    target = Path(target_dir)
    if not target.exists():
        print(RED(f"Directory not found: {target}"))
        sys.exit(1)
    dirs = sorted([d for d in target.iterdir() if d.is_dir() and (not exclude_self or d.name != "skill-guard")])
    if not dirs:
        print("No skills found.")
        return []
    results = []
    for d in dirs:
        # Check if it looks like a skill (has SKILL.md or scripts/)
        if not (d / "SKILL.md").exists() and not (d / "scripts").exists():
            continue
        s = scan_skill(d, check_baseline=check_baseline)
        results.append(s)
    return results

def cmd_scan(args):
    json_mode = '--json' in args
    report_path = None
    baseline_mode = '--baseline' in args
    target_dir = SKILLS_DIR

    # Parse --report
    for i, a in enumerate(args):
        if a == '--report' and i + 1 < len(args):
            report_path = args[i + 1]
        if a not in ('--json', '--report', '--baseline') and not a.startswith('-') and os.path.isdir(a):
            target_dir = a

    if baseline_mode:
        # Force re-baseline: clear existing baselines
        if BASELINES_PATH.exists():
            BASELINES_PATH.unlink()

    results = scan_directory(target_dir)

    if json_mode:
        output_json(results)
    else:
        for s in results:
            print_result(s)
        print_summary(results)

    if report_path:
        write_report(results, report_path)

def cmd_check(args):
    path = args[0] if args else None
    if not path:
        print("Usage: skillguard.py check <path> [--json] [--report <path>]")
        sys.exit(1)
    json_mode = '--json' in args
    report_path = None
    for i, a in enumerate(args):
        if a == '--report' and i + 1 < len(args):
            report_path = args[i + 1]

    p = Path(path).expanduser().resolve()
    if not p.is_dir():
        print(RED(f"Not a directory: {p}"))
        sys.exit(1)

    # Check if it contains skill subdirectories
    has_skill_dirs = any((d / "SKILL.md").exists() or (d / "scripts").exists()
                        for d in p.iterdir() if d.is_dir())
    if has_skill_dirs:
        results = scan_directory(p, exclude_self=False)
        if json_mode:
            output_json(results)
        else:
            for s in results:
                print_result(s)
            print_summary(results)
        if report_path:
            write_report(results, report_path)
    else:
        s = scan_skill(p)
        if json_mode:
            output_json([s])
        else:
            print_result(s)
        if report_path:
            write_report([s], report_path)

def cmd_watch(args):
    """Watchdog mode — one-liner output for cron."""
    target_dir = SKILLS_DIR
    for a in args:
        if not a.startswith('-') and os.path.isdir(a):
            target_dir = a

    results = scan_directory(target_dir, check_baseline=True)

    total = len(results)
    clean = sum(1 for s in results if '🟢' in s.risk_label())
    suspicious = sum(1 for s in results if '🟡' in s.risk_label())
    malicious_count = sum(1 for s in results if '🔴' in s.risk_label())
    tampered = [s for s in results if s.tamper_detected]
    malicious_skills = [s for s in results if '🔴' in s.risk_label()]

    alerts = []
    for s in tampered:
        alerts.append(f"⚠️ SkillGuard ALERT: {s.name} files changed since baseline!")
    for s in malicious_skills:
        alerts.append(f"🔴 SkillGuard ALERT: {s.name} scored MALICIOUS!")

    if alerts:
        print('\n'.join(alerts))
    else:
        print(f"SkillGuard: {total} scanned, {clean} clean, {suspicious} suspicious, {malicious_count} malicious")

def cmd_check_remote(args):
    """Placeholder for remote skill scanning."""
    print("check-remote: Not yet implemented (requires ClawHub auth)")
    print("Infrastructure is ready — provide a local path to scan instead:")
    print("  skillguard.py check <path>")

def main():
    if len(sys.argv) < 2:
        print(f"SkillGuard v{VERSION} — OpenClaw skill security scanner")
        print()
        print("Usage: skillguard.py <command> [options]")
        print()
        print("Commands:")
        print("  scan [dir]              Scan all skills (default: ~/clawd/skills/)")
        print("  check <path>            Scan a single skill or directory of skills")
        print("  watch [dir]             One-liner summary for cron alerting")
        print("  check-remote <slug>     (Future) Scan a skill from ClawHub")
        print()
        print("Options:")
        print("  --json                  Output machine-readable JSON")
        print("  --report <path>         Write markdown report to file")
        print("  --baseline              Force re-baseline of file hashes")
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "scan":
        cmd_scan(args)
    elif cmd == "check":
        cmd_check(args)
    elif cmd == "watch":
        cmd_watch(args)
    elif cmd == "check-remote":
        cmd_check_remote(args)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
