# Verificação final da Fase 10

Coleta realizada em 18/09/2026, no Windows x64, sobre o commit público
`ee6cebf363b8d785d073c3456edecba701368a25`.

Esta fase foi executada com GPT-5.6 Sol em esforço HIGH, substituição autorizada
pelo usuário devido ao limite de uso do GPT-6 Astra. A troca de modelo não alterou
o checklist nem os critérios de conclusão.

## Clone e instalação

O repositório foi clonado do GitHub sem credenciais para um diretório temporário.
O clone resolveu o mesmo commit da `main` pública.

```powershell
uv sync --frozen --python 3.12
```

Resultado observado:

- uv `0.12.5`;
- Python `3.12.10`;
- 81 pacotes instalados;
- projeto local construído com sucesso;
- `uv lock --check --offline`: código 0, 83 pacotes resolvidos a partir do lock.

## Qualidade e reinício offline

```powershell
uv run --frozen ruff check .
uv run --frozen pytest -q
$env:UV_OFFLINE = '1'
uv run --offline --no-sync pytest -q tests/test_e2e.py
```

Resultados observados:

```text
All checks passed!
41 passed in 60.93s
1 passed in 15.87s
```

O E2E offline iniciou o serviço em processo novo, consultou health e predict,
encerrou o processo e repetiu o ciclo, sem sincronizar ou baixar dependências.

## Demonstração HTTP

O serviço foi iniciado em loopback a partir do clone limpo. As chamadas foram
feitas com os JSONs sintéticos versionados em `examples/`.

| Chamada | HTTP | Resultado observado |
| --- | ---: | --- |
| `GET /health` | 200 | `status=ok`, `model_version=adult-income-v1` |
| `case-1.json` | 200 | `<=50K`, probabilidade `0.13588024571339077` |
| `case-2.json` | 200 | `>50K`, probabilidade `0.5256289902834581` |
| `case-3.json` | 200 | `<=50K`, probabilidade `0.01841773201019456` |
| `invalid.json` | 400 | rejeição de `age` menor que 17 |

O processo temporário foi encerrado ao final da coleta.

## Artefato e métricas

- `models/adult-income-v1.pkl` corresponde ao SHA-256 registrado em
  `models/metadata.json`;
- scikit-learn instalado: `1.9.1`, igual à versão dos metadados;
- versão carregada: `adult-income-v1`;
- accuracy: `0.8331797801117867`;
- ROC-AUC: `0.8825975676743194`;
- baseline majoritário: accuracy `0.7637737239727289` e ROC-AUC `0.5`.

As métricas foram lidas do artefato versionado e não recalculadas nem inventadas
nesta fase.

## Repositório e CI

- consulta anônima ao GitHub: repositório público, branch padrão `main`;
- HEAD público: `ee6cebf363b8d785d073c3456edecba701368a25`;
- workflow `Quality` desse commit: `completed/success`;
- 27 arquivos/artefatos obrigatórios verificados, nenhum ausente;
- `.env.example` contém apenas o nome da variável, sem valor;
- busca por formatos de tokens, chaves de API e chaves privadas: nenhuma ocorrência;
- nenhum e-mail, CPF, telefone ou registro real de prospect foi encontrado;
- README contém clone, instalação, startup, contrato, curls, tempos, métricas,
  limitações, licença e declaração de uso de IA.

## Docker

O cliente Docker `29.4.3` está instalado, mas o daemon `desktop-linux` permaneceu
indisponível. Por isso, build e run não foram repetidos nesta fase. As Fases 5 e 6
preservam a validação anterior do container; a Fase 7 já documenta a indisponibilidade
atual sem afirmar uma execução nova.

A auditoria da Fase 8 também registrou como P2 a publicação
`--publish 3000:3000`, que pode alcançar interfaces externas conforme a rede do host.
O caminho principal da apresentação usa `127.0.0.1` e não depende do Docker.

## Resultado

Status: **READY técnico**.

O repositório atende ao caminho obrigatório de clone, instalação, serviço local,
predição, erro validado, testes, documentação e CI. Antes da entrega, a equipe ainda
deve executar as ações humanas previstas: revisar o commit final, distribuir e
ensaiar as falas, gravar o vídeo backup, confirmar o cache local, submeter o link e
criar/enviar a tag `sr1` somente no prazo.
