# CareerPath MLOps

PoC local de inferência socioeconômica com o dataset **Census Income (Adult)**.
O serviço recebe seis atributos de um perfil e devolve a probabilidade estimada da
classe histórica `>50K`, a classe proxy e a versão do modelo.

> Este projeto não mede renda atual, intenção de compra, necessidade profissional
> nem potencial de carreira. O rótulo é um proxy histórico do Censo dos EUA de
> 1994 e deve apoiar revisão humana, nunca decisão automatizada sobre pessoas.


## Equipe 

- Caio Lima Bezerra
- Felipe Caminha
- João Marcelo
- Lucas Sukar
- Miguel Becker
- Luiz Arruda


## Índice

- [Pré-requisitos](#pré-requisitos)
- [Objetivo e uso responsável](#objetivo-e-uso-responsável)
- [Primeira execução](#primeira-execução)
- [Contrato HTTP e exemplos](#contrato-http-e-exemplos)
- [Qualidade, Docker e CI](#qualidade-docker-e-ci)
- [Modelo, dados e limitações](#modelo-dados-e-limitações)
- [Solução de problemas](#solução-de-problemas)
- [Entrega](#entrega)

## Pré-requisitos

- Git.
- Python **3.12**. O projeto aceita `>=3.12,<3.13` e fixa `3.12` em
  [`.python-version`](.python-version).
- [uv](https://docs.astral.sh/uv/) **0.12.5** para criar o ambiente a partir do
  lockfile.
- Docker Desktop é opcional para o caminho em container.
- [just](https://just.systems/) é opcional; os comandos principais abaixo não
  dependem dele.

O modelo e sua metadata já são versionados em `models/`. A primeira inferência
não baixa dados nem treina um modelo.

## Objetivo e uso responsável

A PoC demonstra apenas o componente socioeconômico de uma priorização comercial
hipotética do Career Accelerator. Hoje, consultores atendem por ordem de chegada,
engajamento e julgamento manual. No fluxo futuro proposto, um processamento
noturno forma uma fila no CRM até 08:00, Growth revisa sua ordem e o consultor
decide se fará o contato. A probabilidade desta API é só um sinal auxiliar: não
define preço, benefício, elegibilidade ou contato automático, e não há integração
com processo real nem uso operacional de dados pessoais.

## Primeira execução

Clone o repositório e instale exatamente as dependências fixadas:

```powershell
git clone https://github.com/Fcc2187/AV1-Entrega-Pratica-MLOps.git
cd AV1-Entrega-Pratica-MLOps
uv sync --frozen --python 3.12
```

Inicie o serviço em um terminal:

```powershell
uv run --frozen bentoml serve careerpath.service:CareerPathService --host 127.0.0.1 --port 3000 --do-not-track
```

Pare o processo com `Ctrl+C`. O serviço fica em `http://127.0.0.1:3000`.

Em outro terminal, confirme a prontidão:

```powershell
curl.exe http://127.0.0.1:3000/health
```

Resposta esperada:

```json
{"status":"ok","model_version":"adult-income-v1"}
```

Em uma máquina local já preparada, a instalação frozen levou menos de um segundo
e o serviço respondeu ao health em cerca de 6,4 segundos. Em clone/ambiente frio,
o tempo depende do download das dependências; mantenha o cache do uv antes da
apresentação.

## Contrato HTTP e exemplos

### `POST /predict`

Envie um objeto JSON na raiz com estes campos:

| Campo | Tipo | Regra |
| --- | --- | --- |
| `age` | inteiro | de 17 a 100 |
| `education` | texto | obrigatório, 1 a 80 caracteres |
| `workclass` | texto ou `null` | obrigatório; opção da lista abaixo |
| `occupation` | texto ou `null` | obrigatório; opção da lista abaixo |
| `marital_status` | texto | obrigatório, 1 a 80 caracteres |
| `hours_per_week` | inteiro | de 1 a 99 |

Campos extras, tipos incorretos, `?` como categoria, JSON malformado e valores
fora do intervalo recebem HTTP 400. `workclass` e `occupation` podem ser `null`.
Categorias fora da lista abaixo
recebem HTTP 400, acompanhadas da lista de opções válidas para o campo.

### Valores possíveis das variáveis categóricas

Os campos categóricos do dataset Adult usados pelo modelo aceitam apenas estes
valores:

- `workclass`: `Private`, `Self-emp-not-inc`, `Self-emp-inc`, `Federal-gov`,
  `Local-gov`, `State-gov`, `Without-pay`, `Never-worked`
- `education`: `Bachelors`, `Some-college`, `11th`, `HS-grad`, `Prof-school`,
  `Assoc-acdm`, `Assoc-voc`, `9th`, `7th-8th`, `12th`, `Masters`, `1st-4th`,
  `10th`, `Doctorate`, `5th-6th`, `Preschool`
- `marital_status`: `Married-civ-spouse`, `Divorced`, `Never-married`,
  `Separated`, `Widowed`, `Married-spouse-absent`, `Married-AF-spouse`
- `occupation`: `Tech-support`, `Craft-repair`, `Other-service`, `Sales`,
  `Exec-managerial`, `Prof-specialty`, `Handlers-cleaners`, `Machine-op-inspct`,
  `Adm-clerical`, `Farming-fishing`, `Transport-moving`, `Priv-house-serv`,
  `Protective-serv`, `Armed-Forces`

Resposta de sucesso:

```json
{
  "income_class_proxy": "<=50K",
  "probability_above_50k": 0.13588024571339077,
  "model_version": "adult-income-v1"
}
```

`income_class_proxy` é `>50K` quando `probability_above_50k >= 0.5`; caso
contrário é `<=50K`.

### PowerShell

Os arquivos em `examples/` evitam escapes frágeis no terminal. No segundo
terminal, entre no clone antes de executar as chamadas:

```powershell
cd AV1-Entrega-Pratica-MLOps
curl.exe -X POST http://127.0.0.1:3000/predict --header "Content-Type: application/json" --data-binary "@examples/case-1.json"
curl.exe -X POST http://127.0.0.1:3000/predict --header "Content-Type: application/json" --data-binary "@examples/case-2.json"
curl.exe -X POST http://127.0.0.1:3000/predict --header "Content-Type: application/json" --data-binary "@examples/case-3.json"
curl.exe -X POST http://127.0.0.1:3000/predict --header "Content-Type: application/json" --data-binary "@examples/invalid.json"
```

Os três primeiros retornam HTTP 200. `case-2.json` exercita categorias
desconhecidas; `case-3.json` exercita os dois campos anuláveis. O último retorna
HTTP 400 porque `age` é inválida.

### Linux/macOS

```bash
cd AV1-Entrega-Pratica-MLOps
curl -X POST http://127.0.0.1:3000/predict -H 'Content-Type: application/json' --data-binary @examples/case-1.json
curl -X POST http://127.0.0.1:3000/predict -H 'Content-Type: application/json' --data-binary @examples/case-2.json
curl -X POST http://127.0.0.1:3000/predict -H 'Content-Type: application/json' --data-binary @examples/case-3.json
curl -X POST http://127.0.0.1:3000/predict -H 'Content-Type: application/json' --data-binary @examples/invalid.json
```

## Qualidade, Docker e CI

### Checks locais

```powershell
uv run --frozen ruff check .
uv run --frozen pytest -q
```

A suíte inclui testes de contrato, modelo, dados, entradas inválidas, categorias
desconhecidas, artefato ausente e um E2E que sobe o BentoML duas vezes e confirma
health/predict após reinício.

### Atalhos opcionais com just

```powershell
just sync
just serve
just check
just demo
```

`just demo` sincroniza o ambiente e executa o E2E real. As receitas são atalhos
para os comandos acima; o README continua executável sem instalar `just`.

### Docker

Com o Docker Desktop em execução:

```powershell
docker build --tag careerpath-mlops:local .
docker run --rm --publish 3000:3000 careerpath-mlops:local
```

Em outro terminal, use `curl.exe http://127.0.0.1:3000/health`. A imagem usa
Python e uv fixados por digest, instala somente dependências de runtime pelo
`uv.lock`, leva o artefato local e executa o serviço como usuário sem privilégios.
O build e o health foram validados localmente, inclusive com startup sem rede.

### CI

O workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) executa em push
na `main` e em pull requests. Ele usa ações fixadas por SHA, `uv sync --frozen`,
Ruff e pytest em Linux. Não retreina nem baixa o dataset bruto.

## Modelo, dados e limitações

O modelo é uma regressão logística com pré-processamento completo em um único
pipeline scikit-learn. Ele foi treinado com o
[UCI Census Income / Adult, ID 20](https://archive.ics.uci.edu/dataset/20/census+income)
(DOI `10.24432/C5GP7S`, CC BY 4.0), usando seed 42.

Features usadas: `age`, `education`, `workclass`, `occupation`, `marital-status`
e `hours-per-week`. `race` e `sex` foram excluídas; `fnlwgt`, `relationship`,
`native-country`, `capital-gain`, `capital-loss` e `education-num` também foram
excluídas por não integrarem o formulário mínimo ou duplicarem informação.

No teste oficial, após remover 25 linhas exatamente sobrepostas ao treino, o
modelo obteve accuracy `0.8331797801`, ROC-AUC `0.8825975677` e Brier
`0.1142367999`. O baseline majoritário obteve accuracy `0.7637737240` e ROC-AUC
`0.5`. Métricas, hashes, versões, contagens e limitações completas ficam em
[`models/metadata.json`](models/metadata.json).

Limitações importantes:

- O Adult representa renda histórica dos EUA em 1994; não é resultado de carreira
  nem uma medida atual de renda.
- Excluir atributos sensíveis não elimina vieses ou proxies nas demais variáveis.
- Categorias nunca vistas são aceitas para manter a operação, não para prometer
  qualidade preditiva.
- O endpoint não deve acionar crédito, elegibilidade, contratação, demissão ou
  qualquer decisão automatizada sobre pessoas.
- O pickle é carregado apenas do artefato confiável versionado; hash e versão do
  scikit-learn são verificados antes da desserialização.

## Estrutura do repositório

```text
src/careerpath/     pacote de treino, schema, modelo e serviço BentoML
models/             pipeline versionado e metadata
examples/           três requests válidos e um inválido
tests/              testes unitários, HTTP e E2E
scripts/            download explícito do dataset para novo treino
docs/               checkpoints, fases e design
```

## Solução de problemas

| Situação | Ação |
| --- | --- |
| `uv sync --frozen` falha | Confirme Python 3.12 e não altere `pyproject.toml`/`uv.lock` separadamente. |
| Serviço não inicia | Confirme a presença de `models/adult-income-v1.pkl` e `models/metadata.json`; o startup falha de propósito se faltarem. |
| Porta 3000 ocupada | Pare o processo conflitante ou troque `--port 3000` e a URL dos curls. |
| Docker não conecta | Inicie o Docker Desktop e repita o build. |
| Sem rede na apresentação | Use o ambiente e a imagem já preparados; inferência não baixa dados nem treina. |

## Entrega

O código está sob [MIT](LICENSE). A licença do código não substitui os termos da
fonte de dados UCI.

O desenvolvimento utilizou Codex como apoio para análise de requisitos,
implementação, testes, revisão e documentação. As solicitações cobriram a leitura
da rubrica, construção das fases, validação do serviço e revisão das mudanças. A
equipe rejeitou a sugestão de versionar documentos internos de desenvolvimento por
serem redundantes para a entrega e validou independentemente os comandos, as
respostas HTTP e o container. A equipe continua responsável por explicar cada
linha e por apresentar as limitações do proxy.

Para o congelamento final, a equipe deve revisar o commit de entrega, gravar o
vídeo backup e criar manualmente a tag somente no prazo:

```powershell
git tag -a sr1 -m "Entrega do SR1"
git push origin sr1
```
