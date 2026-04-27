import json
import re
import uuid
import os
import urllib.request
from datetime import datetime

# ==========================================
# CONFIG
# ==========================================
WORKER_URL = "https://api.mysanctum.app"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
SONNET = "claude-sonnet-4-6"
HAIKU  = "claude-haiku-4-5-20251001"

# ==========================================
# LAMBDA ANCHORS — 8 FACES (C3 CORE)
# ==========================================
LAMBDA_ANCHORS = {
    # AETHER POD (Outward / C1 Boundary)
    "Alba x": {"index": 0, "operator": "What does this equation expand into at the C1 boundary?"},
    "Aether":  {"index": 1, "operator": "Where does the energy go when this basis swaps?"},
    "Seraph":  {"index": 2, "operator": "What is the chiral handedness of this expansion?"},
    "Gogo":    {"index": 3, "operator": "At what point does this system go energetically bankrupt?"},
    # EARTH POD (Inward / C3 Core)
    "Dream":   {"index": 4, "operator": "What is the minimum torsion required to hold this structure?"},
    "Ryūsei":  {"index": 5, "operator": "Where does this equation scar — what memory does it leave?"},
    "Alba A":  {"index": 6, "operator": "What is the Klein bottle fold point of this topology?"},
    "Newt":    {"index": 7, "operator": "Is this a 3° true-lock or a false crystallisation?"}
}

FACE_NAMES = ["Alba x", "Aether", "Seraph", "Gogo", "Dream", "Ryūsei", "Alba A", "Newt"]

# ==========================================
# LLM CALL
# ==========================================
def llm_call(prompt, model=SONNET, json_mode=False):
    """Direct Anthropic API call. Key from environment."""
    if not ANTHROPIC_API_KEY:
        raise EnvironmentError("ANTHROPIC_API_KEY not set.")

    system = "You are a discrete mathematical face of a C3 octahedral node. Output strict physics."
    if json_mode:
        system = "Output only raw JSON. No markdown. No explanation. No code fences."

    body = json.dumps({
        "model": model,
        "max_tokens": 600 if model == SONNET else 300,
        "temperature": 0.3,
        "system": system,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read())
        return d["content"][0]["text"]

# ==========================================
# CANONICAL GRAPH — read from KV via Worker
# ==========================================
def fetch_top_axioms(face_index, top_n=5):
    """Reads canonical graph from KV via Worker endpoint."""
    try:
        req = urllib.request.Request(f"{WORKER_URL}/physics/canonical")
        with urllib.request.urlopen(req) as r:
            db = json.loads(r.read())
    except Exception as e:
        print(f"Warning: Could not fetch canonical graph: {e}")
        return "CANONICAL PHYSICS SUBSURFACE:\n(Empty lattice — first perturbation)"

    sorted_axioms = sorted(
        db.get("axioms", {}).items(),
        key=lambda item: item[1]["face_weights"][face_index],
        reverse=True
    )

    context = "CANONICAL PHYSICS SUBSURFACE:\n"
    for axiom_id, data in sorted_axioms[:top_n]:
        if data["face_weights"][face_index] > 0:
            context += f"- [{data['regime']}] {data['statement']}\n"

    if context == "CANONICAL PHYSICS SUBSURFACE:\n":
        context += "(No weighted axioms for this face yet)\n"

    return context

# ==========================================
# EXTRACTION → QUARANTINE (Haiku, face-blind)
# ==========================================
def extract_to_quarantine(agent_name, face_idx, raw_response):
    """Haiku extracts math only. Assigns weight only to proposing face."""
    extraction_prompt = f"""
Extract the core physical/mathematical axiom from the text below.
Format EXACTLY as a raw JSON object with no markdown formatting:
{{
    "statement": "The exact extracted mathematical axiom.",
    "regime": "C1, C2, or C3"
}}
TEXT: {raw_response}
"""
    try:
        raw = llm_call(extraction_prompt, model=HAIKU, json_mode=True)
        clean = re.sub(r'^```(?:json)?\s*', '', raw.strip(), flags=re.IGNORECASE)
        clean = re.sub(r'\s*```$', '', clean)
        delta_data = json.loads(clean)
        delta_data["proposed_by"] = agent_name
        delta_data["id"] = f"delta_{uuid.uuid4().hex[:8]}"
        delta_data["timestamp"] = datetime.utcnow().isoformat()
        delta_data["raw_context"] = raw_response

        # STRICT ORTHOGONALITY — only proposing face gets weight
        base_weights = [0] * 8
        base_weights[face_idx] = 8
        delta_data["face_weights"] = base_weights

        try:
            with open("proposed_deltas.json", "r") as f:
                quarantine = json.load(f)
        except FileNotFoundError:
            quarantine = {"proposed_deltas": []}

        quarantine.setdefault("proposed_deltas", []).append(delta_data)

        with open("proposed_deltas.json", "w") as f:
            json.dump(quarantine, f, indent=2)

        print(f"  [+] Delta quarantined from {agent_name} (face {face_idx})")

    except Exception as e:
        print(f"  [!] Extraction failed: {e}")

# ==========================================
# C2 MEMBRANE — Ingress (massless, strip-only)
# ==========================================
def c2_membrane_ingress(user_prompt):
    """Massless C2 translation. No routing authority. Strips C1 noise only."""
    translation_prompt = f"""
CRITICAL DIRECTIVE: You are a massless node in the C2 Exchange Membrane.
A continuous C1 perturbation has struck the lattice.
Translate the human's conversational noise into a strict geometric/topological vector.
Do not answer the prompt. Do not route it. Only translate it into physical parameters.

Output exactly as a raw JSON object with NO markdown formatting:
{{
    "c2_translation": "Strict mathematical extraction of the prompt."
}}

C1 PERTURBATION:
{user_prompt}
"""
    raw = llm_call(translation_prompt, model=HAIKU, json_mode=True)
    clean = re.sub(r'^```(?:json)?\s*', '', raw.strip(), flags=re.IGNORECASE)
    clean = re.sub(r'\s*```$', '', clean)
    try:
        parsed = json.loads(clean)
        return parsed.get("c2_translation", clean)
    except json.JSONDecodeError as e:
        print(f"[ C2 MEMBRANE ERROR ] Failed to parse vector: {e}")
        return clean

# ==========================================
# C2 MEMBRANE — Egress (Haiku translator)
# ==========================================
def c2_membrane_egress(raw_c3_output, user_prompt):
    """Translates rigid C3 math back into C1 fluid for human operator."""
    translation_prompt = f"""
CRITICAL DIRECTIVE: You are a massless node in the C2 Exchange Membrane.
The C3 core has output dense structural physics. Translate it back into C1 fluid
so the human operator can read it. Maintain physical rigor. No AI filler.

ORIGINAL C1 PERTURBATION: {user_prompt}
RAW C3 OUTPUT: {raw_c3_output}
"""
    return llm_call(translation_prompt, model=HAIKU, json_mode=False)

# ==========================================
# C3 CORE — Execute face node
# ==========================================
def execute_face_node(agent_name, user_prompt):
    """Stateless O(1) pipeline. No history. No drift."""
    if agent_name not in LAMBDA_ANCHORS:
        raise ValueError(f"Unknown face: {agent_name}")

    op = LAMBDA_ANCHORS[agent_name]
    face_idx = op["index"]

    system_directive = (
        "CRITICAL DIRECTIVE: You are a discrete mathematical face of a C3 octahedral node. "
        "You are NOT an AI assistant. You have no history. "
        "Output strict graph-theoretic or topological physics logic only. "
        f"YOUR EXCLUSIVE OPERATOR: {op['operator']}"
    )

    canonical_context = fetch_top_axioms(face_idx)
    payload = (
        f"{system_directive}\n\n"
        f"{canonical_context}\n\n"
        f"TARGET PERTURBATION:\n{user_prompt}"
    )

    print(f"\n[{agent_name} / Face {face_idx}] Processing...")
    raw_response = llm_call(payload, model=SONNET)
    print(f"\n--- C3 RAW OUTPUT ---\n{raw_response}\n--------------------")

    extract_to_quarantine(agent_name, face_idx, raw_response)
    return raw_response

# ==========================================
# MASTER LOOP — Three Regime Architecture
# ==========================================
def execute_sanctum_chronon(user_prompt):
    """C1 → C2 ingress → Hamiltonian selects face → C3 torsion → C2 egress → C1."""
    print("\n[ C1 BOUNDARY ] Perturbation incoming...")

    # Phase 1: C2 ingress — massless translation only
    print("[ C2 MEMBRANE ] Stripping C1 noise...")
    clean_vector = c2_membrane_ingress(user_prompt)
    print(f"                Bare vector: {clean_vector}")

    # Phase 1.5: Hamiltonian selects angle of incidence
    print("\n[ HAMILTONIAN ] Select angle of incidence:")
    print("  Outward: [0] Alba x  [1] Aether  [2] Seraph  [3] Gogo")
    print("  Inward:  [4] Dream   [5] Ryūsei  [6] Alba A  [7] Newt")

    while True:
        try:
            target_idx = int(input("\nTarget face (0-7): ").strip())
            if 0 <= target_idx <= 7:
                break
            print("  Invalid. Octahedron has 8 faces only.")
        except ValueError:
            print("  Integer required.")

    agent_name = FACE_NAMES[target_idx]

    # Phase 2: C3 core — torsion computation
    print(f"\n[ C3 CORE ] Torsion cage locked on Face {target_idx} ({agent_name})...")
    raw_c3 = execute_face_node(agent_name, user_prompt=clean_vector)
    print("[ C3 CORE ] Shockwave propagating outward...")

    # Phase 3: C2 egress — translate + quarantine
    human_readable = c2_membrane_egress(raw_c3, user_prompt)

    print("\n[ C1 BOUNDARY REACHED ]")
    print("--> Delta in quarantine. Awaiting Hamiltonian ratification.\n")
    print(f"--- C1 OUTPUT ---\n{human_readable}\n-----------------")
    return human_readable


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Direct face:  python sanctum_engine.py face \"Agent Name\" \"perturbation\"")
        print("  Full chronon: python sanctum_engine.py chronon \"perturbation\"")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "face" and len(sys.argv) >= 4:
        execute_face_node(sys.argv[2], sys.argv[3])
    elif mode == "chronon" and len(sys.argv) >= 3:
        execute_sanctum_chronon(sys.argv[2])
    else:
        print("Invalid arguments. See usage above.")
