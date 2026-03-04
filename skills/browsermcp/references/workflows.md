# BrowserMCP Common Workflows

Practical, copy-paste ready workflow patterns for common browser automation tasks.

## Table of Contents

1. [Web Search](#web-search)
2. [Form Handling](#form-handling)
3. [Authentication](#authentication)
4. [Data Extraction](#data-extraction)
5. [E-commerce Tasks](#e-commerce-tasks)
6. [Social Media](#social-media)
7. [Testing and Verification](#testing-and-verification)
8. [Documentation Reading](#documentation-reading)

---

## Web Search

### Google Search and Extract Results

```javascript
// Navigate to Google
navigate(url="https://google.com")
wait(time=2)

// Get page structure
snapshot()

// Enter search query and submit
type(element="Google search box", ref="e8", text="BrowserMCP automation tool", submit=true)

// Wait for results to load
wait(time=2)

// Capture results structure
snapshot()

// Click first organic result (skip ads)
// Look for [eXX] refs that represent result links
click(element="First search result link", ref="e25")

// Wait for page load
wait(time=3)

// Verify landing page
screenshot()
snapshot()
```

### DuckDuckGo Search

```javascript
navigate(url="https://duckduckgo.com")
wait(time=2)
snapshot()

type(element="Search input", ref="e5", text="browser automation best practices", submit=true)
wait(time=2)
snapshot()

// Extract information from results
get_console_logs()
screenshot()
```

### Academic Search (Google Scholar)

```javascript
navigate(url="https://scholar.google.com")
wait(time=2)
snapshot()

type(element="Search articles", ref="e6", text="machine learning", submit=true)
wait(time=2)
snapshot()

// Click on a paper
click(element="Paper title link", ref="e15")
wait(time=2)
screenshot()
```

---

## Form Handling

### Contact Form Submission

```javascript
// Navigate to contact page
navigate(url="https://example.com/contact")
wait(time=2)

// Get form structure
snapshot()

// Fill form fields sequentially
type(element="Full name input", ref="e10", text="Jane Smith")
type(element="Email address input", ref="e12", text="jane.smith@example.com")
type(element="Subject dropdown", ref="e14", text="General Inquiry")
type(element="Message textarea", ref="e16", text="Hello, I would like to know more about your services. Please contact me at your convenience.")

// Optional: Check newsletter checkbox
// click(element="Subscribe to newsletter checkbox", ref="e18")

// Submit form
type(element="Submit button", ref="e20", text="", submit=true)
// OR: click(element="Send message button", ref="e20")

// Wait for submission response
wait(time=3)

// Verify success
screenshot()
snapshot()
get_console_logs()
```

### Multi-Step Form (Wizard)

```javascript
// Step 1: Personal Information
navigate(url="https://example.com/signup")
wait(time=2)
snapshot()

type(element="First name", ref="e5", text="John")
type(element="Last name", ref="e6", text="Doe")
type(element="Date of birth", ref="e7", text="01/01/1990")
click(element="Next button", ref="e10")

// Step 2: Account Details
wait(time=2)
snapshot()

type(element="Username", ref="e12", text="johndoe123")
type(element="Email", ref="e14", text="john@example.com")
type(element="Password", ref="e16", text="SecurePass123!")
type(element="Confirm password", ref="e18", text="SecurePass123!")
click(element="Next button", ref="e20")

// Step 3: Preferences
wait(time=2)
snapshot()

select_option(element="Country", ref="e22", values=["US"])
select_option(element="Language", ref="e24", values=["en"])
click(element="Terms checkbox", ref="e26")
click(element="Complete signup", ref="e28")

// Verify completion
wait(time=3)
screenshot()
```

### File Upload Form

```javascript
navigate(url="https://example.com/upload")
wait(time=2)
snapshot()

// Fill description
type(element="File description", ref="e8", text="Quarterly report document")

// Note: File upload via drag-drop or file picker
// BrowserMCP may have limitations on direct file uploads
// User may need to manually select file

// Click upload button after manual file selection
click(element="Upload button", ref="e15")
wait(time=5)  // Wait for upload
screenshot()
```

---

## Authentication

### Login with Existing Session

```javascript
// User is already logged in via browser profile
navigate(url="https://github.com")
wait(time=2)
snapshot()

// Should show authenticated content
// Look for user-specific elements in snapshot
```

### Login Flow (When Required)

```javascript
// Navigate to login page
navigate(url="https://example.com/login")
wait(time=2)
snapshot()

// Fill credentials
// NOTE: Be cautious with passwords - consider having user enter manually
type(element="Username or email", ref="e5", text="myusername")

// Option 1: Have user enter password manually in browser
// Option 2: Type password (user consent required)
// type(element="Password", ref="e7", text="mypassword")

// Inform user to enter password manually if needed
// Then continue:

click(element="Sign in button", ref="e10")
wait(time=3)

// Verify login success
screenshot()
snapshot()
```

### Two-Factor Authentication

```javascript
// After initial login
wait(time=2)
snapshot()

// Check for 2FA prompt
// If 2FA code field appears:
// Option A: User enters code manually
// Option B: Automation enters code

// type(element="2FA code", ref="e15", text="123456")
// click(element="Verify", ref="e18")

wait(time=3)
screenshot()
```

### OAuth Login (Google, GitHub, etc.)

```javascript
// Navigate to site with OAuth
navigate(url="https://example-app.com")
wait(time=2)

// Click "Sign in with Google/GitHub"
snapshot()
click(element="Sign in with Google", ref="e12")

// If already logged in to provider, may auto-redirect
// If not, provider login page appears
wait(time=3)
snapshot()

// Handle provider login if needed
// (User may need to complete manually for security)

// Return to app
wait(time=2)
screenshot()
```

---

## Data Extraction

### Extract Table Data

```javascript
navigate(url="https://example.com/data")
wait(time=3)
snapshot()

// Tables appear in ARIA snapshot
// Look for table structure in output

// Example snapshot output might show:
// - table "Sales Data"
//   - rowgroup
//     - row
//       - cell "January"
//       - cell "$10,000"

// Parse snapshot text to extract data
// Note: Direct data export may require JavaScript evaluation
// (if browser_evaluate tool is available)

get_console_logs()
screenshot()
```

### Scrape Article Content

```javascript
// Navigate to article
navigate(url="https://blog.example.com/article")
wait(time=3)
snapshot()

// Article content appears in snapshot
// Look for main content, headings, paragraphs

// Take screenshot for visual reference
screenshot()

// Check for any loading errors
get_console_logs()

// For long articles, may need to scroll (if supported)
// press_key(key="End")
// wait(time=1)
// snapshot()
```

### Collect Search Results

```javascript
// Search on a directory site
navigate(url="https://directory.example.com")
wait(time=2)
snapshot()

type(element="Search businesses", ref="e8", text="restaurants", submit=true)
wait(time=3)
snapshot()

// Results appear in snapshot
// Extract refs for each result

// Click through results to collect details
click(element="First result", ref="e20")
wait(time=2)
snapshot()  // Get detailed info

// Navigate back to results
go_back()
wait(time=2)
snapshot()

// Continue with next result
click(element="Second result", ref="e22")
// ... repeat
```

---

## E-commerce Tasks

### Product Search and Browse

```javascript
// Navigate to store
navigate(url="https://shop.example.com")
wait(time=3)
snapshot()

// Search for product
type(element="Search products", ref="e12", text="wireless headphones", submit=true)
wait(time=3)
snapshot()

// Apply filters
click(element="Filter by: Electronics", ref="e25")
wait(time=2)
snapshot()

// Sort results
select_option(element="Sort by", ref="e30", values=["price_low_high"])
wait(time=2)
snapshot()

// View product details
click(element="Product: Sony WH-1000XM4", ref="e40")
wait(time=3)
snapshot()

// Check availability, price
screenshot()
```

### Add to Cart

```javascript
// On product page
snapshot()

// Select options if needed
select_option(element="Color", ref="e15", values=["black"])
select_option(element="Size", ref="e18", values=["large"])
wait(time=1)

// Click add to cart
click(element="Add to cart button", ref="e25")
wait(time=2)

// Handle confirmation modal if appears
snapshot()

// Continue shopping or view cart
click(element="View cart", ref="e30")
wait(time=2)
snapshot()
screenshot()
```

### Checkout Process

```javascript
// From cart page
click(element="Proceed to checkout", ref="e20")
wait(time=3)
snapshot()

// Shipping information
type(element="Full name", ref="e25", text="John Doe")
type(element="Street address", ref="e27", text="123 Main St")
type(element="City", ref="e29", text="New York")
select_option(element="State", ref="e31", values=["NY"])
type(element="ZIP code", ref="e33", text="10001")
click(element="Continue to payment", ref="e35")

// Payment (usually user handles manually for security)
wait(time=3)
snapshot()
screenshot()

// User completes payment manually
// Then verify order confirmation
wait(time=5)
snapshot()
screenshot()
```

---

## Social Media

### Check Notifications

```javascript
// Navigate to platform
navigate(url="https://twitter.com")
wait(time=3)
snapshot()

// Click notifications
click(element="Notifications tab", ref="e15")
wait(time=2)
snapshot()

// Review notifications
screenshot()
```

### Read Feed

```javascript
navigate(url="https://linkedin.com/feed")
wait(time=3)
snapshot()

// Scroll to see more (if supported)
// press_key(key="End")
// wait(time=2)
// snapshot()

screenshot()
```

### Post Content (With Caution)

```javascript
// Navigate to platform
navigate(url="https://twitter.com/compose/tweet")
wait(time=2)
snapshot()

// Type post content
type(element="Tweet text", ref="e10", text="Hello from BrowserMCP automation!")

// IMPORTANT: Stop here and get user confirmation before posting
// click(element="Post", ref="e15")  // Only with explicit user approval
```

**Warning:** Automated social media posting may violate platform terms of service. Always get explicit user approval.

---

## Testing and Verification

### Page Load Performance

```javascript
// Test page load
navigate(url="https://example.com")
wait(time=1)
snapshot()

// Check for errors
get_console_logs()

// Verify key elements loaded
// Look for expected elements in snapshot
// - Header
// - Navigation
// - Main content
// - Footer

screenshot()
```

### Form Validation Testing

```javascript
navigate(url="https://example.com/signup")
wait(time=2)
snapshot()

// Test 1: Submit empty form
click(element="Submit", ref="e20")
wait(time=1)
snapshot()  // Check for validation errors

// Test 2: Invalid email
type(element="Email", ref="e12", text="not-an-email")
click(element="Submit", ref="e20")
wait(time=1)
snapshot()  // Check for email validation error

// Test 3: Password mismatch
type(element="Email", ref="e12", text="test@example.com")
type(element="Password", ref="e14", text="pass123")
type(element="Confirm password", ref="e16", text="pass456")
click(element="Submit", ref="e20")
wait(time=1)
snapshot()  // Check for mismatch error

screenshot()
```

### Responsive Design Check

```javascript
// Test at different viewports
// Note: Viewport resizing may require additional tools

// Desktop
navigate(url="https://example.com")
wait(time=2)
screenshot()

// May need to resize browser window manually
// Then refresh
navigate(url="https://example.com")
wait(time=2)
screenshot()
```

### Link Verification

```javascript
navigate(url="https://example.com")
wait(time=2)
snapshot()

// Find all links in snapshot
// Look for "link" role entries

// Test specific links
click(element="About Us link", ref="e15")
wait(time=2)
screenshot()

// Return home
go_back()
wait(time=2)

// Test another link
click(element="Contact link", ref="e18")
wait(time=2)
screenshot()
```

---

## Documentation Reading

### Read API Documentation

```javascript
// Navigate to docs
navigate(url="https://docs.example.com/api")
wait(time=3)
snapshot()

// Navigate through sections
click(element="Authentication", ref="e20")
wait(time=2)
snapshot()

// Read specific endpoint docs
click(element="GET /users", ref="e25")
wait(time=2)
snapshot()

// Extract code examples from snapshot
screenshot()
```

### Navigate Changelog

```javascript
navigate(url="https://github.com/example/repo/releases")
wait(time=3)
snapshot()

// Click latest release
click(element="Version 2.0.0", ref="e15")
wait(time=2)
snapshot()

// Read changes
screenshot()
```

---

## Workflow Patterns Summary

### The Standard Pattern

Most workflows follow this structure:

```javascript
// 1. Navigate
navigate(url="https://target-site.com")

// 2. Wait for load
wait(time=2)

// 3. Understand structure
snapshot()

// 4. Interact
click(element="Target", ref="eX")

// 5. Wait for changes
wait(time=2)

// 6. Verify
screenshot()
snapshot()

// 7. Debug if needed
get_console_logs()
```

### Iterative Exploration

```javascript
// Start at entry point
navigate(url="https://example.com")

// Explore iteratively
while (more_to_explore) {
  snapshot()           // See what's available
  click(element, ref)  // Explore deeper
  wait(time=2)         // Let it load
  screenshot()         // Visual check
}
```

### Data Collection Loop

```javascript
// Collect data from multiple similar pages
const items_to_check = ["item1", "item2", "item3"]

for (const item of items_to_check) {
  navigate(url=`https://example.com/items/${item}`)
  wait(time=2)
  snapshot()  // Extract data from snapshot
  screenshot() // Visual record
}
```

---

## Safety and Ethics

### Rate Limiting

Add delays to avoid overwhelming servers:

```javascript
// Between requests
wait(time=2)

// After errors
wait(time=5)

// For large batches
wait(time=3)  // Be respectful
```

### Respect Robots.txt

Check if automation is allowed on target sites.

### User Consent

Always confirm before:
- Posting content
- Making purchases
- Modifying data
- Accessing sensitive accounts

### Data Privacy

- Don't automate extraction of personal data without consent
- Be cautious with screenshots containing sensitive info
- Respect terms of service
