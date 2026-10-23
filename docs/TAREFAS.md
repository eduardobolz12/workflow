# Tarefas do Decisor — para o ambiente ficar pronto

Ordem de execução. Cada bloco tem critério de pronto. Total: ~2h até a fatia 001 começar.

## A. Decisão (15 min)

- [ ] **A1. Escolher onde o código mora.**
  - **Recomendado:** mover o workspace do DSH para `C:\dev` (fora do OneDrive) e levar junto `docs/`,
    `projetos/` e `tools/`.
  - **Alternativa:** manter no OneDrive e pausar a sincronização durante builds.
  - *Pronto quando:* `setup-check` não marcar "repo dentro do OneDrive".

- [ ] **A2. Confirmar as ferramentas.** `git --version`, `python -V`, `node -v`, `pnpm -v`.
  - *Pronto quando:* os quatro respondem. (Já respondem nesta máquina.)

## B. Projeto (30 min)

- [ ] **B1. Criar o projeto a partir do template.**
  ```powershell
  Copy-Item <workspace>\projetos\_template C:\dev\meu-projeto -Recurse
  ```
- [ ] **B2. Escolher o stack e trocar a config.**
  ```powershell
  cd C:\dev\meu-projeto
  Copy-Item dsh.node.json dsh.json      # ou dsh.python.json
  ```
- [ ] **B3. Apagar o piso de fábrica.**
  ```powershell
  Remove-Item ferramentas\piso.py, ferramentas\piso_estado.json -Force
  Remove-Item docs\SPECS\900.md, tests\acceptance\900 -Recurse -Force
  ```
- [ ] **B4. Criar `.git`, primeiro commit.**
  ```powershell
  git init -b main; git add -A; git commit -m "base"
  ```
  - *Pronto quando:* `git log --oneline` mostra um commit e `git status` está limpo.

## C. Stack (30–60 min — a parte que só você sabe)

- [ ] **C1. Comando de teste com relatório.** Rodar uma vez e conferir o arquivo:
  ```powershell
  pnpm vitest run tests/acceptance/900 --reporter=json --outputFile=.dsh/report-900.json
  # ou: python -m pytest tests/acceptance/900 -q --junitxml=.dsh/report-900.xml
  Test-Path .dsh\report-900.*
  ```
- [ ] **C2. Comando de start.** `pnpm start` (ou equivalente), anotando a **porta** e a **URL**.
- [ ] **C3. Preencher `dsh.json`:** `acceptance_cmd`, `report_path`, `report_format`, `start_cmd`,
      `base_url`, `regression_cmd`, `allowed_paths`.
- [ ] **C4. Criar `tests/acceptance/900/` de volta** só se quiser repetir a prova; senão pule para D.
  - *Pronto quando:* os comandos de C1 e C2 funcionam digitados por você, no terminal.

## D. Validação (15 min)

- [ ] **D1. `setup-check`.**
  ```powershell
  powershell -File tools\setup-check.ps1 -Repo . -Workspace C:\dev -RunTests
  ```
- [ ] **D2. Corrigir o que ele apontar** (é sempre um dos seis: local, OneDrive, git, `.gitignore`,
      `dsh.json`, relatório).
- [ ] **D3. Commit da config.**
  - *Pronto quando:* `=== ambiente pronto ===`.

## E. Primeira fatia (meio dia)

- [ ] **E1. Pedir ao Claude** a fatia 001: walking skeleton, 2 CAs, rota normal. Ele escreve
      `docs/SPECS/001.md` e `tests/acceptance/001/`.
- [ ] **E2. Aprovar a tabela de CAs** (10 min): valores concretos, resultado verificável, fora de
      escopo correto.
- [ ] **E3. Rodar o gate.** `python tools\dsh.py gate 001`
      — ler a tela, responder `s`. Se reprovar, volta ao Claude.
- [ ] **E4. Mandar para o Kimi** os três documentos: `briefing-kimi-v4.md`, `relatorio-tecnico-kimi.md`,
      `relatorio-dsh-para-kimi.md`.
- [ ] **E5. Fechar a fatia:** `verify` verde → seu teste manual (3 passos da spec) → merge.

## F. Rotina (a partir da 002)

- [ ] **F1.** Uma linha no `metricas.csv` por fatia (eu escrevo).
- [ ] **F2.** Registrar atrito em `docs/QA/NNN.md`: `atrito: <o que travou> <tempo>`.
- [ ] **F3.** Não mexer no processo antes de 10 fatias.
- [ ] **F4.** Na 10ª, revisar com os números: defeitos escapados, voltas, tempo, burla.

## Opcional — rota completa

- [ ] **O1. Instalar Kimi CLI:** `irm https://code.kimi.com/kimi-code/install.ps1 | iex`
- [ ] **O2. Instalar CodeRabbit CLI:** `irm https://cli.coderabbit.ai/install.ps1 | iex`
      e autenticar com `cr auth login`.
- *Sem isso, a rota normal funciona; só a completa fica sem CR e sem eu despachar o Kimi.*

## O que NÃO fazer

- [ ] ~~Instalar o `dsh` global, criar venv, montar CI~~ — o harness é stdlib e vive no repo.
- [ ] ~~Editar `tests/acceptance/` para "ajustar"~~ — conteste.
- [ ] ~~Adicionar holdout, hash encadeado, isolamento~~ — só com defeito escapado que os justifique.
