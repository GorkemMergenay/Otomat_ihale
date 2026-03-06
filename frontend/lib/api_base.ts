const DEFAULT_BACKEND_ORIGIN = "http://localhost:8000";

function stripTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

function appendPath(origin: string, path: string): string {
  const left = stripTrailingSlash(origin);
  const right = path.startsWith("/") ? path : `/${path}`;
  return `${left}${right}`;
}

function pushUnique(list: string[], value: string): void {
  const normalized = stripTrailingSlash(value);
  if (!normalized) return;
  if (!list.includes(normalized)) {
    list.push(normalized);
  }
}

function buildCandidates(): string[] {
  const raw = (process.env.NEXT_PUBLIC_API_BASE_URL || "").trim();
  const internalRaw = (process.env.NEXT_INTERNAL_API_BASE_URL || "").trim();
  const list: string[] = [];

  if (internalRaw) {
    try {
      const parsed = new URL(internalRaw);
      pushUnique(list, stripTrailingSlash(parsed.toString()));
    } catch {
      // Ignore malformed internal URL and continue.
    }
  }

  if (raw) {
    try {
      const parsed = new URL(raw);
      const base = stripTrailingSlash(parsed.toString());
      const path = stripTrailingSlash(parsed.pathname || "/");

      pushUnique(list, base);
      if (path === "" || path === "/") {
        pushUnique(list, appendPath(parsed.origin, "/api/v1"));
      } else if (path === "/api") {
        pushUnique(list, appendPath(parsed.origin, "/api/v1"));
      } else if (path === "/api/v1") {
        pushUnique(list, appendPath(parsed.origin, "/api"));
      } else {
        pushUnique(list, appendPath(base, "/api/v1"));
        pushUnique(list, appendPath(parsed.origin, "/api/v1"));
      }
    } catch {
      // Relative or malformed value; fall back to explicit backend origin.
      pushUnique(list, appendPath(DEFAULT_BACKEND_ORIGIN, "/api/v1"));
    }
  }

  // Docker and local fallbacks.
  pushUnique(list, "http://backend:8000/api/v1");
  pushUnique(list, "http://backend:8000/api");
  pushUnique(list, appendPath(DEFAULT_BACKEND_ORIGIN, "/api/v1"));
  pushUnique(list, appendPath(DEFAULT_BACKEND_ORIGIN, "/api"));
  pushUnique(list, "http://127.0.0.1:8000/api/v1");
  pushUnique(list, "http://127.0.0.1:8000/api");
  pushUnique(list, "http://localhost:8001/api/v1");
  pushUnique(list, "http://127.0.0.1:8001/api/v1");
  return list;
}

const API_BASE_CANDIDATES = buildCandidates();

export function getApiBaseCandidates(): string[] {
  return API_BASE_CANDIDATES;
}

export function getApiBase(): string {
  return API_BASE_CANDIDATES[0];
}
