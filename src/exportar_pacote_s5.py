"""Gera relatório executivo (5 páginas) e cartões de personas (4 páginas), só com agregados.

Uso: python src/exportar_pacote_s5.py. Dependência de exportação: reportlab.
Conteúdo descritivo da S5; limites e rastreabilidade em docs/entregas/entrega_coletiva_s5.md.
"""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'saidas/s5'
INK=colors.HexColor('#173D3A');GREEN=colors.HexColor('#147D69')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TituloS5',fontName='Helvetica-Bold',fontSize=24,leading=29,textColor=INK,spaceAfter=22))
styles.add(ParagraphStyle(name='SecaoS5',fontName='Helvetica-Bold',fontSize=14,leading=19,textColor=GREEN,spaceBefore=15,spaceAfter=8))
styles.add(ParagraphStyle(name='CorpoS5',fontName='Helvetica',fontSize=11,leading=16,spaceAfter=11))
styles.add(ParagraphStyle(name='FonteS5',fontName='Helvetica',fontSize=8,leading=11,textColor=colors.HexColor('#526662'),spaceAfter=8))

def par(text,style='CorpoS5'):return Paragraph(text,styles[style])
def table(rows,widths):
    cells=[[par(str(v),'FonteS5') for v in row] for row in rows]
    t=Table(cells,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E4EDE6')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#C5D2C9'))]))
    return t

def footer(canvas,doc):
    canvas.setFont('Helvetica',8);canvas.setFillColor(INK)
    canvas.drawString(44,28,'Vitaliza fictícia | Grupo 01 | Corte: 30/09/2026')
    canvas.drawRightString(A4[0]-44,28,str(doc.page))

def build(name,pages):
    flow=[]
    for i,(title,blocks) in enumerate(pages):
        if i:flow.append(PageBreak())
        flow.extend([par(title,'TituloS5')]+blocks)
    SimpleDocTemplate(str(OUT/name),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=44,bottomMargin=48,title=name.replace('_',' '),author='Grupo 01 - MBA Inteli').build(flow,onFirstPage=footer,onLaterPages=footer)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    pages=[('1. Diagnóstico e recomendação',[
      par('A Vitaliza encerra o corte com 14.753 assinantes pagantes. O churn aumentou em 2026 e a piora permanece dentro dos planos mensal e anual. O diagnóstico sustenta investigar uso anterior, ciclo contratual, preço e problemas de produto, sem atribuir causalidade a um único fator.'),
      par('Recomendação para esta etapa','SecaoS5'),par('Usar quatro perfis para organizar a investigação e formular testes de retenção. Antes de ampliar contatos, combinar risco, elegibilidade de renovação, valor e efeito incremental de cada ação. Manter a opção de não contatar.'),
      table([['Indicador','Resultado'],['Pagantes no corte','14.753'],['Churn jan-set/2025','5,61%'],['Churn jan-set/2026','6,61%'],['Pico de abril/2026','1.154 perdas / 14.237 expostos = 8,11%']], [280,227]),
      par('O que está entregue','SecaoS5'),par('Base consolidada, histórico de saídas, análise exploratória, quatro segmentos, quatro personas, checagens de qualidade e análise econômica descritiva. A implementação está versionada, com resultados individuais mantidos fora do repositório público.'),
      par('Fontes: enunciado; src/preparar_diagnostico_s5.py; síntese de diagnóstico; documentos de clusterização, personas e qualidade. Taxas comparáveis usam perdas / exposições usuário-mês em janeiro a setembro.','FonteS5')]),
    ('2. Dados confiáveis para interpretar o churn',[
      par('A preparação exclui contas de teste, corrige fusos por origem e trata cópias do relógio no app. O histórico utiliza eventos de início e expiração. Desligar a renovação automática não encerra o período já pago.'),
      table([['Conferência','Resultado e decisão'],['População','14.753 na entrada e na saída; nenhuma exclusão nas checagens ou na segmentação'],['Atividades','9.383 cópias removidas; 3.649 durações zero antes da deduplicação'],['Ausências estruturais','759 sem treino em 90 dias; 177 sem treino observado em 2026'],['Onboarding','1.029 níveis e 1.491 dias planejados ausentes'],['Alertas exploratórios','58 pessoas com volume/duração para investigação; sem exclusão automática'],['Conferências','108 pessoas em amostras por quotas; 1.836 comparações concordantes nas tolerâncias']], [150,357]),
      par('Limitações que acompanham os resultados','SecaoS5'),par('BI mensal e detalhe tratado dos treinos divergem em 6.716 linhas de setembro, sendo 5.542 de pagantes no corte. As fontes são mantidas separadas. Existem cinco divergências conhecidas de renovação entre eventos e retrato, além de 1.112 casos sem estado inicial nos eventos relevantes.'),
      par('Atividade anterior ao pagamento é compatível com o freemium. Ausência de treino é característica útil para análise. As amostras por quotas exercitam casos de borda, mas zero falhas não estima o erro de toda a população.'),
      par('Fontes: docs/entregas/qualidade_claudinne_s5.md; conferencia_personas_kiril_s5.md; decisões do projeto.','FonteS5')]),
    ('3. Quatro perfis de assinantes',[
      table([['Perfil','Pessoas','Uso observado','Renovação desligada'],['Adormecidos','2.783','2 dias ativos em 90 dias (mediana)','57,5%'],['Rotina em casa','4.315','24 dias; vídeo em 85,7% dos treinos (mediana)','7,6%'],['Rua e ritmo','4.793','26 dias; vídeo em 19,2% dos treinos (mediana)','4,8%'],['Novatos','2.862','38 dias de assinatura (mediana)','3,3%']], [115,55,220,117]),
      par('Método e qualidade dos grupos','SecaoS5'),par('K-means sobre oito dimensões de comportamento, com correção de exposição, tratamento de ausências, transformações e padronização. A seleção avaliou k de 2 a 8, estabilidade por reamostragem e interpretabilidade. Quatro grupos mantêm cobertura integral e estabilidade alta nas reamostragens.'),
      par('A silhueta próxima de 0,169 indica baixa separação. Os segmentos são cortes interpretáveis de um comportamento contínuo. A estabilidade de reamostragem não comprova estabilidade longitudinal.'),
      par('Como usar os nomes','SecaoS5'),par('Nomes adotados como rótulos de trabalho da S5. Treinos em vídeo não comprovam localização em casa. Entre Novatos, 492 pessoas (17,2%) têm 90 dias ou mais de assinatura. Nenhum nome substitui os indicadores individuais ou a elegibilidade de uma ação.'),
      par('Fontes: src/clusterizacao_s5.py; docs/entregas/personas_s5.md. Personas: Kiril + Claude; clusterização: Leonardo; preparação: John.','FonteS5')]),
    ('4. Valor e condições econômicas',[
      table([['Persona','Proxy líquida/mês','Contribuição/mês'],['Adormecidos','R$ 63.337,65','R$ 51.649,05'],['Rotina em casa','R$ 122.295,46','R$ 104.172,46'],['Rua e ritmo','R$ 134.466,95','R$ 114.336,35'],['Novatos','R$ 85.439,26','R$ 73.418,86'],['Total','R$ 405.539,32','R$ 343.576,72']], [167,170,170]),
      par('Definição e limites','SecaoS5'),par('Proxy líquida: última cobrança aprovada antes do corte, anual dividida por 12, menos taxas do método. Contribuição: proxy líquida menos R$ 4,20 de custo mensal por pagante. Valores sem estornos/chargebacks, sem LTV, sem receita futura assegurada e sem efeito causal atribuído a contato.'),
      par('Rua e ritmo concentra o maior valor total. Adormecidos concentra 1.599 assinantes com renovação desligada. São recortes para investigação; isoladamente não definem retorno ou prioridade de contato.'),
      par('Restrições do CRM','SecaoS5'),par('R$ 40 mil por mês, incluindo ofertas e IA. WhatsApp: R$ 0,40 e 1.500 mensagens/mês. CS: R$ 18 e 300 atendimentos/mês. Push: no máximo um por pessoa por semana. E-mail: R$ 0,01 por envio. Reservar o custo integral de ofertas antes de prometer benefícios.'),
      par('Fonte: enunciado, seção 03; src/valor_priorizacao_s5.py; src/complementar_entregas_personas_s5.py.','FonteS5')]),
    ('5. Decisões, testes e acompanhamento',[
      par('Decisões para a versão S5','SecaoS5'),par('Manter os quatro segmentos e nomes de trabalho, sem subdividir Adormecidos nesta etapa. Preservar todos os pagantes e representar ausências conforme o método documentado. Usar hipóteses de ações como propostas para teste. Evitar inferir motivação individual a partir de palavras-chave do cadastro.'),
      par('Próximas análises do módulo','SecaoS5'),par('Avaliar a campanha de agosto na população originalmente sorteada, com controle e desfecho de saída. Usar características anteriores ao tratamento. Desenvolver previsão com separação temporal e integrar risco, efeito, custo e elegibilidade. Acompanhar churn, efeito incremental, custo por retido e contribuição adicional.'),
      par('Atenção aos vieses','SecaoS5'),par('Cliques medem atenção. A tabela por personas de sobreviventes de setembro não estima retenção causal. O experimento de push/e-mail não comprova efeito em WhatsApp ou CS. Aniversário da assinatura é cenário, sem confirmação da próxima cobrança. Pesquisa de saída descreve respondentes opcionais do site.'),
      par('Autoria e revisão','SecaoS5'),par('Grupo 01: Leonardo, segmentação; Kiril + Claude, personas e conferidores; Claudinne, checagens; John, preparação, diagnóstico e valor. Consolidação e revisão técnica por Codex a pedido de John. A revisão delegada não equivale a aprovação autoral individual dos colegas.'),
      par('Rastreabilidade','SecaoS5'),par('Código, decisões, documentação e pacote em GitHub: leonardomoraesmendes/vitaliza. Ponto de entrada: docs/entregas/entrega_coletiva_s5.md. Bases e comparações individuais permanecem em dados/, ignorado no Git. O pacote não contém registros individuais.'),
      par('Escopo: entrega parcial S5. Não foi realizada submissão à plataforma do curso.','FonteS5')])]
    build('Vitaliza_S5_Relatorio_Executivo.pdf',pages)
    descriptions=[
      ('Adormecidos','2.783 pagantes (18,9%)','2 dias ativos em 90 dias; 36,8 dias desde o último treino (medianas). 27,3% sem treino na janela. 91,8% no anual.','57,5% com renovação desligada: 1.599 pessoas.','R$ 63.337,65 de proxy líquida e R$ 51.649,05 de contribuição equivalente mensal.','Avaliar retomada com plano personalizado e, conforme elegibilidade, pausa. Medir efeito e possibilidade de reação negativa ao contato.','Baixa frequência não confirma frustração. 72,7% tiveram ao menos um treino na janela.'),
      ('Rotina em casa','4.315 pagantes (29,2%)','24 dias ativos em 90 dias, 85,7% de vídeo e 41,5 minutos por treino (medianas).','7,6% com renovação desligada: 329 pessoas.','R$ 122.295,46 de proxy líquida e R$ 104.172,46 de contribuição equivalente mensal.','Avaliar conteúdo guiado e continuidade por push/e-mail, respeitando limites e teste com controle.','Predominância de vídeo não comprova local do treino nem objetivo atual de bem-estar.'),
      ('Rua e ritmo','4.793 pagantes (32,5%)','26 dias ativos em 90 dias, 19,2% de vídeo e 47,9 minutos por treino (medianas).','4,8% com renovação desligada: 228 pessoas.','R$ 134.466,95 de proxy líquida e R$ 114.336,35 de contribuição equivalente mensal.','Avaliar desafios e metas pertinentes, medindo efeito incremental antes de ampliar contatos.','Não inferir endereço, rota, objetivo ou resposta individual a partir do rótulo.'),
      ('Novatos','2.862 pagantes (19,4%)','38 dias de assinatura (mediana), maior frequência relativa e 0,2 seguidores (média). Tickets em 6,2% do grupo.','3,3% com renovação desligada: 94 pessoas.','R$ 85.439,26 de proxy líquida e R$ 73.418,86 de contribuição equivalente mensal.','Avaliar descoberta de recursos e construção de rotina. Verificar data individual antes de aplicar linguagem de onboarding.','492 integrantes (17,2%) têm pelo menos 90 dias de assinatura. O nome descreve a tendência central.')]
    cards=[]
    for name,n,behavior,signal,value,action,limit in descriptions:
        cards.append((name,[par(n,'SecaoS5'),par('Comportamento medido','SecaoS5'),par(behavior),par('Sinal observado','SecaoS5'),par(signal),par('Valor descritivo','SecaoS5'),par(value),par('Hipótese de ação para teste','SecaoS5'),par(action),par('Limite de interpretação','SecaoS5'),par(limit),par('Fontes: personas_s5.md e integracao_personas_s5.md. Autoria das personas: Kiril + Claude. Nomes de trabalho da S5. Renovação desligada não é previsão de churn. Contribuição não é ROI.','FonteS5')]))
    build('Vitaliza_S5_Cartoes_Personas.pdf',cards)

if __name__=='__main__':main()
