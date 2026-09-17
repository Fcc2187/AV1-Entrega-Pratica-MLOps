# Qualidade e Docker — 17/09/2026

## Ruff

Comando equivalente ao `uv run --frozen ruff check .`, usando o ambiente criado
pelo sync frozen:

```powershell
.\.venv\Scripts\ruff.exe check .
```

Código de saída: `0`.

```text
All checks passed!
```

## Pytest

O E2E exige `uv` e, no Windows, `taskkill` no PATH. O comando final manteve o
`uv` temporário e `C:\Windows\System32` disponíveis somente para o processo de
teste. `BENTOML_HOME` foi redirecionado para o diretório local ignorado pelo Git
por causa da restrição do sandbox.

```powershell
$env:Path = 'C:\Users\MIGUEL\AppData\Local\Temp\careerpath-phase7-uv\bin;C:\Windows\System32;' + $env:Path
$env:BENTOML_HOME = Join-Path (Get-Location) '.bentoml'
.\.venv\Scripts\pytest.exe -q
```

Código de saída: `0`.

```text
.........................................                                [100%]
41 passed in 18.97s
```

O teste E2E subiu o serviço duas vezes, chamou health e predict e encerrou apenas
os processos que criou.

## Docker

O cliente foi identificado:

```text
Docker version 29.4.3, build 055a478
Context: desktop-linux
```

Foi feita somente uma consulta de diagnóstico, sem build e sem container:

```powershell
docker info
```

Código de saída: `1`.

Mensagem observada:

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine;
check if the path is correct and if the daemon is running:
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

Conclusão: o Dockerfile e os comandos permanecem configurados, mas Docker não foi
revalidado na Fase 7 porque o daemon local estava indisponível. As validações reais
anteriores continuam registradas nos checkpoints das Fases 5 e 6.
