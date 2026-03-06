function Bar({ label, value, max = 100 }: { label: string; value: number; max?: number }) {
  const pct = Math.min(max, Math.max(0, Number(value)));
  const tone =
    pct >= 75 ? "score-high" : pct >= 55 ? "score-mid" : pct >= 35 ? "score-watch" : "score-low";
  return (
    <div className="score-bar-row">
      <span className="score-bar-label">{label}</span>
      <div className="score-bar-track">
        <div className={`score-bar-fill ${tone}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="score-bar-value">{value}</span>
    </div>
  );
}

export function ScoreBars({
  relevance_score,
  commercial_score,
  technical_score,
  total_score,
}: {
  relevance_score: number;
  commercial_score: number;
  technical_score: number;
  total_score: number;
}) {
  return (
    <div className="score-bars">
      <Bar label="Uygunluk" value={relevance_score} />
      <Bar label="Ticari" value={commercial_score} />
      <Bar label="Teknik" value={technical_score} />
      <Bar label="Toplam" value={total_score} />
    </div>
  );
}
