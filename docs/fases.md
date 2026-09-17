# Fases do projeto

Este documento explica como a entrega será construída e revisada. O trabalho é
dividido por responsabilidade, com checkpoints e trocas manuais de modelo. Cada
checkpoint registra o que mudou, comandos executados, resultados, pendências,
riscos e a próxima fase.

## Regras dos gates

Ao chegar a um Model Gate, o trabalho para por completo. A pessoa responsável
troca manualmente o modelo indicado e responde `CONTINUAR`. Na retomada, o agente
confere o Git, relê o checkpoint e confirma a próxima fase antes de trabalhar.

Nenhum gate cria ou envia a tag `sr1`. Essa tag só será criada pela equipe no
commit final da entrega, em 24/09 às 10:30, conforme o enunciado.

## Visão geral

| Fase | Modelo | Finalidade | Saída principal |
| --- | --- | --- | --- |
| 0 | GPT-6 Astra, HIGH/MAX | Entender negócio, rubrica, dados e arquitetura. | Design aprovado e matriz da rubrica. |
| 1 | GPT-5.6 SOL, HIGH | Criar a fundação instalável do repositório. | Estrutura, Python 3.12, pyproject e lock. |
| 2 | GPT-5.6 SOL, HIGH | Treinar e persistir a inferência. | Pipeline local, métricas reais e metadata. |
| 3 | GPT-5.6 SOL, HIGH | Expor a inferência por HTTP. | Serviço BentoML com predict e health. |
| 4 | GPT-5.6 SOL, HIGH | Validar contrato e operação. | Testes, lint e E2E após reinício. |
| 5 | GPT-5.6 SOL, MEDIUM/HIGH | Adicionar diferenciais seguros. | Docker, comando único e CI. |
| 6 | GPT-5.6 Terra, MEDIUM/HIGH | Tornar o projeto reproduzível por terceiros. | README completo e executável. |
| 7 | GPT-5.6 Terra, MEDIUM/HIGH | Preparar evidências e apresentação. | Evidências, roteiro de 15 min e vídeo backup. |
| 8 | GPT-6 Astra, MAX | Auditar a entrega contra a rubrica. | Relatório read-only com P0/P1/P2. |
| 9 | GPT-5.6 SOL, HIGH | Corrigir problemas importantes da auditoria. | Correções limitadas aos P0/P1 encontrados. |
| 10 | GPT-6 Astra, MAX | Fazer a verificação final. | Status READY/NOT READY e instruções finais. |

## Fase 0 — descoberta, triagem e design

Lê o Project Charter, o enunciado e todo o repositório. Separa requisitos
obrigatórios, diferenciais e itens fora do MVP. Define o papel honesto do Adult:
prever a classe histórica `>50K`/`<=50K` como sinal socioeconômico auxiliar, sem
afirmar intenção de compra, necessidade profissional ou renda comprovada.

Também fixa o contrato proposto, features, exclusões, estratégia de treinamento,
persistência, operação offline, testes, evidências e riscos. O resultado está em
`docs/phase-0-design.md`.

### Model Gate 1

Após a Fase 0, trocar para GPT-5.6 SOL com esforço HIGH e responder `CONTINUAR`.

## Fase 1 — fundação do repositório

Cria a menor estrutura capaz de sustentar o serviço: pacote em `src/`, diretórios
de modelos, scripts, exemplos, testes e documentação; `pyproject.toml`,
`uv.lock`, `.python-version`, `.gitignore`, `.env.example` e `LICENSE`.

O ambiente usa Python 3.12 e dependências compatíveis e fixadas. A instalação é
validada com uv em estado frozen. Esta fase não baixa dados nem treina o modelo.

## Fase 2 — modelo e pipeline de inferência

Procura novamente um notebook ou artefato anterior. Na ausência dele, treina um
baseline explicável com scikit-learn: preprocessamento numérico e categórico,
`OneHotEncoder(handle_unknown="ignore")` e regressão logística.

O treino trata `?`, mantém partições independentes, usa seed, compara com a classe
majoritária e registra métricas observadas. O pipeline completo é salvo localmente
com `metadata.json`. Um processo novo deve conseguir carregar e usar o artefato.

## Fase 3 — serviço BentoML

Carrega o artefato local ao iniciar e expõe `POST /predict` e `GET /health`.
O predict recebe um perfil, valida o JSON e devolve a classe histórica, a
probabilidade de `>50K` e a versão do modelo. O health só informa prontidão quando
o artefato está carregado.

São mantidos três exemplos válidos e um inválido. As chamadas são feitas de
verdade e seus resultados são registrados depois, sem números ilustrativos.

## Fase 4 — testes e robustez

Valida carregamento do modelo, inferência, contrato, health, erros de entrada e
categorias desconhecidas. Executa pytest e ruff até ambos passarem.

O E2E encerra somente o processo iniciado pelo teste, sobe o serviço a partir do
comando documentável, chama health e predict e confirma a resposta após reinício.

## Fase 5 — diferenciais técnicos

Só começa com as fases 1–4 funcionando. Implementa, nessa ordem, Dockerfile,
justfile e GitHub Actions com instalação frozen, ruff e pytest. Docker só será
declarado validado se build e run forem realmente executados.

### Model Gate 2

Após a implementação técnica, trocar para GPT-5.6 Terra com esforço MEDIUM ou
HIGH e responder `CONTINUAR`.

## Fase 6 — README reproduzível

Escreve o caminho completo entre `git clone` e a primeira predição. Inclui Python,
pré-requisitos, uv, instalação, inicialização, endereço local, contrato, exemplos,
curl.exe para PowerShell, curl para Linux/macOS, testes, lint, origem do modelo,
limitações, solução de problemas, tempo medido, licença, uso de IA, apresentação
e o procedimento manual da tag `sr1`.

Os comandos vêm do projeto real e são executados antes de serem publicados. O
README funciona sem depender do justfile.

## Fase 7 — evidências e apresentação

Registra em `docs/evidence/` saídas reais de ambiente, instalação, startup,
health, três predições, erro, pytest, ruff e Docker quando testado.

Cria `docs/presentation-outline.md` com os quatro blocos obrigatórios na ordem da
rubrica: objetivo, processo de negócio, como subir e demonstração. O total é 15
minutos, seguido por 5 minutos de perguntas. Cria também um roteiro de cerca de
dois minutos para o vídeo backup e reexecuta os comandos citados no README.

### Model Gate 3

Após README, evidências e roteiros, trocar para GPT-6 Astra com esforço MAX e
responder `CONTINUAR`.

## Fase 8 — auditoria final independente

Começa sem alterar arquivos. Compara PDF, enunciado, README, código, lock,
container, CI, exemplos, testes e evidências com cada item da rubrica. Simula o
caminho de outra equipe: clone, setup, serve e curl.

Classifica achados como P0, que impede entrega ou demonstração; P1, que pode perder
ponto obrigatório; ou P2, acabamento. Também procura segredos, dados pessoais,
métricas inventadas, dependência de internet e afirmações indevidas sobre o Adult.

Se não houver P0/P1, segue para a Fase 10. Se houver, para no Model Gate 4.

### Model Gate 4 — condicional

Com P0/P1, trocar para GPT-5.6 SOL com esforço HIGH e responder `CONTINUAR`.

## Fase 9 — correções da auditoria

Existe somente quando a Fase 8 encontra P0/P1. Corrige apenas esses itens, atualiza
a documentação afetada e executa teste, lint e E2E quando aplicável.

### Model Gate 5 — condicional

Após resolver P0/P1, trocar para GPT-6 Astra com esforço MAX e responder
`CONTINUAR`.

## Fase 10 — verificação final

Confere instalação frozen, serviço, artefato local, operação sem internet,
endpoints, exemplos, README, configuração, licença, uso de IA, testes, evidências,
Docker/CI, apresentação, vídeo e ausência de credenciais, dados pessoais e métricas
inventadas. Executa pytest, ruff e o caminho principal da demonstração uma última
vez.

Entrega um relatório `READY` ou `NOT READY`, os comandos para subir e demonstrar,
resultados reais, checklist da rubrica e pendências. A equipe então revisa o commit,
grava o vídeo, confirma o cache e cria/envia `sr1` no prazo.

## Estado atual

- Fase 0: concluída e publicada em `origin/main` no commit `bcb58a5`.
- Model Gate 1: atendido pelo usuário com SOL/HIGH e `CONTINUAR`.
- Fase 1: concluída e sincronizada com `origin/main`.
- Fase 2: concluída; pipeline, metadata e métricas reais estão versionados.
- Resultado do modelo no teste oficial: accuracy `0.8331797801` e ROC-AUC
  `0.8825975677`; 8 testes automatizados passaram.
- Fase 3: concluída; `POST /predict`, `GET /health` e quatro exemplos executáveis.
- Fase 4: concluída; threshold, startup sem artefato e E2E com reinício real cobertos.
- Fase 5: concluída; Docker validado localmente, justfile e CI criados.
- Verificação atual: 41 testes passaram, Ruff não encontrou problemas e o health
  respondeu a partir do container.
- Model Gate 2: atendido pelo usuário com `CONTINUAR`.
- Fase 6: concluída; README reproduzível, contrato escrito e caminhos local e
  Docker validados com comandos reais.
- Fase 7: concluída; evidências locais, roteiro de apresentação de 15 minutos e
  roteiro de vídeo backup foram registrados. Nesta execução, 41 testes passaram,
  Ruff ficou limpo e o daemon Docker estava indisponível para nova validação.
- Próxima etapa: Model Gate 3 — trocar para GPT-6 Astra com esforço MAX e responder
  `CONTINUAR` antes da auditoria read-only da Fase 8.
