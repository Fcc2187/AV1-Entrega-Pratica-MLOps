# Ambiente e instalação — 17/09/2026

## Contexto

```text
Data/hora inicial: 2026-09-17T14:56:24-03:00
Sistema: Microsoft Windows 10.0.26200
Arquitetura: X64
Python: 3.12.10
uv: 0.12.5 (210d1f678 2026-08-14 x86_64-pc-windows-msvc)
Commit-base: 2382094008160e80be0f2e1b704e897789b0a65f
Branch: main, acompanhando origin/main
Worktree antes da coleta: limpo
```

O `uv` não estava instalado globalmente nesta máquina. Para executar a versão
exata do README sem alterar ferramentas globais, `uv==0.12.5` foi instalado em
um diretório temporário e chamado pelo caminho absoluto. Isso não modifica as
dependências declaradas nem o lock do projeto.

## Instalação frozen

Comando equivalente ao `uv sync --frozen --python 3.12` do README, usando o
executável temporário:

```powershell
& 'C:\Users\MIGUEL\AppData\Local\Temp\careerpath-phase7-uv\bin\uv.exe' sync --frozen --python 3.12
```

Código de saída: `0`.

Saída observada:

```text
Using CPython 3.12.10 interpreter at: C:\Users\MIGUEL\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\python.exe
Creating virtual environment at: .venv
Building careerpath-mlops @ file:///D:/Usu%C3%A1rios/MIGUEL/%C3%81rea%20de%20Trabalho/AV1-Entrega-Pratica-MLOps
Prepared 81 packages in 11.86s
warning: Failed to hardlink files; falling back to full copy.
```

O fallback de hardlink para cópia afeta apenas velocidade e espaço. A instalação
concluiu e o ambiente criado foi usado nas verificações seguintes.
