# Entrega de valor e priorização da S5

Atualização de responsabilidade em 03/11/2026: John assumiu a frente anteriormente associada à Marcela, que deixou o projeto. A preparação financeira dessa frente está concluída e disponível para revisão do grupo. Isso não representa a conclusão do sistema completo de retenção.

## Escopo concluído

- Base de valor com uma linha por pagante no corte de 30/09/2026 e chave `user_id` para integração.
- Contribuição equivalente mensal por plano e canal, após taxas e custo de servir.
- Cortes descritivos por engajamento, sem inventar clusters ou risco individual.
- Cenários de equilíbrio de contato e oferta, distinguindo hipóteses de resultados observados.
- Capacidade e orçamento do CRM, com ofertas e reservas hipotéticas de IA identificadas.
- Relatório de leitura, síntese para integração, tabelas agregadas, filtros e auditoria local.
- Conferência de três pagamentos diretamente no bruto e conciliação com a preparação anterior.

## Reprodução e localização

Com os arquivos do data room na estrutura já definida no README, executar na raiz:

```sh
.venv/bin/python src/preparar_diagnostico_s5.py
.venv/bin/python src/valor_priorizacao_s5.py
.venv/bin/python -m unittest discover -s tests -v
```

As duas primeiras etapas geram as bases e os textos. A verificação executa os 16 testes disponíveis, aprovados na preparação desta entrega. Para exportar o PDF no macOS, com Swift instalado:

```sh
swift src/exportar_valor_s5.swift
```

| Artefato local | Finalidade |
|---|---|
| `dados/saidas/s5_valor_priorizacao/John_Valor_Priorizacao_S5.md` e PDF equivalente | Leitura e discussão da frente financeira |
| `dados/saidas/s5_valor_priorizacao/sintese_para_relatorio.md` | Integração ao texto coletivo |
| `dados/saidas/s5_valor_priorizacao/valor_por_plano_canal.csv` | Conciliação da carteira por plano e canal |
| `dados/saidas/s5_valor_priorizacao/valor_por_plano_engajamento.csv` | Contexto descritivo para discutir segmentos |
| `dados/saidas/s5_valor_priorizacao/cenarios_equilibrio.csv` | Sensibilidade de horizonte, tarifa, contato, oferta e IA |
| `dados/saidas/s5_valor_priorizacao/capacidade_orcamento.csv` | Limites de capacidade e compromissos de ofertas |
| `dados/saidas/s5_valor_priorizacao/filtros.csv` e `qualidade_financeira.csv` | Ponte dos filtros e auditoria |
| `dados/processados/s5_valor_priorizacao/base_valor_corte.csv` | Integração individual por `user_id` |
| `dados/processados/s5_valor_priorizacao/manifesto_validacao.json` e `conferencia_tres_registros.csv` | Rastreabilidade local e verificações contra os pagamentos |

Conforme a revisão de Leonardo no [PR #4](https://github.com/leonardomoraesmendes/vitaliza/pull/4#discussion_r4419110912), dados, relatórios e saídas permanecem em `dados/`, fora do Git. A execução local com o data room é o caminho de acesso reproduzível. Os arquivos não foram publicados como anexos nem disponibilizados por links pessoais com acesso presumido.

## Integração com as demais frentes

| Responsável | Encaminhamento |
|---|---|
| John | Preparação e diagnóstico; também valor e critérios de priorização, antes associados à Marcela |
| Leonardo | Clusterização e validação dos grupos; integrar os rótulos por `user_id`, um para um |
| Kiril | Personas apoiadas nos clusters e nos comportamentos observados |
| Claudinne | Revisão de qualidade, tratamentos e limitações com apoio dos filtros e decisões |

Esses encaminhamentos preservam a divisão registrada na entrega anterior de John; não atribuem novas tarefas aos colegas. A tabela financeira mantém `cluster` e `uplift` sem preenchimento até que essas informações existam.

## Dependências para a decisão final

A preparação econômica e seus critérios estão concluídos. A priorização individual exige clusters, elegibilidade, efeito incremental estimado e custo real de IA. Receita da carteira não é LTV nem retorno de campanha. Cenários de meses adicionais e limiares de uplift não são previsões. O experimento de agosto testa push e e-mail; não demonstra automaticamente o efeito de WhatsApp ou CS.

A incorporação à `main` depende de revisão e de uma aprovação, conforme o fluxo do repositório. Código desta frente: [`src/valor_priorizacao_s5.py`](../../src/valor_priorizacao_s5.py), [`src/exportar_valor_s5.swift`](../../src/exportar_valor_s5.swift). Decisões: [`decisoes.md`](../../decisoes.md). Testes: [`tests/test_valor_priorizacao_s5.py`](../../tests/test_valor_priorizacao_s5.py).
