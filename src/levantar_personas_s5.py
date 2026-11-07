"""Levantamento descritivo por segmento para as personas da S5. Só lê dados/brutos e segmentos.csv.

Uso (na raiz):  .venv/bin/python src/levantar_personas_s5.py [--saida PASTA]
Entrada: dados/processados/s5_leo/segmentos.csv (gerado por src/clusterizacao_s5.py --k 4).
Saída (padrão dados/saidas/s5_kiril/): CSVs por segmento. Não altera nada em dados/brutos.

Idade: referência 01/10/2026 (limite exclusivo), dias ÷ 365,25; datas ausentes ficam fora da mediana. NÃO se descartam
idades implausíveis (a idade mediana de Rua e ritmo dá 47,1, como na revisão publicada); 133 pagantes têm idade fora de
14 a 90 anos e estão incluídos. Para descartá-los, filtre `idade` antes da mediana (o resultado vira 47,0).
Sexo: F/Fem/feminino e M/Masc/masculino; o resto fica como "outro/não informado" (não é redistribuído).
Sistema, canal e relógio: texto normalizado em minúsculas. Motivações: regras em src/personas_regras_s5.py.
"""
import argparse
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from personas_regras_s5 import NAO_CLASSIFICADO, estado_objetivo, meta_com_data, norm, tema_principal  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BRUTOS = ROOT / "dados/brutos"
CORTE = pd.Timestamp("2026-10-01")
NOMES = {0: "Adormecidos", 1: "Rotina em casa", 2: "Rua e ritmo", 3: "Novatos"}
ORDEM = list(NOMES.values())
SEXO = {"f": "feminino", "fem": "feminino", "feminino": "feminino", "m": "masculino", "masc": "masculino", "masculino": "masculino"}


def dias_num(x):
    if pd.isna(x):
        return pd.NA
    m = re.search(r"\d+", str(x))
    return int(m.group()) if m and 1 <= int(m.group()) <= 7 else pd.NA


def pct(s):
    return round(100 * s.mean(), 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", type=Path, default=ROOT / "dados/saidas/s5_kiril")
    out = ap.parse_args().saida
    out.mkdir(parents=True, exist_ok=True)

    seg = pd.read_csv(ROOT / "dados/processados/s5_leo/segmentos.csv")
    seg["segmento_nome"] = seg["segmento"].map(NOMES)
    assert seg["user_id"].is_unique
    ponte = [("pagantes em segmentos.csv", len(seg))]

    # cadastro
    u = pd.read_csv(BRUTOS / "usuarios.csv")
    d = seg.merge(u.drop(columns=["email", "cidade"]), on="user_id", how="left", validate="1:1", indicator="_m_usuarios")
    ponte.append(("encontrados em usuarios.csv", int((d["_m_usuarios"] == "both").sum())))
    ponte.append(("com data de nascimento preenchida", int(d["data_nascimento"].notna().sum())))
    nasc = pd.to_datetime(d["data_nascimento"], errors="coerce")
    d["idade"] = ((CORTE - nasc).dt.days / 365.25).where(nasc.notna())
    d["sexo_n"] = d["sexo"].map(lambda x: SEXO.get(norm(x), "outro/não informado") if pd.notna(x) else "outro/não informado")
    d["faixa_idade"] = pd.cut(d["idade"], [0, 24, 34, 44, 54, 200], labels=["até 24", "25-34", "35-44", "45-54", "55+"])
    d["sudeste"] = d["uf"].map(lambda x: norm(x).upper() if pd.notna(x) else "NI").isin({"SP", "RJ", "MG", "ES"})
    d["relogio_tipo"] = d["relogio_conectado"].map(norm)
    d["relogio"] = ~d["relogio_tipo"].isin({"nenhum", "nan", "", "none"})
    d["sistema_n"] = d["sistema"].map(norm)
    d["canal_aq_n"] = d["canal_aquisicao"].map(norm)

    # onboarding
    ob = pd.read_csv(BRUTOS / "onboarding.csv").sort_values("respondido_em").drop_duplicates("user_id", keep="last")
    d = d.merge(ob[["user_id", "objetivo_texto", "dias_por_semana"]].rename(columns={"dias_por_semana": "dias_texto"}),
                on="user_id", how="left", indicator="_m_ob", validate="1:1")
    ponte.append(("encontrados em onboarding.csv", int((d["_m_ob"] == "both").sum())))
    d["obj_estado"] = d["objetivo_texto"].map(estado_objetivo)
    com = d["obj_estado"] == "com conteúdo"
    d["_obj_norm"] = d["objetivo_texto"].map(lambda x: norm(x) if pd.notna(x) else "")
    d["tema_obj"] = [tema_principal(t) if c else None for t, c in zip(d["_obj_norm"], com)]
    d["meta_com_data"] = com & d["_obj_norm"].map(meta_com_data)
    d["dias_plan"] = pd.to_numeric(d["dias_texto"].map(dias_num), errors="coerce")

    # campanha de agosto
    c = pd.read_csv(BRUTOS / "campanha_ago26.csv")
    d = d.merge(c[["user_id", "grupo", "abriu_push", "abriu_email", "clicou"]], on="user_id", how="left")
    d["na_campanha"] = d["grupo"].notna()
    ponte.append(("estavam na campanha de 10/08", int(d["na_campanha"].sum())))

    g = d.groupby("segmento_nome")
    perfil = pd.DataFrame({
        "assinantes": g.size(),
        "idade_mediana": g["idade"].median().round(1),
        "idade_sem_data_pct": g["idade"].apply(lambda s: round(100 * s.isna().mean(), 1)),
        "feminino_pct": g["sexo_n"].apply(lambda s: pct(s == "feminino")),
        "masculino_pct": g["sexo_n"].apply(lambda s: pct(s == "masculino")),
        "sudeste_pct": g["sudeste"].apply(pct),
        "ios_pct": g["sistema_n"].apply(lambda s: pct(s == "ios")),
        "android_pct": g["sistema_n"].apply(lambda s: pct(s == "android")),
        "relogio_conectado_pct": g["relogio"].apply(pct),
        "iniciante_pct": g["nivel"].apply(lambda s: pct(s.map(norm) == "iniciante")),
        "nivel_nao_informado_pct": g["nivel"].apply(lambda s: round(100 * s.isna().mean(), 1)),
        "dias_planejados_mediana": g["dias_plan"].median(),
        "dias_planejados_nao_extraido_pct": g["dias_plan"].apply(lambda s: round(100 * s.isna().mean(), 1)),
        "objetivo_nulo_pct": g["obj_estado"].apply(lambda s: pct(s == "nulo")),
        "objetivo_sem_conteudo_pct": g["obj_estado"].apply(lambda s: pct(s == "sem conteúdo")),
        "objetivo_com_conteudo_pct": g["obj_estado"].apply(lambda s: pct(s == "com conteúdo")),
        "na_campanha_pct": g["na_campanha"].apply(pct),
    }).loc[ORDEM]
    perfil.T.to_csv(out / "perfil_demografico_segmentos.csv")
    pd.crosstab(d["segmento_nome"], d["faixa_idade"], normalize="index").mul(100).round(1).loc[ORDEM].to_csv(out / "faixa_idade_segmentos.csv")
    pd.crosstab(d["segmento_nome"], d["canal_aq_n"], normalize="index").mul(100).round(1).loc[ORDEM].to_csv(out / "canal_aquisicao_segmentos.csv")
    pd.crosstab(d["segmento_nome"], d["relogio_tipo"], normalize="index").mul(100).round(1).loc[ORDEM].to_csv(out / "relogio_segmentos.csv")
    pd.crosstab(d["segmento_nome"], d["nivel"].fillna("não informado").map(norm), normalize="index").mul(100).round(1).loc[ORDEM].to_csv(out / "nivel_segmentos.csv")

    base_c = d[com]
    temas = pd.crosstab(base_c["segmento_nome"], base_c["tema_obj"], normalize="index").mul(100).round(1)
    temas["meta_com_data_pct"] = base_c.groupby("segmento_nome")["meta_com_data"].apply(pct)
    temas["n_com_conteudo"] = base_c.groupby("segmento_nome").size()
    temas.loc[ORDEM].to_csv(out / "temas_objetivo_segmentos.csv")
    base_c.loc[base_c["tema_obj"] == NAO_CLASSIFICADO, "_obj_norm"].value_counts().head(15).to_csv(out / "objetivo_nao_classificado_top.csv", header=["n"])
    base_c["_obj_norm"].value_counts().head(40).to_csv(out / "respostas_objetivo_mais_comuns.csv", header=["n"])

    rec = d[d["na_campanha"] & (d["grupo"] != "controle")]
    camp = pd.DataFrame({
        "na_campanha": d[d["na_campanha"]].groupby("segmento_nome").size(),
        "receberam_mensagem": rec.groupby("segmento_nome").size(),
        "abriu_push_pct": rec.groupby("segmento_nome")["abriu_push"].apply(pct),
        "abriu_email_pct": rec.groupby("segmento_nome")["abriu_email"].apply(pct),
        "clicou_pct": rec.groupby("segmento_nome")["clicou"].apply(pct),
    }).loc[ORDEM]
    camp.to_csv(out / "campanha_engajamento_segmentos.csv")
    pd.crosstab(d.loc[d["na_campanha"], "segmento_nome"], d.loc[d["na_campanha"], "grupo"]).loc[ORDEM].to_csv(out / "campanha_grupos_segmentos.csv")
    rec.groupby(["segmento_nome", "grupo"])["clicou"].mean().mul(100).round(1).unstack().loc[ORDEM].to_csv(out / "campanha_clique_por_mensagem.csv")
    rec.groupby(["segmento_nome", "grupo"]).size().unstack().loc[ORDEM].to_csv(out / "campanha_n_por_mensagem.csv")
    rec.groupby(["segmento_nome", "grupo"])["clicou"].sum().unstack().loc[ORDEM].to_csv(out / "campanha_cliques_por_mensagem.csv")
    pd.DataFrame(ponte, columns=["etapa", "linhas"]).to_csv(out / "ponte_linhas_personas.csv", index=False)

    pd.set_option("display.width", 220, "display.max_columns", 50)
    print("PONTE", ponte)
    print(perfil.T.to_string())
    print(temas.loc[ORDEM].to_string())
    print(camp.to_string())


if __name__ == "__main__":
    main()
