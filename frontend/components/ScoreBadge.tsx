export function ScoreBadge({ value }: { value: number }) {
  let tone = "score-low";
  if (value >= 75) tone = "score-high";
  else if (value >= 55) tone = "score-mid";
  else if (value >= 35) tone = "score-watch";

  const formatted = value.toLocaleString("tr-TR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
  return <span className={`score ${tone}`}>{formatted}</span>;
}
