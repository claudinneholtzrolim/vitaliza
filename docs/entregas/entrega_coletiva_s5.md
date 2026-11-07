# Vitaliza — entrega parcial da semana 5

Grupo 01. Corte analítico: **30/09/2026**, limite exclusivo de dados temporais **01/10/2026, Brasília**. A Vitaliza e sua base são fictícias, conforme o enunciado.

## Materiais para leitura

- [Apresentação executiva, três slides](../../saidas/s5/Vitaliza_S5_Executivo_v2.pptx).
- [Relatório executivo, cinco páginas](../../saidas/s5/Vitaliza_S5_Relatorio_Executivo.pdf).
- [Quatro cartões de persona](../../saidas/s5/Vitaliza_S5_Cartoes_Personas.pdf).
- Documentação: [segmentação](clusterizacao_s5.md), [personas](personas_s5.md), [qualidade de Claudinne](qualidade_claudinne_s5.md), [conferências](conferencia_personas_kiril_s5.md), [integração e valor](integracao_personas_s5.md) e [revisão final](revisao_final_s5.md).

O pacote atende ao conteúdo identificado nas orientações de aula: análise exploratória, bases consolidadas, histórico de saídas, segmentação, documentação reproduzível e síntese executiva. Inclui cartões de persona e relatório executivo, formatos também mencionados na trilha de negócios. A rubrica e o prazo exatos na plataforma não foram confirmados: o acesso disponível recebeu restrição institucional. Não houve submissão ao curso; John determinou preparar apenas o GitHub.

## Diagnóstico

A base fecha com 14.753 pagantes. Em janeiro–setembro, o churn agregado passa de 5,61% em 2025 para 6,61% em 2026. O mensal passa de 9,14% para 10,86%; o anual, de 2,45% para 3,32%. A maior participação do anual atenua a alta, em vez de explicá-la. As taxas comparáveis são perdas / exposições usuário-mês. Não são taxas de pessoas distintas durante todo o período.

Baixo uso anterior se associa a maior saída posterior. Reajuste de preço e problemas de produto motivam hipóteses adicionais. As análises não identificam uma causa isolada nem comprovam que estimular treino reduzirá churn. BI e detalhe dos treinos continuam identificados separadamente devido às diferenças de registro.

## Segmentos e personas

| Persona de trabalho | Segmento | Pessoas | % da base | Renovação desligada |
|---|---|---:|---:|---:|
| Adormecidos | Distantes | 2.783 | 18,9% | 57,5% |
| Rotina em casa | Engajados em casa | 4.315 | 29,2% | 7,6% |
| Rua e ritmo | Engajados ao ar livre | 4.793 | 32,5% | 4,8% |
| Novatos | Recém-chegados | 2.862 | 19,4% | 3,3% |
| Total | | **14.753** | **100,0%** | |

A segmentação usa oito dimensões observadas, sem desfecho de saída. Silhueta próxima de 0,169: baixa separação entre grupos. A estabilidade de reamostragem é alta, sem demonstrar estabilidade longitudinal. Nomes descrevem tendências, sem substituir medidas individuais. Vídeo não comprova localização; 492 Novatos têm 90 dias ou mais de assinatura. Renovação desligada é sinal observado, não expiração ou probabilidade calibrada.

Por delegação expressa de John para revisar e resolver a S5, os quatro nomes são adotados como rótulos de trabalho e não há subdivisão adicional de Adormecidos nesta entrega. Hipóteses de ação ficam para teste; nenhum contato foi realizado. A decisão não atribui uma assinatura autoral adicional aos colegas.

## Qualidade e valor

Todos os 14.753 pagantes são mantidos. Há 759 sem treino em 90 dias, 177 sem treino observado em 2026 e 58 alertas exploratórios de volume/duração. Nenhum desses fatos gera exclusão automática. Atividade anterior ao pagamento é possível no freemium.

| Persona | Proxy líquida mensal | Custo de servir mensal | Contribuição equivalente mensal |
|---|---:|---:|---:|
| Adormecidos | R$ 63.337,65 | R$ 11.688,60 | R$ 51.649,05 |
| Rotina em casa | R$ 122.295,46 | R$ 18.123,00 | R$ 104.172,46 |
| Rua e ritmo | R$ 134.466,95 | R$ 20.130,60 | R$ 114.336,35 |
| Novatos | R$ 85.439,26 | R$ 12.020,40 | R$ 73.418,86 |
| Total | **R$ 405.539,32** | **R$ 61.962,60** | **R$ 343.576,72** |

Proxy: última cobrança aprovada, anual /12, após taxa do método. Contribuição desconta R$ 4,20/pagante/mês. Sem estornos/chargebacks, LTV, perda garantida ou retorno causal de contato. Rua e ritmo concentra valor total; Adormecidos concentra renovação desligada. Os recortes motivam investigação, sem ordenar uma fila operacional.

## Reprodução

Preparar o data room conforme o README, em `dados/brutos/`, sem versioná-lo. As dependências de análise estão em `requirements-revisao-kiril.txt`.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-revisao-kiril.txt
.venv/bin/python src/reproduzir_entrega_s5.py
```

O comando executa preparação, checagens, finanças, segmentação, levantamentos, conferências, integração e testes. As amostras de 12 e 96 são reproduzidas por seeds 42/96, sem necessidade dos PDFs originais. `git clone` comum preserva o commit histórico de referência usado na revisão; clone raso pode não contê-lo.

PDFs podem ser regenerados com `python src/exportar_pacote_s5.py` em ambiente com `reportlab` (dependências opcionais em `requirements-pacote-s5.txt`). O PPTX é editável e acompanha a entrega. A correção visual e a rastreabilidade são registradas na revisão final.

As bases individuais, amostras, textos de cadastro e relatórios de comparação ficam em `dados/`, ignorado no Git. O pacote público contém apenas documentos agregados, código e testes. Não se publica a lista de pessoas de cada segmento.

## Autoria

Leonardo: segmentação. Kiril + Claude: personas, classificador e conferidores. Claudinne: checagens. John: preparação, diagnóstico e valor. Codex: revisão técnica e consolidação por solicitação de John. Revisão delegada não equivale a aceite autoral de cada colega nem a revisão independente formal do GitHub.
