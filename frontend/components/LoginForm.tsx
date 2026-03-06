"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { setClientAuthToken } from "@/lib/auth";
import { getApiBaseCandidates } from "@/lib/api_base";

// Login için önce kök adres denensin (POST /auth/login); sonra /api/v1
const LOGIN_BASE_CANDIDATES = [
  "http://localhost:8000",
  "http://127.0.0.1:8000",
  ...getApiBaseCandidates(),
];

type LoginPayload = {
  access_token: string;
  token_type: string;
  expires_at: string;
};

export function LoginForm({ nextPath = "/" }: { nextPath?: string }) {
  const router = useRouter();
  const [email, setEmail] = useState("admin@otomat.local");
  const [password, setPassword] = useState("Otomat123!");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setBusy(true);
    setMessage(null);

    const errors: string[] = [];
    for (const base of LOGIN_BASE_CANDIDATES) {
      const url = `${base}/auth/login`;
      try {
        const response = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        if (!response.ok) {
          errors.push(`${url} -> ${response.status}`);
          continue;
        }

        const payload = (await response.json()) as LoginPayload;
        const expiresAt = Date.parse(payload.expires_at);
        const ttlSeconds = Number.isFinite(expiresAt)
          ? Math.max(60, Math.floor((expiresAt - Date.now()) / 1000))
          : 3600;
        setClientAuthToken(payload.access_token, ttlSeconds);
        router.push(nextPath || "/");
        router.refresh();
        return;
      } catch (error) {
        const detail = error instanceof Error ? error.message : "bağlantı hatası";
        errors.push(`${url} -> ${detail}`);
      }
    }

    const is404 = errors.some((e) => e.includes("404"));
    const hint = is404
      ? " Backend güncel olmayabilir veya login adresi yanlış. Backend'i yeniden başlatın (proje kökünde: PYTHONPATH=backend:. uvicorn app.main:app --app-dir backend --port 8000)."
      : "";
    setMessage(`Giriş başarısız.${hint} Denenen adresler: ${errors.join(" | ")}`);
    setBusy(false);
  };

  return (
    <form className="login-form" onSubmit={submit}>
      <h2>Oturum Aç</h2>
      <p>Kamu ihale radarı paneline giriş yapın. Tüm ihaleler ve skorlar tek ekranda.</p>
      <label>
        E-posta
        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          autoComplete="email"
          required
        />
      </label>
      <label>
        Şifre
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          required
          minLength={8}
        />
      </label>
      <button type="submit" disabled={busy}>
        {busy ? "Giriş yapılıyor..." : "Giriş Yap"}
      </button>
      <small>Varsayılan kullanıcı: admin@otomat.local / Otomat123!</small>
      {message ? <p className="login-error">{message}</p> : null}
    </form>
  );
}
