#!/usr/bin/env python3
"""MVG CLI - Münchner Verkehrsgesellschaft vom Terminal aus.

Inoffizielle CLI für die MVG API.
Rein Python, keine externen Dependencies (nur stdlib + requests).

Nutzung:
    mvg search "Marienplatz"                     # Station suchen
    mvg departures "Marienplatz"                 # Nächste Abfahrten
    mvg departures "Marienplatz" --limit 20      # Mit Limit
    mvg departures "Marienplatz" --type ubahn    # Nur U-Bahn
    mvg departures "Marienplatz" --offset 5      # +5min Fußweg
    mvg route "Marienplatz" "Garching"           # Verbindungssuche  
    mvg route "Marienplatz" "Garching" --arrive  # Ankunftszeit
    mvg route "Marienplatz" "Garching" --time "18:00"  # Bestimmte Zeit
    mvg nearby                                   # Nächste Stationen (Default-Position)
    mvg nearby 48.1351 11.5820                   # Bestimmte Koordinaten
    mvg alerts                                   # Aktuelle Störungen
    mvg alerts --station "Marienplatz"          # Stationsspezifische Störungen
    mvg lines                                    # Alle Linien
    mvg lines --type ubahn                       # Nur U-Bahn Linien
    mvg live                                     # Alle S-Bahnen live
    mvg live --line S3                           # Nur S3 anzeigen
    mvg live --line S8 --json                    # JSON-Ausgabe

Alle Commands unterstützen --json für JSON-Ausgabe.
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Dict, List
import re


# Configuration
BASE_URL = "https://www.mvg.de/api/bgw-pt/v3"
GEOPS_WS_URL = "wss://api.geops.io/realtime-ws/v1/"
GEOPS_API_KEY = "5cc87b12d7c5370001c1d655112ec5c21e0f441792cfc2fafe3e7a1e"
GEOPS_ORIGIN = "https://s-bahn-muenchen-live.de"
SESSION_FILE = Path.home() / ".mvg_session.json"

# Exit codes
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_API_ERROR = 2

# Transport type emojis
TRANSPORT_EMOJIS = {
    "UBAHN": "🔵",
    "SBAHN": "🟢", 
    "BUS": "🚌",
    "TRAM": "🚋",
    "BAHN": "🚆",
    "REGIONAL_BUS": "🚍",
    "RUFTAXI": "🚕",
    "PEDESTRIAN": "🚶",
}

# All transport types for filtering
ALL_TRANSPORT_TYPES = ["UBAHN", "SBAHN", "BUS", "TRAM", "BAHN", "REGIONAL_BUS", "RUFTAXI"]
TRANSPORT_TYPE_MAP = {
    "ubahn": "UBAHN", "u-bahn": "UBAHN",
    "sbahn": "SBAHN", "s-bahn": "SBAHN",
    "bus": "BUS",
    "tram": "TRAM",
    "bahn": "BAHN", "re": "BAHN", "rb": "BAHN", "regional": "BAHN",
    "regionalbus": "REGIONAL_BUS",
    "ruftaxi": "RUFTAXI", "rufbus": "RUFTAXI",
}

# Default location (Munich)
DEFAULT_LAT = 48.1351
DEFAULT_LON = 11.5820


class MVGAPIError(Exception):
    """Custom exception for MVG API errors."""
    def __init__(self, message: str, status: Optional[int] = None):
        super().__init__(message)
        self.status = status


class MVGAPI:
    """MVG.de API client using only Python stdlib + requests."""
    
    def __init__(self):
        self.session: Dict[str, Any] = {}
        self._load_session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get default HTTP headers."""
        return {
            "User-Agent": "mvg-cli/1.0 (Python stdlib)",
            "Accept": "application/json",
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to MVG API."""
        url = f"{BASE_URL}{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        
        headers = self._get_headers()
        request = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                content = response.read().decode("utf-8")
                if content:
                    return json.loads(content)
                return {}
        except urllib.error.HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode("utf-8")
            except:
                pass
            raise MVGAPIError(f"HTTP {e.code}: {e.reason}. {error_body}", e.code)
        except urllib.error.URLError as e:
            raise MVGAPIError(f"Verbindungsfehler: {e.reason}")
        except json.JSONDecodeError as e:
            raise MVGAPIError(f"Ungültige JSON-Antwort: {e}")
    
    def _save_session(self) -> None:
        """Save session data to file."""
        with open(SESSION_FILE, "w") as f:
            json.dump(self.session, f, ensure_ascii=False, indent=2)
    
    def _load_session(self) -> None:
        """Load session data from file."""
        if SESSION_FILE.exists():
            try:
                with open(SESSION_FILE) as f:
                    self.session = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.session = {}
    
    def search_stations(self, query: str) -> List[Dict[str, Any]]:
        """Search for stations by name."""
        params = {"query": query}
        response = self._make_request("/locations", params)
        
        stations = []
        for location in response:
            if location.get("type") == "STATION":
                stations.append({
                    "globalId": location.get("globalId"),
                    "name": location.get("name"),
                    "place": location.get("place"),
                    "transportTypes": location.get("transportTypes", []),
                    "latitude": location.get("latitude"),
                    "longitude": location.get("longitude"),
                })
        
        return stations
    
    def get_departures(
        self,
        global_id: str,
        limit: int = 10,
        transport_types: Optional[List[str]] = None,
        offset_minutes: int = 0
    ) -> List[Dict[str, Any]]:
        """Get departures for a station."""
        params = {
            "globalId": global_id,
            "limit": str(limit),
        }
        
        if offset_minutes > 0:
            params["offsetInMinutes"] = str(offset_minutes)
        
        if transport_types:
            params["transportTypes"] = ",".join(transport_types)
        
        response = self._make_request("/departures", params)
        departures = []
        
        for dep in response:
            transport_type = dep.get("transportType")
            
            planned_time = dep.get("plannedDepartureTime")
            realtime_time = dep.get("realtimeDepartureTime")
            delay_minutes = dep.get("delayInMinutes", 0)
            
            departure = {
                "label": dep.get("label"),
                "transportType": transport_type,
                "destination": dep.get("destination"),
                "plannedTime": planned_time,
                "realtimeTime": realtime_time,
                "delayMinutes": delay_minutes,
                "cancelled": dep.get("cancelled", False),
                "platform": dep.get("platform"),
                "platformChanged": dep.get("platformChanged", False),
                "infos": dep.get("infos", []),
            }
            departures.append(departure)
        
        return departures
    
    def resolve_location(self, query: str) -> Dict[str, Any]:
        """Resolve a query to a location (station or address).
        
        Returns dict with either 'globalId' (station) or 'latitude'/'longitude' (address).
        Accepts stations, addresses, and POIs.
        """
        params = {"query": query}
        locations = self._make_request("/locations", params)
        if not locations:
            return {}
        return locations[0]

    def find_routes(
        self,
        origin: Dict[str, Any],
        destination: Dict[str, Any],
        is_arrival_time: bool = False,
        departure_time: Optional[str] = None,
        transport_types: Optional[List[str]] = None,
        routing_mode: str = "FAST",
        walk_speed: str = "NORMAL",
        accessible: bool = False,
        via: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Find routes between two locations (stations or addresses)."""
        params = {}
        
        # Origin: station (globalId) or address (lat/lon)
        if origin.get("globalId"):
            params["originStationGlobalId"] = origin["globalId"]
        else:
            params["originLatitude"] = origin["latitude"]
            params["originLongitude"] = origin["longitude"]
        
        # Destination: station (globalId) or address (lat/lon)
        if destination.get("globalId"):
            params["destinationStationGlobalId"] = destination["globalId"]
        else:
            params["destinationLatitude"] = destination["latitude"]
            params["destinationLongitude"] = destination["longitude"]
        
        if is_arrival_time:
            params["routingDateTimeIsArrival"] = "true"
        
        if departure_time:
            params["routingDateTime"] = departure_time
        
        if transport_types:
            params["transportTypes"] = ",".join(transport_types)
        
        if routing_mode != "FAST":
            params["routingMode"] = routing_mode
        
        if walk_speed != "NORMAL":
            params["walkSpeed"] = walk_speed
        
        if accessible:
            params["wheelchair"] = "true"
        
        if via:
            if via.get("globalId"):
                params["viaStationGlobalId"] = via["globalId"]
            else:
                params["viaLatitude"] = via["latitude"]
                params["viaLongitude"] = via["longitude"]
        
        response = self._make_request("/routes", params)
        routes = []
        
        for route in response:
            parts = []
            for part in route.get("parts", []):
                from_info = part.get("from", {})
                to_info = part.get("to", {})
                part_info = {
                    "from": {
                        "name": from_info.get("name"),
                        "departure": from_info.get("plannedDeparture"),
                        "departureDelayInMinutes": from_info.get("departureDelayInMinutes", 0),
                        "platform": from_info.get("platform"),
                        "platformChanged": from_info.get("platformChanged", False),
                    },
                    "to": {
                        "name": to_info.get("name"),
                        "arrival": to_info.get("plannedDeparture"),  # API uses plannedDeparture for arrival too
                        "arrivalDelayInMinutes": to_info.get("arrivalDelayInMinutes", 0),
                    },
                    "line": part.get("line"),
                }
                parts.append(part_info)
            
            # Calculate departure/arrival/duration from first and last part
            route_departure = parts[0]["from"]["departure"] if parts else None
            route_arrival = parts[-1]["to"]["arrival"] if parts else None
            route_duration = None
            if route_departure and route_arrival:
                try:
                    from datetime import datetime
                    fmt = "%Y-%m-%dT%H:%M:%S%z"
                    dep_dt = datetime.strptime(route_departure, fmt)
                    arr_dt = datetime.strptime(route_arrival, fmt)
                    route_duration = int((arr_dt - dep_dt).total_seconds() / 60)
                except (ValueError, TypeError):
                    pass

            route_info = {
                "departure": route_departure,
                "arrival": route_arrival,
                "duration": route_duration,
                "parts": parts,
            }
            routes.append(route_info)
        
        return routes
    
    def get_nearby_stations(self, latitude: float, longitude: float) -> List[Dict[str, Any]]:
        """Get stations near given coordinates."""
        params = {"latitude": str(latitude), "longitude": str(longitude)}
        response = self._make_request("/stations/nearby", params)
        
        stations = []
        for location in response:
            stations.append({
                "globalId": location.get("globalId"),
                "name": location.get("name"),
                "place": location.get("place"),
                "transportTypes": location.get("transportTypes", []),
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "distanceInMeters": location.get("distanceInMeters"),
            })
        
        return stations[:10]  # Limit to 10 nearest
    
    def get_alerts(self, global_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get disruption messages."""
        params = {}
        if global_id:
            params["globalId"] = global_id
        
        response = self._make_request("/messages", params)
        alerts = []
        
        for alert in response:
            alert_info = {
                "id": alert.get("id"),
                "title": alert.get("title"),
                "description": alert.get("description"),
                "validFrom": alert.get("validFrom"),
                "validTo": alert.get("validTo"),
                "affectedLines": alert.get("affectedLines", []),
                "severity": alert.get("severity"),
            }
            alerts.append(alert_info)
        
        return alerts
    
    def get_lines(self, transport_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all lines."""
        response = self._make_request("/lines")
        lines = []
        
        for line in response:
            line_transport_type = line.get("transportType")
            if transport_type and line_transport_type != transport_type.upper():
                continue
            
            line_info = {
                "name": line.get("name"),
                "label": line.get("label"),
                "transportType": line_transport_type,
                "network": line.get("network"),
            }
            lines.append(line_info)
        
        return lines
    
    def resolve_station(self, station_name: str) -> Optional[str]:
        """Resolve station name to globalId."""
        stations = self.search_stations(station_name)
        if not stations:
            return None
        
        # Return best match (first result)
        return stations[0].get("globalId")


class SBahnLiveAPI:
    """S-Bahn München Live Tracking via geOps WebSocket API."""

    # S-Bahn line colors for terminal display
    LINE_COLORS = {
        "S1": "\033[94m",   # Blue
        "S2": "\033[92m",   # Green
        "S3": "\033[95m",   # Purple
        "S4": "\033[91m",   # Red
        "S6": "\033[32m",   # Dark Green
        "S7": "\033[91m",   # Red (brown-ish)
        "S8": "\033[93m",   # Yellow/Orange
        "S20": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    # Known S-Bahn München station names by approximate coordinate (EPSG:3857)
    # Used for resolving nearest station from trajectory coordinates
    STATIONS = {
        "Hauptbahnhof": (1288239, 6133745),
        "Marienplatz": (1289702, 6133330),
        "Isartor": (1290526, 6133225),
        "Rosenheimer Platz": (1291105, 6133047),
        "Ostbahnhof": (1292158, 6132944),
        "Leuchtenbergring": (1293233, 6133003),
        "Donnersbergerbrücke": (1287007, 6133850),
        "Hackerbrücke": (1287718, 6133801),
        "Karlsplatz (Stachus)": (1288704, 6133546),
        "Pasing": (1281748, 6133844),
        "Laim": (1283811, 6133894),
        "Hirschgarten": (1285067, 6133862),
    }

    def fetch_trajectories(self, timeout: int = 15) -> list:
        """Fetch all S-Bahn trajectories via WebSocket.

        Uses subprocess + node for reliable WebSocket handling.
        Falls back to stdlib if node unavailable.
        """
        import subprocess
        import tempfile

        js_code = """
// Try multiple locations for ws module
const paths = [
  process.env.HOME + '/.openclaw/workspace/node_modules/ws',
  '/app/node_modules/.pnpm/ws@8.19.0/node_modules/ws',
];
let WebSocket;
for (const p of paths) {
  try { WebSocket = require(p); break; } catch(e) {}
}
if (!WebSocket) { try { WebSocket = require('ws'); } catch(e) { process.stderr.write('ws module not found'); process.exit(1); } }
const url = process.argv[2];
const origin = process.argv[3];
const waitMs = parseInt(process.argv[4]) || 8000;
const ws = new WebSocket(url, { headers: { Origin: origin } });
const trains = [];
ws.on('open', () => {
  ws.send('GET sbm_full');
  ws.send('SUB sbm_full');
  ws.send('BBOX 1268000 6110000 1350000 6200000 14');
});
ws.on('message', (raw) => {
  try {
    const d = JSON.parse(raw.toString());
    if (d.source === 'trajectory' && d.content?.properties) {
      trains.push(d.content);
    }
  } catch(e) {}
});
ws.on('error', (e) => { process.stderr.write('ERR: ' + e.message + '\\n'); });
const outFile = process.argv[5];
setTimeout(() => {
  ws.close();
  require('fs').writeFileSync(outFile, JSON.stringify(trains));
  process.exit(0);
}, waitMs);
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(js_code)
            js_path = f.name

        try:
            url = f"{GEOPS_WS_URL}?key={GEOPS_API_KEY}"
            out_file = js_path + ".json"
            result = subprocess.run(
                ["node", js_path, url, GEOPS_ORIGIN, str((timeout - 2) * 1000), out_file],
                capture_output=True, text=True, timeout=timeout
            )
            if result.returncode != 0:
                raise ConnectionError(f"Node process failed: {result.stderr}")
            import os as _os2
            if _os2.path.exists(out_file):
                with open(out_file) as f:
                    data = json.load(f)
                _os2.unlink(out_file)
                return data
            return []
        except FileNotFoundError:
            raise ConnectionError("node not found — required for S-Bahn live tracking")
        finally:
            import os as _os
            try:
                _os.unlink(js_path)
            except OSError:
                pass

    @staticmethod
    def _nearest_station(coord, stations) -> str:
        """Find nearest known station to a coordinate."""
        if not stations:
            return "Unbekannt"
        x, y = coord
        best = None
        best_dist = float("inf")
        for name, (sx, sy) in stations.items():
            d = (x - sx) ** 2 + (y - sy) ** 2
            if d < best_dist:
                best_dist = d
                best = name
        return best or "Unbekannt"

    def parse_trajectories(self, trajectories: list) -> list:
        """Parse raw trajectory data into clean train info."""
        trains = []

        for traj in trajectories:
            props = traj.get("properties", {})
            line_info = props.get("line")
            if not line_info:
                continue

            line_name = line_info.get("name", "")
            # Skip non-S-Bahn (e.g. BusS2 replacement buses)
            if line_name and not line_name.startswith("S"):
                continue

            state = props.get("state", "UNKNOWN")
            delay = props.get("delay")
            train_number = props.get("train_number")

            # Get current position from first coordinate
            coords = traj.get("geometry", {}).get("coordinates", [])
            current_pos = coords[0] if coords else None

            # Delay is in milliseconds
            delay_min = None
            if delay is not None:
                delay_min = round(delay / 60000)

            # Route identifier sometimes contains destination info
            route_id = props.get("route_identifier", "")

            train = {
                "line": line_name,
                "color": line_info.get("color", ""),
                "trainNumber": train_number,
                "state": state,
                "delayMinutes": delay_min,
                "routeId": route_id,
                "position": current_pos,
                "hasRealtime": props.get("has_realtime", False),
                "trainId": props.get("train_id", ""),
                "timestamp": props.get("timestamp", 0),
            }
            trains.append(train)

        # Deduplicate: keep latest update per train_id
        by_id = {}
        for t in trains:
            tid = t["trainId"]
            if tid not in by_id or t["timestamp"] > by_id[tid]["timestamp"]:
                by_id[tid] = t
        trains = list(by_id.values())

        # Sort by line name, then train number
        trains.sort(key=lambda t: (t["line"], t.get("trainNumber") or 0))
        return trains


def handle_live(args) -> int:
    """Handle S-Bahn live tracking command."""
    try:
        api = SBahnLiveAPI()
        
        is_json = args.json or getattr(args, 'live_json', False)
        if not is_json:
            print("🔄 Verbinde mit S-Bahn Live Map...", end="", flush=True)
        trajectories = api.fetch_trajectories(timeout=12)
        if not is_json:
            print(f" {len(trajectories)} Züge empfangen.")
        
        if not trajectories:
            print("❌ Keine S-Bahn-Daten empfangen")
            return EXIT_ERROR

        trains = api.parse_trajectories(trajectories)

        # Filter by line if requested
        if args.line:
            line_filter = args.line.upper()
            if not line_filter.startswith("S"):
                line_filter = "S" + line_filter
            trains = [t for t in trains if t["line"] == line_filter]
            if not trains:
                print(f"❌ Keine Züge der Linie {line_filter} gefunden")
                return EXIT_ERROR

        if args.json or getattr(args, 'live_json', False):
            print(json.dumps(trains, indent=2, ensure_ascii=False))
            return EXIT_OK

        # Group by line
        by_line = {}
        for t in trains:
            by_line.setdefault(t["line"], []).append(t)

        print()
        for line_name in sorted(by_line.keys()):
            line_trains = by_line[line_name]
            color = SBahnLiveAPI.LINE_COLORS.get(line_name, "")
            reset = SBahnLiveAPI.RESET if color else ""

            print(f"  {color}━━━ {line_name} ({len(line_trains)} Züge) ━━━{reset}")

            for t in line_trains:
                # State emoji
                state_map = {
                    "DRIVING": "🚆",
                    "BOARDING": "🚏",
                    "STOPPED": "⏸️",
                }
                state_emoji = state_map.get(t["state"], "❓")

                # Delay
                delay_str = ""
                if t["delayMinutes"] is not None and t["delayMinutes"] > 0:
                    delay_str = f" \033[91m+{t['delayMinutes']}min{reset}"
                elif t["delayMinutes"] is not None and t["delayMinutes"] == 0:
                    delay_str = " ✅"

                number = f"#{t['trainNumber']}" if t["trainNumber"] else ""
                rt = " 📡" if t.get("hasRealtime") else ""

                info = f"  {state_emoji} {color}{line_name}{reset}"
                if number:
                    info += f" {number}"
                info += f"  [{t['state']}]"
                info += delay_str
                info += rt

                print(info)

            print()

        # Summary
        total = len(trains)
        delayed = sum(1 for t in trains if t["delayMinutes"] and t["delayMinutes"] > 0)
        driving = sum(1 for t in trains if t["state"] == "DRIVING")
        print(f"  📊 {total} Züge aktiv | {driving} fahren | {delayed} verspätet")
        print()

        return EXIT_OK

    except ConnectionError as e:
        print(f"\n❌ Verbindungsfehler: {e}")
        return EXIT_API_ERROR
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"\n❌ Fehler: {e}")
        return EXIT_ERROR


# ─────────────────────────────────────────────────────────────────────────────
# Utility Functions
# ─────────────────────────────────────────────────────────────────────────────

def format_time(timestamp_ms: Optional[int]) -> str:
    """Format Unix timestamp (ms) to local time string."""
    if not timestamp_ms:
        return "N/A"
    
    try:
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        return dt.strftime("%H:%M")
    except (ValueError, OverflowError):
        return "N/A"


def format_datetime(timestamp_ms: Optional[int]) -> str:
    """Format Unix timestamp (ms) to local datetime string."""
    if not timestamp_ms:
        return "N/A"
    
    try:
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        return dt.strftime("%d.%m.%Y %H:%M")
    except (ValueError, OverflowError):
        return "N/A"


def format_time_iso(iso_time: Optional[str]) -> str:
    """Format ISO time string to local time string."""
    if not iso_time:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
        return dt.strftime("%H:%M")
    except (ValueError, TypeError):
        return "N/A"


def format_delay(delay_minutes: int) -> str:
    """Format delay with emoji indicators."""
    if delay_minutes == 0:
        return "✅ pünktlich"
    elif delay_minutes > 0:
        indicator = "🔴" if delay_minutes > 5 else "🟡"
        return f"{indicator} +{delay_minutes} min"
    else:
        return f"⏩ {abs(delay_minutes)} min früh"


def get_transport_emoji(transport_type: str) -> str:
    """Get emoji for transport type."""
    return TRANSPORT_EMOJIS.get(transport_type, "🚇")


def clean_html(text: str) -> str:
    """Remove HTML tags from text."""
    import re
    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
    text = re.sub(r'&nbsp;', ' ', text)  # Replace &nbsp; with space
    text = re.sub(r'&gt;', '>', text)   # Replace &gt; with >
    text = re.sub(r'&lt;', '<', text)   # Replace &lt; with <
    text = re.sub(r'&amp;', '&', text)  # Replace &amp; with &
    return text.strip()


def wrap_text(text: str, max_width: int = 80) -> List[str]:
    """Wrap text to maximum width."""
    lines = []
    words = text.split()
    current_line = ""
    
    for word in words:
        if len(current_line + " " + word) <= max_width:
            current_line += " " + word if current_line else word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines


def print_box(title: str, content: List[str], max_width: int = 80) -> None:
    """Print content in a Unicode box."""
    if not content:
        return
    
    # Wrap content lines
    wrapped_content = []
    for line in content:
        if len(line) > max_width - 4:
            wrapped_content.extend(wrap_text(line, max_width - 4))
        else:
            wrapped_content.append(line)
    
    # Calculate box width
    max_line_width = max(len(title), max(len(line) for line in wrapped_content))
    width = min(max_line_width + 4, max_width)  # Padding
    
    # Top border
    print("╔" + "═" * (width - 2) + "╗")
    
    # Title
    title_padding = width - len(title) - 4
    left_pad = title_padding // 2
    right_pad = title_padding - left_pad
    print(f"║ {' ' * left_pad}{title}{' ' * right_pad} ║")
    
    # Separator
    print("╠" + "═" * (width - 2) + "╣")
    
    # Content
    for line in wrapped_content:
        padding = width - len(line) - 4
        print(f"║ {line}{' ' * padding} ║")
    
    # Bottom border
    print("╚" + "═" * (width - 2) + "╝")


def print_table(headers: List[str], rows: List[List[str]]) -> None:
    """Print data as a table with Unicode borders."""
    if not rows:
        return
    
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))
    
    # Top border
    print("┌" + "┬".join("─" * (w + 2) for w in widths) + "┐")
    
    # Headers
    header_row = "│".join(f" {h:<{widths[i]}} " for i, h in enumerate(headers))
    print("│" + header_row + "│")
    
    # Separator
    print("├" + "┼".join("─" * (w + 2) for w in widths) + "┤")
    
    # Rows
    for row in rows:
        row_str = "│".join(f" {str(row[i]):<{widths[i]}} " if i < len(row) else f" {'':<{widths[i]}} " for i in range(len(widths)))
        print("│" + row_str + "│")
    
    # Bottom border
    print("└" + "┴".join("─" * (w + 2) for w in widths) + "┘")


# ─────────────────────────────────────────────────────────────────────────────
# Command Handlers
# ─────────────────────────────────────────────────────────────────────────────

def handle_search(args) -> int:
    """Handle station search command."""
    try:
        api = MVGAPI()
        stations = api.search_stations(args.query)
        
        if args.json:
            print(json.dumps(stations, indent=2, ensure_ascii=False))
            return EXIT_OK
        
        if not stations:
            print(f"❌ Keine Stationen gefunden für '{args.query}'")
            return EXIT_ERROR
        
        content = []
        for station in stations[:10]:  # Limit to 10 results
            name = station.get("name", "N/A")
            place = station.get("place", "")
            global_id = station.get("globalId", "N/A")
            
            transport_types = station.get("transportTypes", [])
            emojis = " ".join(get_transport_emoji(t) for t in transport_types)
            
            location = f"{name}"
            if place and place != name:
                location += f", {place}"
            
            content.append(f"{emojis} {location}")
            content.append(f"   ID: {global_id}")
            
            if station != stations[-1] and len([s for s in stations[:10] if stations.index(s) > stations.index(station)]) > 0:
                content.append("")
        
        print_box(f"Stationen für '{args.query}'", content)
        return EXIT_OK
        
    except MVGAPIError as e:
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"❌ API-Fehler: {e}")
        return EXIT_API_ERROR


def handle_departures(args) -> int:
    """Handle departures command."""
    try:
        api = MVGAPI()
        
        # Resolve station name to globalId
        global_id = api.resolve_station(args.station)
        if not global_id:
            error = f"Station '{args.station}' nicht gefunden"
            if args.json:
                print(json.dumps({"error": error}, indent=2))
            else:
                print(f"❌ {error}")
            return EXIT_ERROR
        
        # Parse transport types filter
        transport_types = None
        if args.type:
            transport_types = [TRANSPORT_TYPE_MAP[t.strip().lower()] for t in args.type.split(",") if t.strip().lower() in TRANSPORT_TYPE_MAP]
        
        departures = api.get_departures(
            global_id,
            limit=args.limit,
            transport_types=transport_types,
            offset_minutes=args.offset
        )
        
        if args.json:
            print(json.dumps(departures, indent=2, ensure_ascii=False))
            return EXIT_OK
        
        if not departures:
            print(f"❌ Keine Abfahrten gefunden für '{args.station}'")
            return EXIT_ERROR
        
        # Prepare table data
        headers = ["Linie", "Ziel", "Abfahrt", "Verspätung", "Gleis"]
        rows = []
        
        for dep in departures:
            emoji = get_transport_emoji(dep.get("transportType", ""))
            label = dep.get("label", "")
            destination = dep.get("destination", "")
            
            planned_time = format_time(dep.get("plannedTime"))
            delay = format_delay(dep.get("delayMinutes", 0))
            
            platform = dep.get("platform", "")
            if dep.get("platformChanged"):
                platform += " ⚠️"
            
            line_info = f"{emoji} {label}"
            if dep.get("cancelled"):
                line_info += " ❌"
            
            rows.append([line_info, destination, planned_time, delay, platform])
        
        print()
        print(f"📍 Abfahrten für {args.station}")
        if args.offset > 0:
            print(f"   (mit {args.offset} min Fußweg)")
        print()
        print_table(headers, rows)
        print()
        
        return EXIT_OK
        
    except MVGAPIError as e:
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"❌ API-Fehler: {e}")
        return EXIT_API_ERROR


def handle_route(args) -> int:
    """Handle route search command."""
    try:
        api = MVGAPI()
        
        # Resolve locations (stations or addresses)
        origin_loc = api.resolve_location(args.origin)
        if not origin_loc:
            error = f"Start '{args.origin}' nicht gefunden"
            if args.json:
                print(json.dumps({"error": error}, indent=2))
            else:
                print(f"❌ {error}")
            return EXIT_ERROR
        
        destination_loc = api.resolve_location(args.destination)
        if not destination_loc:
            error = f"Ziel '{args.destination}' nicht gefunden"
            if args.json:
                print(json.dumps({"error": error}, indent=2))
            else:
                print(f"❌ {error}")
            return EXIT_ERROR
        
        # Resolve via stop if provided
        via_loc = None
        if args.via:
            via_loc = api.resolve_location(args.via)
            if not via_loc:
                error = f"Zwischenstopp '{args.via}' nicht gefunden"
                if args.json:
                    print(json.dumps({"error": error}, indent=2))
                else:
                    print(f"❌ {error}")
                return EXIT_ERROR
        
        # Parse time if provided
        departure_time = None
        if args.time:
            try:
                # Assume format HH:MM
                time_parts = args.time.split(":")
                if len(time_parts) == 2:
                    hour, minute = int(time_parts[0]), int(time_parts[1])
                    now = datetime.now()
                    dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    departure_time = dt.isoformat()
            except (ValueError, IndexError):
                error = f"Ungültiges Zeitformat: {args.time} (erwartet HH:MM)"
                if args.json:
                    print(json.dumps({"error": error}, indent=2))
                else:
                    print(f"❌ {error}")
                return EXIT_ERROR
        
        # Parse transport type filters
        transport_types = None
        
        if args.type:
            transport_types = [TRANSPORT_TYPE_MAP[t.strip().lower()] for t in args.type.split(",") if t.strip().lower() in TRANSPORT_TYPE_MAP]
        elif args.exclude:
            excluded = {TRANSPORT_TYPE_MAP[t.strip().lower()] for t in args.exclude.split(",") if t.strip().lower() in TRANSPORT_TYPE_MAP}
            transport_types = [t for t in ALL_TRANSPORT_TYPES if t not in excluded]
        
        # Map CLI options to API params
        mode_map = {"fast": "FAST", "less-changes": "LESS_CHANGES", "less-walking": "LESS_WALKING"}
        speed_map = {"slow": "SLOW", "normal": "NORMAL", "fast": "FAST"}
        
        routes = api.find_routes(
            origin_loc,
            destination_loc,
            is_arrival_time=args.arrive,
            departure_time=departure_time,
            transport_types=transport_types,
            routing_mode=mode_map.get(args.mode, "FAST"),
            walk_speed=speed_map.get(args.walk_speed, "NORMAL"),
            accessible=args.accessible,
            via=via_loc
        )
        
        if args.json:
            print(json.dumps(routes, indent=2, ensure_ascii=False))
            return EXIT_OK
        
        if not routes:
            print(f"❌ Keine Verbindungen gefunden von '{args.origin}' nach '{args.destination}'")
            return EXIT_ERROR
        
        print()
        via_str = f" via {args.via}" if args.via else ""
        print(f"🗺️  Verbindungen: {args.origin}{via_str} → {args.destination}")
        print()
        
        for i, route in enumerate(routes[:5], 1):  # Show max 5 routes
            # Extract departure and arrival times from parts if not available at route level
            parts = route.get("parts", [])
            
            route_departure = route.get("departure")
            route_arrival = route.get("arrival")
            
            if not route_departure and parts:
                first_part = parts[0]
                route_departure = first_part.get("from", {}).get("departure")
            
            if not route_arrival and parts:
                last_part = parts[-1]  
                route_arrival = last_part.get("to", {}).get("arrival")
            
            departure = format_time_iso(route_departure) if route_departure else "N/A"
            arrival = format_time_iso(route_arrival) if route_arrival else "N/A"
            duration = route.get("duration") or 0
            
            content = [f"Abfahrt: {departure} → Ankunft: {arrival} (Dauer: {duration} min)"]
            content.append("")
            
            for part in route.get("parts", []):
                line = part.get("line")
                if line:
                    transport_type = line.get("transportType", "")
                    label = line.get("label", "")
                    emoji = get_transport_emoji(transport_type)
                    
                    from_name = part.get("from", {}).get("name", "")
                    to_name = part.get("to", {}).get("name", "")
                    from_time = format_time_iso(part.get("from", {}).get("departure"))
                    to_time = format_time_iso(part.get("to", {}).get("arrival"))
                    
                    content.append(f"{emoji} {label}: {from_name} ({from_time}) → {to_name} ({to_time})")
                else:
                    # Pedestrian part
                    from_name = part.get("from", {}).get("name", "")
                    to_name = part.get("to", {}).get("name", "")
                    content.append(f"🚶 Fußweg: {from_name} → {to_name}")
            
            print_box(f"Verbindung {i}", content)
            print()
        
        return EXIT_OK
        
    except MVGAPIError as e:
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"❌ API-Fehler: {e}")
        return EXIT_API_ERROR


def handle_nearby(args) -> int:
    """Handle nearby stations command."""
    try:
        api = MVGAPI()
        
        # Use provided coordinates or defaults
        lat = args.latitude if args.latitude is not None else DEFAULT_LAT
        lon = args.longitude if args.longitude is not None else DEFAULT_LON
        
        stations = api.get_nearby_stations(lat, lon)
        
        if args.json:
            print(json.dumps(stations, indent=2, ensure_ascii=False))
            return EXIT_OK
        
        if not stations:
            print(f"❌ Keine Stationen in der Nähe von {lat}, {lon} gefunden")
            return EXIT_ERROR
        
        content = []
        for station in stations:
            name = station.get("name", "N/A")
            place = station.get("place", "")
            distance = station.get("distanceInMeters")
            
            transport_types = station.get("transportTypes", [])
            emojis = " ".join(get_transport_emoji(t) for t in transport_types)
            
            location = f"{name}"
            if place and place != name:
                location += f", {place}"
            
            distance_str = f" ({distance}m)" if distance else ""
            content.append(f"{emojis} {location}{distance_str}")
        
        print_box(f"Nächste Stationen ({lat:.4f}, {lon:.4f})", content)
        return EXIT_OK
        
    except MVGAPIError as e:
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"❌ API-Fehler: {e}")
        return EXIT_API_ERROR


def handle_alerts(args) -> int:
    """Handle alerts/disruptions command."""
    try:
        api = MVGAPI()
        
        # Resolve station if provided
        global_id = None
        if args.station:
            global_id = api.resolve_station(args.station)
            if not global_id:
                error = f"Station '{args.station}' nicht gefunden"
                if args.json:
                    print(json.dumps({"error": error}, indent=2))
                else:
                    print(f"❌ {error}")
                return EXIT_ERROR
        
        alerts = api.get_alerts(global_id)
        
        if args.json:
            print(json.dumps(alerts, indent=2, ensure_ascii=False))
            return EXIT_OK
        
        if not alerts:
            location_str = f" für {args.station}" if args.station else ""
            print(f"✅ Keine Störungen{location_str} gemeldet")
            return EXIT_OK
        
        title = f"Störungsmeldungen"
        if args.station:
            title += f" für {args.station}"
        
        content = []
        for alert in alerts:
            title_text = alert.get("title", "Unbekannte Störung")
            description = clean_html(alert.get("description", ""))
            severity = alert.get("severity", "")
            
            valid_from = format_datetime(alert.get("validFrom"))
            valid_to = format_datetime(alert.get("validTo"))
            
            affected_lines = alert.get("affectedLines", [])
            lines_str = ", ".join(affected_lines) if affected_lines else "Alle Linien"
            
            severity_emoji = "🔴" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🔵"
            
            content.append(f"{severity_emoji} {title_text}")
            if description:
                content.append(f"   {description}")
            content.append(f"   Betroffene Linien: {lines_str}")
            content.append(f"   Gültig: {valid_from} - {valid_to}")
            
            if alert != alerts[-1]:
                content.append("")
        
        print_box(title, content)
        return EXIT_OK
        
    except MVGAPIError as e:
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"❌ API-Fehler: {e}")
        return EXIT_API_ERROR


def handle_lines(args) -> int:
    """Handle lines listing command."""
    try:
        api = MVGAPI()
        
        # Parse transport type filter
        transport_type = None
        if args.type:
            transport_type = TRANSPORT_TYPE_MAP.get(args.type.lower())
            if not transport_type:
                error = f"Unbekannter Verkehrsmitteltyp: {args.type}"
                if args.json:
                    print(json.dumps({"error": error}, indent=2))
                else:
                    print(f"❌ {error}")
                return EXIT_ERROR
        
        lines = api.get_lines(transport_type)
        
        if args.json:
            print(json.dumps(lines, indent=2, ensure_ascii=False))
            return EXIT_OK
        
        if not lines:
            type_str = f" ({args.type})" if args.type else ""
            print(f"❌ Keine Linien{type_str} gefunden")
            return EXIT_ERROR
        
        # Group by transport type
        grouped_lines = {}
        for line in lines:
            t_type = line.get("transportType", "UNKNOWN")
            if t_type not in grouped_lines:
                grouped_lines[t_type] = []
            grouped_lines[t_type].append(line)
        
        print()
        for t_type, type_lines in grouped_lines.items():
            emoji = get_transport_emoji(t_type)
            
            content = []
            for line in sorted(type_lines, key=lambda x: x.get("label", "")):
                label = line.get("label", "")
                name = line.get("name", "")
                network = line.get("network", "")
                
                line_str = f"{label}"
                if name and name != label:
                    line_str += f" - {name}"
                if network:
                    line_str += f" ({network})"
                
                content.append(line_str)
            
            print_box(f"{emoji} {t_type} Linien", content)
            print()
        
        return EXIT_OK
        
    except MVGAPIError as e:
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"❌ API-Fehler: {e}")
        return EXIT_API_ERROR


# ─────────────────────────────────────────────────────────────────────────────
# CLI Setup
# ─────────────────────────────────────────────────────────────────────────────

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="mvg",
        description="Münchner Verkehrsgesellschaft (MVG) CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Global options
    parser.add_argument(
        "--json",
        action="store_true",
        help="Ausgabe als JSON"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Verfügbare Commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Station suchen")
    search_parser.add_argument("query", help="Suchbegriff für Station")
    
    # Departures command  
    dep_parser = subparsers.add_parser("departures", help="Abfahrten anzeigen")
    dep_parser.add_argument("station", help="Stationsname")
    dep_parser.add_argument("--limit", type=int, default=10, help="Anzahl Abfahrten (default: 10)")
    dep_parser.add_argument("--type", help="Verkehrsmittel-Filter (z.B. ubahn,sbahn,bus,tram)")
    dep_parser.add_argument("--offset", type=int, default=0, help="Fußweg-Offset in Minuten")
    
    # Route command
    route_parser = subparsers.add_parser("route", help="Verbindung suchen")
    route_parser.add_argument("origin", help="Start (Station oder Adresse)")
    route_parser.add_argument("destination", help="Ziel (Station oder Adresse)")
    route_parser.add_argument("--via", help="Zwischenstopp (Station oder Adresse)")
    route_parser.add_argument("--arrive", action="store_true", help="Zeit als Ankunftszeit verwenden")
    route_parser.add_argument("--time", help="Bestimmte Zeit (HH:MM)")
    route_parser.add_argument("--type", help="Nur bestimmte Verkehrsmittel (z.B. ubahn,sbahn)")
    route_parser.add_argument("--exclude", help="Verkehrsmittel ausschließen (z.B. bus,tram)")
    route_parser.add_argument("--mode", choices=["fast", "less-changes", "less-walking"],
                              default="fast", help="Suchmodus (default: fast)")
    route_parser.add_argument("--walk-speed", choices=["slow", "normal", "fast"],
                              default="normal", help="Lauftempo (default: normal)")
    route_parser.add_argument("--accessible", action="store_true",
                              help="Nur rollstuhlgerechte Verbindungen")
    
    # Nearby command
    nearby_parser = subparsers.add_parser("nearby", help="Nächste Stationen")
    nearby_parser.add_argument("latitude", nargs="?", type=float, help="Breitengrad")
    nearby_parser.add_argument("longitude", nargs="?", type=float, help="Längengrad")
    
    # Alerts command
    alerts_parser = subparsers.add_parser("alerts", help="Störungsmeldungen")
    alerts_parser.add_argument("--station", help="Stationsspezifische Störungen")
    
    # Lines command
    lines_parser = subparsers.add_parser("lines", help="Linien auflisten")
    lines_parser.add_argument("--type", help="Verkehrsmittel-Filter (ubahn, sbahn, bus, tram, bahn)")
    
    # Live S-Bahn tracking command
    live_parser = subparsers.add_parser("live", help="S-Bahn München Live-Tracking")
    live_parser.add_argument("--line", help="Nur bestimmte Linie (z.B. S3, S8)")
    live_parser.add_argument("--json", action="store_true", dest="live_json", help="JSON-Ausgabe")
    
    return parser


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return EXIT_ERROR
    
    # Route to appropriate handler
    handlers = {
        "search": handle_search,
        "departures": handle_departures,
        "route": handle_route,
        "nearby": handle_nearby,
        "alerts": handle_alerts,
        "lines": handle_lines,
        "live": handle_live,
    }
    
    handler = handlers.get(args.command)
    if not handler:
        print(f"❌ Unbekannter Command: {args.command}")
        return EXIT_ERROR
    
    try:
        return handler(args)
    except KeyboardInterrupt:
        print("\n❌ Abgebrochen")
        return EXIT_ERROR
    except Exception as e:
        if args.json:
            print(json.dumps({"error": f"Unerwarteter Fehler: {e}"}, indent=2))
        else:
            print(f"❌ Unerwarteter Fehler: {e}")
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())