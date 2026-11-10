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
| 2 | Registrar entradas, saídas e falhas | JSONL append-only testado | Pendente |
| 3 | Validar e interpretar `/metrics` | Endpoint real e guia de cálculos | Pendente |
| 4 | Gerar carga reproduzível | Script e demonstração controlada | Pendente |
| 5 | Integrar Docker, CI e reinício | Persistência e regressões verificadas | Pendente |
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

**Interfaces propostas:**
- `configure_monitoring(log_path: Path) -> logging.Logger`: cria pais, valida abertura, configura um handler append sem propagação/duplicação.
- `InferenceLoggingMiddleware(app: ASGIApp, *, logger: logging.Logger, model_version: str)`: observa `/predict`, captura mensagens HTTP e escreve o evento definido no escopo.
- Configuração pública: `CAREERPATH_LOG_PATH`, padrão `logs/inference.jsonl`.
- Consome o contrato atual de `Profile`/`Prediction`; produz o JSONL lido nas fases seguintes. Tipos ASGI vêm de Starlette já instalado.

- [ ] Escrever testes que falham: evento de sucesso com seis features e saída igual à resposta, probabilidade numérica em `[0,1]`, UUID e timestamp UTC com microssegundos, latência não negativa.
- [ ] Acrescentar teste de append: gravar uma linha, realizar novas chamadas e verificar prefixo anterior idêntico em bytes, novas linhas parseáveis e nenhuma duplicação por handler.
- [ ] Acrescentar casos: JSON malformado, idade inválida, campo extra, categoria desconhecida, `null` e exceção interna simulada. Exigir um evento por pedido concluído, status real e saída nula nos erros.
- [ ] Acrescentar teste de captura em vários chunks, Unicode, mais de 8 KiB, campos extras e valor aninhado: nenhuma fuga de campos e nenhum corpo consumido ou alterado pelo middleware.
- [ ] Acrescentar teste de concorrência no worker: eventos íntegros, IDs únicos e entrada/saída correspondentes, sem exigir ordem de conclusão.
- [ ] Acrescentar testes de falha de abertura e escrita: startup falha claramente na primeira; falha posterior chega a stderr e não reenvia nem substitui uma resposta já iniciada.
- [ ] Executar `uv run --frozen pytest -q tests/test_monitoring.py tests/test_service.py` e confirmar falha ligada ao comportamento novo antes da implementação.
- [ ] Implementar as interfaces pela integração pública confirmada na fase 1, usando `logging`, `json`, `uuid`, UTC e relógio monotônico da biblioteca padrão.
- [ ] Configurar o caminho no `.env.example` com valor de exemplo não secreto e ignorar `logs/` e resultados locais; não depender de carregamento automático de `.env` inexistente.
- [ ] Executar novamente os testes direcionados e Ruff; confirmar sucesso e contrato HTTP preservado.
- [ ] Documentar cada campo, tratamento de erros/nulos, limites de captura e justificativa CRISP-DM; registrar checkpoint.

**Aceite:** rastros de sucesso, validação e falha interna são analisáveis, append é
comprovado e chamadas concorrentes no worker não corrompem nem duplicam registros.

## Fase 3 — métricas e interpretação

**Alterar:** testes E2E e configuração de serviço apenas se necessário.
**Criar:** `docs/av2/metrics.md`.

**Consome:** `/metrics` nativo observado na fase 1 e JSONL da fase 2.
**Produz:** nomes reais das séries, duas coletas comparáveis e método de cálculo.

- [ ] Adicionar E2E que consulta metrics antes e depois de predict válido e inválido; verificar exposição parseável, contador por endpoint/status e histograma de duração. Preferir parser já presente no ambiente; não fixar a ordem das linhas.
- [ ] Executar o teste e verificar o estado real: métricas nativas já funcionais não precisam de código novo nem de teste artificialmente vermelho.
- [ ] Habilitar/ajustar somente a configuração nativa necessária; não escrever endpoint concorrente e não usar rótulos de alta cardinalidade como request ID.
- [ ] Documentar unidades reais, soma, contagem, limites e buckets cumulativos usando nomes copiados da execução.
- [ ] Explicar frequências por diferença de buckets, média por `delta(sum)/delta(count)` e taxas HTTP/servidor definidas no escopo; mostrar denominador zero como `N/A` e resets como janela nova.
- [ ] Explicar boxplot exato a partir de `latency_ms` no JSONL e limitações de estimativas pelos buckets; não alegar igualdade exata de duração com o runtime.
- [ ] Demonstrar exemplos aritméticos identificados como didáticos: 20 pedidos, 2 respostas 4xx e 1 resposta 5xx resultam em 15% de falhas HTTP e 5% de falhas do servidor. Capturas reais ficam separadas.
- [ ] Executar E2E e registrar nomes observados, comportamento de reset e checkpoint.

**Aceite:** métricas mudam com carga real; guia permite interpretar histogramas,
latência e erros e distingue memória do processo de armazenamento histórico.

## Fase 4 — carga e suficiência dos dados

**Criar:** `scripts/generate_load.py`, `tests/test_generate_load.py`.
**Alterar:** `justfile` para receita opcional de carga.

**Interfaces propostas:**
- `build_payloads(count: int, *, seed: int, scenario: str) -> list[dict[str, object]]`: perfis sintéticos com categorias dos exemplos atuais; cenários `baseline` e `shifted`.
- CLI: `uv run --frozen python scripts/generate_load.py --url http://127.0.0.1:3000 --count 100 --seed 42 --scenario baseline --invalid-every 10`.
- `--scenario shifted` desloca somente idades e horas semanais, respeitando os limites do schema. `--invalid-every 0` desliga erros; com 10, cada décimo pedido recebe `age=-1`.
- Resumo em stdout: enviados, 2xx, 4xx, 5xx e falhas de rede. Exit code 0 para resultados esperados; não zero para rede, 5xx ou resposta inesperada. Timeout por pedido: 10 s.

- [ ] Criar testes que falham para determinismo por seed, limites de `Profile`, cenário deslocado, `count > 0`, intervalos inválidos e contabilização de respostas/rede com HTTP simulado.
- [ ] Executar `uv run --frozen pytest -q tests/test_generate_load.py` e confirmar a falha esperada.
- [ ] Implementar gerador e CLI com biblioteca padrão, sem banco, treinamento ou dependência de dados baixados. Não afirmar que o cenário sintético representa a população Adult.
- [ ] Executar testes direcionados e Ruff e confirmar sucesso.
- [ ] Com servidor real, coletar metrics antes/depois de 100 pedidos baseline e repetir 100 shifted; executar também uma carga curta sem erros.
- [ ] Conferir deltas no JSONL: 90 sucessos e 10 rejeições por lote de 100 com configuração acima, se não houver falhas inesperadas. Não contar erros esperados como exemplos de falha do servidor.
- [ ] Carregar as linhas com pandas já instalado e conferir tipos de idade, horas, probabilidade e latência, variação dos valores e exclusão de eventos inválidos das distribuições de features.
- [ ] Registrar procedimento da referência Adult e da referência de probabilidades conforme o escopo, sem precisar executar KS/PSI ou baixar a base para gerar carga.
- [ ] Registrar comandos, contagens reais e limitações no checkpoint.

**Aceite:** professor consegue gerar tráfego variado e erros controlados; valores
individuais de entrada e saída podem ser recuperados sem parsing de texto livre.

## Fase 5 — integração, persistência e qualidade

**Alterar:** Dockerfile, justfile, CI e testes E2E.
**Consome:** logging, carga e métricas já funcionais. **Produz:** operação reproduzível
no host e, quando disponível, container com logs graváveis e preservados por volume.

- [ ] Ampliar E2E para passar caminho temporário de log ao subprocesso, gerar carga e reiniciar o serviço usando o mesmo arquivo; verificar bytes anteriores, novas linhas e resposta do modelo após reinício.
- [ ] Observar contadores antes/depois do reinício e registrar a janela nova; não depender de valores globais exatos de outros endpoints.
- [ ] Atualizar Dockerfile para criar `/app/logs` com permissão para UID 10001 antes de `USER appuser` e definir o caminho coerente com o volume.
- [ ] Documentar comando Docker com volume nomeado em `/app/logs`; testar remover/recriar container com o mesmo volume e confirmar append. Não apagar volumes do usuário.
- [ ] Ajustar CI para pushes em `main` e `av2`, mantendo pull requests, permissões mínimas, versões fixadas, Ruff e pytest. CI de qualidade não precisa de artifact de dados do pipeline Garmin.
- [ ] Ajustar receitas úteis do justfile, preservando o comando direto com uv para quem não tem just instalado.
- [ ] Executar `uv run --frozen pytest -q`, `uv run --frozen ruff check .` e `uv run --frozen python -m compileall -q src scripts tests`.
- [ ] Se Docker disponível, executar `docker build --tag careerpath-mlops:av2 .` e smoke test com volume, predict, metrics e reinício. Se indisponível, registrar explicitamente que Docker não foi validado.
- [ ] Registrar resultados e checkpoint; não declarar CI remota aprovada sem observar a execução remota.

**Aceite:** testes existentes e novos passam; logging sobrevive ao reinício local;
container tem estratégia documentada de escrita e persistência, com teste real ou
limitação declarada. Nenhum dado gerado é versionado inadvertidamente.

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
