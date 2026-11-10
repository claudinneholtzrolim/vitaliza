"""Conferência de 96 registros (24 por persona, seed 96), independente da conferência de 12.

Uso (na raiz):  .venv/bin/python src/conferir_96_registros_s5.py [--saida PASTA]
Os 12 registros da conferência de 12 (seed 42) são reproduzidos por seed e EXCLUÍDOS do sorteio.
Saída (padrão dados/saidas/s5_kiril/conferencia_96/): comparacoes_96x17.csv, resumo_por_registro.csv,
resumo_por_metrica.csv, falhas.csv, estatisticas.json. Não altera dados/brutos.

Desenho (quotas por persona; NÃO é amostra probabilística da base):
  por persona 24 = 8 sorteio simples (A) + 8 com garmin e cópia do app (B) + 4 borda C1 + 4 borda C2.
  Bordas: Adormecidos C1 sem treino em 90 dias, C2 renovação desligada com treino; Rotina em casa e Rua e ritmo
  C1 renovação desligada, C2 ticket em 90 dias; Novatos C1 conta com menos de 30 dias, C2 de 30 a 89 dias.
Zero falhas NÃO autoriza limite populacional de erro (a regra de três só vale para amostra aleatória simples).
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conferencia_comum_s5 import (NOMES, bate, carregar_brutos, carregar_segmentos, comparar, diferenca,  # noqa: E402
                                  indexar_atividades, sortear_12, sortear_96)

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", type=Path, default=ROOT / "dados/saidas/s5_kiril")
    base = ap.parse_args().saida
    out = base / "conferencia_96"
    out.mkdir(parents=True, exist_ok=True)

    seg = carregar_segmentos(ROOT)
    atv_all, rows_de = indexar_atividades(ROOT)
    anteriores = set(sortear_12(seg, rows_de))
    assert len(anteriores) == 12
    alvo = sortear_96(seg, atv_all, anteriores)
    print("sorteados:", len(alvo), "| por persona:", pd.Series([v[0] for v in alvo.values()]).value_counts().sort_index().to_dict())

    T = carregar_brutos(ROOT / "dados/brutos", alvo)
    seg_i = seg.set_index("user_id")
    atv_i = {u: g.to_dict("records") for u, g in atv_all[atv_all.user_id.isin(set(alvo))].groupby("user_id")}
    linhas, resumo = [], []
    for u, (k, letra, rotulo) in alvo.items():
        comp, _ = comparar(u, seg_i.loc[u], atv_i.get(u, []), T)
        n_ok = 0
        for nome, mine, pipe, tol in comp:
            bom = bate(mine, pipe, tol)
            n_ok += bom
            linhas.append(dict(user_id=u, persona=NOMES[k], papel=letra, rotulo=rotulo, metrica=nome, recalculado=mine,
                               base=None if (isinstance(pipe, float) and pd.isna(pipe)) else pipe,
                               confere=bool(bom), diferenca=diferenca(mine, pipe)))
        resumo.append(dict(user_id=u, persona=NOMES[k], papel=letra, rotulo=rotulo, metricas_ok=n_ok, metricas=len(comp)))

    df, rp = pd.DataFrame(linhas), pd.DataFrame(resumo)
    df.to_csv(out / "comparacoes_96x17.csv", index=False)
    rp.sort_values(["persona", "papel", "user_id"]).to_csv(out / "resumo_por_registro.csv", index=False)
    pm = df.groupby("metrica").agg(comparacoes=("confere", "size"), conferem=("confere", "sum"), dif_max=("diferenca", "max"),
                                   dif_media=("diferenca", "mean")).reset_index()
    pm.to_csv(out / "resumo_por_metrica.csv", index=False)
    df[~df.confere].to_csv(out / "falhas.csv", index=False)
    stats = {"registros": len(rp), "metricas_por_registro": int(rp.metricas.iloc[0]), "comparacoes": len(df),
             "conferem": int(df.confere.sum()), "falhas": int((~df.confere).sum()),
             "registros_17_17": int((rp.metricas_ok == rp.metricas).sum()), "semente": 96,
             "excluidos_da_amostra_anterior": len(anteriores),
             "tempo_assinatura_dif_dias": df[df.metrica == "tempo de assinatura (dias)"].diferenca.value_counts().sort_index().to_dict()}
    (out / "estatisticas.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
    print(rp.assign(ok=rp.metricas_ok == rp.metricas).groupby(["persona", "papel"]).ok.agg(["sum", "size"]).to_string())
    if stats["falhas"]:
        print(df[~df.confere].head(40).to_string())


if __name__ == "__main__":
    main()
