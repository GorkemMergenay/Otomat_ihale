"use client";

import { FormEvent, useState } from "react";

import { getClientAuthToken } from "@/lib/auth";
import { getApiBase } from "@/lib/api_base";
import { statusLabel } from "@/lib/labels";

const STATUSES = [
  "new",
  "auto_flagged",
  "under_review",
  "relevant",
  "high_priority",
  "proposal_candidate",
  "ignored",
  "archived",
];

const API_BASE = getApiBase();

function authHeaders(extra: Record<string, string> = {}) {
  const token = getClientAuthToken() || process.env.NEXT_PUBLIC_API_TOKEN || "";
  const headers: Record<string, string> = { ...extra };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

export function TenderActions({
  tenderId,
  currentStatus,
  currentNotes,
}: {
  tenderId: number;
  currentStatus: string;
  currentNotes: string | null;
}) {
  const [status, setStatus] = useState(currentStatus);
  const [notes, setNotes] = useState(currentNotes || "");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setBusy(true);
    setMessage(null);

    try {
      const response = await fetch(`${API_BASE}/tenders/${tenderId}`, {
        method: "PATCH",
        headers: authHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({ status, notes }),
      });

      if (!response.ok) {
        throw new Error(`Güncelleme başarısız (${response.status})`);
      }

      setMessage("İhale güncellendi. Sayfayı yenileyin.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Güncelleme hatası");
    } finally {
      setBusy(false);
    }
  };

  return (
    <form onSubmit={submit} className="action-form">
      <h3>Durum Güncelle</h3>
      <select value={status} onChange={(e) => setStatus(e.target.value)}>
        {STATUSES.map((item) => (
          <option key={item} value={item}>
            {statusLabel(item)}
          </option>
        ))}
      </select>
      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        rows={3}
        placeholder="Notlar"
      />
      <button type="submit" disabled={busy}>
        {busy ? "Kaydediliyor..." : "Kaydet"}
      </button>
      {message ? <p>{message}</p> : null}
    </form>
  );
}
