import { ExploreClient } from "@/components/ExploreClient";
import { getCandidatos } from "@/lib/data";

export default async function ExplorarPage() {
  const { candidatos, meta } = await getCandidatos();
  const partidos = [...new Set(candidatos.map((c) => c.partido))].sort();
  const ufs = [...new Set(candidatos.map((c) => c.uf))].sort();
  const cargos = [...new Set(candidatos.map((c) => c.cargo))].sort();

  return (
    <div className="space-y-6">
      <div className="max-w-2xl">
        <h1 className="font-[family-name:var(--font-display)] text-3xl tracking-tight">
          Explorar repasses
        </h1>
        <p className="mt-2 text-[var(--muted)]">
          Filtre por partido, estado e cargo. Exportação CSV para quem quiser
          analisar fora do site.
        </p>
        {meta.modo === "demo" && (
          <p className="mt-3 text-sm text-[var(--warn)]">
            Dataset de demonstração — rode o ETL com dados do TSE para números
            reais.
          </p>
        )}
      </div>
      <ExploreClient
        candidatos={candidatos}
        partidos={partidos}
        ufs={ufs}
        cargos={cargos}
      />
    </div>
  );
}
