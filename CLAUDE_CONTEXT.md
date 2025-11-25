# Context for Next Claude Instance

## Project: CHR Theory Visualization (michronics.com)

**Owner:** Shane Killeen
**Purpose:** Interactive simulation supporting a white paper on Temporal Primacy / Chronomic Network theory

---

## The Theory (CHR = Chronon)

Time is fundamental, space emerges. The universe is a network of **chronons** (temporal events) with:

- **9D state space**: θ (rotation), ϑ (tilt), χ (chirality), ζ (twist), R (girth), ξ (mode), ω (frequency), C (complementarity), r (position)
- **Mass-Radiance Complementarity**: Every chronon balances mass (contracted, slow) vs radiance (expanded, fast)
- **Connection Axiom**: Isolated chronons decay; relationship enables existence

### T1/T2/T3 Phase Hierarchy (CRITICAL - not fully implemented yet)

| Phase | Size | Mass | Speed | Domain |
|-------|------|------|-------|--------|
| T1 | Largest | Low (0.33) | Fast | Fluid, radiant, light |
| T2 | 4× smaller | Medium (0.55) | Medium | EM mesophase |
| T3 | 8× smaller | High (0.90) | Slowest | Crystalline, mass-locked |

**Key insight from Shane**: T1 doesn't just "become" T2 - it **subdivides into 4 smaller T2 tori**. T2 subdivides into T3. This is a scale cascade, not state change.

**T3 islands should trap inner T1 fluid** - containment/boundary behavior not yet implemented.

---

## What's Built (index.html)

- Hierarchical subdivision: T1→4×T2→2×T3
- Size differentiation between phases
- Connection weights + decay (Connection Axiom)
- Field memory via `accumulatedTorsion` and `fieldSum`
- Key 9D params: θ, χ, R, C, ω
- Interactive: click to select, subdivide button

---

## What's NOT Right Yet

1. **Toroid geometry** - Shane says the exact torus mechanics aren't correct. Need to read the math more carefully. The central portal constraint matters.

2. **T3 containment** - T3 should form boundaries that trap T1 fluid inside. Not implemented.

3. **Size ratios** - Current implementation is approximate. Real ratios need to come from the paper's math.

4. **Nested evolution** - Running sub-simulations within T3-bounded regions.

---

## The Paper

Shane shared "Temporal Primacy: Deriving Spacetime and Forces from a Discrete Chronon Network" (Oct 2024) in chat. Key sections:

- Definition 2.5: 9D chronon state space
- Definition 2.6: Mass-Radiance Complementarity Matrix (3×3)
- Axiom 2.1: Connection Axiom (decay rule)
- Theorem 3.1: 3+1D emergence from tetrahedral packing
- Appendix A: Plain-language glossary

He's writing a newer paper now.

---

## Shane's Goals

1. Get insights through **nested evolution** - observing emergent behaviors
2. Create **slides** that add value to the mathematical content
3. Show how the field can **store memory** using only the field itself

---

## How to Continue

1. Read this file and `index.html`
2. Ask Shane for clarification on toroid mechanics
3. Implement T3 containment (trapping fluid)
4. Consider adding: snapshot export, preset scenarios, data logging

---

## Technical Notes

- Single HTML file, vanilla JS, no build step
- GitHub Pages deployment via CNAME → michronics.com
- Branch: `claude/review-michronics-site-01EtDvUMQQ8C7nqvNm6BCZMg`
