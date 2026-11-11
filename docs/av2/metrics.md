# AV2 — como interpretar `/metrics`

Verificado em 10/11/2026 com BentoML 1.4.39, Python 3.12.14 e o serviço CareerPath.
O endpoint nativo já atende ao formato Prometheus; não foi criado outro endpoint
nem adicionada dependência. O [baseline](phase-1-baseline.md) explica o ambiente e
o [formato do log](log-format.md) descreve as observações individuais.

## 1. Coletar duas fotografias da mesma instância

Na raiz, iniciar o serviço em um terminal:

```powershell
$env:CAREERPATH_LOG_PATH = 'logs/inference.jsonl'
uv run --frozen bentoml serve careerpath.service:CareerPathService --host 127.0.0.1 --port 3000 --do-not-track
```

Em outro terminal, coletar, chamar o endpoint e coletar novamente:

```powershell
curl.exe -fsS http://127.0.0.1:3000/metrics -o logs/metrics-before.prom
curl.exe -sS -X POST http://127.0.0.1:3000/predict -H 'Content-Type: application/json' --data-binary '@examples/case-1.json'
curl.exe -sS -X POST http://127.0.0.1:3000/predict -H 'Content-Type: application/json' --data-binary '@examples/invalid.json'
curl.exe -fsS http://127.0.0.1:3000/metrics -o logs/metrics-after.prom
```

O segundo perfil deve retornar 400; esse erro é proposital. Os exemplos acima
pressupõem serviço iniciado e pasta `logs/` criada pelo startup. Em Linux/macOS,
exportar a variável com `export` e usar `curl` no lugar de `curl.exe`.
Não reiniciar o servidor entre as duas coletas. Tráfego de outros clientes dentro
da janela também será contado. `/metrics` é texto de exposição, não JSON.

## 2. O que cada série significa

| Série | Interpretação |
| --- | --- |
| `bentoml_service_request_total` | Contador acumulado de pedidos, separado por endpoint/status |
| `bentoml_service_request_duration_seconds_count` | Quantidade de observações do histograma de duração |
| `bentoml_service_request_duration_seconds_sum` | Soma das durações, em segundos |
| `bentoml_service_request_duration_seconds_bucket` | Contagem acumulada até o limite `le`, em segundos |
| `bentoml_service_request_in_progress` | Gauge de pedidos em andamento; não é total histórico |

Filtrar `endpoint="/predict"` para os cálculos deste guia; não somar health com
inferência. As séries de requisição têm os labels `endpoint`, `http_response_code`,
`runner_name`, `service_name` e `service_version`. Buckets também têm `le`.
Agregar apenas séries do mesmo serviço e população. IDs de requisição ficam no
JSONL, não em labels Prometheus.

Na execução a partir do fonte, `runner_name`/`service_name` foram `careerpath` e
`service_version` foi `not available`. Esse label não substitui a versão do modelo
`adult-income-v1`, que está nas respostas e no JSONL. São métricas operacionais;
accuracy e ROC-AUC da metadata são medidas diferentes, obtidas no treinamento.

O Content-Type real foi `text/plain; version=1.0.0; charset=utf-8`. As capturas foram
lidas com o parser `prometheus_client.parser` disponível no ambiente. A
[documentação BentoML](https://docs.bentoml.com/en/latest/build-with-bentoml/observability/metrics.html)
descreve a instrumentação; os nomes acima também foram confirmados na versão instalada.

## 3. Janela, quantidade e média de latência

Para uma série de contador, usar `delta = valor_depois - valor_antes`, com os mesmos
labels e dentro da mesma instância. Série ainda não materializada pode valer zero
na primeira coleta, desde que a população/instância não tenha mudado.

```text
N = soma dos deltas de request_total, em todos os status de /predict
C = soma dos deltas de request_duration_seconds_count
S = soma dos deltas de request_duration_seconds_sum
latência média em ms = 1000 × S / C
```

Se `C=0`, a média é **N/A**, não zero. Somar as somas e as contagens antes de dividir;
não tirar média simples das médias de status ou de workers com volumes diferentes.
As chamadas concluídas normais da demonstração deram `N=C`; conexões interrompidas
ou outras condições operacionais podem exigir investigar diferenças.

Se um contador diminuiu, houve reset ou mudança de série: descartar essa janela
manual e coletar outra. Comparar também a identidade da instância e os horários:
nem todo reset é detectável por queda numérica, pois o contador pode já ter crescido
novamente. Se houver Prometheus externo, `rate`/`increase` tratam resets observados
na série; aplicar essas funções antes de agregar instâncias.
[Referência de funções Prometheus](https://prometheus.io/docs/prometheus/latest/querying/functions/).

## 4. Histogramas: retirar a acumulação dos buckets

Os limites reais observados, em segundos, foram:
`0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 120, 180, +Inf`.
O limite é inclusivo: `le="0.025"` conta durações menores ou iguais a 25 ms.

Primeiro obter, para cada limite `b`, o delta temporal do bucket, somando os status
escolhidos. Chamando esse valor de `B(b)`:

```text
frequência da primeira faixa = B(primeiro limite)
frequência da faixa (limite anterior, limite atual] = B(atual) - B(anterior)
frequência relativa = frequência da faixa / C
```

O bucket `+Inf` deve conter todas as observações selecionadas. Não somar buckets
cumulativos para calcular o número de pedidos, porque isso conta a mesma observação
várias vezes. Para um gráfico por faixas, usar as frequências não cumulativas.
A faixa final acima do último limite finito é aberta e deve ser identificada como tal.

Exemplo **real do primeiro ciclo**, com dois pedidos:

| Limite | Delta cumulativo | Frequência da faixa |
| --- | --- | --- |
| até 5 ms | 0 | 0 |
| até 10 ms | 0 | 0 |
| até 25 ms | 1 | 1 em (10, 25] ms |
| até 50 ms | 2 | 1 em (25, 50] ms |
| limites seguintes, inclusive `+Inf` | 2 | 0 em cada faixa seguinte |

Esses buckets descrevem distribuição aproximada: não revelam a latência individual
dentro da faixa. A [referência Prometheus sobre histogramas](https://prometheus.io/docs/practices/histograms/)
explica buckets, soma, contagem e estimativas de quantis.

## 5. Boxplot: usar as latências individuais do JSONL

Para um boxplot exato em relação aos dados coletados, usar `latency_ms` do JSONL.
Quartis obtidos por interpolação dos buckets são aproximações; não permitem recuperar
os outliers individuais ou os extremos observados. A captura do middleware e a
duração nativa do BentoML podem diferir, pois têm fronteiras distintas.

Escolher janela, endpoint e, se desejado, status; registrar a mesma seleção para
comparar gráficos. Para o conjunto escolhido:

1. Calcular Q1, mediana e Q3; neste guia, interpolação **linear**.
2. `IQR = Q3 - Q1`; limites de Tukey: `Q1 - 1,5 × IQR` e `Q3 + 1,5 × IQR`.
3. Os bigodes são o menor/maior valor observado dentro desses limites, não os
   próprios limites. Valores além dos limites são outliers.
4. Sem observações, apresentar N/A; com poucas observações ou IQR zero, indicar
   o tamanho da amostra e manter a convenção declarada.

Código executável na raiz com o ambiente do projeto (`uv run python`), usando a
amostra sintética capturada nesta fase. Para o arquivo vivo, trocar o caminho por
`logs/inference.jsonl` e filtrar timestamps UTC conforme a janela desejada:

```python
from pathlib import Path
import pandas as pd

path = Path("docs/av2/evidence/phase-3/inference-sample.jsonl")
frame = pd.read_json(path, lines=True)
latency = pd.Series(dtype="float64")
if not frame.empty:
    latency = pd.to_numeric(frame.loc[frame["endpoint"].eq("/predict"), "latency_ms"])
if latency.empty:
    print("N/A: sem observações")
else:
    q1, median, q3 = latency.quantile([0.25, 0.5, 0.75], interpolation="linear")
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    inside = latency.between(lower, upper)
    print({
        "n": len(latency), "q1_ms": q1, "median_ms": median, "q3_ms": q3,
        "lower_whisker_ms": latency[inside].min(),
        "upper_whisker_ms": latency[inside].max(),
        "outliers_ms": latency[~inside].tolist(),
    })
```

A convenção de interpolação está documentada no
[pandas.Series.quantile](https://pandas.pydata.org/docs/reference/api/pandas.Series.quantile.html).
Para desenhar o boxplot numa planilha, importar a coluna `latency_ms`, aplicar a
mesma convenção de quartis/bigodes e inserir o gráfico. Não usar as médias ou os
buckets como se fossem uma lista de latências individuais.

Exemplo **didático**, separado da captura: latências `[10, 20, 30, 40, 200]` ms
dão Q1=20, mediana=30, Q3=40, IQR=20; bigodes em 10 e 40, com 200 como outlier.

## 6. Taxas de erro e volume

Usar o mesmo endpoint, serviço e janela em numerador e denominador:

```text
falhas HTTP (%) = 100 × delta(contadores 4xx + 5xx) / N
falhas do servidor (%) = 100 × delta(contadores 5xx) / N
requisições por segundo = N / duração da janela em segundos
```

Se `N=0`, as taxas percentuais são **N/A**. Respostas 4xx indicam rejeição de pedidos,
e não necessariamente defeito do servidor. Falha de rede vista pelo cliente deve
ser reportada separadamente; não inventar um 500 quando não houve resposta HTTP.

Exemplo **didático**: 20 pedidos, 2 respostas 4xx e 1 resposta 5xx dão 15% de falhas
HTTP e 5% de falhas do servidor. Exemplo **real desta demonstração**, em cada ciclo:
1 resposta 200 e 1 resposta 400 dão 50% de falhas HTTP e 0% de falhas do servidor.
O erro foi gerado de propósito; esses dois pedidos não são benchmark de desempenho.

## 7. Por quanto tempo os dados ficam disponíveis

| Informação | Preservação neste projeto |
| --- | --- |
| Contadores/histogramas expostos pelo runtime | Acumulados da instância atual; voltaram a zero após reinício no E2E |
| Histórico de várias coletas de `/metrics` | Não existe automaticamente; salvar snapshots ou instalar coletor externo |
| Snapshots `.prom` exportados | Permanecem no arquivo até sua remoção; uma coleta não contém o histórico inteiro |
| Eventos JSONL | Preservados no disco com append; sem rotação/expiração automática; remoção do arquivo/disco elimina o histórico |
| Logs em container | Sem volume, remover o container pode removê-los; validação de volume fica na fase 5 |

Não existe uma retenção configurada de “X dias” para `/metrics` neste projeto.
Arquivos temporários internos do runtime não constituem uma interface de histórico.
Um Prometheus externo teria armazenamento e retenção próprios, ainda não implantados.
Não calcular deltas manuais através de reinícios: a captura inicial do segundo
ciclo foi zero mesmo após o primeiro acumular dois pedidos.

## 8. Evidências e reprodução

O E2E em `tests/test_e2e.py` inicia o serviço real duas vezes e verifica parser,
status, deltas, soma/contagem, monotonicidade dos buckets, frequência por faixa e
reset. Encerra somente os processos iniciados pelo teste e confirma a porta liberada.

```powershell
uv run --frozen pytest -q tests/test_e2e.py -o faulthandler_timeout=40
```

Captura versionada da execução direcionada (**1 teste passou em 17,82 s**):

- [Antes da carga](evidence/phase-3/metrics-0-before.prom).
- [Depois da carga](evidence/phase-3/metrics-0-after.prom).
- [Após reiniciar, antes da nova carga](evidence/phase-3/metrics-1-before.prom).
- [Resumo dos dois ciclos](evidence/phase-3/metrics-summary.json).
- [Quatro eventos sintéticos de inferência](evidence/phase-3/inference-sample.jsonl).

No primeiro ciclo, soma nativa `0.06805769999982658` s e contagem 2 resultaram em
**34,02885 ms** de média. No segundo, soma `0.07001620000028197` s e contagem 2
resultaram em **35,00810 ms**. Valores mudam entre execuções; os arquivos acima
registram aquela execução, e não uma promessa de latência.

Foram usadas somente features sintéticas e os exemplos do projeto. A fase 4
acrescentará carga maior e reproduzível. Planilha é um apoio recomendado pelo
enunciado; nesta fase o guia e as capturas fornecem os dados e o método, sem arquivo
de planilha ou dashboard novo.
