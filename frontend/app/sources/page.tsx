import { SourceManager } from "@/components/SourceManager";
import { getSources } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function SourcesPage() {
  const sources = await getSources();

  return (
    <section>
      <header className="page-header">
        <h2>Kaynak Yönetimi</h2>
        <p>Kaynakların sağlık ve çalışma durumunu izleyin.</p>
      </header>

      <SourceManager initialSources={sources} />
    </section>
  );
}
