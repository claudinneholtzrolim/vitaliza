"""Checagens de qualidade da base de clusterização da S5 (frente de Claudinne).

Lê as bases geradas por src/preparar_diagnostico_s5.py e não altera nada em dados/brutos/.

Uso, na raiz do repositório:
    .venv/bin/python src/checagens_qualidade_s5.py

Entradas:  dados/processados/s5_john/base_clusterizacao.csv
           dados/processados/s5_john/base_assinantes_corte.csv
Saída:     dados/processados/s5_claudinne/qualidade_flags.csv (uma linha por assinante, fora do Git)
           e o resumo das cinco dimensões impresso na tela.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ENTRADA = ROOT / "dados/processados/s5_john"
SAIDA = ROOT / "dados/processados/s5_claudinne"


def carregar():
    clus = pd.read_csv(ENTRADA / "base_clusterizacao.csv")
    base = pd.read_csv(ENTRADA / "base_assinantes_corte.csv")
    return clus, base


def marcar(df):
    """Marcações por assinante: características do dado e casos para revisão."""
    t = df.tempo_assinatura_dias
    mpt90 = df.minutos_90d / df.treinos_90d.replace(0, np.nan)
    f = pd.DataFrame({"user_id": df.user_id})
    f["sem_treino_90d"] = (df.treinos_90d == 0).astype(int)
    f["sem_treino_2026"] = df.sem_treino_observado_2026
    f["onboarding_nivel_vazio"] = df.nivel.isna().astype(int)
    f["onboarding_dias_planejados_vazio"] = df.dias_planejados_semana.isna().astype(int)
    f["atividade_antes_do_inicio"] = (
        (t < 90) & ((df.dias_ativos_90d > t + 1)
                    | (df.dias_desde_ultimo_treino_2026 > t + 1)
                    | ((t < 30) & (df.treinos_90d > df.treinos_30d)))
    ).astype(int)
    f["treino_longo_300min"] = (mpt90 > 300).astype(int)
    f["volume_extremo_40treinos_30d"] = (df.treinos_30d >= 40).astype(int)
    f["minutos_30d_acima_p99"] = (df.minutos_30d > df.minutos_30d.quantile(0.99)).astype(int)
    f["minutos_90d_acima_p99"] = (df.minutos_90d > df.minutos_90d.quantile(0.99)).astype(int)
    f["revisar"] = f[["atividade_antes_do_inicio", "treino_longo_300min",
                      "volume_extremo_40treinos_30d"]].max(axis=1)
    return f


def regras_clusterizacao(df):
    """Regras lógicas entre colunas. Esperado: 0 em todas."""
    return {
        "treinos_30d > treinos_90d": (df.treinos_30d > df.treinos_90d).sum(),
        "minutos_30d > minutos_90d": (df.minutos_30d > df.minutos_90d + 0.05).sum(),
        "dias_ativos_30d > dias_ativos_90d": (df.dias_ativos_30d > df.dias_ativos_90d).sum(),
        "dias_ativos_30d > 30 ou dias_ativos_90d > 90": ((df.dias_ativos_30d > 30) | (df.dias_ativos_90d > 90)).sum(),
        "dias_ativos_30d > treinos_30d": (df.dias_ativos_30d > df.treinos_30d).sum(),
        "treinos = 0 sem minutos = 0 (ou o inverso)": ((df.treinos_30d == 0) != (df.minutos_30d == 0)).sum(),
        "proporcao_video vazia com treino em 90d": (df.proporcao_video_90d.isna() & (df.treinos_90d > 0)).sum(),
        "dias_desde_ultimo vazio != sem_treino_observado": (df.dias_desde_ultimo_treino_2026.isna() != (df.sem_treino_observado_2026 == 1)).sum(),
        "último treino < 30 dias e treinos_30d = 0": ((df.dias_desde_ultimo_treino_2026 < 30) & (df.treinos_30d == 0)).sum(),
        "último treino > 30 dias e treinos_30d > 0": ((df.dias_desde_ultimo_treino_2026 >= 30.01) & (df.treinos_30d > 0)).sum(),
        "variação > treinos_30d": (df.variacao_treinos_tratados_30d > df.treinos_30d).sum(),
        "mês anterior > treinos_90d - treinos_30d": ((df.treinos_30d - df.variacao_treinos_tratados_30d) > (df.treinos_90d - df.treinos_30d)).sum(),
        "user_id duplicado": df.user_id.duplicated().sum(),
        "user_id fora do padrão u_xxxxxxxx": (~df.user_id.str.match(r"^u_[0-9a-f]{8}$")).sum(),
    }


def recalculos_base(b):
    """Fórmulas do dicionário recalculadas na base complementar. Esperado: 0."""
    taxa = 1 - b.receita_liquida_mensal_equivalente_proxy / b.receita_mensal_equivalente_proxy
    taxa_esperada = b.canal_cobranca.map({"app_store": 0.15, "google_play": 0.15,
                                          "web_cartao": 0.035, "web_pix": 0.0099})
    s = b.sistema.str.lower()
    gap = b.tempo_cadastro_dias - b.tempo_assinatura_dias
    return {
        "variacao = treinos_30d - anteriores": (b.variacao_treinos_tratados_30d != b.treinos_30d - b.treinos_30d_anteriores).sum(),
        "vídeo + ar livre = treinos (30d e 90d)": ((b.treinos_video_30d + b.treinos_ar_livre_30d != b.treinos_30d)
                                                    | (b.treinos_video_90d + b.treinos_ar_livre_90d != b.treinos_90d)).sum(),
        "proporcao_video = vídeo / treinos (90d)": ((b.proporcao_video_90d - b.treinos_video_90d / b.treinos_90d.replace(0, np.nan)).abs() > 1e-9).sum(),
        "conciliação = BI set - treinos_30d": (b.atividades_bi_set - b.treinos_30d != b.bi_treinos_set_menos_detalhe).sum(),
        "receita mensal = 39,90; anual = cobrança / 12": (((b.plano == "mensal") & (b.receita_mensal_equivalente_proxy.round(2) != 39.90))
                                                          | ((b.plano == "anual") & ((b.receita_mensal_equivalente_proxy - b.ultima_cobranca_aprovada_reais / 12).abs() > 0.01))).sum(),
        "taxa implícita = taxa do canal (enunciado)": ((taxa - taxa_esperada).abs() > 1e-4).sum(),
        "App Store só em iOS; Google Play só em Android": (((b.canal_cobranca == "app_store") & (s != "ios"))
                                                         | ((b.canal_cobranca == "google_play") & (s != "android"))).sum(),
        "renovacao_divergente vazia = estado ausente nos eventos": (b.renovacao_divergente.isna() != b.renovacao_desligada_eventos.isna()).sum(),
        "cadastro fora de 6 a 7 dias antes do início pago": (~gap.between(6, 7)).sum(),
    }


def achados_novos(b):
    return {
        "sistema com grafia fora do padrão (minúsculas)": (b.sistema != b.sistema.str.lower()).sum(),
        "anual R$ 239,90 com mais de 365 dias de assinatura": ((b.ultima_cobranca_aprovada_reais == 239.9) & (b.tempo_assinatura_dias > 365)).sum(),
        "tickets pendentes > tickets abertos em 90d (esperado)": (b.tickets_pendentes_corte > b.tickets_90d).sum(),
    }


def ponte_valor(b):
    bruto = b.receita_mensal_equivalente_proxy.sum()
    liquido = b.receita_liquida_mensal_equivalente_proxy.sum()
    servir = 4.20 * len(b)
    return {"receita bruta equivalente": bruto, "(-) taxas": liquido - bruto,
            "receita após taxas": liquido, "(-) custo de servir R$ 4,20": -servir,
            "contribuição aproximada": liquido - servir}


def imprimir(titulo, d, fmt="{:>10}"):
    print(f"\n{titulo}")
    for k, v in d.items():
        print(f"  {k:60s} " + fmt.format(v))


def main():
    clus, base = carregar()
    assert set(clus.user_id) == set(base.user_id), "as duas bases precisam ter os mesmos user_id"
    print(f"Linhas: base de clusterização {len(clus)}; base complementar {len(base)}")

    flags = marcar(clus)
    SAIDA.mkdir(parents=True, exist_ok=True)
    flags.to_csv(SAIDA / "qualidade_flags.csv", index=False)

    imprimir("Consistência: regras na base de clusterização (esperado 0)", regras_clusterizacao(clus))
    imprimir("Consistência: fórmulas recalculadas na base complementar (esperado 0)", recalculos_base(base))
    imprimir("Achados novos", achados_novos(base))
    print("\nCompletude: vazios por coluna")
    print(clus.isna().sum()[lambda s: s > 0].to_string())
    imprimir("Marcações por assinante", flags.drop(columns="user_id").sum().to_dict())
    imprimir("Ponte de valor (equivalente mensal, R$)", ponte_valor(base), "{:>14,.2f}")
    print("\nPonte de filtros: 14.753 pagantes; "
          f"{int(flags.sem_treino_90d.sum())} sem treino em 90 dias; "
          f"{int((flags.sem_treino_90d == 0).sum())} para o algoritmo")
    print(f"\nMarcações salvas em {SAIDA.relative_to(ROOT)}/qualidade_flags.csv (fora do Git)")


if __name__ == "__main__":
    main()
