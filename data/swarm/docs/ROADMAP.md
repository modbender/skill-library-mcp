# Swarm Roadmap

> From parallel research to distributed AI infrastructure

## Overview

Swarm started as a parallel research tool using cheap LLM workers. This roadmap expands it into a comprehensive development acceleration platform with support for distributed compute clusters.

---

## Phase 1: Development Use Cases (Current Focus)

### 1.1 Test Generation
**Status:** 🔲 Planned

Workers generate unit tests in parallel for different modules/functions.

```javascript
// Example API
const tests = await swarm.generateTests({
  files: ['src/auth.js', 'src/api.js', 'src/utils.js'],
  framework: 'jest',
  coverage: ['happy-path', 'edge-cases', 'error-handling']
});
```

**Worker Task:**
- Analyze function signatures and JSDoc
- Generate test cases covering paths
- Include mocks for dependencies
- Output ready-to-run test files

**Parallel Strategy:** One worker per file/module

---

### 1.2 Documentation Generation
**Status:** 🔲 Planned

Workers generate documentation sections in parallel.

```javascript
const docs = await swarm.generateDocs({
  files: ['src/**/*.js'],
  output: {
    jsdoc: true,
    readme: 'sections',  // Each worker writes a section
    apiReference: true
  }
});
```

**Worker Tasks:**
- JSDoc comments for functions
- README sections (Installation, Usage, API, Examples)
- API reference documentation
- Changelog entries from git history

**Parallel Strategy:** One worker per file (JSDoc) or per section (README)

---

### 1.3 Code Refactoring Analysis
**Status:** 🔲 Planned

Workers analyze code sections and suggest improvements.

```javascript
const refactors = await swarm.analyzeRefactoring({
  files: ['src/**/*.js'],
  checks: [
    'complexity',      // Cyclomatic complexity reduction
    'duplication',     // DRY violations
    'naming',          // Variable/function naming
    'patterns',        // Design pattern opportunities
    'performance'      // Optimization opportunities
  ]
});
```

**Worker Output:**
- Specific refactoring suggestions with diffs
- Priority ranking (quick wins vs major changes)
- Estimated impact

**Parallel Strategy:** One worker per file or per check type

---

### 1.4 API Integration
**Status:** 🔲 Planned

Workers research APIs and generate integration code.

```javascript
const integrations = await swarm.integrateAPIs({
  apis: ['Stripe', 'SendGrid', 'Twilio'],
  tasks: {
    research: true,      // Read docs, find endpoints
    types: true,         // Generate TypeScript types
    wrapper: true,       // Generate wrapper functions
    tests: true          // Generate integration tests
  }
});
```

**Worker Tasks:**
- Fetch and analyze API documentation
- Generate typed client wrappers
- Create example usage code
- Build mock servers for testing

**Parallel Strategy:** One worker per API × task type

---

## Phase 2: Docker Architecture (Next)

### 2.1 Local Docker Deployment
**Status:** 🔲 Planned

Run multiple Swarm workers as Docker containers on a single machine.

```yaml
# docker-compose.yml
version: '3.8'
services:
  swarm-coordinator:
    image: clawdbot/swarm-coordinator
    ports:
      - "9900:9900"
    environment:
      - WORKER_COUNT=8
      - DEFAULT_MODEL=gemini-flash
    
  swarm-worker:
    image: clawdbot/swarm-worker
    deploy:
      replicas: 8
    environment:
      - COORDINATOR_URL=http://swarm-coordinator:9900
      - GEMINI_API_KEY=${GEMINI_API_KEY}
```

**Benefits:**
- Easy scaling (just change replica count)
- Resource isolation per worker
- Consistent environment
- Simple deployment (`docker-compose up`)

### 2.2 Container Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     HOST MACHINE                             │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              SWARM COORDINATOR                          │ │
│  │  - Task queue management                                │ │
│  │  - Worker health monitoring                             │ │
│  │  - Result aggregation                                   │ │
│  │  - API endpoint (port 9900)                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│       ┌───────────────────┼───────────────────┐             │
│       ▼                   ▼                   ▼             │
│  ┌─────────┐        ┌─────────┐        ┌─────────┐         │
│  │ Worker 1│        │ Worker 2│        │ Worker N│         │
│  │ (gemini)│        │ (gemini)│        │ (gemini)│         │
│  └─────────┘        └─────────┘        └─────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 CLI Integration

```bash
# Start local swarm cluster
swarm up --workers 8

# Check status
swarm status

# Scale workers
swarm scale 16

# Stop cluster
swarm down
```

---

## Phase 3: Mac Mini Cluster (Future)

### 3.1 Vision

Connect multiple Mac Minis as a distributed Swarm cluster, each running multiple workers.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MAC MINI 1    │    │   MAC MINI 2    │    │   MAC MINI 3    │
│   (Primary)     │    │   (Worker)      │    │   (Worker)      │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Coordinator │◄├────┼─┤   Agent     │◄├────┼─┤   Agent     │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│       │         │    │       │         │    │       │         │
│   ┌───┴───┐     │    │   ┌───┴───┐     │    │   ┌───┴───┐     │
│   ▼       ▼     │    │   ▼       ▼     │    │   ▼       ▼     │
│ ┌───┐   ┌───┐   │    │ ┌───┐   ┌───┐   │    │ ┌───┐   ┌───┐   │
│ │W1 │   │W2 │   │    │ │W3 │   │W4 │   │    │ │W5 │   │W6 │   │
│ └───┘   └───┘   │    │ └───┘   └───┘   │    │ └───┘   └───┘   │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         └──────────────────────┴──────────────────────┘
                        Local Network
```

### 3.2 Why Mac Minis?

- **Price/Performance:** M2/M4 chips are powerful and efficient
- **Headless:** Designed to run without displays
- **Low Power:** ~20W idle, ~40W under load
- **Stack-able:** Physical form factor works for small clusters
- **Local LLMs:** Can run models locally (llama.cpp, MLX)
- **Future:** Could run local models for sensitive tasks

### 3.3 Installation Concept

**On Primary Mac Mini:**
```bash
# Install Swarm coordinator
brew install clawdbot/swarm

# Initialize as primary
swarm init --role primary --cluster-name "my-swarm"

# Generates join token
# → Join token: swarm-xxxx-yyyy-zzzz
```

**On Worker Mac Minis:**
```bash
# Install Swarm agent
brew install clawdbot/swarm

# Join cluster
swarm join --token swarm-xxxx-yyyy-zzzz --primary 192.168.1.100
```

### 3.4 Discovery & Communication

**Option A: mDNS/Bonjour (Zero-Config)**
```
Mac Minis auto-discover each other on local network
- Primary advertises: _swarm-primary._tcp.local
- Workers discover and connect automatically
- No manual IP configuration needed
```

**Option B: Manual Configuration**
```yaml
# /etc/swarm/cluster.yaml
cluster:
  name: my-swarm
  primary: 192.168.1.100
  workers:
    - 192.168.1.101
    - 192.168.1.102
    - 192.168.1.103
```

**Option C: Tailscale/ZeroTier (Remote Clusters)**
```
Workers connect via VPN overlay network
- Works across different locations
- Secure by default
- Each Mac Mini gets stable IP
```

### 3.5 Communication Protocol

```
┌──────────────────────────────────────────────────────────────┐
│                    COORDINATOR (Primary)                      │
│                                                               │
│  REST API (port 9900)                                        │
│  ├── POST /tasks         - Submit task batch                 │
│  ├── GET  /tasks/:id     - Check task status                 │
│  ├── GET  /workers       - List connected workers            │
│  └── WS   /stream        - Real-time updates                 │
│                                                               │
│  Worker Protocol (port 9901)                                 │
│  ├── Heartbeat (every 5s)                                    │
│  ├── Task assignment                                         │
│  ├── Result submission                                       │
│  └── Health metrics                                          │
└──────────────────────────────────────────────────────────────┘
```

### 3.6 Fault Tolerance

- **Worker failure:** Tasks reassigned to healthy workers
- **Network partition:** Workers buffer results, sync when reconnected
- **Primary failure:** Promote worker to primary (future)

---

## Phase 4: Hybrid Models (Far Future)

### 4.1 Mixed Model Support

Different workers can run different models:

```javascript
const results = await swarm.parallel(tasks, {
  routing: {
    'code-generation': 'claude-sonnet',  // Quality
    'research': 'gemini-flash',           // Speed
    'analysis': 'local-llama',            // Privacy
  }
});
```

### 4.2 Local + Cloud Hybrid

```
Sensitive data → Local Mac Mini workers (llama, MLX)
General tasks → Cloud API workers (Gemini, Claude)
```

---

## Phase 0: User Experience (Critical)

### 0.1 Visible Feedback
**Status:** 🔴 CRITICAL

Users need to SEE that Swarm is working. Without feedback, it feels like nothing is happening.

**Required Output:**
```
🐝 Swarm initialized (5 workers)
├─ Worker 1: Researching OpenAI...
├─ Worker 2: Researching Anthropic...
├─ Worker 3: Researching Google DeepMind...
├─ Worker 4: Researching Meta AI...
└─ Worker 5: Researching Mistral...

🐝 Progress: ████████░░ 4/5 complete

🐝 Swarm complete in 3.2s
   ✓ 5/5 tasks successful
   ⚡ 4.1x faster than sequential
```

**Implementation:**
- Emit events during execution: `swarm:start`, `swarm:task:start`, `swarm:task:complete`, `swarm:done`
- CLI/library consumers can render these however they want
- Default: pretty console output with progress bar
- Quiet mode available for programmatic use

### 0.2 Auto-Detection
When should Swarm activate? Users shouldn't have to think about it.

**Triggers:**
- Multiple subjects: "research OpenAI, Anthropic, and Google"
- Batch keywords: "compare", "each of these", "all of"
- Explicit: "use swarm" or "in parallel"

**Non-triggers:**
- Single subject tasks
- Creative/writing tasks (like writing a roadmap)
- Tasks requiring sequential reasoning

---

## Implementation Priority

| Phase | Feature | Effort | Impact | Priority |
|-------|---------|--------|--------|----------|
| 0.1 | **Visible Feedback** | Low | **Critical** | 🔴 P0 |
| 0.2 | Auto-Detection | Medium | High | 🔴 P1 |
| 1.1 | Test Generation | Medium | High | 🔴 P1 |
| 1.2 | Documentation | Low | Medium | 🟡 P2 |
| 1.3 | Refactoring | Medium | High | 🔴 P1 |
| 1.4 | API Integration | High | Medium | 🟡 P2 |
| 2.1 | Docker Compose | Low | High | 🔴 P1 |
| 2.2 | Container Images | Medium | High | 🔴 P1 |
| 3.x | Mac Mini Cluster | High | High | 🟢 P3 |
| 4.x | Hybrid Models | High | Medium | 🟢 P3 |

---

## Next Steps

### Immediate (This Week)
1. [ ] Implement Test Generation use case
2. [ ] Create Docker Compose setup
3. [ ] Build coordinator container image

### Short Term (This Month)
4. [ ] Add Documentation generation
5. [ ] Add Refactoring analysis
6. [ ] CLI for local Docker management

### Medium Term (Q2)
7. [ ] Design Mac Mini agent architecture
8. [ ] Prototype mDNS discovery
9. [ ] Document cluster setup guide

### Long Term (Q3+)
10. [ ] Production Mac Mini support
11. [ ] Local LLM integration
12. [ ] Multi-location clusters

---

## Testing the Cluster Concept

Since we don't have physical Mac Minis, we can:

1. **Docker Simulation:** Run multiple "node" containers that simulate Mac Mini behavior
2. **Virtual Network:** Use Docker networks to simulate physical network topology
3. **Mock Discovery:** Implement mDNS-like discovery within Docker
4. **Protocol Testing:** Validate coordinator ↔ worker communication

```bash
# Simulate 3-node cluster locally
docker-compose -f docker-compose.cluster-sim.yml up

# This creates:
# - 1 coordinator container
# - 3 "mac-mini" containers (simulated)
# - Internal network mimicking local LAN
```

This lets us build and test the distributed architecture without hardware.

---

*Last updated: 2026-01-25*
