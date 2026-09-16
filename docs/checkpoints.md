# Checkpoints do projeto

## Fase 1 — fundação do repositório

Status: concluída em 15/09/2026.

### O que foi feito

- Publicado o checkpoint anterior da Fase 0 em `origin/main` no commit `bcb58a5`.
- Criado projeto Python em layout `src` para Python `>=3.12,<3.13`.
- Fixadas dependências diretas de runtime, desenvolvimento e build.
- Criados arquivos de segurança do repositório e diretórios das próximas fases.
- Gerado `uv.lock` e criado `.venv` novo somente a partir dele.
- Validado o import do pacote e de todas as dependências diretas.

### Arquivos alterados

- `.python-version`
- `pyproject.toml`
- `uv.lock`
- `.gitignore`
- `.env.example`
- `LICENSE`
- `src/careerpath/__init__.py`
- `models/.gitkeep`
- `scripts/.gitkeep`
- `examples/.gitkeep`
- `tests/.gitkeep`
- `docs/checkpoints.md`
- `docs/fases.md`

### Comandos e resultados observados

- `uv run --no-project --python 3.12 --with ...`: resolveu em ambiente temporário
  Python 3.12.14, BentoML 1.4.39, scikit-learn 1.9.1, Pydantic 2.13.5,
  pandas 3.0.5, Starlette 1.6.0, pytest 9.1.1, Ruff 0.16.7 e Hatchling 1.32.0.
- Validação com `tomllib`: `pyproject: ok`.
- `Test-Path .venv` antes do primeiro sync: `False`.
- `uv lock --python 3.12`: 83 pacotes resolvidos com Python 3.12.14.
- `uv sync --frozen --python 3.12`: ambiente criado, projeto construído e 81
  pacotes instalados. O uv avisou que não pôde usar hardlinks entre cache e
  destino e copiou os arquivos; isso afeta velocidade/espaço, não o resultado.
- Verificação de imports: `3.12.14 1.4.39 1.9.1 2.13.5 3.0.5 1.6.0 0.1.0`.
- Segundo `uv sync --frozen --python 3.12`: 81 pacotes conferidos; hash SHA-256
  do lock permaneceu `9131A7053FE08C472421215B469CB6D96BF1F85DC89842201772F2FD42D48869`.
- `uv run --frozen ruff check .`: `All checks passed!`.
- `uv run --frozen python -m compileall -q src`: exit code 0.
- `git diff --check`: exit code 0 antes da criação deste checkpoint.

### Resultados

A fundação instala em um ambiente `.venv` inicialmente ausente, usa Python
3.12.14 e importa todas as dependências fixadas. Nenhum dataset foi baixado,
nenhum modelo foi treinado, nenhuma métrica foi calculada e nenhum serviço foi
iniciado nesta fase.

### Pendências e riscos conhecidos

- Validar o lock também no Linux ocorrerá na CI da Fase 5.
- O serviço e a integração BentoML/ASGI ainda não existem; serão verificados nas
  Fases 3 e 4.
- O caminho offline completo só pode ser testado após criar o artefato local.
- O aviso de hardlink do uv pode tornar instalações locais mais lentas; se for
  recorrente, documentar `UV_LINK_MODE=copy`, sem transformá-lo em requisito.

### Próxima fase

Fase 2 — procurar novamente notebook/artefato anterior e, na ausência, implementar
e executar o treinamento reprodutível, persistir o pipeline completo e metadata,
registrar métricas reais e validar carregamento em processo novo.

## Fase 2 — modelo e pipeline de inferência

Status: concluída em 15/09/2026.

### O que foi feito

- Repetida a procura por notebook, dataset e artefato anterior; nenhum foi encontrado.
- Baixados explicitamente os três arquivos do Adult a partir do ZIP oficial da UCI.
- Implementadas leitura, normalização e remoção de sobreposição exata entre partições.
- Treinado um pipeline com imputação, escala, one-hot encoding e regressão logística.
- Comparado o modelo com `DummyClassifier(strategy="most_frequent")` no teste oficial.
- Persistidos pipeline completo, metadata, hashes, métricas, contagens e limitações.
- Validada a integridade antes do unpickle e a inferência em um processo Python novo.

### Arquivos alterados

- `src/careerpath/train.py`
- `src/careerpath/model.py`
- `scripts/download_data.py`
- `models/adult-income-v1.pkl`
- `models/metadata.json`
- `tests/test_train.py`
- `tests/test_model.py`
- `tests/test_download_data.py`
- `docs/checkpoints.md`
- `docs/fases.md`

Os arquivos em `data/raw/` são locais e continuam ignorados pelo Git.

### Comandos e resultados observados

- `uv run --frozen python scripts/download_data.py`: gravou `adult.data`,
  `adult.test` e `adult.names` em `data/raw/`.
- `uv run --frozen python -m careerpath.train`: treinou e persistiu o modelo.
- Contagens: 32.561 linhas originais de treino, 25 sobreposições exatas removidas,
  32.536 linhas usadas no treino e 16.281 linhas no teste.
- Modelo: accuracy `0.8331797801`, balanced accuracy `0.7312244263`, precision
  `0.6878324468`, recall `0.5379615185`, F1 `0.6037350452`, ROC-AUC
  `0.8825975677` e Brier `0.1142367999`.
- Matriz de confusão do modelo, classes `<=50K`/`>50K`:
  `[[11496, 939], [1777, 2069]]`.
- Baseline majoritário: accuracy `0.7637737240`, balanced accuracy `0.5`,
  precision/recall/F1 `0`, ROC-AUC `0.5` e Brier `0.2362262760`.
- SHA-256 de `adult.data`:
  `5b00264637dbfec36bdeaab5676b0b309ff9eb788d63554ca0a249491c86603d`.
- SHA-256 de `adult.test`:
  `a2a9044bc167a35b2361efbabec64e89d69ce82d9790d2980119aac5fd7e9c05`.
- SHA-256 do artefato:
  `cfc85186a943d1ec52b97a8c9ee4b675d948a69918ae958a6d72c222027bb716`.
- Processo novo: retornou classe `>50K`, probabilidade `0.6348314505` e versão
  `adult-income-v1` para o perfil literal de verificação.
- `uv run --frozen pytest -q -W error`: 8 testes passaram.
- `uv run --frozen ruff check .`: sem achados após ordenar um bloco de imports.
- `uv run --frozen python -m compileall -q src scripts tests`: exit code 0.
- `git diff --check`: exit code 0.

### Resultados

O repositório contém um pipeline treinado e versionado que supera o baseline nas
métricas registradas. O carregamento valida versão do scikit-learn e SHA-256 antes
do unpickle; inferência e startup futuro não precisam de rede nem de treinamento.

### Pendências e riscos conhecidos

- O Adult representa o Censo dos EUA de 1994 e a classe de renda é apenas um proxy
  histórico, não intenção de compra, necessidade profissional ou renda comprovada.
- Excluir atributos sensíveis não elimina vieses ou proxies presentes nas features.
- Categorias desconhecidas executam, mas não possuem efeito aprendido próprio.
- O artefato pickle só deve ser carregado do repositório confiável e com metadata
  correspondente; o hash detecta corrupção, não torna uma origem externa confiável.
- O serviço HTTP e sua validação de entrada ainda serão implementados na Fase 3.

### Próxima fase

Fase 3 — carregar o artefato local no serviço BentoML e expor `POST /predict` e
`GET /health`, sem download ou treinamento como fallback.

## Fase 3 — serviço BentoML

Status: concluída em 15/09/2026.

### O que foi feito

- Definido contrato Pydantic estrito para os seis campos de entrada e três de saída.
- Exposto `POST /predict` como API BentoML com objeto JSON na raiz.
- Montado `GET /health` por Starlette no mesmo serviço.
- Carregado o pipeline local uma vez por processo, com validações de versão e hash
  herdadas da Fase 2 e sem fallback de download ou treinamento.
- Corrigido o tratamento de `null` para que `workclass` e `occupation` cheguem aos
  imputadores treinados como valores ausentes.
- Criados três exemplos sintéticos válidos e um inválido, todos exercitados por HTTP.
- Desabilitada a telemetria local do BentoML na configuração de exemplo.

### Arquivos alterados

- `.env.example`
- `pyproject.toml`
- `src/careerpath/schema.py`
- `src/careerpath/service.py`
- `src/careerpath/model.py`
- `examples/case-1.json`
- `examples/case-2.json`
- `examples/case-3.json`
- `examples/invalid.json`
- `tests/test_schema.py`
- `tests/test_service.py`
- `tests/test_model.py`
- `docs/checkpoints.md`
- `docs/fases.md`

### Contrato HTTP observado

- Comando: `uv run --frozen bentoml serve careerpath.service:CareerPathService
  --host 127.0.0.1 --port 3000 --do-not-track`.
- `GET /health`: HTTP 200, `{"status":"ok","model_version":"adult-income-v1"}`.
- `case-1.json`: HTTP 200, classe `<=50K`, probabilidade `0.13588024571339077`.
- `case-2.json`: HTTP 200, classe `>50K`, probabilidade `0.5256289902834581`.
- `case-3.json`: HTTP 200, classe `<=50K`, probabilidade `0.01841773201019456`.
- `invalid.json`: HTTP 400 com detalhe indicando `age >= 17`.
- BentoML 1.4.39 converte `ValidationError` em HTTP 400; portanto, o 422 da Fase 0
  era apenas uma proposta e foi substituído pelo comportamento nativo verificado.
- O processo iniciado para o smoke test foi encerrado explicitamente após as chamadas.

### Comandos e resultados observados

- Ciclos TDD: falhas esperadas por módulos e exemplos ausentes, seguidas por estados
  verdes de 17 testes de schema, 3 de modelo e 11 de serviço no escopo de cada ciclo.
- `uv run --frozen pytest -q`: 37 testes passaram em 3,83 s.
- `uv run --frozen ruff check .`: `All checks passed!`.
- `uv run --frozen python -m compileall -q src scripts tests`: exit code 0.
- `git diff --check`: exit code 0.

### Compatibilidade de avisos

Starlette 1.6.0 avisa que seu `TestClient` migrará de `httpx` para `httpx2`;
BentoML 1.4.39 ainda usa APIs descontinuadas pelo Pydantic 2.13.5 e padrões antigos
do `pathspec`. O pytest trata avisos como erro e ignora somente essas mensagens,
categorias e módulos externos conhecidos. Nenhum pacote foi adicionado ou alterado.

### Resultados

O serviço inicia pelo CLI fixado, responde ao health e executa inferência local com
o artefato versionado. Entrada inválida, extra, malformada ou com tipo incorreto é
rejeitada; categorias desconhecidas e os dois campos anuláveis continuam executando.

### Pendências e riscos conhecidos

- O BentoML registra uma stack trace em nível ERROR para validação inválida, embora
  devolva o HTTP 400 esperado; é comportamento nativo da versão fixada.
- A Fase 4 ainda deve automatizar o E2E com processo real, espera limitada, reinício
  e encerramento somente do processo iniciado pelo teste.
- Ausência ou corrupção do artefato impede o startup de propósito; não há 503 quando
  o processo não consegue abrir a porta.
- O modelo mantém as limitações de uso e viés registradas no checkpoint da Fase 2.

### Próxima fase

Fase 4 — ampliar os testes de contrato e robustez e automatizar o E2E real com
reinício do serviço, mantendo pytest, Ruff e operação offline.

## Fase 4 — testes e robustez

Status: concluída em 15/09/2026.

### O que foi feito

- Confirmado o limite de classificação: probabilidade menor que `0,5` resulta em
  `<=50K`, enquanto `0,5` já resulta em `>50K`.
- Verificado que o startup falha com `FileNotFoundError` claro quando a metadata do
  artefato local não existe, sem tentar baixar dados ou treinar um modelo.
- Automatizado um E2E que executa o comando documentável do BentoML, aguarda o
  health com limite de 30 segundos e chama o predict por HTTP real.
- Executado um segundo ciclo na mesma porta para confirmar a inferência após um
  reinício completo.
- Isolado cada ciclo em seu próprio grupo de processos; o teste encerra a árvore
  identificada pelo PID iniciado, usa timeouts e confirma que a porta foi liberada.
- Mantidas as dependências e o código de produção inalterados.

### Arquivos alterados

- `tests/test_e2e.py`
- `tests/test_model.py`
- `tests/test_service.py`
- `docs/checkpoints.md`
- `docs/fases.md`

### Comandos e resultados observados

- `uv run --frozen pytest -q tests/test_e2e.py`: 1 teste passou em 14,79 s.
- `uv run --frozen pytest -q`: 41 testes passaram em 24,36 s, incluindo dois
  startups reais do serviço.
- `uv run --frozen ruff check .`: `All checks passed!`.
- `uv run --frozen python -m compileall -q src scripts tests`: exit code 0.

### Resultados

O contrato, os erros de entrada, o carregamento local, categorias desconhecidas,
campos anuláveis, health e inferência já cobertos pelas fases anteriores agora são
complementados por testes do threshold, do startup sem artefato e do ciclo HTTP
real com reinício. O E2E usa espera por condição em vez de pausa fixa.

### Pendências e riscos conhecidos

- O teste escolhe uma porta local livre antes do startup; permanece a pequena
  corrida inerente entre liberar a reserva e o BentoML ocupar a porta. A CI deve
  executar a suíte em ambiente isolado para evitar colisão com serviço compatível.
- O encerramento da árvore usa grupos de processo no Windows e no POSIX; a futura
  CI da Fase 5 validará também o caminho Linux.
- As limitações do modelo e os avisos externos fixados continuam os mesmos dos
  checkpoints das Fases 2 e 3.

### Próxima fase

Fase 5 — adicionar Dockerfile, comando único e GitHub Actions, mantendo instalação
frozen, Ruff, pytest e validação honesta do Docker quando o runtime estiver disponível.

## Fase 5 — diferenciais técnicos

Status: concluída em 16/09/2026.

### O que foi feito

- Criado `Dockerfile` para Python 3.12 e uv `0.12.5` fixados por digest,
  instalação a partir do `uv.lock` congelado, código-fonte, artefato local do
  modelo e usuário sem privilégios.
- Criado `.dockerignore` para excluir estado local, cache, dados brutos e segredos
  do contexto de build.
- Criado `justfile` com receitas para sync, serviço, lint, testes, check, demo E2E
  e ciclo manual do Docker.
- Criada CI para push na `main` e pull requests, com permissões mínimas de leitura,
  actions fixadas por SHA, uv fixado, instalação frozen, Ruff e pytest.
- Validado o container com build real e `GET /health` por HTTP local; o container
  temporário foi removido ao final do smoke test.

### Arquivos alterados

- `Dockerfile`
- `.dockerignore`
- `justfile`
- `.github/workflows/ci.yml`
- `docs/checkpoints.md`
- `docs/fases.md`

### Comandos e resultados observados

- `uv sync --frozen --python 3.12`: 81 pacotes conferidos.
- `uv run --frozen ruff check .`: `All checks passed!`.
- Parser YAML local: `ci yaml: ok`.
- `uv run --frozen pytest -q`: 41 testes passaram em 48,42 s.
- `uv run --frozen python -m compileall -q src scripts tests`: exit code 0.
- `docker build --tag careerpath-mlops:local .`: imagem construída com sucesso.
- Smoke test offline do container: UID `10001` e `GET /health` interno retornou
  `{"status":"ok","model_version":"adult-income-v1"}`.

### Resultados

O projeto possui caminhos reproduzíveis para qualidade e operação local: o Docker
inclui runtime, pacote, modelo local e ferramentas mínimas de execução, sem
dependências de desenvolvimento; o justfile reúne os comandos reais; e a CI
reproduz instalação congelada, lint e testes em Linux. As actions da CI ainda
executarão pela primeira vez após o push deste checkpoint.

### Pendências e riscos conhecidos

- O executável `just` não está instalado neste computador, portanto as receitas
  foram criadas mas ainda não foram executadas localmente. Nenhuma dependência
  global foi adicionada só para esse teste.
- A imagem deve ser reconstruída sempre que código, dependências ou artefato do
  modelo mudarem.
- A CI Linux e o justfile serão verificados novamente nas fases de documentação e
  auditoria, com os comandos publicados no README.

### Próxima fase

Model Gate 2 — trocar para GPT-5.6 Terra com esforço MEDIUM ou HIGH e responder
`CONTINUAR` antes da Fase 6.
