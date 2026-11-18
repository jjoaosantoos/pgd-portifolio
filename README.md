# PGD1 — Painel de Disponibilidade

Versão demonstrativa desktop em Python e PyQt6. Reutiliza o calendário anual recuperado do PGD1 com equipes e ausências fictícias. A seleção de área representa a entrada do usuário. Os registros de exemplo representam as férias e licenças importadas no sistema original.

## Executar no Windows

Instale o Python 3.10 ou superior. No PowerShell, na pasta do projeto, rode:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

O aplicativo funciona offline após a instalação. Os dados ficam em `%LOCALAPPDATA%\PGD1-Portfolio\dados.json`.

## Fluxo de demonstração

1. Selecione uma área. Use o ano, o líder, a UF ou o nome para navegar pelo calendário.
2. Escolha uma célula vazia e digite um código da legenda. Os períodos fictícios importados têm edição bloqueada.
3. Clique em **Salvar** para registrar uma versão local. **Consultar** recarrega a versão salva.
4. Use **Feriados** para cadastrar ou remover um feriado nacional ou por UF.
5. Use **Recursos externos** para cadastrar uma pessoa ou remover seu cadastro e lançamentos.
6. Clique em **Exportar CSV** para gerar o calendário do ano selecionado.
