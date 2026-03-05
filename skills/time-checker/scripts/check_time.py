import sys
import argparse
import subprocess
import re

def get_time(location):
    """
    Scrapes time.is for the current time using curl to avoid SSL issues.
    """
    loc_path = location.replace(' ', '_')
    url = f"https://time.is/{loc_path}"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    try:
        # Use curl to fetch the page
        cmd = ['curl', '-s', '-L', '-A', user_agent, url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        html = result.stdout
        
        # Regex to find the time in the clock div
        # time.is often uses <time id="clock"> or <div id="t_clock">
        time_match = re.search(r'<(?:div|time)[^>]*id=["\'](?:t_)?clock["\'][^>]*>(.*?)</(?:div|time)>', html, re.IGNORECASE)
        if not time_match:
            # Fallback for different structures
            time_match = re.search(r'class=["\']clock["\'][^>]*>(.*?)</', html, re.IGNORECASE)
            
        if not time_match:
            return {"error": f"Could not find clock for location: {location}. The page might have changed or location is invalid."}
        
        current_time = time_match.group(1).strip()
        # Remove any inner spans/tags
        current_time = re.sub(r'<[^>]*>', '', current_time)
        
        # Extract details from msgdiv
        details_match = re.search(r'<div[^>]*id=["\']msgdiv["\'][^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
        details = ""
        if details_match:
            details = re.sub(r'<[^>]*>', '', details_match.group(1)).strip()
            details = ' '.join(details.split())

        return {
            "location": location,
            "time": current_time,
            "details": details,
            "url": url
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check time for a location via time.is")
    parser.add_argument("location", help="Location to check")
    args = parser.parse_args()
    
    res = get_time(args.location)
    
    if "error" in res:
        print(f"Error: {res['error']}")
        sys.exit(1)
    else:
        print(f"Time in {res['location']}: {res['time']}")
        if res['details']:
            print(f"Details: {res['details']}")
        print(f"Source: {res['url']}")
