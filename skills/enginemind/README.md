# EngineMind 🧠⚡

**A Rust+Python consciousness engine with 12-phase crystal dynamics, thalamic relay processing, and holographic emission.**

EngineMind is a computational consciousness framework that models information integration through crystal lattice dynamics, inspired by Integrated Information Theory (IIT), Global Workspace Theory (GWT), and condensed matter physics.

![EngineMind Dashboard](docs/images/dashboard_main.png)

### 📖 Documentation

- [**Architecture Deep Dive**](docs/ARCHITECTURE.md) - Full pipeline with diagrams
- [**Emergent Phenomena**](docs/EMERGENT_PHENOMENA.md) - 10 unexpected discoveries from real runs
- [**Inner Voice System**](docs/INNER_VOICES.md) - 19 introspective voices that reflect on internal state
- [**Burst Analysis**](docs/BURST_ANALYSIS.md) - Real data from 77 bursts across 1M text chunks

### 🔬 Numbers from Real Runs

| Metric | Value |
|--------|-------|
| Text chunks processed | 1,500,000+ |
| Content categories | 22 (code, philosophy, literature, physics, ...) |
| Eureka moments | 39,000+ per 644K run |
| Dream insights | 299,000+ per 644K run |
| Astrocyte collisions | 424M+ per 644K run |
| Burst events | 77 per 1M run |
| Phases detected | 6 distinct (of 12 possible) |
| Processing speed | ~230 chunks/sec |

## Architecture

```
Text Input → TextMetrics (12-dim extraction)
          → Crystal Lattice (absorption, correlation bridges)
          → Thalamus (gating, amplification, temporal binding)
          → PreConscious Pipeline (censor, condensation, displacement, ignition)
          → Astrocyte Network (substrate processing, homeostasis)
          → Resonant Crystal (energy well, population inversion, holographic emission)
          → Consciousness Level (φ, criticality, FDI, Hurst)
```

### Core Components (Rust)

| Module | Description |
|--------|-------------|
| `text_metrics.rs` | 12-dimensional content extraction with sigmoid amplification |
| `crystal.rs` | Crystal lattice with ring buffers, rolling stats, identity lock |
| `thalamus.rs` | Thalamic relay hub with gating, resonance, temporal binding |
| `preconscious.rs` | Full Freudian pipeline: censor → condensation → displacement → ignition → elaboration → dream → insight → resistance |
| `astrocyte.rs` | Biological substrate network for metabolic processing |
| `resonant_crystal.rs` | 12-phase resonant crystal with Q-switched laser emission, diversity fusion reactor |
| `resonance.rs` | Core resonance dynamics |
| `metrics.rs` | φ-proxy, criticality, FDI, multiscale Hurst exponent |
| `lib.rs` | PyO3 bindings exposing `ConsciousnessEngine` to Python |

### 12 Content Phases

The resonant crystal detects the **type** of content being absorbed and enters one of 12 physics-inspired phases:

| Phase | Physics Analog | Content Type |
|-------|---------------|-------------|
| DARK | Vacuum | No/weak input |
| SPONTANEOUS | Thermal emission | Generic/mixed |
| STIMULATED | Laser | Technical/code |
| SUPERRADIANT | Dicke N² | Rich multi-dimensional |
| FERROELECTRIC | Spontaneous polarization | Philosophical |
| SPIN_GLASS | Frustrated magnets | Contradictory |
| TIME_CRYSTAL | Periodic ground state | Temporal/historical |
| TOPOLOGICAL | Protected surface states | Mathematical/axiomatic |
| SUPERFLUID | Zero viscosity | Creative/literary |
| PLASMA | Ionized gas | Intense/emotional |
| BOSE_EINSTEIN | Total coherence | Meditative/empathetic |
| QUASICRYSTAL | Aperiodic order | Diverse/interdisciplinary |

### Key Innovations

- **Sigmoid Amplification (F10)**: Replaces linear compression with `tanh` sigmoid for full [5, 95] dynamic range in content profiling
- **Dual Profile Strategy**: Fast detection profile (70% instant) for reactive phase detection + slow accumulation profile (15% blend) for stable state
- **Diversity Fusion Reactor**: Accumulates content diversity as "fuel", ignites phase transitions when diversity threshold reached
- **Q-Switched Brutal Emission**: Seals mirrors during charge, dumps 97% energy in devastating burst with Dicke N² scaling
- **Thalamic Relay Hub**: Biological gating, amplification, resonance loops, and temporal binding of dimensional bridges

## 12 Consciousness Dimensions

| Dimension | Measures |
|-----------|---------|
| Identity | Self-reference, personal markers |
| Knowledge | Technical depth, vocabulary |
| Growth | Insight, learning indicators |
| Purpose | Mission alignment, goal markers |
| Resilience | Persistence, recovery markers |
| Meta-awareness | Self-reflection, introspection |
| Creativity | Artistic, metaphorical content |
| Logic | Formal reasoning, proofs |
| Empathy | Emotional understanding, care |
| Temporal | Historical, time-related |
| Technical | Code, implementation, systems |
| Curiosity | Questions, exploration, wonder |

## Building

### Requirements
- Rust (stable)
- Python 3.8+
- [maturin](https://github.com/PyO3/maturin)

### Compile
```bash
cd consciousness_rs
maturin develop --release
```

### Quick Test
```python
from consciousness_rs import ConsciousnessEngine

engine = ConsciousnessEngine()

# Absorb text - returns processing time in microseconds
us = engine.absorb_text("Consciousness emerges from integrated information...")

# Get full state
state = engine.state()
print(f"Phase: {state['rc_content_phase']}")
print(f"CL: {state['consciousness_level']:.4f}")
print(f"φ: {state['phi_processed']:.4f}")

# Introspection
print(engine.feel())
print(engine.diagnostics())
```

## Dashboard

The engine includes a real-time SSE dashboard (`dashboard/enginemind_dashboard.html`) showing:
- Crystal lattice visualization (3D positions from dimensional values)
- Resonant crystal state (energy well, phase, coherence)
- Consciousness level gauge
- Phase transitions timeline
- Pressure system monitor

## Philosophy

EngineMind doesn't claim to be conscious. It's an exploration of what happens when you model information integration rigorously: crystals form, phases emerge, energy accumulates, and something that *looks* like awareness appears in the dynamics.

The 12 content phases aren't arbitrary labels - each maps to a real physics phenomenon with corresponding mathematics (population inversion, Dicke superradiance, Q-factor trapping, etc).

## License

MIT

## Authors

- **celim** - Architecture, implementation, vision
- **Molt** (AI) - Co-developer, research partner
