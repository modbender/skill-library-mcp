# tcl_tool.py
import os
import sqlite3
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tcl.db") 

def _get_active_services(conn, date_str: str, weekday: str) -> set:
    """Retourne les service_id actifs pour une date donnée."""
    rows = conn.execute(f"""
        SELECT service_id FROM calendar
        WHERE {weekday} = '1'
          AND start_date <= ?
          AND end_date >= ?
    """, (date_str, date_str)).fetchall()
    active = {r[0] for r in rows}

    exceptions = conn.execute("""
        SELECT service_id, exception_type FROM calendar_dates WHERE date = ?
    """, (date_str,)).fetchall()
    for service_id, exc_type in exceptions:
        if exc_type == '1':
            active.add(service_id)
        elif exc_type == '2':
            active.discard(service_id)
    return active


def _normalize_time(t: str) -> str:
    """Convertit 24:41:00 en 00:41 (après minuit) pour l'affichage."""
    h, m, s = t.split(":")
    h_int = int(h)
    h_display = h_int % 24
    suffix = " (après minuit)" if h_int >= 24 else ""
    return f"{h_display:02d}:{m}{suffix}"


def get_next_departures(stop_name: str, limit: int = 5, line: str = None) -> str:
    """Prochains départs depuis un arrêt TCL. Filtre optionnel par ligne."""
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    date_str = now.strftime("%Y%m%d")
    weekday = now.strftime("%A").lower()

    also_check_prev = now.hour < 3
    prev_date_str = (now - timedelta(days=1)).strftime("%Y%m%d")
    prev_weekday = (now - timedelta(days=1)).strftime("%A").lower()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    stops = conn.execute(
        "SELECT stop_id, stop_name FROM stops WHERE stop_name LIKE ? LIMIT 10",
        (f"%{stop_name}%",)
    ).fetchall()

    if not stops:
        conn.close()
        return f"Aucun arrêt trouvé pour '{stop_name}'."

    active = _get_active_services(conn, date_str, weekday)
    if also_check_prev:
        active_prev = _get_active_services(conn, prev_date_str, prev_weekday)

    line_filter = "AND r.route_short_name = ?" if line else ""

    results = []
    for stop in stops:
        sid = stop["stop_id"]
        sname = stop["stop_name"]

        if also_check_prev:
            prev_offset = f"{now.hour + 24:02d}:{now.strftime('%M:%S')}"
            params = [sid, prev_offset] + ([line.upper()] if line else []) + list(active_prev) + [limit]
            rows = conn.execute("""
                SELECT st.departure_time, r.route_short_name,
                       r.route_long_name, t.trip_headsign
                FROM stop_times st
                JOIN trips t ON st.trip_id = t.trip_id
                JOIN routes r ON t.route_id = r.route_id
                WHERE st.stop_id = ?
                  AND st.departure_time >= ?
                  {}
                  AND t.service_id IN ({})
                ORDER BY st.departure_time
                LIMIT ?
            """.format(line_filter, ",".join("?" * len(active_prev))), params).fetchall()
        else:
            params = [sid, current_time] + ([line.upper()] if line else []) + list(active) + [limit]
            rows = conn.execute("""
                SELECT st.departure_time, r.route_short_name,
                       r.route_long_name, t.trip_headsign
                FROM stop_times st
                JOIN trips t ON st.trip_id = t.trip_id
                JOIN routes r ON t.route_id = r.route_id
                WHERE st.stop_id = ?
                  AND st.departure_time >= ?
                  {}
                  AND t.service_id IN ({})
                ORDER BY st.departure_time
                LIMIT ?
            """.format(line_filter, ",".join("?" * len(active))), params).fetchall()

        if rows:
            results.append(f"\n{sname} (id:{sid})")
            for r in rows:
                results.append(
                    f"  {_normalize_time(r['departure_time'])} — "
                    f"Ligne {r['route_short_name']} "
                    f"→ {r['trip_headsign']}"
                )

    conn.close()

    if not results:
        return f"Aucun départ trouvé prochainement à '{stop_name}'" + (f" (ligne {line})" if line else "") + "."
    return "\n".join(results)


def get_last_departures(stop_name: str, direction: str = None, line: str = None) -> str:
    """Derniers départs de la soirée depuis un arrêt TCL (jusqu'à ~03h00)."""
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    weekday = now.strftime("%A").lower()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    stops = conn.execute(
        "SELECT stop_id, stop_name FROM stops WHERE stop_name LIKE ? LIMIT 10",
        (f"%{stop_name}%",)
    ).fetchall()

    if not stops:
        conn.close()
        return f"Aucun arrêt trouvé pour '{stop_name}'."

    active = _get_active_services(conn, date_str, weekday)
    if not active:
        conn.close()
        return "Aucun service actif trouvé pour aujourd'hui."

    direction_filter = "AND t.trip_headsign LIKE ?" if direction else ""
    line_filter = "AND r.route_short_name = ?" if line else ""

    results = []
    for stop in stops:
        sid = stop["stop_id"]
        sname = stop["stop_name"]

        params = [sid] + ([f"%{direction}%"] if direction else []) + ([line.upper()] if line else []) + list(active)
        rows = conn.execute("""
            SELECT st.departure_time, r.route_short_name,
                   r.route_long_name, t.trip_headsign
            FROM stop_times st
            JOIN trips t ON st.trip_id = t.trip_id
            JOIN routes r ON t.route_id = r.route_id
            WHERE st.stop_id = ?
              AND st.departure_time <= '27:00:00'
              {}
              {}
              AND t.service_id IN ({})
            ORDER BY st.departure_time DESC
            LIMIT 5
        """.format(direction_filter, line_filter, ",".join("?" * len(active))),
        params).fetchall()

        if rows:
            results.append(f"\n{sname} (id:{sid})")
            for r in rows:
                h, m, _ = r['departure_time'].split(":")
                time_display = f"{int(h):02d}:{m}"
                results.append(
                    f"  {time_display} — "
                    f"Ligne {r['route_short_name']} "
                    f"→ {r['trip_headsign']}"
                )

    conn.close()

    if not results:
        msg = f"Aucun dernier départ trouvé à '{stop_name}'"
        if direction: msg += f" vers '{direction}'"
        if line: msg += f" (ligne {line})"
        return msg + "."
    return "\n".join(results)


def get_first_departures(stop_name: str, direction: str = None, line: str = None) -> str:
    """Premiers départs de la journée depuis un arrêt TCL (depuis 00:00)."""
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    weekday = now.strftime("%A").lower()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    stops = conn.execute(
        "SELECT stop_id, stop_name FROM stops WHERE stop_name LIKE ? LIMIT 10",
        (f"%{stop_name}%",)
    ).fetchall()

    if not stops:
        conn.close()
        return f"Aucun arrêt trouvé pour '{stop_name}'."

    active = _get_active_services(conn, date_str, weekday)
    if not active:
        conn.close()
        return "Aucun service actif trouvé pour aujourd'hui."

    direction_filter = "AND t.trip_headsign LIKE ?" if direction else ""
    line_filter = "AND r.route_short_name = ?" if line else ""

    results = []
    for stop in stops:
        sid = stop["stop_id"]
        sname = stop["stop_name"]

        params = [sid] + ([f"%{direction}%"] if direction else []) + ([line.upper()] if line else []) + list(active)
        rows = conn.execute("""
            SELECT st.departure_time, r.route_short_name,
                   r.route_long_name, t.trip_headsign
            FROM stop_times st
            JOIN trips t ON st.trip_id = t.trip_id
            JOIN routes r ON t.route_id = r.route_id
            WHERE st.stop_id = ?
              AND st.departure_time >= '04:30:00'
              AND st.departure_time < '24:00:00'
              {}
              {}
              AND t.service_id IN ({})
            ORDER BY st.departure_time ASC
            LIMIT 5
        """.format(direction_filter, line_filter, ",".join("?" * len(active))),
        params).fetchall()

        if rows:
            results.append(f"\n{sname} (id:{sid})")
            for r in rows:
                results.append(
                    f"  {_normalize_time(r['departure_time'])} — "
                    f"Ligne {r['route_short_name']} "
                    f"→ {r['trip_headsign']}"
                )

    conn.close()

    if not results:
        msg = f"Aucun premier départ trouvé à '{stop_name}'"
        if direction: msg += f" vers '{direction}'"
        if line: msg += f" (ligne {line})"
        return msg + "."
    return "\n".join(results)


def search_stops(query: str) -> str:
    """Liste les arrêts correspondant à une recherche."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT stop_id, stop_name FROM stops WHERE stop_name LIKE ? LIMIT 10",
        (f"%{query}%",)
    ).fetchall()
    conn.close()
    if not rows:
        return f"Aucun arrêt trouvé pour '{query}'."
    return "\n".join(f"{r[0]} — {r[1]}" for r in rows)


def get_line_info(line_name: str) -> str:
    """Infos sur une ligne TCL."""
    type_map = {
        "0": "Tram", "1": "Métro", "2": "Train",
        "3": "Bus", "7": "Funiculaire", "11": "Trolleybus"
    }
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT route_short_name, route_long_name, route_type FROM routes WHERE route_short_name = ?",
        (line_name.upper(),)
    ).fetchall()
    if not rows:
        rows = conn.execute(
            "SELECT route_short_name, route_long_name, route_type FROM routes WHERE route_short_name LIKE ? LIMIT 5",
            (f"{line_name.upper()}%",)
        ).fetchall()
    conn.close()
    if not rows:
        return f"Ligne '{line_name}' introuvable."
    return "\n".join(
        f"Ligne {r[0]} ({type_map.get(r[2], r[2])}) — {r[1]}"
        for r in rows
    )


if __name__ == "__main__":
    import sys

    def _parse_args(argv):
        """Parse argv, extrait --line si présent."""
        line = None
        args = []
        i = 0
        while i < len(argv):
            if argv[i] == "--line" and i + 1 < len(argv):
                line = argv[i + 1]
                i += 2
            else:
                args.append(argv[i])
                i += 1
        return args, line

    if len(sys.argv) >= 3:
        remaining, line = _parse_args(sys.argv[1:])
        cmd = remaining[0]
        arg = remaining[1] if len(remaining) > 1 else ""

        if cmd == "departures":
            limit = int(remaining[2]) if len(remaining) >= 3 else 5
            print(get_next_departures(arg, limit=limit, line=line))
        elif cmd == "first":
            direction = remaining[2] if len(remaining) >= 3 else None
            print(get_first_departures(arg, direction=direction, line=line))
        elif cmd == "last":
            direction = remaining[2] if len(remaining) >= 3 else None
            print(get_last_departures(arg, direction=direction, line=line))
        elif cmd == "line":
            print(get_line_info(arg))
        elif cmd == "stops":
            print(search_stops(arg))
        else:
            print(f"Commande inconnue: {cmd}")
    else:
        print(get_next_departures("Bellecour"))
        print("---")
        print(get_line_info("D"))
        print("---")
        print(search_stops("Part-Dieu"))
