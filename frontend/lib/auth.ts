export const AUTH_COOKIE_NAME = "otomat_auth_token";

export function getClientAuthToken(): string | null {
  if (typeof document === "undefined") return null;

  const pairs = document.cookie.split(";").map((part) => part.trim());
  for (const pair of pairs) {
    if (!pair.startsWith(`${AUTH_COOKIE_NAME}=`)) continue;
    return decodeURIComponent(pair.slice(AUTH_COOKIE_NAME.length + 1));
  }
  return null;
}

export function setClientAuthToken(token: string, ttlSeconds: number): void {
  if (typeof document === "undefined") return;
  const safeTtl = Number.isFinite(ttlSeconds) && ttlSeconds > 0 ? Math.floor(ttlSeconds) : 3600;
  document.cookie = `${AUTH_COOKIE_NAME}=${encodeURIComponent(token)}; Path=/; Max-Age=${safeTtl}; SameSite=Lax`;
}

export function clearClientAuthToken(): void {
  if (typeof document === "undefined") return;
  document.cookie = `${AUTH_COOKIE_NAME}=; Path=/; Max-Age=0; SameSite=Lax`;
}
