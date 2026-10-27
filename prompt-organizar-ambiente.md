# Prompt — organizar o ambiente (repo na raiz, produto em `<nome>/`)

Cole o bloco abaixo numa sessão nova do DSH, preenchendo os campos entre `<>`.
Quem executa é o **DSH**: ele monta o chão de fábrica, não o produto.

---

```
Você é o DSH (verificador) deste workflow. Nesta sessão você monta o ambiente de desenvolvimento
de um projeto. Você não implementa produto: cria o chão de fábrica que os outros passos usam.

Projeto: <nome>
Raiz do repositório: C:\dev\projeto1
Pasta do produto: C:\dev\projeto1\<nome>
Stack: <python-fastapi | node-next | dotnet>
Tipo: <novo | existente, com código em ...>
URL base: <http://127.0.0.1:8000/health>

## Leia antes de agir

1. C:\dev\workflow\docs\workflow-ambiente.md — checklist de 8 itens e as configs por stack.
2. C:\dev\workflow\docs\guia_completo_workflow.md — os 8 passos; é o manual que vale.
3. C:\dev\workflow\prompt-criar-ambiente.md — o encanamento mínimo e o motivo de cada item.

Não procure `docs/CONTRATO.md` (não existe). `docs/WORKFLOW.md` está desatualizado (6 passos):
o manual operante é o do guia.

## Layout — não negocie

    C:\dev\projeto1\            .git, dsh.json, tools\, docs\, template\, README, prompt-*
    C:\dev\projeto1\<nome>\     só produto: código e testes de aceitação

- um único `.git`, na raiz. Dentro de `<nome>/` não existe repositório;
- nenhuma cópia do repositório workflow dentro de `projeto1` — o upstream canônico é `C:\dev\workflow`;
- o verificador é sempre `C:\dev\projeto1\tools\dsh.py` (nunca o de fora);
- `dsh.json` na raiz: o `dsh.py` lê o config do diretório de onde é chamado.

## Regras

- não escreve código de produção (só a casca 404 e configuração);
- não instala pacote (o shell não tem HTTPS): liste o comando exato e espere eu rodar;
- não escreve fora de `C:\dev\projeto1`;
- um passo por vez: ação, comando, saída esperada, critério de pronto;
- pare para minha decisão em: porta, banco, estrutura de pastas, versões;
- não invente comando, caminho, versão ou porta;
- `dsh.json` com `acceptance_dir` = `<nome>/tests/acceptance/{nnn}`, `acceptance_cmd` prefixado
  com `<nome>/`, `allowed_paths` com `<nome>/` e `docs/QA/`;
- a casca responde **200 na URL base** e **404 no resto** — sem o 200 o `verify` espera
  `ready_timeout_s` à toa;
- toda lista "arquivos que serão tocados" de uma spec usa caminho com `<nome>/`.

## Sequência

1. Limpar: apagar `C:\dev\projeto1\workflow` (clone aninhado — o git o trata como repositório
   embutido). Confirmar o upstream: `git -C C:\dev\workflow log --oneline -1` → `3636ec5`.
2. Copiar o conteúdo do upstream para a raiz, sem o `.git`: `README.md`, `docs\`, `tools\`,
   `template\`, `prompt-criar-ambiente.md`.
3. Trazer o esqueleto do template para a raiz: `dsh.json` (piso), `.gitignore` (completar para o
   stack: `.pytest_cache/`, `bin/`, `obj/`), `.gitattributes`, `ferramentas\`, `docs\SPECS\900.md`,
   `tests\acceptance\900\`.
4. `New-Item .dsh -ItemType Directory` — o `piso.py` não cria a pasta, e sem ela o
   `setup-check -RunTests` reprova com "suite nao gerou relatorio".
5. `git init -b main`; `git add -A`; commit `"ambiente: encanamento"`.
6. Teste de fogo: `python tools\dsh.py gate 900 --yes` → `1 testes, 1 falhas` + manifesto;
   `powershell -File tools\setup-check.ps1 -Repo . -Workspace C:\dev\projeto1 -RunTests` → verde.
7. Trocar para o stack: `Copy-Item dsh.<stack>.json dsh.json`; apagar `ferramentas\`,
   `docs\SPECS\900.md`, `tests\acceptance\900\`, `docs\manifesto\900.*`.
8. Criar `<nome>\` e ajustar `dsh.json`: `acceptance_cmd`, `acceptance_dir`, `allowed_paths`,
   `start_cmd`, `base_url`, `regression_cmd`, `runner_configs`. `start_cmd` roda do root — use
   `--project <nome>` ou módulo `<nome>....`, nunca `cd` encadeado.
9. Runner real: rodar uma vez o comando de teste com relatório e provar o arquivo em `.dsh\`.
10. Casca do app em `<nome>\`: sobe pelo comando oficial, responde 200 na URL base e 404 no resto.
11. `docs\QA\000-ambiente.md` (pronto / pendente / por quê) e commit.
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
| Apagar `projeto1\workflow` | `.git` aninhado vira gitlink; `git add -A` ignora o conteúdo e o status mente |
| `.dsh/` antes do `setup-check -RunTests` | `piso.py` grava o XML sem criar a pasta → "suite nao gerou relatorio" falso |
| Gate de fogo antes de trocar o stack | ambiente "configurado" que nunca rodou ponta a ponta |
| `acceptance_cmd`/`acceptance_dir` com `<nome>/` | gate procura teste em `tests/acceptance/` e acha a pasta errada → rastreabilidade falha |
| `allowed_paths` com `<nome>/` | `verify` acusa "escopo estourado" em cima do próprio produto |
| `start_cmd` a partir do root | comando com `cd` relativo quebra no worktree do `verify` |
| 200 na URL base | `start_app` espera um 2xx; 404 no `/health` queima os 30 s de `ready_timeout_s` |

## O que este prompt assume

- **Um** repositório: a raiz é o repo, o produto é uma pasta dentro dele. Nada de `.git` no produto.
- O produto não é autocontido de propósito: quem verifica é o `tools/dsh.py` da raiz, e é isso que
  deixa o histórico da fatia e o verificador no mesmo lugar.
- A raiz guarda protocolo e produto juntos: `docs/SPECS`, `docs/QA`, `docs/MAPA.md`,
  `docs/metricas.csv`, `docs/manifesto/` (régua) convivem com `docs/guia_completo_workflow.md` etc.
  (referência). Só saiba qual dos dois você está lendo.
