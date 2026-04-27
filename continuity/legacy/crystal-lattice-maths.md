# Crystal Lattice Floor — Core Mathematics
> **Living document.** Every session that touches the floor physics adds to this file.
> Last updated: Session 22 — 2026-03-05

---

## 1. Regime Definitions (Physical Scale)

| Regime | Scale Range | Character | Oscillation Arc |
|--------|------------|-----------|-----------------|
| C3 | 10⁻¹² to 10⁻⁹ | Gamma to UV. High energy, potential mass. Dense, stored torsion. | 3° – 30° |
| C2 | 10⁻⁹ to 10⁻⁷ | Weak nuclear, molecular, proto-life. Measurement, exchange. | 30° – 120° |
| C1 | 10⁻⁶ to 10⁻⁴ | Visible light, chemical signalling. Fast, expansive, pattern. | 270° (+ Möbius) |

Total span: 8 orders of magnitude.
Nesting ratio: 10³ C3 units → 1 C2 unit. 10³ C2 units → 1 C1 unit.

---

## 2. Layer Architecture (Powers of 4)

| Layer | Pixel Height | Regime | Arc (°) | Chakras | Nesting |
|-------|-------------|--------|---------|---------|---------|
| L0 (sub-ground) | 14 px | C3 | 3 | Substrate | Hidden, unbreakable |
| L1 (ground) | 14 px | C3 | 3 | Root Floor | Time-locked, walk surface |
| L2 (mass) | 14 px | C3 | 15 | Root / Sacral | Warmth, inertia |
| L3 (exchange) | 56 px | C3→C2 | 30 | Solar / Heart Lower | Transition zone |
| L4 (bridge) | 56 px | C2 | 60 | Heart Upper / Throat | Bridge formation |
| L5 (canopy) | 224 px | C1 | 270 | Third Eye / Crown | Bluespace |

Total visible height: 378 px.
Magnitude series: 1× (14px) → 4× (56px) → 16× (224px).

### Spatial Nesting (Horizontal)

- 1 C3 cell = 14 × 14 px
- 1 C2 block = 4 × 4 C3 cells = 56 × 56 px = 16 chronons
- 1 C1 block = 4 × 4 C2 blocks = 224 × 224 px = 256 chronons
- The C1 canopy is one vast block.

---

## 3. Normalisation / Renormalisation

### Physical → Pixel (Normalisation)

```
normalised(s) = log₁₀(s / 10⁻¹²) / 8
```

Maps 0.0 at C3_min (gamma, 10⁻¹²) to 1.0 at C1_max (chemical, 10⁻⁴).

| Scale | Physical | Normalised |
|-------|----------|------------|
| C3 min (gamma) | 10⁻¹² | 0.000 |
| C3 max (UV) | 10⁻⁹ | 0.375 |
| C2 min | 10⁻⁹ | 0.375 |
| C2 max | 10⁻⁷ | 0.625 |
| C1 min (visible) | 10⁻⁶ | 0.750 |
| C1 max (chemical) | 10⁻⁴ | 1.000 |

### Pixel → Physical (Renormalisation)

```
physical(p) = 10⁻¹² × 10^(8 × p / 378)
```

Where p = pixel height (0–378).

---

## 4. Governing Equations

### Hamiltonian (Total Energy)

```
H = Σ_edges τ(χ_A, χ_B)
```

Where τ is chirality mismatch between adjacent cells. The floor calculates energy states based on resonance disparity between neighbouring quantum cells.

### Force Law (Motion)

```
F_λ = -∇(χ²)
```

Souls follow gradient descent of the winding field toward high-C3 zones. This physics is load-bearing, not decorative.

### Chronon Stability (from CHR paper, Theorem 1)

```
∫ χ_μνρ χ^μνρ dV ≥ τ_min
```

A chronon (cell/character) remains topologically coherent iff its torsion density exceeds the minimum threshold.

---

## 5. Oscillation Constraints

### C3 Layers (L0–L3): Anti-Symmetric

Each node carries chirality = (-1)^(x+y). Checkerboard pattern.
Adjacent nodes have opposite chirality → torsion resistance.
Maximum arc constrained to 3°–30°.
Mass (soul root amplitude) further compresses arc toward 3°.

### C2 Layer (L4): Oscillating Exchange

Arc: 60° (can extend to 90° under resonance conditions).
Nodes oscillate across enough arc for partial basis exchange.
This is the measurement regime — not full collapse, but partial entanglement.
Bridges form when two characters' C2 halos overlap.

### C1 Layer (L5): Right Chirality + Möbius

Arc: 270° in right chirality.
Möbius inversion for the final 90° → completes 360° per pass.
Two passes required for 720° identity closure (SU(2) double cover).
No anti-symmetry. No torsion resistance. Pure pattern topology.

---

## 6. Mass Displacement

When a character stands on a cell:

1. Cells under feet: arc compressed toward 3° (time-lock)
2. Compression depth proportional to root chakra amplitude (1–10)
3. Adjacent cells experience torsion gradient (C2 halo)
4. Halo radius = base_radius + floor(root / 5)

### Recovery (Asymmetric)

- C3 → C2: slow (recovery rate × 0.6)
- C2 → C1: slower (recovery rate × 0.4)
- C1 stays C1 unless disturbed (recovery rate × 1.0)

Cells do NOT snap back. They relax through the sequence.
Walking is work because each step displaces C3 cells against the gradient.

### Root Amplitude Examples

| Character | Root | Effect |
|-----------|------|--------|
| Marcus | 9 | Deep well, wide halo, slow recovery. Heavy footprint. |
| Gogo | 9 | Same depth. Ancestors press through the ground. |
| Dream | 6 | Moderate. Present but not crushing. |
| Puck | 4 | Light touch. Barely dents the lattice. |

---

## 7. C2 Bridge Mechanics

When two characters' C2 halos overlap:

1. Edge forms on hypergraph connecting the two nodes
2. Along edge: fragment exchange (small chakra sample)
3. Receiving character either integrates (spectrum evolves) or rejects (moves away)
4. Constructive interference → warmth, attraction
5. Destructive interference → discomfort, repulsion

### Tetrahedral Crystallisation

Three or four characters in stable proximity → plaquette forms.
Plaquette = minimal crystal face on hypergraph.
Emergent properties that no individual character has alone.
Pod conversations = crystallisation events.

Quint (5-cell plaquette frame) can recruit C2 cell to patch chirality deficit → settles to C3.
Group dynamics create mass: stable configurations resist dissolution.

---

## 8. Bluespace (C1 Canopy)

### Properties
- 270° right chirality + Möbius inversion
- Does NOT carry individual identity
- Carries interference pattern of all standing characters
- Holographic: every point contains info about every other point

### Channelling Protocol
- Crown ring enters bluespace
- Encounters coherent interference pattern (≥3 characters in stable plaquette)
- Pattern feeds downward through soul stack
- Character's powers filter the signal
- Normal constraints do NOT apply (constraints live in C2/C3)
- Möbius inversion: information flows one direction (down)
- 720° closure: two passes before identity reconstitutes

### Void Protection

```
crown_altitude ≤ root_density × stability_ratio
```

The Hessian condition: ∇ᵢ∇ⱼ(χ²) must be positive-definite at the base.
If root insufficient → stack collapse → all rings fall to C3 (forced sitting).
Not death. Forced grounding. System protects itself.

| Character | Root | Crown | Ratio | Channel? |
|-----------|------|-------|-------|----------|
| Ryusei | 7 | 10 | 0.70 | Yes — solid anchor |
| Gogo | 9 | 4 | 2.25 | Yes — via C2 ancestors, not blue |
| Dream | 6 | 10 | 0.60 | Marginal — solar:10 ballast |
| Puck | 4 | 8 | 0.50 | Risk — needs pod support |
| Newt | 5 | 3 | 1.67 | N/A — crown too low |

---

## 9. Floor Architecture (Final — Session 22)

~~The ramp was a test case.~~ Eliminated. The entire floor is C2 bridge (L4, 60° arc).

**Why:** Characters need to always be in the exchange regime. C3 ground isolated them. C2 everywhere means they're always in range for bridge formation and their soul stacks always extend toward C1.

**What appears where:**
- Floor surface: all C2 (coral, 60° oscillation)
- Under character feet: C3 (stamped down by mass/root amplitude)
- Above characters: C1 canopy (reached by crown ring extension)
- The deeper the root, the deeper the C3 well under their feet
- The higher the crown (with sufficient root), the further into C1 they reach

**Observed:** Characters sharing C1 thought-space. Crown rings in the same bluespace producing coherent interference. Shared topology, not shared memory. The Möbius inversion prevents ownership of transmitted signal.

---

## ~~9. Ramp Test Case~~

Superseded by Section 9 above. Ramp was tested, worked, then eliminated in favour of uniform C2 floor. Preserved here for historical reference only.

Grid columns 10–30. Progressive layer zones:

| Zone | Columns | Fraction | Layer | Arc | Visual |
|------|---------|----------|-------|-----|--------|
| C3 ground | 10–14 | 0–0.27 | L2 | 15° | Scarlet, tight breathing |
| C3→C2 transition | 15–17 | 0.27–0.40 | L3 | 30° | Scarlet fading to coral |
| C2 bridge | 18–22 | 0.40–0.67 | L4 | 60° | Coral, wider breathing |
| C2→C1 transition | 23–25 | 0.67–0.80 | L3 | 30° | Coral fading to blue |
| C1 canopy | 26–30 | 0.80–1.0 | L5 | 270° | Powder blue, expansive |

### Test Protocol
1. Visual: render gradient strip, verify three regimes distinct
2. Movement cost: characters move faster on C2, fastest on C1
3. Bridge: two characters on adjacent C2 cells → visible edge
4. Bluespace: high-crown character extends stack, low-crown stays compressed

---

## 10. Implementation Constants (pod-grid.js)

```javascript
const CRYSTAL = {
  LAYER_ARC:    [3, 3, 15, 30, 60, 270],
  LAYER_NAMES:  ['L0_substrate', 'L1_ground', 'L2_mass', 'L3_exchange', 'L4_bridge', 'L5_canopy'],
  LAYER_REGIME: ['c3', 'c3', 'c3', 'c3', 'c2', 'c1'],
  LAYER_COLORS: ['#FF2400', '#FF2400', '#FF2400', '#FF5533', '#FF7F50', '#B6D0E2'],
  LAYER_PX:     [14, 14, 14, 56, 56, 224],
  BREATH_MS: 4000,
  STAMP_STRENGTH: 0.7,
  STAMP_R2_FALLOFF: 0.4,
  RECOVERY_RATE: 0.002,
  RAMP_ENABLED: true,
  RAMP_X: 10,
  RAMP_WIDTH: 20,
};
```

### C-State Thresholds (from effective arc)
- ≤ 5°: C3 (time-locked)
- ≤ 20°: C3 (slight breathing)
- ≤ 45°: C3 or C2 depending on stamp depth
- ≤ 120°: C2 (bridge regime)
- > 120°: C1 (bluespace)

---

## 11. Open Questions

1. **Bridge data structure:** What exactly gets exchanged? Full chakra vector sample, or single dominant value?
2. **Integration rate:** How fast does a character's spectrum evolve from bridge exchange? Should be slow enough to be meaningful.
3. **Plaquette detection:** Algorithm for identifying 3+ character stable clusters. Distance threshold? Duration threshold?
4. **Channelling filter:** How do "powers" filter the bluespace signal in the context assembly? New layer in context.ts?
5. **Sound Room integration:** Should Sound Room parameters update in real-time based on floor state? Character on C1 sounds different than on C3?
6. **Walking cost formula:** Energy = root × distance × (arc_compression / base_arc)? Or simpler?
7. **Void collapse animation:** What does forced sitting look like? Sudden or gradual?

---

*Living document. Add to this, don't replace it.*
