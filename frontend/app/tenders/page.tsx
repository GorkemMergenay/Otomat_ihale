import Link from "next/link";

import { ArchiveTenderButton } from "@/components/ArchiveTenderButton";
import { ScoreBadge } from "@/components/ScoreBadge";
import { StatusBadge } from "@/components/StatusBadge";
import { statusLabel } from "@/lib/labels";
import { getTenders } from "@/lib/api";
import { TenderListPagination } from "./TenderListPagination";

export const dynamic = "force-dynamic";

function queryFromSearchParams(searchParams: Record<string, string | string[] | undefined>) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(searchParams)) {
    if (!value) continue;
    if (Array.isArray(value)) {
      value.forEach((v) => params.append(key, v));
    } else {
      params.set(key, value);
    }
  }
  if (!params.has("active_only")) params.set("active_only", "true");
  if (!params.has("sort_by")) params.set("sort_by", "total_score");
  if (!params.has("sort_order")) params.set("sort_order", "desc");
  return `?${params.toString()}`;
}

export default async function TenderListPage({
  searchParams,
}: {
  searchParams: Record<string, string | string[] | undefined>;
}) {
  const statusOptions = [
    "new",
    "auto_flagged",
    "under_review",
    "relevant",
    "high_priority",
    "proposal_candidate",
    "ignored",
    "archived",
  ];
  const query = queryFromSearchParams(searchParams);
  const response = await getTenders(query);
  const currentPage = response.page;
  const pageSize = response.page_size;
  const totalPages = Math.max(1, Math.ceil(response.total / pageSize));

  return (
    <section>
      <header className="page-header">
        <h2>İhale Listesi</h2>
        <p>
          Varsayılan olarak sadece son tarihi geçmemiş ihaleler gösterilir. Tarihi geçenler otomatik arşivlenir.
        </p>
      </header>

      <form className="filter-row" method="get">
        <label className="filter-checkbox">
          <input
            type="hidden"
            name="active_only"
            value="false"
          />
          <input
            type="checkbox"
            name="active_only"
            value="true"
            defaultChecked={(searchParams.active_only as string) !== "false"}
          />
          Sadece geçerli ihaleler
        </label>
        <input name="search" placeholder="Ara (başlık/kurum)" defaultValue={(searchParams.search as string) || ""} />
        <input name="city" placeholder="Şehir" defaultValue={(searchParams.city as string) || ""} />
        <input
          name="institution_name"
          placeholder="Kurum"
          defaultValue={(searchParams.institution_name as string) || ""}
        />
        <input name="source_name" placeholder="Kaynak" defaultValue={(searchParams.source_name as string) || ""} />
        <input name="min_score" type="number" min="0" max="100" step="1" placeholder="Min skor" defaultValue={(searchParams.min_score as string) || ""} />
        <input name="publish_date_from" type="date" defaultValue={(searchParams.publish_date_from as string) || ""} />
        <input name="publish_date_to" type="date" defaultValue={(searchParams.publish_date_to as string) || ""} />
        <input name="deadline_from" type="date" defaultValue={(searchParams.deadline_from as string) || ""} />
        <input name="deadline_to" type="date" defaultValue={(searchParams.deadline_to as string) || ""} />
        <select name="status" defaultValue={(searchParams.status as string) || ""}>
          <option value="">Durum</option>
          {statusOptions.map((status) => (
            <option key={status} value={status}>
              {statusLabel(status)}
            </option>
          ))}
        </select>
        <select name="official_verified" defaultValue={(searchParams.official_verified as string) || ""}>
          <option value="">Resmi Doğrulama</option>
          <option value="true">Doğrulandı</option>
          <option value="false">Sinyal</option>
        </select>
        <select name="sort_by" defaultValue={(searchParams.sort_by as string) || "total_score"}>
          <option value="total_score">En alakalı (skor)</option>
          <option value="deadline_date">Son başvuru tarihi</option>
          <option value="publishing_date">Yayın tarihi</option>
        </select>
        <select name="sort_order" defaultValue={(searchParams.sort_order as string) || "desc"}>
          <option value="desc">Azalan (önce yüksek/geç)</option>
          <option value="asc">Artan (önce düşük/erken)</option>
        </select>
        <select name="page_size" defaultValue={(searchParams.page_size as string) || "25"}>
          <option value="10">10</option>
          <option value="25">25</option>
          <option value="50">50</option>
        </select>
        <input type="hidden" name="page" value="1" />
        <button type="submit">Listele</button>
      </form>

      {response.items.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">İhale bulunamadı</p>
          <p className="text-muted">Filtreleri gevşetin veya kaynak taraması çalıştırın.</p>
          <Link href="/tenders" className="quick-filter-chip">Filtreleri temizle</Link>
        </div>
      ) : (
        <>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Başlık</th>
                  <th>Kurum</th>
                  <th>Şehir</th>
                  <th>Skor</th>
                  <th>Durum</th>
                  <th>Kaynak</th>
                  <th>Son Tarih</th>
                  <th aria-label="İşlem" />
                </tr>
              </thead>
              <tbody>
                {response.items.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <Link href={`/tenders/${item.id}`} className="tender-list-title">{item.title}</Link>
                    </td>
                    <td>{item.institution_name || "-"}</td>
                    <td>{item.city || "-"}</td>
                    <td>
                      <ScoreBadge value={item.total_score} />
                    </td>
                    <td>
                      <StatusBadge value={item.status} />
                    </td>
                    <td>{item.source_name}</td>
                    <td>{item.deadline_date || "-"}</td>
                    <td>
                      <ArchiveTenderButton tenderId={item.id} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="table-footer-row">
            <p className="table-footer">
              Toplam: {response.total} | Sayfa: {response.page} / {totalPages} | Sayfa boyutu: {response.page_size}
            </p>
            <TenderListPagination
              currentPage={currentPage}
              totalPages={totalPages}
              total={response.total}
              pageSize={pageSize}
              searchParams={searchParams}
            />
          </div>
        </>
      )}
    </section>
  );
}
