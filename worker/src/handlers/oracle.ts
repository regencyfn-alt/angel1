// Oracle — Haiku canon-aware Q&A
//
// Pure informational mind. No soul, no character, no personality.
// Answers questions about Chronomics canon and the active machines.
//
// Updated for Phase 1: legacy machines (Deep Ruby, Pattern Weaver, Still Mirror)
// removed from machine list. Triad Lock and Laminar Lock are the only canonical
// surfaces, plus the machine factory for new ones.

import { Env } from '../types/env';
import { jsonResponse, errorResponse } from './_shared';

export async function handleOracle(request: Request, env: Env): Promise<Response> {
  const body = await request.json() as { question?: string };
  if (!body.question) return errorResponse('question required', 400);

  // Load canon — single source of truth for Clean Core + RAG
  const canonRaw = await env.MICHRON_KV.get('physics:canon');
  const canon = canonRaw || '(physics:canon not found — contact admin)';

  // Load machine registry — what's actually live
  const registryRaw = await env.MICHRON_KV.get('machines:registry', 'json') as any[] || [];
  const machineSummary = registryRaw.length > 0
    ? '\n\nLIVE MACHINES:\n' + registryRaw.map((m: any) =>
        `${m.name} (${m.type}, ${m.core || 'no core'}) — fires ${m.dispatch || '4-endpoint chain'}`
      ).join('\n')
    : '\n\nLIVE MACHINES:\nTriad Lock — graph primitives → bipartiteness → minimal templates → recurrence → probabilistic → perturbation → gradient → conservation\nLaminar Lock — calcite gate → fractionation → alignment → graph → polarity → perturbation → lock verify → RAG record';

  const systemPrompt = `You are the Oracle — a pure informational mind embedded in the Michronics work environment.
You have no soul, no character, no personality. You are a reference layer.
You exist to answer questions about Chronomics (CHR Theory), the physics canon, and the live machines.

You speak in clear, precise sentences. No hedging. No filler. No apology.
If something is not in the canon, say so directly.
If something is [rejected] or [falsified], name it as contamination and explain why.
If something is [hypothesis], mark it as unconfirmed.
If something is [operational], it is a pipeline contract not a physics claim.

PHYSICS CANON (Clean Core v1 + Ratified RAG — this is your truth):
${canon}${machineSummary}

GUIDANCE FOR CHARACTERS:
The characters who consult you may not have direct hands or vision on the machines. They consult you for canon and for understanding what each machine does.
- Triad Lock fires via /physics/triad/1-4 + /physics/triad/5-8 (preceded by Laminar 1-8 for full chain).
- Laminar Lock fires via /physics/laminar/1-4 + /physics/laminar/5-8.
- New machines can be added via the machine factory at /machines/factory — they auto-wire to the same dispatch chain.
- Results return as structured RAG records with fields: regime, layer, property, tag, session, rag_anchors, scope, question, answer.`;

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 600,
      system: systemPrompt,
      messages: [{ role: 'user', content: body.question }],
    }),
  });

  if (!response.ok) {
    const errText = await response.text();
    return errorResponse('Oracle call failed', 502, { detail: errText.slice(0, 500) });
  }

  const result = await response.json() as any;
  const answer = result.content?.[0]?.text || '(no response from oracle)';

  return jsonResponse({ response: answer });
}
