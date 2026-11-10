# Personas dos pagantes da Vitaliza — versão revisada

**Autoria das personas, nomes provisórios, hipóteses e propostas de ação: Kiril + Claude — Grupo 01.**
Revisão técnica e reprodução das conferências: John Neto (apoio de Codex), em 07/11/2026.
Clusterização de Leonardo; preparação da base e frente financeira de John.
Versão de trabalho S5 revisada tecnicamente por Codex por delegação explícita de John. Esse aceite técnico não representa assinatura autoral adicional de Kiril ou dos demais colegas. A integração à main obedece à revisão exigida pelo GitHub.

## Escopo e evidência

Retrato dos 14.753 pagantes ativos em 30/09/2026; limite exclusivo 01/10/2026, Brasília.
Os quatro perfis abaixo descrevem comportamento observado. Nomes e interpretações são provisórios.
As medidas das tabelas foram reproduzidas nas bases locais. A classificação temática das motivações foi reexecutada
a partir do código publicado em `src/personas_regras_s5.py` e `src/levantar_personas_s5.py`: é uma reexecução do
código do próprio rascunho, não uma verificação independente.
Método, versões, conferências e limites: [relatório da revisão](conferencia_personas_kiril_s5.md).

## Quatro personas

| Indicador | Adormecidos | Rotina em casa | Rua e ritmo | Novatos |
|---|---:|---:|---:|---:|
| Segmento de Leonardo | Distantes (0) | Engajados em casa (1) | Engajados ao ar livre (2) | Recém-chegados (3) |
| Pagantes | 2.783 | 4.315 | 4.793 | 2.862 |
| Participação na base | 18,9% | 29,2% | 32,5% | 19,4% |
| Dias com treino em 90 dias, mediana | 2 | 24 | 26 | 14 |
| Dias ativos / exposição, mediana | 0,022 | 0,267 | 0,300 | 0,324 |
| Dias desde o último treino, mediana | 36,8 | 2,2 | 1,7 | 1,8 |
| Proporção de treinos em vídeo, mediana | 16,7% | 85,7% | 19,2% | 26,7% |
| Minutos por treino, mediana | 46,0 | 41,5 | 47,9 | 43,3 |
| Tempo de assinatura, mediana em dias | 338 | 334 | 361 | 38 |
| Plano anual | 91,8% | 51,7% | 53,5% | 39,4% |
| Renovação automática desligada, retrato de 01/10 | 57,5% | 7,6% | 4,8% | 3,3% |
| Pessoas com renovação desligada | 1.599 | 329 | 228 | 94 |
| Proxy líquida mensal equivalente | R$ 63.337,65 | R$ 122.295,46 | R$ 134.466,95 | R$ 85.439,26 |
| Com ticket aberto nos últimos 90 dias | 3,3% | 3,5% | 3,3% | 6,2% |
| Seguidores, média | 1,9 | 2,0 | 2,1 | 0,2 |

As quatro proxies somam R$ 405.539,32; as renovações desligadas somam 2.250.
Proxy = última cobrança aprovada antes do corte, anual dividida por 12, menos a taxa do método.
Não desconta estornos, chargebacks ou custo de servir. Não mede receita contábil, LTV,
perda futura garantida nem valor incremental de contato.
Proporção de vídeo e recência usam apenas valores observados nas medianas; ausências não viram zero.
Exposição = mínimo entre 90 e dias inteiros desde o cadastro + 1.

### Adormecidos — “pagou e parou”

**Medido:** mediana de 2 dias com treino em 90; 27,3% sem nenhum treino nessa janela.
91,8% estão no anual. Entre os 1.599 com renovação desligada, 1.577 são anuais;
a proxy líquida mensal desse subconjunto é R$ 34.837,16, cerca de 55% do segmento.
Renovação desligada não foi usada no agrupamento; sua concentração é uma associação descritiva.

**Hipóteses de Kiril:** uma meta de desempenho ou evento pode ter passado; o período anual
pode permitir que a baixa utilização persista antes de uma decisão de renovação.

**Ações candidatas de Kiril:** avaliar pausa de até 60 dias e plano personalizado.
Uma eventual prioridade exige risco, efeito incremental da ação, valor e capacidade do CRM.
Algumas pessoas podem reagir negativamente ao contato; isso deve ser investigado no objetivo 6.

**Cenário de aniversário, sem data de renovação confirmada:** 439 pessoas desse subconjunto
têm aniversário do início da assinatura entre 01/10 e 29/11/2026. A proxy soma **R$ 9.539,30**,
corrigindo os R$ 9,8 mil do rascunho. O cenário supera os 300 atendimentos mensais de CS
caso se tente concentrar todos no mesmo mês; a janela abrange partes de dois meses.
O histórico disponível não confirma a próxima renovação dessas pessoas.

### Rotina em casa — “o vídeo que virou hábito”

**Medido:** mediana de 24 dias de treino em 90; 85,7% de vídeo na mediana e 41,5 minutos
por treino. A proporção com renovação desligada é 7,6%; esse indicador não é uma previsão de churn.
O nome de Kiril interpreta a predominância de vídeo; a base não confirma que o treino ocorreu em casa.

**Hipótese de Kiril:** o vídeo pode apoiar uma rotina de bem-estar.

**Ações candidatas de Kiril:** testar conteúdo do app por push ou e-mail. A hipótese de que
desconto custaria receita sem benefício adicional precisa de avaliação de efeito incremental.

### Rua e ritmo — “corre e pedala de rotina”

**Medido:** maior segmento e maior proxy líquida mensal total; mediana de 26 dias de treino
em 90, 19,2% de vídeo e 47,9 minutos por treino. Tempo de assinatura mediano de 361 dias;
4,8% com renovação desligada.

**Hipótese de Kiril:** desafios e metas de ritmo podem ser relevantes; os indicadores descritivos
não demonstram que essas ofertas retenham mais assinantes.

**Ações candidatas de Kiril:** avaliar conteúdo pertinente e frequência de contato comedida,
considerando efeito incremental e custo.

### Novatos — “chegaram há pouco, ainda sem rede”

**Medido:** assinatura mediana de 38 dias, 60,6% no mensal e maior mediana de frequência
relativa dos quatro grupos. Média de 0,2 seguidores; 26,7% vieram por influenciador,
contra 14,2% a 15,1% nos demais. Tickets em 6,2%, contra 3,3% a 3,5% nos demais.
A tendência de treino tem janela incompleta em 63,0% do grupo.
O nome descreve a tendência central: 492 integrantes (17,2%) têm pelo menos 90 dias de assinatura.
Não usar a persona como substituta da data individual de início ou da elegibilidade de onboarding.

**Hipóteses de Kiril:** a rede pequena pode refletir uma fase inicial; uma aquisição associada
a metas passageiras pode ter retenção diferente. Ambas precisam de avaliação longitudinal.

**Ações candidatas de Kiril:** avaliar mensagens de primeira meta, rotina e construção de rede.
Não há efeito de retenção demonstrado para essas ações nesta entrega.

## Cadastro e motivações

| Indicador descritivo | Adormecidos | Rotina em casa | Rua e ritmo | Novatos |
|---|---:|---:|---:|---:|
| Idade mediana, anos | 46,7 | 47,5 | 47,1 | 46,4 |
| Mulheres / homens | 49,7% / 45,2% | 49,1% / 46,4% | 50,9% / 44,6% | 49,1% / 45,8% |
| Sudeste | 66,9% | 69,3% | 67,9% | 65,4% |
| iOS | 44,8% | 48,4% | 52,8% | 49,4% |
| Relógio conectado | 39,1% | 37,7% | 38,1% | 38,3% |
| Aquisição por influenciador | 14,2% | 14,2% | 15,1% | 26,7% |

Percentuais usam todos os integrantes de cada segmento; sexo ausente não é redistribuído.
Idade = dias entre nascimento interpretável e limite de 01/10, divididos por 365,25;
datas ausentes (764 pagantes) são excluídas da mediana. Idades fora de 14 a 90 anos (133 pessoas) **não** são excluídas.
O rascunho as excluía e mostrava 47,0 para Rua e ritmo (47,04); sem o filtro dá 47,1 (47,11). Os demais segmentos não mudam.
Sexo foi normalizado pelas grafias F/Fem/feminino e M/Masc/masculino; sistema por minúsculas.
Essas características são descritivas: não se afirma igualdade estatística entre segmentos.

As diferenças de cadastro são pequenas: idade mediana entre 46,4 e 47,5 anos e mulheres entre 49,1% e 50,9%.
A exceção é a aquisição por influenciador nos Novatos (26,7%, contra 14,2% a 15,1% nos demais).
Por isso as personas se distinguem pelo comportamento de uso e pela motivação declarada, não por perfil demográfico.

**Leitura temática do objetivo declarado no cadastro** (código em `src/personas_regras_s5.py` e `src/levantar_personas_s5.py`):

| Persona | Respostas com conteúdo (denominador) | Leitura de destaque | Não classificadas |
|---|---:|---|---:|
| Adormecidos | 1.947 | Desempenho 31,5%; meta com data 27,5% | 7,3% |
| Rotina em casa | 2.994 | Mente/bem-estar 25,0%; saúde clínica 27,0%; desempenho 7,7% | 7,1% |
| Rua e ritmo | 3.393 | Desempenho 26,4%; saúde clínica 26,1% | 5,3% |
| Novatos | 1.978 | Estética/peso 21,7%; meta com data 27,0% | 7,2% |

Regras de leitura:

- Cada resposta recebe **um** tema principal, o primeiro que casar na ordem companhia/social, mente/bem-estar,
  saúde clínica, desempenho, estética/peso. Os percentuais de tema somam 100% entre as respostas com conteúdo
  (incluindo as não classificadas, em geral por erro de digitação).
- O denominador exclui respostas nulas e sem conteúdo (de 29% a 31% de cada segmento).
- **Meta com data** (verão, casamento, formatura, viagem, prova) é um sinalizador à parte: pode coexistir com
  qualquer tema e por isso não soma com os percentuais de tema.
- A classificação é por palavras-chave sobre cerca de 35 frases-modelo do cadastro e deve ser revista pelo grupo.
  O cadastro pode ser antigo e seu texto não comprova a motivação atual.

## Campanha de agosto: descrição de cliques

Tabela reproduzida no subconjunto da campanha que permanecia pagante em 30/09.
Cada célula mostra cliques / destinatários da mensagem e a respectiva taxa;
o controle não recebeu mensagem e não integra esse denominador.

| Persona | Conteúdo | Cupom | Desafio |
|---|---:|---:|---:|
| Adormecidos | 100 / 675 (14,8%) | 125 / 698 (17,9%) | 81 / 643 (12,6%) |
| Rotina em casa | 165 / 1.071 (15,4%) | 176 / 1.020 (17,3%) | 151 / 1.100 (13,7%) |
| Rua e ritmo | 168 / 1.178 (14,3%) | 185 / 1.215 (15,2%) | 181 / 1.191 (15,2%) |
| Novatos | 49 / 305 (16,1%) | 40 / 264 (15,2%) | 48 / 275 (17,5%) |

Clique mede atenção. A seleção dos sobreviventes em setembro e os segmentos calculados depois
da campanha impedem usar esta tabela como estimativa causal de retenção. Para o objetivo 6,
é necessário avaliar a população originalmente sorteada, incluir o controle, reconstruir o desfecho
e usar características anteriores ao tratamento.

## Limites e decisões pendentes

- Segmentos exploratórios no retrato do corte. Silhueta 0,169 indica baixa separação;
  estabilidade por reamostragem foi reproduzida (ARI médio 0,990; mínimo 0,984).
  Isso não demonstra estabilidade ao longo do tempo nem valida os nomes das personas.
- Conferências automatizadas das mesmas 108 pessoas: 1.836 comparações concordantes,
  dentro das tolerâncias. Revisão técnica delegada e conferências por recálculo concluídas; não são certificação humana independente.
- Para a S5, John delegou a revisão e adota os quatro nomes de trabalho, sem subdivisão dos Adormecidos. Ações continuam hipóteses para teste.
- A integração à priorização por valor deve usar a chave local do segmento; bases individuais
  e listas de contato permanecem fora do repositório público.
- A classificação temática é por palavras-chave e foi reexecutada pelo mesmo código do rascunho; uma revisão
  das categorias semânticas não é afirmada. Os percentuais são uma descrição do classificador, fora das conclusões executivas.
- A próxima renovação não deve ser inferida apenas do aniversário de início da assinatura.
- [Complemento às entregas dependentes](integracao_personas_s5.md): compatibilidade conferida,
  contribuição por persona, integração financeira e briefings condicionais de comunicação.

## Proveniência

Origem autoral: `Personas Vitaliza – rascunho.pdf`, enviado por John, com reunião indicada para
07/11/2026. Os dois sumários de conferência de Kiril estão referenciados no relatório técnico.
Os PDFs originais foram preservados localmente; esta versão pública contém apenas agregados,
interpretações atribuídas e pendências. Nenhum identificador ou texto individual foi incorporado.

Código de reprodução das tabelas de cadastro, motivações e campanha, e do cenário de aniversários:
`src/levantar_personas_s5.py`, `src/calcular_risco_janela_s5.py` e `src/personas_regras_s5.py`
(testes em `tests/test_personas_s5.py`).
