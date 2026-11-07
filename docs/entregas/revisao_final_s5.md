# Revisão integrada da entrega S5 — 07/11/2026

Revisão e decisões técnicas de Codex por solicitação explícita de John. Fontes: enunciado, dicionário, decisões e PRs #5, #7, #8 e #9. Escopo: entrega preparada no GitHub, sem submissão ao Inteli.

## Verificações

- Integração local das quatro contribuições em cópia isolada: sem perda de trabalho preexistente.
- Preparação reexecutada a partir do data room; 14.753 pagantes no corte e referências históricas conciliadas.
- Checagens: 14 regras e oito fórmulas com zero violações; 14.753 pessoas preservadas.
- Segmentos reproduzidos: 2.783 / 4.315 / 4.793 / 2.862; oito dimensões observadas, sem churn na matriz.
- Conferidores por seeds: 12 e 96 pessoas sem sobreposição; 204 e 1.632 comparações concordantes dentro das tolerâncias das 17 métricas. Quotas e bordas não permitem limite populacional de erro.
- O revisor separado também recalculou as mesmas 108 pessoas. Cada conjunto usa as mesmas regras documentadas: não é validação independente dessas regras de negócio.
- Integração bijetiva de assinante, persona, segmento e valor; proxy líquida de R$ 405.539,32 e contribuição de R$ 343.576,72.
- Classificador de motivações e regras recebidos no PR #9, inspecionados e reexecutados; percentuais e denominadores conciliados. A categorização por palavras-chave não comprova motivação atual e não sustenta as recomendações executivas.
- 50 testes de regras, cobertura, ausência, tolerâncias, janelas e integração passaram no conjunto.
- Hashes dos brutos preservados; notebooks sem saídas. Bases, amostras e evidências individuais fora do Git público.
- PPTX de três slides: validação estrutural/layout e reimportação passaram. Tabela editável. Todos os slides renderizados e conferidos visualmente.
- PDFs de cinco e quatro páginas: contagem e extração conferidas; todas as páginas renderizadas e inspecionadas. Sem cortes, sobreposições ou linhas órfãs identificados.

## Ajustes decorrentes da revisão

1. O resumo do cenário de aniversário no revisor separado ainda incluía mensais. Corrigido para anuais: 439 pessoas e R$ 9.539,30 mensais equivalentes, sem data de próxima renovação confirmada.
2. O revisor ganhou `--amostras-seeds`, utilizando o código original de seleção e um recálculo separado. PDFs pessoais deixam de ser requisito para reproduzir a revisão.
3. A varredura de k passou a conservar o mesmo percurso aleatório completo quando chamada com `--k 4`. Antes, mudar de varredura 2–8 para uma varredura só de k=4 alterava as reamostragens e o ARI publicado, embora os rótulos finais fossem os mesmos.
4. Atualizados textos que ainda diziam que o classificador ou seeds estavam ausentes. Nomes são rótulos de trabalho aceitos tecnicamente por delegação de John, sem atribuir aceite individual aos autores.
5. Entrega coletiva, três slides, cinco páginas executivas e quatro cartões prontos. Uma rotina reúne a reprodução das frentes.

## Entropia editorial

A análise usa entropia como critério editorial de dispersão, redundância e ambiguidade. Não atribui nota estatística de qualidade a frequência de palavras.

| Aspecto | Decisão e evidência |
|---|---|
| Ponto de entrada | entrega_coletiva_s5.md reúne o mapa; cada documento de método mantém a responsabilidade por sua frente |
| Redundância | Contagens repetidas no resumo, slides e cartões são intencionais para leitura independente; não são evidências adicionais |
| Populações | Pagantes no corte, expostos no mês, respondentes e sobreviventes da campanha identificados separadamente |
| Unidades | Proxy líquida, custo de servir e contribuição nomeados; valores monetários não apresentados como retorno comprovado |
| Temporalidade | Corte e janelas explícitos; aniversário não é calendário de cobrança |
| Causalidade | Cliques, uso anterior, renovação desligada e motivos por texto não tratados como efeitos incrementais |
| Autoria | Créditos preservados; autorização de John e revisão de Codex não atribuídas a colegas |
| Visual | Fontes, títulos, tabela, quebra de linhas e páginas revisados após renderização |

## Limites residuais

Mantidas as divergências entre fontes de uso e renovação, a baixa separação dos grupos, as ausências estruturais e a natureza exploratória das motivações. Não são bloqueios de produção da S5 quando explicitados; não foram resolvidos por ajuste para forçar concordância. Modelagem de risco, efeito incremental e ROI pertencem às etapas posteriores identificadas no case.

O Adalove exigiu acesso institucional, indisponível na sessão consultada. A rubrica exata e o prazo permanecem sem conferência nativa. John determinou não submeter agora.

O GitHub rejeitou a aprovação dos PRs de John pela própria conta autora e exigiu um revisor com escrita. Nenhuma proteção foi reduzida. A revisão técnica deste documento não substitui esse controle externo.
