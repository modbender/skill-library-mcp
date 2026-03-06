# Patterns - Second-Order Thinking

> **Reference patterns only.** Common consequence chains to watch for.

## Universal Patterns

### The Cobra Effect
First: Incentive created to solve problem
Second: People optimize for incentive, not problem
Third: Problem worsens because incentive misaligned

*Example: Paying for dead cobras → people breed cobras*

Watch for: Any incentive-based solution.

### The Streisand Effect
First: Attempt to hide/suppress information
Second: Attention drawn to suppression attempt
Third: Information spreads far more than it would have

*Example: Demanding removal of content → content goes viral*

Watch for: Reputation management, content removal, secrecy.

### Goodhart's Law
First: Metric chosen as target
Second: People optimize metric at expense of underlying goal
Third: Metric improves while actual outcomes worsen

*Example: Lines of code as productivity metric → verbose code*

Watch for: Any KPI or OKR.

### The Lindy Effect
First: Something survives initial period
Second: Survival signals robustness
Third: Expected future lifespan increases

*Example: Book in print for 50 years → likely in print for 50 more*

Watch for: Technology choices, methodology adoption.

## Business Patterns

### Price Increase Chain
```
Price up →
  ├→ Short-term revenue up
  ├→ Price-sensitive customers leave
  ├→ Remaining customers expect more value
  └→ Brand perception shifts toward premium
      └→ Attracts premium-seeking customers
      └→ Competitors claim "affordable" positioning
```

### Hiring Chain
```
New hire →
  ├→ Capacity increases (1st order)
  ├→ Training load increases temporarily
  ├→ Team dynamics shift
  └→ Culture affected by new person's habits
      └→ If senior: others adopt their patterns
      └→ If junior: reveals mentorship capability
```

### Feature Addition Chain
```
New feature →
  ├→ Some users happy
  ├→ Complexity increases
  ├→ Support tickets for new feature
  └→ Maintenance burden forever
      └→ Future features slower
      └→ Technical debt compounds
```

### Layoff Chain
```
Layoffs →
  ├→ Costs reduced immediately
  ├→ Remaining team overworked
  ├→ Trust eroded ("am I next?")
  └→ Best performers update resumes
      └→ Talent drain
      └→ Institutional knowledge lost
```

## Personal Patterns

### Saying Yes Chain
```
Say yes to commitment →
  ├→ Immediate social approval
  ├→ Calendar fills
  ├→ Energy depletes
  └→ Quality of all commitments drops
      └→ Reputation for unreliability
      └→ Fewer meaningful opportunities
```

### Saying No Chain
```
Say no to request →
  ├→ Immediate disappointment from requester
  ├→ Time protected
  ├→ Precedent set for boundaries
  └→ Future requests filtered better
      └→ Respect for your time increases
      └→ Higher-quality opportunities arrive
```

### Shortcut Chain
```
Take shortcut →
  ├→ Immediate time saved
  ├→ Skill not developed
  ├→ Dependency on shortcut
  └→ When shortcut unavailable, stuck
      └→ Others who didn't shortcut surpass you
```

## Technical Patterns

### Dependency Addition Chain
```
Add dependency →
  ├→ Immediate functionality gained
  ├→ Attack surface increased
  ├→ Update burden added
  └→ Dependency's roadmap affects you
      └→ Breaking changes force rewrites
      └→ Security vuln in dep = vuln in you
```

### Quick Fix Chain
```
Quick fix deployed →
  ├→ Immediate problem solved
  ├→ Root cause unaddressed
  ├→ Fix becomes load-bearing
  └→ Future changes must work around fix
      └→ Complexity compounds
      └→ Eventually: "we need a rewrite"
```

## How to Use This File

1. When analyzing a decision, scan for matching patterns
2. If pattern matches, trace the known chain
3. Adjust for context (patterns are templates, not predictions)
4. Add new patterns when you observe them

## Adding New Patterns

```markdown
### [Pattern Name]
```
Trigger →
  ├→ First-order effect
  ├→ Another first-order effect
  └→ Second-order effect
      └→ Third-order effect
```

*Example: [real example]*

Watch for: [triggers that indicate this pattern].
```
