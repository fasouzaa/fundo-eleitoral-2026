import { formatCompactBRL } from "@/lib/format";

type Item = { label: string; value: number };

export function BarList({
  items,
  maxItems = 12,
}: {
  items: Item[];
  maxItems?: number;
}) {
  const slice = items.slice(0, maxItems);
  const max = Math.max(...slice.map((i) => i.value), 1);

  return (
    <ul className="space-y-2.5">
      {slice.map((item) => (
        <li key={item.label}>
          <div className="mb-1 flex items-baseline justify-between gap-3 text-sm">
            <span className="font-medium text-[var(--ink)]">{item.label}</span>
            <span className="shrink-0 tabular-nums text-[var(--muted)]">
              {formatCompactBRL(item.value)}
            </span>
          </div>
          <div className="h-2 overflow-hidden rounded-sm bg-[var(--wash)]">
            <div
              className="h-full rounded-sm bg-[var(--accent)] transition-[width] duration-500"
              style={{ width: `${(item.value / max) * 100}%` }}
            />
          </div>
        </li>
      ))}
    </ul>
  );
}
