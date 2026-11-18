# PGD — Painel Gestão de Dados

Demonstração desktop baseada no PGD de abril de 2026, feita em Python e PyQt6. O painel abre diretamente com 15 colaboradores fictícios e exemplos de férias e licenças. Os lançamentos e feriados são armazenados em JSON por área. A exportação aparece desativada.

## Executar no Windows

No PowerShell, com Python 3.10 ou superior:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Após a instalação, o aplicativo funciona offline. O arquivo da demonstração fica em `%LOCALAPPDATA%/PGD1-Fiel/ferias_DEMO.json`.
