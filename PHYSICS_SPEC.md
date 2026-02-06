# ANGEL-2 Triangular C2 Network — Physics Specification

## Overview
A cellular automaton on a triangular lattice where each cell cycles through compression states (C1→C2→C3), interacts with neighbors, and can be excited by particle injections.

---

## GLOBAL CONSTANTS

| Variable | Value | Description | Physical Meaning |
|----------|-------|-------------|------------------|
| `TICK_INTERVAL` | 150 ms | Time between simulation steps | Base clock rate |
| `TRI_SIZE` | 45 px | Triangle edge length | Spatial scale |
| `numRings` | 1-10 | Mesh radius in triangle layers | System size |
| `meshShape` | 'hex'/'oct'/'rect' | Boundary geometry | Topology |

---

## TRIANGLE STATE MACHINE

Each triangle has:

| Property | Type | Range | Description |
|----------|------|-------|-------------|
| `id` | int | 0..N | Unique identifier |
| `state` | int | 0,1,2,3 | Compression state (see below) |
| `phase` | int | 0,1,2 | Position in 3-phase cycle |
| `polarity` | int | -1,+1 | Chirality/handedness |
| `neighbors` | int[] | max 3 | Adjacent triangle IDs |
| `skipping` | bool | — | Currently phase-locked |
| `skipCount` | int | 0..3 | Consecutive skips |
| `_removed` | bool | — | Carved out of mesh |
| `_isolationCount` | int | 0..5 | Ticks without active neighbors |

### State Definitions

| State | Value | Color | CHR Meaning | C-Level |
|-------|-------|-------|-------------|---------|
| DORMANT | 0 | Gray | Inert, no oscillation | — |
| STATE_1 | 1 | Red | Contracted | Virtual C3 |
| STATE_2 | 2 | Green | Equilibrium | True C2 |
| STATE_3 | 3 | Blue | Expanded | Virtual C1 |

---

## PHASE CYCLE

```
phase: 0 → 1 → 2 → 0 → ...
state: STATE_1 (red) → STATE_2 (green) → STATE_3 (blue) → STATE_1 ...
```

**Update rule** (each tick, if not skipping):
```javascript
phase = (phase + 1) % 3
if (phase === 0) state = STATE_1  // Contracted
if (phase === 1) state = STATE_2  // Equilibrium  
if (phase === 2) state = STATE_3  // Expanded
```

---

## SKIP LOGIC (Phase Locking)

A triangle skips its phase advance when:
- All active neighbors are in the same state
- AND triangle is in STATE_1 (contracted)

```javascript
shouldSkip(tri):
  activeNeighbors = neighbors.filter(n => n.state !== DORMANT && !n._removed)
  if (activeNeighbors.length === 0) return false
  allSame = activeNeighbors.every(n => n.state === tri.state)
  return allSame && tri.state === STATE_1
```

**Skip counter:**
- `skipCount` increments each tick while skipping
- After `skipCount > 2`, forced to resume cycling
- Reset to 0 when not skipping

---

## ISOLATION DECAY (Optional Mode)

When `isolationDecay = true`:

```javascript
if (activeNeighbors.length === 0):
  _isolationCount++
  
  if (_isolationCount >= 3 && state !== STATE_2):
    state = STATE_2  // Decay to equilibrium
    phase = 1
    
  if (_isolationCount >= 5):
    state = DORMANT  // Full decay
    phase = 0
    _isolationCount = 0

else:
  _isolationCount = 0  // Reset if has neighbors
```

---

## CONTACT RULES

Contacts occur when a STATE_3 (blue/expanded) triangle checks its neighbors.

### Bootstrap Spread
When STATE_3 contacts DORMANT:
```javascript
dormant.state = STATE_2
dormant.phase = 1
active.state = STATE_2
active.phase = 1
flipPolarity(both)
contactCount++
```

### State Collision: STATE_3 + STATE_1
```javascript
// Blue meets Red → Both become Green
t1.state = STATE_2; t1.phase = 1
t2.state = STATE_2; t2.phase = 1
flipPolarity(both)
```

### State Collision: STATE_3 + STATE_2
```javascript
// Blue meets Green → Blue→Green, Green→Blue
t1.state = STATE_2; t1.phase = 1
t2.state = STATE_3; t2.phase = 2
flipPolarity(both)
```

### Polarity Flip
Every contact flips both participants:
```javascript
flipPolarity(tri): tri.polarity *= -1
```

---

## PARTICLE INJECTIONS

### Electron (e⁻) — 0.45 eV
- **Behavior**: Passes through without activation
- **Speed**: 8 px/frame
- **Effect**: Visual only, no state changes

### Muon (μ) — Bootstrap
- **Behavior**: Targets random dormant edge triangle
- **Speed**: 6 px/frame
- **Effect**: Activates target to STATE_2 (green)

### Tau (τ) — Bomb
- **Behavior**: Targets center triangle
- **Speed**: 12 px/frame
- **Effect**: Shockwave activates ALL triangles to STATE_3
- **Delay**: Activation spreads at 3ms per pixel distance

---

## METRICS

| Metric | Calculation |
|--------|-------------|
| `Triangles` | Total non-removed triangles |
| `Active` | Triangles with state > 0 |
| `State 1 (Red)` | Count where state === 1 |
| `State 2 (Green)` | Count where state === 2 |
| `State 3 (Blue)` | Count where state === 3 |
| `Contacts` | Cumulative contact events |
| `Status` | 'DORMANT' if all dormant, 'ACTIVE' otherwise |

---

## PARAMETERS THAT NEED PHYSICS

These are currently **magic numbers** that should derive from CHR theory:

| Parameter | Current | What It Should Be |
|-----------|---------|-------------------|
| Skip threshold | 2 ticks | Function of coupling strength? |
| Isolation decay: equilibrium | 3 ticks | Relaxation time τ₁? |
| Isolation decay: dormant | 5 ticks | Relaxation time τ₂? |
| Phase cycle period | 3 states | Fixed by C1-C2-C3 geometry |
| Contact rules | Hard-coded | Derived from energy conservation? |
| Particle speeds | 6,8,12 | Mass-energy relation? |
| Shockwave speed | 3ms/px | Wave propagation in medium? |

---

## RECORDING FORMAT

Each frame captures:
```json
{
  "timestamp": 1234567890,
  "tick": 47,
  "params": {
    "speedMultiplier": 1.0,
    "isolationDecay": false,
    "meshShape": "hex",
    "numRings": 4
  },
  "metrics": {
    "total": 96,
    "active": 23,
    "state1": 8,
    "state2": 10,
    "state3": 5,
    "contacts": 47
  },
  "triangles": [
    {"id": 0, "state": 2, "phase": 1, "polarity": 1, "skipCount": 0, "isolationCount": 0},
    ...
  ]
}
```

---

## QUESTIONS FOR THE COUNCIL

1. **What determines skip threshold?** Currently arbitrary `> 2`. Should relate to local energy minimum?

2. **What are the decay timescales?** The 3-tick and 5-tick values for isolation decay — how do these relate to τ_temporal?

3. **Is the phase cycle correct?** Current: simple modular increment. Should there be asymmetry? Different dwell times per state?

4. **Contact energy exchange**: Currently both flip polarity. Should energy transfer depend on relative phase?

5. **Particle masses**: Electron/muon/tau have different speeds. Should map to 0.45eV / 105MeV / 1.78GeV ratios?

6. **Boundary conditions**: Edges have fewer neighbors. Should they have different dynamics?

---

## RECOMMENDED EXPERIMENTS

1. **Measure relaxation time**: Activate single triangle, record decay to dormant
2. **Measure propagation speed**: Launch muon, track wavefront
3. **Measure phase coherence**: Start with all green, measure time to disorder
4. **Contact rate vs density**: Vary initial conditions, measure contacts/tick
5. **Topology comparison**: Same initial state on hex/oct/rect, compare evolution
