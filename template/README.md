# Template

Copie esta pasta, renomeie e troque o que for do seu stack:

1. Escolha o `dsh.json`: copie `dsh.node.json` ou `dsh.python.json` por cima.
2. Apague `ferramentas/piso.py`, `ferramentas/piso_estado.json`, `docs/SPECS/900.md` e `tests/acceptance/900/`
   quando o runner real estiver no lugar.
3. Rode `powershell -File tools/setup-check.ps1 -Repo . -Workspace <pai> -RunTests`.

Ordem do workflow em `docs/WORKFLOW.md` (ou no manual de 8 passos).

