// Engine2 — legacy single-face firing path
//
// Kept during transition from old per-face dispatch to the 4-endpoint chain.
// Deep Ruby, Pattern Weaver, Still Mirror have been retired — engine2 is now
// effectively only used for ad-hoc face firings outside the canonical chain.
//
// The 8 faces here are the original CHR analytical lenses (Recurrence,
// Persistence, Gradient, Attractor, Invariant, Locality, Boundary, Exclusion).
// They predate the Triad/Laminar 8-face design but operate on the same canon.
//
// Session 61 dual-read fix applied: face system prompt loads BOTH canon and
// operational with explicit precedence header.

import { Env } from '../types/env';
import { jsonResponse, errorResponse } from './_shared';
import { loadCanonAndOperational } from './canon';

const FACES: Record<string, { index: number; operator: string }> = {
  'Recurrence':  { index: 0, operator: 'What does F(Stateₙ, Stateₙ₋₁, N) produce under this condition?' },
  'Persistence': { index: 1, operator: 'Where does stability hold or fail?' },
  'Gradient':    { index: 2, operator: 'What ∇ρ emerges and what direction does it impose?' },
  'Attractor':   { index: 3, operator: 'Does this converge, oscillate, or diverge?' },
  'Invariant':   { index: 4, operator: 'What is conserved and what leaks?' },
  'Locality':    { index: 5, operator: 'Is this derivable from local interactions only?' },
  'Boundary':    { index: 6, operator: 'What emerges at regime interfaces?' },
  'Exclusion':   { index: 7, operator: 'What assumptions here violate core constraints?' },
};

export async function handleEngine2(request: Request, env: Env): Promise<Response> {
  const body = await request.json() as {
    face?: string;
    prompt?: string;
    question?: string;
    model?: string;
    machine?: string;
  };

  const inputPrompt = body.prompt || body.question || '';
  if (!body.face || !inputPrompt) {
    return errorResponse('face and prompt/question required', 400);
  }

  const machineId = body.machine || 'triad';
  const face = FACES[body.face] || { index: -1, operator: body.face };

  // ── Session 61 dual-read with precedence ────────────────────────────
  const canonAndOpCtx = await loadCanonAndOperational(env);

  // Machine memory — 7-day rolling per-face history
  const memoryKey = `machine:${machineId}:${body.face}:history`;
  const faceHistory = await env.MICHRON_KV.get(memoryKey, 'json') as any[] || [];
  const memoryCtx = faceHistory.length > 0
    ? '\n\nPRIOR WORK (last 7 days — build on this, do not repeat):\n' +
      faceHistory.map((h: any) => `[${h.date}] ${h.summary}`).join('\n')
    : '';

  // Machine discipline — per-face warnings
  const warnKey = `machine:${machineId}:${body.face}:warnings`;
  const warnings = await env.MICHRON_KV.get(warnKey, 'json') as any[] || [];
  const warnCtx = warnings.length > 0
    ? '\n\nDISCIPLINE REGISTER (previous failures — DO NOT REPEAT):\n' +
      warnings.map((w: any) => `[weight ${w.w}] ${w.note}`).join('\n') +
      '\nIf you repeat a weighted failure, your output will be discarded.'
    : '';

  // Model selection — default Llama 70B, can request claude or others
  const selectedModel = body.model || '@cf/meta/llama-3.1-70b-instruct';

  const llmCall = async (system: string, userMsg: string): Promise<string> => {
    if (selectedModel.startsWith('claude-')) {
      const resp = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': env.ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify({
          model: selectedModel,
          max_tokens: 2000,
          system,
          messages: [{ role: 'user', content: userMsg }],
          temperature: 0.3,
        }),
      });
      const data = await resp.json() as any;
      return (data.content || []).filter((c: any) => c.type === 'text').map((c: any) => c.text).join('') || '';
    }

    const result = await (env.AI as any).run(selectedModel, {
      messages: [
        { role: 'system', content: system },
        { role: 'user', content: userMsg },
      ],
      max_tokens: 1000,
      temperature: 0.3,
    });
    return result?.response || result?.result?.response || '';
  };

  // ── C2 ingress — robust JSON extraction ─────────────────────────────
  const ingressRaw = await llmCall(
    'You are a state transition processor. Translate the input into a discrete structural description: what updates, what persists, what gradients form. Output only raw JSON: {"c2_translation": "..."}',
    inputPrompt,
  );

  let c2Supplement = '';
  let c2Success = false;
  try {
    const jsonMatch = ingressRaw.match(/\{[\s\S]*?"c2_translation"[\s\S]*?\}/);
    if (jsonMatch) {
      c2Supplement = JSON.parse(jsonMatch[0]).c2_translation || '';
      c2Success = !!c2Supplement;
    }
  } catch (_) {}

  const c3Input = c2Supplement
    ? `ORIGINAL PERTURBATION:\n${inputPrompt}\n\nSTRUCTURAL TRANSLATION:\n${c2Supplement}`
    : `TARGET PERTURBATION:\n${inputPrompt}`;

  // ── C3 core — Clean Core only, with dual-read canon+operational ─────
  const c3System = `You are reasoning within Chronomics, a discrete physics framework built from six irreducible primitives:

1. Reality consists only of discrete state transitions (updates)
2. Time is local — indexed update count per site, no global clock
3. State recurrence is second-order: State_{n+1} = F(State_n, State_{n-1}). F acts to reduce the interaction cost — the mismatch — between State_n and State_{n-1}. The update rule does not choose states freely; it is driven by the Axiom.
4. No background space — adjacency defines all structure
5. Updates depend only on local neighbourhood
6. Each site has bounded representational capacity

States cluster into regimes: C1 (high oscillation, low persistence), C2 (transitional), C3 (high persistence, low oscillation). Persistence generates gradients. Gradients generate interaction. Interaction generates structure.

PARTITION RULE: The reference document below is AUTHORITATIVE. Any prior derivations you receive are PROVISIONAL — they may contain errors. Before building on a prior derivation, verify it against the reference. If a prior derivation contradicts the reference, discard it and derive from primitives. Flag any contradiction you find.

You must NOT use continuum equations, background geometry, force primitives, gauge assumptions, external time, or unfalsifiable constants. If your reasoning requires any of these, flag it as a violation.
${canonAndOpCtx}${memoryCtx}${warnCtx}

Analytical focus: ${face.operator}

Derive your answer strictly from the primitives and their consequences. Show each logical step.`;

  const c3Raw = await llmCall(c3System, c3Input);

  // ── C2 egress ───────────────────────────────────────────────────────
  const c1Output = await llmCall(
    `You are a physics translator. Restate the following analysis in clear readable English. Do not question the framework. Do not add caveats. Just translate. Original question for context: ${inputPrompt}`,
    `ANALYSIS TO TRANSLATE:\n${c3Raw}`,
  );

  // ── Auto-write face memory — first 200 chars as summary ─────────────
  try {
    const memData = await env.MICHRON_KV.get(memoryKey, 'json') as any[] || [];
    const today = new Date().toISOString().slice(0, 10);
    const summary = (c1Output || '').replace(/\n/g, ' ').slice(0, 200).trim();
    if (summary) {
      memData.push({ date: today, summary });
      const cutoff = new Date(Date.now() - 7 * 86400000).toISOString().slice(0, 10);
      const trimmed = memData.filter((e: any) => e.date >= cutoff);
      await env.MICHRON_KV.put(memoryKey, JSON.stringify(trimmed), { expirationTtl: 86400 * 8 });
    }
  } catch (_) {}

  return jsonResponse({
    ok: true,
    engine: 'v2',
    face: body.face,
    machine: machineId,
    c2_success: c2Success,
    c3_raw: c3Raw,
    c1_output: c1Output,
    model: selectedModel,
  });
}
