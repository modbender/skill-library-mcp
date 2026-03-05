#!/usr/bin/env python3
"""
Location / Travel Mapper: analyze where your photos were taken.
Cluster GPS coordinates into locations, identify trips, find most-photographed places.
"""

import math
import sys
from collections import defaultdict
from typing import Any, Optional

from _common import PhotosDB, coredata_to_datetime, format_size, run_script, validate_year

# ---------------------------------------------------------------------------
# Offline reverse geocoding: maps lat/lon to approximate place names using
# a small set of well-known cities / regions worldwide.  Each entry is
#   (lat, lon, name, country)
# We find the nearest city within a threshold distance.
# ---------------------------------------------------------------------------
KNOWN_PLACES: list[tuple[float, float, str, str]] = [
    # North America
    (40.7128, -74.0060, "New York", "US"),
    (34.0522, -118.2437, "Los Angeles", "US"),
    (41.8781, -87.6298, "Chicago", "US"),
    (29.7604, -95.3698, "Houston", "US"),
    (33.4484, -112.0740, "Phoenix", "US"),
    (29.4241, -98.4936, "San Antonio", "US"),
    (32.7157, -117.1611, "San Diego", "US"),
    (32.7767, -96.7970, "Dallas", "US"),
    (37.7749, -122.4194, "San Francisco", "US"),
    (47.6062, -122.3321, "Seattle", "US"),
    (39.7392, -104.9903, "Denver", "US"),
    (25.7617, -80.1918, "Miami", "US"),
    (33.7490, -84.3880, "Atlanta", "US"),
    (42.3601, -71.0589, "Boston", "US"),
    (38.9072, -77.0369, "Washington DC", "US"),
    (36.1627, -86.7816, "Nashville", "US"),
    (30.2672, -97.7431, "Austin", "US"),
    (36.1699, -115.1398, "Las Vegas", "US"),
    (45.5152, -122.6784, "Portland", "US"),
    (35.2271, -80.8431, "Charlotte", "US"),
    (21.3069, -157.8583, "Honolulu", "US"),
    (43.6532, -79.3832, "Toronto", "CA"),
    (45.5017, -73.5673, "Montreal", "CA"),
    (49.2827, -123.1207, "Vancouver", "CA"),
    (19.4326, -99.1332, "Mexico City", "MX"),
    (20.6597, -103.3496, "Guadalajara", "MX"),
    (25.6866, -100.3161, "Monterrey", "MX"),
    # Europe
    (51.5074, -0.1278, "London", "GB"),
    (48.8566, 2.3522, "Paris", "FR"),
    (52.5200, 13.4050, "Berlin", "DE"),
    (48.1351, 11.5820, "Munich", "DE"),
    (50.1109, 8.6821, "Frankfurt", "DE"),
    (41.9028, 12.4964, "Rome", "IT"),
    (45.4642, 9.1900, "Milan", "IT"),
    (43.7696, 11.2558, "Florence", "IT"),
    (40.4168, -3.7038, "Madrid", "ES"),
    (41.3874, 2.1686, "Barcelona", "ES"),
    (52.3676, 4.9041, "Amsterdam", "NL"),
    (50.8503, 4.3517, "Brussels", "BE"),
    (47.3769, 8.5417, "Zurich", "CH"),
    (46.2044, 6.1432, "Geneva", "CH"),
    (48.2082, 16.3738, "Vienna", "AT"),
    (50.0755, 14.4378, "Prague", "CZ"),
    (52.2297, 21.0122, "Warsaw", "PL"),
    (47.4979, 19.0402, "Budapest", "HU"),
    (59.3293, 18.0686, "Stockholm", "SE"),
    (60.1699, 24.9384, "Helsinki", "FI"),
    (55.6761, 12.5683, "Copenhagen", "DK"),
    (59.9139, 10.7522, "Oslo", "NO"),
    (38.7223, -9.1393, "Lisbon", "PT"),
    (37.9838, 23.7275, "Athens", "GR"),
    (41.0082, 28.9784, "Istanbul", "TR"),
    (55.7558, 37.6173, "Moscow", "RU"),
    (59.9311, 30.3609, "St Petersburg", "RU"),
    (53.3498, -6.2603, "Dublin", "IE"),
    (55.9533, -3.1883, "Edinburgh", "GB"),
    # Asia
    (35.6762, 139.6503, "Tokyo", "JP"),
    (34.6937, 135.5023, "Osaka", "JP"),
    (35.0116, 135.7681, "Kyoto", "JP"),
    (37.5665, 126.9780, "Seoul", "KR"),
    (31.2304, 121.4737, "Shanghai", "CN"),
    (39.9042, 116.4074, "Beijing", "CN"),
    (22.3193, 114.1694, "Hong Kong", "HK"),
    (22.5431, 114.0579, "Shenzhen", "CN"),
    (23.1291, 113.2644, "Guangzhou", "CN"),
    (25.0330, 121.5654, "Taipei", "TW"),
    (1.3521, 103.8198, "Singapore", "SG"),
    (13.7563, 100.5018, "Bangkok", "TH"),
    (14.5995, 120.9842, "Manila", "PH"),
    (21.0278, 105.8342, "Hanoi", "VN"),
    (10.8231, 106.6297, "Ho Chi Minh City", "VN"),
    (3.1390, 101.6869, "Kuala Lumpur", "MY"),
    (-6.2088, 106.8456, "Jakarta", "ID"),
    (28.6139, 77.2090, "New Delhi", "IN"),
    (19.0760, 72.8777, "Mumbai", "IN"),
    (12.9716, 77.5946, "Bangalore", "IN"),
    (25.2048, 55.2708, "Dubai", "AE"),
    (24.7136, 46.6753, "Riyadh", "SA"),
    (31.7683, 35.2137, "Jerusalem", "IL"),
    (32.0853, 34.7818, "Tel Aviv", "IL"),
    # Oceania
    (-33.8688, 151.2093, "Sydney", "AU"),
    (-37.8136, 144.9631, "Melbourne", "AU"),
    (-27.4698, 153.0251, "Brisbane", "AU"),
    (-36.8485, 174.7633, "Auckland", "NZ"),
    # South America
    (-23.5505, -46.6333, "São Paulo", "BR"),
    (-22.9068, -43.1729, "Rio de Janeiro", "BR"),
    (-34.6037, -58.3816, "Buenos Aires", "AR"),
    (-33.4489, -70.6693, "Santiago", "CL"),
    (-12.0464, -77.0428, "Lima", "PE"),
    (4.7110, -74.0721, "Bogota", "CO"),
    # Africa
    (30.0444, 31.2357, "Cairo", "EG"),
    (-33.9249, 18.4241, "Cape Town", "ZA"),
    (-1.2921, 36.8219, "Nairobi", "KE"),
    (6.5244, 3.3792, "Lagos", "NG"),
    (33.5731, -7.5898, "Casablanca", "MA"),
]

# Match threshold: max distance in km to assign a place name
REVERSE_GEO_THRESHOLD_KM = 50


def reverse_geocode(lat: float, lon: float) -> Optional[str]:
    """
    Offline reverse geocode: return "City, Country" for a coordinate,
    or None if no known place is within the threshold distance.
    """
    best_dist = float("inf")
    best_name = None
    for plat, plon, city, country in KNOWN_PLACES:
        dist = haversine_km(lat, lon, plat, plon)
        if dist < best_dist:
            best_dist = dist
            best_name = f"{city}, {country}"
    if best_dist <= REVERSE_GEO_THRESHOLD_KM:
        return best_name
    return None


# Haversine distance in km
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS coordinates in kilometers."""
    r = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def cluster_locations(
    photos: list[dict[str, Any]],
    radius_km: float = 1.0,
) -> list[dict[str, Any]]:
    """
    Cluster photos by GPS proximity using simple greedy clustering.

    Args:
        photos: List of photo dicts with latitude/longitude
        radius_km: Cluster radius in km

    Returns:
        List of location clusters
    """
    unassigned = list(range(len(photos)))
    clusters = []

    while unassigned:
        # Pick the first unassigned photo as seed
        seed_idx = unassigned[0]
        seed = photos[seed_idx]
        cluster_indices = [seed_idx]
        remaining = []

        for idx in unassigned[1:]:
            p = photos[idx]
            dist = haversine_km(seed["latitude"], seed["longitude"], p["latitude"], p["longitude"])
            if dist <= radius_km:
                cluster_indices.append(idx)
            else:
                remaining.append(idx)

        # Compute cluster centroid
        cluster_photos = [photos[i] for i in cluster_indices]
        avg_lat = sum(p["latitude"] for p in cluster_photos) / len(cluster_photos)
        avg_lon = sum(p["longitude"] for p in cluster_photos) / len(cluster_photos)

        clusters.append(
            {
                "centroid_lat": round(avg_lat, 4),
                "centroid_lon": round(avg_lon, 4),
                "photo_count": len(cluster_photos),
                "photos": cluster_photos,
            }
        )

        unassigned = remaining

    return clusters


def analyze_locations(
    db_path: Optional[str] = None,
    cluster_radius_km: float = 1.0,
    year: Optional[str] = None,
    min_photos: int = 3,
) -> dict[str, Any]:
    """
    Analyze photo locations and identify trips/places.

    Args:
        db_path: Path to database
        cluster_radius_km: Radius in km for clustering nearby photos
        year: Filter to specific year
        min_photos: Minimum photos to include a location cluster

    Returns:
        Location analysis dictionary
    """
    with PhotosDB(db_path) as conn:
        cursor = conn.cursor()

        where_clauses = [
            "a.ZTRASHEDSTATE != 1",
            "a.ZLATITUDE IS NOT NULL",
            "a.ZLONGITUDE IS NOT NULL",
            "a.ZLATITUDE != 0",
            "a.ZLONGITUDE != 0",
        ]
        params: list = []

        if year:
            year = validate_year(year)
            where_clauses.append("strftime('%Y', datetime(a.ZDATECREATED + 978307200, 'unixepoch')) = ?")
            params.append(year)

        query = f"""
            SELECT
                a.Z_PK,
                a.ZFILENAME,
                a.ZDATECREATED,
                a.ZKIND,
                a.ZLATITUDE,
                a.ZLONGITUDE,
                a.ZFAVORITE,
                aa.ZORIGINALFILESIZE
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            WHERE {" AND ".join(where_clauses)}
            ORDER BY a.ZDATECREATED
        """

        cursor.execute(query, params)

        photos_with_location = []
        total_assets = 0

        for row in cursor.fetchall():
            created = coredata_to_datetime(row["ZDATECREATED"])
            photos_with_location.append(
                {
                    "id": row["Z_PK"],
                    "filename": row["ZFILENAME"],
                    "created": created.isoformat() if created else None,
                    "created_dt": created,
                    "latitude": row["ZLATITUDE"],
                    "longitude": row["ZLONGITUDE"],
                    "kind": "photo" if row["ZKIND"] == 0 else "video",
                    "is_favorite": bool(row["ZFAVORITE"]),
                    "size": row["ZORIGINALFILESIZE"] or 0,
                }
            )
            total_assets += 1

        # Count total assets (with and without location)
        cursor.execute("""
            SELECT COUNT(*) as total FROM ZASSET WHERE ZTRASHEDSTATE != 1
        """)
        total_all = cursor.fetchone()["total"]
        without_location = total_all - total_assets

        # Cluster locations
        clusters = cluster_locations(photos_with_location, cluster_radius_km)

        # Filter to significant clusters and enrich
        locations = []
        for cluster in clusters:
            if cluster["photo_count"] < min_photos:
                continue

            cluster_photos = cluster["photos"]

            # Date range
            dates = [p["created_dt"] for p in cluster_photos if p["created_dt"]]
            first = min(dates) if dates else None
            last = max(dates) if dates else None

            # Count by year-month
            by_month = defaultdict(int)
            for p in cluster_photos:
                if p["created_dt"]:
                    key = p["created_dt"].strftime("%Y-%m")
                    by_month[key] += 1

            # Identify potential trips (>= 5 photos, spanning multiple hours)
            is_trip = False
            if first and last and len(cluster_photos) >= 5:
                duration_hours = (last - first).total_seconds() / 3600
                is_trip = duration_hours >= 4

            favorites = sum(1 for p in cluster_photos if p["is_favorite"])
            total_size = sum(p["size"] for p in cluster_photos)

            # Get people at this location
            photo_ids = [p["id"] for p in cluster_photos]
            people_at_location = []
            if photo_ids:
                placeholders = ",".join("?" * len(photo_ids))
                cursor.execute(
                    f"""
                    SELECT DISTINCT p.ZFULLNAME, COUNT(df.ZASSET) as count
                    FROM ZPERSON p
                    JOIN ZDETECTEDFACE df ON p.Z_PK = df.ZPERSON
                    WHERE df.ZASSET IN ({placeholders})
                    AND p.ZFULLNAME IS NOT NULL AND p.ZFULLNAME != ''
                    GROUP BY p.Z_PK
                    ORDER BY count DESC
                    LIMIT 5
                """,
                    photo_ids,
                )
                people_at_location = [{"name": row["ZFULLNAME"], "count": row["count"]} for row in cursor.fetchall()]

            place_name = reverse_geocode(cluster["centroid_lat"], cluster["centroid_lon"])

            locations.append(
                {
                    "centroid_lat": cluster["centroid_lat"],
                    "centroid_lon": cluster["centroid_lon"],
                    "place_name": place_name,
                    "photo_count": cluster["photo_count"],
                    "favorites": favorites,
                    "total_size": total_size,
                    "total_size_formatted": format_size(total_size),
                    "first_photo": first.isoformat() if first else None,
                    "last_photo": last.isoformat() if last else None,
                    "is_trip": is_trip,
                    "by_month": dict(sorted(by_month.items())),
                    "people": people_at_location,
                }
            )

        # Sort by photo count
        locations.sort(key=lambda x: x["photo_count"], reverse=True)

        # Travel timeline: identify distinct trips (clusters of photos far from "home")
        trips = [loc for loc in locations if loc["is_trip"]]

        return {
            "locations": locations,
            "trips": trips,
            "summary": {
                "total_with_location": total_assets,
                "total_without_location": without_location,
                "location_coverage": round(total_assets / total_all * 100, 1) if total_all else 0,
                "unique_locations": len(locations),
                "identified_trips": len(trips),
                "cluster_radius_km": cluster_radius_km,
            },
        }


def format_summary(data: dict[str, Any]) -> str:
    """Format location analysis as human-readable summary."""
    lines = []
    lines.append("📍 LOCATION / TRAVEL MAPPER")
    lines.append("=" * 50)
    lines.append("")

    summary = data["summary"]
    lines.append(f"Photos with GPS: {summary['total_with_location']:,} ({summary['location_coverage']}%)")
    lines.append(f"Without GPS: {summary['total_without_location']:,}")
    lines.append(f"Unique locations: {summary['unique_locations']:,}")
    lines.append(f"Possible trips: {summary['identified_trips']:,}")
    lines.append("")

    lines.append("Top Locations:")
    for i, loc in enumerate(data["locations"][:15], 1):
        trip_flag = " 🧳" if loc["is_trip"] else ""
        fav_str = f" ⭐{loc['favorites']}" if loc["favorites"] else ""
        place = loc.get("place_name") or f"({loc['centroid_lat']}, {loc['centroid_lon']})"
        lines.append(f"  {i:>3}. {place}")
        lines.append(f"       {loc['photo_count']:,} photos{fav_str}{trip_flag} | {loc['total_size_formatted']}")

        if loc["first_photo"] and loc["last_photo"]:
            lines.append(f"       📅 {loc['first_photo'][:10]} → {loc['last_photo'][:10]}")

        if loc["people"]:
            names = ", ".join(p["name"] for p in loc["people"][:3])
            lines.append(f"       👥 {names}")

    lines.append("")

    if data["trips"]:
        lines.append("Identified Trips:")
        for trip in data["trips"][:10]:
            place = trip.get("place_name") or f"({trip['centroid_lat']}, {trip['centroid_lon']})"
            lines.append(f"  🧳 {place}")
            lines.append(f"     {trip['photo_count']} photos, {trip['first_photo'][:10]} → {trip['last_photo'][:10]}")
        lines.append("")

    return "\n".join(lines)


def main():
    def add_args(parser):
        parser.add_argument("--radius", type=float, default=1.0, help="Cluster radius in km (default: 1.0)")
        parser.add_argument("--year", help="Filter to specific year (YYYY)")
        parser.add_argument(
            "--min-photos", type=int, default=3, help="Minimum photos per location cluster (default: 3)"
        )

    def invoke(db_path, args):
        return analyze_locations(
            db_path=db_path,
            cluster_radius_km=args.radius,
            year=args.year,
            min_photos=args.min_photos,
        )

    return run_script(
        description="Analyze photo locations and identify trips",
        analyze_fn=invoke,
        format_fn=format_summary,
        extra_args_fn=add_args,
        epilog="""
Examples:
  %(prog)s --human
  %(prog)s --radius 2.0 --year 2025
  %(prog)s --min-photos 10 --output locations.json
        """,
    )


if __name__ == "__main__":
    sys.exit(main())
