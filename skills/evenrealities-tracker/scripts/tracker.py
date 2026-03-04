#!/usr/bin/env python3
"""
Evenrealities Order Tracker
Checks order status and notifies on changes

DEPENDENCIES:
- playwright (pip install playwright && playwright install)
- No environment variables required for the tracker script itself
- Telegram notifications handled by OpenClaw cron delivery mechanism

MULTI-SHIPMENT SUPPORT:
- Orders can have multiple shipments (e.g., smart ring sizing kit + final ring)
- Tracking page shows combined status across all shipments
- Status changes trigger notifications only when current status differs from history
- Supports PENDING, SHIPPED, PROCESSING, DELIVERED, IN_PRODUCTION statuses

SECURITY:
- Input validation: Email and order_id are validated before use
- No credential handling: This script only reads/writes local files and accesses public tracking page
- Notifications: Handled by cron delivery mechanism (not embedded in script)

Usage:
  python3 tracker.py --check        # Check all orders now
  python3 tracker.py --config       # Show configured orders
  python3 tracker.py --history      # Show status history
"""

import json
import os
import sys
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class EventrealitiesTracker:
    def __init__(self):
        self.skill_dir = Path(__file__).parent.parent
        # Go up to clawd root, then to memory
        self.memory_dir = self.skill_dir.parent.parent / "memory"
        self.memory_dir.mkdir(exist_ok=True)
        self.config_file = self.memory_dir / "evenrealities-orders.json"
        self.status_history = self.memory_dir / "evenrealities-status-history.json"
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format to prevent injection"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_valid_order_id(self, order_id: str) -> bool:
        """Validate order ID format (alphanumeric and common separators)"""
        # Allow digits, letters, hyphens, underscores (typical order ID formats)
        pattern = r'^[a-zA-Z0-9\-_]+$'
        if len(order_id) > 50:  # Reasonable length limit
            return False
        return bool(re.match(pattern, order_id))
    
    def load_orders(self) -> List[Dict]:
        """Load orders from config file"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                data = json.load(f)
                return data.get("orders", [])
        return []
    
    def load_history(self) -> Dict:
        """Load status history"""
        if self.status_history.exists():
            with open(self.status_history) as f:
                return json.load(f)
        return {}
    
    def save_history(self, history: Dict):
        """Save status history"""
        with open(self.status_history, 'w') as f:
            json.dump(history, f, indent=2, default=str)
    
    def get_order_key(self, email: str, order_id: str) -> str:
        """Create unique key for order"""
        return f"{email}:{order_id}"
    
    def track_orders(self) -> List[Dict]:
        """
        Main tracking logic - uses playwright to check statuses
        Returns list of changed orders
        """
        orders = self.load_orders()
        history = self.load_history()
        changes = []
        
        if not orders:
            print("❌ No orders configured in evenrealities-orders.json")
            return changes
        
        print(f"🔍 Checking {len(orders)} order(s)...")
        print("=" * 60)
        
        for order in orders:
            email = order.get("email")
            order_id = order.get("order_id")
            
            # Validate inputs
            if not email or not self._is_valid_email(email):
                print(f"⚠️ Invalid email in order entry: {order}")
                continue
            
            if not order_id or not self._is_valid_order_id(order_id):
                print(f"⚠️ Invalid order ID in entry: {order}")
                continue
            
            key = self.get_order_key(email, order_id)
            print(f"\n📦 Checking: {email} / Order #{order_id}")
            
            # Fetch status via browser
            status = self.fetch_status_via_browser(email, order_id)
            
            if status:
                print(f"   Status: {status}")
                
                # Check if status changed
                previous_status = history.get(key, {}).get("status")
                
                if previous_status and previous_status != status:
                    print(f"   ✨ CHANGED: {previous_status} → {status}")
                    changes.append({
                        "email": email,
                        "order_id": order_id,
                        "previous_status": previous_status,
                        "new_status": status,
                        "timestamp": datetime.now().isoformat()
                    })
                elif not previous_status:
                    print(f"   (First check - baseline established)")
                else:
                    print(f"   (No change)")
                
                # Update history
                history[key] = {
                    "email": email,
                    "order_id": order_id,
                    "status": status,
                    "last_checked": datetime.now().isoformat()
                }
            else:
                print(f"   ❌ Failed to fetch status")
        
        print("\n" + "=" * 60)
        
        # Save updated history
        self.save_history(history)
        
        return changes
    
    def fetch_status_via_browser(self, email: str, order_id: str) -> Optional[str]:
        """
        Use Playwright to fetch order status from Evenrealities
        Returns the status text or None if failed
        """
        try:
            from playwright.sync_api import sync_playwright
            import time
            
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                
                # Navigate to tracking page
                print(f"   → Loading https://track.evenrealities.com...")
                page.goto('https://track.evenrealities.com', wait_until='networkidle')
                
                # Wait for page to fully load
                page.wait_for_load_state('networkidle')
                time.sleep(0.5)
                
                # Fill email input
                print(f"   → Filling email: {email}")
                try:
                    email_selectors = [
                        'input[type="email"]',
                        'input[name="email"]',
                        'input[placeholder*="email" i]',
                        'input[placeholder*="Email" i]',
                        '#email',
                    ]
                    
                    email_input = None
                    for selector in email_selectors:
                        elements = page.locator(selector)
                        if elements.count() > 0:
                            email_input = elements.first
                            break
                    
                    if email_input:
                        email_input.fill(email)
                    else:
                        print(f"   ⚠️ Could not find email input field")
                        browser.close()
                        return None
                
                except Exception as e:
                    print(f"   ⚠️ Error filling email: {e}")
                    browser.close()
                    return None
                
                # Fill order ID input
                print(f"   → Filling order ID: {order_id}")
                try:
                    order_selectors = [
                        'input[name="order"]',
                        'input[name="order_id"]',
                        'input[placeholder*="order" i]',
                        'input[placeholder*="Order" i]',
                        'input[placeholder*="numéro" i]',
                        'input:nth-of-type(2)',
                        '#order_id',
                        '#orderNumber',
                    ]
                    
                    order_input = None
                    for selector in order_selectors:
                        elements = page.locator(selector)
                        if elements.count() > 0 and elements.first != email_input:
                            order_input = elements.first
                            break
                    
                    if order_input:
                        order_input.fill(order_id)
                    else:
                        print(f"   ⚠️ Could not find order ID input field")
                        browser.close()
                        return None
                
                except Exception as e:
                    print(f"   ⚠️ Error filling order ID: {e}")
                    browser.close()
                    return None
                
                # Click submit button
                print(f"   → Clicking submit button...")
                try:
                    submit_selectors = [
                        'button:has-text("Submit")',
                        'button:has-text("Check")',
                        'button:has-text("Confirm")',
                        'button:has-text("Vérifier")',
                        'button:has-text("Rechercher")',
                        'button[type="submit"]',
                        'button:nth-of-type(1)',
                        '#searchButton',
                    ]
                    
                    submit_btn = None
                    for selector in submit_selectors:
                        elements = page.locator(selector)
                        if elements.count() > 0:
                            submit_btn = elements.first
                            break
                    
                    if submit_btn:
                        submit_btn.click()
                    else:
                        print(f"   ⚠️ Could not find submit button")
                        browser.close()
                        return None
                
                except Exception as e:
                    print(f"   ⚠️ Error clicking submit: {e}")
                    browser.close()
                    return None
                
                # Wait for status to appear
                print(f"   → Waiting for status response...")
                time.sleep(2)
                
                # Extract status from page content
                try:
                    # Get full page text
                    page_text = page.locator('body').text_content()
                    
                    # Extract status - look for "Status Pending", "Status Shipped" etc
                    status_match = re.search(r'Status\s+(Pending|Shipped|Processing|Delivered|In Production)', page_text, re.IGNORECASE)
                    if status_match:
                        status_text = status_match.group(1).strip()
                    else:
                        # Fallback: look for key indicators
                        if 'Not shipped yet' in page_text:
                            status_text = 'Pending'
                        elif 'Shipped' in page_text.replace('Not shipped', ''):
                            status_text = 'Shipped'
                        elif 'In Production' in page_text:
                            status_text = 'In Production'
                        else:
                            status_text = 'Unknown'
                    
                    browser.close()
                    
                    # Map to standard statuses
                    status_map = {
                        'pending': 'PENDING',
                        'shipped': 'SHIPPED',
                        'processing': 'PROCESSING',
                        'delivered': 'DELIVERED',
                        'in production': 'IN_PRODUCTION',
                        'unknown': 'UNKNOWN',
                    }
                    
                    mapped_status = status_map.get(status_text.lower(), status_text.upper())
                    return mapped_status
                
                except Exception as e:
                    print(f"   ⚠️ Error extracting status: {e}")
                    browser.close()
                    return None
        
        except ImportError:
            print(f"   ❌ Playwright not installed. Install with: pip install playwright")
            return None
        except Exception as e:
            print(f"   ❌ Browser error: {e}")
            return None
    
    def show_config(self):
        """Show current configuration"""
        orders = self.load_orders()
        if orders:
            print("📋 Configured orders:")
            for i, order in enumerate(orders, 1):
                print(f"   {i}. {order.get('email')} - Order #{order.get('order_id')}")
        else:
            print("No orders configured yet")
    
    def show_history(self):
        """Show status history"""
        history = self.load_history()
        if history:
            print("📜 Status history:")
            for key, data in history.items():
                print(f"\n   {key}")
                print(f"      Status: {data.get('status')}")
                print(f"      Last checked: {data.get('last_checked')}")
        else:
            print("No history yet")


def main():
    parser = argparse.ArgumentParser(description="Evenrealities Order Tracker")
    parser.add_argument("--check", action="store_true", help="Check all orders")
    parser.add_argument("--config", action="store_true", help="Show configuration")
    parser.add_argument("--history", action="store_true", help="Show status history")
    
    args = parser.parse_args()
    
    tracker = EventrealitiesTracker()
    
    if args.check:
        changes = tracker.track_orders()
        if changes:
            print(f"\n✨ {len(changes)} change(s) detected!")
            for change in changes:
                print(f"   📦 {change['order_id']}: {change['previous_status']} → {change['new_status']}")
        else:
            print("\n✓ No changes detected")
    elif args.history:
        tracker.show_history()
    elif args.config:
        tracker.show_config()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
