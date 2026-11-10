# AV2 — baseline e decisões de integração

Verificado em 10/11/2026, branch `av2`, HEAD `496d277`.
Estado: fase 1 concluída; logging de entradas/saídas permanece para a fase 2.
As alterações documentais existentes da fase 0 foram preservadas.

## Ambiente e verificações

| Item | Resultado observado |
| --- | --- |
| Python | 3.12.14 |
| uv | 0.12.5, instalado localmente em `.bentoml/tools/bin/uv.exe` |
| BentoML | 1.4.39 |
| Ambiente virtual | `.venv/`, com as dependências exatas do lock |
| Conferência frozen offline | `Checked 81 packages in 12ms` |
| Suíte completa | **41 passed in 47.25s**, incluindo serviço HTTP com reinício |
| Ruff | `All checks passed!` |

O código, os testes existentes, o modelo, o `pyproject.toml` e o lock não foram
alterados. `.bentoml/` e `.venv/` já são ignorados pelo Git.

O download do Python para `.bentoml/python/` falhou ao renomear o diretório com
erro Windows 5 (acesso negado). A instalação em `%LOCALAPPDATA%/Temp/careerpath-av2-python/`
funcionou. A causa do bloqueio no Desktop não foi determinada. Se a limpeza do
Windows remover esse Python temporário, recriar o ambiente; uma instalação normal
de Python 3.12 e uv também atende ao projeto. Nenhuma ferramenta foi instalada globalmente.

## Comandos da retomada

Executados em PowerShell, na raiz. As variáveis valem apenas para o processo atual:

```powershell
$env:PATH = "$PWD\.bentoml\tools\bin;$env:PATH"
$env:UV_CACHE_DIR = "$PWD\.bentoml\cache"
$env:UV_PYTHON_INSTALL_DIR = "$env:LOCALAPPDATA\Temp\careerpath-av2-python"
$env:BENTOML_DO_NOT_TRACK = 'True'
$env:BENTOML_HOME = "$PWD\.bentoml\runtime"
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'

uv sync --frozen --python 3.12 --offline
uv run --frozen pytest -vv -o faulthandler_timeout=45
uv run --frozen ruff check .
```

`--offline` serviu à conferência final, após os downloads; no primeiro setup, omitir
essa opção. O limite de threads reduziu uso simultâneo de recursos nas verificações;
não há evidência de que uma biblioteca numérica tenha causado o travamento anterior.

## Serviço real e métricas

Foi usada uma porta livre, `55506` na captura final:

```powershell
uv run --frozen bentoml serve careerpath.service:CareerPathService --host 127.0.0.1 --port 55506 --do-not-track
```

| Chamada | Resultado |
| --- | --- |
| `GET /health` | 200; `status=ok`, `model_version=adult-income-v1` |
| `POST /predict`, `examples/case-1.json` | 200; classe `<=50K`, probabilidade `0.13588024571339077` |
| `POST /predict`, `{"age":-1}` | 400; perfil inválido/incompleto |
| `POST /predict`, corpo `{` | 400; JSON malformado |
| `GET /metrics`, antes/depois | 200; formato parseado por `prometheus_client.parser` já instalado |

Content-Type observado: `text/plain; version=1.0.0; charset=utf-8`.
A árvore de processos iniciada pela sondagem foi encerrada e a porta liberada.

Séries observadas: `bentoml_service_request_total` e
`bentoml_service_request_duration_seconds_{bucket,sum,count}`. Labels de requisição:
`endpoint`, `http_response_code`, `runner_name`, `service_name`, `service_version`;
buckets também têm `le`. As durações são em segundos. Para `/predict`, runner e
serviço são `careerpath`; `service_version` é `not available` nesta execução de
código-fonte e não equivale à versão `adult-income-v1` do modelo.

Entre as capturas, os deltas de `request_total` para `/predict` foram: **200 = 1,
400 = 2, 500 = 0**. A soma dos deltas dos buckets `le="+Inf"` foi **3**, confirmando
o registro das três chamadas no histograma. Não é necessário criar outro `/metrics`.

## Integração definida para a fase 2

1. Registrar pela API pública `CareerPathService.add_asgi_middleware(Classe, **opcoes)`
   após a declaração do serviço. Não modificar a biblioteca instalada.
2. Capturar na camada HTTP do serviço inteiro e filtrar `/predict`; a captura deve
   envolver mensagens ASGI `receive`/`send` sem alterá-las. Não instrumentar somente
   o app de health ou a função de inferência.
3. A sondagem temporária observou status **200, 400, 400 e 500**, preservou o corpo
   válido e confirmou que entradas inválidas não chegaram à inferência. O 500 veio
   de exceção injetada, não de falha espontânea do modelo.
4. Criar/validar o `FileHandler` no worker durante `@bentoml.on_startup` e fechá-lo
   em `@bentoml.on_shutdown`. Evitar abrir arquivo no import executado também pelo
   supervisor. Middleware e startup devem usar o mesmo logger nomeado, com handler
   idempotente e sem duplicação entre contextos de teste.
5. Na sondagem, `PermissionError` simulado ao abrir o handler impediu completar o
   lifespan. Os testes permanentes da implementação real, incluindo falha posterior
   de escrita, continuam pertencendo à fase 2.
6. Integrar `workers=1` explicitamente no decorator na fase 2. O default atual já
   resultou em um worker, confirmado por configuração e árvore de processos.

No Windows, `.venv/Scripts/python.exe` lança o interpretador base com os mesmos
argumentos. A sondagem inicialmente contou ambos como workers. A relação pai/filho
confirmou um launcher e um interpretador efetivo, com o mesmo `--worker-id 1`;
somente o interpretador efetivo executa a aplicação e seria escritor do log.

A leitura da versão instalada também confirmou o fluxo: `Service.add_asgi_middleware`
registra a classe, `ServiceAppFactory.middlewares` monta a pilha e
`input_spec.from_http_request` executa a validação dentro do endpoint.

## Interrupção e recuperação

O usuário precisou reiniciar o PC. Na retomada, `middleware-result.json` continha
resultado positivo anterior ao reinício, mas `pytest.log` e `server.log` da execução
interrompida estavam vazios. Eles não comprovavam suíte ou servidor aprovados.

Havia verificações concorrentes e o primeiro E2E em execução restrita havia falhado,
sem diagnóstico final preservado. Após reiniciar, a suíte completa e o servidor
passaram em execuções sequenciais com acesso aos subprocessos locais.
**Os registros não identificam a causa do travamento do sistema operacional.**
Não há base para atribuí-lo ao código, antivírus, memória ou skill.

Na retomada, verificações pesadas foram serializadas, pytest exibiu cada teste com
diagnóstico de espera, e o servidor teve limite de startup e encerramento controlado.
Nenhuma sondagem de servidor desta retomada permaneceu em execução.

Capturas e experimentos locais, ignorados pelo Git, ficam em `.bentoml/phase1/`:
`probe.py`, `middleware-result.json`, `cli-result.json`, `metrics-before.prom`,
`metrics-after.prom` e `metrics-check.json`. São evidências exploratórias da fase 1,
não implementação de logging ou substitutos dos testes permanentes da fase 2.
