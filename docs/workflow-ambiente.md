# Workflow — ambiente em qualquer computador

**Para:** o Decisor, numa máquina nova — ou o DSH lendo isto pela primeira vez.
**Promessa:** em 20 minutos, o repositório está clonado, a ferramenta validada e o projeto com
`gate`/`verify` funcionando. Sem depender de memória de conversa.

---

## 0. O que este arquivo não faz

Não instala nada por você, não autentica e não faz `push`. O shell do DSH não tem HTTPS: instalação,
login e publicação são atos seus. O resto, ele executa.

---

## 1. Clonar

```powershell
git clone https://github.com/eduardobolz12/workflow.git C:\dev\workflow
cd C:\dev\workflow
```

Confira: `git log --oneline -1` deve mostrar o último commit, e `docs/` deve conter
`guia_completo_workflow.md` e este arquivo.

---

## 2. Pré-requisitos

### Obrigatórios em qualquer projeto

| Ferramenta | Versão | Para quê | Instalar (Windows) |
|---|---|---|---|
| Git | 2.30+ | branches, worktree, manifesto | `winget install --id Git.Git -e` |
| Python | 3.12+ | roda o `tools/dsh.py` | `winget install --id Python.Python.3.12 -e` |

> Linux: `sudo apt install git python3` · macOS: `brew install git python@3.12`

### Por stack

| Stack | Ferramenta | Instalar | Conferir |
|---|---|---|---|
| **C#/.NET** | .NET SDK 8 ou 10 | `winget install --id Microsoft.DotNet.SDK.8 -e` | `dotnet --list-sdks` |
| **Python** | pytest | `python -m venv .venv; .\.venv\Scripts\python.exe -m pip install pytest` | `pytest --version` |
| **Node** | Node LTS + pnpm | `winget install --id OpenJS.NodeJS.LTS -e`; `npm i -g pnpm` | `node -v; pnpm -v` |

---

## 3. Validar a ferramenta antes de qualquer projeto

```powershell
python tools/test_dsh.py
```

Esperado: `Ran 12 tests ... OK`. Se falhar aqui, não adianta seguir: o problema é a máquina, não o
projeto.

---

## 4. Criar o projeto

```powershell
Copy-Item C:\dev\workflow\template C:\dev\meu-projeto -Recurse
cd C:\dev\meu-projeto
Remove-Item .git -Recurse -Force
git init -b main
```

Escolha a config do stack e apague o piso de fábrica:

```powershell
Copy-Item dsh.node.json dsh.json      # Node
# ou
Copy-Item dsh.python.json dsh.json    # Python
# ou
Copy-Item dsh.dotnet.json dsh.json    # C#/.NET
```

```powershell
Remove-Item ferramentas, docs\SPECS\900.md, tests\acceptance\900 -Recurse -Force
```

---

## 5. Configuração por stack

### C#/.NET — o exemplo completo

**Estrutura que funciona com o verificador:**

```
src/App/App.csproj              → a aplicação (minimal API ou web)
tests/acceptance/Acceptance.csproj → UM projeto de teste para todas as fatias
tests/acceptance/001/            → os testes da fatia 001
docs/SPECS/001.md
```

**Criar (só na primeira vez; precisa de internet para o NuGet):**

```powershell
dotnet new web -n App -o src/App
dotnet new xunit -n Acceptance -o tests/acceptance
dotnet new sln -n MeuProjeto
dotnet sln add src/App/App.csproj tests/acceptance/Acceptance.csproj
```

**`dsh.json` para .NET:**

```json
{
  "repo": ".",
  "base_branch": "main",
  "spec": "docs/SPECS/{nnn}.md",
  "acceptance_dir": "tests/acceptance/{nnn}",
  "acceptance_cmd": ["dotnet", "test", "tests/acceptance",
                     "--filter", "FullyQualifiedName~Acceptance{nnn}",
                     "--logger", "trx;LogFileName=report-{nnn}.trx",
                     "--results-directory", ".dsh"],
  "report_path": ".dsh/report-{nnn}.trx",
  "report_format": "trx",
  "runner_configs": ["global.json", "Directory.Build.props", "src/App/App.csproj"],
  "regression_cmd": ["dotnet", "test", "--nologo"],
  "start_cmd": ["dotnet", "run", "--project", "src/App", "--urls", "http://127.0.0.1:5080"],
  "base_url": "http://127.0.0.1:5080/health",
  "allowed_paths": ["src/", "docs/QA/"]
}
```

**Convenções obrigatórias:**

- a classe de teste da fatia **precisa conter o número**: `public class Acceptance001`.
  É isso que o `--filter` usa e o que a rastreabilidade do gate lê (`CA-1` → `CA1_...`);
- métodos nomeados com o CA: `public void CA1_exporta_somente_pagos()`;
- os testes falam com a **fronteira HTTP** (`HttpClient`), nunca com classe interna;
- `dotnet test` compila tudo a cada execução: mantenha o projeto pequeno.

**Casca do app (antes da fatia 001)** — `src/App/Program.cs`:

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/health", () => Results.Ok(new { status = "ok" }));

app.Run();
```

Qualquer rota não mapeada devolve **404** — é o que faz o teste da 001 falhar pelo motivo certo
("esperava 200, recebeu 404") em vez de "conexão recusada".

### Python — pytest

```json
{
  "acceptance_cmd": [".venv/Scripts/python.exe", "-m", "pytest", "tests/acceptance/{nnn}",
                     "-q", "--junitxml={report}"],
  "report_path": ".dsh/report-{nnn}.xml",
  "report_format": "junit",
  "regression_cmd": [".venv/Scripts/python.exe", "-m", "pytest", "-q"],
  "start_cmd": [".venv/Scripts/python.exe", "-m", "uvicorn", "app.main:app", "--port", "8000"],
  "base_url": "http://127.0.0.1:8000/health",
  "allowed_paths": ["app/", "src/", "docs/QA/"]
}
```

Convenção: `def test_CA1_...()`. A pasta da fatia é `tests/acceptance/001/`.

### Node — vitest

```json
{
  "acceptance_cmd": ["pnpm", "vitest", "run", "tests/acceptance/{nnn}",
                     "--reporter=json", "--outputFile={report}"],
  "report_path": ".dsh/report-{nnn}.json",
  "report_format": "vitest",
  "regression_cmd": ["pnpm", "test"],
  "start_cmd": ["pnpm", "start"],
  "base_url": "http://127.0.0.1:3000/health",
  "allowed_paths": ["src/", "app/", "docs/QA/"]
}
```

Convenção: `it('CA-1 ...')`.

---

## 6. Checklist de ambiente (os 8 itens)

- [ ] repo **fora do OneDrive**, dentro do workspace do DSH
- [ ] `.gitignore` com `.dsh/`, `docs/manifesto/`, `__pycache__/`, `.pytest_cache/`, `.venv/`,
      `bin/`, `obj/`, `node_modules/`
- [ ] `.gitattributes` com `* text=auto eol=lf`
- [ ] comando de teste **gera relatório** (JUnit, JSON ou TRX) — provado rodando uma vez
- [ ] `dsh.json` com `acceptance_cmd`, `report_path`, `report_format`, `regression_cmd`,
      `start_cmd`, `base_url`, `allowed_paths`, `runner_configs`
- [ ] casca do app sobe pelo comando oficial e responde **404** em rota não mapeada
- [ ] `.claude/settings.json` + `CLAUDE.md` do arquiteto
- [ ] teste de fogo: `setup-check` verde e `gate` provando vermelho

---

## 7. Teste de fogo

```powershell
powershell -File tools\setup-check.ps1 -Repo . -Workspace C:\dev
python tools\dsh.py gate 001 --yes
```

Esperado: `=== ambiente pronto ===` e, no gate, `N testes, N falhas` + manifesto gravado.
Se o gate disser `relatorio de testes ausente`, o problema é o item 4 do checklist.

---

## 8. Falhas comuns (e a causa real)

| Sintoma | Causa | Correção |
|---|---|---|
| `relatorio de testes ausente` | flag de relatório errada, ou caminho diferente | conferir `report_path` × saída real do runner |
| `0 testes` | filtro não casou com o nome da classe | `--filter` igual ao nome usado no código |
| `oraculo adulterado` | teste/spec/runner mudou depois do gate | reverter; se a mudança era legítima, contestar |
| `commit divergente` | QA commitado junto com o código | QA fica **fora** do commit |
| `escopo estourado` | arquivo tocado fora do declarado na spec | dividir a fatia ou atualizar a spec |
| `Access denied` ao gravar | projeto fora do workspace do DSH | mover para dentro, ou trocar o workspace |
| `CRLF will be replaced` | normal — `.gitattributes` agindo | ignorar |
| `Unexpected UTF-8 BOM` | editor salvou com BOM | salvar como UTF-8 sem BOM (o DSH já lê `utf-8-sig`) |
| `__pycache__` no manifesto | filtro antigo | atualizar `tools/dsh.py` |

---

## 9. Em outra máquina — o resumo de seis linhas

```
1. winget install Git.Git Python.Python.3.12 (+ SDK do stack)
2. git clone https://github.com/eduardobolz12/workflow.git C:\dev\workflow
3. python C:\dev\workflow\tools\test_dsh.py      → 12 OK
4. copiar template → projeto, escolher dsh.<stack>.json
5. preencher start_cmd/base_url e rodar uma vez o comando de teste com relatório
6. setup-check verde + gate de fogo
```

---

## 10. O que o DSH vai te perguntar

Para não perder tempo, tenha estas respostas antes de começar:

1. **Nome e caminho** do projeto.
2. **Stack e versão** (`dotnet --list-sdks`, `python -V`, `node -v`).
3. **Comando que sobe o app** e em **qual porta/URL** ele responde.
4. **Comando de teste** que gera relatório.
5. **Projeto novo ou existente?** Se existente, onde está o código (`src/`, `app/`…).

---

## 11. Prompt de abertura (cole numa sessão nova)

```
Leia C:\dev\workflow\docs\workflow-ambiente.md e C:\dev\workflow\docs\guia_completo_workflow.md.
Você é o DSH. Vamos preparar o ambiente do projeto <nome> em <caminho>, stack <stack>.
Siga o checklist de 8 itens, um passo por vez, e pare para minhas decisões.
Não instale nada: me diga o comando. Não escreva fora do workspace.
Entregue: plano de até 12 passos, dsh.json preenchido, setup-check e gate de fogo.
```
