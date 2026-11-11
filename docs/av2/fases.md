# CareerPath AV2 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** acrescentar logging de entradas/saídas e métricas operacionais reproduzíveis ao serviço da AV1.

**Architecture:** preservar BentoML e o pipeline local. Capturar inferências na camada HTTP em JSONL append-only e aproveitar `/metrics` nativo. O README conecta instalação, geração de carga e interpretação dos dados.

**Tech Stack:** Python 3.12, BentoML 1.4.39, Starlette, Pydantic, scikit-learn, logging da biblioteca padrão, uv, pytest e Ruff.

**Spec:** [Escopo e decisões propostas](escopo.md). Ler também [checkpoints](checkpoints.md) antes de retomar.

## Global Constraints

- Trabalhar na branch existente `av2`; conferir Git e alterações do usuário antes de cada bloco.
- Manter modelo `adult-income-v1`, contratos de `/predict` e `/health` e validação da AV1.
- Seguir o contrato de evento, captura de 8 KiB e sanitização definidos em `escopo.md`.
- Um worker de aplicação e um escritor do log; provar a topologia no comando real do servidor.
- Usar JSONL UTF-8 e append; sem rotação automática inicial ou exclusão automática de logs.
- Usar dependências existentes e biblioteca padrão; não atualizar o lock sem necessidade demonstrada.
- Não importar prazos, tag `sr1`, duração de apresentação ou gates de troca de modelo da AV1.
- Não apresentar resultados históricos, exemplos ou resultados esperados como execução atual.
- Executar somente as fases solicitadas pelo usuário. Commit, push, merge e publicação exigem instrução correspondente.

## Review Focus

1. JSON malformado e validação rejeitada antes de `predict`: devem produzir evento sanitizado (fase 2).
2. Requisições simultâneas no worker: não misturar dados, quebrar JSONL ou duplicar eventos (fase 2).
3. Reinício e diretório sem permissão: preservar bytes anteriores ou falhar explicitamente no startup (fases 1 e 5).
4. Coletas com tráfego zero ou reset de contadores: não produzir divisão por zero nem taxa negativa (fases 3 e 4).
5. Corpo com campos extras, textos longos ou captura excedida: respeitar limites e preservar o comportamento HTTP (fase 2).

## Organização e responsabilidades dos arquivos

Os caminhos abaixo são planejados. O estado executado de cada fase fica no checkpoint.

| Caminho | Ação futura e responsabilidade |
| --- | --- |
| `src/careerpath/monitoring.py` | Criar: captura HTTP, sanitização e escrita JSONL |
| `src/careerpath/service.py` | Alterar: integrar monitoramento sem mudar a inferência |
| `tests/test_monitoring.py` | Criar: contrato do evento, erros, limites e escrita |
| `tests/test_service.py` | Ampliar: regressões e comportamento HTTP instrumentado |
| `tests/test_e2e.py` | Ampliar: arquivo real, métricas, concorrência e reinício |
| `scripts/generate_load.py` | Criar: carga HTTP determinística, sem treinar nem iniciar servidor |
| `tests/test_generate_load.py` | Criar: sequência de carga e contabilização de desfechos |
| `docs/av2/metrics.md` | Criar: leitura das métricas, cálculos, boxplot e retenção |
| `docs/av2/log-format.md` | Criar: dicionário final do JSONL e ligação com o negócio |
| `docs/av2/evidence/` | Criar na demonstração: capturas reais e roteiro executado |
| `README.md` | Alterar: caminho completo do clone à observação do log |
| `.env.example`, `.gitignore` | Alterar: configuração do caminho e exclusão de dados gerados |
| `Dockerfile`, `justfile`, `.github/workflows/ci.yml` | Alterar: diretório/volume de logs, receitas e CI da branch |
| `docs/av2/analise-metricas.xlsx` | Opcional: planilha com dados reais, fórmulas e boxplot |

## Visão geral

| Fase | Finalidade | Entregável | Estado atual |
| --- | --- | --- | --- |
| 0 | Consolidar escopo e reaproveitamento | Estes documentos e revisão estática | Concluída |
| 1 | Verificar base, runtime e integração | Baseline atual e decisões confirmadas | Concluída |
| 2 | Registrar entradas, saídas e falhas | JSONL append-only testado | Concluída |
| 3 | Validar e interpretar `/metrics` | Endpoint real e guia de cálculos | Concluída |
| 4 | Gerar carga reproduzível | Script e demonstração controlada | Concluída |
| 5 | Integrar Docker, CI e reinício | Persistência local verificada e integração configurada | Concluída com validação Docker pendente |
| 6 | Documentar e coletar evidências | README e capturas reais | Pendente |
| 7 | Auditar e encerrar | Matriz final e READY/NOT READY | Pendente |

Ordem: `0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7`.
Ao concluir cada fase, registrar checkpoint. Pausas técnicas devem indicar a causa
concreta; não há troca obrigatória de modelo. O usuário pode pedir execução por fase.

## Fase 0 — escopo e preservação

Entregável: `escopo.md`, `fases.md` e `checkpoints.md`.

- [x] Ler enunciado e identificar a modalidade de servidor de modelos.
- [x] Conferir branch, código e planos da AV1.
- [x] Mapear requisitos, arquivos preservados e alterações futuras.
- [x] Registrar limites, critérios e ausência de resultados de runtime atuais.
- [x] Revisar novamente o projeto após o commit `496d277` e consolidar arquitetura, contrato e evidências estáticas na seção 11 de `escopo.md`.

Conclusão: descoberta e design consolidados em 10/11/2026. Hash do artefato confere
com a metadata; contratos, pontos de alteração e pendências estão registrados.
Implementação e validação em runtime continuam pendentes a partir da fase 1.

## Fase 1 — baseline e decisões de integração

**Arquivos:** inspecionar `pyproject.toml`, `service.py`, testes e runtime instalado;
atualizar `escopo.md` apenas se a verificação técnica exigir uma decisão diferente.

**Consome:** branch e artefato da AV1. **Produz:** baseline com comandos observados,
API pública de middleware confirmada e topologia de um escritor definida.

- [x] Conferir `git status --short` e `git branch --show-current`; preservar alterações existentes.
- [x] Localizar uv e Python 3.12; preparar ambiente local sem atualização global desnecessária.
- [x] Executar instalação frozen, suíte completa e Ruff. Na retomada, pytest verboso com diagnóstico de espera: 41 testes passaram em 47,25 s.
- [x] Subir BentoML com host `127.0.0.1` e porta livre (`55506` na captura final); consultar health, predict válido, inválido, JSON malformado e metrics.
- [x] Confirmar a API pública e a posição do middleware em relação à validação na versão fixada.
- [x] Confirmar um worker efetivo, criação do handler no startup e prevenção de duplicação nos imports.
- [x] Confirmar propagação de falha de abertura simulada no startup; reservar testes permanentes da implementação para a fase 2.
- [x] Registrar comando final, nomes/labels de métricas e [baseline da fase 1](phase-1-baseline.md).

**Aceite:** API da AV1 responde; ambiente frozen funciona; integração proposta consegue
observar erros de validação e tem um único escritor. Se isso falhar, resolver a causa
antes de implementar logging sobre uma premissa incorreta.

Conclusão em 10/11/2026: ambiente frozen conferido (81 pacotes), 41 testes passaram,
Ruff aprovado, HTTP e métricas confirmados, um worker efetivo e integração pública
validados. O servidor da sondagem foi encerrado e a porta liberada. Ver limitações
do ambiente e retomada no baseline; logging de entrada/saída permanece pendente.

## Fase 2 — logging de inferência

**Criar:** `monitoring.py`, `tests/test_monitoring.py`, `docs/av2/log-format.md`.
**Alterar:** `service.py`, testes de serviço, `.env.example`, `.gitignore`.
Integração necessária: preparar diretório gravável no Dockerfile e excluir logs do
contexto Docker. Volume e validação real do container continuam na fase 5.

**Interfaces propostas:**
- `configure_monitoring(log_path: Path) -> logging.Logger`: cria pais, valida abertura, configura um handler append sem propagação/duplicação.
- `InferenceLoggingMiddleware(app: ASGIApp, *, logger: logging.Logger, model_version: str)`: observa `/predict`, captura mensagens HTTP e escreve o evento definido no escopo.
- Configuração pública: `CAREERPATH_LOG_PATH`, padrão `logs/inference.jsonl`.
- Consome o contrato atual de `Profile`/`Prediction`; produz o JSONL lido nas fases seguintes. Tipos ASGI vêm de Starlette já instalado.

- [x] Escrever teste de evento de sucesso e observar sua falha por ausência do arquivo antes de implementar o logging.
- [x] Cobrir append com prefixo idêntico em bytes, reinício de lifespan e reconfiguração sem duplicação.
- [x] Cobrir JSON malformado, idade inválida, campo extra, categoria desconhecida, `null` e falha interna simulada, sem gravar detalhes da exceção.
- [x] Cobrir chunks, Unicode, 8 KiB, valores aninhados e não finitos, mantendo os corpos HTTP originais.
- [x] Verificar concorrência no worker: 12 eventos íntegros, IDs únicos e pares entrada/saída corretos.
- [x] Cobrir falha no startup e falha posterior de escrita com stderr visível e resposta preservada, inclusive com `logging.raiseExceptions=False`.
- [x] Executar o teste inicial vermelho; depois os testes direcionados (27 passaram) e a suíte completa (59 passaram).
- [x] Implementar captura via `add_asgi_middleware`, configuração do handler no startup e fechamento no shutdown.
- [x] Documentar/exportar `CAREERPATH_LOG_PATH`; ignorar logs no Git e contexto Docker sem carregar `.env` automaticamente.
- [x] Confirmar Ruff e contrato HTTP preservado; verificar três eventos pelo CLI real e `/metrics` funcionando sem gerar eventos de inferência.
- [x] Documentar formato em [log-format.md](log-format.md), registrar checkpoint e obter revisão independente sem achados bloqueantes.

**Aceite:** rastros de sucesso, validação e falha interna são analisáveis, append é
comprovado e chamadas concorrentes no worker não corrompem nem duplicam registros.

Concluída em 10/11/2026. Suíte completa: 59 testes passaram em 23,66 s. Servidor
real gerou status 200/400/400 no JSONL, com saída correspondente à resposta e
health/metrics excluídos. A fase 3 e as demais permanecem pendentes.

## Fase 3 — métricas e interpretação

**Alterar:** testes E2E e configuração de serviço apenas se necessário.
**Criar:** `docs/av2/metrics.md`.

**Consome:** `/metrics` nativo observado na fase 1 e JSONL da fase 2.
**Produz:** nomes reais das séries, duas coletas comparáveis e método de cálculo.

- [x] Ampliar o E2E com capturas antes/depois de predict válido e inválido, parser existente, contadores/status e histograma sem depender da ordem textual.
- [x] Confirmar o funcionamento nativo: novo contrato passou sem alteração de produção ou falha artificial.
- [x] Preservar configuração e endpoint nativos; nenhuma nova dependência ou label de alta cardinalidade.
- [x] Documentar unidades, soma, contagem, labels e limites reais dos buckets em [metrics.md](metrics.md).
- [x] Explicar diferenças de buckets, média ponderada, taxas HTTP/servidor, zero tráfego como N/A e reset como nova janela.
- [x] Documentar boxplot a partir do JSONL e quartis lineares, distinguindo observações individuais de estimativas por buckets.
- [x] Separar exemplos didáticos de aritmética dos valores reais, com capturas versionadas em `docs/av2/evidence/phase-3/`.
- [x] Verificar dois ciclos do servidor real e reset; suíte completa com 59 testes passou; revisão independente e checkpoint registrados.

**Aceite:** métricas mudam com carga real; guia permite interpretar histogramas,
latência e erros e distingue memória do processo de armazenamento histórico.

Concluída em 10/11/2026: E2E direcionado passou em 17,82 s; suíte completa com
59 testes passou em 23,19 s; Ruff aprovado. Exemplo Python do guia executado com
amostra real e log vazio; ajuste de zero tráfego encontrado na revisão foi corrigido.

## Fase 4 — carga e suficiência dos dados

**Criar:** `scripts/generate_load.py`, `tests/test_generate_load.py`.
**Alterar:** `justfile` para receita opcional de carga.

**Interfaces propostas:**
- `build_payloads(count: int, *, seed: int, scenario: str) -> list[dict[str, object]]`: perfis sintéticos com categorias dos exemplos atuais; cenários `baseline` e `shifted`.
- CLI: `uv run --frozen python scripts/generate_load.py --url http://127.0.0.1:3000 --count 100 --seed 42 --scenario baseline --invalid-every 10`.
- `--scenario shifted` desloca somente idades e horas semanais, respeitando os limites do schema. `--invalid-every 0` desliga erros; com 10, cada décimo pedido recebe `age=-1`.
- Resumo em stdout: enviados, 2xx, 4xx, 5xx e falhas de rede. Exit code 0 para resultados esperados; não zero para rede, 5xx ou resposta inesperada. Timeout por pedido: 10 s.

- [x] Testar determinismo, limites de `Profile`, deslocamento, argumentos e contabilização com HTTP simulado.
- [x] Observar a falha inicial pela ausência do gerador e as falhas reproduzidas durante a revisão.
- [x] Implementar gerador e CLI com biblioteca padrão, usando perfis sintéticos dos exemplos.
- [x] Aprovar testes direcionados, suíte completa e Ruff.
- [x] Capturar `/metrics` antes e depois de 100 pedidos baseline, 100 shifted e cinco pedidos válidos.
- [x] Conciliar os contadores da CLI, do JSONL e de `/metrics`. Cada lote principal teve 90 sucessos e 10 rejeições planejadas.
- [x] Conferir tipos e variação com pandas e excluir eventos inválidos das distribuições de features.
- [x] Registrar a reconstrução da referência Adult e das probabilidades no [guia de carga](load.md).
- [x] Registrar comandos, resultados e limitações no checkpoint.

**Aceite:** professor consegue gerar tráfego variado e erros controlados; valores
individuais de entrada e saída podem ser recuperados sem parsing de texto livre.

Concluída em 11/11/2026. O servidor registrou 205 eventos reconciliados com as
métricas e a CLI. A suíte final passou com 74 testes e Ruff aprovado.

## Fase 5 — integração, persistência e qualidade

**Alterar:** Dockerfile, justfile, CI e testes E2E.
**Consome:** logging, carga e métricas já funcionais. **Produz:** operação reproduzível
no host e, quando disponível, container com logs graváveis e preservados por volume.

- [x] Ampliar o E2E com dois ciclos no mesmo log temporário. Conferir o prefixo byte a byte, duas novas linhas por ciclo, IDs distintos e a previsão após reinício.
- [x] Conferir a nova janela de contadores de `/predict` em ambos os ciclos.
- [x] Conferir no Dockerfile o proprietário de `/app/logs` e definir `CAREERPATH_LOG_PATH` dentro do ponto de montagem.
- [x] Documentar o volume nomeado e o teste de recriação no [guia Docker](docker.md).
- [x] Configurar CI para pushes em `main` e `av2` e pull requests, com Ruff, pytest e compilação.
- [x] Alinhar as receitas de build e execução e incluir compilação em `just check`.
- [x] Executar suíte completa, Ruff e compilação de `src`, `scripts` e `tests`.
- [x] Registrar a indisponibilidade do motor Docker e a validação de build e volume pendente.
- [x] Registrar resultados locais e estado da CI no checkpoint.

**Aceite:** testes existentes e novos passam; logging sobrevive ao reinício local;
container tem estratégia documentada de escrita e persistência, com teste real ou
limitação declarada. Nenhum dado gerado é versionado inadvertidamente.

Concluída em 11/11/2026 com 74 testes aprovados. A persistência foi verificada
no serviço local. A execução Docker e a CI remota aguardam verificação.

## Fase 6 — README, evidências e material de apoio

**Alterar:** README principal. **Criar:** evidências em `docs/av2/evidence/`.
**Consome:** comandos e resultados reais das fases anteriores.

- [ ] Escrever README com propósito, evolução AV1/AV2, Python/uv, clone, instalação frozen, startup, payloads, erro esperado e troubleshooting.
- [ ] Incluir comandos PowerShell e Linux/macOS para configurar `CAREERPATH_LOG_PATH`, executar carga, ler linhas recentes e consultar `/metrics`; testar ambos quando houver ambiente disponível e declarar o que não foi testado.
- [ ] Incluir links para formato do log, métricas, entendimento do negócio, planejamento e histórico da AV1.
- [ ] Explicar diretório de trabalho, permissões, ausência de rotação automática, retenção em disco, reinício de contadores e volume Docker.
- [ ] Coletar evidências reais: ambiente, health, predict, erro, amostra JSONL, métricas antes/depois, carga, testes e persistência. Registrar data, comando, resultado e versão do modelo; não inventar números.
- [ ] Preparar roteiro curto de demonstração: subir, observar arquivo, gerar baseline, gerar shifted, mostrar erro, comparar metrics e explicar retenção. Duração fica a cargo da orientação posterior do professor.
- [ ] Opcional recomendado: produzir planilha com latências reais, quartis, boxplot, deltas dos buckets e taxa de erros. Se omitida, texto deve continuar suficiente; não criar planilha vazia para simular entrega.
- [ ] Atualizar declaração de uso de IA e checkpoint com participação e revisão efetivamente realizadas.

**Aceite:** outra pessoa, seguindo apenas o README, consegue produzir e interpretar
o rastro. Capturas e documentação usam o mesmo contrato da aplicação.

## Fase 7 — auditoria, correções e verificação final

**Criar:** `docs/av2/review.md`; atualizar checkpoints.

- [ ] Começar pela leitura, sem alterar código: confrontar cada linha da matriz do escopo com arquivo, comando e evidência correspondente.
- [ ] Classificar achados: P0 impede subir/demonstrar; P1 deixa requisito aplicável sem cobertura ou produz dados incorretos; P2 é melhoria não obrigatória.
- [ ] Verificar especificamente entradas e saídas, append, microssegundos/fuso, erros antes da função, sanitização, métricas reais, suficiência analítica, referência e retenção.
- [ ] Corrigir P0/P1 dentro do escopo e executar verificações afetadas. Não implementar extras para aumentar o tamanho da entrega.
- [ ] Repetir o caminho principal do README em ambiente limpo quando disponível; executar suíte completa e Ruff após a última mudança de código.
- [ ] Conferir `git diff --check`, arquivos gerados, links locais e ausência de dados/segredos indevidos nas evidências.
- [ ] Entregar `READY` somente com requisitos aplicáveis demonstrados; caso contrário, `NOT READY` com pendências objetivas e limitações do ambiente.
- [ ] Atualizar checkpoint final com comandos, resultados reais, riscos e ações restantes da equipe. Não criar tag ou submeter a entrega sem instrução.

## Como registrar e retomar

Cada checkpoint informa: fase, estado, arquivos, decisões, comandos/resultados,
pendências, riscos e próxima ação. Em uma retomada, reler estes três documentos,
conferir branch/diff e começar pela primeira etapa ainda pendente. Não repetir
treinamento da AV1 nem reexecutar fases concluídas sem alteração ou falha que justifique.
