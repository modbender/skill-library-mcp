#!/usr/bin/env python3
"""
Tor Browser Automation CLI
A headless browser automation tool with Tor SOCKS5 proxy support.
Enables navigation, clicking, typing, and data extraction on .onion sites.
"""

import argparse
import asyncio
import json
import sys
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

# Check dependencies
try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
except ImportError:
    print("Error: playwright not installed. Run: pip install playwright && playwright install")
    sys.exit(1)

try:
    import aiohttp
except ImportError:
    aiohttp = None

@dataclass
class Config:
    tor_proxy: str = "socks5://127.0.0.1:9050"
    tor_control_port: int = 9051
    headless: bool = True
    timeout: int = 30000
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0"
    viewport: Dict[str, int] = None
    
    def __post_init__(self):
        if self.viewport is None:
            self.viewport = {"width": 1920, "height": 1080}

class TorBrowser:
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self._state: Dict[str, Any] = {}
    
    async def start(self):
        """Initialize browser with Tor proxy"""
        self.playwright = await async_playwright().start()
        
        browser_args = {
            "headless": self.config.headless,
            "proxy": {
                "server": self.config.tor_proxy
            }
        }
        
        self.browser = await self.playwright.chromium.launch(**browser_args)
        
        self.context = await self.browser.new_context(
            user_agent=self.config.user_agent,
            viewport=self.config.viewport,
            bypass_csp=True,
            java_script_enabled=True
        )
        
        self.page = await self.context.new_page()
        self.page.set_default_timeout(self.config.timeout)
        
        return self
    
    async def close(self):
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def navigate(self, url: str, wait_until: str = "networkidle"):
        """Navigate to URL via Tor"""
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        response = await self.page.goto(url, wait_until=wait_until)
        return {
            "url": self.page.url,
            "status": response.status if response else None,
            "title": await self.page.title()
        }
    
    async def get_snapshot(self, interactive_only: bool = False) -> Dict:
        """Get page snapshot with element refs"""
        if not self.page:
            raise RuntimeError("Browser not started.")
        
        elements = await self.page.query_selector_all("*")
        snapshot = {
            "url": self.page.url,
            "title": await self.page.title(),
            "elements": []
        }
        
        for i, elem in enumerate(elements):
            tag = await elem.evaluate("el => el.tagName.toLowerCase()")
            
            if interactive_only:
                is_interactive = await elem.evaluate("""
                    el => el.tagName.match(/^(INPUT|TEXTAREA|SELECT|BUTTON|A)$/i) ||
                          el.onclick !== null ||
                          el.getAttribute('role') === 'button'
                """)
                if not is_interactive:
                    continue
            
            text = await elem.inner_text()
            elem_info = {
                "ref": f"@e{i}",
                "tag": tag,
                "text": text[:100] if text else "",
                "type": await elem.get_attribute("type") or "",
                "name": await elem.get_attribute("name") or "",
                "id": await elem.get_attribute("id") or "",
                "class": await elem.get_attribute("class") or ""
            }
            snapshot["elements"].append(elem_info)
        
        return snapshot
    
    async def find_element(self, ref_or_selector: str):
        """Find element by ref or CSS selector"""
        if ref_or_selector.startswith("@e"):
            index = int(ref_or_selector[2:])
            elements = await self.page.query_selector_all("*")
            return elements[index] if index < len(elements) else None
        else:
            return await self.page.query_selector(ref_or_selector)
    
    async def click(self, ref_or_selector: str):
        """Click element"""
        elem = await self.find_element(ref_or_selector)
        if elem:
            await elem.click()
            return {"success": True}
        return {"success": False, "error": "Element not found"}
    
    async def fill(self, ref_or_selector: str, text: str):
        """Fill input field"""
        elem = await self.find_element(ref_or_selector)
        if elem:
            await elem.fill(text)
            return {"success": True}
        return {"success": False, "error": "Element not found"}
    
    async def type(self, ref_or_selector: str, text: str):
        """Type text into element"""
        elem = await self.find_element(ref_or_selector)
        if elem:
            await elem.type(text)
            return {"success": True}
        return {"success": False, "error": "Element not found"}
    
    async def get_text(self, ref_or_selector: str = None) -> str:
        """Get text content"""
        if ref_or_selector:
            elem = await self.find_element(ref_or_selector)
            return await elem.inner_text() if elem else ""
        return await self.page.inner_text("body")
    
    async def get_html(self, ref_or_selector: str = None) -> str:
        """Get HTML content"""
        if ref_or_selector:
            elem = await self.find_element(ref_or_selector)
            return await elem.inner_html() if elem else ""
        return await self.page.content()
    
    async def screenshot(self, path: str = None, full_page: bool = False):
        """Take screenshot"""
        if path:
            await self.page.screenshot(path=path, full_page=full_page)
            return {"saved": path}
        else:
            import base64
            data = await self.page.screenshot(full_page=full_page)
            return {"base64": base64.b64encode(data).decode()}
    
    async def extract_links(self) -> list:
        """Extract all links from page"""
        links = await self.page.query_selector_all("a")
        result = []
        for link in links:
            href = await link.get_attribute("href")
            text = await link.inner_text()
            if href:
                result.append({"href": href, "text": text.strip()[:50]})
        return result
    
    async def wait(self, ms: int = 1000):
        """Wait for milliseconds"""
        await asyncio.sleep(ms / 1000)
        return {"waited": ms}
    
    async def check_tor_connection(self) -> Dict:
        """Check if Tor connection is working"""
        try:
            check_url = "https://check.torproject.org/api/ip"
            response = await self.navigate(check_url)
            content = await self.get_text()
            data = json.loads(content)
            return {
                "is_tor": data.get("IsTor", False),
                "ip": data.get("IP", "unknown"),
                "status": "connected" if data.get("IsTor") else "not_using_tor"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def state_save(self, path: str):
        """Save session state (cookies, storage)"""
        # Implementation requires storage state export
        pass
    
    def state_load(self, path: str):
        """Load session state"""
        pass


async def main():
    parser = argparse.ArgumentParser(description="Tor Browser Automation")
    parser.add_argument("--proxy", default="socks5://127.0.0.1:9050", help="Tor SOCKS5 proxy")
    parser.add_argument("--headless", action="store_true", default=True, help="Run headless")
    parser.add_argument("--headed", action="store_true", help="Show browser window")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Open command
    open_parser = subparsers.add_parser("open", help="Navigate to URL")
    open_parser.add_argument("url", help="URL to navigate to")
    
    # Snapshot command
    snap_parser = subparsers.add_parser("snapshot", help="Get page snapshot")
    snap_parser.add_argument("-i", "--interactive", action="store_true", help="Interactive elements only")
    
    # Click command
    click_parser = subparsers.add_parser("click", help="Click element")
    click_parser.add_argument("ref", help="Element ref (e.g., @e1) or selector")
    
    # Fill command
    fill_parser = subparsers.add_parser("fill", help="Fill input")
    fill_parser.add_argument("ref", help="Element ref")
    fill_parser.add_argument("text", help="Text to fill")
    
    # Get text command
    text_parser = subparsers.add_parser("gettext", help="Get text content")
    text_parser.add_argument("--ref", help="Element ref (default: body)")
    
    # Screenshot command
    ss_parser = subparsers.add_parser("screenshot", help="Take screenshot")
    ss_parser.add_argument("--output", "-o", help="Output file path")
    ss_parser.add_argument("--full", action="store_true", help="Full page")
    
    # Links command
    subparsers.add_parser("links", help="Extract links")
    
    # Check Tor command
    subparsers.add_parser("check-tor", help="Check Tor connection")
    
    # Wait command
    wait_parser = subparsers.add_parser("wait", help="Wait")
    wait_parser.add_argument("ms", type=int, default=1000, help="Milliseconds")
    
    # Close command
    subparsers.add_parser("close", help="Close browser")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    config = Config(
        tor_proxy=args.proxy,
        headless=not args.headed
    )
    
    browser = TorBrowser(config)
    
    try:
        await browser.start()
        
        if args.command == "open":
            result = await browser.navigate(args.url)
        elif args.command == "snapshot":
            result = await browser.get_snapshot(interactive_only=args.interactive)
        elif args.command == "click":
            result = await browser.click(args.ref)
        elif args.command == "fill":
            result = await browser.fill(args.ref, args.text)
        elif args.command == "gettext":
            text = await browser.get_text(args.ref)
            result = {"text": text}
        elif args.command == "screenshot":
            result = await browser.screenshot(args.output, args.full)
        elif args.command == "links":
            result = {"links": await browser.extract_links()}
        elif args.command == "check-tor":
            result = await browser.check_tor_connection()
        elif args.command == "wait":
            result = await browser.wait(args.ms)
        elif args.command == "close":
            await browser.close()
            result = {"closed": True}
        else:
            result = {"error": "Unknown command"}
        
        output = json.dumps(result, indent=2, ensure_ascii=False) if args.json else result
        print(output)
        
    except Exception as e:
        error = {"error": str(e)}
        print(json.dumps(error, indent=2) if args.json else f"Error: {e}")
        sys.exit(1)
    finally:
        if args.command != "close":
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
