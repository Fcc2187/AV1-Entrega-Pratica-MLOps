# AV2 — escopo e decisões propostas

Data: 10/11/2026. Branch observada: `av2`.
Status: fases 0 a 3 concluídas; logging e métricas validados; fase 4 pendente.

## 1. Objetivo

Continuar o CareerPath da AV1 acrescentando monitoramento ao serviço BentoML:
registrar entradas, saídas e execução das inferências em arquivo texto append-only,
expor `/metrics` e permitir que o professor reproduza a demonstração pelo README.

A modalidade aplicável é a seção 1 do enunciado, para servidores de modelos.
O workflow de qualidade existente não transforma o projeto no pipeline Garmin da
seção 2. Artifacts de execução desse pipeline não são requisitos desta modalidade.

## 2. Fontes e estado encontrado

- Enunciado da AV2 fornecido pelo usuário em `Texto colado.txt`, lido integralmente
  nesta sessão. Os requisitos aplicáveis estão consolidados na matriz abaixo.
- Código em `src/careerpath/`, exemplos, testes, Dockerfile, justfile e CI.
- Contexto de negócio em `docs/phase-0-design.md` e no documento de entendimento
  de negócio da AV1. O classificador é um componente socioeconômico auxiliar;
  renda inferida não mede intenção de compra ou necessidade de desenvolvimento.
- Plano e histórico da AV1 em `docs/fases.md` e `docs/checkpoints.md`.
- Commit observado: `d2982c2`; árvore limpa antes de criar estes documentos.
- Modelo existente: `models/adult-income-v1.pkl`, com `models/metadata.json`.
- Endpoints declarados: `POST /predict` e `GET /health`.
- README atual: somente o título do repositório.
- Não há logging de entradas/saídas implementado no código da aplicação.
- `/metrics` é oferecido pelo runtime BentoML segundo sua documentação, mas não
  foi verificado em execução nesta sessão.
- Os checkpoints antigos registram 41 testes aprovados. Isso é evidência histórica,
  não uma execução nova. O comando `uv` não foi localizado no PATH desta sessão.

## 3. Requisitos aplicáveis

| Requisito do enunciado | Pontos informados | Evidência prevista |
| --- | --- | --- |
| Arquivo texto append-only no disco do processo | Parte dos 50 de logging | JSONL real, com linhas anteriores preservadas após novas chamadas e reinício |
| Dados relevantes de entrada e saída | Parte dos 50 de logging | Seis features, classe e probabilidade, com justificativa ligada ao CRISP-DM |
| Dados suficientes para histogramas, boxplots, KS e PSI futuros | Parte dos 50 de logging | Valores individuais, tipos documentados, nulos identificáveis e referência definida |
| Data e hora detalhadas | Parte dos 50 de logging | Timestamp ISO 8601 em UTC com microssegundos |
| `GET /metrics` em exposição Prometheus | Parte dos 10 de métricas | Resposta real do runtime e comparação antes/depois da carga |
| Texto sobre latência, histograma, boxplot, taxa de erros e retenção | Parte dos 10 de métricas | Guia com cálculos, unidades, limites e dados reais |
| Professor consegue gerar carga e ver o rastro usando o README | Transversal | Instalação, startup, carga, leitura do log e consulta às métricas reproduzíveis |

O trecho aplicável soma 60 pontos. Não inferir outros critérios ou os 40 pontos
restantes da AV2. Prazo, tag e duração de apresentação da AV2 não foram informados;
não reutilizar automaticamente datas, tag `sr1` ou regras de apresentação da AV1.

O enunciado recomenda uma planilha e permite análises demonstrativas. Não exige
construir dashboards, calcular KS/PSI agora ou implantar Prometheus/Grafana.

## 4. Abordagem

Opção proposta: manter BentoML, modelo, dataset e contratos da AV1; acrescentar
captura HTTP de inferência, arquivo JSONL e usar as métricas nativas do servidor.
É a menor continuação que atende ao enunciado e preserva os testes existentes.

Alternativas consideradas: trocar para FastAPI exigiria migrar um servidor que já
existe; instrumentar apenas a função `predict` perderia erros que ocorrem antes
dela, como JSON malformado e validação. Essas alternativas não são adotadas.

As decisões técnicas abaixo são propostas deste planejamento, não resultados já
implementados. A integração pública de middleware e os nomes reais das métricas
devem ser confirmados na versão fixada, BentoML `1.4.39`, antes de escrever código.

## 5. Contrato proposto do rastro

Arquivo padrão: `logs/inference.jsonl`, UTF-8, um objeto JSON por linha, escrito
com `logging.FileHandler` em modo `a`. `CAREERPATH_LOG_PATH` permite escolher outro
caminho; um caminho relativo é resolvido a partir do diretório de trabalho.

Um evento por requisição de inferência concluída, incluindo falhas observáveis:

| Campo | Conteúdo |
| --- | --- |
| `schema_version` | Inteiro `1`, versão do formato de monitoramento |
| `timestamp` | Finalização em UTC, ISO 8601 com microssegundos e fuso |
| `request_id` | UUID gerado pelo servidor para esta requisição |
| `method`, `endpoint` | Método e caminho, inicialmente `/predict` |
| `status_code` | Status HTTP efetivamente enviado; nulo se nenhuma resposta começou |
| `outcome` | `success`, `client_error` ou `server_error` |
| `latency_ms` | Duração medida com relógio monotônico, do início HTTP ao término da resposta |
| `input` | Somente `age`, `education`, `workclass`, `occupation`, `marital_status`, `hours_per_week` |
| `output` | Classe, probabilidade e versão presentes na resposta; nulo nas falhas |
| `model_version` | Versão do artefato carregado, também nos erros |
| `error_type` | Categoria sanitizada do erro, ou nulo |
| `input_capture` | `complete`, `invalid_json`, `truncated` ou `unsupported` |

Registrar campos faltantes como ausentes e preservar `null` explícito. Para entradas
inválidas, conservar apenas valores escalares dos campos permitidos; limitar textos
a 80 caracteres e omitir estruturas aninhadas. Não salvar corpo bruto, campos extras,
IP, cookies, autorização, cabeçalhos ou mensagens de exceção com payloads embutidos.
O exemplo de log na documentação deve ser identificado como ilustrativo até existir
uma captura real. Evidências devem usar somente perfis sintéticos ou dados públicos.

A captura deve observar o HTTP antes da validação e preservar o corpo consumido
pelo BentoML e a resposta ao cliente. Limite proposto de captura: 8 KiB por corpo;
excedê-lo interrompe somente a cópia de monitoramento, sem mudar a API. Corpos
incompletos não entram nas análises de features; o evento continua com status e tempo.
`/health` e `/metrics` ficam fora deste arquivo para não poluir as distribuições.

O rastro não é transacional: queda abrupta do processo ou falha do disco pode impedir
o último evento. Validar o destino na inicialização; erro de abertura impede startup.
Falha posterior de escrita deve aparecer claramente em stderr, sem sucesso silencioso
do monitoramento e sem substituir uma resposta HTTP já iniciada.

## 6. Variáveis e referência

- Entradas numéricas: `age` e `hours_per_week`; permitem histogramas, boxplots,
  comparação KS e PSI com referência numérica.
- Entradas categóricas: quatro campos restantes; permitem frequências e PSI
  categórico com política explícita para nulos e categorias desconhecidas. Não
  aplicar KS diretamente a códigos arbitrários de categorias.
- Saída numérica: `probability_above_50k`; permite histogramas, boxplots e futura
  comparação com probabilidades produzidas pelo mesmo modelo na referência.
- Saída categórica: `income_class_proxy`; permite proporções por classe.
- Operação: `latency_ms`, `status_code` e `outcome`; sustentam latência e erros.

Referência proposta: partição Adult usada no treinamento, após a mesma limpeza e
remoção de sobreposição presentes em `train.py`. Registrar origem, hashes, versão
do modelo e procedimento de reconstrução. Para referência da saída, executar o
modelo sobre esses perfis; não comparar probabilidades com os rótulos verdadeiros.
Não é necessário gerar esse conjunto nesta entrega para demonstrar o logging.
Se gerado, deve ser separado do tráfego sintético e ter proveniência explícita.

Mudança de distribuição dos dados ou previsões é um sinal a investigar. Sozinha,
não comprova mudança na relação entre entradas e rótulo, nem queda de acurácia.

## 7. Métricas e persistência

Usar `/metrics` do BentoML sem criar outro endpoint concorrente. Confirmar nomes,
labels, buckets e unidades na execução real. Não confundir métricas de treinamento
em `metadata.json` com métricas operacionais do servidor.

O guia deve explicar contagens de intervalo por diferença entre duas coletas;
histogramas clássicos possuem buckets cumulativos, cuja diferença entre limites
adjacentes fornece a frequência da faixa. Explicar também média de latência por
diferença de soma dividida por diferença de contagem e conversão de segundos em ms.

Taxas: `100 * delta(4xx + 5xx) / delta(total)` para falhas HTTP e, separadamente,
`100 * delta(5xx) / delta(total)` para falhas do servidor, filtradas por endpoint.
Sem requisições, apresentar `N/A`. Não subtrair contadores através de um reinício;
iniciar uma janela nova. Erro de rede do cliente é relatado separadamente.

Boxplot exato usa latências individuais do JSONL: Q1, mediana, Q3 e regra de 1,5 IQR.
Quartis estimados por buckets devem ser identificados como aproximações; os buckets
não recuperam observações individuais nem os outliers exatos. Explicar que a duração
do middleware pode diferir da medida pelo runtime por usar fronteiras diferentes.

Configuração inicial: um worker de aplicação e um escritor do arquivo; confirmar
essa topologia em execução, sem presumir que uma configuração de teste vale no CLI.
Não prometer escrita multiprocesso segura por um `FileHandler` compartilhado. Se a
topologia real exigir múltiplos escritores, rever a estratégia antes de implementá-la.

Métricas do processo não constituem histórico persistente: observar o comportamento
após reinício e documentá-lo. O arquivo de log é preservado até remoção manual nesta
PoC, sem rotação automática inicial. No Docker, criar diretório gravável pelo usuário
UID 10001 e oferecer volume para sobreviver à remoção do container. Não confundir
reiniciar o processo, reiniciar o container e remover um container com `--rm`.

## 8. Preservação dos arquivos da AV1

| Arquivos | Orientação |
| --- | --- |
| `src/` | Manter: implementação usada pela AV2 |
| `models/` | Manter: a API depende do artefato e da metadata para iniciar |
| `tests/` | Manter e ampliar: detectam regressões da API e do modelo |
| `examples/` | Manter: contratos executáveis e base das demonstrações |
| `scripts/download_data.py` e `train.py` | Manter: origem e reconstrução do modelo/referência |
| `pyproject.toml`, `uv.lock`, Dockerfile, CI, justfile | Manter e ajustar quando a AV2 exigir |
| Documentação e PDF da AV1 | Preservar como histórico e contexto de negócio; não é dependência de execução |
| `.venv`, caches, logs e resultados gerados | São locais/recriáveis; não precisam ser versionados |

Não duplicar o projeto inteiro em pastas AV1 e AV2. Git preserva versões; a branch
`av2` evolui os mesmos arquivos. Uma reorganização da documentação antiga pode ser
feita depois, atualizando links, mas não é necessária para começar a AV2.

## 9. Limites

Não fazem parte deste plano: novo modelo, novo dataset, novo tema, CRM, ranking
comercial completo, deploy, Garmin, Gemini, banco de dados, Grafana, alertas de drift,
retreinamento automático ou migração de framework. Planilha e gráficos são opcionais.
Não apagar arquivos, criar tags, fazer commit, push ou merge nesta etapa de planejamento.

## 10. Referências técnicas

- [Logging no Python 3.12](https://docs.python.org/3.12/howto/logging.html)
- [Logging do BentoML](https://docs.bentoml.com/en/latest/build-with-bentoml/observability/logging.html)
- [Métricas do BentoML](https://docs.bentoml.com/en/latest/build-with-bentoml/observability/metrics.html)
- [Formato de exposição Prometheus](https://prometheus.io/docs/instrumenting/exposition_formats/)
- [Histogramas e summaries](https://prometheus.io/docs/practices/histograms/)

Documentação `latest` orienta o desenho, mas não substitui a verificação da versão
fixada do projeto. O enunciado do professor continua sendo a fonte dos requisitos.

## 11. Resultado da fase 0 — revisão após o commit do planejamento

Revisão realizada em 10/11/2026 sobre a branch `av2`, HEAD `496d277`
(`docs: planeja continuidade do CareerPath para AV2`). Esta seção registra o
resultado da descoberta; as seções anteriores continuam sendo o contrato proposto.

### Arquitetura definida para a continuação

```text
Cliente / gerador de carga
          |
          v
Servidor BentoML
  captura HTTP de /predict -> validação Profile -> pipeline existente -> Prediction
          |                                                         |
          +---------- evento de entrada + saída + tempo + status ----+
                                    |
                                    v
                         logs/inference.jsonl (append)

GET /metrics -> exposição nativa BentoML, consultada antes/depois da carga
GET /health  -> contrato atual preservado
```

O ponto de extensão HTTP será confirmado na fase 1 para incluir JSON malformado e
validação rejeitada antes de `predict`. O diagrama não comprova que esse ponto já
foi instalado ou testado. A inferência e o treinamento não receberão dependência
do módulo de monitoramento; a composição fica no serviço HTTP.

### Contrato existente que deve ser preservado

| Campo HTTP | Uso atual e motivo para observar | Nome no dataset/pipeline |
| --- | --- | --- |
| `age` | Idade, distribuição numérica de perfis recebidos; inteiro de 17 a 100 | `age` |
| `hours_per_week` | Jornada semanal, distribuição numérica; inteiro de 1 a 99 | `hours-per-week` |
| `education` | Escolaridade, frequência das categorias | `education` |
| `workclass` | Vínculo de trabalho, frequência e presença de nulos | `workclass` |
| `occupation` | Ocupação, frequência e presença de nulos | `occupation` |
| `marital_status` | Estado civil, frequência das categorias | `marital-status` |

Os seis campos são exigidos pelo schema; `workclass` e `occupation` aceitam `null`,
o que não equivale a campo ausente. Categorias têm até 80 caracteres; `?` e campos
extras são rejeitados. O monitoramento não deve mudar essas regras.

A saída continua com `income_class_proxy`, `probability_above_50k` e
`model_version`. O limiar atual é 0,5: igualdade já resulta em `>50K`.
Não acrescentar score comercial, renda atual ou decisão de elegibilidade ao contrato.

### Evidências estáticas verificadas

- SHA-256 do arquivo `models/adult-income-v1.pkl`:
  `cfc85186a943d1ec52b97a8c9ee4b675d948a69918ae958a6d72c222027bb716`.
  O valor calculado com `Get-FileHash` corresponde ao registrado na metadata.
  Essa correspondência não substitui carregar o modelo no runtime compatível.
- `load_artifact` verifica hash, versão de scikit-learn e tipo do artefato antes
  de retornar o pipeline; não é necessário criar outro carregador para a AV2.
- O E2E atual já inicia e encerra o serviço duas vezes; será ampliado para usar o
  mesmo destino de log entre ciclos. Ainda não verifica logs nem métricas.
- Os testes de serviço esperam HTTP 400 para entradas inválidas. Preservar o
  comportamento observado pela suíte; não presumir HTTP 422 por analogia a FastAPI.
- `Dockerfile` usa UID 10001 e ainda não prepara um diretório de logs gravável.
- A CI aceita push em `main` e pull requests; push direto em `av2` não está listado.
- A instalação pede Python `>=3.12,<3.13`; o launcher local listou somente Python
  3.14 na preparação anterior. O runtime da aplicação ainda precisa ser preparado.

### Decisões e dependências da próxima fase

| Decisão consolidada | Verificação exigida antes de implementá-la |
| --- | --- |
| Usar captura HTTP, em vez de logging somente dentro de `predict` | API pública e ordem dos middlewares na versão BentoML fixada |
| Usar um escritor para `inference.jsonl` | Configuração e topologia efetivas no comando CLI |
| Aproveitar métricas nativas | Resposta de `/metrics`, nomes, labels e unidade reais |
| Preservar previsões e validação | Baseline atual com instalação frozen, pytest e Ruff |
| Manter histórico da AV1 | Limitar alterações de documentação nova a `docs/av2/` nesta fase |

Não há impedimento de escopo para a continuação. Ausência de runtime verificado é
uma pendência da fase 1, não prova de defeito no serviço. A fase 0 termina aqui;
ainda não há evidência atual de logging, métricas, teste ou container funcionando.

## 12. Atualização após a fase 1

O estado acima registra o encerramento da fase 0. Em 10/11/2026 a fase 1 confirmou
o ambiente frozen, 41 testes aprovados, Ruff aprovado, respostas HTTP reais,
`/metrics` nativo e um worker efetivo. A integração pública e a propagação de erro
no startup também foram sondadas. Os detalhes, comandos, limites e registro da
retomada após reinício estão no [baseline da fase 1](phase-1-baseline.md).
O logging da AV2 e seus testes permanentes ainda serão implementados na fase 2.

## 13. Atualização após a fase 2

Em 10/11/2026 foi implementada captura HTTP append-only com logger configurado no
startup do único worker e fechado no shutdown. O contrato JSONL, sanitização,
limites e interpretação dos campos estão em [log-format.md](log-format.md).
A suíte passou com 59 testes, incluindo os 41 anteriores; o servidor real gerou
três eventos 200/400/400 com saída correspondente à resposta. `/metrics` nativo
continuou respondendo e não virou evento de inferência.

Foi necessário preparar `/app/logs` no Dockerfile e excluir logs do contexto para
que o novo requisito de escrita não tornasse o startup incompatível com UID 10001.
Build/volume Docker, análises detalhadas de métricas e geração de carga continuam
nas fases correspondentes, sem alegar validação de container nesta fase.

## 14. Atualização após a fase 3

Em 10/11/2026, o E2E passou a validar contadores e histogramas antes/depois de uma
inferência válida e uma inválida em cada um de dois startups. O reset foi observado
no segundo ciclo. O guia [metrics.md](metrics.md) reúne cálculos, retenção, limites
de quantis, boxplot pelo JSONL e capturas reais versionadas. A suíte completa passou
com 59 testes; não houve mudança no código da aplicação nem nas dependências.
O exemplo de log vazio foi corrigido e reexecutado após a revisão independente.
