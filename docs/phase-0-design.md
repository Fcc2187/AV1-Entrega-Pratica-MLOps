# Fase 0 — Descoberta e design proposto

Status: Fase 0 concluída — design consolidado; parada no Model Gate 1.

O plano por fases, as oito páginas do Project Charter v1.4 e o enunciado integral
da segunda entrega foram lidos e confrontados. Este documento define a proposta
para implementação; não atesta um serviço funcionando nem pontos já conquistados.
A Fase 1 depende da troca manual para GPT-5.6 SOL/HIGH e da resposta CONTINUAR.
Nenhuma implementação foi iniciada.

## 1. Fontes e estado encontrado

- Plano de orquestração por fases anexado à conversa, com gates manuais de modelo.
- Enunciado integral e rubrica da segunda entrega, recebidos no segundo anexo
  textual da conversa: segunda nota da AV1, valendo 40% dela, total de 40 pontos.
- `Entendimento de negócio.docx.pdf`: oito páginas, todas lidas.
- `README.md`: apenas o título do repositório.
- Branch: `main`, acompanhando `origin/main` segundo as referências locais.
- HEAD: `17d0acea2cb9dec24c0bf543b79960cd4edf3837`.
- Histórico local: `17d0ace` e `898fed0`; somente o README está versionado.
- O PDF já estava não rastreado antes deste trabalho. Seu conteúdo foi preservado.
- Não há código, notebook, dataset, artefato de modelo, testes, lock ou checkpoint anterior.
- Não há `AGENTS.md` na raiz do projeto nem em `D:/`; não há grafo Graphify existente.
- Nenhuma tag local encontrada. Não foi feito fetch para verificar o remoto.
- Python acessível fora do sandbox: 3.11.9. uv: 0.12.5.
- Python 3.12 e compatibilidade das dependências serão preparados na Fase 1.

## 2. Coerência com o negócio

O objetivo aprovado permanece o do PDF: melhorar a priorização comercial do
Career Accelerator, identificando a combinação de necessidade de desenvolvimento,
engajamento e possibilidade de investimento. O piloto prevê aumento relativo de
20% na conversão em oito semanas, 75% de confirmação do público-alvo entre os de
alta prioridade e 60% das abordagens originadas da fila priorizada (páginas 5–7).
Esses números são metas de negócio, não métricas obtidas pelo modelo.

Hoje, os consultores atendem por ordem de chegada, engajamento e julgamento manual.
No processo futuro descrito no PDF, o processamento noturno alimenta uma fila no
CRM até 08:00; Growth revisa a ordem e o consultor decide o contato. O cliente
escolhe entre tiers preexistentes. Preço, benefício e elegibilidade não dependem
automaticamente do sinal de renda. A indisponibilidade da fila exige fallback manual.

A API acadêmica proposta serve somente o componente socioeconômico desse processo.
O rótulo supervisionado é a faixa histórica `>50K` versus `<=50K` do Adult; ele não
substitui o target de negócio aprovado. Necessidade de desenvolvimento, estágio
de carreira, intenção de compra, conversão e tempo de espera não são rótulos
observados nessa base. Não criaremos esses rótulos por regras arbitrárias.

O dataset é o UCI Census Income/Adult, ID 20, extraído da base censitária de 1994.
A referência e o rótulo são confirmados na [fonte oficial da UCI](https://archive.ics.uci.edu/dataset/20/census+income).
O limite de US$ 50 mil/ano pertence ao contexto histórico da base; não será
convertido em renda atual, poder de compra ou capacidade comprovada de pagamento.

O endpoint retorna um sinal auxiliar por perfil. Integrar CRM, engajamento,
necessidade confirmada e tempo de espera pertence à aplicação operacional futura,
conforme o escopo de MVP do enunciado. Não haverá um campo de prioridade comercial
calculado somente a partir da probabilidade de renda.

O enunciado exige o mesmo problema, fonte e modo de inferência da primeira prova.
Preservamos CareerPath, Adult e a classificação tabular de faixa de renda como
componente socioeconômico. O processamento noturno é o consumo futuro desse
componente: um chamador poderia enviar os perfis à API, um por vez, e combinar
as respostas com sinais do CRM. Expor a inferência via HTTP não implementa nem
substitui a regra comercial completa ou o processamento noturno descritos no PDF.
Não foi fornecido notebook/contrato da primeira prova além do PDF; não é possível
atestar igualdade com um artefato ausente. Na Fase 2, repetir a procura prevista
no plano e preservar eventual inferência anterior tecnicamente apropriada. Se
ela conflitar com esta proposta, registrar a divergência antes de substituí-la.

## 3. Requisitos identificados e limites

Esta classificação distingue exigências do professor de compromissos adicionais
do plano do usuário. O enunciado não exige treinar, testes automatizados ou um
endpoint chamado /predict, mas o plano os exige e continua sendo seguido.

| Categoria | Itens |
| --- | --- |
| Obrigatório no enunciado | Mesmo problema, fonte e modo de inferência da primeira prova; repositório público no GitHub com código, instruções e evidências e link submetido; serviço local respondendo ao vivo; apresentação de 15 minutos e 5 de perguntas; participação oral de todos os presentes; README do clone à predição, Python e tempo aproximado; pyproject.toml e uv.lock commitado; ausência de segredos e dados pessoais reais; variáveis de ambiente e .env.example com nomes sem valores; .gitignore; endpoint, entrada, saída e curl copiável; LICENSE; Uso de IA com ferramenta, pedidos e avaliação crítica; congelamento por tag sr1 no prazo. |
| Obrigatório adicional no plano | Python 3.12, instalação frozen; src/ e estrutura indicada; treinamento real e reproduzível na ausência de modelo anterior; pipeline completo local e metadata; BentoML; POST /predict e GET /health; validação; três exemplos válidos e um inválido; pytest, ruff e E2E com reinício; evidências reais detalhadas; roteiro de apresentação e roteiro de vídeo; checkpoints e gates. |
| Obrigatório para coerência com o PDF | Manter objetivo de negócio e decisão humana; explicitar o limite do proxy; comparar o classificador com classe majoritária ou regra simples; não apresentar metas do piloto como resultados do Adult. |
| Diferenciais do professor, em ordem de valor | 1. Dockerfile ou bentoml containerize com imagem subindo; 2. comando único que faz tudo; 3. origem e versão/treino do modelo no README; 4. ruff no CI; 5. revisão entre integrantes por PR; 6. /health que responde. |
| Ordem de execução dos diferenciais no plano | Fase 5: Dockerfile, justfile e GitHub Actions, somente após o núcleo funcionar. /health entra antes, na Fase 3, por exigência do plano; origem do modelo será registrada no treinamento e documentada na Fase 6. Runtime Docker apenas se disponível, com limitação declarada se não testado. Revisão por colegas permanece ação da equipe. |
| Explicitamente excluído | Deploy; criar/push da tag sr1 durante o trabalho; preços ou benefícios individuais automáticos; crédito; bloqueio de acesso; contratação/demissão; qualquer elegibilidade automática. |
| Fora do MVP acadêmico | CRM real, painel comercial, agendamento noturno, ranking completo, piloto de negócio, telemetria externa e dados reais de prospects. Front-end, uso complexo, deploy e log de experimentos não somam pontos segundo o enunciado. |

### Matriz da rubrica oficial

| Critério | Pontos | Evidência planejada | Fases |
| --- | --- | --- | --- |
| Objetivo e processo de negócio | 9 | README e apresentação explicam decisão, responsável, antes/depois e limite do componente socioeconômico. Métricas técnicas apenas apoiam essa explicação. | 0, 6, 7, 8 |
| Serviço de pé e demonstrado | 9 | BentoML local reiniciado, chamada ao vivo e resposta real; três casos disponíveis e um erro explicável. Vídeo é plano B, não equivale à execução ao vivo. | 3, 4, 7, 10 e apresentação |
| Instruções reproduzíveis | 9 | Outra equipe consegue seguir clone, setup e predição; Python, comandos exatos e tempo medido; README mostrado na apresentação. | 1, 6, 7, 8, 10 |
| Repositório | 6 | GitHub público; código e evidências; pyproject e lock commitado; .env.example sem valores; .gitignore; ausência de segredos/dados pessoais reais; contrato e curl; LICENSE; Uso de IA. | 1–8, 10 e submissão |
| Domínio oral individual | 7 | Todos os integrantes presentes falam; cada um consegue explicar qualquer linha e responder às perguntas do professor. | 7 e preparação da equipe |
| Total | 40 | A Fase 0 planeja a cobertura; não atribui nota nem atesta critérios ainda não executados. | — |

### Prazo, entrega e responsabilidades humanas

- Entrega: 24/09 às 10:30; apresentação em 24/09 ou 29/09, conforme sorteio a ser
  publicado pelo professor até 22/09. Não presumir qual data foi atribuída à equipe.
- Outra pilha exige aprovação do professor até 23/09. Manter BentoML como servidor
  e runtime principal; a pequena rota ASGI é extensão interna de /health, não um
  serviço FastAPI independente. Agente/Google ADK não se aplica a este projeto.
- Criar e enviar sr1 às 10:30 de 24/09 é obrigação da equipe conforme o enunciado.
  O agente apenas documentará `git tag -a sr1 -m "Entrega do SR1"` e
  `git push origin sr1`, pois o plano proíbe criá-la durante a execução.
- A equipe deverá tornar/verificar o repositório público e submeter seu link,
  revisar o commit final, gravar o vídeo e ensaiar a apresentação. A visibilidade
  pública e a submissão ainda não foram verificadas nem realizadas.
- O vídeo deve ter cerca de dois minutos e mostrar a mesma demonstração. Se o
  serviço falhar, explicar o que quebrou e o que foi tentado; o vídeo não preserva
  integralmente a pontuação da execução. Não consumir a apresentação tentando
  reparar indefinidamente a chamada.
- Entregas atrasadas valem 80%, segundo o enunciado. Não há extensão de prazo
  por escolha de outra pilha.

### Ajustes concretos à preparação

- .env.example listará somente variáveis realmente usadas, sem valores de
  exemplo ou segredos. Esta PoC local não exige credenciais de serviços externos.
- LICENSE proposta: MIT para o código da equipe; manter a atribuição e os termos
  próprios da fonte de dados, sem apresentar a licença de código como licença do dataset.
- justfile oferecerá os comandos sugeridos no plano e um `just demo` que prepare
  o ambiente e execute a demonstração E2E, reaproveitando a rotina de teste do
  serviço. Não criar outro orquestrador apenas para essa finalidade.
- O README terá origem e versão/treino do modelo, ainda que seja diferencial na
  rubrica, porque o plano já o exige.
- A revisão por PR depende de outro integrante e de trabalho efetivamente
  revisado. Não inventar revisão nem abrir/publicar PR sem autorização.

Também não se justificam nesta PoC: banco de dados, fila de tarefas, autenticação
de produção, AutoML, busca extensa de hiperparâmetros ou serviços separados de
pré-processamento e inferência. O serviço de demonstração ficará em localhost.

## 4. Alternativas e arquitetura escolhida

1. **Recomendada:** um serviço BentoML e um pipeline scikit-learn local. Atende à
   entrega com poucas peças, permite inferência offline e tem treinamento separado.
2. Serviço com cadastro/importação obrigatório no model store do BentoML: possível,
   mas acrescenta uma etapa de preparação ao clone. Só usar se a rubrica exigir.
3. Sistema completo de CRM e priorização: exige dados e critérios que não estão
   disponíveis. Não resolve a falta desses dados inventando um score.

Fluxo de treinamento: arquivos locais do Adult → leitura e normalização → treino
do pipeline → avaliação no teste separado → artefato e metadata.

Fluxo de inferência: JSON → validação Pydantic → organização das seis colunas →
pipeline carregado na inicialização → probabilidade e classe proxy → JSON.

Uma classe de serviço será responsável pelo ciclo de vida do modelo e por
`POST /predict`. BentoML documenta serviços por classe e endpoints de inferência
com `@bentoml.api`: [serviços BentoML](https://docs.bentoml.com/en/latest/build-with-bentoml/services.html).

Para o `GET /health` literal exigido, a proposta é montar uma rota ASGI mínima
com Starlette no mesmo serviço, usando a instância carregada para informar saúde.
Não confundir `/health` com os endpoints nativos `/livez` e `/readyz`.
A integração ASGI é suportada pelo BentoML; a compatibilidade da rota será
testada na versão fixada: [integração ASGI](https://docs.bentoml.com/en/latest/build-with-bentoml/asgi.html).

Dependências de runtime propostas: BentoML, scikit-learn, Pydantic, pandas para
CSV/tabelas com colunas nomeadas e Starlette para a rota GET. Dependências usadas
diretamente serão declaradas, mesmo se também forem transitivas. Desenvolvimento:
pytest e ruff. Persistência com pickle da biblioteca padrão. O resolvedor de uv
selecionará versões compatíveis; a Fase 1 fixará os números e o patch do Python
3.12 efetivamente testado. Não há instalação validada nesta fase.

## 5. Features e contrato de entrada

Escolha proposta: seis variáveis compatíveis com um formulário acadêmico de perfil.
O PDF menciona idade, escolaridade, setor e estado civil. Tipo de vínculo, ocupação
e horas semanais complementam o perfil profissional; a disponibilidade real desses
campos precisaria ser confirmada antes de uma integração de CRM.

| Campo JSON | Coluna Adult | Validação proposta |
| --- | --- | --- |
| age | age | Inteiro estrito entre 17 e 100. |
| education | education | String de 1 a 80 caracteres após trim. |
| workclass | workclass | String de 1 a 80 caracteres ou null. |
| occupation | occupation | String de 1 a 80 caracteres ou null. |
| marital_status | marital-status | String de 1 a 80 caracteres após trim. |
| hours_per_week | hours-per-week | Inteiro estrito entre 1 e 99. |

Todos os campos devem estar presentes; null só será aceito nos campos indicados.
Os limites numéricos são guardas do contrato proposto, não uma afirmação de
cobertura de todos esses valores no treinamento. Booleanos e strings numéricas
não serão convertidos em inteiros. Campos extras serão rejeitados.

As categorias dos exemplos usarão os nomes originais da UCI. Categorias novas,
desde que strings válidas, serão aceitas e ignoradas pelo OneHotEncoder no bloco
correspondente. Isso assegura execução, não qualidade preditiva para essa categoria.
Não usar Enum fechado que contradiga o teste de categoria desconhecida.

Trim e tratamento de `?` serão iguais na preparação de treino e inferência.
Em workclass/occupation, `?` representa ausência e segue para imputação; campos
obrigatórios não nulos vazios ou `?` serão inválidos no contrato HTTP.
As tabelas passadas ao pipeline terão a mesma ordem, nomes e tipos em ambos os fluxos.

| Features excluídas | Motivo da decisão de design |
| --- | --- |
| race, sex | Excluir dos preditores operacionais, conforme preferência do plano. |
| fnlwgt | Peso amostral, não atributo natural que um prospect informa. Não será usado como feature nem peso de treinamento no baseline. |
| relationship | Informação doméstica adicional e categorias que também revelam sexo; pouco justificável no formulário. |
| native-country | Origem nacional não é necessária para demonstrar o componente. |
| capital-gain, capital-loss | Informações financeiras detalhadas pouco adequadas ao formulário básico descrito. |
| education-num | Representação adicional de escolaridade; manter somente education simplifica o contrato. |

Excluir race/sex não elimina vieses nem associações indiretas com outras variáveis,
incluindo idade e estado civil. A escolha limita coleta e escopo; não constitui
certificação de equidade nem validação para uso operacional.

## 6. Modelo, avaliação e persistência

Proposta de baseline:

- Numéricas: SimpleImputer(strategy="median") + StandardScaler.
- Categóricas: SimpleImputer(strategy="most_frequent") + OneHotEncoder(handle_unknown="ignore").
- Composição por ColumnTransformer, seguida de LogisticRegression em um Pipeline.
- Seed 42 onde aplicável, parâmetros registrados e convergência verificada.
- Sem ponderação automática de classes inicialmente; medir o baseline sem alterar
  a distribuição efetiva apenas para melhorar uma métrica isolada.

A composição mantém transformações e estimador unidos e ajuda a evitar vazamento
de estatísticas do teste: [pipelines scikit-learn](https://scikit-learn.org/stable/modules/compose.html).

Usar adult.data para treino e adult.test para teste, preservando a separação
fornecida. Remover espaços dos campos, tratar `?`, ignorar o cabeçalho de comentário
do teste e normalizar o ponto final dos rótulos de teste. Conferir número de linhas,
classes, campos ausentes e possíveis duplicatas entre partições antes do fit.
Se houver duplicatas completas, remover a sobreposição do treino preservando o
teste e registrar contagens; não deduplicar apenas pelas seis features selecionadas,
pois perfis iguais podem corresponder a pessoas diferentes.

Imputadores, scaler e encoder serão ajustados exclusivamente no treino. Se alguma
escolha exigir ajuste posterior, separar validação estratificada dentro do treino;
não escolher hiperparâmetros olhando repetidamente o teste final.

Comparar com DummyClassifier(strategy="most_frequent") nas mesmas partições.
Registrar accuracy, balanced accuracy, precision/recall/F1 para `>50K`, ROC-AUC,
Brier score e matriz de confusão com ordem explícita das classes. Tratar divisões
por zero nas métricas do baseline. Não prometer valores antes de executar.
Os falsos positivos/negativos da faixa de renda são diferentes dos erros comerciais
descritos no PDF; somente dados de piloto podem avaliar estes últimos.

Persistir `models/adult-income-v1.pkl` com o Pipeline completo. Não usar funções
locais/lambdas dependentes do processo de treinamento dentro do artefato.
Carregar exclusivamente o artefato confiável do projeto e manter as versões
do ambiente de treino e serviço iguais: [persistência scikit-learn](https://scikit-learn.org/stable/model_persistence.html).

`models/metadata.json` conterá model_name, model_version, dataset,
dataset_reference/DOI, features, excluded_features com justificativas,
sklearn_version, python_version, trained_at em UTC, seed, parâmetros, contagens
das partições, limpeza aplicada, hashes dos arquivos de dados e do artefato,
métricas do modelo e baseline, ordem das classes e limitações.

O artefato e metadata serão distribuídos junto do repositório, sem download
automático na inicialização. O serviço verificará presença e compatibilidade;
artefato ausente/corrompido deverá causar falha clara, sem treinar como fallback.
O caminho será resolvido em relação ao projeto/pacote instalado, sem depender
acidentalmente do diretório do terminal. Esta entrega será validada a partir de
clone com instalação local; distribuição wheel independente não faz parte do escopo.

O teste de persistência abrirá um processo Python novo e executará inferência.

## 7. Endpoints e exemplos propostos

### POST /predict

Uma observação por requisição, JSON na raiz, com Content-Type application/json.
BentoML suporta entrada raiz sem envelope adicional: [tipos de entrada](https://docs.bentoml.com/en/latest/build-with-bentoml/iotypes.html).

Exemplo sintético de entrada, ainda não executado:

```json
{
  "age": 35,
  "education": "Bachelors",
  "workclass": "Private",
  "occupation": "Tech-support",
  "marital_status": "Never-married",
  "hours_per_week": 40
}
```

Contrato de saída, sem inventar uma probabilidade:

| Campo | Tipo e significado |
| --- | --- |
| income_class_proxy | `<=50K` ou `>50K`; usar `>50K` quando p >= 0.5. |
| probability_above_50k | Float finito entre 0 e 1, obtido de predict_proba para a classe `>50K`. |
| model_version | String `adult-income-v1`, consistente com metadata. |

A posição da classe positiva será identificada por classes_, não presumida.
A probabilidade é uma estimativa do modelo para o rótulo histórico, não uma
probabilidade validada de compra nem comprovação da renda de uma pessoa.

O campo opcional socioeconomic_signal do exemplo conceitual do plano fica
excluído da proposta: repetiria a probabilidade com limiares arbitrários e poderia
ser confundido com prioridade. Assim não haverá categorização high/medium/low.

Sucesso: HTTP 200. Payload com campos/tipos/valores inválidos: HTTP 422 proposto,
com detalhe útil; JSON malformado: HTTP 400. Os códigos e o formato exato nativos
do BentoML serão verificados na Fase 3 e a implementação ajustada ao contrato.
Nenhum erro de validação deve ser disfarçado como 200 ou 500.

Planejar quatro arquivos:

1. case-1.json: perfil sintético do exemplo acima.
2. case-2.json: perfil sintético com escolaridade, ocupação, idade e horas diferentes.
3. case-3.json: perfil sintético com workclass/occupation ausentes, exercitando imputação.
4. invalid.json: age negativo, mantendo os demais campos válidos.

As três respostas válidas não precisam produzir classes distintas. Registrar
os resultados efetivos; não escolher valores para encenar superioridade do modelo.
Categoria desconhecida será coberta também por teste específico.

### GET /health

Retornar HTTP 200 e JSON com status="ok" e model_version somente quando a
instância estiver pronta com pipeline carregado. Estado conhecido de indisponibilidade
deve retornar 503; se a inicialização falhar, o processo pode não abrir a porta,
e não se deve prometer um 503 de um servidor que sequer iniciou.

O endpoint não baixa arquivos nem treina. Documentação interativa e endereço
localhost serão conferidos no serviço real antes de serem publicados no README.

## 8. Estratégia offline

- A instalação inicial de Python e dependências exige rede se não houver cache.
- Antes da apresentação: uv sync --frozen, artefato local, dependências e Python
  já disponíveis, exemplos e documentação local, serviço reiniciado e testado.
- No dia: executar com o ambiente preparado e flags offline/no-sync apropriadas
  à versão validada do uv; não resolver dependências durante a demonstração.
- Desabilitar telemetria do BentoML pela configuração documentada para a versão
  fixada e verificar ausência de downloads no caminho de inicialização/inferência.
- Testar reinício e chamadas com acesso externo indisponível e loopback disponível.
- Treinamento é opcional e separado. Um script de download explícito guarda os
  arquivos em data/raw/ ignorado pelo Git; treinar aceita os arquivos locais.
- Caso Docker funcione, deixar imagem construída localmente; não depender de pull.
- Preparar vídeo backup de cerca de 2 minutos; gravá-lo é uma ação posterior da equipe.

O tempo até a primeira predição será medido separando instalação fria,
inicialização com ambiente preparado e requisição. Nenhuma estimativa será
apresentada como tempo observado nesta fase.

## 9. Árvore prevista

Somente docs/phase-0-design.md é criado nesta fase. Os demais itens abaixo são
planejados, não arquivos existentes.

```text
.
├── README.md
├── Entendimento de negócio.docx.pdf
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── .env.example
├── LICENSE
├── src/careerpath/
│   ├── __init__.py
│   ├── schema.py
│   ├── model.py
│   ├── train.py
│   └── service.py
├── models/
│   ├── adult-income-v1.pkl
│   └── metadata.json
├── scripts/
│   └── download_data.py
├── examples/
│   ├── case-1.json
│   ├── case-2.json
│   ├── case-3.json
│   └── invalid.json
├── tests/
│   ├── test_model.py
│   └── test_service.py
├── docs/
│   ├── phase-0-design.md
│   ├── checkpoints.md
│   ├── evidence/
│   ├── presentation-outline.md
│   └── demo-video-script.md
├── Dockerfile
├── .dockerignore
├── justfile
└── .github/workflows/ci.yml
```

schema.py centraliza validação e normalização compartilhadas; model.py organiza
colunas e carrega/usa o artefato; train.py contém preparação, fit, avaliação e
persistência. service.py expõe os endpoints e carrega uma vez por worker.
Sem interfaces, factories ou camadas de repositório adicionais.

## 10. Testes e evidências

Cobertura mínima proposta:

1. Pipeline carrega em processo novo e metadata corresponde ao artefato.
2. Inferência válida retorna classe permitida, probabilidade finita em [0,1] e versão.
3. Classe calculada é consistente com p e limiar, incluindo a fronteira 0.5.
4. Valores ausentes admitidos e categoria inédita passam pelo pipeline.
5. HTTP real: health, três casos válidos, campo inválido, tipo inválido, extra e JSON malformado.
6. Reinício real do serviço e nova sequência health/predict, com limite de espera
   e encerramento apenas do processo iniciado pelo teste.
7. Inicialização com artefato ausente falha claramente, sem download/treinamento.

pytest e ruff serão executados na Fase 4 e depois dos diferenciais. A CI fará
instalação frozen, lint e testes usando o modelo distribuído, sem retreinar.
Os testes de serviço devem atravessar o HTTP, além das chamadas diretas de modelo.

Evidências terão comando, data, ambiente, commit, estado do worktree quando sujo,
código de saída e stdout/stderr reais. Registrar Python, instalação, startup,
health, três predictions, erro, pytest, ruff e Docker se executado.
Não reutilizar números ilustrativos como evidência. Não registrar dados reais de prospects.

Fase 6: README deve cobrir os 37 itens do plano, com comandos efetivamente
executados e curl.exe no PowerShell. Evitar escapes frágeis usando os JSONs de
examples/ com --data-binary. O README deve funcionar sem just.

Fase 7: apresentação com exatamente os quatro blocos exigidos pelo plano:
objetivo (2 min), processo de negócio (3 min), como subir (4 min), demonstração
(6 min), total de 15 minutos; os cinco minutos de perguntas vêm depois.
Mostrar o README na tela no terceiro bloco e uma resposta real no quarto.
Distribuir falas para todos os integrantes presentes; os nomes e a quantidade de
integrantes serão preenchidos na preparação da equipe, sem inventar participantes.
Preparar perguntas sobre fluxo, features, limitação do proxy, dependências,
validação e qualquer código usado: domínio oral vale sete pontos individuais.
Roteiro de backup de aproximadamente 2 minutos.
Reexecutar os comandos importantes antes de registrar a documentação como concluída.

## 11. Ordem de implementação e gates

1. Fase 0 concluída com enunciado/rubrica confrontados e design consolidado;
   emitir a mensagem exata do Model Gate 1 e parar.
2. Após troca manual para SOL/HIGH e CONTINUAR: Fase 1, fundação e lock.
3. SOL: Fase 2, treino real, baseline, artefato, metadata e teste de recarga.
4. SOL: Fase 3, serviço e outputs HTTP; Fase 4, testes, lint e E2E.
5. SOL: Fase 5, Docker, just e CI; repetir checks e parar no Model Gate 2.
6. Após troca para TERRA e CONTINUAR: Fases 6–7, README, evidências e apresentação;
   parar no Model Gate 3.
7. ASTRA/MAX: Fase 8, auditoria inicialmente read-only. Se houver P0/P1, Gate 4
   para SOL, Fase 9 apenas para correções apontadas, depois Gate 5 para ASTRA.
8. ASTRA/MAX: Fase 10, verificação final e relatório prescrito pelo usuário.

Não trocar modelo automaticamente, ultrapassar gate, implementar nesta fase ou
criar a tag sr1. Os próximos checkpoints devem registrar mudanças, comandos,
resultados, pendências, riscos e fase seguinte.

## 12. Riscos e pendências

| Risco | Tratamento proposto |
| --- | --- |
| Inferência da primeira prova sem notebook fornecido | Preservar problema/fonte/classificação descritos; procurar novamente artefato na Fase 2 e não substituir silenciosamente um contrato anterior diferente. |
| Confundir renda histórica com o público-alvo | Separar objetivo comercial, rótulo supervisionado e decisão humana em API/README/apresentação. |
| Dados antigos e categorias estrangeiras | Documentar domínio da PoC e necessidade de revalidação com CRM atual; sem uso operacional alegado. |
| Disponibilidade das seis features | Formulário acadêmico explícito; coleta real precisa de validação futura. |
| Desempenho baixo com features reduzidas | Comparar baseline, publicar métricas reais e discutir limitações; não adicionar atributos só para inflar score. |
| Python/Windows/BentoML | Preparar 3.12 e testar startup/HTTP real cedo; fixar versões compatíveis. |
| GET /health e códigos de erro | Confirmar integração na versão fixada com testes HTTP reais. |
| Artefato ausente ou ambiente incompatível | Distribuir pipeline e metadata, instalar com lock e testar recarga em processo novo. |
| Rede indisponível na apresentação | Cache e modelo antecipados, reinício offline, exemplos locais e vídeo backup. |
| PDF fora do Git | Preservado; sua inclusão na entrega precisa ocorrer durante a preparação do repositório. |
| Docker indisponível | Registrar teste não realizado; não afirmar build/run bem-sucedido. |
| Publicação, prazo e apresentação | Equipe confirma GitHub público, envia link/tag no prazo, grava vídeo e distribui falas; ações humanas ainda pendentes. |

## 13. Checkpoint da Fase 0

**Feito:** leitura integral do plano e das oito páginas do PDF; inventário integral
do pequeno repositório; inspeção do README, histórico, branches e tags locais;
identificação do ambiente; consulta às fontes oficiais; leitura integral do
enunciado e rubrica recebidos na retomada; proposta de arquitetura, features,
contrato, avaliação, offline, testes, evidências e fases; matriz dos 40 pontos
e distinção entre exigências do professor, extras do plano e ações da equipe.

**Arquivos alterados:** criados docs/phase-0-design.md e docs/fases.md. README e
PDF preservados. Nenhum código de implementação, commit ou tag criado nesta fase.

**Comandos executados e resultados:**

- rg --files --hidden com exclusão de .git e .venv; Get-ChildItem -Force; leitura
  de README: encontrados somente README e PDF antes deste documento.
- git status/log inicialmente recusados por titularidade diferente no sandbox.
  Repetidos com `git -c safe.directory=D:/AV1-Entrega-Pratica-MLOps ...`, sem mudar
  a configuração global: status, log -5 --oneline, ls-files, branch -a,
  diff --stat, tag --list e rev-parse HEAD.
- Git também avisou falta de acesso ao arquivo de ignore global no sandbox;
  o inventário de diretório foi conferido independentemente.
- python e uv inicialmente sem permissão de execução no sandbox; executados fora
  dele com aprovação da ferramenta: Python 3.11.9 e uv 0.12.5.
- Verificação de módulos PDF: pypdf, pymupdf, fitz e pdfplumber não instalados
  nesse Python. Usado `uv run --no-project --with pypdf python -c ...` para
  PdfReader/extract_text de todas as páginas, em ambiente temporário do uv.
  A leitura foi repetida com stdout UTF-8 para preservar acentos.
- Leitura das referências oficiais UCI, BentoML, scikit-learn e uv pela ferramenta web.
- Na retomada: git status --short --branch com safe.directory local ao comando;
  Get-Content integral do checkpoint/design e do novo anexo textual do enunciado;
  atualização exclusivamente deste documento com apply_patch; conferência das
  seções, ausência de pendência antiga e estado final de Git.
- Após o Gate 1: criado docs/fases.md para explicar fases 0–10, gates, entregáveis
  e estado atual. O usuário autorizou commit e push desses documentos e do PDF
  diretamente na main antes de iniciar a Fase 1.

**Resultados:** design consolidado e rubrica mapeada; zero treinamento, testes, métricas
ou execução de serviço realizados. O leitor PDF temporário não foi adicionado
como dependência do projeto.

**Pendência para iniciar implementação:** troca manual para GPT-5.6 SOL/HIGH e
resposta CONTINUAR, conforme Model Gate 1. Nenhuma pendência documental impede
concluir esta fase. Notebook anterior não fornecido permanece risco explicitado,
com nova procura prevista na Fase 2; o plano permite baseline na sua ausência.

**Riscos conhecidos:** os da seção 12; compatibilidade runtime, métricas,
reprodução em ambiente limpo, publicação e domínio oral ainda não foram validados.

**Próxima fase:** Fase 1 — fundação do repositório. Ao receber CONTINUAR após a
troca manual, conferir git status, reler este checkpoint e confirmar a fase antes
de implementar. Nenhuma execução deve ultrapassar o Gate 1 automaticamente.
