#!/usr/bin/env python3
"""
Ontopo CLI - Search Israeli restaurants and check table availability.

A complete, self-contained CLI for interacting with the Ontopo restaurant
booking platform API.
"""

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx", file=sys.stderr)
    sys.exit(1)


# =============================================================================
# CONSTANTS
# =============================================================================

BASE_URL = "https://ontopo.com/api"
WEBSITE_URL = "https://ontopo.com"
ISRAEL_DISTRIBUTOR_SLUG = "15171493"  # Required for venue search
ISRAEL_MARKETPLACE_ID = "29421469"   # Required for batch availability search

CITIES = [
    "tel-aviv", "jerusalem", "haifa", "herzliya", "raanana", "ramat-gan",
    "netanya", "ashdod", "ashkelon", "beer-sheva", "eilat", "modiin",
    "rehovot", "rishon-lezion", "petah-tikva", "holon", "bat-yam",
    "givataim", "kfar-saba", "hod-hasharon", "rosh-haayin", "shoham",
    "yavne", "caesarea", "zichron-yaakov", "pardes-hanna", "hadera", "nahariya"
]

CATEGORIES = [
    "restaurants", "bars", "fine_dining", "happy_hour",
    "brunch", "business", "kosher", "events"
]

# City to geocode mapping for availability search (from Ontopo API)
CITY_GEOCODES = {
    "tel-aviv": "telavivjaffa",
    "jerusalem": "jerusalem",
    "haifa": "haifa",
    "herzliya": "herzliya",
    "raanana": "raanana",
    "ramat-gan": "ramatgan",
    "netanya": "netanya",
    "ashdod": "ashdod",
    "ashkelon": "ashkelon",
    "beer-sheva": "beersheva",
    "eilat": "eilat",
    "modiin": "modiin",
    "rehovot": "rehovot",
    "rishon-lezion": "rishonlezion",
    "petah-tikva": "petahtikva",
    "holon": "holon",
    "kfar-saba": "kfarsaba",
    "hod-hasharon": "hodhasharon",
    "caesarea": "caesarea",
    "north": "north",
    "south": "south",
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def parse_time(time_str: str) -> str:
    """
    Parse flexible time input and return HHMM format.
    Accepts: HH:MM, HHMM, "19:00", "7pm", "7:30pm", "19"
    """
    time_str = time_str.strip().lower().replace('"', '').replace("'", "")

    # Handle am/pm format
    is_pm = 'pm' in time_str
    is_am = 'am' in time_str
    time_str = time_str.replace('pm', '').replace('am', '').strip()

    # Try different patterns
    patterns = [
        (r'^(\d{1,2}):(\d{2})$', lambda m: (int(m.group(1)), int(m.group(2)))),
        (r'^(\d{4})$', lambda m: (int(m.group(1)[:2]), int(m.group(1)[2:]))),
        (r'^(\d{1,2})$', lambda m: (int(m.group(1)), 0)),
    ]

    for pattern, extractor in patterns:
        match = re.match(pattern, time_str)
        if match:
            hour, minute = extractor(match)
            break
    else:
        raise ValueError(f"Invalid time format: {time_str}. Use HH:MM, HHMM, or 7pm")

    # Apply am/pm conversion
    if is_pm and hour < 12:
        hour += 12
    elif is_am and hour == 12:
        hour = 0

    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Invalid time: {hour:02d}:{minute:02d}")

    return f"{hour:02d}{minute:02d}"


def parse_date(date_str: str) -> str:
    """
    Parse date input (YYYY-MM-DD) and return YYYYMMDD format.
    Also accepts: today, tomorrow, or relative days like +3
    """
    date_str = date_str.strip().lower()

    if date_str == 'today':
        dt = datetime.now()
    elif date_str == 'tomorrow':
        dt = datetime.now() + timedelta(days=1)
    elif date_str.startswith('+'):
        days = int(date_str[1:])
        dt = datetime.now() + timedelta(days=days)
    else:
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD, today, tomorrow, or +N")

    return dt.strftime('%Y%m%d')


def format_date_display(date_str: str) -> str:
    """Convert YYYYMMDD to readable format."""
    try:
        dt = datetime.strptime(date_str, '%Y%m%d')
        return dt.strftime('%Y-%m-%d (%A)')
    except ValueError:
        return date_str


def format_time_display(time_str: str) -> str:
    """Convert HHMM to HH:MM format."""
    if len(time_str) == 4:
        return f"{time_str[:2]}:{time_str[2:]}"
    return time_str


def format_price(price: Any) -> str:
    """Format price for display."""
    if price is None:
        return "N/A"
    try:
        return f"{float(price):.0f} ILS"
    except (ValueError, TypeError):
        return str(price)


def print_table(headers: List[str], rows: List[List[str]], min_widths: Optional[List[int]] = None) -> str:
    """Create a markdown-style table."""
    if not rows:
        return "No data to display."

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))

    if min_widths:
        for i, mw in enumerate(min_widths):
            if i < len(widths):
                widths[i] = max(widths[i], mw)

    # Build table
    lines = []

    # Header
    header_line = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    lines.append(header_line)

    # Separator
    sep_line = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
    lines.append(sep_line)

    # Rows
    for row in rows:
        row_cells = []
        for i, cell in enumerate(row):
            if i < len(widths):
                row_cells.append(str(cell).ljust(widths[i]))
        line = "| " + " | ".join(row_cells) + " |"
        lines.append(line)

    return "\n".join(lines)


# =============================================================================
# API CLIENT
# =============================================================================

class OntopoClient:
    """Async client for Ontopo API."""

    def __init__(self, locale: str = "en"):
        self.locale = locale
        self.token: Optional[str] = None
        self._venue_page_cache: Dict[str, str] = {}
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def _ensure_auth(self) -> None:
        """Ensure we have a valid JWT token."""
        if self.token:
            return

        response = await self._request("POST", "/loginAnonymously", auth_required=False)
        self.token = response.get("jwt_token")
        if not self.token:
            raise RuntimeError("Failed to obtain authentication token")

    async def _request(
        self,
        method: str,
        endpoint: str,
        body: Optional[Dict] = None,
        params: Optional[Dict] = None,
        auth_required: bool = True,
        retries: int = 3
    ) -> Any:
        """Make an API request with retry logic."""
        if auth_required:
            await self._ensure_auth()

        url = f"{BASE_URL}/{endpoint.lstrip('/')}"
        headers = {"Content-Type": "application/json"}

        if auth_required and self.token:
            headers["token"] = self.token

        for attempt in range(retries):
            try:
                if method == "GET":
                    response = await self._client.get(url, params=params, headers=headers)
                elif method == "POST":
                    response = await self._client.post(url, json=body, headers=headers)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                if response.status_code == 429:
                    # Rate limited - wait and retry
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue

                if response.status_code == 401:
                    # Token expired - refresh and retry
                    self.token = None
                    await self._ensure_auth()
                    continue

                response.raise_for_status()

                if response.content:
                    return response.json()
                return {}

            except httpx.HTTPStatusError as e:
                if attempt == retries - 1:
                    raise RuntimeError(f"API error: {e.response.status_code} - {e.response.text}")
                await asyncio.sleep(1)
            except httpx.RequestError as e:
                if attempt == retries - 1:
                    raise RuntimeError(f"Network error: {e}")
                await asyncio.sleep(1)

        raise RuntimeError("Max retries exceeded")

    async def search_venues(self, query: str, city: Optional[str] = None) -> List[Dict]:
        """Search for venues by query."""
        params = {
            "slug": ISRAEL_DISTRIBUTOR_SLUG,
            "version": "1",
            "terms": query,
            "locale": self.locale
        }

        response = await self._request("GET", "/venue_search", params=params, auth_required=False)

        venues = response if isinstance(response, list) else response.get("venues", response.get("results", []))
        return venues if isinstance(venues, list) else []

    async def get_venue_profile(self, venue_id: str) -> Dict:
        """Get venue profile including page mappings."""
        params = {
            "slug": venue_id,
            "version": "1",
            "locale": self.locale
        }
        return await self._request("GET", "/venue_profile", params=params, auth_required=False)

    async def get_page(self, page_id: str) -> Dict:
        """Get page/venue details using slug_content API."""
        params = {
            "slug": page_id,
            "locale": self.locale
        }
        return await self._request("GET", "/slug_content", params=params, auth_required=False)

    async def resolve_page_id(self, venue_id: str) -> str:
        """Resolve venue_id to page_id for booking operations."""
        if venue_id in self._venue_page_cache:
            return self._venue_page_cache[venue_id]

        try:
            profile = await self.get_venue_profile(venue_id)
            pages = profile.get("pages", [])
            # Look for a page with content_type="reservation"
            for page in pages:
                if page.get("content_type") == "reservation":
                    page_slug = page.get("slug", page.get("id", venue_id))
                    self._venue_page_cache[venue_id] = page_slug
                    return page_slug
            # Fallback to first page if no reservation type found
            if pages:
                page_slug = pages[0].get("slug", pages[0].get("id", venue_id))
                self._venue_page_cache[venue_id] = page_slug
                return page_slug
        except Exception:
            pass

        # Fallback: try using venue_id directly as page_id
        self._venue_page_cache[venue_id] = venue_id
        return venue_id

    async def resolve_venue_name(self, venue_input: str) -> str:
        """Resolve venue name or ID to a usable venue ID.

        If input is numeric, return as-is.
        If input is text (e.g., 'taizu'), search and return first match's slug.
        """
        # If it's already numeric, use directly
        if venue_input.isdigit():
            return venue_input

        # Search for the venue name
        try:
            results = await self.search_venues(venue_input)
            if results:
                # Return the first match's slug
                first = results[0]
                slug = first.get("slug", first.get("id", venue_input))
                return slug
        except Exception:
            pass

        # Fallback: return as-is and let downstream handle errors
        return venue_input

    async def create_search_token(
        self,
        date: str,
        time: str,
        size: int,
        geocodes: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> str:
        """Create a search session for batch availability."""
        body = {
            "marketplace_id": ISRAEL_MARKETPLACE_ID,
            "criteria": {
                "date": date,
                "time": time,
                "size": str(size)  # Must be string
            },
            "locale": self.locale,
            "analytics": {
                "distributor_id": "il",
                "platform": "web"
            }
        }
        if geocodes:
            body["geocodes"] = geocodes
        if category:
            body["primary"] = [category]

        response = await self._request("POST", "/search_token", body=body)
        return response.get("search_id", response.get("token", ""))

    async def get_search_results(self, search_id: str) -> Dict:
        """Get search results with availability."""
        body = {"search_id": search_id}
        response = await self._request("POST", "/search_request", body=body)
        return response

    async def check_availability(
        self,
        venue_id: str,
        date: str,
        time: str,
        size: int
    ) -> Dict:
        """Check specific venue availability."""
        page_id = await self.resolve_page_id(venue_id)

        # The API requires specific structure:
        # - slug at top level (not 'venue')
        # - criteria object with size/date/time as STRINGS
        body = {
            "slug": page_id,
            "locale": self.locale,
            "criteria": {
                "size": str(size),  # Must be string!
                "date": date,       # YYYYMMDD format
                "time": time,       # HHMM format
            }
        }
        return await self._request("POST", "/availability_search", body=body)

    async def get_venue_info(self, venue_id: str) -> Dict:
        """Get detailed venue information."""
        page_id = await self.resolve_page_id(venue_id)
        return await self.get_page(page_id)


# =============================================================================
# COMMAND HANDLERS
# =============================================================================

class CommandHandler:
    """Handle CLI commands and format output."""

    def __init__(self, client: OntopoClient, json_output: bool = False):
        self.client = client
        self.json_output = json_output

    def _output(self, data: Any, markdown: str) -> None:
        """Output data in JSON or markdown format."""
        if self.json_output:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(markdown)

    async def cmd_cities(self) -> None:
        """List supported cities."""
        data = {"cities": CITIES, "count": len(CITIES)}

        if self.json_output:
            self._output(data, "")
        else:
            print(f"Supported Cities ({len(CITIES)}):")
            print("-" * 40)
            for i, city in enumerate(CITIES, 1):
                print(f"  {i:2}. {city}")

    async def cmd_categories(self) -> None:
        """List supported categories."""
        data = {"categories": CATEGORIES, "count": len(CATEGORIES)}

        if self.json_output:
            self._output(data, "")
        else:
            print(f"Supported Categories ({len(CATEGORIES)}):")
            print("-" * 40)
            for cat in CATEGORIES:
                print(f"  - {cat}")

    async def cmd_search(self, query: str, city: Optional[str] = None) -> None:
        """Search for venues."""
        venues = await self.client.search_venues(query, city)

        if not venues:
            msg = f"No venues found for '{query}'"
            if city:
                msg += f" in {city}"
            msg += "."
            if self.json_output:
                self._output({"venues": [], "message": msg}, "")
            else:
                print(msg)
            return

        data = {"venues": venues, "count": len(venues)}

        if self.json_output:
            self._output(data, "")
        else:
            print(f"Search Results for '{query}':")
            if city:
                print(f"City: {city}")
            print()

            rows = []
            for v in venues[:20]:  # Limit display
                venue_id = v.get("slug", v.get("id", v.get("venue_id", "N/A")))
                name = v.get("title", v.get("name", "Unknown"))[:40]
                address = v.get("address", "")[:30]
                rows.append([str(venue_id), name, address])

            table = print_table(
                ["Venue ID", "Name", "Address"],
                rows,
                [12, 40, 30]
            )
            print(table)

            if len(venues) > 20:
                print(f"\n... and {len(venues) - 20} more results")

    async def cmd_available(
        self,
        date: str,
        time: str,
        city: Optional[str] = None,
        party_size: int = 2
    ) -> None:
        """Search for available venues."""
        api_date = parse_date(date)
        api_time = parse_time(time)

        # Get geocode for city (single value, wrapped in list for API)
        geocode = CITY_GEOCODES.get(city) if city else None
        geocodes = [geocode] if geocode else None

        try:
            search_id = await self.client.create_search_token(
                api_date, api_time, party_size, geocodes
            )

            if not search_id:
                raise RuntimeError("Failed to create search session")

            response = await self.client.get_search_results(search_id)
            # Extract posts array from response
            results = response.get("posts", response.get("results", []))
            if not isinstance(results, list):
                results = []
        except Exception as e:
            if self.json_output:
                self._output({"error": str(e), "venues": []}, "")
            else:
                print(f"Error searching availability: {e}")
            return

        data = {
            "date": api_date,
            "time": api_time,
            "party_size": party_size,
            "city": city,
            "venues": results,
            "count": len(results)
        }

        if self.json_output:
            self._output(data, "")
        else:
            print(f"Available Venues")
            print(f"Date: {format_date_display(api_date)}")
            print(f"Time: {format_time_display(api_time)}")
            print(f"Party Size: {party_size}")
            if city:
                print(f"City: {city}")
            print()

            if not results:
                print("No available venues found for this search.")
                return

            rows = []
            for r in results[:25]:
                # Structure: {"post": {...}, "availability": {...}}
                post = r.get("post", r)
                avail = r.get("availability", {})

                venue_id = post.get("page_slug", post.get("slug", "N/A"))
                name = post.get("venue_name", post.get("title", "Unknown"))[:35]

                # Get available times from areas[].options[] where method="seat"
                areas = avail.get("areas", [])
                times_set = set()
                for area in areas:
                    for opt in area.get("options", []):
                        if isinstance(opt, dict) and opt.get("method") == "seat":
                            time_val = opt.get("time", "")
                            if time_val:
                                times_set.add(format_time_display(time_val))

                slot_times = ", ".join(sorted(times_set)[:5]) if times_set else "Check venue"
                rows.append([str(venue_id), name, slot_times[:30]])

            table = print_table(
                ["ID", "Name", "Available Times"],
                rows,
                [10, 35, 30]
            )
            print(table)

    async def cmd_check(
        self,
        venue_id: str,
        date: str,
        time: Optional[str] = None,
        party_size: int = 2
    ) -> None:
        """Check availability for a specific venue."""
        # Resolve venue name to ID if needed
        resolved_id = await self.client.resolve_venue_name(venue_id)

        api_date = parse_date(date)
        api_time = parse_time(time) if time else "1900"

        try:
            result = await self.client.check_availability(
                resolved_id, api_date, api_time, party_size
            )
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                if venue_id != resolved_id:
                    error_msg = f"Venue '{venue_id}' resolved to ID {resolved_id}, but not found. Try: ontopo-cli.py search <name>"
                else:
                    error_msg = f"Venue not found: {venue_id}. Try: ontopo-cli.py search <name>"
            if self.json_output:
                self._output({"error": error_msg, "available": False}, "")
            else:
                print(f"Error: {error_msg}")
            return

        data = {
            "venue_id": resolved_id,
            "venue_input": venue_id,
            "date": api_date,
            "time": api_time,
            "party_size": party_size,
            "availability": result
        }

        if self.json_output:
            self._output(data, "")
        else:
            print(f"Availability Check")
            if venue_id != resolved_id:
                print(f"Venue: {venue_id} (ID: {resolved_id})")
            else:
                print(f"Venue ID: {resolved_id}")
            print(f"Date: {format_date_display(api_date)}")
            print(f"Time: {format_time_display(api_time)}")
            print(f"Party Size: {party_size}")
            print()

            # Parse areas[].options[] structure from API response
            areas = result.get("areas", [])
            has_availability = False
            rows = []

            for area in areas:
                area_name = area.get("name", area.get("id", "Unknown"))
                area_icon = area.get("icon", "")
                options = area.get("options", [])

                for opt in options:
                    method = opt.get("method", "")
                    opt_time = opt.get("time", "")

                    if method == "seat":
                        has_availability = True
                        status = "✅ Available"
                        rows.append([format_time_display(opt_time), area_name, status])
                    elif method == "standby":
                        has_availability = True
                        status = "⏳ Waitlist"
                        rows.append([format_time_display(opt_time), area_name, status])

            if rows:
                print("Available Time Slots:")
                print()
                table = print_table(["Time", "Area", "Status"], rows, [8, 30, 15])
                print(table)

                # Show recommended options if available
                recommended = result.get("recommended", [])
                if recommended:
                    print("\nRecommended:")
                    for rec in recommended[:3]:
                        rec_time = format_time_display(rec.get("time", ""))
                        rec_area = rec.get("text", rec.get("id", ""))
                        print(f"  • {rec_time} - {rec_area}")
            else:
                # Check for alternative dates
                alt_dates = result.get("dates", [])
                if alt_dates:
                    print("No availability at requested time.")
                    print("\nAlternative dates with availability:")
                    for alt in alt_dates[:5]:
                        # Format: "202602021900" -> "2026-02-02 19:00"
                        if len(alt) >= 12:
                            alt_date = f"{alt[:4]}-{alt[4:6]}-{alt[6:8]}"
                            alt_time = f"{alt[8:10]}:{alt[10:12]}"
                            print(f"  • {alt_date} at {alt_time}")
                        else:
                            print(f"  • {alt}")
                else:
                    print("No availability at the requested time.")

    async def cmd_range(
        self,
        venue_id: str,
        start_date: str,
        end_date: str,
        times: str = "19:00,20:00",
        party_size: int = 2
    ) -> None:
        """Check availability over a date range."""
        # Resolve venue name to ID if needed
        resolved_id = await self.client.resolve_venue_name(venue_id)

        start = datetime.strptime(parse_date(start_date), '%Y%m%d')
        end = datetime.strptime(parse_date(end_date), '%Y%m%d')

        time_list = [parse_time(t.strip()) for t in times.split(",")]

        results = []
        current = start

        while current <= end:
            date_str = current.strftime('%Y%m%d')
            date_results = {"date": date_str, "times": []}

            for api_time in time_list:
                try:
                    result = await self.client.check_availability(
                        resolved_id, date_str, api_time, party_size
                    )
                    # Check areas[].options[] for method="seat" or "standby" availability
                    areas = result.get("areas", [])
                    available_times = []
                    waitlist_times = []
                    for area in areas:
                        for opt in area.get("options", []):
                            method = opt.get("method", "")
                            if method == "seat":
                                available_times.append(opt.get("time", ""))
                            elif method == "standby":
                                waitlist_times.append(opt.get("time", ""))

                    available = len(available_times) > 0
                    has_waitlist = len(waitlist_times) > 0
                    date_results["times"].append({
                        "time": api_time,
                        "available": available,
                        "waitlist": has_waitlist,
                        "slots": available_times,
                        "waitlist_slots": waitlist_times
                    })
                except Exception as e:
                    date_results["times"].append({
                        "time": api_time,
                        "available": False,
                        "error": str(e)
                    })

            results.append(date_results)
            current += timedelta(days=1)

        data = {
            "venue_id": venue_id,
            "start_date": start.strftime('%Y%m%d'),
            "end_date": end.strftime('%Y%m%d'),
            "times": time_list,
            "party_size": party_size,
            "results": results
        }

        if self.json_output:
            self._output(data, "")
        else:
            print(f"Availability Range Check")
            print(f"Venue ID: {venue_id}")
            print(f"Date Range: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
            print(f"Times: {', '.join(format_time_display(t) for t in time_list)}")
            print(f"Party Size: {party_size}")
            print()

            headers = ["Date"] + [format_time_display(t) for t in time_list]
            rows = []

            for day_result in results:
                row = [format_date_display(day_result["date"])[:12]]
                for time_result in day_result["times"]:
                    if time_result.get("available"):
                        row.append("Available")
                    elif time_result.get("waitlist"):
                        row.append("Waitlist")
                    elif time_result.get("error"):
                        row.append("Error")
                    else:
                        row.append("-")
                rows.append(row)

            table = print_table(headers, rows)
            print(table)

    async def cmd_menu(
        self,
        venue_id: str,
        section: Optional[str] = None,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> None:
        """Get venue menu."""
        # Resolve venue name to ID if needed
        resolved_id = await self.client.resolve_venue_name(venue_id)

        try:
            info = await self.client.get_venue_info(resolved_id)
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                error_msg = f"Venue not found: {venue_id}. Try: ontopo-cli.py search <name>"
            if self.json_output:
                self._output({"error": error_msg}, "")
            else:
                print(f"Error: {error_msg}")
            return

        menus = info.get("menus", info.get("menu", []))
        if isinstance(menus, dict):
            menus = [menus]

        # Flatten menu items from structure: menus[].sections[].items[]
        all_items = []
        for menu_obj in menus:
            menu_title = menu_obj.get("title", "Menu")
            sections = menu_obj.get("sections", [])

            # If no sections, try items directly
            if not sections:
                items = menu_obj.get("items", menu_obj.get("dishes", []))
                for item in items:
                    item_copy = dict(item)
                    item_copy["_section"] = menu_title
                    item_copy["_menu"] = menu_title
                    all_items.append(item_copy)
            else:
                for section_obj in sections:
                    section_name = section_obj.get("title", section_obj.get("name", ""))
                    items = section_obj.get("items", section_obj.get("dishes", []))
                    for item in items:
                        item_copy = dict(item)
                        item_copy["_section"] = section_name if section_name else menu_title
                        item_copy["_menu"] = menu_title
                        all_items.append(item_copy)

        # Apply filters
        filtered = all_items

        if section:
            section_lower = section.lower()
            filtered = [i for i in filtered if section_lower in i.get("_section", "").lower()]

        if search:
            search_lower = search.lower()
            filtered = [i for i in filtered if (
                search_lower in i.get("name", "").lower() or
                search_lower in i.get("description", "").lower()
            )]

        if min_price is not None:
            filtered = [i for i in filtered if (
                i.get("price") is not None and float(i.get("price", 0)) >= min_price
            )]

        if max_price is not None:
            filtered = [i for i in filtered if (
                i.get("price") is not None and float(i.get("price", 999999)) <= max_price
            )]

        data = {
            "venue_id": venue_id,
            "items": filtered,
            "count": len(filtered),
            "filters": {
                "section": section,
                "search": search,
                "min_price": min_price,
                "max_price": max_price
            }
        }

        if self.json_output:
            self._output(data, "")
        else:
            venue_name = info.get("name", info.get("title", venue_id))
            print(f"Menu: {venue_name}")
            print()

            if not filtered:
                print("No menu items found matching your criteria.")
                return

            # Group by section
            sections: Dict[str, List[Dict]] = {}
            for item in filtered:
                sec = item.get("_section", "Other")
                if sec not in sections:
                    sections[sec] = []
                sections[sec].append(item)

            for sec_name, items in sections.items():
                print(f"## {sec_name}")
                print()
                rows = []
                for item in items:
                    name = item.get("name", item.get("title", ""))[:40]
                    desc = item.get("description", "")[:30]
                    price = format_price(item.get("price"))
                    rows.append([name, desc, price])

                table = print_table(["Item", "Description", "Price"], rows)
                print(table)
                print()

    async def cmd_info(self, venue_id: str) -> None:
        """Get detailed venue information."""
        # Resolve venue name to ID if needed
        resolved_id = await self.client.resolve_venue_name(venue_id)

        try:
            info = await self.client.get_venue_info(resolved_id)
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                error_msg = f"Venue not found: {venue_id}. Try: ontopo-cli.py search <name>"
            if self.json_output:
                self._output({"error": error_msg}, "")
            else:
                print(f"Error: {error_msg}")
            return

        if self.json_output:
            self._output(info, "")
        else:
            name = info.get("name", info.get("title", "Unknown"))
            print(f"# {name}")
            print()

            details = [
                ("ID", info.get("id", venue_id)),
                ("Address", info.get("address", info.get("location", {}).get("address", "N/A"))),
                ("City", info.get("city", info.get("area", "N/A"))),
                ("Cuisine", info.get("cuisine", info.get("category", "N/A"))),
                ("Rating", info.get("rating", "N/A")),
                ("Price Range", info.get("price_range", info.get("price_level", "N/A"))),
                ("Phone", info.get("phone", info.get("telephone", "N/A"))),
                ("Website", info.get("website", info.get("url", "N/A"))),
            ]

            for label, value in details:
                if value and value != "N/A":
                    print(f"**{label}**: {value}")

            # Hours
            hours = info.get("hours", info.get("opening_hours", {}))
            if hours:
                print()
                print("## Opening Hours")
                if isinstance(hours, dict):
                    for day, time_range in hours.items():
                        print(f"  {day}: {time_range}")
                elif isinstance(hours, list):
                    for h in hours:
                        print(f"  {h}")

            # Description
            description = info.get("description", info.get("about", ""))
            if description:
                print()
                print("## About")
                print(description[:500])
                if len(description) > 500:
                    print("...")

    async def cmd_url(self, venue_id: str) -> None:
        """Get booking URL for venue."""
        # Resolve venue name to ID if needed
        resolved_id = await self.client.resolve_venue_name(venue_id)
        page_id = await self.client.resolve_page_id(resolved_id)
        url = f"https://ontopo.com/{self.client.locale}/il/page/{page_id}"

        if self.json_output:
            self._output({"venue_id": venue_id, "page_id": page_id, "url": url}, "")
        else:
            print(f"Booking URL: {url}")

# =============================================================================
# CLI SETUP
# =============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="ontopo-cli.py",
        description="Search Israeli restaurants on Ontopo and check table availability.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ontopo-cli.py cities                              # List supported cities
  ontopo-cli.py search "sushi" --city tel-aviv      # Search for sushi in Tel Aviv
  ontopo-cli.py available 2024-12-25 19:00          # Find available restaurants
  ontopo-cli.py check abc123 2024-12-25             # Check venue availability
  ontopo-cli.py range abc123 2024-12-20 2024-12-27  # Check availability range
  ontopo-cli.py menu abc123 --search "hummus"       # Search venue menu
  ontopo-cli.py info abc123                         # Get venue details
  ontopo-cli.py url abc123                          # Get booking URL
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # cities
    cities_parser = subparsers.add_parser("cities", help="List supported cities")
    cities_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # categories
    cat_parser = subparsers.add_parser("categories", help="List supported categories")
    cat_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # search
    search_parser = subparsers.add_parser("search", help="Search for venues")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--city", help="Filter by city")
    search_parser.add_argument("--locale", choices=["en", "he"], default="en", help="Language")
    search_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # available
    avail_parser = subparsers.add_parser("available", help="Search available venues")
    avail_parser.add_argument("date", help="Date (YYYY-MM-DD, today, tomorrow, +N)")
    avail_parser.add_argument("time", help="Time (HH:MM, HHMM, 7pm)")
    avail_parser.add_argument("--city", help="City to search in")
    avail_parser.add_argument("--party-size", type=int, default=2, help="Party size (default: 2)")
    avail_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # check
    check_parser = subparsers.add_parser("check", help="Check venue availability")
    check_parser.add_argument("venue_id", help="Venue ID or name (e.g., 36960535 or 'taizu')")
    check_parser.add_argument("date", help="Date (YYYY-MM-DD, today, tomorrow, +N)")
    check_parser.add_argument("time", nargs="?", default="19:00", help="Time (HH:MM, HHMM, 7pm) - default: 19:00")
    check_parser.add_argument("--party-size", type=int, default=2, help="Party size (default: 2)")
    check_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # range
    range_parser = subparsers.add_parser("range", help="Check availability over date range")
    range_parser.add_argument("venue_id", help="Venue ID")
    range_parser.add_argument("start_date", help="Start date (YYYY-MM-DD)")
    range_parser.add_argument("end_date", help="End date (YYYY-MM-DD)")
    range_parser.add_argument("--times", default="19:00,20:00", help="Times to check (comma-separated)")
    range_parser.add_argument("--party-size", type=int, default=2, help="Party size (default: 2)")
    range_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # menu
    menu_parser = subparsers.add_parser("menu", help="Get venue menu")
    menu_parser.add_argument("venue_id", help="Venue ID")
    menu_parser.add_argument("--section", help="Filter by section name")
    menu_parser.add_argument("--search", help="Search menu items")
    menu_parser.add_argument("--min-price", type=float, help="Minimum price")
    menu_parser.add_argument("--max-price", type=float, help="Maximum price")
    menu_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # info
    info_parser = subparsers.add_parser("info", help="Get venue details")
    info_parser.add_argument("venue_id", help="Venue ID")
    info_parser.add_argument("--locale", choices=["en", "he"], default="en", help="Language")
    info_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # url
    url_parser = subparsers.add_parser("url", help="Get booking URL")
    url_parser.add_argument("venue_id", help="Venue ID")
    url_parser.add_argument("--locale", choices=["en", "he"], default="en", help="Language")
    url_parser.add_argument("--json", action="store_true", help="Output as JSON")

    return parser


async def main_async(args: argparse.Namespace) -> int:
    """Main async entry point."""
    locale = getattr(args, "locale", "en")
    json_output = getattr(args, "json", False)

    async with OntopoClient(locale=locale) as client:
        handler = CommandHandler(client, json_output=json_output)

        try:
            if args.command == "cities":
                await handler.cmd_cities()

            elif args.command == "categories":
                await handler.cmd_categories()

            elif args.command == "search":
                await handler.cmd_search(args.query, args.city)

            elif args.command == "available":
                await handler.cmd_available(
                    args.date, args.time, args.city, args.party_size
                )

            elif args.command == "check":
                await handler.cmd_check(
                    args.venue_id, args.date, args.time, args.party_size
                )

            elif args.command == "range":
                await handler.cmd_range(
                    args.venue_id, args.start_date, args.end_date,
                    args.times, args.party_size
                )

            elif args.command == "menu":
                await handler.cmd_menu(
                    args.venue_id, args.section, args.search,
                    args.min_price, args.max_price
                )

            elif args.command == "info":
                await handler.cmd_info(args.venue_id)

            elif args.command == "url":
                await handler.cmd_url(args.venue_id)

            else:
                return 1

            return 0

        except ValueError as e:
            if json_output:
                print(json.dumps({"error": str(e)}))
            else:
                print(f"Error: {e}", file=sys.stderr)
            return 1

        except RuntimeError as e:
            if json_output:
                print(json.dumps({"error": str(e)}))
            else:
                print(f"Error: {e}", file=sys.stderr)
            return 1


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
