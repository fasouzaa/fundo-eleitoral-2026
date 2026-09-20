"use client";

import { useMemo, useState } from "react";
import type { CriterioPartido } from "@/lib/types-criterios";

const SINAL_LABELS: Record<string, string> = {
  menciona_genero: "Gênero",
  menciona_raca: "Raça",
  menciona_cargo: "Cargos",
  menciona_percentual: "Percentuais",
  menciona_uf: "UF/estado",
};

export function CriteriosClient({ partidos }: { partidos: CriterioPartido[] }) {
  const [q, setQ] = useState("");
  const [aberto, setAberto] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const query = q.trim().toLowerCase();
    if (!query) return partidos;
    return partidos.filter(
      (p) =>
        p.sigla.toLowerCase().includes(query) ||
        p.nome.toLowerCase().includes(query) ||
        p.pje.includes(query),
    );
  }, [partidos, q]);

  return (
    <div className="space-y-4">
      <label className="block max-w-sm text-sm">
        <span className="mb-1 block text-[var(--muted)]">Buscar partido</span>
        <input
          className="field"
          placeholder="Ex.: PT, PL, União…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </label>

      <ul className="space-y-3">
        {filtered.map((p) => {
          const isOpen = aberto === p.sigla;
          const sinais = Object.entries(p.resumo?.sinais || {}).filter(
            ([, v]) => v,
          );
          return (
            <li
              key={p.sigla}
              className="rounded-lg border border-[var(--line)] bg-[var(--surface)]"
            >
              <button
                type="button"
                className="flex w-full flex-wrap items-center justify-between gap-2 px-4 py-3 text-left"
                onClick={() => setAberto(isOpen ? null : p.sigla)}
                aria-expanded={isOpen}
              >
                <div>
                  <p className="font-[family-name:var(--font-display)] text-lg text-[var(--ink)]">
                    {p.sigla}
                    <span className="ml-2 text-sm font-sans font-normal text-[var(--muted)]">
                      {p.nome !== p.sigla ? p.nome : ""}
                    </span>
                  </p>
                  <p className="text-xs text-[var(--muted)]">
                    PJe {p.pje}
                    {p.liberado_em ? ` · liberado em ${p.liberado_em}` : ""}
                    {" · "}
                    {p.status === "ok"
                      ? "PDF disponível"
                      : p.status === "sem_arquivo"
                        ? "Sem arquivo no TSE"
                        : "PDF não indexado"}
                  </p>
                </div>
                <span className="text-sm text-[var(--accent)]">
                  {isOpen ? "Fechar" : "Ver critérios"}
                </span>
              </button>

              {isOpen && (
                <div className="space-y-3 border-t border-[var(--line)] px-4 py-3 text-sm text-[var(--muted)]">
                  {sinais.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {sinais.map(([k]) => (
                        <span
                          key={k}
                          className="rounded bg-[var(--accent-soft)] px-2 py-0.5 text-xs text-[var(--accent)]"
                        >
                          {SINAL_LABELS[k] || k}
                        </span>
                      ))}
                    </div>
                  )}

                  {(p.resumo?.trechos || []).length > 0 && (
                    <div>
                      <p className="mb-1 font-medium text-[var(--ink)]">
                        Trechos detectados
                      </p>
                      <ul className="list-disc space-y-1 pl-5">
                        {p.resumo.trechos.slice(0, 6).map((t) => (
                          <li key={t.slice(0, 40)}>{t}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {p.texto_preview && (
                    <details>
                      <summary className="cursor-pointer text-[var(--ink)]">
                        Prévia do texto extraído do PDF
                      </summary>
                      <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap rounded bg-[var(--wash)] p-3 text-xs leading-relaxed text-[var(--ink)]">
                        {p.texto_preview}
                      </pre>
                    </details>
                  )}

                  <div className="flex flex-wrap gap-3 pt-1">
                    {p.pdf_url && (
                      <a
                        href={p.pdf_url}
                        target="_blank"
                        rel="noreferrer"
                        className="rounded-md bg-[var(--accent)] px-3 py-1.5 text-white hover:brightness-110"
                      >
                        Abrir PDF no TSE
                      </a>
                    )}
                    <a
                      href={`https://www.tse.jus.br/eleicoes/eleicoes-2026-content/prestacao-de-contas/fundo-especial-de-financiamento-de-campanha-fefc`}
                      target="_blank"
                      rel="noreferrer"
                      className="rounded-md border border-[var(--line)] px-3 py-1.5 text-[var(--ink)] hover:bg-[var(--wash)]"
                    >
                      Página oficial
                    </a>
                  </div>
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
