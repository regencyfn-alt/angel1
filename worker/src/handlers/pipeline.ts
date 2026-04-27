// Pipeline — Laminar Lock + Triad Lock 4-endpoint chain
//
// Architecture (4-call):
//   Call 1: /physics/laminar/1-4   (fresh)                      → L1-L4 output
//   Call 2: /physics/laminar/5-8   (priorContext = L1-L4)       → L5-L8 + face8 record
//   Call 3: /physics/triad/1-4     (priorContext = L1-L8 || L4) → T1-T4 output
//   Call 4: /physics/triad/5-8     (priorContext = T1-T4)       → T5-T8 + final record
//
// Each handler runs 4 face firings via NVIDIA Nemotron 70B/120B.
// Face 8 of each pair returns a structured RAG candidate.
// Face 8 reads BOTH physics:canon AND physics:operational (Session 61).
//
// Includes Session 60 question-propagation fix (commit 5a326a8) — qHeader
// is prepended to ctx on every iteration so all 16 face firings see the
// original user question, not just Face 1.

import { Env } from '../types/env';
import { jsonResponse, errorResponse, physicsAuth } from './_shared';
import { loadCanonOnly, loadCanonAndOperational } from './canon';

const NVIDIA_BASE = 'https://integrate.api.nvidia.com/v1/chat/completions';
const NVIDIA_MODEL = 'nvidia/nemotron-3-super-120b-a12b';

// ── NVIDIA call helper ─────────────────────────────────────────────────
async function nCall(env: Env, sys: string, ctx: string, op: string, temp: number): Promise<string> {
  const msgs: any[] = [{ role: 'system', content: sys }];
  if (ctx) {
    msgs.push({ role: 'user', content: ctx });
    msgs.push({ role: 'assistant', content: '[Context received.]' });
  }
  msgs.push({ role: 'user', content: op });

  const r = await fetch(NVIDIA_BASE, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${env.NVIDIA_API_KEY}`,
    },
    body: JSON.stringify({
      model: NVIDIA_MODEL,
      messages: msgs,
      temperature: temp,
      max_tokens: 1200,
    }),
  });

  const d = await r.json() as any;
  return d.choices?.[0]?.message?.content || '(no output)';
}

// ── System prompt builder (Faces 1-7 read canon only; Face 8 dual-read) ─
async function buildFaceSystem(env: Env, session: string, faceNum: number): Promise<string> {
  // Face 8 (in either chain) gets canon + operational with precedence.
  // Faces 1-7 see canon only — keeps them focused on derivation, not policing.
  const ctx = (faceNum === 8)
    ? await loadCanonAndOperational(env)
    : await loadCanonOnly(env);

  const rules = `rho=1-Delta_avg. C1:rho<=0.4|C2:0.4<rho<=0.8|C3:rho>0.8. CORRECT:Delta=0.7->rho=0.3->C1.
t=1-rho,w(P),phi_alpha->hypothesis+binary_polarity_toy. T5.2,T5.3,T5.8,T5.9 never closed silently.
EXCLUSIONS:torsion,Z/3Z,SU(2),Hamiltonians,continuum,chirality(unless derived),materials,3D coords.
tag=plain string. [tag] prefix in answer text only. Session: ${session}`;

  return ctx + '\n\n' + rules;
}

// ── Face 8 RAG record schema (used by both Laminar and Triad) ──────────
const FACE8_SCHEMA = `{"regime":"C1|C2|C3|CROSS","layer":"Core|Toy-Model|Interpretation|Contamination","property":"Adjacency & Bipartiteness|Minimal Templates|Formal Closure|Recurrence & Cost|Probabilistic Update Family|Perturbation Propagation|Persistence Gradient|Emergent Time|Conserved Invariants","tag":"derived|hypothesis|observed|axiom|falsified|rejected|open","session":"$SESSION","rag_anchors":["canonical IDs"],"scope":["all_models"],"question":"restated stripped query","answer":"[tag] derivation chain"}`;

// ── Face prompts — Laminar 1-4 ─────────────────────────────────────────
const LAMINAR_1_4 = [
  { id: 'L1', face: 1, op: 'You are Face 1 of Laminar Lock: Calcite Gate. Reject contamination terms (torsion,Z/3Z,SU(2),Hamiltonians,chirality). Split query into ordinary ray (RAG-aligned) and extraordinary ray. OUTPUT: STRIPPED_QUERY + triage.', temp: 0.3 },
  { id: 'L2', face: 2, op: 'You are Face 2: Graphite Fractionation. Decompose STRIPPED_QUERY into ordered sub-questions each answerable from RAG/Clean Core independently. OUTPUT: Numbered SUB_QUERIES.', temp: 0.3 },
  { id: 'L3', face: 3, op: 'You are Face 3: Graphite Alignment. Map each sub-question to RAG entries. Flag gaps as [hypothesis]. OUTPUT: ALIGNED_SUB_QUERIES with dependency table. Canonical RAG IDs only.', temp: 0.3 },
  { id: 'L4', face: 4, op: 'You are Face 4: Graph Derivation. Derive minimal connected subgraph — node set V, edge set E, degree distribution. Interior=all neighbours present. No coordinates, no materials. OUTPUT: GRAPH_SPEC.', temp: 0.35 },
];

// ── Face prompts — Laminar 5-8 ─────────────────────────────────────────
function laminarFaces58(session: string) {
  return [
    { id: 'L5', face: 5, op: 'You are Face 5: Polarity Assignment. Assign binary polarities anti-symmetrically — p(u)!=p(v) for every edge. If not bipartite: identify frustration. OUTPUT: POLARITY_MAP.', temp: 0.3 },
    { id: 'L6', face: 6, op: 'You are Face 6: Perturbation Dynamics. Under T0.3 and delta-minimisation compute next state when delta exceeds persistence threshold. Show sublattice flip or absorption. Compute ejected delta. If perturbation tax invoked: tag [hypothesis], cite R3:PerturbationTax. OUTPUT: POST_PERTURBATION_STATE, EJECTED_DELTA.', temp: 0.35 },
    { id: 'L7', face: 7, op: 'You are Face 7: Lock Verification. Verify T0.3, T0.5, T0.6, delta-minimisation all hold. Confirm ejected delta propagates along gradient. OUTPUT: LOCKED_STATE verification log.', temp: 0.2 },
    { id: 'L8', face: 8, op: `You are Face 8 of Laminar Lock. FALSIFICATION AUDIT: check operational blacklist before any invariant or conserved-quantity discussion. Conservation claims must be scoped to the actual live invariant (parity-style on Eulerian graphs, T5.3a), not to general I-conservation. Produce RAG entry candidate. Output JSON with ALL fields — if any field is missing output only the word INCOMPLETE on its own line:\n${FACE8_SCHEMA.replace('$SESSION', session)}\nJSON only. No preamble.`, temp: 0.15 },
  ];
}

// ── Face prompts — Triad 1-4 ───────────────────────────────────────────
const TRIAD_1_4 = [
  { id: 'T1', face: 1, op: 'You are Face 1 of Triad Lock: Graph Primitives. Extract formal triple (V,E,Sigma). T0.4 adjacency only, T0.6 finite state. No interpretation, no dynamics. Scope: all_models.', temp: 0.3 },
  { id: 'T2', face: 2, op: 'You are Face 2: Bipartiteness & Ground State. Is G bipartite? 2-colouring V=A+B. Anti-symmetric ground state: s(u)=-s(v) for all edges. If not bipartite: identify frustration. OPERATIONAL: do NOT reject degree-1 or degree-3 graphs wholesale as "Non-Eulerian Geometry" — that rejection is too strong and conflicts with valid motifs (e.g., P4). May flag parity leak for a specific invariant claim. OUTPUT: Bipartition, ground-state, edge mismatch summary.', temp: 0.3 },
  { id: 'T3', face: 3, op: 'You are Face 3: Minimal Templates. Smallest connected subgraph satisfying constraints. Derive node/edge count, minimality from adjacency only. T5.9 is OPEN — state it explicitly. OUTPUT: Template spec with minimality proof or open-question statement.', temp: 0.35 },
  { id: 'T4', face: 4, op: 'You are Face 4: Recurrence & Cost. Formalise update rule and delta_total(c). For binary: delta(a,b)=(1-a*b)/2 — tag [hypothesis] if unratified, add T5.2 to gaps. State axiom: F minimises cost. OPERATIONAL: do NOT impose hard staleness clamps or Seizure Thresholds. Staleness Blocking remains hypothesis-tagged. Scope: all_models.', temp: 0.3 },
];

// ── Face prompts — Triad 5-8 ───────────────────────────────────────────
function triadFaces58(session: string) {
  return [
    { id: 'T5', face: 5, op: 'You are Face 5: Probabilistic Update Family. P(s=c)=phi(delta)/sum(phi). phi strictly decreasing. alpha sharpness. Limits: alpha=0 uniform, alpha->inf deterministic. T5.2 open. Tag:hypothesis. Scope:binary_polarity_toy.', temp: 0.3 },
    { id: 'T6', face: 6, op: 'You are Face 6: Perturbation Propagation. t_i=1-rho_i. w(P)=product(1-rho). Connection to expected ticks tau. Binary model only. Tag:hypothesis. Scope:binary_polarity_toy.', temp: 0.3 },
    { id: 'T7', face: 7, op: 'You are Face 7: Persistence Gradient & Emergent Time. rho_i=1-Delta_avg per node. Interior(all neighbours)->gradient approx 0. Boundary->steep gradient. OPERATIONAL: do NOT request closed-form tau(a,b) or general convergence claim unless explicitly supplied with stronger premises. Default output is the qualitative path-weight relation only. Scope:binary_polarity_toy.', temp: 0.25 },
    { id: 'T8', face: 8, op: `You are Face 8 of Triad Lock: Conservation & Gaps. FALSIFICATION AUDIT: check operational blacklist before any invariant or conserved-quantity discussion. Identify conserved quantities. T3.3: no unbounded drift (finite state space, derived). List ALL open gaps: T5.2, T5.3 (edge mismatch falsified Session 54; true invariant open), T5.8, T5.9, closed-form tau(a,b), generalisation beyond binary. Tag each finding. Output JSON ALL fields — if any missing output only INCOMPLETE on its own line:\n${FACE8_SCHEMA.replace('$SESSION', session)}\nJSON only.`, temp: 0.15 },
  ];
}

// ── Generic 4-face runner with question propagation fix ────────────────
async function runFaces(
  env: Env,
  faces: Array<{ id: string; face: number; op: string; temp: number }>,
  question: string,
  priorContext: string,
  ctxLabel: string,
  session: string,
): Promise<{ outputs: string[]; finalCtx: string }> {
  const outputs: string[] = [];

  // qHeader is prepended every iteration so faces never lose the original question
  // (Session 60 fix, commit 5a326a8 — Shard discovered 14/16 face firings were blind)
  const qHeader = `ORIGINAL QUERY: ${question}\n\n`;

  let ctx = priorContext
    ? `${qHeader}${ctxLabel}:\n${priorContext}`
    : `${qHeader}USER QUERY: ${question}`;

  for (const f of faces) {
    const sys = await buildFaceSystem(env, session, f.face);
    const out = await nCall(env, sys, ctx, f.op, f.temp);
    outputs.push(`[${f.id}]\n${out}`);
    // Rebuild ctx with qHeader at the front so next face still sees the question
    ctx = priorContext
      ? `${qHeader}${ctxLabel}:\n${priorContext}\n\n[${ctxLabel.includes('LAMINAR') ? 'LAMINAR' : 'TRIAD'} FACES 5+]:\n` + outputs.join('\n\n---\n\n')
      : `${qHeader}` + outputs.join('\n\n---\n\n');
  }

  return { outputs, finalCtx: ctx };
}

// ── /physics/laminar/1-4 ───────────────────────────────────────────────
export async function handleLaminar14(request: Request, env: Env): Promise<Response> {
  const auth = physicsAuth(request, env.PHYSICS_KEY);
  if (auth) return auth;

  const body = await request.json() as {
    question?: string;
    priorContext?: string;
    session?: string;
    layer0_packet?: any;     // Layer 0 packet attached by UI/dispatcher
  };
  if (!body.question) return errorResponse('question required', 400);

  const session = body.session || 'Session 62';

  // If a Layer 0 packet was attached, log it. (Future: refuse without packet
  // when enforcement mode is enabled via env flag.)
  if (!body.layer0_packet) {
    console.warn('[laminar/1-4] no layer0_packet attached — ingress audit bypassed');
  }

  // Prepend packet declarations to context if present, so faces see what was declared
  const declCtx = body.layer0_packet
    ? `\nLAYER 0 DECLARATIONS:\n  schema/instantiation: ${body.layer0_packet.declarations?.schema_or_instantiation || 'unspecified'}\n  branch: ${body.layer0_packet.declarations?.branch || 'n/a'}\n  falsified items in scope: ${body.layer0_packet.audit?.falsified_count ?? 'unknown'}\n`
    : '';

  const { outputs, finalCtx } = await runFaces(env, LAMINAR_1_4, body.question, body.priorContext || '', '', session);

  return jsonResponse({
    ok: true,
    output: declCtx + finalCtx,
    lastFace: outputs[outputs.length - 1],
    question: body.question,
    session,
    layer0_attached: !!body.layer0_packet,
  });
}

// ── /physics/laminar/5-8 ───────────────────────────────────────────────
export async function handleLaminar58(request: Request, env: Env): Promise<Response> {
  const auth = physicsAuth(request, env.PHYSICS_KEY);
  if (auth) return auth;

  const body = await request.json() as { question?: string; priorContext?: string; session?: string };
  if (!body.question || !body.priorContext) return errorResponse('question and priorContext required', 400);

  const session = body.session || 'Session 62';
  const { outputs, finalCtx } = await runFaces(env, laminarFaces58(session), body.question, body.priorContext, 'LAMINAR FACES 1-4', session);

  const face8 = outputs[outputs.length - 1];
  const f8c = face8.replace(/^\[L8[^\]]*\]\s*/i, '').trimStart();

  if (f8c.startsWith('INCOMPLETE')) {
    return jsonResponse({ ok: false, stage: 'laminar_gate', reason: f8c.slice(0, 200) });
  }

  return jsonResponse({ ok: true, output: finalCtx, face8, question: body.question, session });
}

// ── /physics/triad/1-4 ─────────────────────────────────────────────────
export async function handleTriad14(request: Request, env: Env): Promise<Response> {
  const auth = physicsAuth(request, env.PHYSICS_KEY);
  if (auth) return auth;

  const body = await request.json() as {
    question?: string;
    priorContext?: string;
    session?: string;
    layer0_packet?: any;
  };
  if (!body.question) return errorResponse('question required', 400);

  const session = body.session || 'Session 62';

  if (!body.layer0_packet) {
    console.warn('[triad/1-4] no layer0_packet attached — ingress audit bypassed');
  }

  const { outputs, finalCtx } = await runFaces(env, TRIAD_1_4, body.question, body.priorContext || '', body.priorContext ? 'LAMINAR OUTPUT' : '', session);

  return jsonResponse({
    ok: true,
    output: finalCtx,
    lastFace: outputs[outputs.length - 1],
    question: body.question,
    session,
    layer0_attached: !!body.layer0_packet,
  });
}

// ── /physics/triad/5-8 — final RAG record ──────────────────────────────
export async function handleTriad58(request: Request, env: Env): Promise<Response> {
  const auth = physicsAuth(request, env.PHYSICS_KEY);
  if (auth) return auth;

  const body = await request.json() as { question?: string; priorContext?: string; session?: string };
  if (!body.question || !body.priorContext) return errorResponse('question and priorContext required', 400);

  const session = body.session || 'Session 62';
  const { outputs } = await runFaces(env, triadFaces58(session), body.question, body.priorContext, 'TRIAD FACES 1-4', session);

  const face8 = outputs[outputs.length - 1];
  const f8c = face8.replace(/^\[T8[^\]]*\]\s*/i, '').trimStart();

  // Try to parse JSON from face8 output
  let record: any = null;
  const jm = f8c.match(/\{[\s\S]*\}/);
  if (jm) {
    try {
      record = JSON.parse(jm[0].replace(/,\s*([}\]])/g, '$1'));
    } catch (_) {}
  }

  // Fallback: ask Nemotron to extract structured record from prose
  if (!record && !f8c.startsWith('INCOMPLETE')) {
    try {
      const sys = await buildFaceSystem(env, session, 8);
      const exOut = await nCall(env, sys, '',
        `Output ONLY a JSON object with fields regime,layer,property,tag,session,rag_anchors,scope,question,answer from this derivation:\n${f8c.slice(-2000)}`,
        0.1);
      const em = exOut.match(/\{[\s\S]*\}/);
      if (em) record = JSON.parse(em[0].replace(/,\s*([}\]])/g, '$1'));
    } catch (_) {}
  }

  if (!record) {
    return jsonResponse({ ok: false, stage: 'triad_face8', raw: f8c.slice(0, 500) });
  }

  record.id = `chron_${Date.now()}`;
  record.session = session;
  record.status = 'pending_review';

  // Persist to KV under chr_pairs:{id} for batch runner pickup
  try {
    await env.MICHRON_KV.put(`chr_pairs:${record.id}`, JSON.stringify(record), {
      expirationTtl: 86400 * 365, // 1 year
    });
  } catch (_) {}

  return jsonResponse({ ok: true, record, face8 });
}
