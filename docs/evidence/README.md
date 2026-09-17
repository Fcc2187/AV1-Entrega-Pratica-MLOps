# Evidências da Fase 7

Coleta realizada em 17/09/2026, no Windows x64, sobre o commit-base
`2382094008160e80be0f2e1b704e897789b0a65f`.

O worktree estava limpo antes da criação destas evidências:

```text
## main...origin/main
```

Os arquivos desta pasta preservam os comandos, códigos de saída e resultados
observados na preparação da apresentação:

- `2026-09-17-environment-and-installation.md`: ambiente e instalação frozen;
- `2026-09-17-http.md`: startup, health, três predições e entrada inválida;
- `2026-09-17-quality-and-docker.md`: pytest, Ruff e diagnóstico do Docker.

Os JSONs usados são perfis sintéticos versionados em `examples/`. Nenhum dado
real de prospect foi registrado.

## Interpretação

As respostas HTTP e os resultados de qualidade são desta execução. As métricas
do modelo não foram recalculadas na Fase 7; continuam sendo as métricas reais do
treinamento registradas em `models/metadata.json`.

O Docker não foi reconstruído nem executado nesta coleta porque o daemon local
estava indisponível. Os checkpoints das Fases 5 e 6 preservam a validação anterior,
mas ela não é apresentada como uma nova execução da Fase 7.
