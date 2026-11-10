"""Renovação desligada e cenário de aniversários por segmento.

Uso (na raiz):  .venv/bin/python src/calcular_risco_janela_s5.py [--saida PASTA]
Entrada: dados/processados/s5_leo/segmentos.csv e dados/brutos/assinaturas.csv. Saída (padrão dados/saidas/s5_kiril/):
risco_e_janela_segmentos.csv. Não altera dados/brutos.

Definição do cenário (apenas isso; NÃO é previsão nem calendário confirmado de renovação):
  "Aniversário na janela" = assinatura ANUAL ativa cujo dia e mês de início caem entre 01/10/2026 e 29/11/2026
  (extremos incluídos). O histórico disponível não confirma a próxima renovação; o aniversário é só uma aproximação.
  Planos mensais NÃO entram: eles cobram todo mês e a renovação desligada vale "na próxima cobrança".
  Início em 29/02 vale 28/02/2026 (2026 não é bissexto).

Correção do rascunho anterior (R$ 9.832,62 nos Adormecidos): ele (a) contava os 22 mensais com renovação desligada como
se renovassem no aniversário e (b) olhava só 3 anos adiante, perdendo 22 anuais com início há 4 anos ou mais.
Esta versão dá 439 anuais e R$ 9.539,30 mensais equivalentes (proxy líquida) para os Adormecidos.
Proxy líquida = última cobrança aprovada, anual ÷ 12, menos a taxa do método (coluna de segmentos.csv).
"""
import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NOMES = {0: "Adormecidos", 1: "Rotina em casa", 2: "Rua e ritmo", 3: "Novatos"}
INICIO_JANELA, FIM_JANELA = pd.Timestamp("2026-10-01"), pd.Timestamp("2026-11-29")


def aniversario_2026(inicio):
    """Dia e mês de `inicio` em 2026; 29/02 vira 28/02."""
    inicio = pd.Timestamp(inicio)
    try:
        return inicio.replace(year=2026)
    except ValueError:
        return inicio.replace(year=2026, day=28)


def aniversario_na_janela(plano, inicio):
    """True só para plano anual com aniversário de início em [01/10, 29/11] de 2026."""
    if plano != "anual":
        return False
    return INICIO_JANELA <= aniversario_2026(inicio) <= FIM_JANELA


def tabela_risco(seg, ativas):
    """seg: segmentos.csv; ativas: linhas ativas de assinaturas.csv (user_id, inicio, renovacao_automatica)."""
    d = seg.assign(seg_nome=seg.segmento.map(NOMES)).merge(
        ativas[["user_id", "inicio", "renovacao_automatica"]], on="user_id", how="left", validate="1:1", indicator=True)
    assert (d._merge == "both").all()
    d["off"] = d.renovacao_desligada_retrato.astype(bool)
    assert ((d.renovacao_automatica.astype(str).str.lower() == "nao") == d.off).all()
    d["rec"] = d.receita_liquida_mensal_equivalente_proxy
    d["aniv"] = [aniversario_na_janela(p, i) for p, i in zip(d.plano, d.inicio)]
    g = d.groupby("seg_nome")
    t = pd.DataFrame({
        "pagantes": g.size(),
        "renov_desligada_n": g.off.sum(),
        "renov_desligada_pct": g.off.mean().mul(100).round(1),
        "receita_mensal_total": g.rec.sum().round(2),
        "receita_mensal_com_renov_desligada": d[d.off].groupby("seg_nome").rec.sum().round(2),
        "anual_renov_desligada_n": d[d.off & (d.plano == "anual")].groupby("seg_nome").size(),
        "mensal_renov_desligada_n": d[d.off & (d.plano == "mensal")].groupby("seg_nome").size(),
        "anuais_com_aniversario_na_janela_n": d[d.aniv].groupby("seg_nome").size(),
        "anuais_aniversario_na_janela_e_renov_desligada_n": d[d.aniv & d.off].groupby("seg_nome").size(),
        "anuais_aniversario_na_janela_e_renov_desligada_receita": d[d.aniv & d.off].groupby("seg_nome").rec.sum().round(2),
        "sem_treino_90d_pct": g.sem_treino_90d.mean().mul(100).round(1),
    }).reindex(list(NOMES.values()))
    return d, t.fillna(0)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", type=Path, default=ROOT / "dados/saidas/s5_kiril")
    out = ap.parse_args().saida
    out.mkdir(parents=True, exist_ok=True)
    seg = pd.read_csv(ROOT / "dados/processados/s5_leo/segmentos.csv")
    a = pd.read_csv(ROOT / "dados/brutos/assinaturas.csv", parse_dates=["inicio"])
    ativas = a[a.status_atual == "ativa"]
    assert ativas.user_id.is_unique
    d, t = tabela_risco(seg, ativas)
    t.T.to_csv(out / "risco_e_janela_segmentos.csv")
    pd.set_option("display.width", 200)
    print(t.T.to_string())
    print("\nTotal receita:", round(d.rec.sum(), 2), "| total renovações desligadas:", int(d.off.sum()))


if __name__ == "__main__":
    main()
