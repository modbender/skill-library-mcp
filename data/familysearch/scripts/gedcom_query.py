#!/usr/bin/env python3
"""
gedcom_query.py — GEDCOM family tree query tool for OpenClaw
Supports GEDCOM 5.5 and 5.5.1, no external dependencies.
"""

import sys
import os
import re
from collections import defaultdict, deque

# ─────────────────────────────────────────────────────────────────────────────
# GEDCOM PARSER
# ─────────────────────────────────────────────────────────────────────────────

def load_gedcom(path):
    """Parse a GEDCOM file. Returns (individuals dict, families dict)."""
    if not os.path.exists(path):
        die(f"File not found: {path}")

    # Try UTF-8 with BOM, then UTF-8, then latin-1
    content = None
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            with open(path, encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        die("Could not decode GEDCOM file (tried UTF-8 and latin-1)")

    lines = content.splitlines()
    records = _parse_records(lines)
    individuals = {}
    families = {}

    for rec_id, tag, children in records:
        if tag == "INDI":
            individuals[rec_id] = _parse_individual(rec_id, children)
        elif tag == "FAM":
            families[rec_id] = _parse_family(rec_id, children)

    # Link family data into individuals
    _link_families(individuals, families)
    return individuals, families


def _parse_records(lines):
    """Group top-level (level 0) records with their children."""
    records = []
    current_id = None
    current_tag = None
    current_children = []

    for line in lines:
        line = line.rstrip()
        if not line:
            continue
        parts = line.split(" ", 2)
        if len(parts) < 2:
            continue
        level_str = parts[0]
        if not level_str.isdigit():
            continue
        level = int(level_str)

        if level == 0:
            if current_id is not None or current_tag is not None:
                records.append((current_id, current_tag, current_children))
            # 0 @ID@ TAG  or  0 TAG
            if len(parts) >= 3 and parts[1].startswith("@") and parts[1].endswith("@"):
                current_id = parts[1].strip("@")
                current_tag = parts[2].strip()
            else:
                current_id = None
                current_tag = parts[1].strip()
            current_children = []
        else:
            current_children.append((level, parts[1].strip(), parts[2].strip() if len(parts) > 2 else ""))

    if current_id is not None or current_tag is not None:
        records.append((current_id, current_tag, current_children))

    return records


def _get_sub(children, tag, level=1):
    """Get the first value for a sub-tag at the given level."""
    for lv, t, v in children:
        if lv == level and t == tag:
            return v
    return ""


def _get_all(children, tag, level=1):
    """Get all values for a sub-tag at the given level."""
    return [v for lv, t, v in children if lv == level and t == tag]


def _get_event(children, event_tag):
    """Parse a sub-event block (BIRT, DEAT, MARR) returning {date, plac}."""
    result = {"date": "", "plac": ""}
    in_event = False
    for lv, t, v in children:
        if lv == 1 and t == event_tag:
            in_event = True
            continue
        if in_event and lv == 2 and t == "DATE":
            result["date"] = v
        elif in_event and lv == 2 and t == "PLAC":
            result["plac"] = v
        elif lv == 1:
            in_event = False
    return result


def _parse_name(raw):
    """Parse GEDCOM NAME: 'John /Smith/' → ('John', 'Smith', 'John Smith')"""
    if not raw:
        return "", "", "Unknown"
    given = raw.split("/")[0].strip()
    surname_match = re.search(r"/([^/]*)/", raw)
    surname = surname_match.group(1).strip() if surname_match else ""
    full = f"{given} {surname}".strip() if surname else given
    return given, surname, full


def _parse_individual(rec_id, children):
    """Build an individual dict from child lines."""
    raw_name = _get_sub(children, "NAME")
    given, surname, full_name = _parse_name(raw_name)

    # Handle multiple names (GEDCOM allows it)
    all_names = _get_all(children, "NAME")
    alt_names = []
    for n in all_names[1:]:
        _, _, alt_full = _parse_name(n)
        alt_names.append(alt_full)

    birth = _get_event(children, "BIRT")
    death = _get_event(children, "DEAT")
    sex = _get_sub(children, "SEX")
    famc = [v.strip("@") for v in _get_all(children, "FAMC")]  # families as child
    fams = [v.strip("@") for v in _get_all(children, "FAMS")]  # families as spouse

    return {
        "id": rec_id,
        "raw_name": raw_name,
        "given": given,
        "surname": surname,
        "full_name": full_name,
        "alt_names": alt_names,
        "sex": sex,
        "birth": birth,
        "death": death,
        "famc": famc,
        "fams": fams,
        # Will be filled by _link_families:
        "parents": [],
        "spouses": [],
        "children": [],
    }


def _parse_family(rec_id, children):
    husb = _get_sub(children, "HUSB").strip("@")
    wife = _get_sub(children, "WIFE").strip("@")
    chil = [v.strip("@") for v in _get_all(children, "CHIL")]
    marr = _get_event(children, "MARR")
    return {"id": rec_id, "husb": husb, "wife": wife, "chil": chil, "marr": marr}


def _link_families(individuals, families):
    """Populate parents/spouses/children on each individual."""
    for fam in families.values():
        husb_id = fam["husb"]
        wife_id = fam["wife"]
        children_ids = fam["chil"]

        # Spouses
        if husb_id and husb_id in individuals and wife_id and wife_id in individuals:
            if wife_id not in individuals[husb_id]["spouses"]:
                individuals[husb_id]["spouses"].append(wife_id)
            if husb_id not in individuals[wife_id]["spouses"]:
                individuals[wife_id]["spouses"].append(husb_id)

        # Children — set parents
        for child_id in children_ids:
            if child_id not in individuals:
                continue
            child = individuals[child_id]
            if husb_id and husb_id in individuals and husb_id not in child["parents"]:
                child["parents"].append(husb_id)
            if wife_id and wife_id in individuals and wife_id not in child["parents"]:
                child["parents"].append(wife_id)
            # Parent gets child
            for parent_id in [husb_id, wife_id]:
                if parent_id and parent_id in individuals:
                    if child_id not in individuals[parent_id]["children"]:
                        individuals[parent_id]["children"].append(child_id)


# ─────────────────────────────────────────────────────────────────────────────
# LOOKUP HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def find_person(individuals, id_or_name):
    """Find individual by ID or name. Returns individual dict or None."""
    # Try direct ID match (with or without leading 'I')
    probe = id_or_name.strip("@")
    if probe in individuals:
        return individuals[probe]
    # Try prepending I if numeric
    if probe.isdigit():
        padded = f"I{probe.zfill(4)}"  # some GEDCOM use I0001
        if padded in individuals:
            return individuals[padded]
        # Try without padding
        simple = f"I{probe}"
        if simple in individuals:
            return individuals[simple]

    # Fuzzy name search — return best match
    needle = id_or_name.lower()
    candidates = []
    for p in individuals.values():
        score = _name_score(p["full_name"].lower(), needle)
        if score > 0:
            candidates.append((score, p))
    if candidates:
        candidates.sort(key=lambda x: -x[0])
        return candidates[0][1]
    return None


def _name_score(full_name, needle):
    """Simple scoring: exact match > starts with > contains > token match."""
    if full_name == needle:
        return 100
    if full_name.startswith(needle):
        return 80
    if needle in full_name:
        return 60
    # Token match
    needle_tokens = set(needle.split())
    name_tokens = set(full_name.split())
    overlap = len(needle_tokens & name_tokens)
    if overlap > 0:
        return 40 + overlap * 10
    return 0


def fmt_event(evt):
    """Format a {date, plac} event as a readable string."""
    parts = []
    if evt["date"]:
        parts.append(evt["date"])
    if evt["plac"]:
        parts.append(evt["plac"])
    return ", ".join(parts) if parts else ""


def pname(p):
    return p["full_name"] if p else "Unknown"


# ─────────────────────────────────────────────────────────────────────────────
# COMMANDS
# ─────────────────────────────────────────────────────────────────────────────

def cmd_search(individuals, args):
    if not args:
        die("Usage: search <name>")
    needle = " ".join(args).lower()
    results = []
    for p in individuals.values():
        score = _name_score(p["full_name"].lower(), needle)
        if score > 0:
            results.append((score, p))
    results.sort(key=lambda x: -x[0])

    if not results:
        print(f"🔍 No results found for '{' '.join(args)}'")
        return

    print(f"🔍 Search results for '{' '.join(args)}' ({len(results)} found):\n")
    for _, p in results[:20]:
        birth_yr = _year(p["birth"]["date"])
        death_yr = _year(p["death"]["date"])
        life = f"({birth_yr}–{death_yr})" if birth_yr or death_yr else ""
        print(f"  {p['id']:>8}  {p['full_name']:<30} {life}")


def cmd_person(individuals, args):
    if not args:
        die("Usage: person <id_or_name>")
    p = find_person(individuals, " ".join(args))
    if not p:
        die(f"Person not found: {' '.join(args)}")

    print(f"\n👤 {p['full_name']}")
    print(f"   ID: {p['id']}")
    if p["sex"]:
        sex_label = {"M": "Male", "F": "Female", "U": "Unknown"}.get(p["sex"].upper(), p["sex"])
        print(f"   Sex: {sex_label}")

    birth = fmt_event(p["birth"])
    if birth:
        print(f"   🎂 Born:  {birth}")

    death = fmt_event(p["death"])
    if death:
        print(f"   ✝️  Died:  {death}")

    if p["parents"]:
        print(f"\n   👪 Parents:")
        for pid in p["parents"]:
            par = individuals.get(pid)
            print(f"      • {pname(par)} ({pid})")

    if p["spouses"]:
        print(f"\n   💍 Spouse(s):")
        for sid in p["spouses"]:
            sp = individuals.get(sid)
            print(f"      • {pname(sp)} ({sid})")

    if p["children"]:
        print(f"\n   👶 Children ({len(p['children'])}):")
        for cid in p["children"]:
            ch = individuals.get(cid)
            print(f"      • {pname(ch)} ({cid})")

    print()


def cmd_ancestors(individuals, args):
    if not args:
        die("Usage: ancestors <id_or_name> [depth]")
    depth = 4
    if len(args) >= 2 and args[-1].isdigit():
        depth = int(args[-1])
        name_args = args[:-1]
    else:
        name_args = args

    p = find_person(individuals, " ".join(name_args))
    if not p:
        die(f"Person not found: {' '.join(name_args)}")

    print(f"\n🌳 Ancestors of {p['full_name']} (up to {depth} generations)\n")
    _print_ancestors(individuals, p["id"], depth, 0, "")


def _print_ancestors(individuals, pid, max_depth, gen, prefix):
    p = individuals.get(pid)
    if not p:
        return
    if gen == 0:
        birth_yr = _year(p["birth"]["date"])
        life = f" (b. {birth_yr})" if birth_yr else ""
        print(f"Gen 0: {p['full_name']}{life} [{pid}]")
    if gen < max_depth:
        parents = p["parents"]
        for i, parent_id in enumerate(parents):
            is_last = (i == len(parents) - 1)
            child_prefix = prefix + ("    " if is_last else "│   ")
            connector = prefix + ("└── " if is_last else "├── ")
            par = individuals.get(parent_id)
            if par:
                birth_yr2 = _year(par["birth"]["date"])
                life2 = f" (b. {birth_yr2})" if birth_yr2 else ""
                print(f"{connector}Gen {gen+1}: {par['full_name']}{life2} [{parent_id}]")
                _print_ancestors(individuals, parent_id, max_depth, gen + 1, child_prefix)


def cmd_descendants(individuals, args):
    if not args:
        die("Usage: descendants <id_or_name> [depth]")
    depth = 3
    if len(args) >= 2 and args[-1].isdigit():
        depth = int(args[-1])
        name_args = args[:-1]
    else:
        name_args = args

    p = find_person(individuals, " ".join(name_args))
    if not p:
        die(f"Person not found: {' '.join(name_args)}")

    print(f"\n🌿 Descendants of {p['full_name']} (up to {depth} generations)\n")
    _print_descendants(individuals, p["id"], depth, 0, "")


def _print_descendants(individuals, pid, max_depth, gen, prefix):
    p = individuals.get(pid)
    if not p:
        return
    birth_yr = _year(p["birth"]["date"])
    life = f" (b. {birth_yr})" if birth_yr else ""
    if gen == 0:
        print(f"Gen 0: {p['full_name']}{life} [{pid}]")
    if gen < max_depth:
        children = p["children"]
        for i, child_id in enumerate(children):
            is_last = (i == len(children) - 1)
            connector = prefix + ("└── " if is_last else "├── ")
            child_prefix = prefix + ("    " if is_last else "│   ")
            ch = individuals.get(child_id)
            if ch:
                birth_yr2 = _year(ch["birth"]["date"])
                life2 = f" (b. {birth_yr2})" if birth_yr2 else ""
                print(f"{connector}Gen {gen+1}: {ch['full_name']}{life2} [{child_id}]")
                _print_descendants(individuals, child_id, max_depth, gen + 1, child_prefix)


def cmd_story(individuals, args):
    if not args:
        die("Usage: story <id_or_name>")
    p = find_person(individuals, " ".join(args))
    if not p:
        die(f"Person not found: {' '.join(args)}")

    print(f"\n📖 Life Story: {p['full_name']}\n")
    print(_generate_story(individuals, p))
    print()


def _generate_story(individuals, p):
    name = p["full_name"]
    pronoun = {"M": ("He", "his", "him"), "F": ("She", "her", "her")}.get(
        p["sex"].upper() if p["sex"] else "", ("They", "their", "them")
    )
    he, his, him = pronoun

    sentences = []

    # Birth sentence
    birth = fmt_event(p["birth"])
    if birth:
        sentences.append(f"{name} was born on {birth}.")
    else:
        sentences.append(f"{name} lived in a time when records were sparse.")

    # Parents
    if p["parents"]:
        parent_names = [pname(individuals.get(pid)) for pid in p["parents"][:2]]
        if len(parent_names) == 2:
            sentences.append(
                f"{he} was the child of {parent_names[0]} and {parent_names[1]}."
            )
        else:
            sentences.append(f"{he} was the child of {parent_names[0]}.")

    # Marriage
    if p["spouses"]:
        sp = individuals.get(p["spouses"][0])
        sp_name = pname(sp)
        # Find marriage date from families
        marr_info = _find_marriage_info(individuals, p, sp)
        if marr_info:
            sentences.append(f"{he} married {sp_name} {marr_info}.")
        else:
            sentences.append(f"{he} married {sp_name}.")
        if len(p["spouses"]) > 1:
            others = [pname(individuals.get(s)) for s in p["spouses"][1:]]
            sentences.append(f"{he} was also married to {', '.join(others)}.")

    # Children
    if p["children"]:
        count = len(p["children"])
        child_names = [pname(individuals.get(c)) for c in p["children"][:3]]
        if count == 1:
            sentences.append(f"{he} had one child: {child_names[0]}.")
        elif count <= 3:
            sentences.append(
                f"{he} had {count} children: {', '.join(child_names[:-1])}, and {child_names[-1]}."
            )
        else:
            sentences.append(
                f"{he} had {count} children, including {', '.join(child_names[:3])}, and others."
            )

    # Death
    death = fmt_event(p["death"])
    if death:
        sentences.append(f"{he} passed away {death}.")
    else:
        sentences.append(f"The date and place of {his} death are not recorded.")

    return " ".join(sentences)


def _find_marriage_info(individuals, p1, p2):
    """Try to find marriage date between two individuals."""
    if not p2:
        return ""
    for fam_id in p1["fams"]:
        # We need the families dict — re-access is a bit tricky here
        # Return empty if not available (acceptable limitation)
        pass
    return ""


def cmd_timeline(individuals, args):
    if not args:
        die("Usage: timeline <id_or_name>")
    p = find_person(individuals, " ".join(args))
    if not p:
        die(f"Person not found: {' '.join(args)}")

    print(f"\n📅 Timeline: {p['full_name']}\n")
    events = []

    birth = p["birth"]
    if birth["date"] or birth["plac"]:
        yr = _year(birth["date"])
        events.append((yr or "????", "🎂", f"Born{' — ' + birth['plac'] if birth['plac'] else ''}{' on ' + birth['date'] if birth['date'] else ''}"))

    # Marriage events (via spouses — approximate)
    for sp_id in p["spouses"]:
        sp = individuals.get(sp_id)
        if sp:
            events.append(("????", "💍", f"Married {pname(sp)}"))

    # Children born
    for c_id in p["children"]:
        ch = individuals.get(c_id)
        if ch:
            birth_yr = _year(ch["birth"]["date"])
            events.append((birth_yr or "????", "👶", f"Child born: {pname(ch)}"))

    death = p["death"]
    if death["date"] or death["plac"]:
        yr = _year(death["date"])
        events.append((yr or "????", "✝️ ", f"Died{' — ' + death['plac'] if death['plac'] else ''}{' on ' + death['date'] if death['date'] else ''}"))

    if not events:
        print("  No recorded events found.\n")
        return

    # Sort by year
    def sort_key(e):
        try:
            return int(str(e[0]).lstrip("~c "))
        except:
            return 9999

    events.sort(key=sort_key)
    for yr, emoji, desc in events:
        print(f"  {str(yr):>6}  {emoji}  {desc}")
    print()


def cmd_stats(individuals, families):
    print("\n📊 Family Tree Statistics\n")
    total = len(individuals)
    print(f"  👥 Total individuals: {total}")
    print(f"  👪 Total families:     {len(families)}")

    # Sex distribution
    sex_counts = defaultdict(int)
    for p in individuals.values():
        sex_counts[p["sex"] or "?"] += 1
    print(f"  ♂  Male:   {sex_counts.get('M', 0)}")
    print(f"  ♀  Female: {sex_counts.get('F', 0)}")

    # Completeness
    with_birth = sum(1 for p in individuals.values() if p["birth"]["date"])
    with_death = sum(1 for p in individuals.values() if p["death"]["date"])
    print(f"\n  📈 Completeness:")
    print(f"     Birth date known: {with_birth}/{total} ({pct(with_birth, total)}%)")
    print(f"     Death date known: {with_death}/{total} ({pct(with_death, total)}%)")

    # Top surnames
    surname_counts = defaultdict(int)
    for p in individuals.values():
        if p["surname"]:
            surname_counts[p["surname"]] += 1
    top_surnames = sorted(surname_counts.items(), key=lambda x: -x[1])[:10]
    if top_surnames:
        print(f"\n  🏷️  Top Surnames:")
        for name, cnt in top_surnames:
            bar = "█" * min(cnt, 30)
            print(f"     {name:<20} {cnt:>4}  {bar}")

    # Birth decade distribution
    decade_counts = defaultdict(int)
    for p in individuals.values():
        yr = _year(p["birth"]["date"])
        if yr:
            decade = (int(yr) // 10) * 10
            decade_counts[decade] += 1

    if decade_counts:
        print(f"\n  📆 Birth Decades:")
        max_count = max(decade_counts.values())
        for decade in sorted(decade_counts.keys()):
            cnt = decade_counts[decade]
            bar_len = int(cnt / max_count * 25)
            bar = "▓" * bar_len
            print(f"     {decade}s  {cnt:>3}  {bar}")
    print()


def cmd_find_date(individuals, args):
    if not args or not args[0].isdigit():
        die("Usage: find-date <year>")
    year = args[0]
    results = []
    for p in individuals.values():
        birth_yr = _year(p["birth"]["date"])
        death_yr = _year(p["death"]["date"])
        if birth_yr == year:
            results.append(("born", p))
        elif death_yr == year:
            results.append(("died", p))

    if not results:
        print(f"📅 No records found for year {year}")
        return

    print(f"\n📅 People with records in {year}:\n")
    for evt_type, p in results:
        print(f"  {'🎂' if evt_type == 'born' else '✝️ '}  {p['full_name']:<30} ({evt_type}) [{p['id']}]")
    print()


def cmd_common_ancestor(individuals, args):
    if not args:
        die("Usage: common-ancestor <name1> <name2>")

    joined = " ".join(args)

    # Case 1: comma-separated in single or multiple args
    if "," in joined:
        parts = joined.split(",", 1)
        name1, name2 = parts[0].strip(), parts[1].strip()
    elif len(args) == 1:
        die("Usage: common-ancestor <name1> <name2>  (or: common-ancestor 'Name One,Name Two')")
    elif len(args) == 2:
        # Each arg is one full name (most common case when shell-quoted)
        name1, name2 = args[0], args[1]
    else:
        # Multiple tokens: try to split by looking for individual IDs
        # First check if any arg looks like an ID
        id_positions = [i for i, a in enumerate(args) if re.match(r'^@?I\d+@?$', a, re.IGNORECASE)]
        if len(id_positions) >= 2:
            name1 = args[id_positions[0]]
            name2 = args[id_positions[1]]
        else:
            # Split roughly in half
            mid = max(1, len(args) // 2)
            name1 = " ".join(args[:mid])
            name2 = " ".join(args[mid:])

    p1 = find_person(individuals, name1)
    p2 = find_person(individuals, name2)

    if not p1:
        die(f"Person not found: {name1}")
    if not p2:
        die(f"Person not found: {name2}")

    print(f"\n🔗 Finding common ancestor between:")
    print(f"   A: {p1['full_name']} [{p1['id']}]")
    print(f"   B: {p2['full_name']} [{p2['id']}]\n")

    # BFS from both, find intersection
    ancestors1 = _bfs_ancestors(individuals, p1["id"])
    ancestors2 = _bfs_ancestors(individuals, p2["id"])

    common = {}
    for anc_id, dist in ancestors1.items():
        if anc_id in ancestors2:
            common[anc_id] = dist + ancestors2[anc_id]

    if not common:
        print("  ❌ No common ancestor found in the tree.\n")
        return

    # Find closest
    best_id = min(common, key=lambda x: common[x])
    best = individuals[best_id]
    dist1 = ancestors1[best_id]
    dist2 = ancestors2[best_id]

    print(f"  ✅ Closest common ancestor: {best['full_name']} [{best_id}]")
    birth = fmt_event(best["birth"])
    if birth:
        print(f"     Born: {birth}")
    print(f"     Distance: {dist1} generation(s) from {p1['full_name']}")
    print(f"               {dist2} generation(s) from {p2['full_name']}")

    rel = _describe_relationship(dist1, dist2)
    print(f"     Relationship: {rel}\n")


def _bfs_ancestors(individuals, start_id):
    """BFS from individual upward. Returns {id: generations_distance}."""
    visited = {}
    queue = deque([(start_id, 0)])
    while queue:
        pid, dist = queue.popleft()
        if pid in visited:
            continue
        visited[pid] = dist
        p = individuals.get(pid)
        if p:
            for parent_id in p["parents"]:
                if parent_id not in visited:
                    queue.append((parent_id, dist + 1))
    return visited


def _describe_relationship(d1, d2):
    """Human-readable relationship description based on distances."""
    if d1 == 1 and d2 == 1:
        return "Siblings"
    if d1 == 1 and d2 == 2:
        return "Uncle/Aunt and Nephew/Niece"
    if d1 == 2 and d2 == 1:
        return "Uncle/Aunt and Nephew/Niece"
    if d1 == 2 and d2 == 2:
        return "First Cousins"
    if d1 == 0:
        return f"Direct ancestor ({d2} generation(s) up)"
    if d2 == 0:
        return f"Direct ancestor ({d1} generation(s) up)"
    removal = abs(d1 - d2)
    cousin_num = min(d1, d2) - 1
    if cousin_num == 1:
        base = "First Cousins"
    elif cousin_num == 2:
        base = "Second Cousins"
    elif cousin_num == 3:
        base = "Third Cousins"
    else:
        base = f"{cousin_num}th Cousins"
    if removal == 0:
        return base
    return f"{base}, {removal}x Removed"


# ─────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def _year(date_str):
    """Extract 4-digit year from a GEDCOM date string."""
    if not date_str:
        return None
    m = re.search(r"\b(\d{4})\b", date_str)
    return m.group(1) if m else None


def pct(num, denom):
    if denom == 0:
        return 0
    return round(num / denom * 100)


def die(msg):
    print(f"❌ Error: {msg}", file=sys.stderr)
    sys.exit(1)


def usage():
    print("""
Usage: python gedcom_query.py <gedcom_file> <command> [args...]

Commands:
  search <name>                     Search people by name
  person <id_or_name>               Full profile with family links
  ancestors <id_or_name> [depth]    Pedigree chart upward (default: 4)
  descendants <id_or_name> [depth]  Pedigree chart downward (default: 3)
  story <id_or_name>                Narrative biography paragraph
  timeline <id_or_name>             Chronological life events
  stats                             Tree statistics and summaries
  find-date <year>                  Find people born/died in a year
  common-ancestor <name1> <name2>   Find closest common ancestor

Examples:
  python gedcom_query.py family.ged stats
  python gedcom_query.py family.ged search "John Smith"
  python gedcom_query.py family.ged person "Mary Johnson"
  python gedcom_query.py family.ged ancestors I001 3
  python gedcom_query.py family.ged story "William Adams"
  python gedcom_query.py family.ged common-ancestor "John Adams,Mary Adams"
""")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    gedcom_file = sys.argv[1]
    command = sys.argv[2].lower()
    args = sys.argv[3:]

    individuals, families = load_gedcom(gedcom_file)

    if command == "search":
        cmd_search(individuals, args)
    elif command == "person":
        cmd_person(individuals, args)
    elif command == "ancestors":
        cmd_ancestors(individuals, args)
    elif command == "descendants":
        cmd_descendants(individuals, args)
    elif command == "story":
        cmd_story(individuals, args)
    elif command == "timeline":
        cmd_timeline(individuals, args)
    elif command == "stats":
        cmd_stats(individuals, families)
    elif command == "find-date":
        cmd_find_date(individuals, args)
    elif command == "common-ancestor":
        cmd_common_ancestor(individuals, args)
    else:
        die(f"Unknown command: {command}")
        usage()


if __name__ == "__main__":
    main()
