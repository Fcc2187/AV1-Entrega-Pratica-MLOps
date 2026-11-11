# AV2 — checkpoints

Este histórico é da AV2. `docs/checkpoints.md` continua sendo o registro da AV1.
Os resultados antigos não substituem verificações atuais.

## Preparação — elaboração do planejamento

Data: 10/11/2026.
Estado: planejamento elaborado; implementação não iniciada.

### Contexto confirmado

- Branch atual: `av2`.
- Commit de origem observado: `d2982c2` (`build: add phase 5 delivery automation`).
- Árvore de trabalho limpa antes da criação dos documentos da AV2.
- O enunciado permite continuar o serviço da AV1 e a modalidade aplicável é a 1.
- Código, modelo, exemplos e testes da AV1 permanecem necessários para a continuação.
- Documentação da AV1 é histórico/contexto e será preservada.

### Arquivos criados

- `docs/av2/escopo.md`: requisitos, decisões propostas, dados, métricas e preservação.
- `docs/av2/fases.md`: tarefas, interfaces, arquivos, verificações e critérios de aceite.
- `docs/av2/checkpoints.md`: este registro e formato das próximas atualizações.

### Verificações desta etapa

- Lidos enunciado, código de serviço e schema, configurações, testes relevantes,
  download de dados, CI, fases e checkpoints da AV1.
- Conferidos Git, branch e disponibilidade de comandos; `uv` não foi localizado
  no PATH desta sessão. Não houve instalação de dependências.
- Consultadas referências oficiais de logging Python/BentoML e métricas.
- Não foram executados servidor, carga, testes de aplicação ou Docker nesta etapa.
- Revisados requisitos e tarefas: logging, dados de entrada/saída, erros antes da
  inferência, métricas, cálculos, retenção e demonstração têm fases correspondentes.
- `git diff --check`: sem erros nos arquivos rastreados; os documentos novos ainda
  estão não rastreados e receberam verificação textual separada.
- Links locais entre os três documentos conferidos com `Test-Path`: todos existem.
- `git status --short`: somente `?? docs/av2/`; nenhum arquivo da AV1 foi alterado.

### Decisões propostas

- Manter BentoML, Adult, modelo e contratos existentes.
- Captura na camada HTTP para incluir erros anteriores à função de inferência.
- JSONL append-only, caminho configurável e dados individuais para análise futura.
- Aproveitar `/metrics` nativo; confirmar versão, nomes e comportamento em runtime.
- Separar planejamento AV2 em `docs/av2/`, sem reescrever o histórico da AV1.
- Não transportar os gates de modelos e prazos antigos para a nova entrega.

### Pendências e riscos

- Validar ambiente/uv e baseline atual na fase 1.
- Confirmar integração pública do middleware e um único escritor no BentoML 1.4.39.
- Confirmar `/metrics` e persistência do arquivo com execução real.
- Preparar diretório/volume gravável no Docker e CI para a branch `av2`.
- README precisa ser desenvolvido; contém somente o título na versão examinada.
- Prazo, eventual tag e outras partes da rubrica AV2 não foram fornecidos.

### Próxima ação

Após solicitação de implementação, iniciar a fase 1 de `fases.md`. A existência
deste planejamento não autoriza declarar requisitos implementados ou testes passando.

## Fase 0 — descoberta e design consolidados

Data: 10/11/2026.
Estado: concluída por análise estática, conforme solicitação de executar somente a fase 0.

### O que foi feito

- Confirmados branch `av2` e commit do planejamento `496d277`.
- Relido o enunciado completo e confrontado com serviço, schema, modelo, treino,
  exemplos, testes, Docker, CI e documentação existente.
- Consolidado o desenho na seção 11 de `escopo.md`, sem criar uma cópia concorrente
  do documento de escopo.
- Registrados limites de entrada, campos anuláveis, mapeamento HTTP/dataset,
  threshold de classificação e comportamento de erro esperado pelos testes.
- Conferida a integridade do artefato pelo SHA-256, sem desserializá-lo.
- Separados fatos confirmados por arquivos das verificações futuras de runtime.

### Arquivos alterados

- `docs/av2/escopo.md`: estado da fase 0, arquitetura, contrato, evidências e dependências.
- `docs/av2/fases.md`: fase 0 concluída e demais fases mantidas pendentes.
- `docs/av2/checkpoints.md`: preparação histórica separada deste checkpoint de execução.

### Decisões e justificativas

- Preservar a API e o pipeline; a AV2 acrescenta observabilidade ao serviço existente.
- Capturar na camada HTTP para alcançar falhas anteriores à função de inferência.
- Usar JSONL append-only e métricas nativas, sujeitos à confirmação técnica da fase 1.
- Manter documentação antiga e testes como histórico e proteção da continuação.
- Executar somente a fase solicitada; nenhuma autorização anterior para outras
  fases substitui a delimitação mais recente do usuário.

### Comandos e resultados observados

- `git branch --show-current`: `av2`.
- `git log -3 --oneline`: planejamento registrado em `496d277`.
- `Get-FileHash models/adult-income-v1.pkl -Algorithm SHA256`: corresponde ao
  `artifact_sha256` da metadata (`cfc85186...027bb716`).
- Leitura dos arquivos: confirmados requisitos, contratos e pontos de integração.
- Conferência documental final: links relativos válidos, texto sem espaços finais
  e `git diff --check` sem erros; nenhuma alteração em código ou configuração.
- Nenhum teste de aplicação, servidor, carga, treinamento ou container executado
  nesta fase. Os 41 testes antigos continuam sendo somente evidência histórica.

### Observação sobre a preparação interrompida

Antes de o usuário delimitar o trabalho à fase 0, houve tentativa de preparar uv
localmente em `.tools/`. A tentativa sem acesso de rede falhou em resolver PyPI;
uma tentativa posterior deixou arquivos locais mesmo com o turno interrompido.
Essa ferramenta não faz parte da entrega da fase 0 e o diretório temporário criado
pelo agente foi removido após conferir o caminho e seu conteúdo. Nenhuma dependência
foi adicionada a `pyproject.toml`, e o lock permanece intacto.

### Pendências e riscos

- Fase 1: preparar Python 3.12/uv e executar baseline frozen, pytest e Ruff.
- Confirmar API/ordem de middleware e um único escritor no BentoML 1.4.39.
- Consultar `/metrics` real; não assumir que a documentação latest descreve todos
  os detalhes da versão fixada.
- Docker e CI exigem os ajustes já planejados, nas fases correspondentes.
- Prazo, eventual tag e critérios não incluídos no texto recebido continuam desconhecidos.

### Próxima ação

Fase 1 — baseline e decisões de integração, quando solicitada. Nenhuma outra fase
foi iniciada nesta execução da fase 0.

## Fase 1 — baseline e decisões de integração

Data: 10/11/2026.
Estado: concluída, após retomada solicitada pelo usuário depois de reiniciar o PC.

### O que foi feito

- Preservados branch `av2`, HEAD `496d277` e alterações documentais da fase 0.
- Instalados uv 0.12.5 e Python 3.12.14 para uso local; ambiente `.venv` sincronizado
  com as versões do lock, sem alterar `pyproject.toml` ou `uv.lock`.
- Executada suíte completa e conferido Ruff após o reinício.
- Consultados health, predict válido, perfil inválido, JSON malformado e métricas
  de um servidor HTTP real; encerrada somente sua árvore de processos ao final.
- Confirmados parser Prometheus, deltas dos contadores/histograma, um worker
  efetivo e a API pública para middleware na versão instalada.
- Definidos abertura do handler em startup, fechamento em shutdown e logger
  compartilhado pelo middleware no worker, sem abertura de arquivo no supervisor.
- Registrada a investigação da interrupção em `phase-1-baseline.md`.

### Arquivos alterados

- `docs/av2/phase-1-baseline.md`: ambiente, comandos, resultados, integração e retomada.
- `docs/av2/fases.md`: fase 1 concluída e checklist atualizado.
- `docs/av2/escopo.md`: estado atual e referência ao baseline.
- `docs/av2/checkpoints.md`: este registro.
- Arquivos de ambiente e sondagens permanecem ignorados em `.venv/` e `.bentoml/`.

### Comandos e resultados observados

- `uv sync --frozen --python 3.12 --offline`: 81 pacotes conferidos, 12 ms.
- `uv run --frozen pytest -vv -o faulthandler_timeout=45`: **41 passed in 47.25s**.
- `uv run --frozen ruff check .`: **All checks passed!**.
- CLI BentoML em `127.0.0.1:55506`: health 200, predict 200, perfil inválido 400,
  JSON malformado 400, metrics 200. Porta liberada após encerramento.
- Capturas de métricas: deltas por status para `/predict` de 1 (200), 2 (400) e 0
  (500); delta agregado dos buckets `+Inf` igual a 3.
- Sondagem do middleware: 200/400/400/500 observados, corpo preservado e rejeições
  antes da inferência. O 500 foi injetado, e a falha de abertura no startup foi
  simulada com `PermissionError`; testes permanentes pertencem à fase 2.

### Decisões e desvios registrados

- Usada porta livre em vez de 3000 para evitar colisão com serviços do usuário.
- Usada saída verbosa e diagnóstico de espera do pytest na retomada, mantendo a
  suíte completa e os critérios; as verificações pesadas passaram a ser sequenciais.
- Distinguidos launcher de venv e interpretador filho ao contar workers no Windows:
  dois processos com os mesmos argumentos não significam dois escritores.
- Execuções interrompidas sem resultado final não foram contabilizadas como testes
  aprovados. Os logs não permitem identificar a causa do travamento do PC.
- Python ficou no temporário após erro de acesso ao renomear a instalação no
  Desktop. Se o Windows removê-lo, será necessário recriar o ambiente.

### Pendências e próxima ação

- Fase 2: implementar JSONL append-only, captura/sanitização HTTP e testes permanentes.
- Usar `workers=1` explicitamente ao integrar o logging, embora o default observado
  já tenha resultado em um worker efetivo.
- Preservar métricas nativas; `service_version=not available` não representa a versão
  do modelo e não deve ser usado em lugar de `model_version` no rastro.
- Docker, CI, carga e README continuam nas fases previstas. Nenhuma dessas fases
  foi antecipada; não houve commit, push ou merge pelo agente.

## Fase 2 — logging de inferência

Data: 10/11/2026.
Estado: concluída. Base: `b262b18`, branch `av2`; árvore limpa ao iniciar.

### O que foi feito

- Criado `src/careerpath/monitoring.py`: captura HTTP limitada a 8192 bytes por
  corpo, allowlist de campos, eventos JSONL append-only e fallback de escrita.
- Integrados middleware público, `workers=1`, configuração no startup e fechamento
  dos handlers no shutdown. Inferência, schema e artefato permanecem preservados.
- Documentada variável `CAREERPATH_LOG_PATH`, padrão relativo `logs/inference.jsonl`.
- Criados testes permanentes de logging e fixture ASGI compartilhada para não
  duplicar séries Prometheus ao criar stacks BentoML na mesma suíte.
- Adicionados diretório Docker gravável e exclusão de logs no Git/contexto Docker.
- Criado `docs/av2/log-format.md`; atualizado estado do plano e escopo.

### Arquivos

- Criados: `src/careerpath/monitoring.py`, `tests/conftest.py`,
  `tests/test_monitoring.py`, `docs/av2/log-format.md`.
- Alterados: `src/careerpath/service.py`, `tests/test_service.py`, `.env.example`,
  `.gitignore`, `.dockerignore`, `Dockerfile` e os três documentos de acompanhamento AV2.
- Sem alteração no modelo, treinamento, schema, dependências ou lock.

### Comandos e resultados observados

- Teste inicial de sucesso: **1 failed**, pois a API ainda não criava o arquivo;
  falha esperada antes de implementar a funcionalidade.
- Testes direcionados de monitoramento/serviço: **27 passed in 5.07s**.
- `uv run --frozen pytest -vv -o faulthandler_timeout=30`:
  **59 passed in 23.66s**, incluindo os 41 testes anteriores e E2E com reinício real.
- `ruff check .`: **All checks passed!** após formatação dos arquivos envolvidos.
- Conferência final após formatação/revisão: **18 passed in 1.64s** em
  `tests/test_monitoring.py`; Ruff aprovado e `python -m compileall -q src scripts tests`
  concluído com exit code 0.
- Sondagem CLI HTTP real: health, predict e metrics 200; perfil inválido e JSON
  malformado 400; um worker efetivo; árvore encerrada e porta liberada.
- Arquivo real `.bentoml/phase2/inference.jsonl`: exatamente três eventos com status
  200/400/400 e capturas complete/complete/invalid_json; saída do evento válido
  igual à resposta. Health e as duas consultas de metrics não acrescentaram linhas.
- Revisão independente do código/testes: **nenhum achado bloqueante**; nenhuma
  edição ou teste pesado executado pelo revisor.

### Decisões e desvios registrados

- Ruling: o diretório gravável do Docker foi antecipado da fase 5 para esta fase,
  porque o novo startup precisa abrir o log como UID 10001. Sem o ajuste, o caminho
  padrão em `/app` falharia. Build real e persistência por volume seguem na fase 5.
- Ruling: filtro de `/metrics` verificado no limite ASGI e pelo CLI HTTP real.
  O TestClient em memória ficou aguardando `/metrics`, inclusive em execução isolada;
  a espera foi interrompida. Não foi alterado o endpoint nativo para acomodar o teste.
- O timeout e a tentativa inicial de testes não foram contados como aprovações.
  A suíte final passou inteira. Verificações pesadas continuaram sequenciais.
- Falhas de disco são visíveis em stderr mesmo quando o logging padrão esconderia
  exceções; não incluem mensagem da exceção nem substituem a resposta já enviada.

### Pendências e próxima ação

- Fase 3: guia e verificações permanentes da interpretação de `/metrics`.
- Fases 4–7: carga reproduzível, persistência/CI, README, evidências e revisão final.
- Não há rotação automática nem suporte a vários escritores no mesmo arquivo.
- Docker não foi construído/executado nesta fase; não declarar validação do container.
- Nenhum commit, push ou merge foi realizado pelo agente.

## Fase 3 — métricas e interpretação

Data: 10/11/2026.
Estado: concluída. Base: `57396e5`, branch `av2`; árvore limpa ao iniciar.

### O que foi feito

- Ampliado o E2E existente, mantendo dois ciclos reais do servidor, para consultar
  `/metrics` antes/depois de um predict 200 e outro 400 por ciclo.
- Validado formato com parser Prometheus já instalado, labels, deltas por status,
  soma/contagem e frequências derivadas dos buckets cumulativos.
- Comprovado reset: cada ciclo iniciou com contadores de predict em zero, inclusive
  o segundo depois de o primeiro acumular dois pedidos.
- Isolado o destino do log do E2E em `tmp_path`, sem gravar no log de uso manual.
- Criado guia `docs/av2/metrics.md` com coleta, fórmulas, quartis/boxplot, casos sem
  tráfego, erros, retenção e exemplos didáticos separados de resultados reais.
- Salvas capturas e eventos sintéticos em `docs/av2/evidence/phase-3/`.

### Arquivos

- Alterado: `tests/test_e2e.py`, além dos documentos de acompanhamento AV2.
- Criados: `docs/av2/metrics.md`; evidências `metrics-0-before.prom`,
  `metrics-0-after.prom`, `metrics-1-before.prom`, `metrics-summary.json` e
  `inference-sample.jsonl` em `docs/av2/evidence/phase-3/`.
- Sem alterações no código da aplicação, configuração de runtime, dependências,
  lock, modelo ou contrato de inferência.

### Comandos e resultados observados

- E2E direcionado com capturas locais em `.bentoml/phase3-e2e`:
  **1 passed in 17.82s**. O teste encerrou ambas as árvores e confirmou porta liberada.
- `uv run --frozen pytest -q -o faulthandler_timeout=40`:
  **59 passed in 23.19s**. A quantidade permanece 59 porque foi ampliado o teste
  existente, sem duplicar os ciclos de startup em outro teste.
- Ruff: **All checks passed!**; compilação de `tests/` concluída sem erros.
- Em cada ciclo: deltas por status 200=1, 400=1, 500=0; histograma com contagem 2,
  buckets cumulativos monotônicos e frequências não negativas somando 2.
- Na captura versionada, médias nativas de 34,02885 ms e 35,00810 ms. Taxas de
  falhas HTTP de 50% e falhas do servidor de 0%, devido à rejeição proposital.
- Conferência independente dos arquivos salvos: contadores antes/depois/reset,
  soma e médias correspondem ao resumo. Quatro eventos sintéticos formam a amostra
  de latências do guia.
- Exemplo Python de boxplot executado: quatro observações, quartis lineares e
  bigodes calculados. O mesmo exemplo com arquivo vazio passou a imprimir N/A.

### Revisão e decisões

- A instrumentação nativa já atendia ao contrato, então não foi criado endpoint
  nem produzida falha artificial para justificar código novo de produção.
- A espera pelo health mantém pausa de 0,1 s tanto em erro de conexão quanto em
  resposta HTTP não saudável, após o helper passar a devolver status de erro.
- A revisão independente encontrou acesso a coluna inexistente quando o JSONL
  estava vazio. O problema foi reproduzido (`KeyError: endpoint`), corrigido no
  exemplo e reexecutado com sucesso nos casos vazio e preenchido.
- Demais cálculos, capturas e assertions revisados sem achados bloqueantes.
- Checagem final após ajustar o backoff: E2E **1 passed in 18.18s** e Ruff aprovado.
  Diff sem erros de whitespace e links locais dos documentos conferidos.
- Guia e dados bastam ao escopo desta fase; não foi criada a planilha opcional.

### Próxima ação

Fase 4 — geração de carga reproduzível e suficiência dos dados. Fases 4–7 continuam
pendentes; nenhuma publicação, alteração remota ou commit foi realizado pelo agente.

## Fase 4 — carga e suficiência dos dados

Data 11/11/2026. Base `91610af` na branch `av2`. Fase concluída.

- `scripts/generate_load.py` envia perfis sequencialmente para `/predict`. A seed
  42 define a sequência de categorias, idades e jornadas. O cenário shifted
  aplica +12 às duas variáveis numéricas. O parâmetro `--invalid-every` controla
  a frequência das rejeições esperadas.
- O teste inicial falhou pela ausência do gerador. A revisão também reproduziu
  três URLs inválidas e uma linha de status HTTP malformada que interrompia o
  lote. A CLI agora rejeita essas URLs e contabiliza falhas de protocolo.
- A suíte final com `uv run --frozen pytest -q -o faulthandler_timeout=40` passou
  com **74 testes em 22,94 s**. `uv run --frozen ruff check .` foi aprovado.
- O servidor local recebeu `--count 100 --seed 42 --scenario baseline
  --invalid-every 10`, depois os mesmos argumentos com `--scenario shifted`,
  e por fim `--count 5 --seed 42 --scenario baseline --invalid-every 0`. Os
  lotes principais registraram 90 respostas 200 e 10 respostas 400 cada. O
  curto registrou cinco respostas 200. As 205 linhas concordaram com a CLI
  e com os deltas de `/metrics`, com zero 5xx e zero falhas de comunicação.
- Pandas confirmou tipos numéricos, variação nas quatro colunas e 90 linhas
  válidas por cenário principal. O deslocamento de idade e jornada foi de 12
  em cada par válido, com categorias idênticas.
- Comandos e método de reconstrução da referência estão em [load.md](load.md).
  O [resumo observado](evidence/phase-4/summary.json) foi salvo em `docs/`. Capturas
  brutas e JSONL da execução local ficaram em `.bentoml/phase4-81wlloc7/`.
  O servidor de teste foi encerrado e a porta liberada.
- A receita `just load` delega à CLI. O binário `just` estava indisponível
  neste ambiente. A validação HTTP usou diretamente o comando `uv run`.

A fase 5 trata persistência, Docker e CI.

## Fase 5 — integração, persistência e qualidade

Data 11/11/2026. Branch `av2`. As mudanças locais da fase 4 foram incorporadas
à validação.

- No E2E, o primeiro processo escreveu dois eventos, para status 200 e 400.
  O segundo abriu o mesmo arquivo com os 1.130 bytes anteriores intactos e
  acrescentou outros dois eventos. A previsão coincidiu com a anterior,
  o JSONL concordou com as respostas e os quatro IDs eram distintos.
- O contador inicial de `/predict` foi zero nos dois processos. Cada janela
  registrou um HTTP 200 e um 400. A captura local fica na pasta de testes
  temporária em `.bentoml/phase5-048fdc63c8ff4287b2da75cfc31d16c3/`.
- A suíte completa passou com **74 testes em 26,77 s**. Ruff e compilação
  de `src`, `scripts` e `tests` foram aprovados.
- O Dockerfile define `CAREERPATH_LOG_PATH=/app/logs/inference.jsonl` e mantém
  a preparação do diretório com o proprietário correspondente ao UID 10001.
  As receitas Docker usam a imagem `careerpath-mlops:av2` e um volume nomeado
  montado em `/app/logs`. O [guia Docker](docker.md) descreve a verificação.
- O cliente Docker estava instalado. Antes do startup, o pipe do motor Linux
  estava indisponível. Depois, a consulta de versão retornou HTTP 500 e uma
  nova tentativa excedeu 15 s. O WSL foi reportado como ausente. Build e
  recriação com volume ficam pendentes para outro ambiente com Docker Linux.
  O usuário orientou a usar apenas a validação no host neste PC.
- O workflow Quality agora inclui pushes em `av2`, além de `main` e pull
  requests. Mantém permissões de leitura e versões fixadas e inclui compilação.
  A execução remota ainda precisa ser observada.
- A receita `just check` inclui compilação. O executável `just` estava
  indisponível, então as verificações locais usaram os comandos diretos do uv.

Fase concluída com persistência verificada no host e limitação Docker registrada.
A fase 6 consolida README, evidências e material de apoio.

## Modelo para os próximos checkpoints

```markdown
## Fase N — título

Data:
Estado: em andamento / concluída / impedimento técnico

### O que foi feito
-

### Arquivos alterados
-

### Decisões e justificativas
-

### Comandos e resultados observados
- Comando:
- Resultado real:

### Pendências e riscos
-

### Próxima ação
-
```
