import {
  DashboardOverview,
  KeywordRule,
  NotificationRecord,
  SourceConfig,
  Tender,
  TenderEvent,
  TenderPage,
} from "@/lib/types";
import { getApiBaseCandidates } from "@/lib/api_base";
import { getServerAuthToken } from "@/lib/server_auth";

const API_BASE_CANDIDATES = getApiBaseCandidates();

export class ApiRequestError extends Error {
  status: number | null;
  attempts: string[];

  constructor(message: string, status: number | null, attempts: string[]) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.attempts = attempts;
  }
}

async function apiGet<T>(path: string): Promise<T> {
  const errors: string[] = [];
  const token = getServerAuthToken() || process.env.NEXT_PUBLIC_API_TOKEN || "";
  const statuses: number[] = [];

  for (const base of API_BASE_CANDIDATES) {
    const url = `${base}${path}`;
    try {
      const response = await fetch(url, {
        cache: "no-store",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (response.ok) {
        return (await response.json()) as T;
      }

      statuses.push(response.status);
      errors.push(`${url} -> ${response.status} ${response.statusText}`);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Bilinmeyen bağlantı hatası";
      errors.push(`${url} -> ${message}`);
    }
  }

  const only404 = statuses.length > 0 && statuses.every((status) => status === 404);
  const status = only404 ? 404 : (statuses[0] ?? null);
  throw new ApiRequestError(`API isteği başarısız. Denenen adresler: ${errors.join(" | ")}`, status, errors);
}

export async function getOverview(): Promise<DashboardOverview> {
  return apiGet<DashboardOverview>("/dashboard/overview");
}

export async function getTenders(query = ""): Promise<TenderPage> {
  return apiGet<TenderPage>(`/tenders${query}`);
}

export async function getTender(id: number): Promise<Tender> {
  return apiGet<Tender>(`/tenders/${id}`);
}

export async function getTenderEvents(id: number): Promise<TenderEvent[]> {
  return apiGet<TenderEvent[]>(`/tenders/${id}/events`);
}

export async function getSources(): Promise<SourceConfig[]> {
  return apiGet<SourceConfig[]>("/sources");
}

export async function getKeywordRules(): Promise<KeywordRule[]> {
  return apiGet<KeywordRule[]>("/keyword-rules");
}

export async function getNotifications(): Promise<NotificationRecord[]> {
  return apiGet<NotificationRecord[]>("/notifications?page=1&page_size=100");
}
