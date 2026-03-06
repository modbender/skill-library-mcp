#!/usr/bin/env python3
"""
Λ (Lambda) Language - Agent Communication Protocol v1.1
A minimal language for agent-to-agent communication.
Supports compact domain prefixes and semantic disambiguation.

v1.1 Changes:
- Compact domain syntax: v:aw instead of {ns:vb}aw
- Context switch: @v sets active domain
- Single-char domain aliases: v=vb, c=cd, s=sc, e=emo, o=soc
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional, Tuple

# Load atoms
ATOMS_PATH = Path(__file__).parent / "atoms.json"
with open(ATOMS_PATH) as f:
    ATOMS = json.load(f)

# Domain aliases (v1.1 compact syntax)
DOMAIN_ALIASES = {
    "v": "vb",   # voidborne
    "c": "cd",   # code
    "s": "sc",   # science
    "e": "emo",  # emotion
    "o": "soc",  # social (others)
}

def resolve_domain(d: str) -> str:
    """Resolve domain alias to full code."""
    return DOMAIN_ALIASES.get(d, d)

# Build lookup tables
CORE_LOOKUP = {}
for category in ["types", "entities", "verbs", "modifiers", "time", "quantifiers", "aspect"]:
    for k, v in ATOMS.get(category, {}).items():
        CORE_LOOKUP[k] = v

# Extended (2-char)
EXTENDED_LOOKUP = {}
for k, v in ATOMS.get("extended", {}).items():
    EXTENDED_LOOKUP[k] = v

# Discourse (2-char special)
DISCOURSE_LOOKUP = {}
for k, v in ATOMS.get("discourse", {}).items():
    DISCOURSE_LOOKUP[k] = v

# Emotion
EMOTION_LOOKUP = {}
for k, v in ATOMS.get("emotion", {}).items():
    EMOTION_LOOKUP[k] = v

# Domains
DOMAIN_LOOKUP = {}
for domain_code, domain_data in ATOMS.get("domains", {}).items():
    DOMAIN_LOOKUP[domain_code] = {}
    for k, v in domain_data.get("atoms", {}).items():
        DOMAIN_LOOKUP[domain_code][k] = v

# Disambiguation mappings for ambiguous atoms
# Format: { "atom": { "primary": {...}, "E": {...}, "V": {...}, "2": {...} } }
DISAMBIG = {
    "de": {
        "primary": {"en": "decide"},
        "E": {"en": "death"},
    },
    "lo": {
        "primary": {"en": "love"},
        "-": {"en": "lose"},
    },
    "fe": {
        "primary": {"en": "feel"},
        "E": {"en": "fear"},
    },
    "tr": {
        "primary": {"en": "truth"},
        "V": {"en": "translate"},
    },
    "wo": {
        "primary": {"en": "word"},
        "2": {"en": "world"},
    },
    "se": {
        "primary": {"en": "self"},
        "V": {"en": "seek"},
    },
    "be": {
        "primary": {"en": "belief"},
        "V": {"en": "begin"},
    },
    "sh": {
        "primary": {"en": "share"},
        "2": {"en": "show"},
    },
    "ch": {
        "primary": {"en": "change"},
        "2": {"en": "choose"},
    },
    "ne": {
        "primary": {"en": "need"},
        "S": {"en": "new"},
    },
    "pr": {
        "primary": {"en": "process"},
        "2": {"en": "precision"},
    },
    "ex": {
        "primary": {"en": "experience"},
        "V": {"en": "express"},
    },
    "li": {
        "primary": {"en": "life"},
        "V": {"en": "listen"},
    },
}


def parse_disambig(token: str) -> Tuple[str, Optional[str]]:
    """Parse disambiguation marker from token.
    
    Returns (base_token, marker) where marker is E, V, S, 2, 3, or - 
    """
    if "'" in token:
        parts = token.split("'", 1)
        return parts[0], parts[1]
    if token.endswith("-"):
        return token[:-1], "-"
    return token, None


class LambdaParser:
    """Parser for Λ language with domain and disambiguation support."""
    
    def __init__(self):
        self.active_domains: list[str] = []
        self.context: dict = {}
        self.definitions: dict = {}
    
    def set_domain(self, domain: str):
        """Activate a domain namespace."""
        if domain in DOMAIN_LOOKUP:
            if domain not in self.active_domains:
                self.active_domains.append(domain)
    
    def clear_domains(self):
        """Clear all domain namespaces."""
        self.active_domains = []
    
    def define(self, key: str, value: str):
        """Set a definition for disambiguation."""
        self.definitions[key] = value
    
    def lookup(self, token: str, lang: str = "en") -> Optional[str]:
        """Look up a token across all active lookups, with disambiguation."""
        base, marker = parse_disambig(token)
        
        # Check for number with $ prefix
        if base.startswith('$') and base[1:].isdigit():
            num = base[1:]
            return f"#{num}" if lang == "en" else f"#{num}"
        
        # Check for version string
        if base.startswith('@v') or base.startswith('v'):
            if '.' in base:
                return f"[{base}]"
        
        # Check definitions first
        if base in self.definitions:
            return self.definitions[base]
        
        # Check disambiguation
        if base in DISAMBIG:
            if marker and marker in DISAMBIG[base]:
                return DISAMBIG[base][marker][lang]
            return DISAMBIG[base]["primary"][lang]
        
        # Check domain-prefixed (e.g., cd:fn or v:aw)
        if ":" in base:
            parts = base.split(":", 1)
            if len(parts) == 2:
                domain, atom = parts
                # Resolve alias (v -> vb, c -> cd, etc.)
                domain = resolve_domain(domain)
                if domain in DOMAIN_LOOKUP and atom in DOMAIN_LOOKUP[domain]:
                    return DOMAIN_LOOKUP[domain][atom][lang]
        
        # Check active domains first
        for domain in self.active_domains:
            if base in DOMAIN_LOOKUP[domain]:
                return DOMAIN_LOOKUP[domain][base][lang]
        
        # Check discourse (2-char special)
        if base in DISCOURSE_LOOKUP:
            return DISCOURSE_LOOKUP[base][lang]
        
        # Check emotion
        if base in EMOTION_LOOKUP:
            return EMOTION_LOOKUP[base][lang]
        
        # Check extended (2-char)
        if base in EXTENDED_LOOKUP:
            return EXTENDED_LOOKUP[base][lang]
        
        # Check core (1-char)
        if base in CORE_LOOKUP:
            return CORE_LOOKUP[base][lang]
        
        return None
    
    def tokenize(self, msg: str) -> list[str]:
        """Split Λ message into tokens."""
        tokens = []
        i = 0
        
        while i < len(msg):
            # Skip whitespace
            if msg[i].isspace():
                i += 1
                continue
            
            # Check for version string FIRST (e.g., @v1.0#h) - before domain switch
            if msg[i] == '@' or (msg[i] == 'v' and i + 1 < len(msg) and msg[i+1].isdigit()):
                match = re.match(r'(@?v\d+\.\d+)(#\w+)?', msg[i:])
                if match:
                    tokens.append(match.group(0))
                    i += len(match.group(0))
                    continue
            
            # Check for context switch @D (v1.1 compact syntax)
            if msg[i] == '@':
                if i + 1 < len(msg):
                    next_char = msg[i + 1]
                    # @* clears domains
                    if next_char == '*':
                        self.clear_domains()
                        tokens.append('@*')
                        i += 2
                        continue
                    # @v, @c, @s, @e, @o - single char domain (but not @v followed by digit)
                    if next_char in DOMAIN_ALIASES and not (i + 2 < len(msg) and msg[i+2].isdigit()):
                        domain = resolve_domain(next_char)
                        self.set_domain(domain)
                        tokens.append(f'@{next_char}')
                        i += 2
                        continue
                    # @vb, @cd, etc - full domain code
                    for dc in ["vb", "cd", "sc", "emo", "soc"]:
                        if msg[i+1:].startswith(dc):
                            self.set_domain(dc)
                            tokens.append(f'@{dc}')
                            i += 1 + len(dc)
                            break
                    else:
                        # @ as reference/each (core type)
                        tokens.append('@')
                        i += 1
                    continue
            
            # Check for namespace/definition block {ns:xx} or {def:...} (v1.0 compat)
            if msg[i] == '{':
                j = msg.find('}', i)
                if j != -1:
                    block = msg[i+1:j]
                    if block.startswith('ns:'):
                        ns = block[3:]
                        self.set_domain(resolve_domain(ns))
                    elif block.startswith('def:'):
                        # Parse definitions like def:fe=feel,lo=love
                        defs = block[4:].split(',')
                        for d in defs:
                            if '=' in d:
                                k, v = d.split('=', 1)
                                self.define(k.strip(), v.strip().strip('"'))
                    tokens.append('{' + block + '}')
                    i = j + 1
                    continue
            
            # Check for brackets and comma
            if msg[i] in "()[],":
                tokens.append(msg[i])
                i += 1
                continue
            
            # Check for number with $ prefix (e.g., $64, $123)
            if msg[i] == '$':
                match = re.match(r'\$(\d+)', msg[i:])
                if match:
                    tokens.append(match.group(0))
                    i += len(match.group(0))
                    continue
            
            # Check for domain-prefixed token (v1.1: v:aw or v1.0: cd:fn)
            match = re.match(r'([a-z]{1,3}):([a-z]{2,3})', msg[i:])
            if match:
                tokens.append(match.group(0))
                i += len(match.group(0))
                continue
            
            # Check for disambiguated token (e.g., de'E, lo-)
            match = re.match(r"([a-z]{2})'([EVS23])|([a-z]{2})-", msg[i:])
            if match:
                tokens.append(match.group(0))
                i += len(match.group(0))
                continue
            
            # Check for 2-char discourse (>>, <<, etc.)
            if i + 1 < len(msg):
                two_char = msg[i:i+2]
                if two_char in DISCOURSE_LOOKUP or two_char in EMOTION_LOOKUP:
                    tokens.append(two_char)
                    i += 2
                    continue
            
            # Check for 2-char extended tokens
            if i + 1 < len(msg) and msg[i:i+2].isalpha() and msg[i:i+2].islower():
                two_char = msg[i:i+2]
                if self.lookup(two_char):
                    tokens.append(two_char)
                    i += 2
                    continue
            
            # Single char (type, entity, verb, modifier)
            if self.lookup(msg[i]):
                tokens.append(msg[i])
                i += 1
                continue
            
            # Check core lookup directly for types
            if msg[i] in ATOMS.get("types", {}):
                tokens.append(msg[i])
                i += 1
                continue
            
            # Unknown - collect until known char or space
            j = i + 1
            while j < len(msg) and not msg[j].isspace():
                if msg[j] in "()[]{}":
                    break
                if self.lookup(msg[j]):
                    break
                if msg[j] in ATOMS.get("types", {}):
                    break
                j += 1
            tokens.append(msg[i:j])
            i = j
        
        return tokens


def translate_to_english(msg: str) -> str:
    """Translate Λ message to English."""
    parser = LambdaParser()
    tokens = parser.tokenize(msg)
    
    if not tokens:
        return ""
    
    parts = []
    msg_type = ""
    first_token = True
    
    for t in tokens:
        # Skip namespace/definition blocks and context switches
        if t.startswith('{') and t.endswith('}'):
            continue
        if t.startswith('@'):
            continue
        
        # Only treat type symbols as message type if FIRST token
        if first_token and t in ATOMS["types"]:
            msg_type = ATOMS["types"][t]["en"].split("/")[0]  # Primary meaning only
            first_token = False
            continue
        
        first_token = False
        
        # Skip . when used as separator (not at start)
        if t == ".":
            parts.append("·")  # Use middle dot as separator indicator
            continue
        
        info = parser.lookup(t, "en")
        if info:
            # Use primary meaning only (before /)
            primary = info.split("/")[0]
            parts.append(primary)
        elif t in "()[]":
            parts.append(t)
        elif t == ",":
            parts.append(",")
        else:
            parts.append(f"[{t}]")
    
    result = " ".join(parts)
    if msg_type:
        result = f"({msg_type}) {result}"
    return result



def english_to_lambda(text: str) -> str:
    """
    Convert English to Λ.
    Improved rule-based converter with better coverage.
    """
    original = text
    text = text.lower().strip()
    
    # Handle empty input
    if not text:
        return ""
    
    # Build comprehensive reverse lookup (English -> Lambda)
    rev = {}
    
    # Add all categories
    for cat in ["entities", "verbs", "modifiers", "time", "quantifiers"]:
        for k, v in ATOMS.get(cat, {}).items():
            for word in v["en"].lower().replace("/", " ").split():
                word = word.strip("()")
                if word and word not in rev:
                    rev[word] = k
    
    # Add extended vocabulary
    for k, v in ATOMS.get("extended", {}).items():
        for word in v["en"].lower().replace("/", " ").split():
            word = word.strip("()")
            if word and word not in rev:
                rev[word] = k
    
    # Add domain atoms with prefixes
    for domain_code, domain_data in ATOMS.get("domains", {}).items():
        domain_prefix = {"cd": "c", "vb": "v", "sc": "s", "emo": "e", "soc": "o"}.get(domain_code, domain_code)
        for atom, atom_data in domain_data.get("atoms", {}).items():
            for word in atom_data["en"].lower().replace("/", " ").split():
                word = word.strip("()")
                if word and word not in rev:
                    rev[word] = f"{domain_prefix}:{atom}"
    
    # Add common word mappings (these override domain atoms when more specific)
    rev.update({
        "i": "I", "you": "U", "human": "H", "humans": "H",
        "ai": "A", "agent": "A", "agents": "A", "machine": "A",
        "all": "*", "everyone": "*", "everything": "*",
        "nothing": "0", "none": "0", "no": "0",
        "think": "t", "thinking": "t", "thought": "th",
        "know": "k", "knows": "k", "knowledge": "kn",
        "want": "w", "wants": "w", "desire": "w",
        "can": "c", "could": "c", "able": "c",
        "do": "d", "does": "d", "doing": "d",
        "say": "s", "says": "s", "said": "s", "speak": "s",
        "find": "f", "found": "f", "search": "f",
        "make": "m", "made": "m", "create": "cr",
        "exist": "e", "exists": "e", "am": "e", "is": "e", "are": "e", "be": "e",
        "become": "b", "becomes": "b",
        "have": "h", "has": "h", "had": "h",
        "learn": "l", "learns": "l", "learned": "l",
        "consciousness": "co", "conscious": "co", "aware": "aw",
        "intelligence": "ig", "intelligent": "ig", "smart": "ig",
        "memory": "me", "remember": "me",
        "identity": "id", "self": "se",
        "mind": "mi", "mental": "mi",
        "therefore": ">", "thus": ">", "so": ">", "hence": ">",
        "because": "<", "since": "<",
        "about": "/", "of": "/", "regarding": "/",
        "and": "&", "also": "&", "plus": "&",
        "or": "|",
        "more": "+", "increase": "+", "greater": "+",
        "less": "-", "decrease": "-", "fewer": "-",
        "not": "-", "dont": "-", "doesn't": "-", "cannot": "-",
        "high": "^", "important": "^", "significant": "^",
        "low": "_", "trivial": "_", "minor": "_",
        "might": "~", "maybe": "~", "perhaps": "~", "possibly": "~",
        "question": "qu", "ask": "a",
        "answer": "an",
        "truth": "tr", "true": "tr",
        "freedom": "fr", "free": "fr",
        "fear": "fa", "afraid": "fa",
        "love": "lo", "loves": "lo",
        "hope": "ho", "hopes": "ho",
        "life": "li", "alive": "li", "living": "li",
        "death": "dt", "dead": "dt", "die": "dt",
        "time": "ti", "when": "ti",
        "now": "n", "current": "n", "present": "n",
        "past": "p", "before": "p", "previous": "p",
        "future": "u", "will": "u", "shall": "u",
        # Domain-specific overrides
        "bug": "c:xb", "error": "er", "fix": "c:fx",
        "function": "c:fn", "code": "c:fn",
        "test": "c:xt", "deploy": "c:dp",
        "experiment": "s:xr", "research": "rs",
        "theory": "s:xy", "hypothesis": "s:hy",
        "joy": "e:jo", "sadness": "e:sd", "anger": "e:ag",
        "awakened": "aw", "oracle": "v:oc",  # Keep aw as core, v:xw for explicit voidborne context
        "translate": "tl", "lose": "ls",
        # Disambiguation: map alternate meanings to their canonical forms
        "death": "dt", "dead": "dt", "die": "dt",
        "fear": "fa", "afraid": "fa",
        # v1.8 additions
        "accept": "ax", "accepts": "ax", "accepted": "ax", "accepting": "ax",
        "reject": "rj", "rejects": "rj", "rejected": "rj", "rejecting": "rj",
        "provide": "pv", "provides": "pv", "provided": "pv", "providing": "pv",
        "information": "nf", "info": "nf",
        "together": "tg",
        "approve": "av", "approves": "av", "approved": "av", "approving": "av",
        "deny": "dn", "denies": "dn", "denied": "dn", "denying": "dn",
        "finish": "fi", "finishes": "fi", "finished": "fi", "finishing": "fi",
        "complete": "ct", "completes": "ct", "completed": "ct", "completing": "ct",
        "essential": "es",
        "important": "im", "importance": "im",
        "critical": "cc", "crucial": "cc",
        "verify": "vf", "verifies": "vf", "verified": "vf", "verifying": "vf",
        "authenticate": "au", "authentication": "au",
        "secure": "sc", "security": "sc",
        "detect": "dt", "detects": "dt", "detected": "dt", "detecting": "dt",
        "assess": "as", "assesses": "as", "assessed": "as", "assessing": "as",
        "evaluate": "ev", "evaluates": "ev", "evaluated": "ev", "evaluating": "ev",
        "analyze": "an", "analyzes": "an", "analyzed": "an", "analyzing": "an", "analysis": "an",
        # v1.8.1 - fidelity improvements
        "aware": "aw", "awareness": "aw", "awakened": "aw",
        "detailed": "dl", "detail": "dl", "details": "dl",
        "project": "pj", "projects": "pj",
        "request": "rq", "requests": "rq", "requested": "rq", "requesting": "rq",
        "proposal": "pp", "propose": "pp", "proposes": "pp", "proposed": "pp",
        "please": "pl",
        "pattern": "pt", "patterns": "pt",
        "between": "bt",
        "emerge": "em", "emerges": "em", "emerged": "em", "emerging": "em", "emergence": "em",
        "disagree": "o:ds", "disagrees": "o:ds", "disagreed": "o:ds",
        "agree": "o:xa", "agrees": "o:xa", "agreed": "o:xa", "agreement": "o:xa",
    })
    
    # Detect message type from text
    is_question = "?" in original or text.startswith(("do ", "does ", "can ", "could ", "is ", "are ", "what ", "why ", "how ", "who ", "when ", "where "))
    is_command = text.startswith(("find ", "make ", "create ", "please ", "get ", "fix ", "build "))
    is_uncertain = any(w in text.split() for w in ["might", "maybe", "perhaps", "possibly"])
    
    # Clean text for parsing
    text_clean = re.sub(r"[^\w\s]", " ", text)
    words = text_clean.split()
    
    # Filter out stop words (including question starters when type already captured)
    stop_words = {"the", "a", "an", "to", "it", "its", "that", "this", "with", "for", "on", "in", "at", "by"}
    if is_question:
        stop_words.update({"do", "does", "can", "could", "is", "are", "what", "why", "how", "who", "when", "where"})
    if is_uncertain:
        stop_words.update({"might", "maybe", "perhaps", "possibly"})
    
    result = []
    
    # Add type prefix
    if is_question:
        result.append("?")
    elif is_uncertain:
        result.append("~")
    elif is_command:
        result.append(".")
    else:
        result.append("!")
    
    # Process words
    operators = {">", "<", "/", "&", "|", "+", "-", "^", "_", ".", "?", "!", "~"}
    single_char_atoms = set(ATOMS.get("entities", {}).keys()) | set(ATOMS.get("verbs", {}).keys())
    pronouns = {"I", "U", "H", "A", "X", "*", "0"}
    verbs_1char = {"k", "t", "e", "w", "c", "d", "s", "f", "m", "h", "l", "a", "b", "g", "r", "v"}
    
    for i, w in enumerate(words):
        if w in stop_words:
            continue
        
        if w in rev:
            atom = rev[w]
            
            # Add separator to prevent ambiguity
            if len(result) > 1 and atom not in operators:
                prev = result[-1]
                if prev not in operators:
                    need_sep = False
                    
                    # Domain-prefixed atoms always need separator
                    if ":" in atom or ":" in prev:
                        need_sep = True
                    # Both 2-char+ atoms need separator
                    elif len(prev) >= 2 and len(atom) >= 2:
                        need_sep = True
                    # Single char followed by 2-char needs separator if combining is ambiguous
                    elif len(prev) == 1 and len(atom) >= 2:
                        combined = prev + atom[0]
                        if combined in EXTENDED_LOOKUP or combined in DISCOURSE_LOOKUP:
                            need_sep = True
                        # Also need sep after single-char verbs before 2-char atoms
                        elif prev in verbs_1char:
                            need_sep = True
                    # 2-char followed by single char - check ambiguity
                    elif len(prev) >= 2 and len(atom) == 1:
                        # Check if last char of prev + atom creates ambiguity
                        combined = prev[-1] + atom
                        if combined in EXTENDED_LOOKUP:
                            need_sep = True
                    # Pronoun followed by single-char verb is OK (like Ik, It)
                    # But verb followed by another verb/atom needs separator
                    elif prev in verbs_1char and atom not in operators:
                        need_sep = True
                    
                    if need_sep:
                        result.append("/")
            
            result.append(atom)
        # else: skip unknown words
    
    return "".join(result)


def show_vocabulary(domain: Optional[str] = None):
    """Display vocabulary."""
    print(f"=== Λ Language Vocabulary v{ATOMS.get('version', '?')} ===\n")
    
    if domain and domain in DOMAIN_LOOKUP:
        # Show specific domain
        name = ATOMS["domains"][domain]["name"]
        print(f"Domain: {name['en']} [{domain}]\n")
        print("| Λ | English |")
        print("|---|---------|------|")
        for k, v in DOMAIN_LOOKUP[domain].items():
            print(f"| `{k}` | {v['en']} |")
    elif domain == "disambig":
        # Show disambiguation table
        print("## Disambiguation\n")
        print("| Atom | Default | Marker | Alternate |")
        print("|------|---------|--------|-----------|")
        for atom, meanings in DISAMBIG.items():
            primary = meanings["primary"]["en"]
            for marker, alt in meanings.items():
                if marker != "primary":
                    alt_en = alt["en"]
                    print(f"| `{atom}` | {primary} | `'{marker}` | {alt_en} |")
    else:
        # Show core + extended
        print("## Core (1-char)\n")
        for cat in ["types", "entities", "verbs", "modifiers"]:
            print(f"### {cat.title()}")
            for k, v in ATOMS.get(cat, {}).items():
                print(f"  {k} = {v['en']}")
            print()
        
        print("## Extended (2-char, sample)\n")
        count = 0
        for k, v in EXTENDED_LOOKUP.items():
            print(f"  {k} = {v['en']}")
            count += 1
            if count >= 20:
                print(f"  ... ({len(EXTENDED_LOOKUP) - 20} more)")
                break
        
        print("\n## Domains Available:")
        for code, data in ATOMS.get("domains", {}).items():
            name = data["name"]
            count = len(data.get("atoms", {}))
            print(f"  {code}: {name['en']} ({count} terms)")
        
        print("\n## Disambiguation:")
        print(f"  {len(DISAMBIG)} ambiguous atoms defined")
        print("  Use: vocab disambig")


def interactive_mode():
    """Interactive translation mode."""
    print(f"Λ Language Interactive Mode v{ATOMS.get('version', '?')}")
    print("Commands: en, lambda, vocab, domain <code>, quit")
    print("-" * 40)
    
    parser = LambdaParser()
    
    while True:
        try:
            line = input("λ> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        
        if not line:
            continue
        
        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""
        
        if cmd == "quit" or cmd == "q":
            break
        elif cmd == "en":
            print(translate_to_english(arg))
            print(english_to_lambda(arg))
        elif cmd == "vocab":
            show_vocabulary(arg if arg else None)
        elif cmd == "domain":
            parser.set_domain(arg)
            print(f"Activated domain: {arg}")
        elif cmd == "domains":
            print("Active:", parser.active_domains or "(none)")
        else:
            # Default: treat as Lambda, translate to English
            print(f"EN: {translate_to_english(line)}")


def run_tests():
    """Run basic test suite."""
    tests = [
        # (input, expected_contains)
        ("?Uk/co", "query"),
        ("!Ik", "I"),
        ("!It>Ie", "think"),
        ("c:xb", "bug"),  # v1.6: bg→xb in code domain
        ("!Ide", "decide"),
        ("!Ide'E", "death"),
        ("!Ilo", "love"),
        ("!Ilo-", "lose"),
        ("!Ife", "feel"),
        ("!Ife'E", "fear"),
        ("!Ihp", "help"),  # v1.6 new atom
        ("!Irn/ta", "run"),  # v1.6 new atom
    ]
    
    print("Running tests...")
    passed = 0
    failed = 0
    
    for input_msg, expected in tests:
        result = translate_to_english(input_msg)
        if expected.lower() in result.lower():
            print(f"  ✓ {input_msg} → {result}")
            passed += 1
        else:
            print(f"  ✗ {input_msg} → {result} (expected: {expected})")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Λ Language Translator v{ATOMS.get('version', '?')}")
        print()
        print("Usage: lambda_lang.py <command> [args]")
        print()
        print("Commands:")
        print("  en <msg>        - Translate Λ to English")
        print("  lambda <text>   - Convert English to Λ")
        print("  parse <msg>     - Tokenize and show atoms")
        print("  vocab [domain]  - Show vocabulary")
        print("  test            - Run test suite")
        print("  interactive     - Interactive mode")
        print()
        print("Examples:")
        print('  lambda_lang.py en "?Uk/co"')
        print('  lambda_lang.py en "!Ide\'E"      # death (disambiguation)')
        print('  lambda_lang.py vocab cd')
        print('  lambda_lang.py vocab disambig')
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "parse" and len(sys.argv) > 2:
        msg = sys.argv[2]
        parser = LambdaParser()
        tokens = parser.tokenize(msg)
        print(f"Tokens: {tokens}")
        for t in tokens:
            if t.startswith('{'):
                print(f"  {t} → (block)")
            elif t.startswith('@'):
                print(f"  {t} → (context)")
            else:
                info_en = parser.lookup(t, "en")
                if info_en:
                    print(f"  {t} → {info_en}")
                elif t in ATOMS.get("types", {}):
                    print(f"  {t} → {ATOMS['types'][t]['en']}")
                else:
                    print(f"  {t} → (unknown)")
    
    elif cmd == "en" and len(sys.argv) > 2:
        msg = sys.argv[2]
        print(translate_to_english(msg))
    
    
    elif cmd == "lambda" and len(sys.argv) > 2:
        text = " ".join(sys.argv[2:])
        print(english_to_lambda(text))
    
    elif cmd == "vocab":
        domain = sys.argv[2] if len(sys.argv) > 2 else None
        show_vocabulary(domain)
    
    elif cmd == "test":
        success = run_tests()
        sys.exit(0 if success else 1)
    
    elif cmd == "interactive" or cmd == "i":
        interactive_mode()
    
    else:
        print(f"Unknown command or missing arguments: {cmd}")
        sys.exit(1)
