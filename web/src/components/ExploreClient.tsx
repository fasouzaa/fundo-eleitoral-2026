"use client";

import { useMemo, useState, useTransition } from "react";
import type { CandidatoFefc } from "@/lib/types";
import { formatBRL, formatCompactBRL } from "@/lib/format";

type Props = {
  candidatos: CandidatoFefc[];
  partidos: string[];
  ufs: string[];
  cargos: string[];
};

export function ExploreClient({ candidatos, partidos, ufs, cargos }: Props) {
  const [partido, setPartido] = useState("");
  const [uf, setUf] = useState("");
  const [cargo, setCargo] = useState("");
  const [q, setQ] = useState("");
  const [pending, startTransition] = useTransition();

  const filtered = useMemo(() => {
    const query = q.trim().toLowerCase();
    return candidatos.filter((c) => {
      if (partido && c.partido !== partido) return false;
      if (uf && c.uf !== uf) return false;
      if (cargo && c.cargo !== cargo) return false;
      if (query && !c.nome.toLowerCase().includes(query)) return false;
      return true;
    });
  }, [candidatos, partido, uf, cargo, q]);

  const total = filtered.reduce((s, c) => s + c.valor, 0);

  function onFilter(
    setter: (v: string) => void,
    value: string,
  ) {
    startTransition(() => setter(value));
  }

  function exportCsv() {
    const header = "nome,partido,uf,cargo,valor\n";
    const body = filtered
      .map(
        (c) =>
          `"${c.nome.replace(/"/g, '""')}",${c.partido},${c.uf},"${c.cargo}",${c.valor}`,
      )
      .join("\n");
    const blob = new Blob([header + body], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "fefc-2026-filtrado.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <label className="block text-sm">
          <span className="mb-1 block text-[var(--muted)]">Partido</span>
          <select
            className="field"
            value={partido}
            onChange={(e) => onFilter(setPartido, e.target.value)}
          >
            <option value="">Todos</option>
            {partidos.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="mb-1 block text-[var(--muted)]">UF</span>
          <select
            className="field"
            value={uf}
            onChange={(e) => onFilter(setUf, e.target.value)}
          >
            <option value="">Todas</option>
            {ufs.map((u) => (
              <option key={u} value={u}>
                {u}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="mb-1 block text-[var(--muted)]">Cargo</span>
          <select
            className="field"
            value={cargo}
            onChange={(e) => onFilter(setCargo, e.target.value)}
          >
            <option value="">Todos</option>
            {cargos.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="mb-1 block text-[var(--muted)]">Buscar nome</span>
          <input
            className="field"
            placeholder="Ex.: Silva"
            value={q}
            onChange={(e) => onFilter(setQ, e.target.value)}
          />
        </label>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-[var(--line)] bg-[var(--surface)] px-4 py-3">
        <p className={`text-sm text-[var(--ink)] ${pending ? "opacity-60" : ""}`}>
          <strong className="tabular-nums">{filtered.length}</strong> candidatos ·{" "}
          <strong className="tabular-nums">{formatCompactBRL(total)}</strong> em
          FEFC no filtro
        </p>
        <button
          type="button"
          onClick={exportCsv}
          className="rounded-md bg-[var(--ink)] px-3 py-1.5 text-sm text-[var(--surface)] transition hover:bg-[var(--accent)]"
        >
          Exportar CSV
        </button>
      </div>

      <div className="overflow-x-auto rounded-lg border border-[var(--line)] bg-[var(--surface)]">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="border-b border-[var(--line)] bg-[var(--wash)] text-[var(--muted)]">
            <tr>
              <th className="px-3 py-2 font-medium">Candidato(a)</th>
              <th className="px-3 py-2 font-medium">Partido</th>
              <th className="px-3 py-2 font-medium">UF</th>
              <th className="px-3 py-2 font-medium">Cargo</th>
              <th className="px-3 py-2 text-right font-medium">FEFC</th>
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, 250).map((c) => (
              <tr
                key={`${c.sq_candidato}-${c.nome}`}
                className="border-b border-[var(--line)]/70 hover:bg-[var(--wash)]/60"
              >
                <td className="px-3 py-2 font-medium text-[var(--ink)]">
                  {c.nome}
                </td>
                <td className="px-3 py-2">{c.partido}</td>
                <td className="px-3 py-2">{c.uf}</td>
                <td className="px-3 py-2">{c.cargo}</td>
                <td className="px-3 py-2 text-right tabular-nums">
                  {formatBRL(c.valor)}
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td
                  colSpan={5}
                  className="px-3 py-8 text-center text-[var(--muted)]"
                >
                  Nenhum registro com esses filtros.
                </td>
              </tr>
            )}
          </tbody>
        </table>
        {filtered.length > 250 && (
          <p className="border-t border-[var(--line)] px-3 py-2 text-xs text-[var(--muted)]">
            Mostrando 250 de {filtered.length}. Exporte o CSV para a lista
            completa.
          </p>
        )}
      </div>
    </div>
  );
}
