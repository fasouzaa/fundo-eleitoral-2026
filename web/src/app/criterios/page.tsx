import { CriteriosClient } from "@/components/CriteriosClient";
import { getCriterios } from "@/lib/data";
import { formatDateIso } from "@/lib/format";

export default async function CriteriosPage() {
  const { meta, partidos } = await getCriterios();

  return (
    <div className="space-y-6">
      <div className="max-w-2xl">
        <h1 className="font-[family-name:var(--font-display)] text-3xl tracking-tight">
          Critérios internos dos partidos
        </h1>
        <p className="mt-2 text-[var(--muted)]">
          Cada partido define como repassa o FEFC aos candidatos. Os documentos
          abaixo são os arquivos protocolados no TSE (PJe), com prévia
          automática do texto.
        </p>
        <p className="mt-3 text-sm text-[var(--warn)]">{meta.aviso}</p>
        <p className="mt-2 text-xs text-[var(--muted)]">
          {meta.n_ok} de {meta.n_total} partidos com PDF indexado · gerado em{" "}
          {formatDateIso(meta.gerado_em)} ·{" "}
          <a
            className="text-[var(--accent)] underline-offset-2 hover:underline"
            href={meta.fonte}
            target="_blank"
            rel="noreferrer"
          >
            fonte TSE
          </a>
        </p>
      </div>
      <CriteriosClient partidos={partidos} />
    </div>
  );
}
