"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { getClientAuthToken } from "@/lib/auth";
import { getApiBase } from "@/lib/api_base";

const API_BASE = getApiBase();

function authHeaders() {
  const token = getClientAuthToken() || process.env.NEXT_PUBLIC_API_TOKEN || "";
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

export function ArchiveTenderButton({ tenderId }: { tenderId: number }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);

  const archive = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (busy) return;
    setBusy(true);
    try {
      const res = await fetch(`${API_BASE}/tenders/${tenderId}`, {
        method: "PATCH",
        headers: authHeaders(),
        body: JSON.stringify({ status: "archived" }),
      });
      if (!res.ok) throw new Error("Arşivlenemedi");
      router.refresh();
    } catch {
      setBusy(false);
    }
  };

  return (
    <button
      type="button"
      className="archive-tender-btn"
      onClick={archive}
      disabled={busy}
      title="Eski ihale olarak arşivle"
    >
      {busy ? "..." : "Arşivle"}
    </button>
  );
}
