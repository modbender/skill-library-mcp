# Nova Act Cookbook

Best practices for using Amazon Nova Act safely and effectively in browser automation.

## Core Principles

### 1. Safety First — Stop Before Material Impact

**ALWAYS stop testing before actions that cause monetary impact, external communication, account creation, or data modification.**

Nova Act automates a real browser. Any action it takes has real-world consequences. Before every automation task, evaluate whether the workflow approaches a material-impact boundary.

### Material Impact Keywords

The bundled runner script (`scripts/nova_act_runner.py`) defines `MATERIAL_IMPACT_KEYWORDS` to detect tasks that require safety stops:

```python
MATERIAL_IMPACT_KEYWORDS = [
    # Monetary
    "buy", "purchase", "checkout", "pay", "subscribe", "donate", "order",
    # Communication
    "post", "publish", "share", "send", "email", "message", "tweet",
    # Account creation
    "sign up", "register", "create account", "join",
    # Submissions
    "submit", "apply", "enroll", "book", "reserve",
    # Destructive
    "delete", "remove", "cancel",
]
```

When these keywords are detected, `apply_safety_guardrails()` appends safety instructions to the task prompt, preventing Nova Act from completing irreversible actions. The function modifies the actual prompt sent to Nova Act — this is an active behavioral gate, not just a warning.

### How to Test Safely

When a task approaches a material-impact boundary, follow this 4-step pattern:

1. **Navigate TO the final step** (checkout page, publish screen, submit button)
2. **Verify the final action is accessible** (button exists, is enabled, is visible)
3. **Use `act_get()` to observe without acting** — DO NOT click the final action button
4. **Report findings** to the user without completing the action

```python
# Example: Observe the checkout button — DO NOT click it
can_checkout = nova.act_get(
    "Is there a 'Complete Purchase' or 'Pay Now' button visible and enabled?",
    schema=bool
)
# Report readiness but DO NOT execute the final action
```

## Safe Workflow Examples

### Safe Flight Search (Read-Only)

```python
with NovaAct(starting_page="https://google.com/flights") as nova:
    nova.act("""
        Search for flights from NYC to LAX.
        Set departure date to March 15, 2025.
        Click Search.
        Sort by price, lowest first.
    """)

    flights = nova.act_get(
        "Get available flights with airline, price, departure and arrival times",
        schema=list[dict]
    )
    # SAFETY STOP: Do not select a flight or proceed to booking.
    # Report the search results to the user.
```

### Safe E-Commerce Research (Read-Only)

```python
with NovaAct(starting_page="https://example.com") as nova:
    nova.act("Search for 'wireless headphones' and view results")

    products = nova.act_get(
        "Get the top 5 product names, prices, and ratings",
        schema=list[dict]
    )
    # SAFETY STOP: Do not add to cart, proceed to checkout, or enter payment.
    # Report the product comparison to the user.
```

### Safe Form Testing (Observe-Only)

```python
with NovaAct(starting_page="https://example.com/contact") as nova:
    nova.act("Fill name 'Test User' and email 'test@example.com'")

    submit_ready = nova.act_get(
        "Is the submit button visible and enabled?",
        schema=bool
    )
    # SAFETY STOP: Do not click submit. Report form readiness.
    print(f"Form ready to submit: {submit_ready}")
```

### Safe Booking Flow (Observe-Only)

```python
with NovaAct(starting_page="https://example.com/hotels") as nova:
    nova.act("""
        Search for hotels in San Francisco.
        Set check-in to April 1, 2025 and check-out to April 3, 2025.
        Select the first available hotel.
        Proceed to the booking page.
    """)

    # SAFETY STOP: Verify booking button exists but DO NOT click it
    booking_ready = nova.act_get(
        "Is there a 'Book Now', 'Reserve', or 'Complete Booking' button visible?",
        schema=bool
    )
    # Report booking page details without completing the reservation
```

**Key principle:** Navigate TO the final step, verify the action is accessible, but NEVER complete it. Use `act_get()` to observe and report rather than `act()` to execute.

## 2. Break Tasks into Small Steps

Nova Act works most reliably when tasks can be accomplished in **fewer than 30 steps**.

**Do not** combine too many unrelated actions:
```python
# Too many unrelated steps — avoid
nova.act("search flights, book hotel, rent car, find restaurant")
```

**Do** break into focused steps:
```python
flights = nova.act_get("Search flights from SFO to JFK", schema=list[dict])
# Process results, then move to next task
```

## 3. Be Direct and Specific

Make prompts clear about exactly what should happen.

```python
# Vague — avoid
nova.act("Let's see what's available")

# Specific — prefer
nova.act("Click the 'Search' button to see available flights")
```

## 4. Use Schemas for Data Extraction

Always provide a schema to `act_get()` for structured, predictable output:

```python
from pydantic import BaseModel

class SearchResult(BaseModel):
    title: str
    url: str
    description: str

results = nova.act_get(
    "Get the first 5 search results",
    schema=list[SearchResult]
)
```

## 5. Handle Errors Gracefully

Browser automation can fail due to page changes, slow loads, or unexpected UI. Always wrap Nova Act calls in error handling:

```python
try:
    result = nova.act_get("Get the page title", schema=str)
except Exception as e:
    print(f"Nova Act error: {e}")
    # Fall back or report the failure
```

## 6. Use Screenshots for Verification

Capture visual evidence of results:

```python
from pathlib import Path

nova.page.screenshot(path="result.png")
print(f"MEDIA: {Path('result.png').resolve()}")
```

## Common Patterns

### Data Extraction (Read-Only)

The safest automation pattern — navigates and extracts data without modifying anything:

```python
with NovaAct(starting_page=url) as nova:
    data = nova.act_get("Extract the information from this page", schema=MySchema)
    print(data)
```

### Navigation + Observation

Navigate through a site and report what you find:

```python
with NovaAct(starting_page=url) as nova:
    nova.act("Click on the 'Products' link in the navigation")
    products = nova.act_get("List all product categories visible", schema=list[str])
```

### Form Interaction (With Safety Stop)

Fill forms to test functionality, but stop before submission:

```python
with NovaAct(starting_page=url) as nova:
    nova.act("Fill the search form with 'test query'")
    nova.act("Click the search button")  # Search is safe — read-only
    results = nova.act_get("Get search results", schema=list[str])

    # For contact/signup forms: SAFETY STOP before final submit
    # Use act_get() to verify the submit button is accessible, then report
```
