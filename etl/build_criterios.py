"""Baixa e indexa os critérios internos de distribuição do FEFC publicados pelo TSE.

Fonte: https://www.tse.jus.br/eleicoes/eleicoes-2026-content/prestacao-de-contas/fundo-especial-de-financiamento-de-campanha-fefc
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "criterios"
SEED = ROOT / "data" / "seed"
PROCESSED = ROOT / "data" / "processed"
WEB_DATA = ROOT / "web" / "public" / "data"

FONTE_PAGE = (
    "https://www.tse.jus.br/eleicoes/eleicoes-2026-content/prestacao-de-contas/"
    "fundo-especial-de-financiamento-de-campanha-fefc"
)
ARQUIVOS_BASE = (
    "https://www.tse.jus.br/eleicoes/eleicoes-2026-content/prestacao-de-contas/arquivos"
)

# Metadados oficiais da tabela TSE + slugs prováveis do Plone para o PDF.
# sigla alinhada às cotas do site (UNIÃO, PODE, PP, PC do B…).
PARTIDOS: list[dict] = [
    {"sigla": "AGIR", "nome": "AGIR", "pje": "0601331-51.2026.6.00.0000", "liberado_em": "20.8.2026", "slugs": ["agir"]},
    {"sigla": "AVANTE", "nome": "AVANTE", "pje": "0601256-12.2026.6.00.0000", "liberado_em": "20.8.2026", "slugs": ["avante"]},
    {"sigla": "CIDADANIA", "nome": "CIDADANIA", "pje": "0601386-02.2026.6.00.0000", "liberado_em": "21.8.2026", "slugs": ["cidadania"]},
    {"sigla": "DC", "nome": "DC", "pje": "0601294-24.2026.6.00.0000", "liberado_em": "20.8.2026", "slugs": ["dc"]},
    {"sigla": "DEMOCRATA", "nome": "DEMOCRATA", "pje": "0601633-80.2026.6.00.0000", "liberado_em": None, "slugs": ["democrata"], "tem_arquivo": False},
    {"sigla": "MDB", "nome": "MDB", "pje": "0601241-43.2026.6.00.0000", "liberado_em": "21.8.2026", "slugs": ["mdb"]},
    {"sigla": "MISSÃO", "nome": "MISSÃO", "pje": "0601201-61.2026.6.00.0000", "liberado_em": "20.8.2026", "slugs": ["missao", "missão"]},
    {"sigla": "MOBILIZA", "nome": "MOBILIZA", "pje": "0601289-02.2026.6.00.0000", "liberado_em": "20.8.2026", "slugs": ["mobiliza"]},
    {"sigla": "NOVO", "nome": "NOVO", "pje": "0601242-28.2026.6.00.0000", "liberado_em": "21.8.2026", "slugs": ["novo"]},
    {"sigla": "PCB", "nome": "PCB", "pje": "0601258-79.2026.6.00.0000", "liberado_em": None, "slugs": ["pcb"], "tem_arquivo": False},
    {"sigla": "PC do B", "nome": "PC do B", "pje": "0601045-73.2026.6.00.0000", "liberado_em": "21.8.2026", "slugs": ["pcdob", "pc_do_b", "pc-do-b", "partido_comunista_do_brasil"]},
    {
        "sigla": "PCO",
        "nome": "PCO",
        "pje": "0601433-73.2026.6.00.0000",
        "liberado_em": "11.9.2026",
        "slugs": ["pco"],
        "pdf_urls": [
            f"{ARQUIVOS_BASE}/fefc-do-partido-da-causa-operaria-pco/@@display-file/file/anexo_3777316_petciv_0601433_73-2026-6-00-0000___pco_nacional___criterios_fefc.pdf"
        ],
    },
    {"sigla": "PDT", "nome": "PDT", "pje": "0601505-60.2026.6.00.0000", "liberado_em": "21.8.2026", "slugs": ["pdt"]},
    {"sigla": "PL", "nome": "PL", "pje": "0600974-71.2026.6.00.0000", "liberado_em": "20.8.2026", "slugs": ["pl"]},
    {"sigla": "PODE", "nome": "PODEMOS", "pje": "0601313-30.2026.6.00.0000", "liberado_em": "20.8.2026", "slugs": ["podemos", "pode"]},
    {"sigla": "PRD", "nome": "PRD", "pje": "0601394-76.2026.6.00.0000", "liberado_em": "21.8.2026", "slugs": ["prd"]},
    {"sigla": "PP", "nome": "PROGRESSISTAS", "pje": "0601183-40.2026.6.00.0000", "liberado_em": "20.8.2026", "slugs": ["progressistas", "pp"]},
    {"sigla": "PRTB", "nome": "PRTB", "pje": "0601423-29.2026.6.00.0000", "liberado_em": "27.8.2026", "slugs": ["prtb"]},
    {"sigla": "PSB", "nome": "PSB", "pje": "0601246-65.2026.6.00.0000", "liberado_em": "21.8.2026", "slugs": ["psb"]},
    {"sigla": "PSD", "nome": "PSD", "pje": "0601228-44.2026.6.00.0000", "liberado_em": "20.8.2026", "slugs": ["psd"]},
    {"sigla": "PSDB", "nome": "PSDB", "pje": "0601282-10.2026.6.00.0000", "liberado_em": "20.8.2026", "slugs": ["psdb"]},
    {"sigla": "PSOL", "nome": "PSOL", "pje": "0601317-67.2026.6.00.0000", "liberado_em": "20.8.2026", "slugs": ["psol"]},
    {"sigla": "PSTU", "nome": "PSTU", "pje": "0601348-87.2026.6.00.0000", "liberado_em": "25.8.2026", "slugs": ["pstu"]},
    {"sigla": "PT", "nome": "PT", "pje": "0601252-72.2026.6.00.0000", "liberado_em": "21.8.2026", "slugs": ["pt"]},
    {"sigla": "PV", "nome": "PV", "pje": "0601401-68.2026.6.00.0000", "liberado_em": "21.8.2026", "slugs": ["pv"]},
    {"sigla": "REDE", "nome": "REDE", "pje": "0601400-83.2026.6.00.0000", "liberado_em": "21.8.2026", "slugs": ["rede"]},
    {"sigla": "REPUBLICANOS", "nome": "REPUBLICANOS", "pje": "0601044-88.2026.6.00.0000", "liberado_em": "21.8.2026", "slugs": ["republicanos"]},
    {"sigla": "SOLIDARIEDADE", "nome": "SOLIDARIEDADE", "pje": "0601298-61.2026.6.00.0000", "liberado_em": "20.8.2026", "slugs": ["solidariedade"]},
    {"sigla": "UNIÃO", "nome": "UNIÃO BRASIL", "pje": "0601251-87.2026.6.00.0000", "liberado_em": "21.8.2026", "slugs": ["uniao_brasil", "uniao", "união_brasil"]},
    {
        "sigla": "UP",
        "nome": "UP",
        "pje": "0601351-42.2026.6.00.0000",
        "liberado_em": "02.9.2026",
        "slugs": ["up", "unidade_popular"],
        "pdf_urls": [
            f"{ARQUIVOS_BASE}/anexo_3766845_petciv_0601351_42-2026-6-00-0000___unidade_popular___criterios_fefc/@@display-file/file/anexo_3766845_petciv_0601351_42-2026-6-00-0000___unidade_popular___criterios_fefc.pdf"
        ],
    },
]


def pje_to_folder_id(pje: str) -> str:
    # 0601331-51.2026.6.00.0000 -> 0601331_51-2026-6-00-0000
    left, rest = pje.split("-", 1)
    rest = rest.replace(".", "-")
    return f"{left}_{rest}"


def candidate_urls(partido: dict) -> list[str]:
    urls: list[str] = list(partido.get("pdf_urls") or [])
    folder_id = pje_to_folder_id(partido["pje"])
    for slug in partido.get("slugs") or []:
        name = f"petciv_{folder_id}___{slug}_nacional___criterios_fefc"
        urls.append(f"{ARQUIVOS_BASE}/{name}/@@display-file/file/{name}.pdf")
        urls.append(f"{ARQUIVOS_BASE}/{name}/@@download/file/{name}.pdf")
    # dedupe preserving order
    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def download_bits(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 50_000:
        return True
    ps = (
        f"Import-Module BitsTransfer; "
        f"Start-BitsTransfer -Source '{url}' -Destination '{dest}'"
    )
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            check=True,
            capture_output=True,
            text=True,
            timeout=300,
        )
        return dest.exists() and dest.stat().st_size > 50_000
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        dest.unlink(missing_ok=True)
        return False


def extract_text(pdf_path: Path, max_chars: int = 12000) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        print("Instale pypdf: pip install pypdf", file=sys.stderr)
        return ""
    reader = PdfReader(str(pdf_path))
    parts: list[str] = []
    total = 0
    for page in reader.pages:
        t = page.extract_text() or ""
        parts.append(t)
        total += len(t)
        if total >= max_chars:
            break
    text = "\n".join(parts)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:max_chars].strip()


def summarize_heuristics(text: str) -> dict:
    """Sinais simples para o leigo — não substitui o PDF."""
    low = text.lower()
    flags = {
        "menciona_genero": bool(re.search(r"g[eê]nero|mulher|feminina", low)),
        "menciona_raca": bool(re.search(r"ra[cç]a|negro|negra|preta|parda", low)),
        "menciona_cargo": bool(re.search(r"presidente|governador|senador|deputad", low)),
        "menciona_percentual": bool(re.search(r"\d+\s*%|por\s*cento", low)),
        "menciona_uf": bool(re.search(r"\buf\b|estado|unidade da federa", low)),
    }
    # trechos candidatas a "critério"
    snippets: list[str] = []
    for m in re.finditer(
        r"(?:crit[eé]rio|distribui[cç][aã]o|cota|percentual)[^\n]{20,220}",
        text,
        flags=re.IGNORECASE,
    ):
        s = re.sub(r"\s+", " ", m.group(0)).strip()
        if s not in snippets:
            snippets.append(s)
        if len(snippets) >= 8:
            break
    return {"sinais": flags, "trechos": snippets}


def build() -> dict:
    RAW.mkdir(parents=True, exist_ok=True)
    partidos_out: list[dict] = []

    for p in PARTIDOS:
        entry = {
            "sigla": p["sigla"],
            "nome": p["nome"],
            "pje": p["pje"],
            "liberado_em": p.get("liberado_em"),
            "tem_arquivo": p.get("tem_arquivo", True),
            "pdf_url": None,
            "pdf_local": None,
            "texto_extraido": "",
            "resumo": {"sinais": {}, "trechos": []},
            "status": "sem_arquivo",
        }
        if not entry["tem_arquivo"]:
            partidos_out.append(entry)
            continue

        dest = RAW / f"{p['sigla'].replace(' ', '_').lower()}.pdf"
        ok = False
        used_url = None
        for url in candidate_urls(p):
            print(f"  try {p['sigla']}: {url.split('/')[-3] if '/' in url else url}")
            if download_bits(url, dest):
                ok = True
                used_url = url
                break
        if ok and used_url:
            text = extract_text(dest)
            entry.update(
                {
                    "pdf_url": used_url,
                    "pdf_local": str(dest.relative_to(ROOT)).replace("\\", "/"),
                    "texto_extraido": text,
                    "resumo": summarize_heuristics(text),
                    "status": "ok",
                    "paginas_aprox": None,
                }
            )
            print(f"  OK {p['sigla']} ({dest.stat().st_size:,} bytes)")
        else:
            entry["status"] = "pdf_nao_encontrado"
            print(f"  FAIL {p['sigla']}")
        partidos_out.append(entry)

    payload = {
        "meta": {
            "gerado_em": datetime.now(timezone.utc).isoformat(),
            "fonte": FONTE_PAGE,
            "aviso": (
                "Os critérios são decisão interna de cada partido (PJe no TSE). "
                "O texto abaixo é extração automática do PDF publicado; confira sempre o inteiro teor."
            ),
            "n_ok": sum(1 for x in partidos_out if x["status"] == "ok"),
            "n_total": len(partidos_out),
        },
        "partidos": partidos_out,
    }

    # Versão leve para o site (sem texto completo gigante)
    web = {
        "meta": payload["meta"],
        "partidos": [
            {
                "sigla": x["sigla"],
                "nome": x["nome"],
                "pje": x["pje"],
                "liberado_em": x["liberado_em"],
                "tem_arquivo": x["tem_arquivo"],
                "pdf_url": x["pdf_url"],
                "status": x["status"],
                "resumo": x["resumo"],
                "texto_preview": (x.get("texto_extraido") or "")[:3500],
            }
            for x in partidos_out
        ],
    }

    PROCESSED.mkdir(parents=True, exist_ok=True)
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "criterios.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (WEB_DATA / "criterios.json").write_text(
        json.dumps(web, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    (SEED / "criterios_partidos_2026.json").write_text(
        json.dumps(
            [{"sigla": p["sigla"], "nome": p["nome"], "pje": p["pje"], "liberado_em": p.get("liberado_em"), "slugs": p["slugs"], "tem_arquivo": p.get("tem_arquivo", True)} for p in PARTIDOS],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Wrote criterios: {web['meta']['n_ok']}/{web['meta']['n_total']} PDFs")
    return web


if __name__ == "__main__":
    build()
