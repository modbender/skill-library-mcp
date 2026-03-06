#!/usr/bin/env python3
"""
topic_filter.py - Deduplication thematique des articles de veille.

Logique :
  1. Empreinte titre -> mots-cles normalises (Jaccard) + entites nommees
     (noms propres, nombres, CVE IDs) - robuste cross-langue FR/EN.
  2. Similarite = max(Jaccard_mots_cles, score_entites_nommees).
  3. Sources classees par tier d'autorite (1 = forte, 3 = secondaire).
  4. Un article T2/T3 est filtre si un article de meilleur tier couvrant le
     meme sujet a deja ete vu (batch courant OU store historique).

Tiers d'autorite :
  1 - reference : CERT-FR, Krebs, BleepingComputer, SANS ISC, Ars Technica,
                  Schneier on Security, The Hacker News
  2 - bonne autorite : The Register, Dark Reading, LWN, The New Stack,
                       Lobste.rs, Hacker News
  3 - secondaires/locales : IT-Connect, Korben, DevOps.com

v1 simplifiee : la zone grise (0.25-0.40) est CONSERVEE (pas d'arbitrage LLM).
On ne filtre que les duplicates nets au-dessus de TOPIC_SIMILARITY_THRESHOLD.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# ---- Autorite des sources ---------------------------------------------------

SOURCE_AUTHORITY: dict = {
    # Tier 1 - Autorite forte (reference absolue)
    "CERT-FR":               1,
    "CERT-FR Avis":          1,
    "CERT-FR Alertes":       1,
    "CERT-FR Complet":       1,
    "CERT-FR CTI":           1,
    "CERT-FR Durcissement":  1,
    "Krebs on Security":     1,
    "Schneier on Security":  1,
    "BleepingComputer":      1,
    "SANS ISC":              1,
    "Ars Technica Security": 1,
    "The Hacker News":       1,
    "CISA Advisories":       1,
    "NCSC UK":               1,
    "NVD CVE":               1,
    "Microsoft MSRC":        1,
    "Google Security Blog":  1,
    # Tier 2 - Bonne autorite
    "The Register":          2,
    "Dark Reading":          2,
    "LWN.net":               2,
    "The New Stack":         2,
    "Lobste.rs":             2,
    "Hacker News":           2,
    "SecurityWeek":          2,
    "Help Net Security":     2,
    "Malwarebytes Blog":     2,
    "Recorded Future":       2,
    "Trail of Bits":         2,
    "AWS Security Blog":     2,
    "Ubuntu Security":       2,
    "Mozilla Security":      2,
    "Docker Blog":           2,
    "HashiCorp Blog":        2,
    "Kubernetes Blog":       2,
    "GitHub Blog":           2,
    "InfoQ":                 2,
    "Simon Willison":        2,
    "Hugging Face Blog":     2,
    "VentureBeat AI":        2,
    "MIT Tech Review":       2,
    "CoinDesk":              2,
    "CoinTelegraph":         2,
    "The Decoder":           2,
    # Tier 2 - Actualites / presse de reference
    "Le Monde":              2,
    "BBC News":              2,
    "The Guardian":          2,
    "The Economist":         2,
    "Bloomberg":             2,
    "Financial Times":       2,
    "Nature News":           2,
    "Foreign Policy":        2,
    "Al Jazeera":            2,
    "France Info":           2,
    "RFI":                   2,
    "Courrier International": 2,
    "Science Daily":         2,
    # Tier 3 - Sources secondaires / locales
    "IT-Connect":            3,
    "Korben":                3,
    "DevOps.com":            3,
    "Journal du Coin":       3,
    "Le Big Data":           3,
    "Phoronix":              3,
    "OMG Ubuntu":            3,
    "Linux Today":           3,
    "OpenSource.com":        3,
    "LinuxFR":               3,
    "Red Hat Blog":          3,
    "CNCF Blog":             3,
    "GitLab Blog":           3,
    "Stack Overflow Blog":   3,
    "Martin Fowler":         3,
    "Ars Technica":          3,
    "TechCrunch":            3,
    "Wired":                 3,
    "VentureBeat":           3,
    "Numerama":              3,
    "NextINpact":            3,
    "Le Monde Informatique": 3,
    "ZDNet France":          3,
    "01net":                 3,
    "Bitcoin Magazine":      3,
    "Decrypt":               3,
    "The Block":             3,
    "Towards AI":            3,
}

# ---- Parametres -------------------------------------------------------------

TOPIC_SIMILARITY_THRESHOLD = 0.40   # seuil net : duplicate evident -> filtre
TOPIC_SOFT_MIN             = 0.25   # zone grise bas (conservee en v1)
TOPIC_SOFT_MAX             = 0.40   # zone grise haut
TOPIC_MIN_SHARED_WORDS     = 2      # mots en commun minimum (Jaccard)
TOPIC_MIN_SHARED_NE        = 2      # entites nommees en commun minimum
TOPIC_TTL_DAYS             = 5      # retention du store thematique (jours)

# ---- Paths ------------------------------------------------------------------

SKILL_DIR       = Path(__file__).resolve().parent.parent
_DATA_DIR       = Path.home() / ".openclaw" / "data" / "veille"
TOPIC_SEEN_FILE = _DATA_DIR / "topic_seen.json"

# ---- Stopwords FR + EN ------------------------------------------------------

_STOPWORDS = {
    # FR
    "le","la","les","un","une","des","du","de","d","en","et","ou","est","sont",
    "sur","pour","par","avec","sans","dans","au","aux","ce","qui","que","se",
    "il","elle","ils","elles","vous","nous","je","tu","a","l","n","y","on",
    "c","si","mais","car","donc","ni","ne","pas","plus","tres","bien","tout",
    "aussi","meme","encore","apres","avant","sous","lors","via","des","les",
    "une","son","ses","leur","leurs","dont","ou","cette","ces","cet",
    # EN
    "the","a","an","of","in","to","is","are","was","were","and","or","but",
    "for","with","on","at","by","from","how","what","why","when","where",
    "who","which","that","this","these","those","it","its","be","been","has",
    "have","had","will","can","could","would","should","new","now","more",
    "also","after","over","about","up","as","into","out","not","may","all",
    "use","used","using","your","their","our","his","her","they","we","get",
    "got","just","than","then","them","being","so","do","did","two","says",
    "say","said","one","first","last","via",
}

# ---- Empreinte mots-cles (Jaccard standard) ---------------------------------


def title_fingerprint(title: str) -> frozenset:
    """
    Extrait un ensemble de mots-cles normalises depuis un titre.
    Conserve : nombres, acronymes, termes techniques.
    Supprime : stopwords FR/EN, mots < 3 caracteres.
    """
    t = title.lower()
    t = re.sub(r"[^\w\s]", " ", t)
    words = t.split()
    return frozenset(w for w in words if w not in _STOPWORDS and len(w) >= 3)


# ---- Entites nommees (robuste cross-langue) ---------------------------------


def named_entities(title: str) -> frozenset:
    """
    Extrait les entites nommees language-agnostic depuis un titre :
      - Identifiants CVE complets (cve-2024-1234)
      - Nombres discriminants : >= 3 chiffres, hors annees (2010-2029)
      - Noms propres capitalises (Fortinet, VMware, Kubernetes...)
      - Acronymes techniques (RCE, SQL, VPN...)
    """
    entities: set = set()

    # CVE IDs complets
    entities.update(re.findall(r'cve-\d{4}-\d+', title.lower()))

    # Nombres discriminants
    for n in re.findall(r'\b(\d+)\b', title):
        if len(n) >= 3 and not (len(n) == 4 and n[:2] in ("20", "19")):
            entities.add(n)

    # Noms propres capitalises
    for w in re.findall(r'\b[A-Z][A-Za-z]{2,}\b', title):
        lower = w.lower()
        if lower not in _STOPWORDS:
            entities.add(lower)

    # Acronymes techniques
    for w in re.findall(r'\b[A-Z]{2,}\b', title):
        lower = w.lower()
        if lower != "cve":
            entities.add(lower)

    return frozenset(entities)


# ---- Similarite combinee ----------------------------------------------------


def _jaccard_raw(s1: frozenset, s2: frozenset, min_shared: int = 1) -> float:
    if not s1 or not s2:
        return 0.0
    inter = len(s1 & s2)
    if inter < min_shared:
        return 0.0
    union = len(s1 | s2)
    return inter / union if union > 0 else 0.0


def article_similarity(title1: str, title2: str,
                        fp1: frozenset = None, fp2: frozenset = None,
                        ne1: frozenset = None, ne2: frozenset = None) -> float:
    """
    Calcule la similarite thematique entre deux titres.
    Combine Jaccard sur mots-cles + overlap sur entites nommees.
    Retourne une valeur entre 0 et 1.
    """
    fp1 = fp1 if fp1 is not None else title_fingerprint(title1)
    fp2 = fp2 if fp2 is not None else title_fingerprint(title2)
    ne1 = ne1 if ne1 is not None else named_entities(title1)
    ne2 = ne2 if ne2 is not None else named_entities(title2)

    kw_score = _jaccard_raw(fp1, fp2, min_shared=TOPIC_MIN_SHARED_WORDS)

    shared_ne = ne1 & ne2
    ne_score = 0.0
    if len(shared_ne) >= TOPIC_MIN_SHARED_NE:
        ne_jaccard = _jaccard_raw(ne1, ne2, min_shared=TOPIC_MIN_SHARED_NE)
        has_anchor = any(
            (re.match(r'^\d{3,}$', e) and not (len(e) == 4 and e[:2] in ("20", "19")))
            or re.match(r'^cve-\d{4}-\d+$', e)
            for e in shared_ne
        )
        if has_anchor:
            ne_score = max(ne_jaccard, TOPIC_SIMILARITY_THRESHOLD + 0.05)
        else:
            ne_score = ne_jaccard

    return max(kw_score, ne_score)


def source_tier(source: str) -> int:
    """Retourne le tier d'une source (1 = forte, 99 = inconnue)."""
    return SOURCE_AUTHORITY.get(source, 99)


# ---- Store historique thematique --------------------------------------------


class TopicStore:
    """
    Stocke les empreintes thematiques des articles deja publie.
    TTL : TOPIC_TTL_DAYS jours.

    Format JSON :
    {
      "<url>": {
        "ts":     "2026-02-24T07:00:00",
        "tier":   1,
        "source": "BleepingComputer",
        "title":  "...",
        "fp":     ["600", "attack", "fortinet"],
        "ne":     ["600", "fortinet"]
      }
    }
    """

    def __init__(self, path: Path = TOPIC_SEEN_FILE, ttl_days: int = TOPIC_TTL_DAYS):
        self.path = path
        self.ttl_days = ttl_days
        self._data: Optional[dict] = None
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _ensure_loaded(self):
        if self._data is not None:
            return
        raw = {}
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                pass
        cutoff = (datetime.now() - timedelta(days=self.ttl_days)).isoformat()
        self._data = {k: v for k, v in raw.items() if v.get("ts", "") >= cutoff}

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )

    def mark_seen(self, articles: list):
        """
        Stocke les empreintes d'une liste d'articles publie.
        Chaque article doit avoir au moins : "url", "title", "source".
        """
        self._ensure_loaded()
        now = datetime.now().isoformat(timespec="seconds")
        for a in articles:
            url    = a.get("url", "")
            title  = a.get("title", "")
            source = a.get("source", "")
            if not url:
                continue
            fp = title_fingerprint(title)
            ne = named_entities(title)
            self._data[url] = {
                "ts":     now,
                "tier":   source_tier(source),
                "source": source,
                "title":  title,
                "fp":     sorted(fp),
                "ne":     sorted(ne),
            }
        self._save()

    def get_seen_entries(self) -> list:
        """
        Retourne les entrees du store sous forme de dicts avec fp et ne
        deja convertis en frozensets pour comparaison.
        """
        self._ensure_loaded()
        result = []
        for entry in self._data.values():
            result.append({
                "tier":   entry.get("tier", 99),
                "source": entry.get("source", ""),
                "title":  entry.get("title", ""),
                "fp":     frozenset(entry.get("fp", [])),
                "ne":     frozenset(entry.get("ne", [])),
            })
        return result

    def stats(self) -> dict:
        self._ensure_loaded()
        return {
            "total":    len(self._data),
            "ttl_days": self.ttl_days,
            "file":     str(self.path),
        }


# ---- Deduplication ----------------------------------------------------------


def _is_dominated(title: str, source: str, tier: int,
                   fp: frozenset, ne: frozenset,
                   candidates: list,
                   threshold: float = TOPIC_SIMILARITY_THRESHOLD) -> bool:
    """
    Verifie si un article est domine par un des candidats (meilleur tier).
    v1 : seulement les duplicates nets (sim >= threshold).
    La zone grise (0.25-0.40) est conservee.
    """
    for c in candidates:
        if c["tier"] >= tier:
            continue   # on ne filtre que si la source concurrente est meilleure
        sim = article_similarity(title, c["title"], fp, c["fp"], ne, c["ne"])
        if sim >= threshold:
            return True   # duplicate net

    return False


def deduplicate_articles(
    articles: list,
    store: TopicStore,
    threshold: float = TOPIC_SIMILARITY_THRESHOLD,
) -> tuple:
    """
    Deduplique une liste d'articles par sujet + autorite de source.

    Regles :
    1. Store historique : si un article avec un meilleur tier a deja couvert
       le meme sujet -> filtre.
    2. Intra-batch : tri par tier ascendant (meilleure source en premier) ;
       un article de tier inferieur est filtre si une meilleure source dans
       le meme batch couvre deja le meme sujet.
    3. Zone grise (similarite 0.25-0.40) : conservee en v1 (pas de LLM).

    Retourne : (articles_retenus, nb_filtres)
    L'ordre de publication est restaure apres deduplication.
    """
    hist_entries = store.get_seen_entries()

    # Tri par tier ascendant (tier 1 en premier = priorite absolue)
    sorted_arts = sorted(articles, key=lambda a: source_tier(a.get("source", "")))

    kept: list = []
    kept_meta: list = []
    filtered = 0

    for article in sorted_arts:
        title  = article.get("title", "")
        source = article.get("source", "")
        tier   = source_tier(source)
        fp     = title_fingerprint(title)
        ne     = named_entities(title)

        # 1. Verification contre le store historique
        if _is_dominated(title, source, tier, fp, ne, hist_entries, threshold):
            filtered += 1
            continue

        # 2. Verification intra-batch
        if _is_dominated(title, source, tier, fp, ne, kept_meta, threshold):
            filtered += 1
            continue

        kept.append(article)
        kept_meta.append({"tier": tier, "title": title, "fp": fp, "ne": ne, "source": source})

    # Restaure l'ordre par date de publication (decroissant)
    kept.sort(key=lambda a: a.get("published_ts", 0), reverse=True)

    return kept, filtered


# ---- Instance partagee ------------------------------------------------------

topic_store = TopicStore()


# ---- CLI debug --------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Inspecte le store thematique")
    parser.add_argument("--list", action="store_true", help="Liste toutes les empreintes")
    parser.add_argument("--test", type=str, nargs=2, metavar=("TITRE1", "TITRE2"),
                        help="Calcule la similarite entre deux titres")
    args = parser.parse_args()

    if args.test:
        t1, t2 = args.test
        fp1, fp2 = title_fingerprint(t1), title_fingerprint(t2)
        ne1, ne2 = named_entities(t1), named_entities(t2)
        sim = article_similarity(t1, t2, fp1, fp2, ne1, ne2)
        kw  = _jaccard_raw(fp1, fp2, min_shared=TOPIC_MIN_SHARED_WORDS)
        print(f"Titre 1 : {t1}")
        print(f"  fp  : {sorted(fp1)}")
        print(f"  ne  : {sorted(ne1)}")
        print(f"Titre 2 : {t2}")
        print(f"  fp  : {sorted(fp2)}")
        print(f"  ne  : {sorted(ne2)}")
        print(f"Jaccard mots-cles : {kw:.3f}")
        print(f"Similarite finale : {sim:.3f}  ({'DUPLIQUE' if sim >= TOPIC_SIMILARITY_THRESHOLD else 'distinct'})")
    else:
        s = topic_store.stats()
        print(f"Store : {s['file']}")
        print(f"TTL   : {s['ttl_days']} jours")
        print(f"Total : {s['total']} empreintes")
        if args.list:
            topic_store._ensure_loaded()
            for url, v in sorted(topic_store._data.items(), key=lambda x: x[1]["ts"], reverse=True):
                ne_str = ",".join(v.get("ne", [])[:5])
                print(f"  {v['ts']}  T{v['tier']}  [{v['source'][:20]:20}]  {v['title'][:60]}")
                print(f"          ne: {ne_str}")
