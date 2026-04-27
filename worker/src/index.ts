/**
 * Michronics Worker — Slim Router
 *
 * Maths only. No characters. No chat. No personalities.
 * Lifted from MySanctumLive/src/index.ts lines 901-1460 + Session 61 dual-read fix.
 *
 * Endpoints:
 *   GET    /health
 *   GET    /physics/canon              — system description
 *   PUT    /physics/canon
 *   GET    /physics/operational        — pipeline contracts
 *   PUT    /physics/operational
 *   POST   /physics/layer-0            — five-gate ingress before face firing
 *   POST   /physics/engine2            — legacy single-face firing (with dual-read)
 *   POST   /physics/d9                 — Opus synthesis of 8 face outputs
 *   POST   /physics/laminar/1-4        — Laminar Lock faces 1-4
 *   POST   /physics/laminar/5-8        — Laminar Lock faces 5-8 + RAG record
 *   POST   /physics/triad/1-4          — Triad Lock faces 1-4
 *   POST   /physics/triad/5-8          — Triad Lock faces 5-8 + final record
 *   POST   /oracle                     — Haiku canon-aware Q&A
 *   GET    /machines/list              — registry of all machines
 *   GET    /machines/:id               — single machine config
 *   POST   /machines/factory           — create new machine, auto-wire dispatch
 *   PUT    /machines/:id               — update existing machine
 *   DELETE /machines/:id               — delete (built-ins protected)
 *
 * Auth: X-Physics-Key header on /physics/* and /machines/factory mutations.
 *       PHYSICS_KEY secret set via `wrangler secret put PHYSICS_KEY`.
 */

import { Env } from './types/env';
import { corsHeaders } from './handlers/_shared';
import { handleHealth } from './handlers/health';
import {
  handleCanonGet, handleCanonPut,
  handleOperationalGet, handleOperationalPut,
} from './handlers/canon';
import { handleEngine2 } from './handlers/engine2';
import { handleD9 } from './handlers/d9';
import { handleOracle } from './handlers/oracle';
import {
  handleLaminar14, handleLaminar58,
  handleTriad14, handleTriad58,
} from './handlers/pipeline';
import { handleLayer0 } from './handlers/layer0';
import {
  handleMachinesList, handleMachineGet,
  handleMachineFactory, handleMachineUpdate, handleMachineDelete,
} from './handlers/machines';

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;

    // ── CORS preflight ──────────────────────────────────────────────────
    if (method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders() });
    }

    try {
      // ── Health ─────────────────────────────────────────────────────────
      if (path === '/health' && method === 'GET') {
        return handleHealth(env);
      }

      if (path === '/' && method === 'GET') {
        return new Response(JSON.stringify({
          worker: 'michronics-worker',
          message: 'Maths only. See /health for status.',
          endpoints: [
            '/physics/canon (GET, PUT)',
            '/physics/operational (GET, PUT)',
            '/physics/layer-0 (POST) — five-gate ingress before face firing',
            '/physics/engine2 (POST)',
            '/physics/d9 (POST)',
            '/physics/laminar/{1-4,5-8} (POST)',
            '/physics/triad/{1-4,5-8} (POST)',
            '/oracle (POST)',
            '/machines/list (GET)',
            '/machines/factory (POST)',
            '/machines/:id (GET, PUT, DELETE)',
          ],
        }, null, 2), {
          headers: { ...corsHeaders(), 'Content-Type': 'application/json' },
        });
      }

      // ── Canon ───────────────────────────────────────────────────────────
      if (path === '/physics/canon' && method === 'GET') return handleCanonGet(env);
      if (path === '/physics/canon' && method === 'PUT') return handleCanonPut(request, env);
      if (path === '/physics/operational' && method === 'GET') return handleOperationalGet(env);
      if (path === '/physics/operational' && method === 'PUT') return handleOperationalPut(request, env);

      // ── Pipeline ────────────────────────────────────────────────────────
      if (path === '/physics/layer-0' && method === 'POST') return handleLayer0(request, env);
      if (path === '/physics/engine2' && method === 'POST') return handleEngine2(request, env);
      if (path === '/physics/d9' && method === 'POST') return handleD9(request, env);
      if (path === '/physics/laminar/1-4' && method === 'POST') return handleLaminar14(request, env);
      if (path === '/physics/laminar/5-8' && method === 'POST') return handleLaminar58(request, env);
      if (path === '/physics/triad/1-4' && method === 'POST') return handleTriad14(request, env);
      if (path === '/physics/triad/5-8' && method === 'POST') return handleTriad58(request, env);

      // ── Oracle ──────────────────────────────────────────────────────────
      if (path === '/oracle' && method === 'POST') return handleOracle(request, env);

      // ── Machines ────────────────────────────────────────────────────────
      if (path === '/machines/list' && method === 'GET') return handleMachinesList(env);
      if (path === '/machines/factory' && method === 'POST') return handleMachineFactory(request, env);

      // /machines/:id
      const machineMatch = path.match(/^\/machines\/([a-zA-Z0-9_-]+)$/);
      if (machineMatch) {
        const id = machineMatch[1];
        if (method === 'GET') return handleMachineGet(env, id);
        if (method === 'PUT') return handleMachineUpdate(request, env, id);
        if (method === 'DELETE') return handleMachineDelete(request, env, id);
      }

      // ── 404 ─────────────────────────────────────────────────────────────
      return new Response(JSON.stringify({
        ok: false,
        error: 'not found',
        path,
        method,
        hint: 'GET / for endpoint list',
      }), {
        status: 404,
        headers: { ...corsHeaders(), 'Content-Type': 'application/json' },
      });
    } catch (err: any) {
      // Top-level error handler
      console.error('[michronics-worker] unhandled error:', err);
      return new Response(JSON.stringify({
        ok: false,
        error: 'internal error',
        message: err?.message || String(err),
      }), {
        status: 500,
        headers: { ...corsHeaders(), 'Content-Type': 'application/json' },
      });
    }
  },
};
