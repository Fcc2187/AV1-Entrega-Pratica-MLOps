# Roteiro do vídeo backup — aproximadamente 2 minutos

O vídeo deve ser gravado pela equipe depois de preencher o nome de quem narra.
Usar perfis sintéticos de `examples/`; não exibir dados pessoais, tokens ou `.env`.

## 0:00–0:20 — contexto

Tela: título e início do README.

Fala sugerida:

> Esta é a PoC CareerPath. Ela expõe por BentoML um modelo treinado com o Adult
> para estimar a classe histórica de renda acima de 50 mil dólares. O resultado é
> apenas um sinal socioeconômico auxiliar: não mede renda atual, intenção de compra
> ou potencial de carreira e não toma decisões automáticas sobre pessoas.

## 0:20–0:45 — inicialização

Tela: terminal no diretório do projeto.

Mostrar brevemente os comandos, deixando o ambiente preparado antes da gravação:

```powershell
uv sync --frozen --python 3.12
uv run --frozen bentoml serve careerpath.service:CareerPathService --host 127.0.0.1 --port 3000 --do-not-track
```

Fala sugerida:

> O ambiente usa Python 3.12 e dependências congeladas no uv.lock. O artefato e a
> metadata já estão no repositório; o startup não baixa dados nem treina o modelo.

## 0:45–1:10 — health e predição

Tela: segundo terminal.

```powershell
curl.exe http://127.0.0.1:3000/health
curl.exe -X POST http://127.0.0.1:3000/predict --header "Content-Type: application/json" --data-binary "@examples/case-1.json"
```

Fala sugerida:

> O health confirma que a versão adult-income-v1 está carregada. A predição
> retorna a classe proxy, a probabilidade da classe histórica maior que 50 mil e
> a versão exata do modelo.

## 1:10–1:32 — validação

```powershell
curl.exe -X POST http://127.0.0.1:3000/predict --header "Content-Type: application/json" --data-binary "@examples/invalid.json"
```

Fala sugerida:

> O contrato é estrito. Este exemplo usa idade inválida e recebe HTTP 400 com o
> detalhe da regra, em vez de produzir uma inferência silenciosamente incorreta.

## 1:32–1:52 — qualidade

Tela: evidências ou terminal com resultados já executados.

```text
41 passed in 18.97s
All checks passed!
```

Fala sugerida:

> A suíte cobre contrato, artefato, categorias desconhecidas, falha de startup e
> um E2E que reinicia o serviço. Nesta coleta, 41 testes passaram e o Ruff não
> encontrou problemas.

## 1:52–2:00 — encerramento

Fala sugerida:

> A PoC é reproduzível e funciona localmente, sempre mantendo decisão humana e as
> limitações do proxy de 1994 explícitas.

## Antes de gravar

- Preencher o narrador: `[definir integrante]`.
- Ensaiar para ficar próximo de dois minutos sem acelerar a explicação.
- Confirmar serviço, porta 3000 e exemplos antes de iniciar a captura.
- Manter o vídeo salvo localmente para uso sem internet.
- Como o daemon Docker está indisponível nesta máquina, gravar o caminho local.
