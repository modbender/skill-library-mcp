# Architecture Decision Template

## When to Use This Pattern

✅ **Use when:**
- Making a significant architectural choice with multiple viable options
- Decision has long-term implications (hard to reverse)
- Trade-offs are complex (no obvious "right" answer)
- Want to avoid groupthink or confirmation bias
- Creating Architecture Decision Record (ADR)

❌ **Don't use when:**
- Decision is trivial or easily reversible
- Only one option is viable
- Time-sensitive decision (need answer in <1 hour)
- Team has already reached consensus

## Team Structure

**Lead:** Facilitator who manages debate and synthesizes final ADR
**Teammates:** 2 advocates with opposing positions
- **Advocate A:** Argues for Option A (e.g., PostgreSQL, monolith, REST)
- **Advocate B:** Argues for Option B (e.g., MongoDB, microservices, GraphQL)

Optional: Add a third advocate for a third option if applicable.

## File/Directory Boundaries

```
architecture-decisions/
  adr-NNN-[decision-name]/
    proposal-option-A.md        # Advocate A's position
    proposal-option-B.md        # Advocate B's position
    debate-transcript.md        # Lead's synthesis of debate
    adr-NNN-[decision-name].md  # Final ADR
```

## Spawn Prompt (Copy-Paste Ready)

```markdown
I need to make an architectural decision: [DECISION - e.g., "Choose primary database for new microservice"]

**Context:**
- [BACKGROUND - e.g., "Building user profile service with 100K users, read-heavy workload"]
- [CONSTRAINTS - e.g., "Must support ACID transactions, team familiar with SQL"]
- [TIMELINE - e.g., "Decision needed by end of week, implementation starts next sprint"]

**Options:**
- Option A: [e.g., "PostgreSQL (relational)"]
- Option B: [e.g., "MongoDB (document)"]

**Decision criteria:**
- [CRITERION 1 - e.g., "Performance (read latency <10ms p99)"]
- [CRITERION 2 - e.g., "Team familiarity (reduce learning curve)"]
- [CRITERION 3 - e.g., "Scalability (support 10x growth)"]
- [CRITERION 4 - e.g., "Operational complexity (monitoring, backups)"]

Spawn 2 advocates using Sonnet (they will debate):

1. **Advocate for Option A: PostgreSQL**
   - Name: postgres-advocate
   - Position: Argue that PostgreSQL is the better choice
   - Output: proposal-option-A.md
   - Tasks:
     * Research strengths of PostgreSQL for this use case
     * Address each decision criterion from PostgreSQL perspective
     * Identify weaknesses of MongoDB
     * Provide concrete examples or case studies
     * Recommend PostgreSQL with evidence

2. **Advocate for Option B: MongoDB**
   - Name: mongo-advocate
   - Position: Argue that MongoDB is the better choice
   - Output: proposal-option-B.md
   - Tasks:
     * Research strengths of MongoDB for this use case
     * Address each decision criterion from MongoDB perspective
     * Identify weaknesses of PostgreSQL
     * Provide concrete examples or case studies
     * Recommend MongoDB with evidence

**Coordination rules:**
- Use delegate mode: I facilitate, advocates debate (I don't implement)
- Advocates work independently (no collaboration - they're adversaries)
- Advocates must argue their position honestly (no straw man arguments)
- Advocates should acknowledge trade-offs (not just list benefits)
- After both complete, I facilitate debate via messages
- Final ADR synthesizes both perspectives

**Debate structure:**
1. Advocates present their positions (5 min each)
2. Rebuttals (each advocate responds to the other's weaknesses)
3. Q&A (I ask clarifying questions)
4. Final statements (2 min each)

**After debate:**
I synthesize into ADR following standard format:
- Title
- Status (proposed)
- Context
- Decision
- Consequences (positive and negative)
- Alternatives considered
```

## Expected Outcomes

### Advocate Proposals

**proposal-option-A.md (PostgreSQL):**
```markdown
# Proposal: Use PostgreSQL for User Profile Service

## Executive Summary
PostgreSQL is the recommended choice due to:
1. ACID compliance for profile data integrity
2. Team familiarity reduces implementation risk
3. Mature ecosystem and operational tooling
4. Performance meets requirements (<10ms p99 for reads)

## Decision Criteria Analysis

### 1. Performance (Read latency <10ms p99)
**PostgreSQL:** ✅ **Meets requirement**
- Indexed reads: 1-3ms typical
- With proper indexing (email, user_id), easily achieves <10ms p99
- Read replicas for read-heavy workload
- Connection pooling (pgbouncer) for high concurrency

**Evidence:** Benchmarks show PostgreSQL with proper indexes handles 10K reads/s with p99 <5ms

### 2. Team Familiarity
**PostgreSQL:** ✅ **Strong advantage**
- Team has 5 years SQL experience
- Existing PostgreSQL infrastructure (monitoring, backups, DR)
- No learning curve for queries or schema design
- Faster implementation (no ramp-up time)

**MongoDB:** ❌ **Significant learning curve**
- Team has zero MongoDB experience
- Would need to learn aggregation pipeline, indexing strategies
- Est. 2-4 weeks ramp-up time

### 3. Scalability (Support 10x growth)
**PostgreSQL:** ✅ **Proven at scale**
- Supports 1M+ users with read replicas
- Vertical scaling (larger instances) + horizontal (read replicas)
- Partitioning available for >10M users
- Many examples of PostgreSQL at 100M+ user scale

**Evidence:** Instagram scaled to 1B users on PostgreSQL

### 4. Operational Complexity
**PostgreSQL:** ✅ **Lower complexity**
- Existing monitoring (Datadog integration)
- Existing backup/restore procedures
- Battle-tested DR playbooks
- Team knows how to troubleshoot

**MongoDB:** ❌ **Higher complexity**
- Need new monitoring setup
- New backup/restore procedures
- Team unfamiliar with troubleshooting

## Addressing MongoDB's Strengths

**Flexibility (schema changes):**
- User profiles are stable (name, email, bio, photo)
- Schema changes rare (maybe 1-2/year)
- PostgreSQL supports JSON columns for flexible fields
- Migrations are manageable with Alembic/Flyway

**Horizontal scaling:**
- Not needed for 100K-1M users (read replicas sufficient)
- If needed at 10M+ users, PostgreSQL partitioning available
- MongoDB's sharding advantage only relevant at extreme scale

## Recommendation

**Choose PostgreSQL** for the following reasons:
1. Meets all technical requirements
2. Zero learning curve for team
3. Leverages existing infrastructure
4. Lower operational risk
5. Faster implementation

**Risk mitigation:**
- Use JSON columns for any flexible/optional profile fields
- Plan for read replicas when traffic grows 3x
- Monitor query performance, add indexes proactively

## Estimated Timeline
- With PostgreSQL: 2 weeks to production
- With MongoDB: 4-6 weeks (includes 2 weeks learning curve)
```

**proposal-option-B.md (MongoDB):**
```markdown
# Proposal: Use MongoDB for User Profile Service

## Executive Summary
MongoDB is the recommended choice due to:
1. Schema flexibility for evolving profile requirements
2. Simpler scaling path (horizontal sharding)
3. Better performance for document-centric queries
4. Modern tooling and developer experience

## Decision Criteria Analysis

### 1. Performance (Read latency <10ms p99)
**MongoDB:** ✅ **Exceeds requirement**
- Indexed reads: 1-2ms typical (faster than PostgreSQL)
- Document model eliminates JOINs (profile = single document)
- Built-in caching (WiredTiger)
- Horizontally scalable from day one

**PostgreSQL:** ⚠️ **Meets requirement, but**
- Requires JOINs if profile data is normalized
- Read replicas add operational complexity

### 2. Team Familiarity
**MongoDB:** ❌ **Learning curve exists**
- Team has no MongoDB experience (2-4 week ramp-up)
- However:
  * MongoDB syntax is intuitive (JavaScript-like)
  * Excellent documentation and tutorials
  * Atlas (managed service) eliminates ops learning curve

**PostgreSQL:** ✅ **Team is familiar**
- 5 years SQL experience is a valid advantage
- But: Profile service is greenfield (good time to learn new tech)

### 3. Scalability (Support 10x growth)
**MongoDB:** ✅ **Superior scaling path**
- Native horizontal sharding (built-in, no extra tools)
- Automatic balancing across shards
- Scales to billions of documents
- No single point of failure

**PostgreSQL:** ⚠️ **Vertical scaling, then partitioning**
- Initial scaling via read replicas (works up to 1M users)
- Partitioning complex (requires careful planning)
- Sharding not native (need Citus or manual sharding)

**Evidence:** MongoDB powers systems with >100M users routinely

### 4. Operational Complexity
**MongoDB:** ✅ **Atlas reduces complexity**
- MongoDB Atlas (managed service) handles:
  * Monitoring
  * Backups
  * Scaling
  * High availability
- Team doesn't need deep MongoDB ops knowledge

**PostgreSQL:** ✅ **Existing infrastructure**
- Existing monitoring/backups is an advantage
- But: Adds another database to maintain

## Addressing PostgreSQL's Strengths

**ACID transactions:**
- MongoDB supports ACID transactions (since v4.0)
- Single-document operations are atomic by default
- Multi-document transactions available if needed

**Team familiarity:**
- Valid concern, but:
  * Profile service is isolated (good learning opportunity)
  * MongoDB learning curve is shallow (2 weeks, not 2 months)
  * Investment pays off for future services

**Mature ecosystem:**
- MongoDB ecosystem is mature (15+ years old)
- Excellent drivers for all languages
- Rich tooling (Compass, Atlas, aggregation pipeline)

## Recommendation

**Choose MongoDB** for the following reasons:
1. Better long-term scalability (native sharding)
2. Schema flexibility for evolving profiles (avoid migrations)
3. Superior performance for document-centric queries
4. Atlas reduces operational burden
5. Good learning investment for team

**Risk mitigation:**
- Use MongoDB Atlas (managed service) to reduce ops learning curve
- Pair senior dev with MongoDB expert for first 2 weeks
- Build POC to validate performance before committing
- Plan for 4-week timeline (includes ramp-up)

## Estimated Timeline
- With MongoDB: 4 weeks (includes 2 weeks learning + POC)
- With PostgreSQL: 2 weeks

**Trade-off:** 2 extra weeks upfront, but better long-term scaling
```

### Debate and Final ADR

**adr-005-database-choice.md:**
```markdown
# ADR-005: Database Choice for User Profile Service

## Status
Accepted (2026-02-16)

## Context
We are building a new user profile service to replace the monolithic profile module. The service must support:
- 100K users initially, scaling to 1M+ over 2 years
- Read-heavy workload (95% reads, 5% writes)
- ACID transactions for profile updates
- <10ms p99 read latency
- Team has 5 years SQL experience, zero NoSQL experience

## Decision
**We will use PostgreSQL with JSON columns for flexible fields.**

## Rationale

### Why PostgreSQL Over MongoDB

**Immediate priorities:**
1. **Speed to production:** Team familiarity means 2-week implementation vs 4-6 weeks with MongoDB
2. **Lower risk:** Leveraging existing infrastructure (monitoring, backups, DR playbooks)
3. **Sufficient scalability:** Read replicas + vertical scaling handles 1M users
4. **Team productivity:** No learning curve means full productivity from day one

**MongoDB's advantages don't justify the trade-offs:**
1. **Schema flexibility:** User profiles are stable (name, email, bio, photo). PostgreSQL JSON columns handle flexible fields without MongoDB complexity.
2. **Horizontal scaling:** Not needed at current scale (100K-1M users). If needed at 10M+ users, we can revisit.
3. **Performance:** Both meet <10ms requirement. PostgreSQL 1-3ms vs MongoDB 1-2ms is negligible.

### Compromise: Best of Both Worlds
- Use PostgreSQL for core profile fields (JSONB columns for flexible/optional fields)
- Benefit: Relational integrity + flexibility
- Example schema:
  ```sql
  CREATE TABLE profiles (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    photo_url TEXT,
    metadata JSONB,  -- flexible fields
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
  );
  CREATE INDEX idx_profiles_email ON profiles(email);
  CREATE INDEX idx_profiles_metadata ON profiles USING GIN(metadata);
  ```

## Consequences

### Positive
- ✅ Fast implementation (2 weeks to production)
- ✅ Leverages team expertise (no learning curve)
- ✅ Uses existing infrastructure (lower ops overhead)
- ✅ Meets all technical requirements
- ✅ JSONB provides schema flexibility when needed

### Negative
- ⚠️ Vertical scaling required initially (horizontal scaling is harder)
- ⚠️ May need to revisit at 10M+ users (partitioning or migration)
- ⚠️ Missed opportunity to learn MongoDB (team stays SQL-focused)

## Alternatives Considered

### MongoDB
**Rejected because:**
- 2-4 week learning curve delays implementation
- Operational complexity (new monitoring, backups, troubleshooting)
- Scaling advantage not needed at current scale
- Risk outweighs benefit for this use case

**When to reconsider:**
- If we reach 10M+ users and need native sharding
- If profile schema becomes highly dynamic (frequent changes)
- If team gains MongoDB expertise via other projects

### DynamoDB
**Not seriously considered because:**
- Vendor lock-in (AWS only)
- Limited query flexibility (requires careful key design)
- Team has zero DynamoDB experience (even steeper learning curve than MongoDB)

## Review Date
**2027-02-16 (1 year):** Review decision once we reach 500K users. Consider MongoDB or partitioning if scaling challenges emerge.

## References
- [PostgreSQL JSON column documentation](https://www.postgresql.org/docs/current/datatype-json.html)
- [Instagram scaled to 1B users on PostgreSQL](https://instagram-engineering.com/scaling-instagram-infrastructure-16b48e51d74c)
- [MongoDB Atlas documentation](https://www.mongodb.com/docs/atlas/)
```

## Timing

**Sequential research:** ~60-90 minutes (30-45 min per option)
**Parallel debate:** ~30-40 minutes (advocates work simultaneously)

**Speedup:** ~2x faster

## Cost Estimate

**Team:** 1 Opus lead + 2 Sonnet advocates
**Duration:** ~35 minutes
**Estimated cost:** $18-25

## Success Metrics

✅ **Successful if:**
- Both advocates present strong, honest arguments
- Rebuttals address actual weaknesses (not straw men)
- Final ADR acknowledges trade-offs (not just benefits)
- Decision is based on evidence, not gut feel
- Review date set for reassessing decision

❌ **Red flags:**
- One advocate presents weak argument (debate is rigged)
- ADR ignores trade-offs or negative consequences
- Decision based on personal preference, not criteria
- No plan for revisiting decision

## Variations

### Three-Option Debate
Add a third advocate for a third option:
- Example: PostgreSQL vs MongoDB vs DynamoDB
- Triad debate structure (each advocate rebuts other two)

### Expert Panel
Instead of adversarial advocates, spawn 3 impartial experts who each analyze all options and recommend independently.

**Use when:** Adversarial debate feels forced (e.g., all options are equally viable)

## Follow-Up Actions

After ADR complete:
1. Share ADR with team for feedback (1 week review period)
2. Incorporate feedback, update ADR if needed
3. Mark ADR as "Accepted" after approval
4. Proceed with implementation
5. Schedule review date (add to calendar)
