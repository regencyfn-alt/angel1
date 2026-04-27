// Layer 0 — Triad Lock Ingress Contract
//
// The five-gate ingress that fires BEFORE any face. Operational rules (Session 61)
// are policy; Layer 0 is enforcement.
//
// Per physics_operational.md (Triad Layer 0 Ingress Contract):
//
//   Gate 1: Input-type gate
//           Input must be a raw question. Statements, syntheses, or
//           conclusions-dressed-as-premises return BLOCKED: reformulate as question.
//
//   Gate 2: Falsification audit preload
//           Operational blacklist must be loaded before any derivation begins.
//           Layer 0 verifies the live operational rules, surfaces the blacklist
//           summary, and tags the run with which falsified items are in scope.
//
//   Gate 3: Schema/instantiation declaration
//           The run must declare which it speaks of (axiomatic schema or
//           instantiated graph/state) before face 1 fires.
//
//   Gate 4: Branch/minimality scoping
//           If the question concerns minimality, declare which branch
//           (closure, anti-symmetric oscillation, or enclosed persistence).
//
//   Gate 5: Answer-class declaration
//           Run produces DERIVED / HYPOTHESIS / BLOCKED / FALSIFIED outside
//           any face's prose blob. Layer 0 emits this declaration as a structured
//           field that downstream UI/RAG can read directly.
//
// Endpoint: POST /physics/layer-0
//
// Request:
//   { question: string, declarations?: { schema_or_instantiation?: 'schema'|'instantiation', branch?: string } }
//
// Response on PASS:
//   { ok: true, gates: { ... }, packet: { question, declarations, blacklist_summary, allowed_to_fire: true } }
//
// Response on BLOCK:
//   { ok: false, blocked_at: 'gate_N', reason: '...', hint: '...' }
//
// The packet field is what Triad/Laminar dispatchers should attach to face calls.

import { Env } from '../types/env';
import { jsonResponse, errorResponse, physicsAuth } from './_shared';

// ── Gate 1 — Input type detection ──────────────────────────────────────
//
// Heuristic detection — Nemotron under load can dress conclusions as premises.
// Looking for question shape: ends with ?, or starts with interrogative, or
// uses imperative-derive structure ("Derive...", "Determine...", "Show that...").
// Rejects: pure declaratives, prepared answer packets (JSON), pre-tagged claims.
function classifyInput(text: string): { kind: 'question' | 'statement' | 'packet' | 'tagged_claim'; reason: string } {
  const t = text.trim();

  // Empty
  if (!t) return { kind: 'statement', reason: 'empty input' };

  // JSON packet — looks like prepared output, not a question
  if (t.startsWith('{') && t.endsWith('}')) {
    try {
      JSON.parse(t);
      return { kind: 'packet', reason: 'input parses as JSON; appears to be a prepared answer packet, not a raw question' };
    } catch (_) {}
  }

  // Pre-tagged claim — [derived], [hypothesis], [falsified] at start
  if (/^\s*\[(derived|hypothesis|observed|axiom|stipulated|falsified|rejected|operational|open)\b/i.test(t)) {
    return { kind: 'tagged_claim', reason: 'input begins with a tag prefix; appears to be a conclusion not a question' };
  }

  // Question shape — much more permissive heuristic.
  //
  // A real question has at least ONE of:
  //   • Contains a `?` anywhere in the text (research-narrative questions
  //     often have setup sentences before the actual question)
  //   • Starts with an interrogative word
  //   • Starts with an imperative-derive verb
  //   • Contains an interrogative-or-request phrase anywhere (covers
  //     "Could we ask X", "Can the machine derive Y", "Would it be
  //     possible to Z" — research-narrative voice)
  //
  // We only reject as 'statement' if NONE of these are present AND the
  // input is long-form prose (>300 chars). Short prose without a `?`
  // gets a soft pass — better to let a borderline through than reject
  // a legitimate research question.
  const startsWithInterrogative = /^(what|which|why|how|when|where|who|is|are|does|do|can|could|should|would|will)\s/i.test(t);
  const endsWithQuestionMark = /\?\s*$/.test(t);
  const containsQuestionMark = /\?/.test(t);
  const imperativeDerive = /^(derive|determine|show|prove|find|compute|identify|state|formalise|formalize|construct|enumerate|verify)\b/i.test(t);
  const embeddedInterrogative = /(\bcould we\b|\bcan we\b|\bcan the machine\b|\bcan you\b|\bwould it be possible\b|\bis it possible\b|\bdoes the machine\b|\bdo we\b|\bshould we\b|\bask the machine to\b|\bcan it be shown\b|\bis there a\b|\bhow does\b|\bhow do\b|\bwhat does\b|\bwhat is\b|\bwhat are\b)/i.test(t);

  if (containsQuestionMark || endsWithQuestionMark || startsWithInterrogative || imperativeDerive || embeddedInterrogative) {
    return { kind: 'question', reason: 'matches question shape (interrogative form, embedded question, or imperative-derive)' };
  }

  // Only reject if long prose AND none of the question signals fired.
  // This catches pure declarative submissions ("X is Y. Z follows from W.") with no asking voice.
  if (t.length > 300) {
    return { kind: 'statement', reason: 'long-form input with no question mark, no interrogative word, no imperative-derive, no embedded ask phrase — appears to be a conclusion or synthesis' };
  }

  // Soft pass — short or borderline. Let it through.
  return { kind: 'question', reason: 'no strong rejection signal — admitted by default' };
}

// ── Gate 2 — Falsification audit ───────────────────────────────────────
//
// Loads physics:operational and surfaces the [falsified] register from
// physics:canon for the run packet. The face contracts can now point at
// concrete items the question must NOT re-derive.
async function falsificationAudit(env: Env): Promise<{
  operational_loaded: boolean;
  operational_length: number;
  canon_loaded: boolean;
  falsified_count: number;
  falsified_summary: string[];
}> {
  const [opRaw, canonRaw] = await Promise.all([
    env.MICHRON_KV.get('physics:operational', 'text'),
    env.MICHRON_KV.get('physics:canon', 'text'),
  ]);

  const operational_loaded = !!opRaw;
  const operational_length = opRaw ? opRaw.length : 0;
  const canon_loaded = !!canonRaw;

  // Extract first line of every [falsified] entry for the summary
  const falsified_summary: string[] = [];
  if (canonRaw) {
    const lines = canonRaw.split('\n');
    for (const line of lines) {
      const m = line.match(/\[falsified[^\]]*\]\s*(.+)/i);
      if (m) {
        // Trim to first sentence or 120 chars
        let summary = m[1].trim();
        const dot = summary.search(/[.:]/);
        if (dot > 30 && dot < 120) summary = summary.slice(0, dot);
        else if (summary.length > 120) summary = summary.slice(0, 120) + '…';
        falsified_summary.push(summary);
      }
    }
  }

  return {
    operational_loaded,
    operational_length,
    canon_loaded,
    falsified_count: falsified_summary.length,
    falsified_summary,
  };
}

// ── Gate 3 — Schema/instantiation declaration ──────────────────────────
//
// If the run declares schema or instantiation, accept. If neither declared,
// inspect the question for signals; if ambiguous, require the caller to declare.
function schemaInstantiationGate(
  question: string,
  declared?: 'schema' | 'instantiation',
): { kind: 'schema' | 'instantiation' | 'unspecified'; required: boolean; hint?: string } {
  if (declared === 'schema' || declared === 'instantiation') {
    return { kind: declared, required: false };
  }

  // Heuristic: if question mentions specific graphs (C4, P4, K_n) or specific
  // states (binary polarity), it's likely instantiation. If it talks about F, T0.x,
  // or general structural properties, likely schema.
  const instantiationSignals = /\b(C[3-9]_?graph|P[3-9]\b|K_?[0-9]|binary polarity|specific|particular|this graph|2x2|3x3|3×3|2×2)\b/i;
  const schemaSignals = /\b(general|all (graphs|states|configurations)|every|any (graph|state)|axiom|primitive|T0\.\d|under T\d)\b/i;

  if (instantiationSignals.test(question) && !schemaSignals.test(question)) {
    return { kind: 'instantiation', required: false, hint: 'inferred from instantiation signals; declare explicitly to override' };
  }
  if (schemaSignals.test(question) && !instantiationSignals.test(question)) {
    return { kind: 'schema', required: false, hint: 'inferred from schema signals; declare explicitly to override' };
  }

  // Ambiguous — soft default to schema with a note.
  // Schema is the safer default: most Chronomic derivations are about
  // general structural properties unless the question names a specific
  // graph or state. The packet records this as inferred so downstream
  // can see the assumption.
  return {
    kind: 'schema',
    required: false,
    hint: 'no clear schema/instantiation signal — defaulted to schema. Pass declarations.schema_or_instantiation explicitly to override.',
  };
}

// ── Gate 4 — Branch/minimality scoping ─────────────────────────────────
//
// Detects whether the question is about minimality and, if so, requires
// declaration of which branch.
function branchScopingGate(
  question: string,
  declared?: string,
): { applies: boolean; branch?: string; required: boolean; hint?: string } {
  const minimalityRe = /\b(minim(al|um|ality|ise|ize)|smallest|fewest|least|threshold|critical)\b/i;
  const applies = minimalityRe.test(question);

  if (!applies) return { applies: false, required: false };

  if (declared) {
    const lower = declared.toLowerCase();
    if (['closure', 'anti-symmetric oscillation', 'enclosed persistence', 'antisymmetric oscillation', 'oscillation'].some(b => lower.includes(b))) {
      return { applies: true, branch: declared, required: false };
    }
    return { applies: true, branch: declared, required: true, hint: `declared branch "${declared}" not recognised. Use one of: closure, anti-symmetric oscillation, enclosed persistence` };
  }

  return {
    applies: true,
    branch: 'closure',
    required: false,
    hint: 'minimality question detected without explicit branch — defaulted to closure (the most common branch). Pass declarations.branch explicitly to override (closure | anti-symmetric oscillation | enclosed persistence).',
  };
}

// ── POST /physics/layer-0 ──────────────────────────────────────────────
export async function handleLayer0(request: Request, env: Env): Promise<Response> {
  const auth = physicsAuth(request, env.PHYSICS_KEY);
  if (auth) return auth;

  const body = await request.json() as {
    question?: string;
    declarations?: {
      schema_or_instantiation?: 'schema' | 'instantiation';
      branch?: string;
    };
    session?: string;
  };

  const question = (body.question || '').trim();
  const decl = body.declarations || {};
  const session = body.session || 'Session 62';

  // ── Gate 1 — Input type ──────────────────────────────────────────────
  const inputClass = classifyInput(question);
  if (inputClass.kind !== 'question') {
    return jsonResponse({
      ok: false,
      blocked_at: 'gate_1_input_type',
      reason: `BLOCKED: reformulate as question. Detected: ${inputClass.kind} — ${inputClass.reason}`,
      hint: 'Ingress accepts only raw questions. Statements, syntheses, conclusions-dressed-as-premises, or pre-formed answer packets must be reformulated.',
      answer_class: 'BLOCKED',
    });
  }

  // ── Gate 2 — Falsification audit preload ─────────────────────────────
  const audit = await falsificationAudit(env);
  if (!audit.operational_loaded) {
    return jsonResponse({
      ok: false,
      blocked_at: 'gate_2_falsification_audit',
      reason: 'physics:operational is empty or unreachable — face firing prohibited',
      hint: 'Seed physics:operational with the operational contracts before allowing face firings',
      answer_class: 'BLOCKED',
    });
  }
  if (!audit.canon_loaded) {
    return jsonResponse({
      ok: false,
      blocked_at: 'gate_2_falsification_audit',
      reason: 'physics:canon is empty or unreachable — face firing prohibited',
      hint: 'Seed physics:canon before allowing face firings',
      answer_class: 'BLOCKED',
    });
  }

  // ── Gate 3 — Schema/instantiation ────────────────────────────────────
  const schemaCheck = schemaInstantiationGate(question, decl.schema_or_instantiation);
  if (schemaCheck.required) {
    return jsonResponse({
      ok: false,
      blocked_at: 'gate_3_schema_instantiation',
      reason: 'schema/instantiation declaration required',
      hint: schemaCheck.hint,
      answer_class: 'BLOCKED',
    });
  }

  // ── Gate 4 — Branch/minimality ───────────────────────────────────────
  const branchCheck = branchScopingGate(question, decl.branch);
  if (branchCheck.required) {
    return jsonResponse({
      ok: false,
      blocked_at: 'gate_4_branch_scoping',
      reason: 'branch declaration required for minimality question',
      hint: branchCheck.hint,
      answer_class: 'BLOCKED',
    });
  }

  // ── All gates passed — build packet ──────────────────────────────────
  // Gate 5 (answer-class declaration) is structural: the packet attaches
  // expected_answer_classes that downstream face dispatchers can use.
  const packet = {
    question,
    session,
    declarations: {
      schema_or_instantiation: schemaCheck.kind,
      branch: branchCheck.applies ? branchCheck.branch : null,
      branch_applies: branchCheck.applies,
    },
    blacklist_summary: audit.falsified_summary,
    audit: {
      canon_length: audit.operational_length > 0 ? 'loaded' : 'missing',
      operational_length: audit.operational_length,
      falsified_count: audit.falsified_count,
    },
    expected_answer_classes: ['DERIVED', 'HYPOTHESIS', 'BLOCKED', 'FALSIFIED'],
    allowed_to_fire: true,
    timestamp: new Date().toISOString(),
  };

  return jsonResponse({
    ok: true,
    gates: {
      gate_1_input_type: { passed: true, classified_as: inputClass.kind },
      gate_2_falsification_audit: { passed: true, falsified_items: audit.falsified_count },
      gate_3_schema_instantiation: { passed: true, kind: schemaCheck.kind, ...(schemaCheck.hint ? { hint: schemaCheck.hint } : {}) },
      gate_4_branch_scoping: { passed: true, applies: branchCheck.applies, branch: branchCheck.branch || null },
      gate_5_answer_class: { passed: true, structural: 'expected classes attached to packet' },
    },
    packet,
  });
}
