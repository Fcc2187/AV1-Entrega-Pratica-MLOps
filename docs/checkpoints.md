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
