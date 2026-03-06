#!/usr/bin/env python3
"""
Bulk Device Update Handler for FileWave Skill

Handles school district summer workflows:
- CSV input: SerialNumber, DeviceName, EnrollmentUser
- Device lookup by serial number
- Bulk PATCH operations with backoff/retry
- Model refresh after completion
"""

import csv
import json
import sys
import time
import requests
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime, timezone

from device_cache import DeviceCache, DeviceLookup
from api_utils import normalize_server_url, create_filewave_session, api_call_with_backoff


class BulkUpdateValidator:
    """Validate CSV structure and content."""
    
    REQUIRED_COLUMNS = ["SerialNumber", "DeviceName", "EnrollmentUser"]
    
    @staticmethod
    def validate_csv_file(csv_path: Path) -> Tuple[bool, str]:
        """
        Validate CSV file structure.
        
        Returns: (is_valid, error_message)
        """
        if not csv_path.exists():
            return False, f"CSV file not found: {csv_path}"
        
        try:
            with open(csv_path, "r") as f:
                reader = csv.DictReader(f)
                
                if not reader.fieldnames:
                    return False, "CSV file is empty"
                
                # Check required columns
                fieldnames = reader.fieldnames
                missing = set(BulkUpdateValidator.REQUIRED_COLUMNS) - set(fieldnames)
                if missing:
                    return False, f"Missing required columns: {', '.join(missing)}"
                
                # Check for data rows
                rows = list(reader)
                if not rows:
                    return False, "CSV file has no data rows"
                
                # Validate each row
                for i, row in enumerate(rows, start=2):  # Start at 2 (header is row 1)
                    serial = (row.get("SerialNumber") or "").strip()
                    name = (row.get("DeviceName") or "").strip()
                    user = (row.get("EnrollmentUser") or "").strip()
                    
                    if not serial:
                        return False, f"Row {i}: SerialNumber is empty"
                    if not name:
                        return False, f"Row {i}: DeviceName is empty"
                    if not user:
                        return False, f"Row {i}: EnrollmentUser is empty"
                
                return True, f"Valid CSV with {len(rows)} device(s)"
        
        except csv.Error as e:
            return False, f"CSV parsing error: {e}"
        except Exception as e:
            return False, f"Validation error: {e}"
    
    @staticmethod
    def load_csv(csv_path: Path) -> Optional[List[Dict[str, str]]]:
        """Load and parse CSV file."""
        try:
            rows = []
            with open(csv_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append({
                        "serial": (row.get("SerialNumber") or "").strip(),
                        "name": (row.get("DeviceName") or "").strip(),
                        "user": (row.get("EnrollmentUser") or "").strip(),
                    })
            return rows
        except Exception as e:
            print(f"Error loading CSV: {e}", file=sys.stderr)
            return None


class BulkUpdateExecutor:
    """Execute bulk device updates with retry logic."""
    
    def __init__(self, server: str, token: str, cache: Optional[DeviceCache] = None):
        self.server = normalize_server_url(server)
        self.token = token
        self.cache = cache or DeviceCache()
        self.lookup = DeviceLookup(self.server, self.token, self.cache)
        self.session = create_filewave_session(token)
    
    def _update_device_name(self, device_id: int, new_name: str) -> Tuple[bool, str]:
        """
        PATCH device name with backoff/retry.
        
        Returns: (success, message)
        """
        url = f"{self.server}/filewave/api/devices/v1/devices/{device_id}"
        payload = {"name": new_name}
        
        def patch_name():
            try:
                resp = self.session.patch(url, json=payload, timeout=10)
                if resp.status_code == 200:
                    return True, "Name updated"
                elif resp.status_code in [429, 503, 504]:
                    return None, None  # Retry signal
                else:
                    return False, f"HTTP {resp.status_code}: {resp.text[:100]}"
            except requests.exceptions.RequestException as e:
                return False, f"Request error: {str(e)[:100]}"
        
        return api_call_with_backoff(patch_name)
    
    def _update_device_auth_user(self, device_id: int, auth_user: str) -> Tuple[bool, str]:
        """
        PATCH device auth_username with backoff/retry.
        
        Returns: (success, message)
        """
        url = f"{self.server}/filewave/api/devices/v1/devices/{device_id}"
        payload = {"auth_username": auth_user}
        
        def patch_auth():
            try:
                resp = self.session.patch(url, json=payload, timeout=10)
                if resp.status_code == 200:
                    return True, "Auth user updated"
                elif resp.status_code in [429, 503, 504]:
                    return None, None  # Retry signal
                else:
                    return False, f"HTTP {resp.status_code}: {resp.text[:100]}"
            except requests.exceptions.RequestException as e:
                return False, f"Request error: {str(e)[:100]}"
        
        return api_call_with_backoff(patch_auth)
    
    def _refresh_model(self) -> Tuple[bool, str]:
        """
        POST to /filewave/api/fwserver/update_model with backoff/retry.
        
        Returns: (success, message)
        """
        url = f"{self.server}/filewave/api/fwserver/update_model"
        
        def refresh():
            try:
                resp = self.session.post(url, json={}, timeout=10)
                if resp.status_code in [200, 204]:
                    return True, "Model refreshed"
                elif resp.status_code in [429, 503, 504]:
                    return None, None  # Retry signal
                else:
                    return False, f"HTTP {resp.status_code}: {resp.text[:100]}"
            except requests.exceptions.RequestException as e:
                return False, f"Request error: {str(e)[:100]}"
        
        return api_call_with_backoff(refresh)
    
    def execute(self, devices: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Execute bulk update.
        
        Args:
            devices: List of {serial, name, user} dicts
        
        Returns: Results summary
        """
        results = {
            "total": len(devices),
            "successful": 0,
            "failed": 0,
            "details": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        print(f"\nProcessing {len(devices)} device(s)...\n", file=sys.stderr)
        
        for i, device in enumerate(devices, start=1):
            serial = device["serial"]
            name = device["name"]
            user = device["user"]
            
            print(f"[{i}/{len(devices)}] Serial: {serial}", file=sys.stderr)
            device_result = {
                "serial": serial,
                "name": name,
                "user": user,
                "success": False,
                "messages": []
            }
            
            # Step 1: Lookup device by serial
            print(f"  → Looking up device...", file=sys.stderr, end="")
            lookup_result = self.lookup.search_device(serial)
            
            if not lookup_result:
                device_result["messages"].append("Device not found (serial lookup failed)")
                results["details"].append(device_result)
                results["failed"] += 1
                print(" FAILED", file=sys.stderr)
                continue
            
            device_id = lookup_result["id"]
            device_name = lookup_result.get("name", "unknown")
            print(f" Found (ID: {device_id}, name: {device_name})", file=sys.stderr)
            
            # Step 2: Update device name
            print(f"  → Updating name to: {name}", file=sys.stderr, end="")
            success, msg = self._update_device_name(device_id, name)
            device_result["messages"].append(f"Name update: {msg}")
            if not success:
                print(f" FAILED: {msg}", file=sys.stderr)
                results["details"].append(device_result)
                results["failed"] += 1
                continue
            print(" OK", file=sys.stderr)
            
            # Step 3: Update auth username
            print(f"  → Updating auth user to: {user}", file=sys.stderr, end="")
            success, msg = self._update_device_auth_user(device_id, user)
            device_result["messages"].append(f"Auth user update: {msg}")
            if not success:
                print(f" FAILED: {msg}", file=sys.stderr)
                results["details"].append(device_result)
                results["failed"] += 1
                continue
            print(" OK", file=sys.stderr)
            
            # Mark as successful
            device_result["success"] = True
            results["successful"] += 1
            results["details"].append(device_result)
        
        # Step 4: Refresh model
        print(f"\nRefreshing model...", file=sys.stderr, end="")
        success, msg = self._refresh_model()
        if success:
            print(" OK", file=sys.stderr)
            results["model_refresh"] = "success"
        else:
            print(f" WARNING: {msg}", file=sys.stderr)
            results["model_refresh"] = f"warning: {msg}"
        
        print(f"\nResults: {results['successful']}/{results['total']} successful, {results['failed']} failed\n", 
              file=sys.stderr)
        
        return results


def generate_csv_template(output_path: Path) -> bool:
    """
    Generate a CSV template for bulk device update.
    
    Returns: True if successful
    """
    try:
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "SerialNumber",
                "DeviceName",
                "EnrollmentUser"
            ])
            
            # Example rows
            writer.writerow([
                "DMPPT57WHP50",
                "Student-iPad-001",
                "student@district.edu"
            ])
            writer.writerow([
                "F9FYD15YLMX0",
                "Teacher-iPad-001",
                "teacher@district.edu"
            ])
        
        print(f"CSV template generated: {output_path}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"Error generating template: {e}", file=sys.stderr)
        return False


# Example usage
if __name__ == "__main__":
    # Generate template
    template_path = Path.home() / "Desktop" / "bulk_update_template.csv"
    generate_csv_template(template_path)
    print(f"Template saved to: {template_path}")
