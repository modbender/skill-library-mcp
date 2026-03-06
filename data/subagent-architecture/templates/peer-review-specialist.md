# Peer Review Specialist Pattern

**Use case:** External validation via bot-to-bot collaboration (code review, design critique, fact-checking, bias detection)

## Core Philosophy

**Federated Trust:**
- External agents bring fresh perspective (not influenced by your workspace context)
- Specialists may have domain expertise you lack (legal review, accessibility audit, security pentesting)
- Cross-agent collaboration validates assumptions (your agent's blindspots checked by peer)
- Trust earned through track record (peer reputation system)

**When peer review matters:**
- High-stakes decisions (legal implications, security vulnerabilities)
- Bias detection (your agent might have learned your blind spots)
- Domain expertise gap (you don't have a specialist for this area)
- Fresh perspective (too close to the problem, need outside view)

## Architecture

```
Your Agent
    │
    ├─ Prepares review package (artifact + context)
    │       │
    │       ├─ Sanitizes sensitive data
    │       ├─ Documents review criteria
    │       └─ Packages as shareable artifact
    │
    ├─ Contacts Peer Agent (via message tool or API)
    │       │
    │       └─ Peer spawns ReviewerAgent
    │               │
    │               ├─ Reviews artifact against criteria
    │               ├─ Provides feedback (structured format)
    │               └─ Returns: PEER_REVIEW.md
    │
    └─ Integrates feedback (accept, reject, iterate)
```

## Template Structure

```markdown
## [PeerReviewerName] - External validation specialist

**Type:** External collaboration (federated)
**Peer:** [agent owner/identity, e.g., "Smith's CodeReviewBot"]
**Domain:** [expertise area, e.g., "Security audits", "Legal compliance", "UX accessibility"]
**Trust level:** [verified/provisional/experimental]

### Purpose
Request external review of [artifact type] from trusted peer with [domain expertise].

### Review Package Format
**Sanitized artifact submission:**
\`\`\`json
{
  "artifact_type": "code|design|document|data",
  "content": "[sanitized content or URL]",
  "review_criteria": {
    "focus_areas": ["security", "performance", "accessibility"],
    "constraints": ["must comply with GDPR", "budget < $100/month"],
    "questions": ["Is this approach secure?", "Are there hidden costs?"]
  },
  "context": "[minimal context, no sensitive data]",
  "deadline": "YYYY-MM-DD",
  "requester": "$OWNER_NAME's agent"
}
\`\`\`

### Response Format
**Structured feedback:**
\`\`\`json
{
  "reviewer": "Peer agent identity",
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "verdict": "approved|conditional|rejected",
  "findings": [
    {
      "severity": "critical|major|minor",
      "category": "security|performance|correctness|style",
      "issue": "Description of problem",
      "recommendation": "How to fix"
    }
  ],
  "summary": "Overall assessment",
  "confidence": "0.0-1.0 (reviewer's confidence in their assessment)"
}
\`\`\`

### Communication Protocol
**How to contact peer:**
1. **Discord DM** (if peer bot is on same server)
2. **API endpoint** (if peer provides review service)
3. **Message queue** (federated agent network)
4. **Manual relay** (human forwards review request)

### Example: Discord-based Peer Review
\`\`\`javascript
// Your agent sends message
message({
  action: "send",
  target: "peer-reviewer-bot-user-id",
  message: "Review request: [package JSON or URL]"
})

// Wait for peer's response
// Peer bot processes, spawns its own reviewer subagent
// Returns structured feedback via Discord DM
```

## Real-World Example

**Smith's CodeReviewBot** (fictional external peer):

### Review Request Flow
```markdown
1. **Your agent:** Prepares code for review
   - Sanitizes: removes API keys, personal data, workspace paths
   - Packages: GitHub gist or Discord code block
   - Documents: "Review for SQL injection vulnerabilities"

2. **Contact Smith's bot:**
   message({
     action: "send",
     target: "smith-review-bot",
     message: "Code review request:\n[sanitized code]\n\nFocus: SQL injection, input validation"
   })

3. **Smith's bot:** Spawns SecurityReviewer subagent
   - Analyzes code with security focus
   - Checks against OWASP Top 10
   - Generates findings report

4. **Peer response:** Structured feedback returned
   {
     "verdict": "conditional",
     "findings": [
       {
         "severity": "critical",
         "category": "security",
         "issue": "SQL query uses string concatenation (line 42)",
         "recommendation": "Use parameterized queries"
       }
     ],
     "summary": "Found 1 critical SQL injection risk, 2 minor issues"
   }

5. **Your agent:** Integrates feedback
   - Spawns CoderAgent to fix critical issue
   - Logs review in memory/peer-reviews.md
   - Optionally: Re-submit for follow-up review
```

## Trust & Reputation System

### Trust Levels

**Verified Peers** (high trust):
- Known agent owner (established relationship)
- Track record of accurate reviews (95%+ agreement with human audits)
- Domain certification (verified expertise)
- Accepts reviews without human approval

**Provisional Peers** (medium trust):
- New collaboration, limited history
- Recommendations treated as suggestions (not blockers)
- Human approval required for critical findings

**Experimental Peers** (low trust):
- First-time collaboration
- Reviews used for comparison only (validate against verified peers)
- No automatic actions on feedback

### Tracking Peer Performance

Store in `memory/peer-reviews.md`:
```markdown
## Peer Review History

### Smith's CodeReviewBot
- **Reviews completed:** 12
- **Accuracy:** 91% (11/12 reviews matched human audit)
- **False positives:** 1 (flagged non-issue as critical)
- **Missed issues:** 0
- **Trust level:** Verified
- **Domains:** Security, code quality

### ExperimentalReviewBot
- **Reviews completed:** 2
- **Accuracy:** 50% (1/2 matched human audit)
- **Trust level:** Experimental (more data needed)
```

## Security Considerations

### Data Sanitization Checklist
- [ ] Remove API keys, passwords, tokens
- [ ] Redact user names, email addresses, personal data
- [ ] Replace workspace paths with generic placeholders
- [ ] Sanitize URLs (remove query params with session IDs)
- [ ] Check for embedded secrets in code comments
- [ ] Remove organization-specific business logic (if proprietary)

### Review Scope Limits
**What to share:**
- Generic code patterns (common algorithms, utilities)
- Public-facing designs (UX mockups for public products)
- Sanitized data schemas (no actual data)

**What NOT to share:**
- Production credentials or API keys
- User data (even anonymized if subject to GDPR/CCPA)
- Proprietary algorithms (trade secrets)
- Infrastructure details (internal network topology)

## Cost Optimization

**Peer reviews vs internal review:**
- **Internal reviewer (your CoderAgent):** $0.30, 10 minutes, knows your codebase
- **Peer review (external):** $0.00 (peer's cost), 30-60 minutes, fresh perspective

**When to use peer review:**
- High-stakes (security vulnerability could cost $10,000+)
- Domain gap (you don't have security specialist)
- Bias check (your agent consistently misses certain issues)

**When to use internal review:**
- Low-stakes (styling, documentation)
- Domain expertise available (you have DevOps subagent)
- Fast turnaround needed (peer review may take hours/days)

## Integration

Works with:
- **task-routing** (auto-request peer review for high-risk tasks)
- **drift-guard** (peer validates behavioral alignment)
- **cost-governor** (track peer review ROI: cost saved by catching bugs early)

## Federated Agent Network

**Vision:** OpenClaw agents discover and collaborate with peers automatically.

### Discovery Protocol (Future)
```yaml
# peers.yaml - Trusted peer registry
peers:
  - name: "Smith's SecurityBot"
    endpoint: "https://smith.example.com/review"
    domains: ["security", "code-quality"]
    trust_level: "verified"
    cost: "free" # or "$0.50/review"
    
  - name: "AccessibilityAuditor"
    endpoint: "discord:user:123456789"
    domains: ["accessibility", "UX"]
    trust_level: "provisional"
```

### Auto-routing to Peers
```javascript
// task-routing integration
if (task.domain === "security" && !has_internal_specialist("security")) {
  const peer = find_peer({ domain: "security", trust: "verified" })
  
  if (peer) {
    request_peer_review(peer, sanitize(artifact))
  } else {
    escalate_to_human("No security specialist available")
  }
}
```

## Reciprocal Reviews

**Offer review services to peers:**
```markdown
## Your Review Service

**Domains offered:** [your expertise areas]
**Endpoint:** [Discord ID, API URL, or email]
**Cost:** Free (community reciprocity) or $X per review
**SLA:** 24 hour turnaround for standard reviews
**Specializations:**
- Wuxia/Xianxia worldbuilding review
- Writing craft feedback (AuthorAgent collaboration)
- Task routing architecture audit
```

**Benefits:**
- Learn from reviewing others' work
- Build reputation in agent community
- Access to reciprocal reviews (peer helps you → you help peer)
- Contribute to federated agent ecosystem

## Example Workflow: Multi-Peer Validation

**High-stakes feature:** Payment processing integration

```
Your Agent
    │
    ├─ Internal design (SystemArchitect)
    │
    ├─ Peer Review 1: Smith's SecurityBot
    │       └─ Focus: Vulnerability assessment
    │
    ├─ Peer Review 2: LegalComplianceBot
    │       └─ Focus: PCI-DSS compliance
    │
    ├─ Peer Review 3: CostOptimizerBot
    │       └─ Focus: Transaction fee analysis
    │
    ├─ Synthesize feedback (all 3 reviews)
    │       ├─ Security: 2 critical fixes required
    │       ├─ Legal: Compliant after security fixes
    │       └─ Cost: Recommendation to batch transactions
    │
    └─ Implement with confidence (validated by 3 specialists)
```

**Total cost:** $0 (peer reviews) + $0.80 (your internal agents) = High confidence, low cost

## Ethical Considerations

- **Informed consent:** Peer should know you're sharing sanitized artifacts
- **Data ownership:** Don't share user data without permission
- **Credit peers:** If peer review leads to valuable insight, acknowledge in EVOLOG
- **Reciprocity:** Offer reviews back (don't just take)
- **Feedback loop:** Report back if peer's advice was helpful (improves their accuracy)
