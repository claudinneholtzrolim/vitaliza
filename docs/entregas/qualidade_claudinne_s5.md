# Checagens de qualidade — Claudinne, S5

Autoria original: **Claudinne — Grupo 01**. Revisão técnica e documentação por Codex, a pedido de John Neto, em 07/11/2026. A revisão preserva a autoria; não representa aceite autoral da versão revisada por Claudinne.

## Resultado e alcance

As duas bases regeneradas a partir do data room contêm 14.753 pagantes cada. As 14 regras da base de clusterização e as oito fórmulas complementares verificadas tiveram zero violações. A saída mantém os 14.753 pagantes, sem exclusão, imputação ou alteração do bruto. As ausências estruturais e os limiares exploratórios são marcações para interpretação.

Esta é uma conferência complementar de bases derivadas. Não certifica integralmente os 12 arquivos brutos, a qualidade dos clusters ou a eficácia de ações de retenção. A temporalidade dos eventos, os fusos e a deduplicação do bruto são tratados na preparação anterior; esta checagem testa coerência de janelas agregadas e recência, sem reauditar todos os eventos.

| Dimensão | Evidência nesta revisão | Limite |
|---|---|---|
| Completude | 759 ausências de proporção de vídeo; 177 de recência em 2026; 1.029 de nível; 1.491 de dias planejados | Ausência de proporção/recência acompanha falta de treino; onboarding não é imputado |
| Validade | Domínios de plano/canal, chaves, finitude e medidas obrigatórias não negativas conferidos | Limiares de volume não demonstram erro; esta revisão não revalida cada treino |
| Consistência | 14 regras e oito fórmulas sem violação; valores compartilhados conferidos por chave | Recalcular a fórmula de divergência BI/detalhe não elimina a divergência entre fontes |
| Unicidade | Chaves preenchidas, válidas, únicas; conjuntos iguais nas duas bases | Controle de duplicidade de treino pertence à preparação |
| Temporalidade | Janelas de 30/90 dias e recência coerentes pelas regras verificadas | Uso anterior à assinatura paga é possível no freemium; não prova dado posterior ao corte |

## Achados reproduzidos

| Medida | Pessoas | Interpretação |
|---|---:|---|
| Sem treino nos últimos 90 dias | 759 | 5,14% da base; permanecem na segmentação |
| Sem treino observado em 2026 | 177 | 1,20%; recência ausente, não zero |
| Nível do onboarding ausente | 1.029 | 6,97%; manter ausência |
| Dias planejados ausentes | 1.491 | 10,11%; manter ausência |
| Sinal de atividade anterior à assinatura paga | 395 | Heurística descritiva; o app permite treino gratuito antes do pagamento |
| Média por treino acima de 300 minutos em 90 dias | 12 | Investigar; não significa que 12 sessões individuais foram identificadas |
| Pelo menos 40 treinos em 30 dias | 46 | Investigar sem excluir automaticamente |
| União dos dois alertas anteriores | 58 | 0,39% da base; são alertas, não erros comprovados |
| Minutos em 30 dias acima do p99 | 147 | Limite relativo à amostra, sem descarte |
| Minutos em 90 dias acima do p99 | 148 | Limite relativo à amostra, sem descarte |
| Sistema com maiúsculas | 3.665 | A comparação de loja/sistema usa normalização em minúsculas |
| Anual com última cobrança de R$ 239,90 e assinatura >365 dias | 189 | Investigar histórico; contagem isolada não demonstra cobrança errada |
| Pendências de suporte maiores que aberturas nos últimos 90 dias | 730 | Janelas diferentes; pode haver ticket antigo pendente |

A proxy bruta mensal equivalente soma R$ 457.281,85; após taxas, R$ 405.539,32. Menos R$ 61.962,60 de custo de servir, resulta em R$ 343.576,72 de contribuição equivalente. São aproximações descritivas baseadas na última cobrança; anual dividido por 12. Não descontam estornos/chargebacks e não constituem receita contábil, LTV ou ROI.

## Correções sobre o original

Os dois anexos recebidos eram byte a byte iguais; foi mantido um único script canônico. SHA-256 comum: `a7980ee74a211ff2e1d8f122a21fbac5e6efeea9e75295d685e049b62cbdfb87`.

- Removida a frase que apresentava apenas quem treinou como disponível ao algoritmo. Ponte correta: 14.753 → 14.753, zero excluídos.
- Atividade anterior ao pagamento deixou de integrar `revisar`: o original marcava 451 pessoas nessa união; agora 58 ficam nos dois alertas de volume/duração. A diferença decorre da interpretação freemium, sem apagar a marcação descritiva.
- Cadastro seis/sete dias antes do início pago passou a observação descritiva; não é garantia universal do modelo de negócio.
- A proxy mensal é conferida contra a última cobrança observada e o divisor do plano, em vez de exigir R$ 39,90 para todos os mensais.
- A validação inicial interrompe em caso de duplicata, chave inválida, cobertura diferente, domínio desconhecido, valor obrigatório ausente/não finito ou divergência entre colunas compartilhadas. Igualdade de conjuntos de IDs sozinha não detectava duplicatas.
- Violações das regras/fórmulas passam a interromper a execução antes de novas saídas. Se uma execução falhar, saídas antigas não são evidência de aprovação atual.
- Resumo agregado e hashes das entradas são gravados localmente, junto às flags individuais, fora do Git público.

## Reprodução e validação

Na raiz, com o ambiente e os dados conforme README:

```sh
.venv/bin/python src/preparar_diagnostico_s5.py
.venv/bin/python src/checagens_qualidade_s5.py
.venv/bin/python -m unittest discover -s tests -v
```

Saídas ignoradas: `dados/processados/s5_claudinne/qualidade_flags.csv` e `resumo_qualidade.json`. O segundo contém contagens, fórmulas, ponte financeira e hashes das duas entradas.

Validação feita em cópia isolada da main `8d40886`, sem modificar a cópia de trabalho de outra sessão. Ambiente usado: Python 3.14, pandas 3.1.1, numpy 2.5.4, pyarrow 26.0.1. A preparação passou com suas âncoras e hashes. Os 24 testes passaram (16 existentes e oito novos), incluindo regressões de duplicidade, ausência financeira e interpretação do freemium. Três contas foram conferidas diretamente em usuários e pagamentos: exclusão de testes e proxies bruta/líquida conciliadas. Identificadores dessas conferências permanecem apenas na saída local privada.

## Revisão editorial e entropia

Informação agregada concentrada neste documento; README aponta para ele e o script mantém as regras executáveis. Foram conferidos denominadores, distinção entre sinal/erro, cobertura, unidades monetárias, autoria e ausência de dados individuais nos arquivos de publicação. A repetição das contagens entre resumo local e documento é intencional para reprodução e leitura independente; não foi atribuída pontuação estatística à frequência de palavras. A revisão técnica delegada por John foi concluída na consolidação S5. Não se atribui aceite autoral a Claudinne. A integração à main continua sujeita à aprovação externa exigida pelo GitHub.
