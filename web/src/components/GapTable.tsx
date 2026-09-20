import { formatBRL, formatPct } from "@/lib/format";
import type { PartidoRepasse } from "@/lib/types";

export function GapTable({ rows }: { rows: PartidoRepasse[] }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-[var(--line)] bg-[var(--surface)]">
      <table className="w-full min-w-[720px] text-left text-sm">
        <thead className="border-b border-[var(--line)] bg-[var(--wash)] text-[var(--muted)]">
          <tr>
            <th className="px-3 py-2 font-medium">Partido</th>
            <th className="px-3 py-2 text-right font-medium">Cota</th>
            <th className="px-3 py-2 text-right font-medium">Declarado</th>
            <th className="px-3 py-2 text-right font-medium">Gap</th>
            <th className="px-3 py-2 text-right font-medium">% repassado</th>
            <th className="px-3 py-2 text-right font-medium">Cands.</th>
            <th className="px-3 py-2 text-right font-medium">Média/cand.</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((p) => {
            const gapPositive = p.gap >= 0;
            return (
              <tr
                key={p.sigla}
                className="border-b border-[var(--line)]/70 hover:bg-[var(--wash)]/60"
              >
                <td className="px-3 py-2 font-medium text-[var(--ink)]">
                  {p.sigla}
                </td>
                <td className="px-3 py-2 text-right tabular-nums">
                  {formatBRL(p.cota)}
                </td>
                <td className="px-3 py-2 text-right tabular-nums">
                  {formatBRL(p.declarado_candidatos)}
                </td>
                <td
                  className={`px-3 py-2 text-right tabular-nums ${
                    gapPositive ? "text-[var(--muted)]" : "text-[var(--accent)]"
                  }`}
                >
                  {gapPositive ? "" : "+"}
                  {formatBRL(Math.abs(p.gap))}
                  {gapPositive ? " a declarar" : " acima"}
                </td>
                <td className="px-3 py-2 text-right tabular-nums">
                  {formatPct(p.pct_repassado)}
                </td>
                <td className="px-3 py-2 text-right tabular-nums">
                  {(p.n_candidatos ?? 0).toLocaleString("pt-BR")}
                </td>
                <td className="px-3 py-2 text-right tabular-nums">
                  {p.media_por_candidato
                    ? formatBRL(p.media_por_candidato)
                    : "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
