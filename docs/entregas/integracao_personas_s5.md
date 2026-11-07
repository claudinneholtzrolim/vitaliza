# Compatibilidade das personas e complemento das entregas — S5

John + Codex, 07/11/2026. Autoria dos nomes, perfis, hipóteses e ações candidatas: **Kiril**.
Clusterização: **Leonardo**. Preparação, diagnóstico e frente financeira: **John**.
Integração preparada para revisão do grupo, sem aprovação autoral presumida.

## Confirmação da correspondência

As quatro personas estão de acordo com as características centrais dos segmentos reproduzidos.
A correspondência é uma descrição dos grupos no corte, não uma confirmação das motivações
ou da resposta a campanhas. O código verifica as quatro relações abaixo e interrompe a integração
se alguma deixar de ser sustentada pelos dados.

| Persona de Kiril | Segmento de Leonardo | Evidência reproduzida | Limite da interpretação |
|---|---|---|---|
| Adormecidos | Distantes, 0 | Menor mediana de dias ativos: 2 em 90; 27,3% sem treino na janela | 72,7% registraram ao menos um treino; o nome não significa ausência total de uso |
| Rotina em casa | Engajados em casa, 1 | Maior proporção mediana de vídeo: 85,7%; 24 dias ativos na mediana | Vídeo não comprova localização física em casa |
| Rua e ritmo | Engajados ao ar livre, 2 | Maior grupo, 4.793; vídeo mediano 19,2%; maior duração mediana, 47,9 min | Modalidade é o indicador observado; não se infere endereço, rota ou objetivo individual |
| Novatos | Recém-chegados, 3 | Menor assinatura mediana, 38 dias; maior frequência mediana relativa, 0,324; menor rede média, 0,2 seguidores | 492 pessoas, 17,2%, têm assinatura de 90 dias ou mais; nome não substitui antiguidade real |

Não houve alteração nos rótulos ou reatribuição de pessoas para fazer o perfil combinar com o nome.
Mantidos 2.783 / 4.315 / 4.793 / 2.862 integrantes e a cobertura dos 14.753 pagantes.
As regras completas de Kiril foram recebidas no PR #9 e os percentuais temáticos foram reproduzidos. São categorias por palavras-chave, sem validação independente de motivação individual.
As hipóteses de ação continuam como propostas para teste, sem eficácia demonstrada.

## Quais entregas dependiam desse material

Levantamento fundamentado no README, na entrega de valor/priorização e nos objetivos 3, 6, 7 e 8
do enunciado. Não foi atribuída uma nova tarefa aos colegas nem presumida uma rubrica não encontrada.

| Entrega/frente | Dependência das personas | Complemento realizado | O que permanece aberto |
|---|---|---|---|
| Valor e priorização, John | Cruzar o valor de cada segmento com sua leitura de negócio | Integração um para um; contribuição por persona, plano e canal; recorte de renovação desligada; limiares econômicos | Risco, elegibilidade, efeito incremental e custo real de IA para decidir contatos |
| Síntese financeira para o relatório coletivo | Explicar quais grupos concentram valor e sinais observados | Seção integrada gerada junto à síntese, com conciliação dos totais | Aprovação e consolidação no relatório coletivo |
| Síntese de diagnóstico, John | Conectar hipóteses históricas ao retrato atual sem confundir populações | Acrescentado contexto dos quatro grupos no corte, com limite de sobrevivência explícito | Reconstrução dos segmentos em cortes históricos antes de medir churn por grupo |
| Qualidade e revisão cruzada, Claudinne/grupo | Conferir conceitos, tratamentos e limites das interpretações | Matriz de correspondência, controle de cobertura, hashes e pendências disponíveis | Revisão humana e aceite, sem assinatura de terceiros presumida |
| Decisão de contato, objetivo 6 | Usar a persona como contexto da ação depois de estimar benefício | Critérios e restrições conectados às ações candidatas de Kiril | Estimar efeito com controle e características anteriores à campanha; validar orçamento e elegibilidade |
| Briefing de mensagens, objetivo 8 | Adaptar tema e linguagem ao perfil | Quatro briefings e exemplos condicionais abaixo | Regra de decisão aprovada e validação da mensagem antes de qualquer envio |

Personas não eram condição técnica para começar a estimar churn ou analisar o experimento.
Elas ajudam a interpretar grupos e a formular mensagens; não suprem o desfecho, o controle
ou a estimativa de efeito. Não foi criado modelo supervisionado ou estimador causal novo nesta etapa.

## Valor e contribuição por persona

Última cobrança aprovada equivalente mensal, após taxa do método; custo de servir de R$ 4,20/pessoa/mês.

| Persona | Pagantes | Proxy líquida/mês | Custo de servir/mês | Contribuição equivalente/mês |
|---|---:|---:|---:|---:|
| Adormecidos | 2.783 | R$ 63.337,65 | R$ 11.688,60 | R$ 51.649,05 |
| Rotina em casa | 4.315 | R$ 122.295,46 | R$ 18.123,00 | R$ 104.172,46 |
| Rua e ritmo | 4.793 | R$ 134.466,95 | R$ 20.130,60 | R$ 114.336,35 |
| Novatos | 2.862 | R$ 85.439,26 | R$ 12.020,40 | R$ 73.418,86 |
| **Total** | **14.753** | **R$ 405.539,32** | **R$ 61.962,60** | **R$ 343.576,72** |

As somas das quatro parcelas foram conciliadas ao manifesto financeiro. A contribuição
continua sendo uma aproximação descritiva: anual dividido por 12, sem estornos/chargebacks,
sem LTV, sem receita futura garantida e sem atribuição de valor causal a uma intervenção.

| Persona | Renovação desligada, retrato de 01/10 | Contribuição mensal equivalente desse subconjunto |
|---|---:|---:|
| Adormecidos | 1.599 | R$ 28.121,36 |
| Rotina em casa | 329 | R$ 6.553,22 |
| Rua e ritmo | 228 | R$ 4.445,20 |
| Novatos | 94 | R$ 2.346,92 |

Rua e ritmo concentra o maior valor total; Adormecidos concentra o sinal observado de renovação
desligada. Isso define perguntas de investigação, sem ordenar pessoas para contato.
Renovação desligada ainda não é expiração nem probabilidade calibrada de saída.

## Complemento econômico da priorização

Para ilustrar o custo relativo por persona, usamos a contribuição média observada,
H=3 meses pagos adicionais hipotéticos, sem oferta e com IA=zero apenas como limite inferior de custo.
Uplift de equilíbrio = custo do contato / (contribuição média mensal × H).

| Persona | Push + e-mail, R$ 0,01 | WhatsApp, R$ 0,40 | CS, R$ 18 |
|---|---:|---:|---:|
| Adormecidos | 0,02 p.p. | 0,72 p.p. | 32,33 p.p. |
| Rotina em casa | 0,01 p.p. | 0,55 p.p. | 24,85 p.p. |
| Rua e ritmo | 0,01 p.p. | 0,56 p.p. | 25,15 p.p. |
| Novatos | 0,01 p.p. | 0,52 p.p. | 23,39 p.p. |

Não são efeitos estimados nem limiares individuais. A mistura de planos/tarifas exige a análise
individual por ação antes de qualquer decisão; H não é previsão. As saídas locais também
preservam H=1 e H=6. As ofertas mantêm o custo e a elegibilidade do enunciado e os cenários
originais da frente financeira. Pausa adia receita, não pode ser tratada como retenção monetizada.

Critério para a etapa futura: valor incremental positivo após contato, oferta e IA, elegibilidade
verificada e respeito simultâneo a R$ 40 mil/mês, 1.500 WhatsApps/mês, 300 CS/mês e um push
por pessoa/semana. O efeito do experimento de push/e-mail não se transfere a CS ou WhatsApp.
Manter a opção de não contatar. Nenhuma lista foi gerada ou mensagem enviada.

## Briefings e exemplos condicionais

Rascunhos editoriais para apoiar o objetivo 8 depois da decisão de contato. Derivam das propostas
de Kiril; não são novas decisões dele. Não usar o nome da persona no contato, afirmar motivo
pessoal inferido, citar problemas de saúde ou anunciar benefício/oferta sem elegibilidade confirmada.

| Persona | Tema candidato | Exemplo de mensagem a revisar | Condição específica |
|---|---|---|---|
| Adormecidos | Escolha e retomada sem pressão | “Quer ajustar sua rotina de treinos? Explore as opções do app e escolha um próximo passo que faça sentido para você.” | Evitar constrangimento por baixa utilização; pausa só após validação de elegibilidade e comunicação de seus efeitos |
| Rotina em casa | Sessões guiadas e continuidade | “Que tal escolher uma sessão guiada para esta semana? Veja as opções de força, funcional e ioga no app.” | Não presumir local, objetivo de saúde ou frequência diária |
| Rua e ritmo | Meta de treino ao ar livre | “Escolha uma meta para o próximo treino de caminhada, corrida ou pedal e acompanhe seu registro no app.” | Validar o conteúdo oferecido e não inferir localização ou prometer melhora de desempenho |
| Novatos | Descoberta do app e primeiro objetivo | “Explore os recursos do app e escolha um objetivo de treino para começar sua rotina.” | Usar linguagem de entrada só com antiguidade e etapa de onboarding verificadas; não aplicar aos 492 antigos apenas pelo rótulo |

Push/e-mail são hipóteses de canal para teste, sob os limites do CRM. Estes exemplos não demonstram
retenção, não incluem cupom autorizado e não equivalem a mensagens personalizadas aprovadas.
O efeito deve ser estimado sem selecionar apenas quem abriu/clicou ou sobreviveu até setembro.

## Reprodução e artefatos

Após montar o ambiente conforme [conferência técnica](conferencia_personas_kiril_s5.md),
regenerar a base e executar a revisão de Kiril com os dois PDFs locais. Em seguida:

```sh
.venv/bin/python src/valor_priorizacao_s5.py
.venv/bin/python src/complementar_entregas_personas_s5.py
.venv/bin/python -m unittest discover -s tests -v
swift src/exportar_valor_s5.swift  # PDF local opcional, após o complemento
```

O complemento verifica SHA do artefato de segmentos, do contexto e a compatibilidade das fontes
brutas entre finanças e personas. Reexecução substitui apenas os blocos delimitados do próprio
complemento nos textos locais. A base financeira original permanece separada da base integrada.

| Artefato local, ignorado no Git | Finalidade |
|---|---|
| `dados/processados/s5_integracao_personas/base_valor_personas_corte.csv` | Base individual integrada; acesso local, sem publicação |
| `dados/processados/s5_integracao_personas/manifesto_validacao.json` | Hashes, cobertura e verificações da integração |
| `dados/saidas/s5_integracao_personas/valor_por_persona.csv` | Ponte de receita líquida, custo de servir e contribuição |
| `dados/saidas/s5_integracao_personas/valor_persona_plano_canal.csv` | Cruzamento econômico por grupo, plano e canal |
| `dados/saidas/s5_integracao_personas/renovacao_desligada_por_persona.csv` | Sinal observado separado de previsão |
| `dados/saidas/s5_integracao_personas/limiares_por_persona.csv` | Sensibilidade econômica, H=1/3/6 |
| `dados/saidas/s5_integracao_personas/complemento_valor_personas.md` | Relatório integrado de leitura |
| Sínteses locais em `s5_john/` e `s5_valor_priorizacao/` | Contexto e valor acrescentados para consolidação coletiva |

Versões de referência: preparação em main `8d40886`, clusterização `eafaf08` do PR #5,
personas do PR #7. Ambos os PRs continuam sujeitos à revisão; nenhum merge foi executado.
Na validação do complemento, os 28 testes passaram, incluindo sete casos de integração
contra perda de cobertura, duplicação, troca de rótulo e sobrescrita de decisão.

## Qualidade e entropia do complemento

A informação nova está concentrada neste documento e no relatório local gerado, com links
nas entregas que dependiam dela. O documento de personas continua responsável pela descrição
autoral; este explica sua ligação às finanças e às ações candidatas. Tabelas repetidas entre
texto público e leitura local são intencionais, para ambos serem compreensíveis isoladamente.
Não foi atribuída uma nota estatística de qualidade a frequência de palavras.

Foram conferidos: coerência semântica dos nomes com as medianas, denominadores,
integridade um para um, conciliação monetária, distinção entre hipótese e evidência,
ausência de identificadores nos arquivos destinados ao PR e links internos.

| Dimensão | Resultado da integração |
|---|---|
| Completude | Zero dos 14.753 pagantes sem segmento ou persona |
| Validade | Zero rótulos ausentes ou fora de 0/1/2/3 |
| Consistência | Zero divergências de renovação entre as duas frentes e zero diferenças de proxy acima de R$ 0,00000001; quatro somas econômicas fecham ao manifesto financeiro |
| Unicidade | Zero chaves ausentes/duplicadas; cobertura de 14.753 antes e depois, sem multiplicação de valor |
| Temporalidade | Mesmo contexto do corte em 30/09, verificado por hash; nenhum desfecho posterior foi acrescentado à segmentação |

Os 28 testes e a reexecução idempotente passaram. O PDF financeiro atualizado foi renderizado
em seis páginas e conferido visualmente; permanece na pasta local ignorada pelo Git.
Permanecem explícitas as incertezas de motivação, efeito incremental, próxima renovação,
interpretação individual e aprovação humana. Essa separação evita apresentar o complemento
descritivo como conclusão do sistema de retenção.

Fontes: [personas](personas_s5.md), [conferência](conferencia_personas_kiril_s5.md),
[entrega financeira](valor_priorizacao_s5.md), [enunciado](../enunciado.md) e
[decisões](../../decisoes.md). Os dados tabulares detalhados e suas evidências ficam fora do Git.
