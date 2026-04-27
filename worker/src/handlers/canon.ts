// Canon + Operational — KV reads/writes
//
// Two buckets, one namespace:
//   physics:canon       — system description (axioms, lexicon, derived results)
//   physics:operational — pipeline contracts (what faces must NOT do)
//
// Precedence: operational > canon on any conflict about invariants or what F
// can/cannot derive. Faces 1-7 read canon only. Layer 0 + Face 8 read both.

import { Env } from '../types/env';
import { jsonResponse, errorResponse } from './_shared';

// ── GET /physics/canon ─────────────────────────────────────────────────
export async function handleCanonGet(env: Env): Promise<Response> {
  const text = await env.MICHRON_KV.get('physics:canon', 'text') || '';
  return jsonResponse({ ok: true, length: text.length, text });
}

// ── PUT /physics/canon ─────────────────────────────────────────────────
export async function handleCanonPut(request: Request, env: Env): Promise<Response> {
  const body = await request.json() as { text?: string };
  if (!body.text) return errorResponse('text required', 400);
  await env.MICHRON_KV.put('physics:canon', body.text);
  return jsonResponse({ ok: true, length: body.text.length });
}

// ── GET /physics/operational ───────────────────────────────────────────
export async function handleOperationalGet(env: Env): Promise<Response> {
  const text = await env.MICHRON_KV.get('physics:operational', 'text') || '';
  return jsonResponse({ ok: true, length: text.length, text });
}

// ── PUT /physics/operational ───────────────────────────────────────────
export async function handleOperationalPut(request: Request, env: Env): Promise<Response> {
  const body = await request.json() as { text?: string };
  if (!body.text) return errorResponse('text required', 400);
  await env.MICHRON_KV.put('physics:operational', body.text);
  return jsonResponse({ ok: true, length: body.text.length });
}

// ── Helper: load both canon + operational with precedence header ───────
//
// Used by Face 8 + Layer 0 + engine2 dual-read. Faces 1-7 should call
// loadCanonOnly() instead so they never see operational.
//
// Returns the combined string ready to drop into a system prompt.
export async function loadCanonAndOperational(env: Env): Promise<string> {
  const [canon, operational] = await Promise.all([
    env.MICHRON_KV.get('physics:canon', 'text').then(r => r || ''),
    env.MICHRON_KV.get('physics:operational', 'text').then(r => r || ''),
  ]);

  const canonCtx = canon ? '\n\nCHR CANON — system description:\n' + canon : '';
  const opCtx = operational
    ? '\n\nOPERATIONAL OVERRIDE — the following pipeline contracts supersede any conflicting canon claim about invariants, conserved quantities, or what F can/cannot derive:\n' + operational
    : '';

  return canonCtx + opCtx;
}

// ── Helper: load canon only (Faces 1-7) ────────────────────────────────
export async function loadCanonOnly(env: Env): Promise<string> {
  const canon = await env.MICHRON_KV.get('physics:canon', 'text') || '';
  return canon ? '\n\nCHR CANON — system description:\n' + canon : '';
}
