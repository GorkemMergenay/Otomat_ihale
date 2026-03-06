import Link from "next/link";

function buildQuery(
  searchParams: Record<string, string | string[] | undefined>,
  overrides: { page?: number; page_size?: number }
): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(searchParams)) {
    if (key === "page" && overrides.page != null) continue;
    if (key === "page_size" && overrides.page_size != null) continue;
    if (!value) continue;
    if (Array.isArray(value)) {
      value.forEach((v) => params.append(key, v));
    } else {
      params.set(key, value);
    }
  }
  if (overrides.page != null) params.set("page", String(overrides.page));
  if (overrides.page_size != null) params.set("page_size", String(overrides.page_size));
  const s = params.toString();
  return s ? `?${s}` : "";
}

export function TenderListPagination({
  currentPage,
  totalPages,
  total,
  pageSize,
  searchParams,
}: {
  currentPage: number;
  totalPages: number;
  total: number;
  pageSize: number;
  searchParams: Record<string, string | string[] | undefined>;
}) {
  if (totalPages <= 1 && total <= pageSize) return null;

  const prevQuery = currentPage > 1 ? buildQuery(searchParams, { page: currentPage - 1, page_size: pageSize }) : null;
  const nextQuery =
    currentPage < totalPages ? buildQuery(searchParams, { page: currentPage + 1, page_size: pageSize }) : null;

  return (
    <nav className="pagination" aria-label="Sayfa navigasyonu">
      {prevQuery ? (
        <Link href={prevQuery} className="pagination-btn">
          ← Önceki
        </Link>
      ) : (
        <span className="pagination-btn pagination-btn-disabled">← Önceki</span>
      )}
      <span className="pagination-info">
        {currentPage} / {totalPages}
      </span>
      {nextQuery ? (
        <Link href={nextQuery} className="pagination-btn">
          Sonraki →
        </Link>
      ) : (
        <span className="pagination-btn pagination-btn-disabled">Sonraki →</span>
      )}
    </nav>
  );
}
