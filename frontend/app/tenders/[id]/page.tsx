import { notFound } from "next/navigation";

import { ScoreBadge } from "@/components/ScoreBadge";
import { StatusBadge } from "@/components/StatusBadge";
import { TenderActions } from "@/components/TenderActions";
import { ApiRequestError, getTender, getTenderEvents } from "@/lib/api";
import { classificationLabel, eventTypeLabel } from "@/lib/labels";

export const dynamic = "force-dynamic";

export default async function TenderDetailPage({ params }: { params: { id: string } }) {
  const tenderId = Number(params.id);
  if (!Number.isFinite(tenderId) || tenderId <= 0) {
    notFound();
  }

  let tenderData: Awaited<ReturnType<typeof getTender>> | null = null;
  let eventsData: Awaited<ReturnType<typeof getTenderEvents>> = [];
  try {
    [tenderData, eventsData] = await Promise.all([getTender(tenderId), getTenderEvents(tenderId)]);
  } catch (error) {
    if (error instanceof ApiRequestError && error.status === 404) {
      notFound();
    }
    throw error;
  }
  if (!tenderData) {
    notFound();
  }

  const tender = tenderData;
  const events = eventsData;

  return (
    <section>
      <header className="page-header">
        <h2>İhale Detayı</h2>
        <p>{tender.title}</p>
      </header>

      <div className="detail-grid">
        <div className="panel">
          <h3>Temel Bilgiler</h3>
          <dl>
            <dt>Kurum</dt>
            <dd>{tender.institution_name || "-"}</dd>
            <dt>Şehir</dt>
            <dd>{tender.city || "-"}</dd>
            <dt>Durum</dt>
            <dd>
              <StatusBadge value={tender.status} />
            </dd>
            <dt>Resmi Doğrulama</dt>
            <dd>{tender.official_verified ? "Evet" : "Hayır"}</dd>
            <dt>Kaynak</dt>
            <dd>
              <a href={tender.source_url} target="_blank" rel="noreferrer">
                {tender.source_name}
              </a>
            </dd>
            <dt>Son Tarih</dt>
            <dd>{tender.deadline_date || "-"}</dd>
          </dl>
        </div>

        <div className="panel">
          <h3>Skor Dağılımı</h3>
          <div className="score-row">
            <span>Uygunluk</span>
            <ScoreBadge value={tender.relevance_score} />
          </div>
          <div className="score-row">
            <span>Ticari</span>
            <ScoreBadge value={tender.commercial_score} />
          </div>
          <div className="score-row">
            <span>Teknik</span>
            <ScoreBadge value={tender.technical_score} />
          </div>
          <div className="score-row total-row">
            <span>Toplam</span>
            <ScoreBadge value={tender.total_score} />
          </div>
          <p className="label-pill">{classificationLabel(tender.classification_label)}</p>
        </div>

        <div className="panel">
          <TenderActions tenderId={tender.id} currentStatus={tender.status} currentNotes={tender.notes} />
        </div>

        <div className="panel panel-wide">
          <h3>Çıkarılan Anahtar Kelimeler</h3>
          <div className="chip-wrap">
            {tender.extracted_keywords.length === 0 ? (
              <span className="chip">Anahtar kelime bulunamadı</span>
            ) : (
              tender.extracted_keywords.map((k) => <span className="chip" key={k}>{k}</span>)
            )}
          </div>
          <h3>Eşleşme Gerekçesi</h3>
          <pre>{JSON.stringify(tender.match_explanation, null, 2)}</pre>
        </div>

        <div className="panel panel-wide">
          <h3>Dokümanlar</h3>
          {tender.documents.length === 0 ? (
            <p>Doküman bulunamadı.</p>
          ) : (
            <ul className="timeline">
              {tender.documents.map((doc) => (
                <li key={doc.id}>
                  <strong>{doc.document_type || "doküman"}</strong>
                  <a href={doc.document_url} target="_blank" rel="noreferrer">
                    {doc.document_url}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="panel panel-wide">
          <h3>Olay Geçmişi</h3>
          <ul className="timeline">
            {events.map((event) => (
              <li key={event.id}>
                <strong>{eventTypeLabel(event.event_type)}</strong>
                <span>{new Date(event.created_at).toLocaleString("tr-TR")}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
