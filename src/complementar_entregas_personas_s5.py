"""Integra personas de Kiril à frente financeira de John, somente em dados/.

Exige o manifesto da reprodução; não calcula risco, uplift ou fila de contatos.
Autoria dos perfis: Kiril. Clusterização: Leonardo. Integração: John + Codex.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from revisar_personas_kiril_s5 import LEO_SHA, NAMES
from valor_priorizacao_s5 import fmt, md_table

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dados/saidas/s5_integracao_personas"
PROC = ROOT / "dados/processados/s5_integracao_personas"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integrate(value, segments):
    """Cobertura bijetiva; rótulos incompletos ou inconsistentes interrompem o fluxo."""
    for frame in [value, segments]:
        if frame.user_id.isna().any() or not frame.user_id.is_unique:
            raise ValueError("Chave individual ausente ou duplicada")
    if set(value.user_id) != set(segments.user_id):
        raise ValueError("Cobertura dos segmentos difere da carteira financeira")
    if segments.segmento.isna().any() or not segments.segmento.isin(NAMES).all():
        raise ValueError("Rótulo de segmento ausente ou desconhecido")
    labels = value[["user_id"]].merge(segments[["user_id", "segmento"]], on="user_id", validate="one_to_one")
    if "cluster" in value:
        known = value.cluster.notna()
        if not value.loc[known, "cluster"].astype(int).reset_index(drop=True).equals(
                labels.loc[known.to_numpy(), "segmento"].astype(int).reset_index(drop=True)):
            raise ValueError("Cluster financeiro prévio conflita com a integração")
    result = value.copy()
    result["cluster"] = labels.segmento.to_numpy()
    result["persona"] = result.cluster.map(NAMES)
    result["status_persona"] = "rótulo de trabalho S5, revisão técnica delegada por John"
    # Integration must not replace any estimated effect or authorize intervention.
    return result


def coherence(segments):
    g = segments.groupby("segmento")
    p = g.agg(pagantes=("user_id", "size"), dias_ativos_mediana=("dias_ativos_90d", "median"),
              video_mediana=("proporcao_video_90d", "median"), minutos_mediana=("min_por_treino_90d", "median"),
              assinatura_mediana=("tempo_assinatura_dias", "median"),
              frequencia_mediana=("taxa_dias_ativos_90d", "median"),
              seguidores_media=("seguidores_corte", "mean"))
    if set(p.index) != set(NAMES):
        raise ValueError("É necessário conferir os quatro segmentos")
    tests = {
        "Adormecidos: menor mediana de dias ativos": p.dias_ativos_mediana.idxmin() == 0,
        "Rotina em casa: maior proporção mediana de vídeo": p.video_mediana.idxmax() == 1,
        "Rua e ritmo: maior grupo e maior duração mediana, com vídeo minoritário":
            p.pagantes.idxmax() == 2 and p.minutos_mediana.idxmax() == 2 and p.loc[2, "video_mediana"] < .5,
        "Novatos: menor tempo mediano, maior frequência e menor rede média":
            p.assinatura_mediana.idxmin() == 3 and p.frequencia_mediana.idxmax() == 3 and p.seguidores_media.idxmin() == 3,
    }
    if not all(tests.values()):
        raise ValueError("Perfil observado não sustenta a correspondência das personas")
    return p, {k: bool(v) for k, v in tests.items()}


def aggregate(value):
    return value.groupby(["cluster", "persona"]).agg(
        pagantes=("user_id", "size"), mensais=("plano", lambda s: s.eq("mensal").sum()),
        anuais=("plano", lambda s: s.eq("anual").sum()),
        bruto_equivalente_mes=("bruto_equivalente_mes", "sum"),
        liquido_equivalente_mes=("liquido_equivalente_mes", "sum"),
        custo_servir_mes=("custo_servir_mes", "sum"),
        contribuicao_equivalente_mes=("contribuicao_equivalente_mes", "sum"),
        contribuicao_media_mes=("contribuicao_equivalente_mes", "mean"),
        renovacao_desligada=("renovacao_desligada_retrato", "sum")).reset_index()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--segmentos", type=Path, default=ROOT / "dados/saidas/s5_kiril_revisao/segmentos_reproduzidos.csv")
    ap.add_argument("--manifesto", type=Path, default=ROOT / "dados/saidas/s5_kiril_revisao/manifesto.json")
    args = ap.parse_args()
    inputs = {"segmentos": args.segmentos, "manifesto_personas": args.manifesto,
        "base_financeira": ROOT / "dados/processados/s5_valor_priorizacao/base_valor_corte.csv",
        "manifesto_financeiro": ROOT / "dados/processados/s5_valor_priorizacao/manifesto_validacao.json"}
    before = {k: sha(p) for k, p in inputs.items()}
    m = json.loads(args.manifesto.read_text())
    financial = json.loads(inputs["manifesto_financeiro"].read_text())
    if m["pipeline_leo_sha"] != LEO_SHA or m["sha256_segmentos"] != before["segmentos"]:
        raise ValueError("Segmentação não corresponde à reprodução validada")
    context_path = ROOT / "dados/processados/s5_john/base_assinantes_corte.csv"
    if sha(context_path) != m["sha256_contexto"] or sha(context_path) != financial["hashes_entradas"]["base"]:
        raise ValueError("Personas e finanças partem de contextos diferentes")
    for name in ["usuarios", "assinaturas", "pagamentos"]:
        if financial["hashes_entradas"][name] != m["sha256_brutos"][name]:
            raise ValueError("Fontes brutas diferentes entre as frentes")
    segments = pd.read_csv(args.segmentos)
    value = pd.read_csv(inputs["base_financeira"])
    assert len(value) == 14753
    profiles, tests = coherence(segments)
    integrated = integrate(value, segments)
    # Cross-check the proxy and observed context before monetizing any grouping.
    compare = integrated.merge(segments[["user_id", "receita_liquida_mensal_equivalente_proxy", "renovacao_desligada_retrato"]],
        on="user_id", validate="one_to_one", suffixes=("_financeiro", "_segmentos"))
    assert (compare.receita_liquida_mensal_equivalente_proxy_financeiro - compare.receita_liquida_mensal_equivalente_proxy_segmentos).abs().max() < 1e-8
    assert compare.renovacao_desligada_retrato_financeiro.equals(compare.renovacao_desligada_retrato_segmentos)
    assert integrated.uplift.isna().all(), "Esta etapa não deve classificar uma estimativa de efeito como ausente"
    summary = aggregate(integrated)
    assert summary.pagantes.tolist() == [2783, 4315, 4793, 2862]
    for col in ["bruto_equivalente_mes", "liquido_equivalente_mes", "custo_servir_mes", "contribuicao_equivalente_mes"]:
        assert abs(summary[col].sum() - financial[col]) < 1e-6
    PROC.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    integrated.to_csv(PROC / "base_valor_personas_corte.csv", index=False)
    summary.to_csv(OUT / "valor_por_persona.csv", index=False)
    profiles.to_csv(OUT / "coerencia_personas.csv")
    integrated.groupby(["cluster", "persona", "plano", "canal_cobranca"]).agg(
        pagantes=("user_id", "size"), liquido_equivalente_mes=("liquido_equivalente_mes", "sum"),
        contribuicao_equivalente_mes=("contribuicao_equivalente_mes", "sum")).to_csv(OUT / "valor_persona_plano_canal.csv")
    off = integrated[integrated.renovacao_desligada_retrato.eq(1)]
    off.groupby(["cluster", "persona"]).agg(pagantes=("user_id", "size"),
        contribuicao_equivalente_mes=("contribuicao_equivalente_mes", "sum")).to_csv(OUT / "renovacao_desligada_por_persona.csv")
    # Scenario thresholds only: they are not action effects, ROI, or priorities.
    scenarios = []
    for row in summary.itertuples():
        for months in [1, 3, 6]:
            for action, cost in [("push_email_sem_oferta", .01), ("whatsapp_sem_oferta", .4), ("cs_sem_oferta", 18)]:
                scenarios.append({"persona": row.persona, "meses_adicionais_hipoteticos": months,
                    "acao": action, "custo_contato": cost, "ia_hipotese": 0,
                    "uplift_equilibrio_na_media": cost / (months * row.contribuicao_media_mes)})
    scenarios = pd.DataFrame(scenarios)
    scenarios.to_csv(OUT / "limiares_por_persona.csv", index=False)
    nov = segments[segments.segmento.eq(3)]
    long_nov = int(nov.tempo_assinatura_dias.ge(90).sum())
    report = make_report(summary, profiles, scenarios, tests, long_nov)
    (OUT / "complemento_valor_personas.md").write_text(report)
    # Replace only our own delimited block when re-running; retain base reports.
    addendum = "## Complemento com personas\n\n" + report.split("## Valor integrado", 1)[1].split("## Limiares", 1)[0]
    for target in [ROOT / "dados/saidas/s5_valor_priorizacao/John_Valor_Priorizacao_S5.md",
                   ROOT / "dados/saidas/s5_valor_priorizacao/sintese_para_relatorio.md"]:
        text = target.read_text().split("<!-- INICIO COMPLEMENTO PERSONAS -->", 1)[0].rstrip()
        target.write_text(text + "\n\n<!-- INICIO COMPLEMENTO PERSONAS -->\n" + addendum +
                          "\nRelatório integrado completo: dados/saidas/s5_integracao_personas/complemento_valor_personas.md.\n<!-- FIM COMPLEMENTO PERSONAS -->\n")
    diagnostic = ROOT / "dados/saidas/s5_john/sintese_para_relatorio.md"
    text = diagnostic.read_text().split("<!-- INICIO CONTEXTO PERSONAS -->", 1)[0].rstrip()
    diagnostic.write_text(text + "\n\n<!-- INICIO CONTEXTO PERSONAS -->\n## Contexto dos segmentos no corte\n\n"
        "A integração posterior ligou os 14.753 pagantes às quatro personas propostas por Kiril, "
        "sobre os segmentos de Leonardo: Adormecidos (2.783), Rotina em casa (4.315), Rua e ritmo (4.793) e Novatos (2.862). "
        "Esse retrato complementa a descrição da carteira atual; não atribui essas personas a quem já saiu "
        "nem transforma o diagnóstico histórico em causa. Valor integrado e condições de uso: "
        "dados/saidas/s5_integracao_personas/complemento_valor_personas.md.\n<!-- FIM CONTEXTO PERSONAS -->\n")
    manifest = {"hashes_entradas": before, "corte": "2026-09-30", "pipeline_leo_sha": LEO_SHA,
        "pagantes": len(integrated), "clusters_preenchidos": int(integrated.cluster.notna().sum()),
        "personas_preenchidas": int(integrated.persona.notna().sum()), "coerencia": tests,
        "contribuicao_equivalente_mes": float(summary.contribuicao_equivalente_mes.sum()),
        "novatos_assinatura_90_dias_ou_mais": long_nov,
        "uplift_estimado": False, "fila_operacional_aprovada": False}
    assert before == {k: sha(p) for k, p in inputs.items()}
    (PROC / "manifesto_validacao.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(json.dumps({k: v for k, v in manifest.items() if k != "hashes_entradas"}, indent=2, ensure_ascii=False))


def make_report(summary, profiles, scenarios, tests, long_nov):
    table = summary[["persona", "pagantes", "liquido_equivalente_mes", "custo_servir_mes", "contribuicao_equivalente_mes", "renovacao_desligada"]].copy()
    for c in ["liquido_equivalente_mes", "custo_servir_mes", "contribuicao_equivalente_mes"]:
        table[c] = table[c].map(fmt)
    thresholds = scenarios[scenarios.meses_adicionais_hipoteticos.eq(3)].pivot(index="persona", columns="acao", values="uplift_equilibrio_na_media").reindex(NAMES.values())
    thresholds = thresholds.map(lambda v: fmt(v * 100) + " p.p.").reset_index()
    return f"""# Complemento de valor e priorização com personas

John + Codex | Autoria das personas: Kiril | Clusterização: Leonardo | Corte: 30/09/2026

## Compatibilidade

As quatro descrições correspondem às características centrais dos segmentos reproduzidos.
Adormecidos têm a menor mediana de dias ativos; Rotina em casa, maior vídeo mediano;
Rua e ritmo, maior grupo e duração mediana com vídeo minoritário; Novatos, menor tempo
mediano, maior frequência relativa e menor rede média. As quatro verificações passaram.
Nomes descrevem tendências de grupos: vídeo não comprova localização em casa e {long_nov}
dos 2.862 Novatos ({fmt(long_nov / 2862 * 100, 1)}%) já têm 90 dias ou mais de assinatura.
Hipóteses de motivação e resposta a ações não foram validadas pela segmentação.

## Valor integrado

Integração um para um, sem perdas ou duplicações: 14.753 pagantes com segmento e persona.
O arquivo integrado tem nome próprio e não substitui a base financeira original.
As proxies foram conciliadas individualmente entre as duas frentes antes da agregação.

{md_table(table, ['Persona','Pagantes','Proxy líquida/mês R$','Custo de servir/mês R$','Contribuição/mês R$','Renovação desligada'])}

Total: R$ {fmt(summary.liquido_equivalente_mes.sum())} de proxy líquida menos
R$ {fmt(summary.custo_servir_mes.sum())} de custo de servir =
R$ {fmt(summary.contribuicao_equivalente_mes.sum())} de contribuição equivalente mensal.
Valores aproximados a partir da última cobrança aprovada, anual /12; sem estornos/chargebacks.
Não representam LTV, valor causal de retenção, lucro contábil ou receita futura assegurada.

Rua e ritmo concentra a maior contribuição total. Adormecidos concentra o sinal de renovação
desligada. Nenhum dos dois fatos, isoladamente, define prioridade ou benefício de contato.
A base integrada mantém uplift ausente e a ação pendente; não foi criada fila de CRM.

## Limiares de cenário

H=3 meses pagos adicionais assumidos, sem oferta e IA=zero como limite inferior de custo.
Cada limiar usa a contribuição média da persona; não é o limiar de cada pessoa.

{md_table(thresholds, ['Persona','CS','Push + e-mail','WhatsApp'])}

As médias escondem diferenças de plano/canal e tarifa. Não transferir o efeito do experimento
de push/e-mail para WhatsApp ou CS. Meses adicionais são hipótese após o período já pago.
As tabelas locais preservam H=1/3/6; descontos seguem os cenários originais por plano/canal.

## Dependências e uso

Concluídos: vínculo segmento–persona; valor por persona e por plano/canal; contribuição do
subconjunto com renovação desligada; limiares econômicos descritivos; complemento à síntese.
Briefings condicionais por persona constam do documento público de integração.
Ainda necessários para priorização final: risco e elegibilidade de renovação, efeito incremental,
horizonte de valor e custo real de IA. Nenhuma pessoa foi classificada como persuadível.
Para churn histórico por segmento, reconstruir características nos cortes anteriores; agrupar
somente sobreviventes de setembro não descreve quem já saiu.

Referências: docs/entregas/personas_s5.md; docs/entregas/conferencia_personas_kiril_s5.md;
docs/entregas/integracao_personas_s5.md. Fontes e hashes no manifesto local da integração.
"""


if __name__ == "__main__":
    main()
