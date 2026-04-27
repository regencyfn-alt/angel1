// Shared helpers — CORS, auth, JSON responses

export function corsHeaders(): Record<string, string> {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Physics-Key',
    'Access-Control-Max-Age': '86400',
  };
}

export function jsonResponse(body: any, status: number = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders(), 'Content-Type': 'application/json' },
  });
}

export function errorResponse(message: string, status: number = 400, extra: any = {}): Response {
  return jsonResponse({ ok: false, error: message, ...extra }, status);
}

/**
 * Auth gate for /physics/* endpoints.
 * Returns null if authorised, otherwise an error Response.
 *
 * The PHYSICS_KEY ships in pod.html as a literal — it's anti-noise rather than
 * anti-attacker. Worst case = NVIDIA credit drain. Roll regularly.
 */
export function physicsAuth(request: Request, expected: string): Response | null {
  const got = request.headers.get('x-physics-key') || request.headers.get('X-Physics-Key');
  if (!got || got !== expected) {
    return errorResponse('unauthorized — set X-Physics-Key header', 401);
  }
  return null;
}
