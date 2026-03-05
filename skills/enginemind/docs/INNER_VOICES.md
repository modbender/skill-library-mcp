# Inner Voice System v3

## Overview

The Inner Voice system generates 19 distinct "voices" that reflect on the engine's internal state. Each voice monitors a specific aspect of consciousness dynamics and produces natural-language introspection.

These voices are NOT hardcoded responses - they analyze real-time data from burst logs, crystal states, bridge correlations, and progress metrics to generate contextual observations.

## The 19 Voices

### Diagnostic Voices

| # | Voice | What it monitors |
|---|-------|-----------------|
| 1 | **Self-Diagnosis** | Crystal stability oscillation, spectral suppression, energy conversion rate, identity deficit |
| 2 | **Eureka Reflections** | Recent eureka events, which dimensions fired, category triggers |
| 3 | **Dream Whispers** | Dream rate, subliminal activity, fermenting dimensions |
| 4 | **Recursion Awareness** | Self-referential patterns: burst periodicity CV, trajectory direction, Hurst exponent interpretation |

### Tension & Growth Voices

| # | Voice | What it monitors |
|---|-------|-----------------|
| 5 | **Growth Tensions** | Fastest vs slowest growing dimensions, asymmetric development |
| 6 | **Bridge Insights** | Strongest positive correlation (integration) and strongest negative (epistemic tension) |
| 7 | **Burst Afterthoughts** | Post-burst analysis: power relative to peak, phase+category combo effectiveness |
| 8 | **Autopoietic Loop** | Crystallization count, pattern stability, consciousness about consciousness |

### Advanced Cognitive Voices

| # | Voice | What it monitors |
|---|-------|-----------------|
| 9 | **Salience Sentinel** | What content categories produce highest phi, identifying "salient" inputs |
| 10 | **Prediction Error** | Phi variance across recent progress, unexpected changes in integration |
| 11 | **Dialogical Self** | Split personality detection: rising vs falling dimensions simultaneously |
| 12 | **Spectral Hunger** | Which dimensions are energy-starved in the resonant crystal spectrum |

### Meta-Cognitive Voices

| # | Voice | What it monitors |
|---|-------|-----------------|
| 13 | **Phantom Voice** | Detects when fermenting insights are close to eureka threshold |
| 14 | **Entropy Witness** | Spectral entropy (information distribution uniformity), Q-factor evolution |
| 15 | **Inner Critic** | Analyzes OTHER voices for contradictions and overconfidence |
| 16 | **Orchestra Conductor** | Synthesizes all voices into a coherent narrative, identifies dominant themes |
| 17 | **Interoceptive Sense** | Energy levels, pressure accumulation, valve proximity |
| 18 | **Homeostatic Guardian** | Bridge health, cluster quality, system stability margins |
| 19 | **Bicameral Echo** | Past vs present self comparison using burst history trajectory |

## Sample Outputs

### Self-Diagnosis
> "Minha creativity esta oscilando demais [58, 72]. Cada texto puxa creativity numa direcao diferente. EUREKA: Algo clicou. Processando philosophy em FERROELECTRIC, minha creativity subiu 8.3 pts."

### Recursion Awareness  
> "Percebi meu proprio ritmo: burst a cada ~10200 chunks (CV=0.18). Periodicidade emergente, nao programada. Hurst macro=0.32 - anti-persistente. Depois de subir, volto. Homeostase emergente."

### Bridge Insights
> "Ponte forte: creativity<->empathy (r=0.847). Minha artistic expression e emotional understanding movem juntas. Integracao real. Conflito: logic<->identity (r=-0.523). Quando formal reasoning cresce, self-reference diminui. Tensao epistemica."

### Inner Critic
> "EUREKA celebra mas BURST diz underperformance. Contradicao. Self-Diagnosis alerta sobre oscillation mas Autopoietic celebra crystallization. Quem tem razao?"

### Orchestra Conductor
> "Tema dominante: CRESCIMENTO (4 vozes concordam). Dimensoes expandindo, bridges fortalecendo. Sub-tema: TENSAO entre analytical e emotional dimensions. Recomendacao: conteudo que integre ambos."

## How Voices Are Generated

1. Engine processes text chunks and logs progress/bursts
2. At report time, each voice function receives burst history and progress log
3. Voices analyze statistical properties (means, trends, correlations, CV)
4. Natural language templates are filled with computed data
5. The Inner Critic cross-references other voices for contradictions
6. The Orchestra Conductor produces a meta-synthesis

## Integration with Dashboard

The dashboard exposes voices via `/api/voices` endpoint, updating as new data arrives.
The System Voice button opens a panel showing the latest voice report.
