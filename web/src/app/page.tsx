import Link from "next/link";
import { BarList } from "@/components/BarList";
import { getSummary } from "@/lib/data";
import { formatBRL, formatCompactBRL, formatDateIso, formatPct } from "@/lib/format";

export default async function HomePage() {
  const summary = await getSummary();
  const { meta, por_partido, por_uf, por_cargo, cotas_partidos } = summary;
  const top3 = [...cotas_partidos].sort((a, b) => b.total - a.total).slice(0, 3);
  const top3Share = top3.reduce((s, p) => s + p.pct, 0);

  return (
    <div className="space-y-10">
      <section className="max-w-2xl">
        <h1 className="font-[family-name:var(--font-display)] text-3xl leading-tight tracking-tight text-[var(--ink)] sm:text-4xl">
          Quanto do fundo eleitoral foi para cada partido, cargo e estado?
        </h1>
        <p className="mt-3 text-base text-[var(--muted)] sm:text-lg">
          Painel da comunidade sobre o FEFC 2026: cotas oficiais do TSE e
          repasses declarados a candidatos na prestação de contas.
        </p>
        <div className="mt-5 flex flex-wrap gap-3">
          <Link
            href="/explorar"
            className="rounded-md bg-[var(--accent)] px-4 py-2.5 text-sm font-medium text-white transition hover:brightness-110"
          >
            Explorar por UF e cargo
          </Link>
          <Link
            href="/criterios"
            className="rounded-md border border-[var(--line)] bg-[var(--surface)] px-4 py-2.5 text-sm text-[var(--ink)] transition hover:bg-[var(--wash)]"
          >
            Critérios dos partidos
          </Link>
          <Link
            href="/metodologia"
            className="rounded-md border border-[var(--line)] bg-[var(--surface)] px-4 py-2.5 text-sm text-[var(--ink)] transition hover:bg-[var(--wash)]"
          >
            Como ler os dados
          </Link>
        </div>
      </section>

      {meta.modo === "demo" && (
        <p
          role="status"
          className="rounded-md border border-[var(--warn)]/30 bg-[#fff6e0] px-4 py-3 text-sm text-[var(--warn)]"
        >
          {meta.aviso}
        </p>
      )}

      <section className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border border-[var(--line)] bg-[var(--surface)] p-4">
          <p className="text-xs uppercase tracking-wide text-[var(--muted)]">
            Total do FEFC
          </p>
          <p className="mt-1 font-[family-name:var(--font-display)] text-2xl tabular-nums">
            {formatCompactBRL(meta.total_fefc_oficial)}
          </p>
          <p className="mt-1 text-xs text-[var(--muted)]">
            {formatBRL(meta.total_fefc_oficial, true)} · cota oficial TSE
          </p>
        </div>
        <div className="rounded-lg border border-[var(--line)] bg-[var(--surface)] p-4">
          <p className="text-xs uppercase tracking-wide text-[var(--muted)]">
            Declarado a candidatos
          </p>
          <p className="mt-1 font-[family-name:var(--font-display)] text-2xl tabular-nums">
            {formatCompactBRL(meta.total_declarado_candidatos)}
          </p>
          <p className="mt-1 text-xs text-[var(--muted)]">
            {meta.n_candidatos_com_fefc.toLocaleString("pt-BR")} candidatos com
            receita FEFC
          </p>
        </div>
        <div className="rounded-lg border border-[var(--line)] bg-[var(--surface)] p-4">
          <p className="text-xs uppercase tracking-wide text-[var(--muted)]">
            Concentração (top 3)
          </p>
          <p className="mt-1 font-[family-name:var(--font-display)] text-2xl tabular-nums">
            {formatPct(top3Share)}
          </p>
          <p className="mt-1 text-xs text-[var(--muted)]">
            {top3.map((p) => p.sigla).join(", ")} nas cotas partidárias
          </p>
        </div>
      </section>

      <section className="grid gap-8 lg:grid-cols-2">
        <div>
          <h2 className="font-[family-name:var(--font-display)] text-xl">
            Maiores cotas partidárias
          </h2>
          <p className="mb-4 mt-1 text-sm text-[var(--muted)]">
            Quanto cada partido recebeu do fundo (antes do repasse a
            candidatos).
          </p>
          <BarList
            items={por_partido.map((p) => ({
              label: p.sigla,
              value: p.cota,
            }))}
            maxItems={10}
          />
        </div>
        <div>
          <h2 className="font-[family-name:var(--font-display)] text-xl">
            Por cargo (declarado)
          </h2>
          <p className="mb-4 mt-1 text-sm text-[var(--muted)]">
            Soma das receitas FEFC nas prestações de contas, por cargo.
          </p>
          <BarList
            items={por_cargo.map((c) => ({
              label: c.cargo,
              value: c.valor,
            }))}
          />
        </div>
      </section>

      <section>
        <h2 className="font-[family-name:var(--font-display)] text-xl">
          Por UF (declarado)
        </h2>
        <p className="mb-4 mt-1 text-sm text-[var(--muted)]">
          Estados com mais FEFC declarado a candidatos. Presidente aparece como
          BR quando aplicável.
        </p>
        <BarList
          items={por_uf.map((u) => ({ label: u.uf, value: u.valor }))}
          maxItems={15}
        />
      </section>

      <p className="text-xs text-[var(--muted)]">
        Dados gerados em {formatDateIso(meta.gerado_em)} · modo{" "}
        <code className="rounded bg-[var(--wash)] px-1">{meta.modo}</code>
      </p>
    </div>
  );
}
