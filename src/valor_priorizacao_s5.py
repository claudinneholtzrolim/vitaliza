"""Frente financeira assumida por John em 03/11/2026. Não estima uplift ou LTV.

Executar da raiz: .venv/bin/python src/valor_priorizacao_s5.py
Bases individuais e saídas permanecem em dados/, fora do repositório público.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path

import pandas as pd

from preparar_diagnostico_s5 import CUT, timestamps, money_cents

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dados/saidas/s5_valor_priorizacao"
PROC = ROOT / "dados/processados/s5_valor_priorizacao"
FEES = {"app_store": .15, "google_play": .15, "web_cartao": .035, "web_pix": .0099}
METHOD = {"app_store": "app_store", "google_play": "google_play", "cartao": "web_cartao", "pix_automatico": "web_pix"}
SERVE = 4.20


def contribution(gross: float, plan: str, channel: str) -> float:
    if plan not in {"mensal", "anual"}:
        raise ValueError("Plano não documentado")
    if gross <= 0:
        raise ValueError("Cobrança deve ser positiva")
    return gross / (12 if plan == "anual" else 1) * (1 - FEES[channel]) - SERVE


def incremental_value(uplift: float, months: float, margin: float,
                      contact: float, offer: float = 0, ai: float = 0) -> float:
    """Cenário de meses pagos adicionais condicionais à retenção, não previsão.

    Oferta é custo esperado por pessoa contatada, incluindo quem ficaria sem ação.
    Meses devem ser adicionais ao contrafactual, após o período já pago.
    """
    if not -1 <= uplift <= 1 or min(months, contact, offer, ai) < 0:
        raise ValueError("Parâmetros fora do domínio")
    return uplift * months * margin - contact - offer - ai


def max_offers(budget: float, fixed: float, ai_reserve: float, unit: float) -> int:
    if min(budget, fixed, ai_reserve) < 0 or unit <= 0:
        raise ValueError("Custo inválido")
    remaining = max(Decimal(str(budget)) - Decimal(str(fixed)) - Decimal(str(ai_reserve)), Decimal(0))
    return int((remaining / Decimal(str(unit))).to_integral_value(rounding=ROUND_FLOOR))


def fmt(v, digits=2):
    # Eliminate binary floating noise only for display, then apply financial rounding.
    displayed = Decimal(str(round(float(v), 8))).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)
    return f"{displayed:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def md_table(df, labels=None):
    labels = labels or list(df.columns)
    lines = ["| " + " | ".join(labels) + " |", "| " + " | ".join(["---"] * len(labels)) + " |"]
    lines += ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False, name=None)]
    return "\n".join(lines)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PROC.mkdir(parents=True, exist_ok=True)
    paths = {"base": ROOT / "dados/processados/s5_john/base_assinantes_corte.csv",
             "usuarios": ROOT / "dados/brutos/usuarios.csv",
             "assinaturas": ROOT / "dados/brutos/assinaturas.csv",
             "pagamentos": ROOT / "dados/brutos/pagamentos.csv"}
    hashes = {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in paths.items()}
    b = pd.read_csv(paths["base"])
    u = pd.read_csv(paths["usuarios"])
    subs = pd.read_csv(paths["assinaturas"])
    pay = pd.read_csv(paths["pagamentos"], low_memory=False)
    filters = []
    def step(source, name, frame):
        filters.append({"fonte": source, "etapa": name, "linhas": len(frame)})
    step("pagamentos", "bruto", pay)
    tests = set(u.loc[u.email.str.strip().str.lower().str.endswith("@vitaliza.com.br", na=False), "user_id"])
    pay["ts"] = timestamps(pay.data_hora)
    pay["centavos"] = money_cents(pay.valor)
    assert pay.ts.notna().all() and pay.centavos.notna().all()
    pay = pay[~pay.user_id.isin(tests)].copy(); step("pagamentos", "sem testes", pay)
    pay = pay[pay.ts.lt(CUT)].copy(); step("pagamentos", "anterior a 01/10 em Brasília", pay)
    pay = pay[pay.status.eq("aprovado")].copy(); step("pagamentos", "somente aprovados", pay)
    duplicates = int(pay.duplicated(["user_id", "ts", "centavos"]).sum())
    pay = pay.drop_duplicates(["user_id", "ts", "centavos"]); step("pagamentos", "sem cobranças duplicadas", pay)
    last = pay.sort_values(["ts", "pagamento_id"]).drop_duplicates("user_id", keep="last")
    step("pagamentos", "última cobrança por conta", last)
    assert b.user_id.is_unique and len(b) == 14753 and not b.user_id.isin(tests).any()
    expected = subs[subs.status_atual.eq("ativa") & ~subs.user_id.isin(tests)]
    assert set(expected.user_id) == set(b.user_id)
    step("base", "pagantes preparados e conciliados ao retrato", b)
    b = b.merge(last[["user_id", "pagamento_id", "ts", "centavos", "metodo"]], on="user_id", how="left", validate="one_to_one")
    assert b.centavos.notna().all()
    assert b.metodo.map(METHOD).eq(b.canal_cobranca).all(), "Canal da cobrança difere do plano"
    gross = b.centavos.astype(float) / 100
    assert (gross - b.ultima_cobranca_aprovada_reais).abs().max() < 1e-8
    b["bruto_equivalente_mes"] = gross / b.plano.map({"mensal": 1, "anual": 12})
    b["taxa_canal"] = b.canal_cobranca.map(FEES)
    b["liquido_equivalente_mes"] = b.bruto_equivalente_mes * (1-b.taxa_canal)
    assert (b.liquido_equivalente_mes-b.receita_liquida_mensal_equivalente_proxy).abs().max() < 1e-8
    b["contribuicao_equivalente_mes"] = b.liquido_equivalente_mes-SERVE
    b["custo_servir_mes"] = SERVE
    b["faixa_treinos_30d"] = pd.cut(b.treinos_30d, [-1,0,3,7,float("inf")], labels=["0", "1 a 3", "4 a 7", "8 ou mais"]).astype(str)
    b["cluster"] = pd.NA
    b["uplift"] = pd.NA
    b["acao_recomendada"] = "pendente de efeito incremental e elegibilidade"
    b.to_csv(PROC / "base_valor_corte.csv", index=False)
    cols = {"pagantes": ("user_id", "size"), "bruto_equivalente_mes": ("bruto_equivalente_mes", "sum"),
            "liquido_equivalente_mes": ("liquido_equivalente_mes", "sum"),
            "contribuicao_equivalente_mes": ("contribuicao_equivalente_mes", "sum"),
            "contribuicao_media_mes": ("contribuicao_equivalente_mes", "mean")}
    cells = b.groupby(["plano", "canal_cobranca"]).agg(**cols).reset_index()
    cells["participacao_base_pct"] = 100*cells.pagantes/len(b)
    assert cells.pagantes.sum() == 14753
    assert abs(cells.contribuicao_equivalente_mes.sum()-b.contribuicao_equivalente_mes.sum()) < 1e-6
    cells.to_csv(OUT / "valor_por_plano_canal.csv", index=False)
    cuts = b.groupby(["plano", "faixa_treinos_30d"]).agg(**cols).reset_index()
    cuts.to_csv(OUT / "valor_por_plano_engajamento.csv", index=False)
    scenarios = []
    for plan in ["mensal", "anual"]:
        for channel in FEES:
            for tariff in ([39.9] if plan == "mensal" else [239.9,299.9]):
                margin = contribution(tariff, plan, channel)
                for months in [1,3,6]:
                    for action, contact, offer in [("conteudo_push_email", .01, 0), ("whatsapp_sem_oferta", .4, 0),
                                                    ("cs_sem_oferta", 18, 0), ("cupom_push_email", .01, 35.91 if plan=="mensal" else 25)]:
                        for ai in [0,.10]:
                            threshold = (contact+offer+ai)/(months*margin)
                            scenarios.append({"plano":plan,"canal":channel,"tarifa":tariff,"meses_adicionais":months,
                                              "acao":action,"contribuicao_mes":margin,"contato":contact,"oferta_por_contatado":offer,
                                              "ia_por_contatado":ai,"uplift_equilibrio":threshold,"possivel_com_uplift_ate_100pct":threshold<=1,
                                              "valor_com_uplift_5pp":incremental_value(.05,months,margin,contact,offer,ai)})
    scenarios = pd.DataFrame(scenarios)
    scenarios.to_csv(OUT / "cenarios_equilibrio.csv", index=False)
    n_month = int(b.plano.eq("mensal").sum()); n_year = len(b)-n_month
    cost_email = len(b)*.01
    fixed = 1500*.4+300*18+cost_email
    budget = pd.DataFrame([{"reserva_ia":ai,"contatos_sem_oferta":fixed,"saldo_ofertas":40000-fixed-ai,
                            "max_cupons_mensais":min(n_month,max_offers(40000,fixed,ai,35.91)),
                            "max_ofertas_anuais":min(n_year,max_offers(40000,fixed,ai,25))} for ai in [0,1000,5000]])
    budget.to_csv(OUT / "capacidade_orcamento.csv", index=False)
    # Three direct raw-source checks; independent Decimal recomputation of economic value.
    samples = []
    for plan, channel, price in [("mensal","app_store",39.9),("anual","web_pix",299.9),("anual","google_play",239.9)]:
        row = b[b.plano.eq(plan)&b.canal_cobranca.eq(channel)&gross.eq(price)].iloc[0]
        source = pd.read_csv(paths["pagamentos"],dtype=str)
        source = source[source.pagamento_id.eq(row.pagamento_id)].iloc[0]
        amount = Decimal(source.valor.replace("R$", "").strip().replace(",", "."))
        independent = amount / Decimal(12 if plan=="anual" else 1)*(1-Decimal(str(FEES[channel])))-Decimal("4.20")
        assert abs(float(independent)-row.contribuicao_equivalente_mes) < 1e-8
        samples.append({"user_id":row.user_id,"pagamento_id":row.pagamento_id,"plano":plan,"canal":channel,
                        "valor_bruto_fonte":str(amount),"contribuicao_mes_decimal":str(independent),"conferido":True})
    pd.DataFrame(samples).to_csv(PROC / "conferencia_tres_registros.csv", index=False)
    pd.DataFrame(filters).to_csv(OUT / "filtros.csv", index=False)
    audit = pd.DataFrame([
        ["Completude", "última cobrança aprovada ausente", int(b.centavos.isna().sum()),len(b)],
        ["Validade", "data de pagamento não interpretável",0,filters[0]["linhas"]],
        ["Consistência", "canal do pagamento diferente do canal da assinatura",int(b.metodo.map(METHOD).ne(b.canal_cobranca).sum()),len(b)],
        ["Unicidade", "cobranças aprovadas repetidas removidas após corte e testes",duplicates,int(filters[-3]["linhas"])],
        ["Temporalidade", "última cobrança posterior ou igual ao limite",int(b.ts.ge(CUT).sum()),len(b)]
    ],columns=["dimensao","verificacao","afetadas","denominador"])
    # Denominator for duplicate assessment is the approved pre-deduplication population.
    audit.loc[audit.dimensao.eq("Unicidade"), "denominador"] = next(x["linhas"] for x in filters if x["etapa"]=="somente aprovados")
    audit["percentual"] = 100*audit.afetadas/audit.denominador
    audit.to_csv(OUT / "qualidade_financeira.csv",index=False)
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[n] for n,p in paths.items())
    summary = {"pagantes":len(b),"mensais":n_month,"anuais":n_year,
               "bruto_equivalente_mes":float(b.bruto_equivalente_mes.sum()),
               "liquido_equivalente_mes":float(b.liquido_equivalente_mes.sum()),
               "custo_servir_mes":len(b)*SERVE,"contribuicao_equivalente_mes":float(b.contribuicao_equivalente_mes.sum()),
               "cupons_toda_base":n_month*35.91+n_year*25,
               "custo_contatos_plena_capacidade":fixed,"hashes_entradas":hashes,
               "corte":"30/09/2026","responsavel":"John","data_transferencia":"03/11/2026",
               "clusters_disponiveis":False,"risco_individual_disponivel":False,"uplift_estimado":False,
               "arquivos_brutos_preservados":True,"conferencias_independentes":3}
    (PROC / "manifesto_validacao.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
    make_report(b, cells, cuts, scenarios, budget, summary, filters, audit)
    print(json.dumps({k:v for k,v in summary.items() if k!="hashes_entradas"},indent=2,ensure_ascii=False))


def make_report(b, cells, cuts, scenarios, budget, s, filters, audit):
    tab = cells[["plano","canal_cobranca","pagantes","contribuicao_media_mes","contribuicao_equivalente_mes"]].copy()
    for c in tab.columns[3:]: tab[c]=tab[c].map(fmt)
    break_even = scenarios[(scenarios.tarifa.isin([39.9,299.9]))&scenarios.canal.eq("app_store")&scenarios.meses_adicionais.eq(3)&scenarios.ia_por_contatado.eq(0)].copy()
    break_even["equilibrio_pct"] = break_even.uplift_equilibrio.map(lambda x:fmt(100*x)+" p.p.")
    break_even=break_even[["plano","acao","equilibrio_pct"]]
    low = cuts[cuts.faixa_treinos_30d.eq("0")]
    low_n=int(low.pagantes.sum()); low_value=low.contribuicao_equivalente_mes.sum()
    total=s['contribuicao_equivalente_mes']
    report=f"""# Valor econômico e critérios de priorização

Vitaliza | MBA Inteli | Semana 5 | Responsável: John | Corte: 30/09/2026

## 1. Conclusão para o grupo

A base de {fmt(s['pagantes'],0)} pagantes representa R$ {fmt(total)} por mês de contribuição equivalente aproximada, após taxas de cobrança e custo de servir. Esse valor dimensiona a carteira atual. Não é lucro contábil, receita futura assegurada, LTV ou retorno de campanha.

O uso indiscriminado de cupons em toda a base consumiria R$ {fmt(s['cupons_toda_base'])} em compromissos de oferta, antes dos contatos e da IA. A reserva integral das ofertas corresponde a {fmt(s['cupons_toda_base']/40000,1)} vezes o orçamento mensal de R$ 40.000. É necessário selecionar ações por benefício incremental esperado e respeitar capacidade, elegibilidade e calendário de desembolso.

O caminho recomendado é preparar ações de conteúdo e desafios para teste controlado e condicionar descontos e CS a evidência de retorno. Esta entrega define a economia e os critérios; a escolha de um vencedor exige analisar o experimento de agosto. Risco de saída e valor financeiro isolados não demonstram que uma intervenção funciona.

Escopo: John assumiu a frente antes associada à Marcela, conforme sua instrução de 03/11/2026. Os encaminhamentos locais identificam valor e priorização. Não foi localizada uma rubrica original mais detalhada. Adota-se aqui esse escopo, mantendo clusterização e personas com as respectivas frentes.

## 2. Ponte do valor bruto à contribuição

Última cobrança aprovada no mensal, ou última anuidade dividida por 12, define o bruto equivalente mensal. Em seguida são descontadas as taxas de canal e R$ 4,20 por assinante/mês de custo de servir. Valores são calculados sem arredondamento intermediário e apresentados em centavos.

| Componente | Valor mensal equivalente |
| --- | --- |
| Cobranças convertidas à base mensal | R$ {fmt(s['bruto_equivalente_mes'])} |
| Taxas de canal | R$ {fmt(s['bruto_equivalente_mes']-s['liquido_equivalente_mes'])} |
| Receita líquida equivalente | R$ {fmt(s['liquido_equivalente_mes'])} |
| Custo de servir | R$ {fmt(s['custo_servir_mes'])} |
| Contribuição equivalente aproximada | R$ {fmt(total)} |

O mensal tem {fmt(s['mensais'],0)} pagantes e o anual {fmt(s['anuais'],0)}. A última cobrança anual pode ser R$ 239,90 ou R$ 299,90; usa-se o valor observado por conta. O desconto de influenciador vale no primeiro ano e a renovação pode alterar o valor. A aproximação não liquida estornos ou chargebacks nem aloca competência por dia; o valor anual já pago não pode ser tratado como nova receita recuperada por um contato.

## 3. Valor por plano e canal

{md_table(tab,['Plano','Canal de cobrança','Pagantes','Contribuição média/mês (R$)','Contribuição total/mês (R$)'])}

As oito células somam a base total. Cartão e Pix deixam maior contribuição por mensalidade que as lojas, pelas taxas menores. Essa diferença explica valor unitário, mas não determina eficácia de retenção. O plano anual usa outra cadência de cobrança e sua média inclui preços distintos.

Entre os pagantes atuais, {fmt(low_n,0)} não têm treino válido observado na janela de 30 dias, de 01/09 a 30/09/2026. Sua contribuição equivalente soma R$ {fmt(low_value)} por mês. É um corte descritivo de engajamento, não um cluster, previsão de perda ou recomendação de contato. A fonte de atividade é o detalhe tratado na preparação de John, separado do BI mensal.

## 4. Regra econômica da decisão

Valor incremental esperado por pessoa = uplift da ação x valor dos meses pagos adicionais - custo do contato - custo esperado da oferta por contatado - custo de IA por contatado.

Uplift é a diferença de probabilidade de retenção entre ação e ausência de ação. Não é a probabilidade de churn. No cenário simplificado, valor dos meses adicionais = contribuição mensal x H, sendo H o número assumido de meses pagos extras após o período já contratado. Não há desconto a valor presente nem curva de sobrevivência nessa sensibilidade. Os horizontes de 1, 3 e 6 meses não são previsão nem janela observada do case.

Para taxas e preços constantes, o uplift de equilíbrio = custo total por contatado / (contribuição mensal x H). A ação exige uplift maior que esse limite para gerar valor positivo. Oferta concedida a quem permaneceria sem ação também custa e deve entrar na conta. Se a oferta for resgatada apenas por parte dos contatados, usar probabilidade de resgate e calendário estimados, em vez de presumir resgate zero.

Exemplo didático: mensal pela loja, R$ 39,90, contribuição de R$ {fmt(contribution(39.9,'mensal','app_store'))}/mês. Se o contato gerar 3 meses pagos adicionais e uplift de 5 pontos percentuais, o benefício esperado é R$ {fmt(.05*3*contribution(39.9,'mensal','app_store'))}. Após WhatsApp de R$ 0,40, restam R$ {fmt(incremental_value(.05,3,contribution(39.9,'mensal','app_store'),.4))}, antes da IA. Com CS de R$ 18, o resultado seria R$ {fmt(incremental_value(.05,3,contribution(39.9,'mensal','app_store'),18))}. Os 5 p.p. e os 3 meses são hipóteses ilustrativas, não resultados medidos.

Limiares com tarifa cheia de loja, H = 3 meses adicionais e IA = zero apenas como limite inferior de custo:

{md_table(break_even,['Plano','Ação','Uplift de equilíbrio'])}

O cupom inclui R$ 35,91 no mensal ou R$ 25,00 no anual, mais R$ 0,01 de e-mail; o push tem custo desprezível. Reservam-se integralmente os custos de oferta previstos no enunciado, sem reduzir pelo percentual de taxas. Essa convenção é conservadora. O CSV de cenários inclui anuidade promocional de R$ 239,90 e IA de R$ 0,10 por pessoa como hipótese alternativa, não cotação de provedor.

## 5. Capacidade e orçamento do CRM

Por mês, 1.500 WhatsApps custam R$ 600 e 300 atendimentos de CS custam R$ 5.400. Um e-mail a cada pagante atual custa R$ {fmt(s['pagantes']*.01)}. Juntos, esses contatos custam R$ {fmt(s['custo_contatos_plena_capacidade'])}, sem ofertas e IA. Os volumes não significam pessoas distintas, pois pode haver sobreposição; contatos repetidos precisam de coordenação. Push admite no máximo um por pessoa por semana.

{md_table(pd.DataFrame([[fmt(r.reserva_ia),fmt(r.saldo_ofertas),fmt(r.max_cupons_mensais,0),fmt(r.max_ofertas_anuais,0)] for r in budget.itertuples()]), ['Reserva IA (R$)','Saldo ofertas (R$)','Máx. cupons mensais','Máx. ofertas anuais'])}

Os máximos são alternativas: dedicar todo o saldo a mensal ou a anual, sem somá-los. A reserva de R$ 0 é um limite matemático; R$ 1.000 e R$ 5.000 são hipóteses de planejamento. O custo real da IA depende do provedor, tokens e volume, ainda não definidos. Nenhuma viabilidade operacional com IA foi afirmada sem cotação.

A tabela reserva o compromisso inteiro do cupom mensal de três meses no mês de concessão. Isso é uma política prudencial de compromisso, não o fluxo financeiro mensal: o desconto de R$ 11,97 ocorre em cada mês elegível e o crédito anual só no fim do ciclo. Para novembro e dezembro, projetar compromissos anteriores, novas ofertas e resgates por mês, sem assumir que o mesmo orçamento pode ser usado novamente para compromissos já existentes. Pausa adia receita, não equivale a recebimento preservado, e precisa de cenário próprio.

## 6. Integração com clusters e priorização final

A base financeira tem uma linha por user_id e mantém cluster e uplift sem preenchimento. A tabela de Leonardo deve ser integrada por user_id com validação um para um e cobertura de todos os 14.753 pagantes; não se inventam grupos. Para cada cluster, somar pagantes e contribuição, examinar distribuição e engajamento, e cruzar com as personas construídas por Kiril.

Depois de estimar efeito e elegibilidade, escolher pessoa e ação maximizando a soma dos valores incrementais positivos, sob orçamento de R$ 40.000/mês, 1.500 WhatsApps, 300 CS e frequência de push. Uma simples ordenação por risco ou receita não resolve essa escolha quando custos e restrições variam. Manter a opção de não contatar; ações com efeito negativo ou custo maior que o ganho ficam fora. Não há fila operacional de contatos aprovada nesta entrega.

A campanha de 10/08/2026 testa conjuntos de mensagem/oferta enviados por push e e-mail. Não identifica automaticamente o efeito de WhatsApp ou CS. Além disso, a base termina em 30/09: ainda não há 60 dias completos de seguimento para a campanha. Análises posteriores devem usar horizonte observável comum, preservar o sorteio e não selecionar só quem abriu ou clicou. Modelos por cluster precisam de amostra e incerteza adequadas.

CAC de R$ 118 é referência para aquisição; não é receita nem economia automaticamente realizada por reter alguém. Só adicionar CAC evitado se a empresa demonstrar que reduzirá aquisição substitutiva e evitar dupla contagem. LTV requer sobrevivência, renovação e horizonte; não se extrapola a taxa mensal agregada ao contrato anual.

## 7. Validação e rastreabilidade

Contas de teste são excluídas pelo domínio normalizado @vitaliza.com.br. Pagamentos com Z são convertidos para Brasília; demais horários são locais. Apenas aprovados anteriores a 01/10/2026 entram, com deduplicação por user_id, horário local e valor em centavos. A última cobrança é conciliada à preparação anterior e ao canal de assinatura.

{md_table(pd.DataFrame(filters),['Fonte','Etapa','Linhas restantes'])}

{md_table(audit.assign(percentual=audit.percentual.map(lambda x:fmt(x)+"%")),['Dimensão','Verificação','Afetadas','Denominador','Percentual'])}

Há três conferências diretas contra o pagamento bruto, cobrindo mensal de loja, anual cheio por Pix e anual promocional por loja, com recomputação em Decimal. Totais por plano/canal fecham com os individuais e os hashes confirmam que as entradas não mudaram. Identificadores, amostras e hashes permanecem apenas na área de dados, fora do repositório público.

Fontes: docs/enunciado.md, seção 03, e PDF oficial correspondente; docs/dicionario_dados.md, seções 03 e 07; decisoes.md; preparação de John em src/preparar_diagnostico_s5.py. Cálculos desta frente: src/valor_priorizacao_s5.py. Bases e resultados: dados/processados/s5_valor_priorizacao/ e dados/saidas/s5_valor_priorizacao/. Nenhum dado externo ou resultado de modelo foi inventado.
"""
    (OUT / "John_Valor_Priorizacao_S5.md").write_text(report,encoding="utf-8")
    synthesis=f"""# Seção para integrar ao relatório coletivo

John assumiu a análise de valor e priorização anteriormente associada à Marcela. No corte de 30/09/2026, os 14.753 pagantes representam R$ {fmt(total)} mensais de contribuição equivalente aproximada, após taxas de canal e R$ 4,20 por assinante de custo de servir. A estimativa parte da última cobrança aprovada, dividida por 12 no plano anual. Não representa lucro contábil, LTV, receita futura garantida ou retorno de uma intervenção.

O critério proposto de priorização é o valor incremental esperado: efeito causal estimado da ação sobre retenção multiplicado pelo valor de meses pagos adicionais, menos contato, oferta e IA. Receita e risco de churn, isolados, não bastam. Para ilustrar o custo de oportunidade, um mensal de R$ 39,90 pela loja deixa R$ 29,715/mês após taxa e custo de servir. Com três meses pagos adicionais assumidos, WhatsApp sem oferta exige uplift superior a 0,45 p.p. e CS exige 20,19 p.p., antes da IA. Esses valores são limiares de cenário, não efeitos demonstrados.

O CRM dispõe de R$ 40.000/mês, 1.500 WhatsApps e 300 atendimentos de CS. Usar ambos os tetos e enviar um e-mail por pagante custa R$ {fmt(s['custo_contatos_plena_capacidade'])}, antes de ofertas e IA. Conceder cupons a toda a base comprometeria R$ {fmt(s['cupons_toda_base'])}, considerando o custo integral das ofertas, incompatível com reserva integral em um único orçamento mensal. O fluxo efetivo deve ser projetado por mês de resgate e renovação.

A base financeira está pronta para integração um a um com os clusters de Leonardo e as personas de Kiril. A decisão final depende de elegibilidade, efeito incremental, horizonte de valor e custos reais de IA. A campanha existente testa push e e-mail; seus efeitos não podem ser transferidos automaticamente a CS ou WhatsApp. Até essas etapas serem estimadas, as tabelas dimensionam valor e critérios econômicos, sem classificar pessoas como persuadíveis ou prometer ROI.
"""
    (OUT / "sintese_para_relatorio.md").write_text(synthesis,encoding="utf-8")
    (OUT / "LEIA-ME.md").write_text("# Entrega financeira de John\n\nLeia John_Valor_Priorizacao_S5.md ou seu PDF. Use sintese_para_relatorio.md para integração ao texto coletivo. CSVs preservam os valores sem arredondamento de apresentação.\n\nReprodução: `.venv/bin/python src/valor_priorizacao_s5.py`. Bases individuais e manifesto em dados/processados/s5_valor_priorizacao/. Não publicar os dados no Git.\n",encoding="utf-8")


if __name__ == "__main__":
    main()
