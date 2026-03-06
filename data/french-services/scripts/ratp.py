#!/usr/bin/env python3
"""RATP/IDFM — Transports en commun Île-de-France via l'API PRIM.

Usage:
    python3 ratp.py traffic
    python3 ratp.py traffic --line "Métro 13"
    python3 ratp.py traffic --line "RER A"
    python3 ratp.py next "Châtelet"

Nécessite IDFM_API_KEY (gratuit sur https://prim.iledefrance-mobilites.fr).
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime

API_BASE = "https://prim.iledefrance-mobilites.fr/marketplace"


def get_api_key():
    key = os.environ.get("IDFM_API_KEY")
    if not key:
        print("❌ Variable d'environnement IDFM_API_KEY non définie.", file=sys.stderr)
        print("   Inscris-toi gratuitement sur https://prim.iledefrance-mobilites.fr", file=sys.stderr)
        print("   Puis : export IDFM_API_KEY=ta-clé", file=sys.stderr)
        sys.exit(1)
    return key


def api_call(endpoint, params=None, accept="application/json"):
    """Appel authentifié à l'API PRIM."""
    key = get_api_key()
    url = f"{API_BASE}{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url, headers={
        "apikey": key,
        "Accept": accept,
        "User-Agent": "french-services/1.0",
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode()
            content_type = resp.headers.get("Content-Type", "")
            if "json" in content_type or content.strip().startswith(("{", "[")):
                return json.loads(content)
            elif "xml" in content_type or content.strip().startswith("<"):
                return {"_xml": content}
            return {"_raw": content}
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("❌ Clé API invalide. Vérifie IDFM_API_KEY.", file=sys.stderr)
        else:
            body = e.read().decode() if e.fp else ""
            print(f"❌ Erreur API ({e.code}): {body[:200]}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌ Erreur réseau : {e}", file=sys.stderr)
        sys.exit(1)


# Lignes connues IDFM (mapping nom → ID STIF)
LINES = {
    # Métro
    "métro 1": "IDFM:C01371", "metro 1": "IDFM:C01371", "m1": "IDFM:C01371",
    "métro 2": "IDFM:C01372", "metro 2": "IDFM:C01372", "m2": "IDFM:C01372",
    "métro 3": "IDFM:C01373", "metro 3": "IDFM:C01373", "m3": "IDFM:C01373",
    "métro 3b": "IDFM:C01386", "metro 3b": "IDFM:C01386", "m3b": "IDFM:C01386",
    "métro 4": "IDFM:C01374", "metro 4": "IDFM:C01374", "m4": "IDFM:C01374",
    "métro 5": "IDFM:C01375", "metro 5": "IDFM:C01375", "m5": "IDFM:C01375",
    "métro 6": "IDFM:C01376", "metro 6": "IDFM:C01376", "m6": "IDFM:C01376",
    "métro 7": "IDFM:C01377", "metro 7": "IDFM:C01377", "m7": "IDFM:C01377",
    "métro 7b": "IDFM:C01387", "metro 7b": "IDFM:C01387", "m7b": "IDFM:C01387",
    "métro 8": "IDFM:C01378", "metro 8": "IDFM:C01378", "m8": "IDFM:C01378",
    "métro 9": "IDFM:C01379", "metro 9": "IDFM:C01379", "m9": "IDFM:C01379",
    "métro 10": "IDFM:C01380", "metro 10": "IDFM:C01380", "m10": "IDFM:C01380",
    "métro 11": "IDFM:C01381", "metro 11": "IDFM:C01381", "m11": "IDFM:C01381",
    "métro 12": "IDFM:C01382", "metro 12": "IDFM:C01382", "m12": "IDFM:C01382",
    "métro 13": "IDFM:C01383", "metro 13": "IDFM:C01383", "m13": "IDFM:C01383",
    "métro 14": "IDFM:C01384", "metro 14": "IDFM:C01384", "m14": "IDFM:C01384",
    # RER
    "rer a": "IDFM:C01742", "a": "IDFM:C01742",
    "rer b": "IDFM:C01743", "b": "IDFM:C01743",
    "rer c": "IDFM:C01727", "c": "IDFM:C01727",
    "rer d": "IDFM:C01728", "d": "IDFM:C01728",
    "rer e": "IDFM:C01729", "e": "IDFM:C01729",
    # Tram
    "tram 1": "IDFM:C01389", "t1": "IDFM:C01389",
    "tram 2": "IDFM:C01390", "t2": "IDFM:C01390",
    "tram 3a": "IDFM:C01391", "t3a": "IDFM:C01391",
    "tram 3b": "IDFM:C01679", "t3b": "IDFM:C01679",
    "tram 4": "IDFM:C01843", "t4": "IDFM:C01843",
    "tram 5": "IDFM:C01684", "t5": "IDFM:C01684",
    "tram 6": "IDFM:C01794", "t6": "IDFM:C01794",
    "tram 7": "IDFM:C01774", "t7": "IDFM:C01774",
    "tram 8": "IDFM:C01795", "t8": "IDFM:C01795",
    "tram 9": "IDFM:C02317", "t9": "IDFM:C02317",
    "tram 11": "IDFM:C01999", "t11": "IDFM:C01999",
    "tram 13": "IDFM:C02528", "t13": "IDFM:C02528",
}


def resolve_line(name):
    """Résout un nom de ligne en identifiant IDFM."""
    key = name.lower().strip()
    if key in LINES:
        return LINES[key]
    # Essayer sans accents
    key_clean = key.replace("é", "e").replace("è", "e").replace("ê", "e")
    if key_clean in LINES:
        return LINES[key_clean]
    return None


def parse_siri_disruptions(xml_str):
    """Parse la réponse SIRI XML pour les perturbations."""
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError:
        return []

    # Namespace SIRI
    ns = {
        "siri": "http://www.siri.org.uk/siri",
    }

    disruptions = []
    # Chercher les PtSituationElement
    for elem in root.iter():
        if elem.tag.endswith("PtSituationElement"):
            disruption = {}

            for child in elem:
                tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

                if tag == "Summary":
                    disruption["summary"] = child.text or ""
                elif tag == "Description":
                    disruption["description"] = child.text or ""
                elif tag == "Severity":
                    disruption["severity"] = child.text or ""
                elif tag == "ReportType":
                    disruption["type"] = child.text or ""
                elif tag == "AffectedLines" or tag == "Affects":
                    for line_elem in child.iter():
                        line_tag = line_elem.tag.split("}")[-1] if "}" in line_elem.tag else line_elem.tag
                        if line_tag == "LineName" or line_tag == "PublishedLineName":
                            if line_elem.text:
                                disruption.setdefault("lines", []).append(line_elem.text)
                        elif line_tag == "LineRef":
                            if line_elem.text:
                                disruption.setdefault("line_refs", []).append(line_elem.text)

            if disruption:
                disruptions.append(disruption)

    return disruptions


def cmd_traffic(args):
    """État du trafic."""
    # API InfoTrafic IDFM (SIRI-SX)
    line_filter = None
    line_id = None

    if args.line:
        line_id = resolve_line(args.line)
        line_filter = args.line.lower()

    # Appel à l'API info trafic général
    data = api_call("/general-message", accept="application/json")

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # Parser la réponse selon le format
    if isinstance(data, dict) and "_xml" in data:
        disruptions = parse_siri_disruptions(data["_xml"])
        if line_filter:
            filtered = []
            for d in disruptions:
                lines = d.get("lines", []) + d.get("line_refs", [])
                for l in lines:
                    if line_filter in l.lower():
                        filtered.append(d)
                        break
                if line_id:
                    for lr in d.get("line_refs", []):
                        if line_id in lr:
                            if d not in filtered:
                                filtered.append(d)
                            break
            disruptions = filtered

        if not disruptions:
            if args.line:
                print(f"✅ Pas de perturbation signalée sur {args.line}.")
            else:
                print("✅ Trafic normal sur l'ensemble du réseau.")
            return

        print(f"🚇 État du trafic{' — ' + args.line if args.line else ''}")
        print("=" * 50)

        for d in disruptions[:20]:
            severity = d.get("severity", "")
            summary = d.get("summary", "")
            desc = d.get("description", "")
            lines = d.get("lines", [])

            severity_icon = "⚠️"
            if severity.lower() in ("normal", "noimpact"):
                severity_icon = "ℹ️"
            elif severity.lower() in ("veryslight", "slight"):
                severity_icon = "⚡"

            line_str = f" [{', '.join(lines[:3])}]" if lines else ""
            print(f"\n  {severity_icon}{line_str} {summary}")
            if desc and desc != summary:
                # Tronquer la description
                desc_clean = desc.replace("\n", " ").strip()
                if len(desc_clean) > 150:
                    desc_clean = desc_clean[:150] + "…"
                print(f"     {desc_clean}")

    elif isinstance(data, dict):
        # Réponse JSON — format SIRI Lite
        siri = data.get("Siri", {}).get("ServiceDelivery", {})
        gm = siri.get("GeneralMessageDelivery", [{}])
        if isinstance(gm, list):
            gm = gm[0] if gm else {}
        messages = gm.get("InfoMessage", [])

        if line_filter:
            filtered = []
            for msg in messages:
                content = msg.get("Content", {})
                line_sections = content.get("LineSection", [])
                if isinstance(line_sections, dict):
                    line_sections = [line_sections]
                for ls in line_sections:
                    line_ref = ls.get("LineRef", {}).get("value", "")
                    if line_id and line_id in line_ref:
                        filtered.append(msg)
                        break
                    line_name = ls.get("LineName", [])
                    if isinstance(line_name, list):
                        for ln in line_name:
                            if isinstance(ln, dict) and line_filter in ln.get("value", "").lower():
                                if msg not in filtered:
                                    filtered.append(msg)
                                break
            messages = filtered

        if not messages:
            if args.line:
                print(f"✅ Pas de perturbation signalée sur {args.line}.")
            else:
                print("✅ Trafic normal sur l'ensemble du réseau.")
            return

        print(f"🚇 État du trafic{' — ' + args.line if args.line else ''}")
        print("=" * 50)

        for msg in messages[:20]:
            content = msg.get("Content", {})
            messages_list = content.get("Message", [])
            if isinstance(messages_list, dict):
                messages_list = [messages_list]

            text = ""
            for m in messages_list:
                mt = m.get("MessageText", {})
                if isinstance(mt, dict):
                    text = mt.get("value", "")
                elif isinstance(mt, list) and mt:
                    text = mt[0].get("value", "")
                if text:
                    break

            line_sections = content.get("LineSection", [])
            if isinstance(line_sections, dict):
                line_sections = [line_sections]
            line_names = []
            for ls in line_sections:
                ln = ls.get("LineName", [])
                if isinstance(ln, list):
                    for l in ln:
                        if isinstance(l, dict):
                            line_names.append(l.get("value", ""))
                elif isinstance(ln, dict):
                    line_names.append(ln.get("value", ""))

            line_str = f" [{', '.join(line_names[:3])}]" if line_names else ""

            # Nettoyer le texte
            if text:
                import re
                text_clean = re.sub(r'<[^>]+>', '', text).strip()
                if len(text_clean) > 200:
                    text_clean = text_clean[:200] + "…"
                print(f"\n  ⚠️{line_str} {text_clean}")
    else:
        print("❌ Format de réponse inattendu.", file=sys.stderr)


def cmd_next(args):
    """Prochains passages à un arrêt."""
    # Rechercher l'arrêt via l'API
    stop_name = args.stop

    # Utiliser l'API de recherche de lieux IDFM
    params = {"q": stop_name, "type": "stop_area", "count": 1}

    # L'API PRIM utilise Navitia en backend pour certains endpoints
    key = get_api_key()
    search_url = f"{API_BASE}/navitia/places?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(search_url, headers={
        "apikey": key,
        "Accept": "application/json",
        "User-Agent": "french-services/1.0",
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            search_data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"❌ Arrêt introuvable : {stop_name}", file=sys.stderr)
        else:
            body = e.read().decode() if e.fp else ""
            print(f"❌ Erreur recherche ({e.code}): {body[:200]}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌ Erreur réseau : {e}", file=sys.stderr)
        sys.exit(1)

    places = search_data.get("places", [])
    if not places:
        print(f"❌ Arrêt introuvable : {stop_name}", file=sys.stderr)
        sys.exit(1)

    stop = places[0]
    stop_id = stop["id"]
    stop_label = stop.get("name", stop_name)

    # Récupérer les prochains passages
    dep_url = f"{API_BASE}/navitia/stop_areas/{stop_id}/departures"
    dep_params = {"count": args.count}
    dep_url += "?" + urllib.parse.urlencode(dep_params)

    req = urllib.request.Request(dep_url, headers={
        "apikey": key,
        "Accept": "application/json",
        "User-Agent": "french-services/1.0",
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            dep_data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"❌ Erreur ({e.code}): {body[:200]}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌ Erreur réseau : {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(dep_data, ensure_ascii=False, indent=2))
        return

    departures = dep_data.get("departures", [])
    if not departures:
        print(f"❌ Aucun passage trouvé pour {stop_label}.")
        return

    print(f"🚇 Prochains passages — {stop_label}")
    print("=" * 50)

    for dep in departures:
        dt_info = dep.get("stop_date_time", {})
        dep_time = dt_info.get("departure_date_time", "")
        base_time = dt_info.get("base_departure_date_time", "")

        display = dep.get("display_informations", {})
        mode = display.get("commercial_mode", "")
        code = display.get("code", "")
        direction = display.get("direction", "")
        headsign = display.get("headsign", "")
        color = display.get("color", "")

        # Formater l'heure
        try:
            dt = datetime.strptime(dep_time, "%Y%m%dT%H%M%S")
            time_str = dt.strftime("%H:%M")
            # Calculer le temps restant
            now = datetime.now()
            diff = (dt - now).total_seconds()
            if 0 < diff < 3600:
                mins = int(diff / 60)
                time_str += f" ({mins} min)"
        except (ValueError, TypeError):
            time_str = dep_time

        # Retard ?
        delay = ""
        if base_time and dep_time and base_time != dep_time:
            try:
                base_dt = datetime.strptime(base_time, "%Y%m%dT%H%M%S")
                delay = f" ⚠️ (prévu {base_dt.strftime('%H:%M')})"
            except ValueError:
                pass

        label = f"{mode} {code}".strip()
        dest = direction.split(" (")[0] if direction else headsign

        print(f"  {time_str}{delay}  {label:15s} → {dest}")


def main():
    parser = argparse.ArgumentParser(
        description="RATP/IDFM — Transports en commun Île-de-France",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", help="Commande")

    # traffic
    p_traffic = sub.add_parser("traffic", help="État du trafic")
    p_traffic.add_argument("--line", help="Filtrer par ligne (ex: 'Métro 13', 'RER A')")
    p_traffic.add_argument("--json", action="store_true", help="Sortie JSON")

    # next
    p_next = sub.add_parser("next", help="Prochains passages à un arrêt")
    p_next.add_argument("stop", help="Nom de l'arrêt")
    p_next.add_argument("--count", type=int, default=10, help="Nombre de résultats")
    p_next.add_argument("--json", action="store_true", help="Sortie JSON")

    args = parser.parse_args()

    if args.command == "traffic":
        cmd_traffic(args)
    elif args.command == "next":
        cmd_next(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
