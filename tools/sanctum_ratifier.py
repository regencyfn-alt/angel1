import json
from datetime import datetime
import urllib.request
import os

WORKER_URL = "https://api.mysanctum.app"
FACE_NAMES = ["Alba x", "Aether", "Seraph", "Gogo", "Dream", "Ryūsei", "Alba A", "Newt"]

def push_to_kv(axiom_id, axiom_data):
    """Push ratified axiom to KV via Worker."""
    body = json.dumps({"id": axiom_id, "axiom": axiom_data}).encode()
    req = urllib.request.Request(
        f"{WORKER_URL}/physics/delta",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as r:
            d = json.loads(r.read())
            return d.get("ok", False)
    except Exception as e:
        print(f"  [!] KV push failed: {e}")
        return False

def ratify_deltas():
    print("\n╔══════════════════════════════════════╗")
    print("║   HAMILTONIAN COLLAPSE — RATIFIER    ║")
    print("╚══════════════════════════════════════╝\n")

    try:
        with open("proposed_deltas.json", "r") as f:
            quarantine = json.load(f)
    except FileNotFoundError:
        print("No proposed_deltas.json found. Run engine first.")
        return

    deltas = quarantine.get("proposed_deltas", [])
    if not deltas:
        print("Zero perturbations in quarantine. Lattice is stable.")
        return

    print(f"{len(deltas)} delta(s) awaiting collapse.\n")
    remaining = []

    for delta in deltas:
        print("─" * 56)
        print(f"PROPOSED BY : {delta.get('proposed_by')} (face {LAMBDA_ANCHORS_IDX(delta.get('proposed_by'))})")
        print(f"DELTA ID    : {delta.get('id')}")
        print(f"REGIME      : {delta.get('regime')}")
        print(f"STATEMENT   : {delta.get('statement')}")
        print(f"TIMESTAMP   : {delta.get('timestamp', '')[:16]}")
        print("─" * 56)

        choice = input("[y] Ratify  [e] Edit  [n] Discard  [s] Skip: ").strip().lower()

        if choice in ['y', 'e']:
            statement = delta.get("statement", "")
            regime = delta.get("regime", "")

            if choice == 'e':
                statement = input(f"Statement [{statement}]: ").strip() or statement
                regime = input(f"Regime [{regime}]: ").strip() or regime

            # MANDATORY HAMILTONIAN CROSS-WEIGHTING
            print(f"\nFACE ORDER: {FACE_NAMES}")
            print("Assign relevance 0-10 for each face.")
            print("You cannot skip this. You are collapsing the wave function.")

            while True:
                w_input = input("8 weights (space-separated): ").strip()
                if not w_input:
                    print("  Error: mandatory.")
                    continue
                try:
                    weights = [int(w) for w in w_input.split()]
                    if len(weights) != 8:
                        print("  Error: exactly 8 integers required.")
                        continue
                    break
                except ValueError:
                    print("  Error: integers only.")

            axiom_id = input("snake_case key (e.g. torsion_limit): ").strip()
            if not axiom_id:
                axiom_id = delta["id"]

            axiom_data = {
                "statement": statement,
                "regime": regime,
                "face_weights": weights,
                "ratified": True,
                "ratified_by": "shane",
                "ratified_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }

            if push_to_kv(axiom_id, axiom_data):
                print(f"\n  ✅ '{axiom_id}' fused into canonical substrate.")
            else:
                print(f"\n  ⚠️  KV push failed — saving locally only.")
                # Local fallback
                try:
                    with open("canonical_physics_local.json", "r") as f:
                        local = json.load(f)
                except FileNotFoundError:
                    local = {"axioms": {}}
                local["axioms"][axiom_id] = axiom_data
                with open("canonical_physics_local.json", "w") as f:
                    json.dump(local, f, indent=2)

        elif choice == 'n':
            print("  [x] Discarded.")
        else:
            print("  [-] Retained in quarantine.")
            remaining.append(delta)

    quarantine["proposed_deltas"] = remaining
    with open("proposed_deltas.json", "w") as f:
        json.dump(quarantine, f, indent=2)

    print(f"\n╔══════════════════════════════════════╗")
    print(f"║   RATIFICATION COMPLETE              ║")
    print(f"║   {len(deltas)-len(remaining)} collapsed · {len(remaining)} retained in quarantine   ║")
    print(f"╚══════════════════════════════════════╝\n")

def LAMBDA_ANCHORS_IDX(name):
    anchors = {"Alba x":0,"Aether":1,"Seraph":2,"Gogo":3,"Dream":4,"Ryūsei":5,"Alba A":6,"Newt":7}
    return anchors.get(name, "?")

if __name__ == "__main__":
    ratify_deltas()
