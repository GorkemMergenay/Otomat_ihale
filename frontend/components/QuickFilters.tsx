import Link from "next/link";

const filters = [
  { href: "/tenders?min_score=75&sort_by=total_score&sort_order=desc", label: "Yüksek skor (75+)" },
  { href: "/tenders?official_verified=true", label: "Resmi doğrulanmış" },
  { href: "/tenders?status=new", label: "Yeni" },
  { href: "/tenders?status=high_priority", label: "Yüksek öncelik" },
];

function todayParam(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export function QuickFilters() {
  const today = todayParam();
  const inAWeek = new Date();
  inAWeek.setDate(inAWeek.getDate() + 7);
  const toStr = (d: Date) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

  return (
    <div className="quick-filters">
      <span className="quick-filters-label">Hızlı filtre:</span>
      {filters.map((f) => (
        <Link key={f.href} href={f.href} className="quick-filter-chip">
          {f.label}
        </Link>
      ))}
      <Link
        href={`/tenders?publish_date_from=${today}&publish_date_to=${today}&sort_by=publishing_date&sort_order=desc`}
        className="quick-filter-chip"
      >
        Bugün eklenenler
      </Link>
      <Link
        href={`/tenders?deadline_to=${toStr(inAWeek)}&sort_by=deadline_date&sort_order=asc`}
        className="quick-filter-chip"
      >
        Yaklaşan son tarih
      </Link>
    </div>
  );
}
