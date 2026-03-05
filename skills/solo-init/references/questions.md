# /init — AskUserQuestion Specifications

Referenced by SKILL.md step 3, 5, 6, 7.

## Round 0: Org Defaults (5 questions)

```
Question 1: "What is your reverse-domain prefix for app IDs?"
Header: "Bundle ID"
multiSelect: false
Options:
- "com.yourcompany" — "Example: com.yourcompany.myapp"
- "com.mycompany" — "Example: com.mycompany.myapp"
- "io.myname" — "Example: io.myname.myapp"

Question 2: "Apple Developer Team ID? (optional, for iOS signing)"
Header: "Apple Team"
multiSelect: false
Options:
- "Skip" — "No iOS apps, skip for now"
- "Enter Team ID" — "10-char alphanumeric, find at developer.apple.com → Membership"

Question 3: "GitHub username or org for new repos?"
Header: "GitHub"
multiSelect: false
Options:
- "your-github-username" — "Personal GitHub account"
- "my-org" — "Organization account"

Question 4: "Where do you keep projects?"
Header: "Projects dir"
multiSelect: false
Options:
- "~/projects" — "Default projects directory"
- "~/code" — "Simple code directory"
- "~/workspace" — "Workspace directory"

Question 5: "Where is your knowledge base repo? (optional)"
Header: "KB repo"
multiSelect: false
Options:
- "~/knowledge-base" — "Default knowledge base location"
- "Skip" — "No knowledge base, skip for now"
```

## Round 1: Philosophy & Values (4 questions)

```
Question 1: "What drives you to build products?"
Header: "Motivation"
multiSelect: true
Options:
- "Privacy & data ownership" — "Users own their data, on-device processing, no cloud dependency"
- "Speed to market" — "Ship fast, learn fast, iterate. Market teaches better than planning"
- "Creative freedom" — "Build what doesn't exist yet, express ideas through products"
- "Financial independence" — "Revenue-generating products, sustainable solo business"

Question 2: "What will you NEVER build?"
Header: "Hard no's"
multiSelect: true
Options:
- "Dark patterns & addiction" — "No engagement tricks, no manipulative UX, no vanity metrics"
- "Surveillance & tracking" — "No selling user data, no hidden analytics, no ad-tech"
- "Subscription traps" — "No lock-in, no cancellation friction, honest pricing"
- "Exploitation" — "No extracting value from vulnerable people, no discrimination"

Question 3: "How do you think about user data?"
Header: "Data philosophy"
multiSelect: false
Options:
- "Offline-first (Recommended)" — "All data local by default. Cloud only when user explicitly chooses"
- "Cloud-first" — "Cloud storage with strong encryption. Convenience over full local control"
- "Hybrid" — "Sensitive data local, non-sensitive in cloud. User chooses per data type"

Question 4: "Default pricing model for your products?"
Header: "Pricing"
multiSelect: false
Options:
- "Free + one-time purchase" — "Free tier with paid upgrade, no recurring fees"
- "Freemium + subscription" — "Free core, subscription for premium features"
- "Open source + services" — "Code is free, charge for hosting/support/custom work"
- "Pay once, own forever" — "One-time purchase, all updates included"
```

## Round 2: Development Preferences (4 questions)

```
Question 1: "Your TDD approach?"
Header: "Testing"
multiSelect: false
Options:
- "TDD moderate (Recommended)" — "Test business logic & APIs. Skip tests for UI layout and prototypes"
- "TDD strict" — "Test everything. Red-Green-Refactor for every feature"
- "Tests after" — "Write code first, add tests for critical paths later"
- "Minimal" — "Only test what breaks. Integration tests over unit tests"

Question 2: "How do you handle infrastructure?"
Header: "Infrastructure"
multiSelect: false
Options:
- "Serverless-first (Recommended)" — "Vercel/Cloudflare/Lambda. VPS only for persistent processes or GPU"
- "VPS / Docker" — "Hetzner/Fly.io/DigitalOcean. Full control, predictable costs"
- "Platform-managed" — "Railway/Render/Heroku. Zero DevOps, higher cost"
- "Self-hosted" — "Own hardware or dedicated servers. Maximum control"

Question 3: "Commit and code review style?"
Header: "Workflow"
multiSelect: false
Options:
- "Conventional commits + auto" — "feat:/fix:/chore: prefixes, AI auto-commits per task"
- "Squash & merge" — "Feature branches, squash on merge, clean history"
- "Trunk-based" — "Commit directly to main, small frequent changes"

Question 4: "Documentation level?"
Header: "Docs"
multiSelect: false
Options:
- "CLAUDE.md + AICODE comments (Recommended)" — "AI-optimized docs: CLAUDE.md, AICODE-NOTE/TODO/ASK in code"
- "Comprehensive" — "Full docs: README, CLAUDE.md, ADRs, inline comments, API docs"
- "Minimal" — "README + code comments only. Code should be self-documenting"
```

## Round 3: Decision Style & Stacks (3 questions)

```
Question 1: "How do you make decisions?"
Header: "Risk style"
multiSelect: false
Options:
- "Barbell: safe + bold bets" — "90% conservative, 10% high-risk/high-reward experiments"
- "Calculated risks" — "Research thoroughly, then commit. Reversible decisions fast, irreversible slow"
- "Move fast, fix later" — "Speed over analysis. Default to action, course-correct on feedback"
- "Conservative" — "Proven technologies, established markets. Minimize downside"

Question 2: "What's your ultimate filter for decisions?"
Header: "Priority"
multiSelect: false
Options:
- "Time (Recommended)" — "Time is the only non-renewable resource. Is this worth my finite hours?"
- "Learning" — "Every project is an experiment. Optimize for skills and knowledge gained"
- "Impact" — "Will this change something for real people? Meaningful > profitable"
- "Freedom" — "Does this increase or decrease my optionality and independence?"

Question 3: "Which stacks do you work with?"
Header: "Stacks"
multiSelect: true
Options: dynamically built from `templates/stacks/*.yaml` — read each YAML's `name` and `description` fields.
Show the 4 most popular as options (nextjs-supabase, ios-swift, python-api, python-ml).
```

If user selects "Other" for stacks, list remaining stacks from `templates/stacks/*.yaml` as follow-up options.
