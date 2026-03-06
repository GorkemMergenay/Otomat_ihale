import Link from "next/link";

export function StatCard({
  label,
  value,
  tone = "neutral",
  href,
}: {
  label: string;
  value: number;
  tone?: "neutral" | "good" | "warn" | "alert";
  href?: string;
}) {
  const content = (
    <>
      <p>{label}</p>
      <strong>{value}</strong>
      {href ? <span className="stat-link-hint">Detaya git</span> : null}
    </>
  );

  if (href) {
    return (
      <Link href={href} className={`stat-card stat-card-link tone-${tone}`}>
        {content}
      </Link>
    );
  }

  return <div className={`stat-card tone-${tone}`}>{content}</div>;
}
