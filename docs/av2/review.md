# Parecer técnico da AV2

**READY para a entrega na modalidade servidor de modelos.** Auditoria de
11/11/2026 na branch `av2`, base `2dbf442` com as alterações das fases 6 e 7.
A instalação frozen, os checks e a demonstração foram executados em uma cópia
limpa dos arquivos do candidato no Windows. [Checkpoints](checkpoints.md) ·
[Evidência da execução](evidence/phase-6/summary.json)

## Cobertura do enunciado

| Requisito | Como foi verificado |
| --- | --- |
| Arquivo texto append-only no disco | O E2E subiu dois processos, preservou os 1.130 bytes do primeiro ciclo e acrescentou dois eventos no segundo. [Teste E2E](../../tests/test_e2e.py). |
| Entradas e saídas relevantes | Cada sucesso inclui as seis features, a classe, a probabilidade e a versão. As saídas dos três exemplos no log coincidiram com as respostas HTTP, incluindo o perfil com categorias nulas. [Dicionário](log-format.md) · [Amostra real](evidence/phase-6/sample.jsonl). |
| Dados para histogramas, boxplots, KS e PSI futuros | A execução forneceu 90 eventos completos de sucesso por cenário, com deslocamento pareado nas variáveis numéricas e categorias preservadas. A referência Adult e as probabilidades comparáveis podem ser reconstruídas pelo guia. [Carga e referência](load.md) · [Resultados](demonstracao.md#resultados-da-execução-de-11112026). |
| Data e hora detalhadas | As 204 linhas tinham timestamp ISO 8601 UTC com microssegundos e IDs distintos. [Amostra real](evidence/phase-6/sample.jsonl). |
| `GET /metrics` compatível com Prometheus | O parser reconheceu contador e histograma. Os deltas por status coincidiram com a CLI e o JSONL nos dois lotes. O reinício zerou os contadores do processo. [Evidência](evidence/phase-6/summary.json). |
| Interpretação de latência, erros e retenção | O guia descreve os cálculos e as unidades. O roteiro usa as capturas reais para calcular frequências, quartis, média e taxas. Explica também a retenção do JSONL em disco e a janela de memória do processo. [Métricas](metrics.md) · [Demonstração](demonstracao.md). |
| Reprodução pelo README | Em cópia limpa, `uv sync --frozen` criou um ambiente novo a partir do cache. O startup documentado, os quatro exemplos e o bloco PowerShell de carga produziram 204 eventos. [README](../../README.md) · [Checkpoints](checkpoints.md). |

## Rastreabilidade de erros

Os campos `status_code`, `outcome`, `input_capture` e a entrada sanitizada
distinguem rejeições de falhas internas. Os testes cobrem JSON malformado antes
da inferência, categorias inválidas, campos extras, limite de captura, falha
interna, escrita concorrente e falha de gravação. Nas respostas de erro,
`output=null` e `error_type` identifica a categoria geral. A resposta HTTP é
a fonte dos detalhes de validação, como a lista de opções de uma categoria.
[Testes de monitoramento](../../tests/test_monitoring.py) · [Formato e limites](log-format.md).

## Achados e próximos passos

| Prioridade | Achado | Fechamento |
| --- | --- | --- |
| P1 | Teste anterior esperava HTTP 200 para uma categoria Unicode que o schema atual rejeita. | Testes separados cobrem sucesso com nulos e preservação do valor Unicode rejeitado no JSONL. Suíte completa com 79 aprovados. |
| P1 | Marcadores de merge no quadro de fases e no checklist da fase 4. | Plano consolidado, com evidências das fases 4 e 5 preservadas. |
| P1 | README descrevia regras da AV1 e omitia o fluxo completo de observabilidade. | README atualizado e caminho PowerShell executado no Windows. |

A execução Docker e a CI remota do commit final ficam para a equipe. Os blocos
Bash passaram por `bash -n` no Windows. A execução em Linux/macOS fica para
a revisão do grupo. A planilha opcional foi
omitida e os cálculos foram documentados com a evidência real. A segunda revisão
do grupo deve registrar o SHA efetivamente revisado e repetir o fluxo a partir
de um clone desse commit. [Guia de revisão](revisao-plano.md) · [Guia Docker](docker.md).
