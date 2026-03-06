import Link from "next/link";

export default function TenderNotFoundPage() {
  return (
    <section>
      <header className="page-header">
        <h2>İhale Bulunamadı</h2>
        <p>
          Bu kayıt taşınmış, silinmiş veya daha önceki bir veri temizliği nedeniyle artık mevcut değil.
        </p>
      </header>
      <div className="panel">
        <p>Güncel kayıtlar için ihale listesine dönebilirsiniz.</p>
        <p>
          <Link href="/tenders">İhale listesine git</Link>
        </p>
      </div>
    </section>
  );
}

