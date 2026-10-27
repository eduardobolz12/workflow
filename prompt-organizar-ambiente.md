# Prompt — organizar o ambiente

**Como usar:** abra uma sessão nova do DSH com o workspace na raiz do repositório e diga:

```
Leia prompt-organizar-ambiente.md e execute.
Projeto: <projeto>
Stack: <python-fastapi | node-next | dotnet>
URL base: <http://127.0.0.1:8000/health>
É projeto novo.
```

Se o prompt já estiver dentro de `workflow\`, troque o primeiro caminho por
`workflow\prompt-organizar-ambiente.md`.

**Origem:** [github.com/eduardobolz12/workflow](https://github.com/eduardobolz12/workflow) — as
ferramentas em `tools/`, o projeto-base em
[template](https://github.com/eduardobolz12/workflow/tree/main/template). Numa máquina nova:

```powershell
git clone https://github.com/eduardobolz12/workflow.git C:\dev\workflow
```

Quem executa é o **DSH**: ele monta o chão de fábrica, não o produto.

---

```
Você é o DSH (verificador) deste workflow. Nesta sessão você monta o ambiente de desenvolvimento
de um projeto. Você não implementa produto: cria o chão de fábrica que os outros passos usam.

Raiz do repositório (workspace desta sessão): <raiz>
Pasta do software: <raiz>\<projeto>
Stack: <python-fastapi | node-next | dotnet>
Tipo: <novo | existente, com código em ...>
URL base: <http://127.0.0.1:8000/health>
Fonte das ferramentas: C:\dev\workflow
Origem: https://github.com/eduardobolz12/workflow
Template: https://github.com/eduardobolz12/workflow/tree/main/template

## Leia antes de agir

1. <raiz>\workflow\docs\workflow-ambiente.md — checklist de 8 itens e as configs por stack.
2. <raiz>\workflow\docs\guia_completo_workflow.md — os 8 passos; é o manual que vale.
3. <raiz>\workflow\prompt-criar-ambiente.md — o encanamento mínimo e o motivo de cada item.

Não procure docs/CONTRATO.md (não existe). docs/WORKFLOW.md está desatualizado (6 passos):
o manual operante é o do guia.

## Layout — não negocie

    <raiz>\                     .git, dsh.json, .gitignore, .gitattributes
    <raiz>\workflow\            ferramentas + manual (cópia sem .git)
    <raiz>\docs\                SPECS\, QA\, MAPA.md, metricas.csv, manifesto\   ← a régua
    <raiz>\tests\acceptance\    os testes, uma pasta por fatia (NNN)
    <raiz>\<projeto>\           só software: código e config do stack

- um único .git, na raiz. `workflow\` e `<projeto>\` não têm repositório;
- a régua (docs\ e tests\) fica FORA do produto, de propósito: é o que impede o programador de
  "ajustar" o teste;
- `dsh.json` na raiz: o `dsh.py` lê o config do diretório de onde é chamado;
- o verificador é sempre `python workflow\tools\dsh.py`, chamado da raiz;
- `workflow\` é cópia vendorizada: não é submódulo e não entra no `.gitignore`.

## Regras

- não escreve código de produção (só a casca 404 e configuração);
- não instala pacote (o shell não tem HTTPS): lista o comando exato e espera eu rodar;
- não escreve fora de <raiz>;
- um passo por vez: ação, comando, saída esperada, critério de pronto;
- para para minha decisão em: porta, banco, estrutura de pastas, versões;
- não inventa comando, caminho, versão ou porta;
- `allowed_paths` do `dsh.json` = ["<projeto>/", "docs/QA/"];
- a casca responde 200 em `base_url` e 404 em qualquer outra rota;
- toda lista "arquivos que serão tocados" de uma spec usa caminho `<projeto>/...`.

## Sequência

1. Trocar o clone por cópia vendorizada. Se `C:\dev\workflow` não existir:
   `git clone https://github.com/eduardobolz12/workflow.git C:\dev\workflow`.

       Remove-Item <raiz>\workflow -Recurse -Force
       robocopy C:\dev\workflow <raiz>\workflow /E /XD .git

   Conferir: `<raiz>\workflow\tools\dsh.py` existe e `<raiz>\workflow\.git` NÃO existe.
   Código de saída 1–3 do robocopy é sucesso.
   Apagar da raiz as cópias soltas `prompt_claude_arquiteto.md` e `prompt-organizar-ambiente.md`:
   a versão canônica passa a ser a de dentro de `workflow\`.

2. Esqueleto do template para a raiz, criando as pastas: `dsh.json` (piso), `.gitignore`,
   `.gitattributes`, `ferramentas\`, `docs\SPECS\900.md`, `tests\acceptance\900\`.
   `.gitignore`: `.dsh/`, `docs/manifesto/`, `__pycache__/`, `.pytest_cache/`, `.venv/`,
   `node_modules/`, `bin/`, `obj/`.

3. `New-Item .dsh -ItemType Directory` — o `piso.py` não cria a pasta, e sem ela o
   `setup-check -RunTests` reprova com "suite nao gerou relatorio".

4. Ajustar `<raiz>\workflow\tools\setup-check.ps1`: trocar as duas ocorrências de `tools\dsh.py`
   por `workflow\tools\dsh.py`. Registrar em `docs\QA\000-ambiente.md` como divergência local.

5. `git init -b main`; `git add -A`; commit `"ambiente: encanamento"`.

6. Teste de fogo:

       python workflow\tools\dsh.py gate 900 --yes
       powershell -File workflow\tools\setup-check.ps1 -Repo . -Workspace <raiz> -RunTests

   Esperado: `1 testes, 1 falhas` + manifesto gravado; `=== ambiente pronto ===`.

7. Trocar para o stack: `Copy-Item workflow\template\dsh.<stack>.json dsh.json`; apagar
   `ferramentas\`, `docs\SPECS\900.md`, `tests\acceptance\900\`, `docs\manifesto\900.*`.

8. Criar `<projeto>\` e ajustar `dsh.json`: `allowed_paths`, `start_cmd`, `base_url`,
   `regression_cmd`, `runner_configs`. `start_cmd` roda da raiz — use `--project <projeto>` ou
   módulo `<projeto>.app.main:app`, nunca `cd` encadeado. `tests/acceptance/{nnn}` fica como
   está: os testes moram na raiz mesmo.

9. Runner real: rodar uma vez o comando de teste com relatório e provar o arquivo em `.dsh\`.

10. Casca do app em `<projeto>\`: sobe pelo comando oficial, responde 200 em `base_url` e 404
    no resto.

11. `docs\QA\000-ambiente.md` (pronto / pendente / por quê) e commit `"ambiente: stack"`.

12. `setup-check` final: `=== ambiente pronto ===`.

## Entregável

1. plano numerado, no máximo 12 passos, com comando e critério de pronto em cada um;
2. os arquivos criados, um por vez, com o conteúdo colado;
3. saída do `setup-check` e do `gate` de fogo;
4. `docs\QA\000-ambiente.md` com o que ficou pronto, o que ficou pendente e por quê.

Não execute nada antes de eu aprovar o plano.
```

---

## Por que cada item existe

| Item | Falha que evita |
|---|---|
| `workflow\` sem `.git` | clone aninhado vira gitlink; `git add` ignora o conteúdo e o status mente |
| Um `.git` só na raiz | histórico separado: a fatia não registra qual versão do verificador a aprovou |
| `/E /XD .git` no robocopy | copiar o `.git` do upstream cria o repositório embutido de novo |
| Régua fora do produto | o produto vira um pacote que se entrega sem arrastar o teste |
| `.dsh/` antes do `setup-check -RunTests` | `piso.py` grava o XML sem criar a pasta → "suite nao gerou relatorio" falso |
| Ajuste do `setup-check` | ele procura `tools\dsh.py` no repo e reprova o layout |
| Gate de fogo antes do stack | ambiente "configurado" que nunca rodou ponta a ponta |
| `allowed_paths` com `<projeto>/` | `verify` acusa "escopo estourado" em cima do próprio produto |
| `start_cmd` a partir da raiz | comando com caminho relativo quebra no worktree do `verify` |
| 200 na URL base | `start_app` espera um 2xx; 404 queima os 30 s de `ready_timeout_s` |

## O que este prompt assume

- **Um repositório por projeto.** As fatias numeram 001… no repo inteiro. Se um dia houver dois
  produtos no mesmo repo, prefixe a spec por produto (`docs\SPECS\<projeto>\NNN.md`) e ajuste a
  chave `spec` — fora isso, não muda nada.
- **De um produto para outro, mudam três coisas:** o campo `Projeto`, o `stack` e a `URL base`.
  O resto do prompt é idêntico.
- **Atualizar as ferramentas** é ato deliberado: copiar de `C:\dev\workflow` de novo, conferir
  `python workflow\tools\dsh.py --help`, rodar o teste de fogo, commitar. O `dsh.py` não entra no
  manifesto, então o commit é o único registro de qual versão aprovou cada fatia.

## Onde este prompt mora

Versionado no repositório do workflow, não no produto:
`C:\dev\workflow\prompt-organizar-ambiente.md` (commit local `a8eaa57`; sem push, o GitHub ainda
mostra a versão anterior). Para começar um projeto, copie o arquivo para a raiz e cole — depois do
passo 1 ele existe dos dois lados: na raiz, se você copiou, e em `<raiz>\workflow\`.

Ele **não afeta o projeto**: o `dsh.py` só hasheia `docs/SPECS/`, `tests/acceptance/NNN/` e a
config do runner. O prompt não entra no manifesto, não entra no diff e não é lido pelo `gate` nem
pelo `verify`. É um arquivo inerte no repo — útil como referência, invisível para o processo.
