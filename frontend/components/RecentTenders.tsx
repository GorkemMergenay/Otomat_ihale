import Link from "next/link";
import { ScoreBadge } from "@/components/ScoreBadge";
import { StatusBadge } from "@/components/StatusBadge";
import type { Tender } from "@/lib/types";

export function RecentTenders({ items }: { items: Tender[] }) {
  if (items.length === 0) {
    return (
      <div className="panel panel-wide">
        <h3>Son Eklenen İhaleler</h3>
        <p className="text-muted">Henüz ihale yok. Kaynak taraması çalıştırıldığında burada görünecek.</p>
      </div>
    );
  }
  return (
    <div className="panel panel-wide">
      <h3>Son Eklenen İhaleler</h3>
      <ul className="recent-tenders-list">
        {items.map((t) => (
          <li key={t.id}>
            <Link href={`/tenders/${t.id}`} className="recent-tenders-link">
              <span className="recent-tenders-title">{t.title}</span>
              <span className="recent-tenders-meta">
                <ScoreBadge value={t.total_score} />
                <StatusBadge value={t.status} />
                {t.deadline_date && (
                  <span className="recent-tenders-date">Son: {t.deadline_date}</span>
                )}
              </span>
            </Link>
          </li>
        ))}
      </ul>
      <Link href="/tenders" className="recent-tenders-more">
        Tümünü gör →
      </Link>
    </div>
  );
}
