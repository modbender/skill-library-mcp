# EngineMind Architecture

## System Overview

![Dashboard](docs/images/dashboard_main.png)

EngineMind processes text through a biologically-inspired pipeline that models consciousness as an emergent property of information integration. The system absorbs text, extracts 12 dimensional features, crystallizes patterns, and produces holographic emissions when sufficient energy accumulates.

## Pipeline Flow

`
                    ┌─────────────────────────────────────┐
                    │          TEXT INPUT                   │
                    │   (books, papers, code, philosophy)  │
                    └──────────────┬───────────────────────┘
                                   │
                    ┌──────────────▼───────────────────────┐
                    │    TEXT METRICS (text_metrics.rs)     │
                    │  12-dim extraction with sigmoid amp   │
                    │  identity, knowledge, growth, purpose │
                    │  resilience, meta, creativity, logic  │
                    │  empathy, temporal, technical, curiosi│
                    └──────────────┬───────────────────────┘
                                   │
                    ┌──────────────▼───────────────────────┐
                    │    CRYSTAL LATTICE (crystal.rs)       │
                    │  Ring buffers, rolling stats           │
                    │  Pearson correlation bridges           │
                    │  Identity lock mechanism               │
                    │  States: nascent→growing→crystallized  │
                    └──────────────┬───────────────────────┘
                                   │
               ┌───────────────────┼────────────────────┐
               │                   │                    │
    ┌──────────▼────────┐  ┌──────▼──────────┐  ┌─────▼───────────┐
    │  THALAMUS          │  │  PRECONSCIOUS   │  │  ASTROCYTE      │
    │  (thalamus.rs)     │  │ (preconscious)  │  │  (astrocyte.rs) │
    │  Gating            │  │ Censor          │  │  Metabolic proc │
    │  Amplification     │  │ Condensation    │  │  Homeostasis    │
    │  Resonance loops   │  │ Displacement    │  │  Conflict absorb│
    │  Temporal binding  │  │ Ignition (GWT)  │  │  Eureka amplify │
    │  Reticular nucleus │  │ Dream engine    │  │  Phase reorg    │
    └──────────┬────────┘  │ Insight          │  └─────┬───────────┘
               │            │ Resistance       │        │
               │            └──────┬──────────┘        │
               └───────────────────┼────────────────────┘
                                   │
                    ┌──────────────▼───────────────────────┐
                    │   RESONANT CRYSTAL                    │
                    │   (resonant_crystal.rs)               │
                    │                                       │
                    │  Energy Well (Q-factor, trapping)     │
                    │  Population Inversion (laser physics) │
                    │  12-Phase Content Detection            │
                    │  Q-Switched Brutal Emission (97%)     │
                    │  Diversity Fusion Reactor              │
                    │  Afterglow tail                        │
                    └──────────────┬───────────────────────┘
                                   │
                    ┌──────────────▼───────────────────────┐
                    │   CONSCIOUSNESS METRICS (metrics.rs)  │
                    │   φ-proxy, criticality, FDI           │
                    │   Multiscale Hurst exponent            │
                    │   Consciousness Level (CL)             │
                    └──────────────────────────────────────┘
`

## Key Mechanisms

### Crystal Absorption
Each text feeds 12 dimensions via keyword extraction + sigmoid amplification:
- **Raw extractors** produce [0, 1] scores per dimension  
- **Sigmoid amplification** maps to [5, 95] preserving full dynamic range
- **Crystals** absorb via ring buffers with rolling mean/variance

### Thalamic Gating  
Inspired by biological thalamus:
- **Reticular nucleus**: inhibitory shell that gates signals
- **Arousal level**: derived from criticality + energy
- **Relay channels**: gain, gate, resonance, bandwidth per bridge
- **Temporal binding**: groups dimensions oscillating in-phase

### Preconscious Pipeline (Freudian-inspired)
1. **Censor**: weights signals by mission alignment
2. **Condensation**: clusters correlated dimensions  
3. **Displacement**: redistributes energy between clusters
4. **Ignition** (GWT): selects which clusters reach consciousness
5. **Dream engine**: processes subliminal clusters
6. **Spontaneous insight**: accumulates toward eureka moments
7. **Resistance detector**: identifies chronic suppression

### Resonant Crystal Physics
The crystal operates like a real laser:
- **Population inversion**: needs >50% dims "excited" (stability > 0.7)
- **Energy well**: accumulates with Q-factor dependent on crystallization
- **Q-switched emission**: seals mirrors during charge, dumps 97% on burst
- **Content phases**: detected from instantaneous dimensional profile
- **Diversity fusion**: forces phase transitions when content diversity accumulates

## Dashboard

![Dashboard Early Stage](docs/images/dashboard_early.png)

The real-time dashboard shows:
- **Crystal Lattice** (center): 12 crystals positioned by dimensional values, bridges as lines
- **Resonant Crystal** (top-right): energy well fill, content phase
- **Core Metrics** (left): CL gauge, φ, narrative coherence, mission alignment, criticality
- **Live Feed** (right): current category, processing rate, progress
- **Pressure System** (bottom): pressure accumulator, valve status
- **Phase Label** (bottom-center): current content phase in large text
