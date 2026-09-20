export type CriterioSinais = {
  menciona_genero: boolean;
  menciona_raca: boolean;
  menciona_cargo: boolean;
  menciona_percentual: boolean;
  menciona_uf: boolean;
};

export type CriterioPartido = {
  sigla: string;
  nome: string;
  pje: string;
  liberado_em: string | null;
  tem_arquivo: boolean;
  pdf_url: string | null;
  status: string;
  resumo: {
    sinais: Partial<CriterioSinais>;
    trechos: string[];
  };
  texto_preview: string;
};

export type CriteriosFile = {
  meta: {
    gerado_em: string;
    fonte: string;
    aviso: string;
    n_ok: number;
    n_total: number;
  };
  partidos: CriterioPartido[];
};
