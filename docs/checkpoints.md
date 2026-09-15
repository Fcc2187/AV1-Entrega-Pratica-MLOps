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
