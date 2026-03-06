#!/usr/bin/env python3
"""
Session management example - Login and scrape protected content
Use for: Sites requiring authentication
"""
from scrapling.fetchers import StealthySession

# Example: Login to a site and access protected content
# Note: Replace with actual credentials and selectors

login_url = "https://example.com/login"
protected_url = "https://example.com/dashboard"

print("Creating stealth session...")

with StealthySession(headless=False) as session:  # Set headless=True in production
    # Step 1: Load login page
    print(f"\n1. Loading login page: {login_url}")
    login_page = session.fetch(login_url)
    
    # Step 2: Fill login form
    print("2. Filling login form...")
    # Adjust selectors to match the actual site
    login_page.fill('input[name="username"], #username', 'your_username')
    login_page.fill('input[name="password"], #password', 'your_password')
    
    # Step 3: Submit form
    print("3. Submitting login...")
    login_page.click('button[type="submit"], input[type="submit"]')
    
    # Wait for navigation
    import time
    time.sleep(2)
    
    # Step 4: Access protected content
    print(f"4. Accessing protected content: {protected_url}")
    protected_page = session.fetch(protected_url)
    
    # Step 5: Extract data
    data = protected_page.css('.protected-data')
    print(f"\nFound {len(data)} data items:")
    
    for item in data[:5]:
        print(f"  - {item.css('::text').get()}")
    
    # Session automatically closes when exiting 'with' block
    # Cookies and state are preserved within the session

print("\nSession complete. Cookies and login state were maintained.")
print("\nNote: For production use:")
print("  1. Store credentials securely (environment variables)")
print("  2. Use headless=True to hide browser")
print("  3. Save session for reuse: session.save('my_session.pkl')")
