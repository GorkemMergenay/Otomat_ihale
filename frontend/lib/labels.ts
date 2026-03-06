const STATUS_LABELS: Record<string, string> = {
  new: "Yeni",
  auto_flagged: "Otomatik İşaretlendi",
  under_review: "İncelemede",
  relevant: "Uygun",
  high_priority: "Yüksek Öncelik",
  proposal_candidate: "Teklif Adayı",
  ignored: "Göz Ardı",
  archived: "Arşiv",
};

const SOURCE_TYPE_LABELS: Record<string, string> = {
  official: "Resmi",
  public_announcement: "Kamu Duyurusu",
  news: "Haber",
  institution: "Kurum",
};

const CLASSIFICATION_LABELS: Record<string, string> = {
  highly_relevant: "Çok Uygun",
  relevant: "Uygun",
  maybe_relevant: "Sınırda Uygun",
  irrelevant: "İlgisiz",
};

const EVENT_TYPE_LABELS: Record<string, string> = {
  ingestion_created: "Kayıt Oluşturuldu",
  ingestion_updated: "Kayıt Güncellendi",
  rescored: "Skor Yeniden Hesaplandı",
  status_changed: "Durum Değişti",
  official_verified: "Resmi Doğrulama Yapıldı",
};

const NOTIFICATION_CHANNEL_LABELS: Record<string, string> = {
  email: "E-posta",
  telegram: "Telegram",
};

const NOTIFICATION_TYPE_LABELS: Record<string, string> = {
  new_highly_relevant: "Yeni Yüksek Potansiyel",
  official_verified: "Resmi Doğrulama",
  deadline_approaching: "Son Tarih Yaklaşıyor",
  score_threshold: "Skor Eşiği Aşıldı",
};

const DELIVERY_STATUS_LABELS: Record<string, string> = {
  pending: "Beklemede",
  sent: "Gönderildi",
  failed: "Başarısız",
  skipped: "Atlandı",
};

const KEYWORD_CATEGORY_LABELS: Record<string, string> = {
  direct: "Doğrudan",
  related: "İlişkili",
  commercial: "Ticari",
  institution_signal: "Kurum Sinyali",
  technical: "Teknik",
  negative: "Negatif",
};

const MATCHING_TYPE_LABELS: Record<string, string> = {
  contains: "İçerir",
  exact: "Tam Eşleşme",
  fuzzy: "Yakın Eşleşme",
};

const TARGET_FIELD_LABELS: Record<string, string> = {
  any: "Tüm Alanlar",
  title: "Başlık",
  summary: "Özet",
  raw_text: "Metin Gövdesi",
};

export function statusLabel(value: string): string {
  return STATUS_LABELS[value] || value;
}

export function sourceTypeLabel(value: string): string {
  return SOURCE_TYPE_LABELS[value] || value;
}

export function classificationLabel(value: string): string {
  return CLASSIFICATION_LABELS[value] || value;
}

export function eventTypeLabel(value: string): string {
  return EVENT_TYPE_LABELS[value] || value;
}

export function notificationChannelLabel(value: string): string {
  return NOTIFICATION_CHANNEL_LABELS[value] || value;
}

export function notificationTypeLabel(value: string): string {
  return NOTIFICATION_TYPE_LABELS[value] || value;
}

export function deliveryStatusLabel(value: string): string {
  return DELIVERY_STATUS_LABELS[value] || value;
}

export function keywordCategoryLabel(value: string): string {
  return KEYWORD_CATEGORY_LABELS[value] || value;
}

export function matchingTypeLabel(value: string): string {
  return MATCHING_TYPE_LABELS[value] || value;
}

export function targetFieldLabel(value: string): string {
  return TARGET_FIELD_LABELS[value] || value;
}

