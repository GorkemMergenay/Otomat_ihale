import Link from "next/link";

import { ScoreBadge } from "@/components/ScoreBadge";
import { StatusBadge } from "@/components/StatusBadge";
import { statusLabel } from "@/lib/labels";
import { getTenders } from "@/lib/api";

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
  const asString = params.toString();
  return asString ? `?${asString}` : "";
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

  return (
    <section>
      <header className="page-header">
        <h2>İhale Listesi</h2>
        <p>Skor, kaynak ve durum bazlı hızlı tarama.</p>
      </header>

      <form className="filter-row" method="get">
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
        <select name="sort_by" defaultValue={(searchParams.sort_by as string) || "deadline_date"}>
          <option value="deadline_date">Son Tarih</option>
          <option value="total_score">Toplam Skor</option>
          <option value="publishing_date">Yayın Tarihi</option>
        </select>
        <button type="submit">Listele</button>
      </form>

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
            </tr>
          </thead>
          <tbody>
            {response.items.map((item) => (
              <tr key={item.id}>
                <td>
                  <Link href={`/tenders/${item.id}`}>{item.title}</Link>
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
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="table-footer">
        Toplam: {response.total} | Sayfa: {response.page} | Sayfa boyutu: {response.page_size}
      </p>
    </section>
  );
}
