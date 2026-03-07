export type DashboardOverview = {
  total_tenders: number;
  newly_found_today: number;
  highly_relevant_count: number;
  approaching_deadlines: number;
  official_verified_count: number;
  active_sources: number;
  source_failures_last_24h: number;
};

export type Tender = {
  id: number;
  title: string;
  source_type: string;
  source_name: string;
  source_url: string;
  publishing_date: string | null;
  deadline_date: string | null;
  institution_name: string | null;
  city: string | null;
  total_score: number;
  relevance_score: number;
  commercial_score: number;
  technical_score: number;
  classification_label: string;
  official_verified: boolean;
  signal_found: boolean;
  status: string;
  summary: string | null;
  extracted_keywords: string[];
  match_explanation: Record<string, unknown>;
  notes: string | null;
  documents: Array<{
    id: number;
    document_type: string | null;
    document_url: string;
    local_path: string | null;
    checksum: string | null;
    created_at: string;
  }>;
};

export type TenderPage = {
  items: Tender[];
  total: number;
  page: number;
  page_size: number;
};

export type SourceConfig = {
  id: number;
  name: string;
  source_type: string;
  base_url: string;
  is_active: boolean;
  crawl_frequency: string;
  config_json: Record<string, unknown>;
  last_run_at: string | null;
  last_success_at: string | null;
  last_failure_at: string | null;
  last_error: string | null;
};

export type KeywordRule = {
  id: number;
  keyword: string;
  category: string;
  weight: number;
  is_active: boolean;
  is_negative: boolean;
  matching_type: string;
  target_field: string;
};

export type NotificationRecord = {
  id: number;
  tender_id: number | null;
  channel: string;
  recipient: string;
  notification_type: string;
  delivery_status: string;
  created_at: string;
  error_message: string | null;
};

export type NotificationSubscriber = {
  id: number;
  email: string;
  label: string | null;
  is_active: boolean;
  created_at: string;
};

export type TenderEvent = {
  id: number;
  event_type: string;
  event_data: Record<string, unknown>;
  created_at: string;
};
