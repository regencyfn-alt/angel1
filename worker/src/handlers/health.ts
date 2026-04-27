// Health — simple liveness check + KV reachability test

import { Env } from '../types/env';
import { jsonResponse } from './_shared';

export async function handleHealth(env: Env): Promise<Response> {
  const checks: Record<string, any> = {
    worker: 'michronics-worker',
    environment: env.ENVIRONMENT,
    timestamp: new Date().toISOString(),
  };

  // KV reachability
  try {
    const canon = await env.MICHRON_KV.get('physics:canon', 'text');
    checks.kv_reachable = true;
    checks.canon_length = canon ? canon.length : 0;
  } catch (err: any) {
    checks.kv_reachable = false;
    checks.kv_error = err.message;
  }

  // Operational reachability
  try {
    const op = await env.MICHRON_KV.get('physics:operational', 'text');
    checks.operational_length = op ? op.length : 0;
  } catch (err: any) {
    checks.operational_error = err.message;
  }

  // Secret presence (without exposing values)
  checks.secrets_configured = {
    anthropic: !!env.ANTHROPIC_API_KEY,
    nvidia: !!env.NVIDIA_API_KEY,
    physics: !!env.PHYSICS_KEY,
  };

  // Machine registry size
  try {
    const reg = await env.MICHRON_KV.get('machines:registry', 'json') as any[] || [];
    checks.custom_machines = reg.length;
  } catch (_) {}

  const ok = checks.kv_reachable
    && checks.secrets_configured.anthropic
    && checks.secrets_configured.nvidia
    && checks.secrets_configured.physics;

  return jsonResponse({ ok, ...checks }, ok ? 200 : 503);
}
