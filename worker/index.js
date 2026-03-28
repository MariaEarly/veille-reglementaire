/**
 * Early Brief — Log Proxy Worker
 *
 * Proxy sécurisé pour écrire dans le repo GitHub depuis le frontend.
 * Un seul endpoint, plusieurs fichiers : training-log, editorial-log, etc.
 *
 * POST /append
 * Headers: X-API-Key: <shared secret>
 * Body: { "log": "training-log|editorial-log", "entries": [...] }
 *
 * Le Worker :
 * 1. Valide l'API key et le payload
 * 2. Lit le fichier JSONL courant (mois en cours) via GitHub API
 * 3. Append les nouvelles entrées
 * 4. Commit via GitHub API
 */

const VALID_LOGS = ['training-log', 'editorial-log'];

export default {
  async fetch(request, env) {
    // CORS preflight
    if (request.method === 'OPTIONS') {
      return corsResponse(env, new Response(null, { status: 204 }));
    }

    // Only POST /append
    const url = new URL(request.url);
    if (request.method !== 'POST' || url.pathname !== '/append') {
      return corsResponse(env, new Response(JSON.stringify({ error: 'Not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      }));
    }

    try {
      const body = await request.json();
      const { log, entries } = body;

      // Auth: header X-API-Key or body._key (sendBeacon can't set headers)
      const apiKey = request.headers.get('X-API-Key') || body._key || '';
      if (!apiKey || apiKey !== env.API_KEY) {
        return corsResponse(env, new Response(JSON.stringify({ error: 'Unauthorized' }), {
          status: 401,
          headers: { 'Content-Type': 'application/json' },
        }));
      }

      // Validate log name
      if (!log || !VALID_LOGS.includes(log)) {
        return corsResponse(env, new Response(JSON.stringify({
          error: `Invalid log. Must be one of: ${VALID_LOGS.join(', ')}`,
        }), { status: 400, headers: { 'Content-Type': 'application/json' } }));
      }

      // Validate entries
      if (!Array.isArray(entries) || entries.length === 0) {
        return corsResponse(env, new Response(JSON.stringify({ error: 'entries must be a non-empty array' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        }));
      }

      // Max 100 entries per request (safety)
      if (entries.length > 100) {
        return corsResponse(env, new Response(JSON.stringify({ error: 'Max 100 entries per request' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        }));
      }

      // Build file path: logs/<log>/2026-03.jsonl
      const now = new Date();
      const monthStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
      const filePath = `logs/${log}/${monthStr}.jsonl`;

      // New lines to append
      const newLines = entries.map(e => JSON.stringify(e)).join('\n') + '\n';

      // Read current file from GitHub (may not exist yet)
      const { content: existingContent, sha } = await githubReadFile(env, filePath);

      // Append
      const updatedContent = existingContent + newLines;

      // Write back via GitHub API
      await githubWriteFile(env, filePath, updatedContent, sha,
        `log: append ${entries.length} entries to ${log} (${monthStr})`);

      return corsResponse(env, new Response(JSON.stringify({
        ok: true,
        appended: entries.length,
        file: filePath,
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }));

    } catch (err) {
      console.error('Worker error:', err);
      return corsResponse(env, new Response(JSON.stringify({ error: err.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }));
    }
  },
};

// --- GitHub API helpers ---

async function githubReadFile(env, path) {
  const url = `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${path}?ref=${env.GITHUB_BRANCH}`;
  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: 'application/vnd.github.v3+json',
      'User-Agent': 'earlybrief-log-worker',
    },
  });

  if (res.status === 404) {
    // File doesn't exist yet — that's fine
    return { content: '', sha: null };
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`GitHub read failed (${res.status}): ${text}`);
  }

  const data = await res.json();
  // GitHub returns base64-encoded content
  const content = atob(data.content.replace(/\n/g, ''));
  return { content, sha: data.sha };
}

async function githubWriteFile(env, path, content, sha, message) {
  const url = `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${path}`;
  const body = {
    message,
    content: btoa(unescape(encodeURIComponent(content))),
    branch: env.GITHUB_BRANCH,
  };
  if (sha) body.sha = sha; // Update existing file

  const res = await fetch(url, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: 'application/vnd.github.v3+json',
      'User-Agent': 'earlybrief-log-worker',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`GitHub write failed (${res.status}): ${text}`);
  }

  return res.json();
}

// --- CORS ---

function corsResponse(env, response) {
  const allowedOrigin = env.ALLOWED_ORIGINS || '*';
  const headers = new Headers(response.headers);
  headers.set('Access-Control-Allow-Origin', allowedOrigin);
  headers.set('Access-Control-Allow-Methods', 'POST, OPTIONS');
  headers.set('Access-Control-Allow-Headers', 'Content-Type, X-API-Key');
  headers.set('Access-Control-Max-Age', '86400');
  return new Response(response.body, {
    status: response.status,
    headers,
  });
}
