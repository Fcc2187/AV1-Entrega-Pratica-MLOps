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
