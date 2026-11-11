# Roteiro da demonstração da AV2

1. Na raiz do clone da branch `av2`, siga a primeira execução do README. Mostre
   `GET /health` com HTTP 200 e `model_version=adult-income-v1`. Anote o caminho
   do JSONL exibido no terminal.
2. Envie os três exemplos válidos e o inválido. Abra o log e compare a entrada
   e a saída de um HTTP 200 com a resposta recebida. No HTTP 400, mostre
   `outcome=client_error`, a idade rejeitada e `output=null`.
3. Rode o bloco de carga do README. Mostre as 100 linhas novas de cada cenário
   e compare as capturas antes/depois de `/metrics` na mesma instância.
   A seed 42 e `--invalid-every 10` produzem 90 sucessos e 10 rejeições por lote.
4. Mostre como obter a distribuição de latência e a taxa de erros com os
   cálculos abaixo. Use entradas e saídas dos eventos completos e bem-sucedidos
   para discutir as distribuições do modelo.
5. Se for demonstrar persistência, reinicie com o mesmo `CAREERPATH_LOG_PATH`.
   Confirme que o conteúdo anterior continua no disco e que a nova instância
   inicia seus contadores em zero. O JSONL permanece até remoção manual. As
   métricas ficam em memória enquanto durar o processo, e as capturas salvas
   no disco podem ser consultadas depois.

[Comandos do README](../../README.md#primeira-execução) ·
[Formato do JSONL](log-format.md) · [Guia de métricas](metrics.md)

## Resultados da execução de 11/11/2026

Em uma cópia limpa dos arquivos da AV2 no Windows, Python 3.12.14 e BentoML
1.4.39, os quatro exemplos retornaram 200, 200, 200 e 400. Os dois lotes
acrescentaram 200 eventos, totalizando 204 com os exemplos. Cada lote teve
90 respostas 200, 10 respostas 400, zero 5xx e zero falhas de comunicação,
com os mesmos totais na CLI, no JSONL e nas métricas.
[Capturas e respostas](evidence/phase-6/summary.json) ·
[Amostra JSONL](evidence/phase-6/sample.jsonl)

| Lote | 200 antes → depois | 400 antes → depois | Erros HTTP | Erros do servidor |
| --- | --- | --- | --- | --- |
| Baseline | 3 → 93 | 1 → 11 | (10 + 0) / 100 = 10% | 0 / 100 = 0% |
| Shifted | 93 → 183 | 11 → 21 | (10 + 0) / 100 = 10% | 0 / 100 = 0% |

No baseline, o bucket cumulativo de 5 ms cresceu de 0 para 7 e o de 10 ms
passou de 2 para 66. Portanto, houve 7 observações até 5 ms e
`(66 − 2) − (7 − 0) = 57` entre 5 e 10 ms. As demais foram 35 entre
10 e 25 ms e 1 entre 50 e 100 ms. Os intervalos restantes tiveram frequência
zero, e o delta de `+Inf` foi 100. A latência média do histograma foi
`(1,124253 − 0,121808) s / 100 ≈ 10,02 ms`.

O boxplot usa as 100 latências individuais do JSONL de cada lote, incluindo os
400, com quartis lineares. Os limites dos bigodes são as observações extremas
dentro de `[Q1 − 1,5 × IQR, Q3 + 1,5 × IQR]`, onde `IQR = Q3 − Q1`.

| Lote | Q1 | Mediana | Q3 | Bigodes | Pontos além dos bigodes |
| --- | ---: | ---: | ---: | --- | ---: |
| Baseline | 8,26 ms | 9,44 ms | 10,56 ms | 4,94 a 12,97 ms | 9 |
| Shifted | 8,48 ms | 9,28 ms | 10,27 ms | 6,23 a 12,80 ms | 12 |

Para analisar o modelo, selecione os 90 eventos com `outcome=success` e
`input_capture=complete` em cada lote. Nas 90 comparações pareadas, idade e
jornada aumentaram em 12 e as categorias permaneceram iguais. As medianas de
idade passaram de 37 para 49, as de horas semanais de 36 para 48 e as das
probabilidades de aproximadamente 0,128 para 0,231. O guia de carga descreve
como reconstruir o conjunto Adult de referência e calcular probabilidades
comparáveis com o mesmo modelo para análises futuras. [Guia de carga](load.md).

O material de análise fica no texto e no JSON de evidência, com os deltas por
faixa, os quartis e as taxas. A planilha é opcional no enunciado e foi omitida.
