export default function MetodologiaPage() {
  return (
    <article className="prose-custom max-w-2xl space-y-6 text-[var(--ink)]">
      <h1 className="font-[family-name:var(--font-display)] text-3xl tracking-tight">
        Metodologia
      </h1>

      <section className="space-y-2 text-[var(--muted)]">
        <h2 className="font-[family-name:var(--font-display)] text-xl text-[var(--ink)]">
          O que é o FEFC?
        </h2>
        <p>
          O Fundo Especial de Financiamento de Campanha é dinheiro público
          destinado às campanhas eleitorais. Em 2026 o TSE publicou cerca de{" "}
          <strong className="text-[var(--ink)]">R$ 4,96 bilhões</strong>{" "}
          distribuídos entre os partidos segundo regras da Lei das Eleições
          (cotas de 2%, 35%, 48% e 15%).
        </p>
      </section>

      <section className="space-y-2 text-[var(--muted)]">
        <h2 className="font-[family-name:var(--font-display)] text-xl text-[var(--ink)]">
          Duas leituras importantes
        </h2>
        <ol className="list-decimal space-y-2 pl-5">
          <li>
            <strong className="text-[var(--ink)]">Cota do partido</strong> —
            valor oficial que o partido recebe. Não vem quebrado por UF ou
            cargo.
          </li>
          <li>
            <strong className="text-[var(--ink)]">Repasse a candidatos</strong>{" "}
            — o que aparece na prestação de contas como receita com fonte FEFC.
            Aqui entram UF, cargo e nome. Pode haver atraso ou lacunas enquanto
            as contas são atualizadas.
          </li>
        </ol>
      </section>

      <section className="space-y-2 text-[var(--muted)]">
        <h2 className="font-[family-name:var(--font-display)] text-xl text-[var(--ink)]">
          Como processamos
        </h2>
        <p>
          Baixamos o pacote de prestação de contas de candidatos no Portal de
          Dados Abertos do TSE, filtramos lançamentos com fonte FEFC (
          <code className="rounded bg-[var(--wash)] px-1 text-[var(--ink)]">
            CD_FONTE_RECEITA = 2
          </code>{" "}
          ou descrição equivalente) e agregamos por partido, UF e cargo.
        </p>
      </section>

      <section className="space-y-2 text-[var(--muted)]">
        <h2 className="font-[family-name:var(--font-display)] text-xl text-[var(--ink)]">
          Fontes
        </h2>
        <ul className="list-disc space-y-1 pl-5">
          <li>
            <a
              className="text-[var(--accent)] underline-offset-2 hover:underline"
              href="https://www.tse.jus.br/eleicoes/eleicoes-2026-content/prestacao-de-contas/distribuicao-dos-recursos-do-fundo-especial-de-financiamento-de-campanha-fefc-eleicoes-2026"
              target="_blank"
              rel="noreferrer"
            >
              Cálculo de distribuição do FEFC 2026 (TSE)
            </a>
          </li>
          <li>
            <a
              className="text-[var(--accent)] underline-offset-2 hover:underline"
              href="https://dadosabertos.tse.jus.br/dataset/prestacao-de-contas-eleitorais-2026"
              target="_blank"
              rel="noreferrer"
            >
              Prestação de Contas Eleitorais — 2026 (Dados Abertos)
            </a>
          </li>
        </ul>
      </section>

      <section className="space-y-2 text-[var(--muted)]">
        <h2 className="font-[family-name:var(--font-display)] text-xl text-[var(--ink)]">
          Limitações
        </h2>
        <p>
          Prestações parciais mudam com o tempo. Critérios internos de cada
          partido (PDFs no PJe) não entram automaticamente neste painel. Sempre
          confira a data de geração dos arquivos e a fonte oficial do TSE.
        </p>
      </section>
    </article>
  );
}
