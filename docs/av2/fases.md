# CareerPath AV2 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** acrescentar logging de entradas/saídas e métricas operacionais reproduzíveis ao serviço da AV1.

**Architecture:** preservar BentoML e o pipeline local. Capturar inferências na camada HTTP em JSONL append-only e aproveitar `/metrics` nativo. O README conecta instalação, geração de carga e interpretação dos dados.

**Tech Stack:** Python 3.12, BentoML 1.4.39, Starlette, Pydantic, scikit-learn, logging da biblioteca padrão, uv, pytest e Ruff.

**Spec:** [Escopo e decisões propostas](escopo.md). Ler também [checkpoints](checkpoints.md) antes de retomar.

Revisão de continuidade em 11/11/2026: [parecer e cobertura do enunciado](revisao-plano.md).
As fases 0–3 abaixo preservam resultados históricos do colega; esta revisão não os
apresenta como nova execução. A próxima etapa é R, seguida da fase 4.

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
| R | Testar best-prompt-ever na retomada | Prompt das fases 4–7 e avaliação da entrevista | Pendente |
| 4 | Gerar carga reproduzível | Script e demonstração controlada | Pendente |
| 5 | Integrar Docker, CI e reinício | Persistência e regressões verificadas | Pendente |
| 6 | Documentar e coletar evidências | README e capturas reais | Pendente |
| 7 | Auditar e encerrar | Matriz final e READY/NOT READY | Pendente |

Ordem: `0 -> 1 -> 2 -> 3 -> R -> 4 -> 5 -> 6 -> 7`.
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

## Etapa R — aplicar best-prompt-ever ao restante do projeto

**Ler:** `.agents/skills/best-prompt-ever/SKILL.md` e referências exigidas pela skill;
`escopo.md`, este plano, checkpoints, código atual e testes das fases restantes.
**Produz:** prompt na conversa para conduzir as fases 4–7; avaliação breve
no checkpoint após a entrevista. Não reabrir nem reimplementar as fases concluídas.

- [ ] Invocar explicitamente `best-prompt-ever` com o pedido: “Detalhe um prompt para concluir as fases 4–7 de docs/av2/fases.md: carga, integração e persistência, documentação e material de análise, auditoria e correções finais; preserve as fases 0–3 e o contrato atual”.
- [ ] Fazer reconhecimento somente de leitura; consultar `.best-prompt-ever/context.md` se existir e verificar suas informações no código. Não abrir segredos.
- [ ] Usar a entrevista para resolver somente lacunas reais, com opções fundamentadas no repositório. Informar que `av2` já foi escolhida pelo usuário; não perguntar de novo nem criar outra branch sem motivo.
- [ ] Apresentar o painel de cobertura e o prompt em português, com objetivo, arquivos, padrões, sequência e cenários numerados. Separar as unidades das fases 4–7, suas dependências e evidências; referenciar os comandos frozen e os contratos existentes.
- [ ] Incluir na validação: mesma seed produz mesma carga; 100 pedidos com intervalo 10 produzem 90 sucessos e 10 rejeições; falhas de rede ficam separadas; `shifted` respeita o schema; log e métricas crescem conforme os pedidos observados.
- [ ] Cobrir também persistência e regressões da fase 5; reprodução apenas pelo README, cálculos e decisão sobre planilha da fase 6; matriz de requisitos, correções e evidências de READY/NOT READY da fase 7.
- [ ] Antes de cada fase restante, conferir o prompt contra o estado atual e reaproveitar decisões válidas. Retomar a skill para detalhar ou revisar a unidade quando houver lacunas relevantes ou mudança de escopo; não repetir a entrevista inteira nem perguntar o que já está decidido. A skill acompanha todo o restante do projeto, não se encerra na geração de carga.
- [ ] Entregar o prompt na conversa, sem gravá-lo automaticamente. A entrevista não altera código, documentos, branches ou commits. A implementação começa após a confirmação de execução prevista pela skill.
- [ ] Apresentar proposta de memória separadamente e gravar `.best-prompt-ever/context.md` somente se o usuário autorizar especificamente. A autorização de execução não autoriza a memória.
- [ ] Após encerrar a entrevista, registrar no checkpoint: lacunas descobertas, perguntas redundantes, correções do usuário e se o prompt continha arquivos e evidências suficientes. Não declarar a skill testada apenas por estar instalada.

**Aceite:** prompt executável e revisado para as fases 4–7; entrevista respeitou leitura
somente e não repetiu decisões existentes. A revisão atual prepara esse teste, mas
não conta como a realização da entrevista. Usar `superpowers:executing-plans` para
executar a continuação; este plano não exige delegação de implementação.

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
- [ ] Para distribuições de entrada/saída, selecionar `outcome=success` e `input_capture=complete`; preservar nulos como categoria própria nas frequências e excluir ausentes das análises numéricas. Não confundir falhas de validação com drift.
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
- [ ] Conferir `/app/logs` gravável para UID 10001, já preparado na fase 2 para o startup do logging, e definir o caminho coerente com o volume.
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
- [ ] Se produzir a planilha, incluir abas de dados individuais, snapshots identificados por instância/horário e cálculos; mostrar histograma, boxplot e taxas 4xx+5xx e 5xx. Validar fórmulas, unidades, amostra vazia e janela com reset. Manter o mesmo método de quartis do guia e explicar eventuais diferenças do aplicativo. Na omissão, registrar a decisão e manter exemplo completo no texto.
- [ ] Atualizar declaração de uso de IA e checkpoint com participação e revisão efetivamente realizadas.

**Aceite:** outra pessoa, seguindo apenas o README, consegue produzir e interpretar
o rastro. Capturas e documentação usam o mesmo contrato da aplicação.

## Fase 7 — auditoria, correções e verificação final

**Criar:** `docs/av2/review.md`; atualizar checkpoints.

- [ ] Começar pela leitura, sem alterar código: confrontar cada linha da matriz do escopo com arquivo, comando e evidência correspondente.
- [ ] Classificar achados: P0 impede subir/demonstrar; P1 deixa requisito aplicável sem cobertura ou produz dados incorretos; P2 é melhoria não obrigatória.
- [ ] Verificar especificamente entradas e saídas, append, microssegundos/fuso, erros antes da função, sanitização, métricas reais, suficiência analítica, referência e retenção.
- [ ] Auditar a rastreabilidade das respostas 400/500: hoje `output=null` e `error_type` é genérico. Confirmar que o registro sanitizado permite interpretar o desfecho; se insuficiente, planejar e testar resumo estruturado do erro (categoria e campos afetados), sem payload bruto ou detalhes internos. Manter explícita essa limitação no dicionário do log; não afirmar que o corpo completo das respostas de erro está salvo.
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
