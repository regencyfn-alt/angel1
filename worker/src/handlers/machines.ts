// Machine Factory & Registry
//
// New machine surfaces auto-connect to the canonical 4-endpoint dispatch chain
// (Laminar 1-4 → Laminar 5-8 → Triad 1-4 → Triad 5-8) without per-machine code.
//
// Default registry: Triad Lock + Laminar Lock (built-in, cannot be deleted).
// Custom machines: defined via factory, persisted to KV, rendered by engines.html.
//
// Engines.html reads /machines/list on load, draws one tab per machine.
// Each tab fires through /physics/laminar/* + /physics/triad/* by default.
//
// Endpoints:
//   GET  /machines/list         — all live machines
//   GET  /machines/:id          — single machine config
//   POST /machines/factory      — create new machine
//   PUT  /machines/:id          — update machine config
//   DELETE /machines/:id        — delete (Triad/Laminar protected)
//   POST /machines/:id/fire     — convenience wrapper that runs the full 4-call chain

import { Env } from '../types/env';
import { jsonResponse, errorResponse, physicsAuth } from './_shared';

interface MachineConfig {
  id: string;
  name: string;
  type: 'triad' | 'laminar' | 'custom';
  core?: string;                 // substrate name (e.g. "Citrine")
  description?: string;
  dispatch: 'laminar+triad' | 'engine2' | 'laminar' | 'triad';
  faces?: Array<{                // optional override; otherwise uses default chain prompts
    id: string;
    name: string;
    op: string;
    temp: number;
  }>;
  substrates?: Array<{
    regime: 'C1' | 'C2' | 'C3';
    name: string;
    props: Record<string, any>;
  }>;
  protected?: boolean;            // true for Triad + Laminar built-ins
  createdAt?: string;
  updatedAt?: string;
}

// ── Built-in machines — always present, cannot be deleted ──────────────
const BUILT_IN_MACHINES: MachineConfig[] = [
  {
    id: 'triad',
    name: 'Triad Lock',
    type: 'triad',
    core: 'abstract',
    description: 'Graph primitives → bipartiteness → minimal templates → recurrence → probabilistic update → perturbation → gradient → conservation. Eight faces over the abstract graph layer.',
    dispatch: 'laminar+triad',
    protected: true,
  },
  {
    id: 'laminar',
    name: 'Laminar Lock',
    type: 'laminar',
    core: 'Tantalum',
    description: 'Calcite gate → fractionation → alignment → graph derivation → polarity → perturbation dynamics → lock verify → RAG record. Eight faces with Tantalum substrate.',
    dispatch: 'laminar',
    protected: true,
  },
];

// ── GET /machines/list ─────────────────────────────────────────────────
export async function handleMachinesList(env: Env): Promise<Response> {
  const customRaw = await env.MICHRON_KV.get('machines:registry', 'json') as MachineConfig[] || [];
  const all = [...BUILT_IN_MACHINES, ...customRaw];
  return jsonResponse({ ok: true, machines: all, count: all.length });
}

// ── GET /machines/:id ──────────────────────────────────────────────────
export async function handleMachineGet(env: Env, id: string): Promise<Response> {
  // Check built-ins first
  const builtIn = BUILT_IN_MACHINES.find(m => m.id === id);
  if (builtIn) return jsonResponse({ ok: true, machine: builtIn });

  // Custom machines
  const config = await env.MICHRON_KV.get(`machines:${id}:config`, 'json') as MachineConfig | null;
  if (!config) return errorResponse(`machine not found: ${id}`, 404);

  return jsonResponse({ ok: true, machine: config });
}

// ── POST /machines/factory — create new machine ────────────────────────
export async function handleMachineFactory(request: Request, env: Env): Promise<Response> {
  const auth = physicsAuth(request, env.PHYSICS_KEY);
  if (auth) return auth;

  const body = await request.json() as Partial<MachineConfig>;

  if (!body.name || !body.type) {
    return errorResponse('name and type required', 400);
  }

  // Validate type
  if (!['triad', 'laminar', 'custom'].includes(body.type)) {
    return errorResponse('type must be one of: triad, laminar, custom', 400);
  }

  // Generate ID from name (lowercase, alphanumeric + underscores, prefixed with timestamp for uniqueness)
  const slug = body.name.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
  const id = `${slug}_${Date.now()}`;

  // Don't allow shadowing built-ins
  if (BUILT_IN_MACHINES.some(m => m.id === id || m.id === slug)) {
    return errorResponse(`machine id collides with built-in: ${slug}`, 409);
  }

  const config: MachineConfig = {
    id,
    name: body.name,
    type: body.type,
    core: body.core || '',
    description: body.description || '',
    dispatch: body.dispatch || 'laminar+triad',
    faces: body.faces,
    substrates: body.substrates,
    protected: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  // Write config
  await env.MICHRON_KV.put(`machines:${id}:config`, JSON.stringify(config));

  // Update registry index
  const registry = await env.MICHRON_KV.get('machines:registry', 'json') as MachineConfig[] || [];
  registry.push(config);
  await env.MICHRON_KV.put('machines:registry', JSON.stringify(registry));

  return jsonResponse({
    ok: true,
    machine: config,
    kv_keys_created: [`machines:${id}:config`, 'machines:registry (updated)'],
    endpoints_wired: dispatchEndpoints(config.dispatch),
    ui_tab_added: 'engines.html will render this tab on next load',
  }, 201);
}

// ── PUT /machines/:id — update existing ────────────────────────────────
export async function handleMachineUpdate(request: Request, env: Env, id: string): Promise<Response> {
  const auth = physicsAuth(request, env.PHYSICS_KEY);
  if (auth) return auth;

  // Built-ins are protected from rename/dispatch change but can have faces/substrates customised
  const builtIn = BUILT_IN_MACHINES.find(m => m.id === id);

  const body = await request.json() as Partial<MachineConfig>;

  if (builtIn) {
    // Allow only faces + substrates overrides on built-ins
    const overlay: MachineConfig = {
      ...builtIn,
      faces: body.faces || builtIn.faces,
      substrates: body.substrates || builtIn.substrates,
      updatedAt: new Date().toISOString(),
    };
    await env.MICHRON_KV.put(`machines:${id}:config`, JSON.stringify(overlay));
    return jsonResponse({ ok: true, machine: overlay, note: 'built-in machine: only faces and substrates overridden' });
  }

  // Custom machine update
  const existing = await env.MICHRON_KV.get(`machines:${id}:config`, 'json') as MachineConfig | null;
  if (!existing) return errorResponse(`machine not found: ${id}`, 404);

  const updated: MachineConfig = {
    ...existing,
    ...body,
    id: existing.id,                  // never let id be rewritten
    protected: false,
    createdAt: existing.createdAt,
    updatedAt: new Date().toISOString(),
  };

  await env.MICHRON_KV.put(`machines:${id}:config`, JSON.stringify(updated));

  // Update registry entry
  const registry = await env.MICHRON_KV.get('machines:registry', 'json') as MachineConfig[] || [];
  const idx = registry.findIndex(m => m.id === id);
  if (idx >= 0) {
    registry[idx] = updated;
    await env.MICHRON_KV.put('machines:registry', JSON.stringify(registry));
  }

  return jsonResponse({ ok: true, machine: updated });
}

// ── DELETE /machines/:id ───────────────────────────────────────────────
export async function handleMachineDelete(request: Request, env: Env, id: string): Promise<Response> {
  const auth = physicsAuth(request, env.PHYSICS_KEY);
  if (auth) return auth;

  if (BUILT_IN_MACHINES.some(m => m.id === id)) {
    return errorResponse(`built-in machine cannot be deleted: ${id}`, 403);
  }

  const config = await env.MICHRON_KV.get(`machines:${id}:config`, 'json') as MachineConfig | null;
  if (!config) return errorResponse(`machine not found: ${id}`, 404);

  await env.MICHRON_KV.delete(`machines:${id}:config`);

  // Remove from registry
  const registry = await env.MICHRON_KV.get('machines:registry', 'json') as MachineConfig[] || [];
  const filtered = registry.filter(m => m.id !== id);
  await env.MICHRON_KV.put('machines:registry', JSON.stringify(filtered));

  return jsonResponse({ ok: true, deleted: id });
}

// ── Helper — translate dispatch into endpoint description ──────────────
function dispatchEndpoints(dispatch: string): string[] {
  switch (dispatch) {
    case 'laminar+triad':
      return [
        'POST /physics/laminar/1-4',
        'POST /physics/laminar/5-8 (uses /1-4 output as priorContext)',
        'POST /physics/triad/1-4 (uses /5-8 output as priorContext)',
        'POST /physics/triad/5-8 (uses /1-4 output as priorContext) → final RAG record',
      ];
    case 'laminar':
      return ['POST /physics/laminar/1-4', 'POST /physics/laminar/5-8'];
    case 'triad':
      return ['POST /physics/triad/1-4', 'POST /physics/triad/5-8'];
    case 'engine2':
      return ['POST /physics/engine2 (per-face dispatch, legacy)'];
    default:
      return [];
  }
}
