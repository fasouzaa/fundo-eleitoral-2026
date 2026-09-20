"""Enriquece summary.json com contagens e média por candidato (a partir de candidatos.json)."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web" / "public" / "data"
PROCESSED = ROOT / "data" / "processed"


def enrich() -> None:
    candidatos = json.loads((WEB / "candidatos.json").read_text(encoding="utf-8"))
    summary = json.loads((WEB / "summary.json").read_text(encoding="utf-8"))

    by_partido_n: dict[str, int] = defaultdict(int)
    by_uf_n: dict[str, int] = defaultdict(int)
    by_cargo_n: dict[str, int] = defaultdict(int)

    for c in candidatos["candidatos"]:
        by_partido_n[c["partido"]] += 1
        by_uf_n[c["uf"]] += 1
        by_cargo_n[c["cargo"]] += 1

    for p in summary["por_partido"]:
        n = by_partido_n.get(p["sigla"], 0)
        p["n_candidatos"] = n
        p["media_por_candidato"] = (
            round(p["declarado_candidatos"] / n, 2) if n else 0.0
        )

    for u in summary["por_uf"]:
        n = by_uf_n.get(u["uf"], 0)
        u["n_candidatos"] = n
        u["media_por_candidato"] = round(u["valor"] / n, 2) if n else 0.0

    for c in summary["por_cargo"]:
        n = by_cargo_n.get(c["cargo"], 0)
        c["n_candidatos"] = n
        c["media_por_candidato"] = round(c["valor"] / n, 2) if n else 0.0

    n_total = summary["meta"]["n_candidatos_com_fefc"]
    summary["meta"]["media_nacional_por_candidato"] = (
        round(summary["meta"]["total_declarado_candidatos"] / n_total, 2)
        if n_total
        else 0.0
    )

    text = json.dumps(summary, ensure_ascii=False, separators=(",", ":"))
    (WEB / "summary.json").write_text(text, encoding="utf-8")
    PROCESSED.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "summary.json").write_text(text, encoding="utf-8")
    print(
        "enriched:",
        "media nacional",
        summary["meta"]["media_nacional_por_candidato"],
        "| partidos",
        len(summary["por_partido"]),
    )


if __name__ == "__main__":
    enrich()
