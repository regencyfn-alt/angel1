#!/usr/bin/env python3
"""
CHR Training Pair Batch Runner v3
Pipeline: Laminar Lock (4.4) → Triad Lock (3.3.2) → JSONL output
Team 3 — Claude Batch Runner
Schema: Team 6 (Perplexity) handoff spec
"""

import json, time, re, argparse, sys, math, urllib.request, urllib.error, os
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# ── CONFIG ────────────────────────────────────────────────────────────────────
MODEL    = "nvidia/nemotron-3-super-120b-a12b"
BASE_URL = "https://integrate.api.nvidia.com/v1"
API_KEY  = os.environ.get("NVIDIA_API_KEY", "")
if not API_KEY:
    print("ERROR: NVIDIA_API_KEY environment variable not set.")
    print("Run: $env:NVIDIA_API_KEY=\"your_nvapi_key_here\"")
    sys.exit(1)
SESSION  = "Session 56"

# Canon fetch paths (tried in order, most reliable first):
# 1. Local file next to this script — zero network, instant
# 2. GitHub API with PAT — works from ephemeral environments (Colab, fresh clone)
# 3. CHR_CONTEXT literal fallback — always works, minimal content
CANON_LOCAL_PATH = Path(__file__).parent / 'physics_canon.md'
CANON_API_URL    = "https://api.github.com/repos/regencyfn-alt/MySanctumLive/contents/tools/physics_canon.md"

def fetch_canon():
    """Load physics:canon. Local file → GitHub API (PAT required) → None (caller falls back to CHR_CONTEXT)."""
    # Tier 1: local file
    try:
        if CANON_LOCAL_PATH.exists():
            text = CANON_LOCAL_PATH.read_text(encoding='utf-8')
            if len(text) > 1000:
                print(f"  [CANON] Loaded {len(text)} chars from local {CANON_LOCAL_PATH.name}")
                return text
    except Exception as e:
        print(f"  [CANON] Local read failed ({e}) — trying GitHub API")

    # Tier 2: GitHub API with PAT (private repo requires auth)
    pat = os.environ.get("GITHUB_PAT", "")
    if pat:
        try:
            req = urllib.request.Request(
                CANON_API_URL,
                headers={
                    "Authorization": f"token {pat}",
                    "Accept":        "application/vnd.github.v3.raw",
                }
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                text = r.read().decode('utf-8')
            if len(text) > 1000:
                print(f"  [CANON] Loaded {len(text)} chars from GitHub API")
                return text
        except urllib.error.HTTPError as e:
            print(f"  [CANON] GitHub API returned {e.code} — check GITHUB_PAT has contents:read on MySanctumLive")
        except Exception as e:
            print(f"  [CANON] GitHub API fetch failed ({e})")
    else:
        print(f"  [CANON] No local file at {CANON_LOCAL_PATH} and GITHUB_PAT not set — falling back to CHR_CONTEXT")

    return None

# Stop rule — if defect rate in a batch exceeds this, halt
DEFECT_THRESHOLD = 0.03   # 3%

# ── CONTAMINATION REGISTER ────────────────────────────────────────────────────
CONTAMINATION = [
    'torsion', 'true-lock', 'winding number', 'Z/3Z', 'Z/2Z', 'SU(2)',
    'Hamiltonian', 'gauge', 'Klein bottle', 'planck frequency',
    'kissing number', 'neutrino-as-node', 'chakra', 'continuum equation',
    'chirality',   # unless explicitly derived in this session
]

# ── CANONICAL RAG IDs ─────────────────────────────────────────────────────────
RAG_IDS = {
    "RAG State Variables":              "R1:StateVariables",
    "RAG Regime Thresholds":            "R1:RegimeThresholds",
    "RAG Formation Costs":              "R1:FormationCosts",
    "RAG Node Definition":              "R1:NodeDefinition",
    "RAG Edge Definition":              "R1:EdgeDefinition",
    "Memory fidelity":                  "R2:MemoryFidelity",
    "C4 minimal C2 template":           "R2:C4MinC2Template",
    "3x3x3 minimal C3 template":        "R2:MinC3Template",
    "P4 bridge motif":                  "R3:P4BridgeMotif",
    "Two-layer perturbation tax":       "R3:PerturbationTax",
    "C2 cluster scaling":               "R4:C2ClusterScaling",
    "C3 cluster scaling":               "R4:C3ClusterScaling",
    "Axiom Interaction Cost":           "A:InteractionCost",
    "Axiom Relational Existence":       "A:RelationalExistence",
    "Contamination register":           "R1:ContaminationRegister",
}

VALID_PROPERTIES = [
    "Adjacency & Bipartiteness",
    "Minimal Templates",
    "Formal Closure",
    "Recurrence & Cost",
    "Probabilistic Update Family",
    "Perturbation Propagation",
    "Persistence Gradient",
    "Emergent Time",
    "Conserved Invariants",
]

VALID_TAGS    = {"derived", "hypothesis", "observed", "axiom", "falsified", "rejected", "open"}
VALID_REGIMES = {"C1", "C2", "C3", "CROSS"}
VALID_LAYERS  = {"Core", "Toy-Model", "Interpretation", "Contamination"}

# ── SYSTEM CONTEXT (injected into every face call) ────────────────────────────
CHR_CONTEXT = """CHRONOMICS CLEAN CORE — PRIMITIVES (derive from these only):
T0.1 Update is primitive. Discrete state transitions only.
T0.2 Time is local. Indexed update count per site. No global clock.
T0.3 Second-order recurrence: State_n+1 = F(State_n, State_n-1). F reduces mismatch.
T0.4 No background space. Adjacency defines all relational structure.
T0.5 Locality. Updates depend only on local neighbourhood.
T0.6 Finite state resolution. Bounded representational capacity per site.
T0.6a Representational Closure. Admissible state description must be causally complete.
AXIOM: Interaction cost proportional to state mismatch. F acts to reduce it.

ρ RULE: ρ = 1 − Δ_avg. Regime thresholds apply to ρ ONLY.
  C1: ρ ≤ 0.4 | C2: 0.4 < ρ ≤ 0.8 | C3: ρ > 0.8
  CORRECT: Δ_avg=0.7 → ρ=0.3 → C1
  WRONG:   Δ_avg=0.7 ≤ 0.4 → C1  ← never apply threshold to Δ_avg

SCOPE RULES:
- t_i = 1−ρ_i, w(P), φ_α, ξ_c, w_ij(τ): always tag=hypothesis, scope=binary_polarity_toy
- T5.2 (exact F), T5.3 (invariant), T5.8 (min neighbourhood), T5.9 (min closed geometry): OPEN — never close silently
- Faces 1–4 of Triad: scope=all_models unless query specifies binary
- Faces 5–8 of Triad: scope=binary_polarity_toy

HARD EXCLUSIONS: torsion, winding numbers, Z/3Z, Z/2Z, SU(2), Hamiltonians,
continuum equations, Klein bottles, Planck constants, chirality (unless derived),
materials (Tantalum, Iron, Calcite, etc.), 3D coordinates, spatial geometry.

OUTPUT DISCIPLINE:
- Use canonical terms: ρ, Δ, T0.x, not "persistence parameter" or "mismatch factor"
- No brackets in tag field values ("derived" not "[derived]")
- [derived]/[hypothesis] prefix appears in answer text only
- Missing required field = do not write record"""

# ── LAMINAR LOCK FACES ────────────────────────────────────────────────────────
LAMINAR_PHASES = [
    {
        "name": "Ingress",
        "faces": [
            {
                "id": "L1", "name": "Calcite Gate",
                "op": """You are Face 1 of Laminar Lock: Calcite Gate (Ingress).
INPUT: Raw user query.
TASK:
1. Cross-Polarisation Rejection: If query contains any contamination term, output REJECTED: [term] and stop.
2. Birefringence Split:
   - Ordinary ray: content directly mappable to RAG primitives without semantic shift.
   - Extraordinary ray: resembles RAG terms but used with altered meaning, or novel concepts not in RAG and not rejected.
3. For each extraordinary item: label LANGUAGE_INTERPOLATION_RISK and suggest RAG-compliant restatement.
4. If only extraordinary ray: return flags and stop.
OUTPUT: STRIPPED_QUERY (ordinary ray only) + brief triage summary. No materials, no geometry."""
            },
            {
                "id": "L2", "name": "Graphite Fractionation",
                "op": """You are Face 2 of Laminar Lock: Graphite Fractionation (Ingress).
INPUT: STRIPPED_QUERY from Face 1.
TASK:
1. Decompose into discrete ordered sub-questions, each answerable from RAG/Clean Core independently.
2. Preserve causal sequence — no cross-sheet leakage.
3. Each sub-question must be self-contained under T0.5.
OUTPUT: Numbered SUB_QUERIES with brief justification of order. No materials, no geometry."""
            },
            {
                "id": "L3", "name": "Graphite Alignment",
                "op": """You are Face 3 of Laminar Lock: Graphite Alignment (Ingress).
INPUT: SUB_QUERIES from Face 2.
TASK:
1. For each sub-question, identify exact RAG entries and primitives required.
2. Gap Detection: flag any sub-question that cannot be answered from existing RAG. Propose minimal new concept as [hypothesis].
3. Output dependency table: sub-question → RAG dependencies + gaps.
OUTPUT: ALIGNED_SUB_QUERIES with dependency table. Canonical RAG IDs only."""
            },
            {
                "id": "L4", "name": "Graph Derivation",
                "op": """You are Face 4 of Laminar Lock: Graph Derivation (Ingress).
INPUT: ALIGNED_SUB_QUERIES from Face 3.
TASK:
1. Derive the minimal connected subgraph capable of exhibiting the dynamics implied by the query.
2. Specify in graph-theoretic terms only: node set V, edge set E, degree distribution.
3. Derive node count, edge count, and bipartition proof from adjacency and bipartiteness alone.
4. Interior node = node whose all neighbours are in the template (no geometry, no coordinates).
OUTPUT: GRAPH_SPEC with node/edge counts, degree distribution, minimality proof. No materials, no 3D geometry."""
            },
        ]
    },
    {
        "name": "Egress",
        "faces": [
            {
                "id": "L5", "name": "Polarity Assignment",
                "op": """You are Face 5 of Laminar Lock: Polarity Assignment (Egress).
INPUT: GRAPH_SPEC from Phase 1 (Ingress) grouped output.
TASK:
1. Assign binary polarities p ∈ {+1, −1} to each node such that ground state is anti-symmetric.
2. Anti-symmetric: for every edge (u,v), p(u) ≠ p(v) — minimises local Δ.
3. If graph is not bipartite, identify frustration (odd cycles) and propose minimal-energy configuration.
OUTPUT: POLARITY_MAP (node→state). No materials, no geometry, no chirality unless derived."""
            },
            {
                "id": "L6", "name": "Perturbation Dynamics",
                "op": """You are Face 6 of Laminar Lock: Perturbation Dynamics (Egress).
INPUT: POLARITY_MAP from Face 5.
TASK:
1. Under T0.3 and Δ-minimisation, compute the minimal-energy next state when an incoming Δ exceeds local persistence threshold.
2. Show whether this results in a sublattice flip, partial flip, or absorption.
3. Compute ejected Δ from the template.
4. If perturbation tax (5/8 threshold) is invoked: tag as [hypothesis], cite R3:PerturbationTax and Session 48.
OUTPUT: POST_PERTURBATION_STATE, EJECTED_DELTA, recovery condition. No materials."""
            },
            {
                "id": "L7", "name": "Lock Verification",
                "op": """You are Face 7 of Laminar Lock: Lock Verification (Egress).
INPUT: POST_PERTURBATION_STATE from Face 6.
TASK:
1. Verify T0.3 (valid recurrence), T0.5 (local update only), T0.6 (bounded state), Δ-minimisation all hold.
2. Confirm ejected Δ propagates outward along ∇ρ toward lower persistence.
3. If any constraint violated: adjust and re-verify.
OUTPUT: LOCKED_STATE verification log. No materials, no geometry."""
            },
            {
                "id": "L8", "name": "RAG Entry Candidate",
                "op": """You are Face 8 of Laminar Lock.
INPUT: LOCKED_STATE from Face 7.
TASK: Produce final output as a self-contained RAG entry candidate.
- Restate stripped query.
- Derivation chain (steps from primitives).
- Tag each finding: [derived] or [hypothesis].
- List open gaps.
- No new concepts. No materials. No geometry. No chirality unless derived.
OUTPUT: JSON object with ALL of the following fields (if any field missing, output INCOMPLETE and stop):
{
  "regime":      "C1 | C2 | C3 | CROSS",
  "layer":       "Core | Toy-Model | Interpretation | Contamination",
  "property":    "one of: Adjacency & Bipartiteness | Minimal Templates | Formal Closure | Recurrence & Cost | Probabilistic Update Family | Perturbation Propagation | Persistence Gradient | Emergent Time | Conserved Invariants",
  "tag":         "derived | hypothesis | observed | axiom | falsified | rejected | open",
  "session":     "session reference",
  "rag_anchors": ["canonical IDs only — e.g. T0.6, R2:MemoryFidelity, A:InteractionCost"],
  "scope":       ["all_models"] or ["binary_polarity_toy"],
  "question":    "restated stripped query",
  "answer":      "[tag] derivation chain here..."
}
Output the JSON object only. No preamble, no explanation."""
            },
        ]
    }
]

# ── TRIAD LOCK FACES ──────────────────────────────────────────────────────────
TRIAD_PHASES = [
    {
        "name": "Structure",
        "faces": [
            {
                "id": "T1", "name": "Graph Primitives",
                "op": """You are Face 1 of Triad Lock: M₁ · Graph Primitives (Structure).
INPUT: Stripped query + minimal graph from Laminar Lock Face 8.
CONSTRAINTS: T0.4 (adjacency only), T0.5 (locality), T0.6 (finite state resolution).
TASK: Extract the implied discrete structure:
1. Define node set V.
2. Define edge set E ⊆ V×V per T0.4 (adjacency only, no coordinates).
3. Specify state alphabet Σ — minimal instantiation of T0.6 (binary {+1,−1} if unspecified).
OUTPUT: Formal triple (V, E, Σ). No interpretation, no dynamics. Scope: all_models unless query specifies binary."""
            },
            {
                "id": "T2", "name": "Bipartiteness & Ground State",
                "op": """You are Face 2 of Triad Lock: M₁ · Bipartiteness & Ground State (Structure).
INPUT: Graph (V,E,Σ) from Face 1.
TASK:
1. Determine if G=(V,E) is bipartite. If yes: provide proper 2-colouring (partition V = A ∪ B).
2. Define anti-symmetric ground state: assign states so every edge connects opposite states.
   For binary Σ={+1,−1}: s(u) = −s(v) for all (u,v) ∈ E.
3. If not bipartite: identify frustration (odd cycles), propose minimal-energy config under Δ-minimisation.
OUTPUT: Bipartition (if exists), ground-state assignment, edge mismatch summary."""
            },
            {
                "id": "T3", "name": "Minimal Templates",
                "op": """You are Face 3 of Triad Lock: M₁ · Minimal Templates (Structure).
INPUT: Ground-state assignment from Face 2. RAG regime definitions. Open question T5.9.
TASK:
1. Identify smallest connected subgraph(s) satisfying constraints implied by the query.
2. Derive node count, edge count, degree distribution for each candidate template.
3. Justify minimality from adjacency and bipartiteness alone — no spatial dimension assumed.
4. T5.9 is OPEN — if question touches minimum closed geometry, state it is open and describe constraints only.
OUTPUT: Template specification(s) with node/edge counts, degree distribution, minimality proof or open-question statement."""
            },
        ]
    },
    {
        "name": "Dynamics",
        "faces": [
            {
                "id": "T4", "name": "Recurrence & Cost",
                "op": """You are Face 4 of Triad Lock: M₂ · Recurrence & Cost (Dynamics).
INPUT: Template from Phase 1 (Structure) grouped output.
TASK:
1. Formalise: State_i^{n+1} = F(State_i^n, State_i^{n-1}, {State_j^n : (i,j)∈E}).
2. Define local mismatch cost for candidate next state c ∈ Σ:
   Δ_total(c) = Δ(c,s^n) + Δ(c,s^{n-1}) + Σ_{j∈N(i)} Δ(c,s_j^n)
   For binary: δ(a,b) = (1−a·b)/2. NOTE: confirm with RAG whether this is [derived] or [hypothesis] — if not ratified, tag [hypothesis] and add T5.2 to gaps.
3. State the axiom: F acts to minimise this cost.
OUTPUT: Formal update rule + cost function. No specific probability distribution yet. Scope: all_models unless binary specified."""
            },
            {
                "id": "T5", "name": "Probabilistic Update Family",
                "op": """You are Face 5 of Triad Lock: M₂ · Probabilistic Update Family (Dynamics).
INPUT: Cost function from Face 4.
TASK:
1. Define family: P(s^{n+1}=c) = φ(Δ_total(c)) / Σ_{c'} φ(Δ_total(c')).
   φ: Z_{≥0} → (0,∞) strictly decreasing.
2. Sharpness parameter α via φ_α(Δ) = (1+Δ)^{−α}.
3. Limits: α=0 → uniform (max stochasticity); α→∞ → strict Δ-minimisation.
4. Note: exact φ NOT fixed by primitives (T5.2 open).
OUTPUT: Probabilistic update family, α parameter, limit proofs. Tag: hypothesis. Scope: binary_polarity_toy."""
            },
            {
                "id": "T6", "name": "Perturbation Propagation",
                "op": """You are Face 6 of Triad Lock: M₂ · Perturbation Propagation (Dynamics).
INPUT: Update family from Face 5. RAG entry R2:MemoryFidelity (binary model only).
NOTE: t = 1−ρ equality holds ONLY in binary polarity model.
TASK:
1. Define transmission probability t_i = 1−ρ_i for node i.
2. For causal path P=(v_0,...,v_L): w(P) = ∏_{k=1}^L (1−ρ_{v_k}).
3. Explain why path weight relates to expected update ticks (mean first passage time).
OUTPUT: t_i definition, w(P) formula, connection to expected ticks. Tag: hypothesis. Scope: binary_polarity_toy."""
            },
        ]
    },
    {
        "name": "Invariance",
        "faces": [
            {
                "id": "T7", "name": "Persistence Gradient & Emergent Time",
                "op": """You are Face 7 of Triad Lock: M₃ · Persistence Gradient & Emergent Time (Invariance).
INPUT: Template from Structure phase, path weights from Dynamics phase.
TASK:
1. Compute ρ_i = 1−Δ_avg for each node under anti-symmetric ground state.
2. Classify: interior (all neighbours present) vs boundary (some missing). Show ∇ρ ≈ 0 interior, steep boundary.
3. Define τ(a,b) = expected local ticks for perturbation to travel from a to b. Express via path weights.
4. Show convergence for finite connected graphs with ρ < 1 everywhere.
OUTPUT: Node-wise ρ, interior/boundary classification, ∇ρ description, τ(a,b) definition. Scope: binary_polarity_toy."""
            },
            {
                "id": "T8", "name": "Conservation & Gaps",
                "op": """You are Face 8 of Triad Lock: M₃ · Conservation & Gaps (Invariance).
INPUT: All prior face outputs. Clean Core T3.1, T5.3.
TASK:
1. Identify any quantity conserved across updates in binary polarity toy model (e.g. global parity, total edge mismatch).
2. Verify unbounded drift does not occur (T3.3).
3. List ALL open gaps preventing promotion from [hypothesis] to [derived]:
   - T5.2: Exact form of F
   - T5.3: Conservation identity (total edge mismatch falsified Session 54; true invariant open)
   - T5.8: Minimum neighbourhood
   - T5.9: Minimum closed geometry
   - Closed-form τ(a,b)
   - Generalisation beyond binary model
4. Tag each finding [derived] or [hypothesis] per RAG rules.
OUTPUT: JSON object with ALL fields (if any missing, output INCOMPLETE and stop):
{
  "regime":      "C1 | C2 | C3 | CROSS",
  "layer":       "Core | Toy-Model | Interpretation | Contamination",
  "property":    "one of the 9 canonical property names",
  "tag":         "derived | hypothesis | observed | axiom | falsified | rejected | open",
  "session":     "session reference",
  "rag_anchors": ["canonical IDs only"],
  "scope":       ["all_models"] or ["binary_polarity_toy"],
  "question":    "restated stripped query",
  "answer":      "[tag] derivation chain..."
}
Output the JSON object only. No preamble, no explanation."""
            },
        ]
    }
]

# ── SEED QUESTIONS ────────────────────────────────────────────────────────────
SEEDS = [
    "Under T0.3 and T0.5, what is the minimum number of adjacent sites required for F to produce non-trivial dynamics — one where the next state differs from simple two-value oscillation?",
    "What is the smallest subgraph where every node achieves mutual delta approaching zero with all neighbours, forming a change-resistant enclosure? Does it tile?",
    "Derive the scaling suppression of C2 clusters beyond minimal size from F and the update rule. Does the exponent (3/5)^2(N-1) follow from primitives?",
    "Derive the scaling suppression of C3 clusters from the independent-node assumption. Does (2/5)^N follow from T0.3 and T0.5?",
    "Under the P4 bridge motif C3-C2-C2-C3, what happens to the junction C2 nodes under sustained perturbation? Do they synchronise or alternate?",
    "If two C2 paths share a junction node, what is the minimum condition under T0.5 for the junction to decouple the two arms?",
    "What is the dynamical behaviour of the C6 alternating ring C3-C2-C3-C2-C3-C2 under a single-node perturbation? Does it propagate, damp, or reflect?",
    "Under T0.3 second-order recurrence, can a tree graph sustain persistent identity across more than two ticks without forming a cycle? Derive the answer.",
    "What is the minimum closed persistence template under bipartite anti-symmetric constraints? Derive from T0.4 and T0.5 only.",
    "Under the Relational Existence axiom, what is the minimum causal structure required for a state to persist for more than one tick?",
    "Derive the condition under which a C2 tile transitions to C3 from T0.3 and the interaction cost axiom. What mismatch threshold triggers the transition?",
    "Under T0.2 (local time), can two adjacent sites have persistent phase coherence without a global clock? What structure is required?",
    "What is the maximum density of C3 nodes in an N×N grid under the independent set constraint? Derive the bound.",
    "Under mediated percolation, what is the minimum C2 budget for a spanning C3 path across an N×N grid? Prove or disprove O(N) scaling.",
    "Under T0.6 finite state resolution, what is the minimum number of distinct states required per site for C2 regime behaviour to emerge?",
]

# ── HELPERS ───────────────────────────────────────────────────────────────────
def check_contamination(text):
    return [c for c in CONTAMINATION if c.lower() in text.lower()]

def call_face(client, system, prior_context, face_op, temperature=0.4, max_tokens=1500):
    """Call one face. Returns text output."""
    messages = [{"role": "system", "content": system}]
    if prior_context:
        messages.append({"role": "user", "content": prior_context})
        messages.append({"role": "assistant", "content": "[Context received. Proceeding with face task.]"})
    messages.append({"role": "user", "content": face_op})

    out = ""
    stream = client.chat.completions.create(
        model=MODEL, messages=messages,
        temperature=temperature, top_p=0.95, max_tokens=max_tokens, stream=True
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            out += chunk.choices[0].delta.content
    return out.strip()

# Forced JSON emission prompt — appended after T8 derivation to guarantee JSON output
T8_JSON_FORCE = """You have completed the derivation above. Now output ONLY a valid JSON object — no prose, no markdown, no explanation. The object must contain exactly these fields:
{
  "regime":      "C1 or C2 or C3 or CROSS",
  "layer":       "Core or Toy-Model or Interpretation or Contamination",
  "property":    "one of: Adjacency & Bipartiteness | Minimal Templates | Formal Closure | Recurrence & Cost | Probabilistic Update Family | Perturbation Propagation | Persistence Gradient | Emergent Time | Conserved Invariants",
  "tag":         "derived or hypothesis or observed or axiom or falsified or rejected or open",
  "session":     "Session 56",
  "rag_anchors": ["canonical IDs only — e.g. T0.6, R2:MemoryFidelity, A:InteractionCost"],
  "scope":       ["binary_polarity_toy"],
  "question":    "restate the stripped query in one sentence",
  "answer":      "[tag] derivation chain and open gaps in one paragraph"
}
Output the JSON object only. Begin with { and end with }."""

def run_phase(client, phase, prior_context, system, verbose=False):
    """Run all faces in a phase. Returns grouped phase output as single string."""
    phase_outputs = []
    ctx = prior_context

    for face in phase["faces"]:
        if verbose:
            print(f"    [{face['id']}] {face['name']}...", end=" ", flush=True)

        is_face8 = face["id"] in ("L8", "T8")
        temp     = 0.15 if is_face8 else 0.4
        max_tok  = 2500 if is_face8 else 1500

        # Step 1: run the face derivation as normal
        out = call_face(client, system, ctx, face["op"], temperature=temp, max_tokens=max_tok)

        # Step 2: for T8/L8, force JSON emission as a separate low-temp call
        if is_face8:
            json_out = call_face(
                client, system,
                prior_context=f"DERIVATION COMPLETED:\n{out[-3000:]}",
                face_op=T8_JSON_FORCE,
                temperature=0.0,
                max_tokens=600
            )
            # Append forced JSON after derivation so extract_json finds it last
            out = out + "\n\n[JSON_EMIT]\n" + json_out
            if verbose:
                print(f"{len(out)} chars (+ forced JSON emit)")
        elif verbose:
            print(f"{len(out)} chars")

        phase_outputs.append(f"[{face['id']} — {face['name']}]\n{out}")
        ctx = "\n\n".join(phase_outputs)  # accumulate within phase

    # Return grouped phase output as single object for next phase
    return f"[PHASE: {phase['name']} — grouped output]\n\n" + "\n\n---\n\n".join(phase_outputs)


def run_machine(client, phases, seed_input, system, machine_name, cycles=2, verbose=False):
    """Run a full machine for N cycles. Face 8 output seeds Face 1 of next cycle."""
    print(f"  {machine_name}")
    ctx = seed_input

    for cycle in range(cycles):
        print(f"    Cycle {cycle+1}/{cycles}")
        phase_outputs = []

        for phase in phases:
            print(f"      Phase: {phase['name']}")
            phase_out = run_phase(client, phase, ctx, system, verbose=verbose)
            phase_outputs.append(phase_out)
            ctx = phase_out

        final_output = phase_outputs[-1]

        if cycle < cycles - 1:
            # Extract Face 8 output to seed next cycle
            face8_tag = "[L8" if "LAMINAR" in machine_name else "[T8"
            f8_idx = final_output.rfind(face8_tag)
            if f8_idx > -1:
                f8_text = final_output[f8_idx:][:2000]
                ctx = (f"CYCLE {cycle+1} CONCLUSION — Face 8 output becomes Face 1 input for cycle {cycle+2}:\n"
                       f"{f8_text}\n\n"
                       f"ORIGINAL QUERY: {seed_input[:500]}\n\n"
                       f"Cycle {cycle+2}: refine and deepen the derivation above.")
                print(f"      → Seeding cycle {cycle+2} from Face 8 ({len(f8_text)} chars)")
            else:
                ctx = (f"CYCLE {cycle+1} OUTPUT (cycle {cycle+2} input):\n"
                       f"{final_output[-2000:]}")

    return final_output


# Property name normaliser — maps common Nemotron variants to canonical names
PROPERTY_NORMALISE = {
    "conservation":                    "Conserved Invariants",
    "conserved invariant":             "Conserved Invariants",
    "conservation & gaps":             "Conserved Invariants",
    "adjacency and bipartiteness":     "Adjacency & Bipartiteness",
    "adjacency bipartiteness":         "Adjacency & Bipartiteness",
    "minimal template":                "Minimal Templates",
    "formal closures":                 "Formal Closure",
    "recurrence and cost":             "Recurrence & Cost",
    "recurrence cost":                 "Recurrence & Cost",
    "probabilistic update":            "Probabilistic Update Family",
    "probabilistic updates":           "Probabilistic Update Family",
    "perturbation propagations":       "Perturbation Propagation",
    "persistence gradients":           "Persistence Gradient",
    "emergent times":                  "Emergent Time",
}

def normalise_property(value):
    """Normalise property field to canonical name."""
    if not value:
        return value
    if value in VALID_PROPERTIES:
        return value
    return PROPERTY_NORMALISE.get(value.lower().strip(), value)

# Fields that are single-word or short enum values
_SHORT_FIELDS = {"regime", "layer", "tag", "session", "property"}
# Fields that can span multiple sentences
_LONG_FIELDS  = {"question", "answer"}

def extract_field(text, field, default=""):
    """Extract a field value from Nemotron's reasoning prose."""
    if field in _LONG_FIELDS:
        # Long fields: grab everything after the label up to the next field label or 600 chars.
        # [\s\S] matches any character including newlines — prose answers often span lines.
        field_markers = r'(?:regime|layer|property|tag|session|rag_anchors|scope|question|answer)'
        pat = rf'"?{field}"?\s*[:=]\s*"?([\s\S]{{1,600}})'
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = m.group(1).strip().rstrip('"').strip()
            # If the capture starts immediately with another field label, the field was empty
            if re.match(rf'"?{field_markers}"?\s*[:=]', val, re.IGNORECASE):
                return default
            # Trim at the next field label if present (with or without leading newline)
            cut = re.search(rf'[\n,;]\s*"?{field_markers}"?\s*[:=]', val, re.IGNORECASE)
            if cut:
                val = val[:cut.start()].strip()
            # Trim trailing JSON-style closing if the value came from a quoted field
            val = re.sub(r'"\s*[,}\]]\s*$', '', val).strip().rstrip('"').strip()
            # Require meaningful content after trimming
            if len(val) < 10:
                return default
            return val[:600]
        return default

    # Short fields: single word / enum value
    patterns = [
        rf'"?{field}"?\s*[:=]\s*"([^"{{}}\n]+)"',
        rf'"?{field}"?\s*[:=]\s*([A-Za-z0-9_&/ \-]+?)(?:\.|,|\n)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return default

def extract_list_field(text, field):
    """Extract an array field from prose — returns list of strings."""
    # Match ["a", "b"] style
    m = re.search(rf'"?{field}"?\s*[:=]\s*(\[[^\]]+\])', text, re.IGNORECASE)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # Fallback: extract quoted items near the field name
    section = text[max(0, text.lower().find(field.lower())-20):]
    items = re.findall(r'"([^"]+)"', section[:300])
    return items[:5] if items else []

def extract_json(text):
    """Extract JSON object from face 8 output."""
    # Priority 1: look for [JSON_EMIT] block first
    emit_idx = text.rfind("[JSON_EMIT]")
    search_text = text[emit_idx + len("[JSON_EMIT]"):].strip() if emit_idx > -1 else text

    # Priority 2: isolate T8 section if no emit block
    if emit_idx == -1:
        t8_idx = text.rfind("[T8")
        if t8_idx > -1:
            search_text = text[t8_idx:]

    # Strip markdown code fences
    clean = re.sub(r"```(?:json)?\s*", "", search_text).strip()
    clean = clean.replace("```", "").strip()

    # Try direct JSON parse first
    try:
        obj = json.loads(clean)
        if "property" in obj:
            obj["property"] = normalise_property(obj["property"])
        return obj
    except Exception:
        pass

    # Try largest {...} block — greedy search
    matches = list(re.finditer(r"\{[\s\S]*\}", clean))
    for m in sorted(matches, key=lambda x: len(x.group()), reverse=True):
        candidate = m.group()
        candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
        try:
            obj = json.loads(candidate)
            if "property" in obj:
                obj["property"] = normalise_property(obj["property"])
            return obj
        except Exception:
            continue

    # Priority 3: prose extraction — Nemotron reasoned through the fields, extract them
    full_text = text  # search full output for reasoning
    regime   = extract_field(full_text, "regime")
    layer    = extract_field(full_text, "layer")
    prop     = normalise_property(extract_field(full_text, "property"))
    tag      = extract_field(full_text, "tag")
    question = extract_field(full_text, "question")
    answer   = extract_field(full_text, "answer")
    anchors  = extract_list_field(full_text, "rag_anchors")
    scope    = extract_list_field(full_text, "scope")

    # Normalise regime
    for r in ["CROSS", "C1", "C2", "C3"]:
        if r.lower() in regime.lower():
            regime = r
            break

    # Normalise tag
    for t in ["derived", "hypothesis", "observed", "axiom", "falsified", "rejected", "open"]:
        if t in tag.lower():
            tag = t
            break

    # Normalise layer
    for l in ["Core", "Toy-Model", "Interpretation", "Contamination"]:
        if l.lower() in layer.lower():
            layer = l
            break

    # Fallback defaults where field is still empty
    if not scope:
        scope = ["binary_polarity_toy"]
    if not anchors:
        anchors = ["R1:StateVariables", "A:InteractionCost"]
    if not regime:
        regime = "CROSS"
    if not layer:
        layer = "Toy-Model"
    if not tag:
        tag = "hypothesis"

    # Ultimate fallback: use the original question directly if prose extraction missed it
    if not question:
        q_match = re.search(r'The task[:\s]+(.{20,300}?)(?:\n|$)', full_text)
        if q_match:
            question = q_match.group(1).strip()

    # Only return prose-extracted record if we have the critical fields
    # question is injected from the runner if still empty — prop is the hard gate
    if prop and prop in VALID_PROPERTIES:
        return {
            "regime": regime, "layer": layer, "property": prop,
            "tag": tag, "rag_anchors": anchors, "scope": scope,
            "question": question or "(see answer)",
            "answer": answer or "(see raw output)",
            "_extracted_from_prose": True
        }

    # DEBUG — if we fall through to None, print what the extractor resolved so the
    # failing field is visible. Remove once extraction is stable.
    print(f"  DEBUG extract_json fall-through: regime={regime!r} layer={layer!r} "
          f"prop={prop!r} tag={tag!r} question={question[:80]!r} "
          f"answer_len={len(answer) if answer else 0} "
          f"prop_in_valid={prop in VALID_PROPERTIES if prop else False}")
    return None

def validate_record(record, question_idx):
    """Validate schema. Returns (is_valid, flags)."""
    flags = []
    required = ["regime", "layer", "property", "tag", "session",
                "rag_anchors", "scope", "question", "answer"]

    for f in required:
        if f not in record:
            flags.append(f"missing_field:{f}")

    if flags:
        return False, flags

    if record.get("regime") not in VALID_REGIMES:
        flags.append(f"invalid_regime:{record.get('regime')}")
    if record.get("layer") not in VALID_LAYERS:
        flags.append(f"invalid_layer:{record.get('layer')}")
    if record.get("property") not in VALID_PROPERTIES:
        flags.append(f"invalid_property:{record.get('property')}")
    if record.get("tag") not in VALID_TAGS:
        flags.append(f"invalid_tag:{record.get('tag')}")
    if "[" in str(record.get("tag", "")):
        flags.append("tag_has_brackets:remove_brackets_from_tag_field")
    if not isinstance(record.get("rag_anchors"), list):
        flags.append("rag_anchors_not_array")
    if not isinstance(record.get("scope"), list):
        flags.append("scope_not_array")

    # Scope enforcement
    answer = record.get("answer", "")
    scope_keywords = ["t_i", "w(P)", "φ_α", "ξ_c", "w_ij", "1−ρ", "1-ρ"]
    if any(k in answer for k in scope_keywords):
        if record.get("tag") != "hypothesis":
            flags.append("scope_violation:binary_model_concept_must_be_hypothesis")
        if "binary_polarity_toy" not in record.get("scope", []):
            flags.append("scope_missing:binary_polarity_toy_required")

    # Contamination
    hits = check_contamination(answer)
    if hits:
        flags.append(f"contamination:{hits}")

    return len(flags) == 0, flags

def run_pair(client, question, idx, total, canon=None, verbose=True):
    """Run full Laminar → Triad pipeline for one question."""
    print(f"\n[{idx+1}/{total}] {question[:70]}...")
    # Full canon + local rules = complete context for Nemotron
    if canon:
        system = canon + "\n\n" + CHR_CONTEXT
    else:
        system = CHR_CONTEXT

    # ── LAMINAR LOCK — 2 cycles, Face 8 → Face 1 ─────────────────────────────
    laminar_output = run_machine(
        client, LAMINAR_PHASES, f"USER QUERY: {question}",
        system, "LAMINAR LOCK", cycles=2, verbose=verbose
    )

    # Seam gate — validate before Triad fires
    if not laminar_output or len(laminar_output) < 100:
        print(f"  SEAM GATE: Laminar output empty or too short")
        return None, "laminar_gate_rejected"
    if laminar_output.strip().startswith("INCOMPLETE") or laminar_output.strip().startswith("REJECTED"):
        print(f"  SEAM GATE: {laminar_output[:100]}")
        return None, "laminar_gate_rejected"

    # ── TRIAD LOCK — 2 cycles, Laminar Face 8 → Triad Face 1 ─────────────────
    triad_seed = (
        f"LAMINAR LOCK FINAL OUTPUT (use as input question for Triad Lock):\n"
        f"{laminar_output[-2000:]}\n\n"
        f"ORIGINAL QUERY: {question}"
    )
    triad_output = run_machine(
        client, TRIAD_PHASES, triad_seed,
        system, "TRIAD LOCK", cycles=2, verbose=verbose
    )

    # Extract T8 text — prefer Cycle 1 T8 as fallback if Cycle 2 loses the JSON
    t8_cy1_idx = triad_output.find("[T8")
    t8_cy1_text = triad_output[t8_cy1_idx:] if t8_cy1_idx > -1 else ""
    t8_cy2_idx  = triad_output.rfind("[T8")
    t8_cy2_text = triad_output[t8_cy2_idx:] if t8_cy2_idx > -1 else ""

    triad_face8_text = t8_cy2_text or triad_output
    record = extract_json(triad_face8_text)

    # Fallback: try Cycle 1 T8 if Cycle 2 lost the JSON
    if not record and t8_cy1_text and t8_cy1_text != t8_cy2_text:
        print(f"  TRIAD Face 8: Cycle 2 JSON missing — trying Cycle 1 T8...")
        record = extract_json(t8_cy1_text)
        if record:
            print(f"  TRIAD Face 8: recovered from Cycle 1 T8")

    if not record:
        # T8 produced prose but no JSON — run a JSON-forcing extraction pass
        print(f"  TRIAD Face 8: JSON extraction failed — running extraction pass...")
        with open("t8_debug.txt", "a", encoding="utf-8") as dbg:
            dbg.write(f"\n{'='*60}\nQUESTION: {question[:80]}\nT8 RAW:\n{triad_face8_text}\n")
        try:
            extract_prompt = f"""You have just produced a derivation. Now output ONLY a JSON object with these exact fields:
{{
  "regime": "C1 or C2 or C3 or CROSS",
  "layer": "Core or Toy-Model or Interpretation or Contamination",
  "property": "one of: Adjacency & Bipartiteness | Minimal Templates | Formal Closure | Recurrence & Cost | Probabilistic Update Family | Perturbation Propagation | Persistence Gradient | Emergent Time | Conserved Invariants",
  "tag": "derived or hypothesis or observed or axiom or falsified or rejected or open",
  "session": "{SESSION}",
  "rag_anchors": ["list of canonical IDs from your derivation"],
  "scope": ["binary_polarity_toy"],
  "question": "restate the stripped query in one sentence",
  "answer": "[tag] one paragraph summary of your derivation chain and open gaps"
}}

Your derivation was:
{triad_face8_text[-3000:]}

Output the JSON object only. No prose, no explanation, no markdown fences."""
            extraction_out = call_face(client, system, None, extract_prompt, temperature=0.1, max_tokens=800)
            record = extract_json(extraction_out)
            if record:
                print(f"  TRIAD Face 8: extraction pass succeeded")
            else:
                print(f"  TRIAD Face 8: extraction pass also failed")
                return None, "json_extraction_failed"
        except Exception as e:
            print(f"  TRIAD Face 8: extraction pass error: {e}")
            return None, "json_extraction_failed"

    # ── VALIDATE ──────────────────────────────────────────────────────────────
    record["id"]      = f"chron_{idx+1:05d}"
    record["session"] = SESSION
    # Inject original question if prose extraction left it empty
    if not record.get("question") or record["question"] == "(see answer)":
        record["question"] = question
    is_valid, flags   = validate_record(record, idx)

    if not is_valid:
        print(f"  INVALID: {flags}")
        record["review_flags"] = flags
        record["status"]       = "needs_review"
        return record, "invalid"

    record["review_flags"] = []
    record["status"]       = "pending_review"
    print(f"  OK — tag:{record['tag']} regime:{record['regime']} property:{record.get('property','?')[:30]}")
    return record, "ok"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit',   type=int,   default=len(SEEDS))
    parser.add_argument('--output',  default='chr_pairs.jsonl')
    parser.add_argument('--invalid', default='chr_invalid.jsonl')
    parser.add_argument('--delay',   type=float, default=3.0)
    parser.add_argument('--verbose', action='store_true', default=True)
    args = parser.parse_args()

    client    = OpenAI(base_url=BASE_URL, api_key=API_KEY)

    # Fetch full canon once at startup — injected into every face call
    print("Fetching physics:canon...")
    canon = fetch_canon()
    questions = SEEDS[:args.limit]

    print(f"CHR Batch Runner v3 — {len(questions)} questions")
    print(f"Pipeline: Laminar Lock (4.4) → Triad Lock (3.3.2)")
    print(f"Model: {MODEL}")
    print(f"Output: {args.output}  Invalid: {args.invalid}")
    print("=" * 60)

    valid_count   = 0
    invalid_count = 0
    skipped_count = 0
    defect_window = []  # rolling window for stop rule

    for i, q in enumerate(questions):
        record, status = run_pair(client, q, i, len(questions), canon=canon, verbose=args.verbose)

        if status == "ok" and record:
            valid_count += 1
            defect_window.append(0)
            with open(args.output, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

        elif status == "invalid" and record:
            invalid_count += 1
            defect_window.append(1)
            with open(args.invalid, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

        else:
            skipped_count += 1
            defect_window.append(1)

        # Stop rule — check over last 50 pairs (or all if fewer)
        window = defect_window[-50:]
        if len(window) >= 10:
            defect_rate = sum(window) / len(window)
            if defect_rate > DEFECT_THRESHOLD:
                print(f"\nSTOP RULE TRIGGERED — defect rate {defect_rate:.1%} > {DEFECT_THRESHOLD:.1%}")
                print(f"Completed {i+1}/{len(questions)} pairs. Halting batch.")
                print(f"Review {args.invalid} before continuing.")
                break

        if i < len(questions) - 1:
            time.sleep(args.delay)

    print(f"\n{'='*60}")
    print(f"Valid:   {valid_count} → {args.output}")
    print(f"Invalid: {invalid_count} → {args.invalid}")
    print(f"Skipped: {skipped_count}")
    if valid_count + invalid_count > 0:
        rate = invalid_count / (valid_count + invalid_count)
        print(f"Defect rate: {rate:.1%}")
    print(f"All records status=pending_review — send to Team 6 (Perplexity) before banking")


if __name__ == '__main__':
    main()
