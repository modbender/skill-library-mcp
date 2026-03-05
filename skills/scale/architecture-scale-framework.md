# Architecture Scale Framework

Apply this when software architecture cannot support product velocity, reliability, or team autonomy.

## Decision Flow

### 1. Confirm the Failure Pattern
- Delivery slowdown from coupling
- Reliability incidents from shared blast radius
- Team conflicts from unclear ownership boundaries

Do not split architecture based on trend pressure alone.

### 2. Strengthen Boundaries Before Splits
- Define clear domain boundaries and contracts
- Standardize API and event versioning rules
- Establish ownership per boundary with on-call accountability

### 3. Choose the Minimum Structural Change
- Keep modular monolith when deployment and ownership can still scale
- Split services only where independent scaling or autonomy is proven
- Extract platforms only for repeated cross-team bottlenecks

### 4. Manage Coupling Debt Explicitly
- Track top coupling points and their operational impact
- Set budget for interface cleanup each sprint
- Prevent new cross-boundary dependencies without review

### 5. Protect Delivery During Migration
- Use strangler paths for incremental cutover
- Keep compatibility layers with sunset dates
- Measure lead time and incident rate before and after each step

## Red Flags

- Service count growing faster than team maturity.
- New architecture patterns without observability or runbooks.
- Migration roadmap that lacks rollback checkpoints.
