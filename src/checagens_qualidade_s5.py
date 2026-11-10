"""Checagens de qualidade da base de clusterização da S5 (frente de Claudinne).

Lê as bases geradas por src/preparar_diagnostico_s5.py e não altera nada em dados/brutos/.

Uso, na raiz do repositório:
    .venv/bin/python src/checagens_qualidade_s5.py

Entradas:  dados/processados/s5_john/base_clusterizacao.csv
           dados/processados/s5_john/base_assinantes_corte.csv
Saída:     dados/processados/s5_claudinne/qualidade_flags.csv (uma linha por assinante, fora do Git)
           resumo agregado impresso na tela e salvo em resumo_qualidade.json.

Autoria original: Claudinne — Grupo 01.
Revisão técnica: Codex a pedido de John, 07/11/2026.
Não remove assinantes nem substitui a auditoria dos arquivos brutos.
"""
from pathlib import Path
import hashlib
import json

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
    f["sinal_atividade_anterior_assinatura_paga"] = (
        (t < 90) & ((df.dias_ativos_90d > t + 1)
                    | (df.dias_desde_ultimo_treino_2026 > t + 1)
                    | ((t < 30) & (df.treinos_90d > df.treinos_30d)))
    ).astype(int)
    f["treino_longo_300min"] = (mpt90 > 300).astype(int)
    f["volume_extremo_40treinos_30d"] = (df.treinos_30d >= 40).astype(int)
    f["minutos_30d_acima_p99"] = (df.minutos_30d > df.minutos_30d.quantile(0.99)).astype(int)
    f["minutos_90d_acima_p99"] = (df.minutos_90d > df.minutos_90d.quantile(0.99)).astype(int)
    # Treino anterior ao pagamento é permitido no freemium; não é erro.
    f["revisar"] = f[["treino_longo_300min",
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
    return {
        "variacao = treinos_30d - anteriores": (b.variacao_treinos_tratados_30d != b.treinos_30d - b.treinos_30d_anteriores).sum(),
        "vídeo + ar livre = treinos (30d e 90d)": ((b.treinos_video_30d + b.treinos_ar_livre_30d != b.treinos_30d)
                                                    | (b.treinos_video_90d + b.treinos_ar_livre_90d != b.treinos_90d)).sum(),
        "proporcao_video = vídeo / treinos (90d)": ((b.proporcao_video_90d - b.treinos_video_90d / b.treinos_90d.replace(0, np.nan)).abs() > 1e-9).sum(),
        "conciliação = BI set - treinos_30d": (b.atividades_bi_set - b.treinos_30d != b.bi_treinos_set_menos_detalhe).sum(),
        "proxy mensal = última cobrança / divisor do plano": (
            (b.receita_mensal_equivalente_proxy - b.ultima_cobranca_aprovada_reais
             / b.plano.map({"mensal": 1, "anual": 12})).abs() > 1e-9).sum(),
        "taxa implícita = taxa do canal (enunciado)": ((taxa - taxa_esperada).abs() > 1e-4).sum(),
        "App Store só em iOS; Google Play só em Android": (((b.canal_cobranca == "app_store") & (s != "ios"))
                                                         | ((b.canal_cobranca == "google_play") & (s != "android"))).sum(),
        "renovacao_divergente vazia = estado ausente nos eventos": (b.renovacao_divergente.isna() != b.renovacao_desligada_eventos.isna()).sum(),
    }


def achados_novos(b):
    return {
        "cadastro fora de 6 a 7 dias antes do início pago (descritivo)": (~(b.tempo_cadastro_dias - b.tempo_assinatura_dias).between(6, 7)).sum(),
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


def validar_entradas(clus, base):
    """Interrompe antes de salvar: chaves, cobertura, domínios e valores finitos."""
    if len(clus) != 14753 or len(base) != 14753:
        raise ValueError("Esperados 14.753 pagantes em cada entrada nesta versão do case")
    for df in (clus, base):
        ids = df.user_id.astype("string")
        if ids.isna().any() or not ids.str.fullmatch(r"u_[0-9a-f]{8}").all() or ids.duplicated().any():
            raise ValueError("Chave ausente, inválida ou duplicada")
    if set(clus.user_id) != set(base.user_id):
        raise ValueError("Cobertura das duas bases diverge")
    if not base.plano.isin(["mensal", "anual"]).all():
        raise ValueError("Plano ausente ou desconhecido")
    if not base.canal_cobranca.isin(["app_store", "google_play", "web_cartao", "web_pix"]).all():
        raise ValueError("Canal ausente ou desconhecido")
    for df in (clus, base):
        required = ["treinos_30d", "treinos_90d", "minutos_30d", "minutos_90d",
                    "dias_ativos_30d", "dias_ativos_90d", "tempo_assinatura_dias"]
        if df[required].isna().any().any() or not np.isfinite(df[required]).all().all() or (df[required] < 0).any().any():
            raise ValueError("Medida obrigatória ausente, não finita ou negativa")
    for col in ["ultima_cobranca_aprovada_reais", "receita_mensal_equivalente_proxy",
                "receita_liquida_mensal_equivalente_proxy"]:
        if base[col].isna().any() or not np.isfinite(base[col]).all() or (base[col] <= 0).any():
            raise ValueError("Valor financeiro ausente, não finito ou não positivo")
    if not clus.sem_treino_observado_2026.isin([0, 1]).all():
        raise ValueError("Flag sem treino inválida")
    for df in (clus, base):
        prop = df.proporcao_video_90d
        if (prop.notna() & ~prop.between(0, 1)).any():
            raise ValueError("Proporção fora de 0 a 1")
    # Compara as variáveis compartilhadas por chave, sem depender da ordem das linhas.
    shared = sorted(set(clus.columns) & set(base.columns) - {"user_id"})
    try:
        pd.testing.assert_frame_equal(clus.set_index("user_id")[shared].sort_index(),
                                      base.set_index("user_id")[shared].sort_index(),
                                      check_dtype=False, check_exact=True)
    except AssertionError as exc:
        raise ValueError("Variáveis compartilhadas divergem entre as bases") from exc


def main():
    clus, base = carregar()
    validar_entradas(clus, base)
    regras = regras_clusterizacao(clus)
    formulas = recalculos_base(base)
    # Uma violação impede produzir uma nova saída que pareça aprovada.
    if any(regras.values()) or any(formulas.values()):
        imprimir("Violações na clusterização", regras)
        imprimir("Violações na base complementar", formulas)
        raise ValueError("Há inconsistências: nenhuma nova saída foi gravada")
    flags = marcar(clus)
    summary = {
        "linhas_entrada_clusterizacao": len(clus), "linhas_entrada_complementar": len(base),
        "linhas_saida": len(flags), "linhas_excluidas": 0,
        "regras_clusterizacao": regras, "formulas_base": formulas,
        "achados_descritivos": achados_novos(base),
        "ausencias_clusterizacao": clus.isna().sum().to_dict(),
        "flags": flags.drop(columns="user_id").sum().to_dict(),
        "ponte_valor": ponte_valor(base),
        "sha256_entradas": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in [ENTRADA / "base_clusterizacao.csv", ENTRADA / "base_assinantes_corte.csv"]},
    }
    SAIDA.mkdir(parents=True, exist_ok=True)
    flags.to_csv(SAIDA / "qualidade_flags.csv", index=False)
    (SAIDA / "resumo_qualidade.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, default=lambda v: v.item()) + "\n")
    imprimir("Regras da clusterização (esperado 0)", regras)
    imprimir("Fórmulas complementares (esperado 0)", formulas)
    imprimir("Características e achados para investigação", summary["achados_descritivos"])
    imprimir("Ausências na clusterização", summary["ausencias_clusterizacao"])
    imprimir("Marcações por assinante", summary["flags"])
    imprimir("Ponte de valor (proxy equivalente mensal, R$)", summary["ponte_valor"], "{:>14,.2f}")
    print(f"\nPonte: {len(clus)} pagantes na entrada → {len(flags)} na saída; zero excluídos.")
    print("Sem treino é característica observada; todos continuam disponíveis à segmentação.")
    print(f"Saídas locais em {SAIDA.relative_to(ROOT)}; limiares exploratórios não comprovam erro.")


if __name__ == "__main__":
    main()
