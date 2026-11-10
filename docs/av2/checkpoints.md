# AV2 — checkpoints

Este histórico é da AV2. `docs/checkpoints.md` continua sendo o registro da AV1.
Os resultados antigos não substituem verificações atuais.

## Fase 0 — planejamento

Data: 10/11/2026.
Estado: planejamento elaborado; implementação não iniciada.

### Contexto confirmado

- Branch atual: `av2`.
- Commit de origem observado: `d2982c2` (`build: add phase 5 delivery automation`).
- Árvore de trabalho limpa antes da criação dos documentos da AV2.
- O enunciado permite continuar o serviço da AV1 e a modalidade aplicável é a 1.
- Código, modelo, exemplos e testes da AV1 permanecem necessários para a continuação.
- Documentação da AV1 é histórico/contexto e será preservada.

### Arquivos criados

- `docs/av2/escopo.md`: requisitos, decisões propostas, dados, métricas e preservação.
- `docs/av2/fases.md`: tarefas, interfaces, arquivos, verificações e critérios de aceite.
- `docs/av2/checkpoints.md`: este registro e formato das próximas atualizações.

### Verificações desta etapa

- Lidos enunciado, código de serviço e schema, configurações, testes relevantes,
  download de dados, CI, fases e checkpoints da AV1.
- Conferidos Git, branch e disponibilidade de comandos; `uv` não foi localizado
  no PATH desta sessão. Não houve instalação de dependências.
- Consultadas referências oficiais de logging Python/BentoML e métricas.
- Não foram executados servidor, carga, testes de aplicação ou Docker nesta etapa.
- Revisados requisitos e tarefas: logging, dados de entrada/saída, erros antes da
  inferência, métricas, cálculos, retenção e demonstração têm fases correspondentes.
- `git diff --check`: sem erros nos arquivos rastreados; os documentos novos ainda
  estão não rastreados e receberam verificação textual separada.
- Links locais entre os três documentos conferidos com `Test-Path`: todos existem.
- `git status --short`: somente `?? docs/av2/`; nenhum arquivo da AV1 foi alterado.

### Decisões propostas

- Manter BentoML, Adult, modelo e contratos existentes.
- Captura na camada HTTP para incluir erros anteriores à função de inferência.
- JSONL append-only, caminho configurável e dados individuais para análise futura.
- Aproveitar `/metrics` nativo; confirmar versão, nomes e comportamento em runtime.
- Separar planejamento AV2 em `docs/av2/`, sem reescrever o histórico da AV1.
- Não transportar os gates de modelos e prazos antigos para a nova entrega.

### Pendências e riscos

- Validar ambiente/uv e baseline atual na fase 1.
- Confirmar integração pública do middleware e um único escritor no BentoML 1.4.39.
- Confirmar `/metrics` e persistência do arquivo com execução real.
- Preparar diretório/volume gravável no Docker e CI para a branch `av2`.
- README precisa ser desenvolvido; contém somente o título na versão examinada.
- Prazo, eventual tag e outras partes da rubrica AV2 não foram fornecidos.

### Próxima ação

Após solicitação de implementação, iniciar a fase 1 de `fases.md`. A existência
deste planejamento não autoriza declarar requisitos implementados ou testes passando.

## Modelo para os próximos checkpoints

```markdown
## Fase N — título

Data:
Estado: em andamento / concluída / impedimento técnico

### O que foi feito
-

### Arquivos alterados
-

### Decisões e justificativas
-

### Comandos e resultados observados
- Comando:
- Resultado real:

### Pendências e riscos
-

### Próxima ação
-
```
