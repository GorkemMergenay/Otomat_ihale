import { statusLabel } from "@/lib/labels";

const colorMap: Record<string, string> = {
  new: "badge-gray",
  auto_flagged: "badge-blue",
  under_review: "badge-amber",
  relevant: "badge-teal",
  high_priority: "badge-red",
  proposal_candidate: "badge-indigo",
  ignored: "badge-gray",
  archived: "badge-gray",
};

export function StatusBadge({ value }: { value: string }) {
  return <span className={`badge ${colorMap[value] || "badge-gray"}`}>{statusLabel(value)}</span>;
}
