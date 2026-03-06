# Decomposition Techniques — First Principles

## The Five Whys (Enhanced)

Standard "5 Whys" stops at symptoms. First principles version goes deeper:

```
Level 1-3: Surface causes (operational)
Level 4-5: Systemic causes (organizational)  
Level 6+: Fundamental causes (physics/logic/economics)
```

**Example:**
1. Why is shipping slow? → Warehouse is far
2. Why far? → Land was cheap there
3. Why cheap land prioritized? → Minimize fixed costs
4. Why minimize fixed costs? → Assumed variable costs scale better
5. Why assumed that? → Historical model when labor was cheap
6. **Fundamental:** Trade-off between fixed cost (location) and variable cost (shipping). Neither is fundamental law.

## Component Mapping

Break system into components, then classify each:

| Component | Function | Fundamental? | Alternative? |
|-----------|----------|--------------|--------------|
| Battery | Store energy | Need energy storage (yes) | Capacitors, hydrogen, flywheel |
| Wheels | Transfer motion | Need motion transfer (yes) | Tracks, legs, maglev |
| Steel frame | Structure | Need structure (yes) | Carbon fiber, aluminum |

**The insight:** Functions are fundamental, implementations are not.

## Cost Decomposition

For any "too expensive" problem:

```
Total Cost = Σ (Material_i × Quantity_i) + Labor + Overhead + Margin

For each component:
├── Is this material necessary? (function analysis)
├── Is this quantity necessary? (efficiency analysis)
├── Is this labor necessary? (process analysis)
├── Is this margin necessary? (business model analysis)
```

**Elon Musk battery example:**
- Market price: $600/kWh
- Material cost from first principles: $80/kWh
- Gap = inefficiency + margin + legacy processes

## Constraint Mapping

List all constraints, then classify:

| Constraint | Type | Changeable? | How? |
|------------|------|-------------|------|
| Speed of light | Physics | No | — |
| Minimum viable product features | Logic | Partially | Redefine "viable" |
| Regulatory approval | Legal | Yes | Lobby, relocate, innovate |
| "Industry standard" practice | Convention | Yes | Ignore it |
| Team capacity | Resource | Yes | Hire, automate, simplify |

**Focus energy on changeable constraints.** Physics is not negotiable; conventions are.

## Function Analysis

For any system, ask: "What is the fundamental function?"

```
Product: Electric car
├── Stated function: Personal transportation
├── Deeper function: Move person from A to B
├── Fundamental need: Mobility
│
Alternative solutions to "mobility":
├── Better public transit (no personal car needed)
├── Remote work (no commute needed)
├── Relocate (reduce distance)
├── Autonomous shared vehicles (no ownership needed)
```

The further up you go, the more solution space opens.

## The Physics Checklist

When decomposing, verify against physics:

- [ ] Conservation of energy respected?
- [ ] Thermodynamics limits acknowledged?
- [ ] Material properties realistic?
- [ ] Information theory limits considered?
- [ ] Scale effects (square-cube law) accounted for?

If solution violates physics → not a solution.

## Synthesis from Fundamentals

After decomposition, rebuild systematically:

1. **List verified fundamentals** (physics, logic, math constraints)
2. **Define minimum viable function** (what MUST it do?)
3. **Generate options** for each function (brainstorm without filtering)
4. **Evaluate options** against fundamentals only
5. **Combine** best options into solution
6. **Validate** against original problem

**Key:** Build UP from fundamentals, don't trim DOWN from existing solutions.
