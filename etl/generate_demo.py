"""Synthetic FEFC distribution for local UI development when TSE CDN is unreachable."""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "seed"

UFS = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT",
    "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
]
CARGOS = [
    "Presidente",
    "Governador",
    "Senador",
    "Deputado Federal",
    "Deputado Estadual",
    "Deputado Distrital",
]


def generate_demo(seed: int = 2026) -> None:
    from build_dataset import aggregate, write_outputs

    random.seed(seed)
    cotas = json.loads((SEED / "cotas_partidos_2026.json").read_text(encoding="utf-8"))

    # Weight UFs roughly by electorate size (approx)
    uf_weights = {
        "SP": 22, "MG": 10, "RJ": 8, "BA": 7, "RS": 6, "PR": 6, "PE": 5, "CE": 5,
        "PA": 4, "MA": 3, "GO": 3, "SC": 3, "PB": 2, "ES": 2, "AM": 2, "RN": 2,
        "AL": 2, "MT": 2, "PI": 2, "DF": 2, "MS": 1.5, "SE": 1.5, "RO": 1, "TO": 1,
        "AC": 0.5, "AP": 0.5, "RR": 0.4,
    }
    cargo_weights = {
        "Presidente": 0.08,
        "Governador": 0.18,
        "Senador": 0.12,
        "Deputado Federal": 0.32,
        "Deputado Estadual": 0.28,
        "Deputado Distrital": 0.02,
    }

    rows: list[dict] = []
    sq = 1000000
    # Repass ~35% of each party quota into fake candidate receipts (campaign mid-point)
    for partido in cotas["partidos"]:
        pool = partido["total"] * 0.35
        n = max(3, int(partido["pct"] * 800) + 2)
        for i in range(n):
            uf = random.choices(UFS, weights=[uf_weights[u] for u in UFS], k=1)[0]
            if uf == "DF":
                cargo = random.choices(
                    ["Presidente", "Governador", "Senador", "Deputado Federal", "Deputado Distrital"],
                    weights=[0.05, 0.15, 0.15, 0.35, 0.30],
                    k=1,
                )[0]
            else:
                cargo = random.choices(
                    list(cargo_weights.keys())[:-1],
                    weights=[cargo_weights[c] for c in list(cargo_weights.keys())[:-1]],
                    k=1,
                )[0]
            share = random.random() ** 2  # skew to a few large recipients
            valor = round(pool * share / n * random.uniform(0.4, 2.2), 2)
            if valor < 1000:
                continue
            sq += 1
            rows.append(
                {
                    "sq_candidato": str(sq),
                    "nome": f"Candidato(a) Demo {partido['sigla']} {i+1}",
                    "partido": partido["sigla"],
                    "uf": "BR" if cargo == "Presidente" else uf,
                    "cargo": cargo,
                    "cd_cargo": "",
                    "valor": valor,
                    "data_receita": "01/09/2026",
                    "doador": f"Direção Nacional - {partido['sigla']}",
                }
            )

    payload = aggregate(rows, cotas)
    payload["meta"]["modo"] = "demo"
    payload["meta"]["aviso"] = (
        "DATASET DE DEMONSTRAÇÃO — não são valores reais de prestação. "
        "Rode `python etl/build_dataset.py --download` na sua máquina para dados do TSE."
    )
    payload["meta"]["gerado_em"] = datetime.now(timezone.utc).isoformat()
    write_outputs(payload)
    print(f"Demo dataset: {len(payload['candidatos'])} candidatos")


if __name__ == "__main__":
    generate_demo()
