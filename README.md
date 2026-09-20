# Fundo Eleitoral 2026

Site para a comunidade acompanhar a distribuição do **Fundo Especial de Financiamento de Campanha (FEFC)** nas Eleições Gerais de 2026 — por partido, cargo e UF.

> Dados oficiais: Tribunal Superior Eleitoral (TSE). Este projeto **não** é afiliado ao TSE.

## Stack (robusta e leve)

| Camada | Tecnologia | Motivo |
|--------|------------|--------|
| Site | Next.js (App Router) + TypeScript no **Vercel** | Deploy grátis, ISR/estático, DX boa |
| Dados no ar | JSON pré-agregados em `public/data/` | Sem banco, carga leve no browser |
| ETL | Python (stdlib) | CSVs do TSE são grandes; processa uma vez |

Fluxo: TSE → ETL → `summary.json` + `candidatos.json` → site estático no Vercel.

## Duas camadas de informação

1. **Cotas partidárias** — valor que cada partido recebe do FEFC (tabela oficial do TSE).
2. **Repasses a candidatos** — UF, cargo e valores declarados na prestação de contas (fonte FEFC). Podem estar incompletos durante a campanha.

## Desenvolvimento local

### 1. Dados de demonstração (já funciona offline)

```bash
python etl/generate_demo.py
cd web
npm install
npm run dev
```

Abra http://localhost:3000

### 2. Dados reais do TSE

O CDN do TSE (`cdn.tse.jus.br`) às vezes bloqueia automações. Rode **na sua máquina** (browser/normal ISP):

```bash
python etl/build_dataset.py --download
```

Ou baixe manualmente o ZIP em  
https://dadosabertos.tse.jus.br/dataset/prestacao-de-contas-eleitorais-2026  
e depois:

```bash
python etl/build_dataset.py --csv caminho/para/receitas_candidatos_2026_BRASIL.csv
```

### 3. Docker (localhost)

Gere os dados e suba o container:

```bash
python etl/generate_demo.py   # ou build_dataset.py com ZIP do TSE
docker compose up --build -d
```

Abra http://localhost:3000

Parar: `docker compose down`

### 4. Deploy Vercel

1. Suba o repositório no GitHub.
2. Importe no Vercel com **Root Directory** = `web`.
3. Workflow `Atualizar dados FEFC` roda diariamente / manualmente e faz commit dos JSON.

Sem Git o redeploy automático e o workflow de dados não funcionam bem — use o repositório.

## Estrutura

```
data/
  seed/cotas_partidos_2026.json   # cotas oficiais
  raw/                            # ZIPs TSE (gitignored)
  processed/                      # saída do ETL
etl/
  build_dataset.py
  generate_demo.py
web/                              # app Next.js → Vercel
```

## Público

Interface pensada para **eleitor leigo** (filtros simples + linguagem clara) e **pesquisadores** (tabelas, export CSV, metodologia e fontes).
