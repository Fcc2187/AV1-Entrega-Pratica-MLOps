# Docker e persistência do JSONL

O container usa UID 10001 e grava em `/app/logs/inference.jsonl`. O Dockerfile
prepara `/app/logs` com o usuário da aplicação como proprietário. Monte um volume
nomeado nesse diretório e reutilize o mesmo nome ao recriar o container. O volume
tem ciclo de vida próprio e conserva os dados após a remoção do container.
[Documentação de volumes do Docker](https://docs.docker.com/engine/storage/volumes/).

## Build e execução

Na raiz do projeto, com o motor Docker Linux disponível, execute em PowerShell:

```powershell
docker build --tag careerpath-mlops:av2 .
if ($LASTEXITCODE -ne 0) { throw 'O build da imagem falhou' }
docker run --rm --name careerpath-av2 --publish 127.0.0.1:3000:3000 --mount "type=volume,source=careerpath-av2-logs,target=/app/logs" careerpath-mlops:av2
```

`just docker-build` e `just docker-run` executam o build e a inicialização com
essa imagem e esse volume. A receita de execução também aceita outro nome de
volume, por exemplo `just docker-run careerpath-av2-demo-logs`. Use um container
por volume para manter um único escritor do arquivo.

## Conferir permissão e persistência

Com o container pronto, abra outro terminal na raiz do projeto. Use um nome de
volume novo nos dois ciclos se quiser uma demonstração com um arquivo inicialmente
vazio.

```powershell
docker exec careerpath-av2 sh -c 'test "$(id -u)" -eq 10001 && test -w /app/logs'
if ($LASTEXITCODE -ne 0) { throw 'Confira o UID e a permissão de escrita no volume' }
curl.exe -fsS http://127.0.0.1:3000/health
curl.exe -fsS http://127.0.0.1:3000/metrics
curl.exe -fsS -X POST http://127.0.0.1:3000/predict -H 'Content-Type: application/json' --data-binary '@examples/case-1.json'
New-Item -ItemType Directory -Path logs -Force | Out-Null
docker cp careerpath-av2:/app/logs/inference.jsonl logs/docker-before.jsonl
if ($LASTEXITCODE -ne 0) { throw 'Falha ao copiar o log do primeiro ciclo' }
```

Encerre o primeiro container com Ctrl+C no terminal que executa `docker run`.
A opção `--rm` remove o container. Repita o comando de inicialização com o mesmo
volume e espere o novo serviço ficar pronto. Em seguida, confirme que o arquivo
reaberto tem o mesmo hash, envie outra previsão e verifique o acréscimo.

```powershell
curl.exe -fsS http://127.0.0.1:3000/health
curl.exe -fsS http://127.0.0.1:3000/metrics
docker cp careerpath-av2:/app/logs/inference.jsonl logs/docker-reopened.jsonl
if ($LASTEXITCODE -ne 0) { throw 'Falha ao copiar o log após recriar o container' }
if ((Get-FileHash logs/docker-before.jsonl).Hash -ne (Get-FileHash logs/docker-reopened.jsonl).Hash) {
    throw 'O conteúdo anterior foi alterado'
}
curl.exe -fsS -X POST http://127.0.0.1:3000/predict -H 'Content-Type: application/json' --data-binary '@examples/case-1.json'
docker cp careerpath-av2:/app/logs/inference.jsonl logs/docker-after.jsonl
if ($LASTEXITCODE -ne 0) { throw 'Falha ao copiar o log após a nova previsão' }
uv run --frozen python -c "import json; from pathlib import Path; before = Path('logs/docker-before.jsonl').read_bytes(); after = Path('logs/docker-after.jsonl').read_bytes(); assert after.startswith(before); added = after[len(before):].splitlines(); assert len(added) == 1 and json.loads(added[0])['status_code'] == 200"
```

No novo processo, consulte `/metrics` antes da primeira previsão para abrir
uma nova janela de contadores. O JSONL, por sua vez, continua no volume.
[Guia de métricas](metrics.md).

## Estado da validação em 11/11/2026

O E2E no Windows confirmou a persistência byte a byte após reiniciar o serviço.
O build da imagem e a recriação de containers com volume ficaram pendentes de
validação. O Docker Desktop aceitou o comando de inicialização, mas o motor
Linux devolveu HTTP 500 na consulta de versão e uma nova tentativa excedeu
15 segundos. O Windows informou que o WSL não está instalado.

A validação do container fica para outro ambiente com motor Docker Linux
disponível, conforme a orientação do usuário. Neste PC, use a suíte no host.
