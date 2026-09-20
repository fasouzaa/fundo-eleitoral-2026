"""Download and transform TSE FEFC campaign finance data for Eleições 2026.

Expected input (after unzip):
  receitas_candidatos_2026_BRASIL.csv  (semicolon, latin-1)
  — filter CD_FONTE_RECEITA == 2  (FEFC)
  — also match DS_FONTE_RECEITA containing "Fundo Especial"

Outputs written to data/processed/ and copied into web/public/data/.
"""

from __future__ import annotations

import json
import os
import re
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlretrieve

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SEED = ROOT / "data" / "seed"
PROCESSED = ROOT / "data" / "processed"
WEB_DATA = ROOT / "web" / "public" / "data"

CANDIDATOS_ZIP_URL = (
    "https://cdn.tse.jus.br/estatistica/sead/odsele/prestacao_contas/"
    "prestacao_de_contas_eleitorais_candidatos_2026.zip"
)

# TSE open-data layouts historically use these codes for public funds.
FEFC_FONTE_CODES = {"2"}
FEFC_FONTE_PATTERN = re.compile(
    r"fundo\s+especial|fefc",
    re.IGNORECASE,
)


def _brl_to_float(value: str) -> float:
    value = (value or "").strip().strip('"')
    if not value:
        return 0.0
    # Brazilian: 1.234.567,89
    if "," in value and "." in value:
        value = value.replace(".", "").replace(",", ".")
    elif "," in value:
        value = value.replace(",", ".")
    return float(value)


def _download_with_bits(url: str, dest: Path) -> bool:
    """Windows BITS often bypasses Akamai 403 that blocks plain urllib/curl."""
    import platform
    import subprocess

    if platform.system() != "Windows":
        return False
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
            timeout=600,
        )
        return dest.exists() and dest.stat().st_size > 10_000
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        print(f"BITS download failed: {exc}")
        return False


def _download_with_curl(url: str, dest: Path) -> bool:
    """curl with browser UA + warm-up hit on the open-data portal."""
    import shutil
    import subprocess

    curl = shutil.which("curl")
    if not curl:
        return False
    cookie_jar = dest.with_suffix(".cookies")
    ua = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )
    try:
        subprocess.run(
            [
                curl,
                "-fsSL",
                "-A",
                ua,
                "-c",
                str(cookie_jar),
                "-o",
                os.devnull,
                "https://dadosabertos.tse.jus.br/dataset/prestacao-de-contas-eleitorais-2026",
            ],
            check=False,
            timeout=60,
        )
        subprocess.run(
            [
                curl,
                "-fL",
                "--retry",
                "3",
                "--retry-delay",
                "2",
                "-A",
                ua,
                "-b",
                str(cookie_jar),
                "-H",
                "Referer: https://dadosabertos.tse.jus.br/dataset/prestacao-de-contas-eleitorais-2026",
                "-o",
                str(dest),
                url,
            ],
            check=True,
            timeout=600,
        )
        return dest.exists() and dest.stat().st_size > 10_000
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        print(f"curl download failed: {exc}")
        return False
    finally:
        cookie_jar.unlink(missing_ok=True)


def download_candidatos_zip(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {CANDIDATOS_ZIP_URL}")

    if _download_with_bits(CANDIDATOS_ZIP_URL, dest):
        print(f"Saved via BITS {dest} ({dest.stat().st_size:,} bytes)")
        return dest

    if _download_with_curl(CANDIDATOS_ZIP_URL, dest):
        print(f"Saved via curl {dest} ({dest.stat().st_size:,} bytes)")
        return dest

    req_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
        "Referer": "https://dadosabertos.tse.jus.br/",
    }
    import urllib.error
    import urllib.request

    request = Request(CANDIDATOS_ZIP_URL, headers=req_headers)
    try:
        with urllib.request.urlopen(request, timeout=300) as response, open(
            dest, "wb"
        ) as out:
            while True:
                chunk = response.read(1024 * 256)
                if not chunk:
                    break
                out.write(chunk)
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"CDN do TSE recusou o download (HTTP {exc.code}). "
            "Baixe o ZIP manualmente em "
            "https://dadosabertos.tse.jus.br/dataset/prestacao-de-contas-eleitorais-2026 "
            "e rode: python etl/build_dataset.py --csv caminho/receitas_candidatos_*.csv\n"
            "Ou use demo: python etl/generate_demo.py"
        ) from exc

    if dest.stat().st_size < 10_000:
        head = dest.read_bytes()[:200]
        dest.unlink(missing_ok=True)
        raise SystemExit(
            f"Download inválido ({len(head)} bytes). Resposta: {head!r}. "
            "Use --csv com o arquivo local ou generate_demo.py."
        )
    print(f"Saved {dest} ({dest.stat().st_size:,} bytes)")
    return dest


def unzip(zip_path: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)
    return out_dir


def find_receitas_csv(extracted: Path) -> Path:
    matches = list(extracted.rglob("receitas_candidatos*.csv"))
    if not matches:
        # some years nest differently
        matches = [p for p in extracted.rglob("*.csv") if "receita" in p.name.lower()]
    if not matches:
        raise FileNotFoundError(
            f"No receitas_candidatos CSV found under {extracted}. "
            "Check the ZIP layout / leia-me.pdf."
        )
    # Prefer BRASIL aggregate if present
    for m in matches:
        if "BRASIL" in m.name.upper():
            return m
    return matches[0]


def is_fefc_row(row: dict[str, str]) -> bool:
    code = (row.get("CD_FONTE_RECEITA") or "").strip().strip('"')
    if code in FEFC_FONTE_CODES:
        return True
    desc = (row.get("DS_FONTE_RECEITA") or "") + " " + (row.get("DS_ORIGEM_RECEITA") or "")
    return bool(FEFC_FONTE_PATTERN.search(desc))


def parse_receitas(csv_path: Path) -> list[dict]:
    """Stream-parse semicolon CSV without loading entire file into pandas."""
    import csv

    rows: list[dict] = []
    with csv_path.open("r", encoding="latin-1", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for raw in reader:
            if not is_fefc_row(raw):
                continue
            valor = _brl_to_float(raw.get("VR_RECEITA", "0"))
            if valor <= 0:
                continue
            rows.append(
                {
                    "sq_candidato": (raw.get("SQ_CANDIDATO") or "").strip('"'),
                    "nome": (raw.get("NM_CANDIDATO") or "").strip('"'),
                    "partido": (raw.get("SG_PARTIDO") or "").strip('"'),
                    "uf": (raw.get("SG_UF") or "").strip('"').upper(),
                    "cargo": (raw.get("DS_CARGO") or "").strip('"'),
                    "cd_cargo": (raw.get("CD_CARGO") or "").strip('"'),
                    "valor": round(valor, 2),
                    "data_receita": (raw.get("DT_RECEITA") or "").strip('"'),
                    "doador": (raw.get("NM_DOADOR") or raw.get("NM_DOADOR_RFB") or "").strip(
                        '"'
                    ),
                }
            )
    return rows


def aggregate(rows: list[dict], cotas: dict) -> dict:
    by_partido: dict[str, float] = defaultdict(float)
    by_uf: dict[str, float] = defaultdict(float)
    by_cargo: dict[str, float] = defaultdict(float)
    by_uf_cargo: dict[str, float] = defaultdict(float)
    by_candidato: dict[str, dict] = {}

    for r in rows:
        by_partido[r["partido"]] += r["valor"]
        by_uf[r["uf"]] += r["valor"]
        by_cargo[r["cargo"]] += r["valor"]
        by_uf_cargo[f"{r['uf']}|{r['cargo']}"] += r["valor"]

        key = r["sq_candidato"] or f"{r['nome']}|{r['partido']}|{r['uf']}"
        if key not in by_candidato:
            by_candidato[key] = {
                "sq_candidato": r["sq_candidato"],
                "nome": r["nome"],
                "partido": r["partido"],
                "uf": r["uf"],
                "cargo": r["cargo"],
                "valor": 0.0,
            }
        by_candidato[key]["valor"] += r["valor"]

    candidatos = sorted(by_candidato.values(), key=lambda x: x["valor"], reverse=True)
    for c in candidatos:
        c["valor"] = round(c["valor"], 2)

    cotas_map = {p["sigla"]: p["total"] for p in cotas["partidos"]}
    n_por_partido: dict[str, int] = defaultdict(int)
    n_por_uf: dict[str, int] = defaultdict(int)
    n_por_cargo: dict[str, int] = defaultdict(int)
    for c in candidatos:
        n_por_partido[c["partido"]] += 1
        n_por_uf[c["uf"]] += 1
        n_por_cargo[c["cargo"]] += 1

    partido_rows = []
    for sigla, total_cota in sorted(cotas_map.items(), key=lambda x: -x[1]):
        declarado = round(by_partido.get(sigla, 0.0), 2)
        n = n_por_partido.get(sigla, 0)
        partido_rows.append(
            {
                "sigla": sigla,
                "cota": total_cota,
                "declarado_candidatos": declarado,
                "gap": round(total_cota - declarado, 2),
                "pct_repassado": round(declarado / total_cota, 6) if total_cota else 0.0,
                "n_candidatos": n,
                "media_por_candidato": round(declarado / n, 2) if n else 0.0,
            }
        )

    total_declarado = round(sum(c["valor"] for c in candidatos), 2)

    return {
        "meta": {
            "ano": 2026,
            "gerado_em": datetime.now(timezone.utc).isoformat(),
            "total_fefc_oficial": cotas["total_fefc"],
            "total_declarado_candidatos": total_declarado,
            "n_candidatos_com_fefc": len(candidatos),
            "n_lancamentos": len(rows),
            "media_nacional_por_candidato": (
                round(total_declarado / len(candidatos), 2) if candidatos else 0.0
            ),
            "modo": "tse_prestacao",
            "aviso": (
                "Valores por candidato/UF/cargo vêm da prestação de contas (fonte FEFC). "
                "Podem estar incompletos enquanto a campanha e as prestações avançam. "
                "Média por candidato = declarado ÷ candidatos que receberam FEFC."
            ),
            "fontes": [
                cotas["fonte"],
                "https://dadosabertos.tse.jus.br/dataset/prestacao-de-contas-eleitorais-2026",
            ],
        },
        "cotas_partidos": cotas["partidos"],
        "por_partido": partido_rows,
        "por_uf": [
            {
                "uf": k,
                "valor": round(v, 2),
                "n_candidatos": n_por_uf.get(k, 0),
                "media_por_candidato": (
                    round(v / n_por_uf[k], 2) if n_por_uf.get(k) else 0.0
                ),
            }
            for k, v in sorted(by_uf.items(), key=lambda x: -x[1])
        ],
        "por_cargo": [
            {
                "cargo": k,
                "valor": round(v, 2),
                "n_candidatos": n_por_cargo.get(k, 0),
                "media_por_candidato": (
                    round(v / n_por_cargo[k], 2) if n_por_cargo.get(k) else 0.0
                ),
            }
            for k, v in sorted(by_cargo.items(), key=lambda x: -x[1])
        ],
        "por_uf_cargo": [
            {"uf": k.split("|")[0], "cargo": k.split("|", 1)[1], "valor": round(v, 2)}
            for k, v in sorted(by_uf_cargo.items(), key=lambda x: -x[1])
        ],
        "candidatos": candidatos,
    }


def write_outputs(payload: dict) -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    WEB_DATA.mkdir(parents=True, exist_ok=True)

    summary = {
        "meta": payload["meta"],
        "por_partido": payload["por_partido"],
        "por_uf": payload["por_uf"],
        "por_cargo": payload["por_cargo"],
        "por_uf_cargo": payload["por_uf_cargo"],
        "cotas_partidos": payload["cotas_partidos"],
        "top_candidatos": payload["candidatos"][:100],
    }
    candidatos = {
        "meta": {
            "gerado_em": payload["meta"]["gerado_em"],
            "n": len(payload["candidatos"]),
            "modo": payload["meta"]["modo"],
        },
        "candidatos": payload["candidatos"],
    }

    for folder in (PROCESSED, WEB_DATA):
        (folder / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        (folder / "candidatos.json").write_text(
            json.dumps(candidatos, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
    print(f"Wrote summary + candidatos to {PROCESSED} and {WEB_DATA}")


def build_from_csv(csv_path: Path) -> None:
    cotas = json.loads((SEED / "cotas_partidos_2026.json").read_text(encoding="utf-8"))
    print(f"Parsing FEFC rows from {csv_path}")
    rows = parse_receitas(csv_path)
    print(f"  {len(rows):,} FEFC revenue rows")
    payload = aggregate(rows, cotas)
    write_outputs(payload)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="ETL FEFC 2026")
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download candidatos ZIP from TSE CDN",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        help="Path to receitas_candidatos CSV (skips download)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Generate demo dataset without TSE download",
    )
    args = parser.parse_args()

    if args.demo:
        from generate_demo import generate_demo

        generate_demo()
        return

    if args.csv:
        build_from_csv(args.csv)
        return

    zip_path = RAW / "prestacao_de_contas_eleitorais_candidatos_2026.zip"
    if args.download or not zip_path.exists():
        download_candidatos_zip(zip_path)

    extracted = RAW / "candidatos_2026"
    unzip(zip_path, extracted)
    csv_path = find_receitas_csv(extracted)
    build_from_csv(csv_path)


if __name__ == "__main__":
    main()
