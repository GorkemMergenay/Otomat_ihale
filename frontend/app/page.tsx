import { QuickFilters } from "@/components/QuickFilters";
import { RecentTenders } from "@/components/RecentTenders";
import { StatCard } from "@/components/StatCard";
import { getOverview, getTenders } from "@/lib/api";

export const dynamic = "force-dynamic";

function toDateInputValue(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export default async function DashboardPage() {
  const [overview, recentPage] = await Promise.all([
    getOverview(),
    getTenders("?sort_by=publishing_date&sort_order=desc&page_size=5"),
  ]);
  const today = new Date();
  const sevenDaysLater = new Date(today);
  sevenDaysLater.setDate(today.getDate() + 7);

  const todayStr = toDateInputValue(today);
  const deadlineTo = toDateInputValue(sevenDaysLater);

  return (
    <section>
      <header className="page-header">
        <h2>Genel Durum</h2>
        <p>Otomat ve self servis satış fırsatlarını operasyonel olarak takip edin.</p>
      </header>
      <QuickFilters />
      <div className="stat-grid">
        <StatCard label="Toplam İhale" value={overview.total_tenders} href="/tenders" />
        <StatCard
          label="Bugün Yeni"
          value={overview.newly_found_today}
          tone="good"
          href={`/tenders?publish_date_from=${todayStr}&publish_date_to=${todayStr}&sort_by=publishing_date&sort_order=desc`}
        />
        <StatCard
          label="Yüksek Potansiyel"
          value={overview.highly_relevant_count}
          tone="alert"
          href="/tenders?min_score=75&sort_by=total_score&sort_order=desc"
        />
        <StatCard
          label="Yaklaşan Son Tarih"
          value={overview.approaching_deadlines}
          tone="warn"
          href={`/tenders?deadline_to=${deadlineTo}&sort_by=deadline_date&sort_order=asc`}
        />
        <StatCard
          label="Resmi Doğrulanmış"
          value={overview.official_verified_count}
          tone="good"
          href="/tenders?official_verified=true"
        />
        <StatCard label="Aktif Kaynak" value={overview.active_sources} href="/sources" />
        <StatCard label="24s Kaynak Hatası" value={overview.source_failures_last_24h} tone="warn" href="/sources" />
      </div>
      <RecentTenders items={recentPage.items} />
    </section>
  );
}
