import { KeywordRuleManager } from "@/components/KeywordRuleManager";
import { getKeywordRules } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function KeywordsPage() {
  const rules = await getKeywordRules();

  return (
    <section>
      <header className="page-header">
        <h2>Anahtar Kelime Kural Yönetimi</h2>
        <p>Pozitif/negatif ağırlıklandırılmış eşleşme kuralları.</p>
      </header>

      <KeywordRuleManager initialRules={rules} />
    </section>
  );
}
