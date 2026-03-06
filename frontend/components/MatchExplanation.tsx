import type { Tender } from "@/lib/types";

interface Hit {
  keyword?: string;
  weight?: number;
  field?: string;
  match_score?: number;
  category?: string;
}

function isHit(x: unknown): x is Hit {
  return x !== null && typeof x === "object";
}

function isArray(x: unknown): x is unknown[] {
  return Array.isArray(x);
}

export function MatchExplanation({ match_explanation }: { match_explanation: Tender["match_explanation"] }) {
  if (!match_explanation || typeof match_explanation !== "object") {
    return <p className="text-muted">Eşleşme gerekçesi yok.</p>;
  }

  const positive = (match_explanation as Record<string, unknown>).positive_hits;
  const negative = (match_explanation as Record<string, unknown>).negative_hits;
  const components = (match_explanation as Record<string, unknown>).components;

  const positiveList = isArray(positive) ? positive.filter(isHit) : [];
  const negativeList = isArray(negative) ? negative.filter(isHit) : [];
  const compList = isArray(components) ? components : [];

  return (
    <div className="match-explanation">
      {positiveList.length > 0 && (
        <div className="match-explanation-block match-explanation-positive">
          <h4>Pozitif eşleşmeler</h4>
          <ul>
            {positiveList.map((hit, i) => (
              <li key={i}>
                <strong>{hit.keyword ?? "—"}</strong>
                {hit.field && <span className="match-field"> ({hit.field})</span>}
                {hit.weight != null && <span className="match-weight"> ağırlık: {hit.weight}</span>}
                {hit.match_score != null && <span className="match-score"> skor: {hit.match_score}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
      {negativeList.length > 0 && (
        <div className="match-explanation-block match-explanation-negative">
          <h4>Negatif eşleşmeler</h4>
          <ul>
            {negativeList.map((hit, i) => (
              <li key={i}>
                <strong>{hit.keyword ?? "—"}</strong>
                {hit.field && <span className="match-field"> ({hit.field})</span>}
                {hit.weight != null && <span className="match-weight"> ağırlık: {hit.weight}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
      {compList.length > 0 && (
        <div className="match-explanation-block match-explanation-components">
          <h4>Bileşenler</h4>
          <ul>
            {compList.map((c, i) => (
              <li key={i}>
                {typeof c === "object" && c !== null && "name" in c && "value" in c
                  ? `${String((c as { name: string }).name)}: ${String((c as { value: unknown }).value)}`
                  : JSON.stringify(c)}
              </li>
            ))}
          </ul>
        </div>
      )}
      {positiveList.length === 0 && negativeList.length === 0 && compList.length === 0 && (
        <pre className="match-explanation-raw">{JSON.stringify(match_explanation, null, 2)}</pre>
      )}
    </div>
  );
}
