# User Story Patterns — Product Owner

## Standard User Story

The classic format that works for most features:

```
As a [user type]
I want [capability]
So that [benefit]

Acceptance Criteria:
- Given [context], when [action], then [outcome]
- Given [context], when [action], then [outcome]
```

### Good Example
```
As a mobile app user
I want to save articles for offline reading
So that I can read during my commute without internet

Acceptance Criteria:
- Given I'm viewing an article, when I tap "Save Offline", then the article downloads
- Given I have saved articles, when I open the app offline, then I can read them
- Given I'm online again, when I view a saved article, then it syncs any updates
```

### Bad Example
```
As a user
I want offline mode
So that it works offline
```
Problems: vague user, vague capability, circular benefit.

## Technical Story

For infrastructure, refactoring, or enabling work:

```
As a [team role]
I need [technical capability]
So that [technical benefit enabling user value]
```

### Example
```
As the development team
We need to upgrade the database to PostgreSQL 15
So that we can use JSON path queries for the search feature

Acceptance Criteria:
- Given the upgrade is complete, when running the test suite, then all tests pass
- Given production data, when migrated, then no data loss occurs
- Given the new version, when running queries, then performance equals or exceeds current
```

## Bug Fix Story

For defects that need tracking:

```
Current: [what happens now]
Expected: [what should happen]
Impact: [who is affected, severity]
Steps to Reproduce:
1. [step]
2. [step]
```

### Example
```
Current: Checkout button disappears on mobile Safari
Expected: Checkout button visible and functional
Impact: 15% of mobile users cannot complete purchase (Critical)
Steps to Reproduce:
1. Open cart on iPhone Safari
2. Scroll down to view all items
3. Scroll back up
4. Button is gone
```

## Spike Story

For research and exploration:

```
Spike: [question to answer]
Timebox: [max time]
Output: [deliverable]
```

### Example
```
Spike: Can we integrate with Stripe Connect for marketplace payments?
Timebox: 2 days
Output: Technical feasibility doc with API requirements and effort estimate
```

## Epic Structure

For large features that span multiple sprints:

```
Epic: [name]
Goal: [outcome]
Success Metric: [how we'll know it worked]

Stories:
1. [Story title] — [brief description]
2. [Story title] — [brief description]
3. [Story title] — [brief description]
```

## Acceptance Criteria Patterns

### Given/When/Then (Gherkin)
Best for behavior-driven scenarios:
```
Given I am logged in as an admin
When I click "Delete User"
Then a confirmation dialog appears
And the user is not deleted until confirmed
```

### Checklist Style
Best for simple validations:
```
Acceptance Criteria:
- [ ] Form validates email format
- [ ] Error message shows for invalid input
- [ ] Success message shows after submission
- [ ] Data appears in admin dashboard
```

### Rules-Based
Best for complex business logic:
```
Acceptance Criteria:
- Discount applies only to orders over $100
- Maximum discount is 30%
- Discount codes are single-use
- Expired codes show "Code expired" message
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Solution masquerading as story | "Add a button" instead of "enable action" | Focus on user need |
| Vague user | "As a user" | Specify user type |
| No benefit | "So that I can do X" (circular) | Connect to real outcome |
| Too big | Can't fit in sprint | Split into smaller stories |
| No acceptance criteria | "We'll know it when we see it" | Define testable criteria |
| Implementation details | "Using React and Redux" | Focus on behavior |

## Splitting Large Stories

When a story is too big, split by:

| Split By | Example |
|----------|---------|
| User type | Admin vs regular user |
| Action | Create vs edit vs delete |
| Data | One item vs bulk |
| Platform | Web vs mobile |
| Scenario | Happy path vs error handling |
| Performance | Basic vs optimized |

### Example Split
**Original:** "As a user, I want to manage my profile"

**Split:**
1. As a user, I want to view my profile
2. As a user, I want to edit my name and email
3. As a user, I want to upload a profile photo
4. As a user, I want to change my password
5. As a user, I want to delete my account
