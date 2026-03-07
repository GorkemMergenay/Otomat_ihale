"use client";

import { FormEvent, useState } from "react";

import { getClientAuthToken } from "@/lib/auth";
import { getApiBaseCandidates } from "@/lib/api_base";
import type { NotificationSubscriber } from "@/lib/types";

function authHeaders(extra: Record<string, string> = {}) {
  const token = getClientAuthToken() || process.env.NEXT_PUBLIC_API_TOKEN || "";
  const headers: Record<string, string> = { ...extra };
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

export function EmailSubscriberManager({
  initialSubscribers,
}: {
  initialSubscribers: NotificationSubscriber[];
}) {
  const [subscribers, setSubscribers] = useState(initialSubscribers);
  const [email, setEmail] = useState("");
  const [label, setLabel] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const bases = getApiBaseCandidates();

  const addSubscriber = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setBusy(true);
    setMessage(null);
    const body = JSON.stringify({
      email: email.trim().toLowerCase(),
      label: label.trim() || null,
    });
    for (const base of bases) {
      try {
        const response = await fetch(`${base}/notification-subscribers`, {
          method: "POST",
          headers: authHeaders({ "Content-Type": "application/json" }),
          body,
        });
        if (response.ok) {
          const created = (await response.json()) as NotificationSubscriber;
          setSubscribers((prev) => [created, ...prev]);
          setEmail("");
          setLabel("");
          setMessage("E-posta adresi eklendi. Eşleşme bildirimleri bu adrese gidecek.");
          setBusy(false);
          return;
        }
        if (response.status === 409) {
          setMessage("Bu e-posta adresi zaten kayıtlı.");
          setBusy(false);
          return;
        }
      } catch {
        continue;
      }
    }
    setMessage("İstek gönderilemedi. Giriş yaptığınızdan ve backend'in çalıştığından emin olun.");
    setBusy(false);
  };

  const deleteSubscriber = async (id: number) => {
    setBusy(true);
    setMessage(null);
    for (const base of bases) {
      try {
        const response = await fetch(`${base}/notification-subscribers/${id}`, {
          method: "DELETE",
          headers: authHeaders(),
        });
        if (response.ok) {
          setSubscribers((prev) => prev.filter((s) => s.id !== id));
          setBusy(false);
          return;
        }
      } catch {
        continue;
      }
    }
    setMessage("Silme işlemi gönderilemedi.");
    setBusy(false);
  };

  return (
    <div className="panel" style={{ marginBottom: "1.5rem" }}>
      <h3>Eşleşme bildirimi alacak e-posta adresleri</h3>
      <p className="text-muted" style={{ marginBottom: "1rem" }}>
        Bu adreslere yüksek potansiyelli ihale eşleşmelerinde otomatik e-posta gider. SMTP ayarlarını
        backend .env dosyasında yapın (EMAIL_ENABLED, SMTP_HOST, SMTP_PORT, vb.).
      </p>

      <form onSubmit={addSubscriber} className="action-form" style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", alignItems: "flex-end", marginBottom: "1rem" }}>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          <span style={{ fontSize: "0.875rem", fontWeight: 500 }}>E-posta</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="ornek@firma.com"
            required
            style={{ width: "220px", height: "40px", padding: "0 0.75rem", borderRadius: "8px", border: "1px solid var(--border-default)" }}
          />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          <span style={{ fontSize: "0.875rem", fontWeight: 500 }}>Etiket (isteğe bağlı)</span>
          <input
            type="text"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            placeholder="Örn: Satış ekibi"
            maxLength={100}
            style={{ width: "160px", height: "40px", padding: "0 0.75rem", borderRadius: "8px", border: "1px solid var(--border-default)" }}
          />
        </label>
        <button type="submit" disabled={busy} style={{ height: "40px", padding: "0 1rem" }}>
          {busy ? "Ekleniyor..." : "Ekle"}
        </button>
      </form>

      {message && <p style={{ margin: "0 0 0.75rem", fontSize: "0.875rem", color: "var(--text-secondary)" }}>{message}</p>}

      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {subscribers.map((s) => (
          <li
            key={s.id}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "0.5rem 0",
              borderBottom: "1px solid var(--border-default)",
            }}
          >
            <span>
              <strong>{s.email}</strong>
              {s.label && <span style={{ marginLeft: "0.5rem", color: "var(--text-tertiary)", fontSize: "0.875rem" }}>({s.label})</span>}
            </span>
            <button
              type="button"
              onClick={() => deleteSubscriber(s.id)}
              disabled={busy}
              className="danger-btn"
              style={{ padding: "0.25rem 0.5rem", fontSize: "0.8125rem", borderRadius: "6px", border: "none", cursor: "pointer" }}
            >
              Kaldır
            </button>
          </li>
        ))}
      </ul>
      {subscribers.length === 0 && (
        <p className="text-muted" style={{ margin: "0.5rem 0 0" }}>
          Henüz e-posta adresi eklenmedi. Yukarıdan ekleyin.
        </p>
      )}
    </div>
  );
}
