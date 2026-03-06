"use client";

import { useState } from "react";

import { getClientAuthToken } from "@/lib/auth";
import { getApiBase } from "@/lib/api_base";
import { sourceTypeLabel } from "@/lib/labels";
import type { SourceConfig } from "@/lib/types";

function sourceHealth(source: SourceConfig): "ok" | "warn" | "error" {
  const hasError = !!source.last_error;
  const lastSuccess = source.last_success_at ? new Date(source.last_success_at).getTime() : 0;
  const lastFailure = source.last_failure_at ? new Date(source.last_failure_at).getTime() : 0;
  const dayAgo = Date.now() - 24 * 60 * 60 * 1000;
  if (hasError && lastFailure >= dayAgo) return "error";
  if (source.last_failure_at && lastFailure >= dayAgo && lastFailure > lastSuccess) return "warn";
  if (source.last_run_at && !source.last_success_at && source.last_failure_at) return "warn";
  return "ok";
}

function HealthBadge({ source }: { source: SourceConfig }) {
  const h = sourceHealth(source);
  const label = h === "ok" ? "OK" : h === "warn" ? "Uyarı" : "Hata";
  return <span className={`health-badge health-badge-${h}`}>{label}</span>;
}

const API_BASE = getApiBase();

function authHeaders(extra: Record<string, string> = {}) {
  const token = getClientAuthToken() || process.env.NEXT_PUBLIC_API_TOKEN || "";
  const headers: Record<string, string> = { ...extra };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

export function SourceManager({ initialSources }: { initialSources: SourceConfig[] }) {
  const [sources, setSources] = useState(initialSources);
  const [message, setMessage] = useState<string | null>(null);

  const updateSource = async (source: SourceConfig, patch: Partial<SourceConfig>) => {
    const response = await fetch(`${API_BASE}/sources/${source.id}`, {
      method: "PATCH",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(patch),
    });
    if (!response.ok) throw new Error(`Güncelleme başarısız (${response.status})`);

    const updated = (await response.json()) as SourceConfig;
    setSources((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
  };

  const triggerCrawl = async (source: SourceConfig) => {
    const response = await fetch(`${API_BASE}/sources/${source.id}/trigger-crawl`, {
      method: "POST",
      headers: authHeaders(),
    });
    if (!response.ok) throw new Error(`Tetikleme başarısız (${response.status})`);
  };

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Sağlık</th>
            <th>Kaynak</th>
            <th>Tip</th>
            <th>Adapter</th>
            <th>Aktif</th>
            <th>Tarama Sıklığı</th>
            <th>Son Çalışma</th>
            <th>Son Başarı</th>
            <th>Son Başarısızlık</th>
            <th>Son Hata</th>
            <th>İşlem</th>
          </tr>
        </thead>
        <tbody>
          {sources.map((source) => (
            <tr key={source.id}>
              <td>
                <HealthBadge source={source} />
              </td>
              <td>
                <strong>{source.name}</strong>
                <div className="table-subline">{source.base_url}</div>
              </td>
              <td>{sourceTypeLabel(source.source_type)}</td>
              <td>
                {(source.config_json?.adapter as string) || "-"}
                {source.config_json?.template_source ? <div className="table-subline">Şablon</div> : null}
              </td>
              <td>
                <input
                  type="checkbox"
                  checked={source.is_active}
                  onChange={async () => {
                    try {
                      await updateSource(source, { is_active: !source.is_active });
                      setMessage("Kaynak güncellendi.");
                    } catch (error) {
                      setMessage(error instanceof Error ? error.message : "Güncelleme hatası");
                    }
                  }}
                />
              </td>
              <td>
                <input
                  className="inline-input"
                  defaultValue={source.crawl_frequency}
                  onBlur={async (event) => {
                    const next = event.target.value.trim();
                    if (!next || next === source.crawl_frequency) return;
                    try {
                      await updateSource(source, { crawl_frequency: next });
                      setMessage("Tarama sıklığı güncellendi.");
                    } catch (error) {
                      setMessage(error instanceof Error ? error.message : "Güncelleme hatası");
                    }
                  }}
                />
              </td>
              <td>{source.last_run_at ? new Date(source.last_run_at).toLocaleString("tr-TR") : "-"}</td>
              <td>{source.last_success_at ? new Date(source.last_success_at).toLocaleString("tr-TR") : "-"}</td>
              <td>{source.last_failure_at ? new Date(source.last_failure_at).toLocaleString("tr-TR") : "-"}</td>
              <td>{source.last_error || "-"}</td>
              <td>
                <button
                  onClick={async () => {
                    try {
                      await triggerCrawl(source);
                      setMessage(`${source.name} kaynağı için tarama tetiklendi.`);
                    } catch (error) {
                      setMessage(error instanceof Error ? error.message : "Tarama hatası");
                    }
                  }}
                >
                  Tara
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {message ? <p className="table-footer">{message}</p> : null}
    </div>
  );
}
