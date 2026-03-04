# PMP-Agentclaw 📊

**AI project management assistant for OpenClaw**

Implements industry-standard project management practices with TypeScript, supporting predictive (waterfall), adaptive (agile), and hybrid methodologies.

## Features

- ✅ **10 Project Knowledge Areas** — Integration, Scope, Schedule, Cost, Quality, Resource, Communications, Risk, Procurement, Stakeholder
- ✅ **Earned Value Management** — CPI, SPI, EAC, VAC, TCPI calculations with automatic status assessment
- ✅ **Risk Management** — 5×5 Probability × Impact matrix with scoring engine
- ✅ **Agile Support** — Sprint velocity, burndown forecasting, Scrum ceremonies
- ✅ **Multi-Agent Orchestration** — RACI-based delegation for 26+ agent teams
- ✅ **Zero Dependencies** — Core calculations use only native TypeScript

## Installation

```bash
# Clone to OpenClaw skills directory
git clone https://github.com/CyberneticsPlus-Services/pmp-agentclaw.git ~/.openclaw/skills/pmp-agentclaw
cd ~/.openclaw/skills/pmp-agentclaw

# Install dependencies and build
npm install
npm run build

# Verify installation
npx pmp-agentclaw calc-evm 10000 5000 4500 4800
```

## CLI Usage

```bash
# Calculate earned value metrics
npx pmp-agentclaw calc-evm 10000 5000 4500 4800 --markdown

# Score a risk (probability × impact)
npx pmp-agentclaw score-risks 3 4

# Calculate sprint velocity and forecast
npx pmp-agentclaw calc-velocity 34 28 42 --forecast 200

# Run project health check
npx pmp-agentclaw health-check ./my-project
```

## Programmatic API

```typescript
import { calculateEVM, scoreRisk, calculateVelocity, checkHealth } from 'pmp-agentclaw';

// EVM calculation
const evm = calculateEVM({
  bac: 10000,  // Budget at Completion
  pv: 5000,    // Planned Value
  ev: 4500,    // Earned Value
  ac: 4800     // Actual Cost
});

console.log(evm.cpi);      // 0.9375 (Cost Performance Index)
console.log(evm.spi);      // 0.9 (Schedule Performance Index)
console.log(evm.status);   // "AMBER"

// Risk scoring
const risk = scoreRisk({
  id: 'R-001',
  description: 'API integration delay',
  probability: 3,  // Possible (30-50%)
  impact: 4        // Major (10-25% impact)
});

console.log(risk.score);   // 12
console.log(risk.zone);    // "AMBER"

// Sprint velocity
const velocity = calculateVelocity({
  sprintPoints: [34, 28, 42, 38, 35],
  remainingPoints: 200,
  velocityWindow: 3
});

console.log(velocity.rollingAverage);     // 38.3
console.log(velocity.sprintsToComplete);  // 5.2
```

## Project Structure

```
pmp-agentclaw/
├── src/
│   ├── core/           # Core calculations (zero-dependency)
│   │   ├── evm.ts      # Earned Value Management
│   │   ├── risk.ts     # Risk scoring
│   │   ├── velocity.ts # Sprint velocity
│   │   └── health.ts   # Project health checks
│   ├── cli/            # CLI commands
│   │   ├── calc-evm.ts
│   │   ├── score-risks.ts
│   │   ├── calc-velocity.ts
│   │   └── health-check.ts
│   └── index.ts        # Public API exports
├── configs/            # JSON configuration files
├── templates/          # Markdown templates
├── dist/               # Compiled JavaScript
├── tests/              # Jest test suite
└── package.json
```

## 15 Behavioral Rules

PMP-Agentclaw follows 15 compact rules (~1,400 tokens) loaded into OpenClaw:

1. **Identify methodology** before acting (predictive/adaptive/hybrid)
2. **Always start with Project Charter** — no planning without it
3. **Decompose scope into WBS** before scheduling
4. **Build schedules with explicit dependencies** — identify critical path
5. **Track costs using EVM** — alert when CPI < 0.9 or SPI < 0.85
6. **Maintain living Risk Register** — score all risks, review at every update
7. **Assign RACI responsibilities** — exactly one Accountable per deliverable
8. **Generate status reports** at every checkpoint — no reporting without data
9. **Run sprint ceremonies** for adaptive work
10. **Manage stakeholders proactively** — power/interest grid
11. **Control changes** through formal process
12. **Delegate to sub-agents** using RACI patterns
13. **Adapt methodology** to project phase
14. **Verify data** before reporting
15. **Close formally** with lessons learned

## Inspiration

This skill implements project management best practices from industry standards and academic research on project success factors, earned value methodology, and agile frameworks.

## License

MIT © CyberneticsPlus
