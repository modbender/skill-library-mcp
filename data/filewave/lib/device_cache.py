#!/usr/bin/env python3
"""
Device ID/Details Cache for FileWave Skill

Maps device names → id → device_id for efficient lookups.
Caches are time-limited (1 week) and cleared on errors.

Optimization history:
- v1.0: Name-based cache only (server:name → device info)
- v1.1: Added ID-based secondary index (server:id:NNN → same entry)
        Added parallel detail lookups via ThreadPoolExecutor
        Added preload_devices() to warm cache from smart groups
"""

import json
import os
import requests
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from api_utils import normalize_server_url, create_filewave_session, safe_api_request


class DeviceCache:
    """In-memory cache of device relationships."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".filewave" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_file = self.cache_dir / "device_relationships.json"
        self.max_age_days = 7
        
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from disk, clearing if expired."""
        if not self.cache_file.exists():
            return {"entries": {}, "created": datetime.now(timezone.utc).isoformat()}
        
        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)
            
            # Check age
            created = datetime.fromisoformat(data.get("created", "2000-01-01"))
            age = datetime.now(timezone.utc) - created
            
            if age > timedelta(days=self.max_age_days):
                print(f"Cache expired ({age.days} days old), clearing", file=sys.stderr)
                return {"entries": {}, "created": datetime.now(timezone.utc).isoformat()}
            
            return data
        except Exception as e:
            print(f"Cache load error: {e}, starting fresh", file=sys.stderr)
            return {"entries": {}, "created": datetime.now(timezone.utc).isoformat()}
    
    def _save_cache(self):
        """Save cache to disk with secure permissions."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
            # Set secure permissions (user read/write only)
            os.chmod(self.cache_file, 0o600)
        except Exception as e:
            print(f"Cache save error: {e}", file=sys.stderr)
    
    def get_device_id_by_name(self, device_name: str, server: str) -> Optional[str]:
        """Get device_id for a device by name."""
        key = f"{server}:{device_name}"
        entry = self.cache["entries"].get(key)
        
        if entry:
            return entry.get("device_id")
        
        return None
    
    def get_device_by_id(self, device_id: int, server: str) -> Optional[Dict]:
        """Get cached device info by its numeric ID."""
        key = f"{server}:id:{device_id}"
        return self.cache["entries"].get(key)

    def add_device(self, server: str, device_name: str, device_id: int, device_uid: str, info: Dict = None):
        """
        Add device mapping to cache.
        
        Args:
            server: Server URL or hostname
            device_name: Device name
            device_id: Numeric ID from /api/devices/v1/devices/{id} 
            device_uid: UUID device_id (for API calls)
            info: Optional dict with additional info (groups, is_clone, etc.)
        """
        # Maintain two entries for each device: one by name (human UX), one by ID (API calls)
        entry = {
            "id": device_id,
            "device_id": device_uid,
            "name": device_name,
            "server": server,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "info": info or {}
        }
        
        # Primary key: name (server:name)
        self.cache["entries"][f"{server}:{device_name}"] = entry
        
        # Secondary index: ID (server:id:123)
        self.cache["entries"][f"{server}:id:{device_id}"] = entry
        
        self._save_cache()
    
    def get_device_info(self, server: str, device_name: str) -> Optional[Dict]:
        """Get cached device info (groups, is_clone, etc.)"""
        key = f"{server}:{device_name}"
        entry = self.cache["entries"].get(key)
        
        if entry:
            return entry.get("info", {})
        
        return None
    
    def clear_on_error(self):
        """Clear cache if API errors detected."""
        print("Clearing device cache due to API error", file=sys.stderr)
        self.cache = {"entries": {}, "created": datetime.now(timezone.utc).isoformat()}
        self._save_cache()
    
    def list_cached_devices(self, server: Optional[str] = None) -> Dict[str, Dict]:
        """List all cached devices, optionally filtered by server."""
        result = {}
        
        for key, entry in self.cache["entries"].items():
            if server and not key.startswith(f"{server}:"):
                continue
            result[key] = entry
        
        return result
    
    def stats(self) -> Dict[str, Any]:
        """Cache statistics."""
        created = datetime.fromisoformat(self.cache.get("created", "2000-01-01"))
        age = datetime.now(timezone.utc) - created
        
        return {
            "entries": len(self.cache["entries"]),
            "created": created.isoformat(),
            "age_days": age.days,
            "max_age_days": self.max_age_days,
            "expired": age > timedelta(days=self.max_age_days)
        }


class DeviceLookup:
    """Lookup device info from FileWave API, using cache for speed."""
    
    def __init__(self, server: str, token: str, cache: Optional[DeviceCache] = None):
        self.server = normalize_server_url(server)
        self.token = token
        self.cache = cache or DeviceCache()
        self.session = create_filewave_session(token)
    
    def search_device(self, search_term: str) -> Optional[Dict[str, Any]]:
        """
        Search for device using cache or /api/search/v1/global
        """
        # 1. Try cache by name
        key_name = f"{self.server}:{search_term}"
        if key_name in self.cache.cache["entries"]:
            entry = self.cache.cache["entries"][key_name]
            return self._format_search_entry(entry, True)
            
        # 2. Try cache by numeric ID (if search term is numeric)
        if search_term.isdigit():
            key_id = f"{self.server}:id:{search_term}"
            if key_id in self.cache.cache["entries"]:
                entry = self.cache.cache["entries"][key_id]
                return self._format_search_entry(entry, True)
        
        # 3. Fallback: API Search
        url = f"{self.server}/api/search/v1/global"
        params = {"query": search_term, "limit": 12}
        
        success, data = safe_api_request(
            self.session, "get", url,
            on_error_callback=self.cache.clear_on_error,
            params=params
        )
        
        if not success or not data: return None
        
        if data and len(data) > 0:
            result_group = data[0]
            entries = result_group.get("entries", [])
            
            if entries:
                device = entries[0]
                device_id = device.get("id")
                
                # Check cache by ID first (avoids detail lookup)
                cached_id = self.cache.get_device_by_id(device_id, self.server)
                if cached_id:
                    return self._format_search_entry(cached_id, True)

                details = self._get_device_details(device_id)
                if details:
                    # Cache it
                    self.cache.add_device(
                        self.server,
                        device.get("name", search_term),
                        device_id,
                        details.get("device_id"),
                        {"is_clone": details.get("is_clone", False)}
                    )
                    
                    return {
                        "id": device_id,
                        "device_id": details.get("device_id"),
                        "name": device.get("name", search_term),
                        "is_clone": details.get("is_clone", False),
                        "from_cache": False
                    }
        return None

    def _format_search_entry(self, entry: Dict, from_cache: bool = True) -> Dict:
        """Helper to format a cache entry for the search return type."""
        return {
            "id": entry["id"],
            "device_id": entry["device_id"],
            "name": entry["name"],
            "is_clone": entry["info"].get("is_clone", False),
            "is_online": None,
            "from_cache": from_cache
        }

    
    def _get_device_details(self, device_id: int) -> Optional[Dict[str, Any]]:
        """Get full device details from /api/devices/v1/devices/{id}"""
        url = f"{self.server}/api/devices/v1/devices/{device_id}"
        success, data = safe_api_request(
            self.session,
            "get",
            url,
            on_error_callback=self.cache.clear_on_error
        )
        return data if success else None
    
    def search_devices(self, search_term: str, limit: int = 50) -> list:
        """
        Search for ALL matching devices using /api/search/v1/global.
        
        Optimized v1.1: Uses ThreadPoolExecutor to parallelize detail lookups
        and checks ID-based cache to avoid redundant API calls.
        """
        url = f"{self.server}/api/search/v1/global"
        params = {"query": search_term, "limit": limit}
        
        success, data = safe_api_request(
            self.session, "get", url,
            on_error_callback=self.cache.clear_on_error,
            params=params
        )
        
        if not success or not data: return []
        
        ids_to_fetch = []
        results = []
        
        # 1. Gather device IDs from search results
        for result_group in data:
            if result_group.get("type") != "client":
                continue
            for device in result_group.get("entries", []):
                device_id = device.get("id")
                # Check cache by ID first
                cached = self.cache.get_device_by_id(device_id, self.server)
                if cached:
                    results.append({
                        "id": device_id,
                        "device_id": cached["device_id"],
                        "name": cached["name"],
                        "client_type": cached["info"].get("client_type"),
                        "is_clone": cached["info"].get("is_clone", False),
                        "serial": cached["info"].get("serial"),
                        "last_connected": cached["info"].get("last_connected"),
                        "from_cache": True
                    })
                else:
                    ids_to_fetch.append(device_id)
        
        # 2. Parallel fetch for missing detail lookups
        if ids_to_fetch:
            # Use max 8 workers to avoid slamming the server too hard
            with ThreadPoolExecutor(max_workers=8) as executor:
                future_to_id = {executor.submit(self._get_device_details, did): did for did in ids_to_fetch}
                for future in as_completed(future_to_id):
                    did = future_to_id[future]
                    details = future.result()
                    if details:
                        entry = {
                            "id": did,
                            "device_id": details.get("device_id"),
                            "name": details.get("name", ""),
                            "client_type": details.get("client_type"),
                            "is_clone": details.get("is_clone", False),
                            "serial": details.get("serial_or_mac"),
                            "last_connected": details.get("last_connected"),
                            "from_cache": False
                        }
                        results.append(entry)
                        # Warm the cache
                        self.cache.add_device(
                            self.server, entry["name"], did, entry["device_id"],
                            {"is_clone": entry["is_clone"], "serial": entry["serial"], 
                             "client_type": entry["client_type"], "last_connected": entry["last_connected"]}
                        )
        
        return results

    
    def get_device_hardware(self, device_id: int) -> Dict[str, Any]:
        """
        Get hardware details for a device.
        
        Returns dict with device_product_name, product, model, etc.
        Uses /api/devices/internal/devices/{id}/details/hardware/fields
        """
        url = f"{self.server}/api/devices/internal/devices/{device_id}/details/hardware/fields"
        success, data = safe_api_request(
            self.session,
            "get",
            url,
            on_error_callback=self.cache.clear_on_error
        )
        
        if not success or not data:
            return {}
        
        hw = {}
        for field_group in data.get("fields", []):
            for f in field_group:
                name = f.get("name", "")
                value = f.get("value")
                if name in ("device_product_name", "product", "product_name", "model",
                            "cpu_type", "ram_size", "total_disk_space", "free_disk_space"):
                    hw[name] = value
                    if f.get("display_value"):
                        hw[f"{name}_display"] = f["display_value"]
        
        return hw
    
    # ── Internal Devices API ──────────────────────────────────────────
    # Uses /filewave/api/devices/internal/devices (same as FileWave Anywhere web admin).
    # Returns rich field data via search_fields parameter.
    # Requires parent_id to drill into groups; without it returns root groups.
    # Pagination: limit (max 1000) + offset.

    # Default fields to request from the internal devices API
    INTERNAL_SEARCH_FIELDS = (
        "name,serial_or_mac_address,os_name,model_version,"
        "invf_Client_device_product_name,invf_Client_device_name,"
        "invf_Client_current_ip_address,invf_Client_last_check_in,"
        "invf_Client_serial_number,invf_Client_free_disk_space,"
        "invf_Client_total_disk_space,invf_Client_auth_username"
    )

    def _internal_devices_list(self, parent_id: Optional[int] = None,
                                search_fields: Optional[str] = None,
                                limit: int = 1000, offset: int = 0) -> Optional[Dict]:
        """
        Query /filewave/api/devices/internal/devices with optional parent_id.
        
        Returns raw API response dict with 'count', 'next', 'previous', 'results'.
        Results include both groups (is_group=True) and devices (is_group=False).
        """
        url = f"{self.server}/filewave/api/devices/internal/devices"
        params = {
            "limit": min(limit, 1000),
            "offset": offset,
            "search_fields": search_fields or self.INTERNAL_SEARCH_FIELDS,
        }
        if parent_id is not None:
            params["parent_id"] = parent_id
        
        success, data = safe_api_request(
            self.session, "get", url,
            on_error_callback=self.cache.clear_on_error,
            params=params
        )
        return data if success else None

    def _get_root_groups(self) -> List[Dict]:
        """Get all root-level groups with metadata."""
        data = self._internal_devices_list()
        if not data:
            return []
        
        groups = []
        for item in data.get("results", []):
            if not item.get("is_group"):
                continue
            name_obj = item.get("name", {})
            groups.append({
                "id": item["id"],
                "name": name_obj.get("value", "") if isinstance(name_obj, dict) else str(name_obj),
                "group_type": name_obj.get("group_type", "") if isinstance(name_obj, dict) else "",
                "has_children": item.get("has_children", False),
            })
        return groups

    def _find_smart_group(self, target_names: List[str]) -> Optional[int]:
        """
        Find a smart group by name from root groups.
        
        Args:
            target_names: List of acceptable group names (e.g., ["All iOS"])
        
        Returns:
            Group ID if found, None otherwise.
        """
        for group in self._get_root_groups():
            if group["group_type"] == "smart" and group["name"] in target_names and group["has_children"]:
                return group["id"]
        return None

    def _collect_devices_from_group(self, group_id: int,
                                     search_fields: Optional[str] = None) -> List[Dict]:
        """
        Get all devices from a group using the internal devices API.
        Handles pagination (limit 1000 per page).
        Returns only non-group items (actual devices).
        """
        devices = []
        offset = 0
        
        while True:
            data = self._internal_devices_list(
                parent_id=group_id,
                search_fields=search_fields,
                offset=offset
            )
            if not data:
                break
            
            results = data.get("results", [])
            for item in results:
                if not item.get("is_group"):
                    devices.append(self._normalize_internal_device(item))
            
            # Check pagination
            if data.get("next"):
                offset += len(results)
            else:
                break
        
        return devices

    def _collect_devices_recursive(self, parent_id: Optional[int] = None,
                                    max_depth: int = 5, _depth: int = 0) -> List[Dict]:
        """
        Recursively collect all devices from a group hierarchy.
        
        Used as fallback when smart groups don't exist (fresh servers).
        Depth-limited to prevent runaway on very deep hierarchies.
        """
        if _depth >= max_depth:
            print(f"Warning: max depth {max_depth} reached, stopping recursion", file=sys.stderr)
            return []
        
        data = self._internal_devices_list(parent_id=parent_id)
        if not data:
            return []
        
        devices = []
        for item in data.get("results", []):
            if item.get("is_group"):
                if item.get("has_children"):
                    # Recurse into subgroups
                    sub_devices = self._collect_devices_recursive(
                        parent_id=item["id"],
                        max_depth=max_depth,
                        _depth=_depth + 1
                    )
                    devices.extend(sub_devices)
            else:
                devices.append(self._normalize_internal_device(item))
        
        return devices

    @staticmethod
    def _normalize_internal_device(item: Dict) -> Dict:
        """Normalize a device record from the internal devices API into a clean dict."""
        name_obj = item.get("name", {})
        os_obj = item.get("os_name", {})
        
        return {
            "id": item.get("id"),
            "device_id": item.get("device_id", ""),  # UUID for API calls
            "name": name_obj.get("value", "") if isinstance(name_obj, dict) else str(name_obj),
            "clone_id": item.get("clone_id"),
            "serial": item.get("serial_or_mac_address", ""),
            "is_clone": item.get("clone_id") is not None,
            "os_name": os_obj.get("display_value", "") if isinstance(os_obj, dict) else str(os_obj),
            "os_type": os_obj.get("os_type", "") if isinstance(os_obj, dict) else "",
            "product_name": item.get("invf_Client_device_product_name", ""),
            "device_name": item.get("invf_Client_device_name", ""),
            "model_version": item.get("model_version", ""),
            "ip_address": item.get("invf_Client_current_ip_address", ""),
            "last_check_in": item.get("invf_Client_last_check_in", ""),
            "last_connected": item.get("last_connected", ""),
            "serial_number": item.get("invf_Client_serial_number", ""),
            "free_disk_space": item.get("invf_Client_free_disk_space", ""),
            "total_disk_space": item.get("invf_Client_total_disk_space", ""),
            "auth_username": item.get("invf_Client_auth_username", ""),
            "groups": item.get("groups", ""),
        }

    # ── Device Type Mapping ─────────────────────────────────────────
    # Maps device type queries to the smart groups most likely to contain them.
    DEVICE_TYPE_SMART_GROUPS = {
        "ipad":    ["All iOS"],
        "iphone":  ["All iOS"],
        "ipod":    ["All iOS"],
        "ios":     ["All iOS"],
        "mac":     ["All macOS"],
        "macbook": ["All macOS"],
        "imac":    ["All macOS"],
        "windows": ["All Windows"],
        "android": ["All Android"],
        "chromebook": ["Chromebooks"],
    }

    def find_devices_by_type(self, device_type: str) -> List[Dict]:
        """
        Find all devices matching a product type (iPad, iPhone, Mac, etc.).
        
        Strategy (two-pass, works on any server):
          1. FAST PATH: Look for known smart groups (e.g., "All iOS" for iPad).
             If found, query that group — returns all matching devices in 1-2 API calls.
          2. FALLBACK: If no smart group exists (fresh server), recursively traverse
             all groups from root, collecting every device, then filter by product_name.
        
        Deduplicates by device ID. Filtering uses invf_Client_device_product_name
        which is the authoritative hardware identifier (e.g., "iPad", "iPhone", "Mac13,1").
        
        Args:
            device_type: Product type to search for (e.g., "iPad", "iPhone", "Mac")
        
        Returns:
            List of device dicts with full details from internal API.
        """
        device_type_lower = device_type.lower()
        seen_ids = set()
        results = []
        
        def _matches_type(product_name: str) -> bool:
            """Check if a device's product_name matches the requested type."""
            pn = (product_name or "").lower()
            if not pn:
                return False
            # Exact match for specific types
            if device_type_lower in ("ipad", "iphone", "ipod"):
                return pn == device_type_lower
            # Prefix match for broader types (e.g., "mac" matches "Mac13,1", "MacBookPro12,1")
            if device_type_lower in ("mac", "macbook", "imac"):
                return pn.startswith(device_type_lower)
            # For "ios", "android", "windows" — match by os_type instead
            if device_type_lower in ("ios", "android", "windows", "chromebook"):
                return True  # Already filtered by smart group
            # Generic: substring match
            return device_type_lower in pn
        
        def _add_device(dev: Dict):
            """Add device to results if it matches and hasn't been seen."""
            dev_id = dev.get("id")
            if dev_id in seen_ids:
                return
            seen_ids.add(dev_id)
            
            # For OS-type queries (ios, android, windows), don't filter by product_name
            if device_type_lower in ("ios", "android", "windows", "chromebook"):
                results.append(dev)
            elif _matches_type(dev.get("product_name", "")):
                results.append(dev)
        
        # ── Fast path: Smart group lookup ──
        target_groups = self.DEVICE_TYPE_SMART_GROUPS.get(device_type_lower, [])
        group_id = self._find_smart_group(target_groups) if target_groups else None
        
        if group_id:
            print(f"Using smart group (id={group_id}) for fast lookup...", file=sys.stderr)
            devices = self._collect_devices_from_group(group_id)
            for dev in devices:
                _add_device(dev)
        
        # ── Fallback: Recursive traversal from root ──
        if not results and not group_id:
            print("No smart group found. Scanning all groups (this may take a moment)...", file=sys.stderr)
            all_devices = self._collect_devices_recursive()
            for dev in all_devices:
                _add_device(dev)
        
        # ── Supplement: Global search by name (catches edge cases) ──
        name_results = self.search_devices(device_type, limit=50)
        for dev in name_results:
            if dev["id"] not in seen_ids:
                # Need to get internal details for this device
                hw = self.get_device_hardware(dev["id"])
                product_name = hw.get("device_product_name", "")
                if _matches_type(product_name):
                    dev["product_name"] = product_name
                    dev["product_model"] = hw.get("product", "")
                    dev["hardware"] = hw
                    seen_ids.add(dev["id"])
                    results.append(dev)
        
        return results
    
    def preload_devices(self, parallel: bool = True) -> int:
        """
        Warms the cache by fetching all devices from known smart groups.
        Uses ThreadPoolExecutor to fetch platforms in parallel.
        
        Returns count of devices cached.
        """
        platform_groups = [
            ["All macOS"], ["All iOS"], ["All Windows"], 
            ["All Android"], ["Chromebooks"]
        ]
        
        # 1. Discover group IDs
        print(f"Discovering smart groups on {self.server}...", file=sys.stderr)
        group_ids = []
        for targets in platform_groups:
            gid = self._find_smart_group(targets)
            if gid:
                group_ids.append((gid, targets[0]))
        
        if not group_ids:
            print("No smart groups found, falling back to full scan...", file=sys.stderr)
            all_devs = self._collect_devices_recursive()
            for dev in all_devs:
                self.cache.add_device(self.server, dev["name"], dev["id"], dev["device_id"], dev)
            return len(all_devs)

        # 2. Fetch group contents (in parallel)
        print(f"Fetching devices from {len(group_ids)} groups...", file=sys.stderr)
        all_fetched = []
        
        def fetch_worker(gid, gname):
            return self._collect_devices_from_group(gid)

        if parallel:
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(fetch_worker, gid, name): name for gid, name in group_ids}
                for future in as_completed(futures):
                    all_fetched.extend(future.result())
        else:
            for gid, name in group_ids:
                all_fetched.extend(fetch_worker(gid, name))
        
        # 3. Cache results
        for dev in all_fetched:
            self.cache.add_device(self.server, dev["name"], dev["id"], dev["device_id"], dev)
            
        return len(all_fetched)

    def get_device_groups(self, device_id: int) -> Optional[Dict[str, Any]]:
        """Get groups for a device from /api/devices/internal/devices/{id}/groups"""
        url = f"{self.server}/api/devices/internal/devices/{device_id}/groups"
        success, data = safe_api_request(
            self.session,
            "get",
            url,
            on_error_callback=self.cache.clear_on_error
        )
        return data if success else None


# Example usage
if __name__ == "__main__":
    cache = DeviceCache()
    
    print("Device Cache Stats:")
    print(json.dumps(cache.stats(), indent=2))
    print()
    
    print("Cached Devices:")
    devices = cache.list_cached_devices()
    if devices:
        for key, entry in list(devices.items())[:5]:
            print(f"  {key}: id={entry.get('id')}, device_id={entry.get('device_id')}")
    else:
        print("  (none yet)")
