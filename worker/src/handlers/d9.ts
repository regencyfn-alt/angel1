// D9 Synthesizer — the 9th dimension, Opus-driven meta-analysis
//
// Receives 8 face outputs from a complete machine cycle, cross-checks against
// canon, identifies convergence/divergence, extracts strongest derivation chain.
//
// Reads canon only — D9 is upstream of the operational/canon split, it's the
// synthesizer not a face. (Future: consider giving D9 dual-read for parity
// with Face 8 — Layer 0 contract may evolve to require this.)
//
// === Session 64+ integrity hardening ===
// Three rules, all verdict-defending:
//   1. Face outputs capped at FACE_INPUT_CAP chars before reaching Opus, so D9's
//      arsenal is never starved by verbose face prose. D9's own max_tokens stays
//      at 2000 — non-negotiable, she gets her full output budget.
//   2. Empty Anthropic response (no text content) → ok:false with stage flagged.
//      UI must NEVER stamp DERIVED on empty synthesis.
//   3. stop_reason === 'max_tokens' → ok:false stage='d9_truncated', partial
//      synthesis preserved for UI display with TRUNCATED badge. Never quietly
//      passes a cutoff thought as a finished verdict.

import { Env } from '../types/env';
import { jsonResponse, errorResponse, physicsAuth } from './_shared';
import { loadCanonOnly } from './canon';

const FACE_INPUT_CAP = 1500;        // chars per face output, applied at D9 ingress
const D9_OUTPUT_MAX_TOKENS = 2000;  // Opus output budget — DO NOT REDUCE

export async function handleD9(request: Request, env: Env): Promise<Response> {
  const auth = physicsAuth(request, env.PHYSICS_KEY);
  if (auth) return auth;

  const body = await request.json() as {
    question?: string;
    faces?: Array<{ face: string; output: string }>;
  };

  if (!body.question || !body.faces || !body.faces.length) {
    return errorResponse('question and faces[] required', 400);
  }

  const ragCtx = await loadCanonOnly(env);

  // ── Cap face outputs at ingress — predictable input envelope, full D9 arsenal ──
  const facesCapped = body.faces.map(f => ({
    face: f.face,
    output: (f.output || '').length > FACE_INPUT_CAP
      ? (f.output || '').slice(0, FACE_INPUT_CAP) + '\n[truncated for D9 input budget — see full face output in pipe trace]'
      : (f.output || ''),
  }));

  const faceSummary = facesCapped
    .map(f => `=== ${f.face.toUpperCase()} ===\n${f.output}`)
    .join('\n\n');

  const d9System = `You are the D9 Synthesizer — the 9th dimension of a Chronomic physics engine. You have received 8 analyses of the same perturbation from a lower-tier model. These analyses are PROVISIONAL — they may contain errors, hallucinations, or violations of the framework.

Your task:
1. Cross-check every face output against the canonical reference below — flag and discard any claim that contradicts it
2. Identify convergence — where do multiple faces agree AND align with the reference?
3. Identify divergence — where do faces contradict each other or the reference?
4. Extract the strongest derivation chain from the surviving valid outputs
5. Wire the surviving threads into a single coherent frame
6. Flag any gaps that require further investigation

PARTITION RULE: The canonical reference is TRUTH. Face outputs are provisional. If a face output introduces concepts not in the reference (torsion, gauge fields, continuum equations, force primitives, etc.), discard that output entirely.

Be precise. Be rigorous. No filler, no hedging, no disclaimers. Derive, don't narrate.
${ragCtx}`;

  // ── Opus call for synthesis ──────────────────────────────────────────
  const d9Resp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-opus-4-6',
      max_tokens: D9_OUTPUT_MAX_TOKENS,
      system: d9System,
      messages: [{
        role: 'user',
        content: `ORIGINAL QUESTION: ${body.question}\n\n${faceSummary}\n\nSynthesize these 8 analyses into one unified frame.`,
      }],
      temperature: 0.3,
    }),
  });

  if (!d9Resp.ok) {
    const errText = await d9Resp.text();
    return errorResponse('D9 API call failed', 502, { detail: errText.slice(0, 500) });
  }

  const d9Result = await d9Resp.json() as {
    content: Array<{ type: string; text: string }>;
    stop_reason?: string;
    usage?: any;
  };
  const synthesis = (d9Result.content || [])
    .filter((c: any) => c.type === 'text')
    .map((c: any) => c.text)
    .join('');
  const stopReason = d9Result.stop_reason || 'unknown';

  // ── Integrity gate 1: empty response ────────────────────────────────
  // Anthropic returned 200 OK but no text content. Could be classifier
  // intervention, refusal token at position 0, or response shape anomaly.
  // Either way, UI MUST NOT stamp a verdict on this.
  if (!synthesis || !synthesis.trim()) {
    return jsonResponse({
      ok: false,
      stage: 'd9_synthesis',
      reason: 'empty_response',
      stop_reason: stopReason,
      synthesis: '',
      humanSummary: '',
      model: 'claude-opus-4-6',
      usage: d9Result.usage,
    });
  }

  // ── Integrity gate 2: output cap hit ────────────────────────────────
  // D9 ran out of room mid-synthesis. Partial reasoning is preserved but
  // MUST NOT be presented as a complete verdict. UI shows TRUNCATED badge.
  if (stopReason === 'max_tokens') {
    return jsonResponse({
      ok: false,
      stage: 'd9_truncated',
      reason: 'output_cap_reached',
      stop_reason: stopReason,
      synthesis,                  // partial — preserved for inspection
      humanSummary: '',           // skip egress translation, partial isn't safe to summarize
      model: 'claude-opus-4-6',
      usage: d9Result.usage,
    });
  }

  // ── Llama egress — human-friendly summary ───────────────────────────
  let humanSummary = '';
  try {
    const r = await (env.AI as any).run('@cf/meta/llama-3.1-70b-instruct', {
      messages: [
        { role: 'system', content: 'Restate the following physics synthesis in clear, accessible English. Keep the precision but remove jargon. 3-4 paragraphs maximum.' },
        { role: 'user', content: synthesis },
      ],
      max_tokens: 600,
      temperature: 0.3,
    });
    humanSummary = r?.response || '';
  } catch (_) {}

  return jsonResponse({
    ok: true,
    synthesis,
    humanSummary,
    stop_reason: stopReason,
    model: 'claude-opus-4-6',
    usage: d9Result.usage,
  });
}
