#!/usr/bin/env python3
"""
markdown-extract skill for OpenClaw
Extracts clean markdown from any URL using the markdown.new API
"""

import sys
import json
import subprocess


def extract_markdown(url: str, method: str = "auto") -> dict:
    """
    Extract markdown from a URL using markdown.new API
    
    Args:
        url: The URL to extract markdown from
        method: Extraction method - auto, ai, or browser
    
    Returns:
        dict with 'success', 'markdown', and optional 'error' keys
    """
    if not url:
        return {"success": False, "error": "No URL provided"}
    
    # Validate URL (basic check)
    if not url.startswith(("http://", "https://")):
        return {"success": False, "error": "URL must start with http:// or https://"}
    
    try:
        if method == "auto":
            # GET request - URL in path
            cmd = ["curl", "-s", f"https://markdown.new/{url}"]
        else:
            # POST request with JSON body
            cmd = [
                "curl", "-s", "-X", "POST",
                "https://markdown.new/",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({"url": url, "method": method})
            ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout.strip()
        
        # Check for error responses
        if not output:
            return {"success": False, "error": "Empty response from API"}
        
        # Check if response is an error JSON
        try:
            error_check = json.loads(output)
            if "error" in error_check or "status" in error_check:
                return {"success": False, "error": error_check.get("error", error_check.get("message", "API error"))}
        except json.JSONDecodeError:
            pass
        
        # Check for Cloudflare block
        if "Please enable cookies" in output or "Cloudflare Ray ID" in output:
            return {"success": False, "error": "API blocked by Cloudflare. Try a different method."}
        
        # Parse JSON response if it's JSON (for POST methods)
        if method != "auto" and output.startswith("{"):
            try:
                data = json.loads(output)
                if data.get("success"):
                    return {"success": True, "markdown": data.get("content", "")}
                else:
                    return {"success": False, "error": data.get("error", "API error")}
            except json.JSONDecodeError:
                pass
        
        return {"success": True, "markdown": output}
    
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Request timed out"}
    except Exception as e:
        return {"success": False, "error": f"Error: {str(e)}"}


def main():
    """Main entry point for the skill"""
    args = sys.argv[1:]
    
    if not args:
        print(json.dumps({
            "success": False, 
            "error": "Usage: markdown-extract <url> [method]"
        }))
        sys.exit(1)
    
    url = args[0]
    method = args[1] if len(args) > 1 else "auto"
    
    # Validate method
    if method not in ["auto", "ai", "browser"]:
        print(json.dumps({
            "success": False,
            "error": f"Invalid method: {method}. Use auto, ai, or browser"
        }))
        sys.exit(1)
    
    result = extract_markdown(url, method)
    print(json.dumps(result))
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
