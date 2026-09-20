export type PartidoCota = {
  sigla: string;
  cota_2: number;
  cota_35: number;
  cota_48: number;
  cota_15: number;
  total: number;
  pct: number;
};

export type PartidoRepasse = {
  sigla: string;
  cota: number;
  declarado_candidatos: number;
  gap: number;
  pct_repassado: number;
};

export type CandidatoFefc = {
  sq_candidato: string;
  nome: string;
  partido: string;
  uf: string;
  cargo: string;
  valor: number;
};

export type Summary = {
  meta: {
    ano: number;
    gerado_em: string;
    total_fefc_oficial: number;
    total_declarado_candidatos: number;
    n_candidatos_com_fefc: number;
    n_lancamentos: number;
    modo: "demo" | "tse_prestacao" | string;
    aviso: string;
    fontes: string[];
  };
  cotas_partidos: PartidoCota[];
  por_partido: PartidoRepasse[];
  por_uf: { uf: string; valor: number }[];
  por_cargo: { cargo: string; valor: number }[];
  por_uf_cargo: { uf: string; cargo: string; valor: number }[];
  top_candidatos: CandidatoFefc[];
};

export type CandidatosFile = {
  meta: { gerado_em: string; n: number; modo: string };
  candidatos: CandidatoFefc[];
};
