# Carga reproduzível e suficiência dos dados

Execute o serviço em um terminal, na raiz do projeto. Use um caminho de log novo
para cada rodada comparável. Os comandos de análise abaixo usam
`logs/phase4-inference.jsonl` e pressupõem que o arquivo está vazio ao iniciar.

```powershell
$env:CAREERPATH_LOG_PATH = 'logs/phase4-inference.jsonl'
uv run --frozen bentoml serve careerpath.service:CareerPathService --host 127.0.0.1 --port 3000 --do-not-track
```

Em outro terminal, faça as três rodadas em sequência com o mesmo processo.

```powershell
function Invoke-LoadBatch($Scenario, $Count, $InvalidEvery, $Tag) {
    curl.exe -fsS http://127.0.0.1:3000/metrics -o "logs/phase4-$Tag-before.prom"
    if ($LASTEXITCODE -ne 0) { throw "Falha ao obter as métricas iniciais" }
    uv run --frozen python scripts/generate_load.py --url http://127.0.0.1:3000 --count $Count --seed 42 --scenario $Scenario --invalid-every $InvalidEvery
    if ($LASTEXITCODE -ne 0) { throw "Carga $Tag terminou com falhas inesperadas" }
    curl.exe -fsS http://127.0.0.1:3000/metrics -o "logs/phase4-$Tag-after.prom"
    if ($LASTEXITCODE -ne 0) { throw "Falha ao obter as métricas finais" }
}

Invoke-LoadBatch baseline 100 10 baseline
Invoke-LoadBatch shifted 100 10 shifted
Invoke-LoadBatch baseline 5 0 short
```

A receita opcional `just load shifted 100 10` chama o mesmo gerador com a seed 42
e o endereço padrão. A CLI imprime um resumo JSON por lote. `sent` conta as
tentativas. `2xx`, `4xx`, `5xx`, `other_status` e `network_errors` dividem esse
total entre respostas HTTP e falhas de comunicação. `unexpected` conta resultados
que diferem do status esperado, 200 para perfil válido e 400 para inválido. O
processo retorna 0 quando todos correspondem, 1 quando há resultado inesperado e
2 quando os argumentos são inválidos. Cada operação HTTP usa timeout de 10 s.

## Cenários e resultado observado

As categorias são sorteadas dos três perfis de exemplo, incluindo valores nulos.
Em `baseline`, as idades vão de 22 a 55 e as jornadas de 28 a 48 horas por semana.
Com a mesma seed e tamanho, `shifted` preserva as categorias e acrescenta 12 a
cada idade e a cada jornada. `--invalid-every 10` substitui a idade do décimo
pedido de cada grupo por `-1`. `--invalid-every 0` mantém todos os perfis válidos.

| Lote | Pedidos | HTTP 200 | HTTP 400 | HTTP 500 | Linhas JSONL |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 100 | 90 | 10 | 0 | 100 |
| Shifted | 100 | 90 | 10 | 0 | 100 |
| Curto, sem erros programados | 5 | 5 | 0 | 0 | 5 |

As contagens do gerador, os deltas de `/metrics` por status e os eventos no JSONL
coincidiram nos três lotes. Cada lote principal teve 10% de rejeições programadas.
Os dados, tipos e estatísticas observados estão no [resumo da execução](evidence/phase-4/summary.json).
Use o [guia de métricas](metrics.md) para calcular os deltas entre as capturas.

## Conferir os campos para análise

Separe as janelas pelos limites de cada lote. O exemplo usa um servidor dedicado
à demonstração e um arquivo novo. Os três lotes acima geram 205 linhas de
`/predict` nessa ordem.

```python
import json
from pathlib import Path

import pandas as pd

path = Path("logs/phase4-inference.jsonl")
with path.open(encoding="utf-8") as stream:
    events = pd.json_normalize([json.loads(line) for line in stream])

assert len(events) == 205
fields = [
    "input.age",
    "input.hours_per_week",
    "output.probability_above_50k",
    "latency_ms",
]
for scenario, batch in (
    ("baseline", events.iloc[:100]),
    ("shifted", events.iloc[100:200]),
    ("short", events.iloc[200:]),
):
    usable = batch.loc[batch["status_code"].eq(200) & batch["input_capture"].eq("complete")]
    numeric = usable[fields].apply(pd.to_numeric, errors="raise")
    print(scenario, len(usable), numeric.nunique().to_dict())
    print(numeric.describe().loc[["min", "50%", "max"]])
```

Nos lotes principais, idade e horas foram lidas como inteiros e probabilidade
e latência como valores de ponto flutuante. Cada uma das quatro colunas variou
em ambos os lotes. Entre as 90 linhas válidas por cenário, a mediana da idade
foi de 37 para 49, a da jornada foi de 36 para 48 e a da probabilidade prevista
foi de 0,1282 para 0,2310. A mudança de entrada foi confirmada par a par, com
categorias iguais. Os eventos 400 ficam disponíveis para contar erros e são
excluídos das distribuições de perfis aceitos e probabilidades. Para estudar a
latência de rejeições, selecione o status 400 como um grupo separado.

## Referência para comparações posteriores

Os lotes sintéticos servem para demonstrar a coleta sob uma mudança controlada.
A referência do modelo é a partição de treino de Census Income, também chamado
Adult, da UCI. O projeto usa o ID 20 e o DOI `10.24432/C5GP7S`.
[Census Income na UCI](https://archive.ics.uci.edu/dataset/20/census%2Bincome).

Para reconstruir a referência, use os arquivos em `data/raw/`. Se precisar obtê-los
em uma execução futura, rode `uv run --frozen python scripts/download_data.py`.
Confira os hashes da metadata, aplique a mesma limpeza do treino e remova as linhas
de treino idênticas às do teste. Passe as seis features pelo pipeline salvo e
extraia a coluna da classe `>50K`. Assim, a referência de saída usa a mesma escala
de probabilidade observada no serviço.

```python
import hashlib
from pathlib import Path

from careerpath.model import load_artifact
from careerpath.train import FEATURES, load_adult, remove_test_overlap

root = Path("data/raw")
pipeline, metadata = load_artifact(
    Path("models/adult-income-v1.pkl"), Path("models/metadata.json")
)
for name in ("adult.data", "adult.test"):
    actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
    if actual != metadata["data_sha256"][name]:
        raise ValueError(f"SHA-256 diferente da metadata em {name}")

train = load_adult(root / "adult.data")
test = load_adult(root / "adult.test", test_file=True)
reference, removed = remove_test_overlap(train, test)
assert len(reference) == metadata["counts"]["train_used"]
assert removed == metadata["counts"]["overlap_removed"]
features = reference[FEATURES]
positive_index = list(pipeline.classes_).index(">50K")
probability = pipeline.predict_proba(features)[:, positive_index]
export = features.rename(columns={
    "marital-status": "marital_status",
    "hours-per-week": "hours_per_week",
}).assign(
    probability_above_50k=probability,
    model_version=metadata["model_version"],
)
export.to_json(root / "adult-reference-v1.jsonl", orient="records", lines=True)
```

A metadata registra 32.536 linhas após remover 25 sobreposições. A exportação
em `data/raw/` fornece a referência para futuras comparações por KS e PSI. Os
resultados medidos nesta fase vêm da carga sintética.
