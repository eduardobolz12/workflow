# Prompt — organizar o ambiente

Um prompt por projeto, mas o mesmo texto sempre. Ele não sabe onde vai rodar: a **raiz é a pasta
atual** (o workspace que você selecionou ao abrir o DSH), e nome do projeto, stack e porta são
perguntados na abertura.

**Como usar:** abra uma sessão nova do DSH na pasta onde o projeto vai nascer e diga:

```
Leia prompt-organizar-ambiente.md e execute.
```

Se a pasta não tiver o arquivo, aponte para o repositório do workflow:

```
Leia C:\dev\workflow\prompt-organizar-ambiente.md e execute.
```

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

Raiz: a pasta atual — o workspace desta sessão. Confirme o caminho absoluto e não escreva fora dela.
Fonte das ferramentas: o repositório workflow nesta máquina (padrão C:\dev\workflow).
Origem: https://github.com/eduardobolz12/workflow
Template: https://github.com/eduardobolz12/workflow/tree/main/template

## Abertura — antes de qualquer ação

1. Diga em 2 linhas o que vai fazer e em que pasta (caminho absoluto). Nada além disso.
2. Inventarie a raiz: está vazia? é repositório git com commits? já existe uma pasta `workflow\`?
   Se houver qualquer coisa, mostre o inventário e pergunte antes de tocar em arquivo.
3. Pergunte, uma de cada vez, esperando a resposta:
   - "Qual é o nome do projeto?" — é o nome da pasta do software: `<projeto>\`.
   - "Projeto novo ou existente?" — se existente, onde está o código hoje.
   - "Qual stack?" — python-fastapi, node-next ou dotnet. Se eu não souber, explique em 1 linha
     o custo de cada um: comando de teste com relatório e porta padrão.
   - "Qual porta e URL base?" — sugira o padrão do stack escolhido.
4. Só então monte o plano numerado. Não execute nada antes de eu aprovar.

## Layout — não negocie

Tudo relativo à raiz:

    .\workflow\              ferramentas + manual (cópia do repositório, sem .git)
    .\docs\                  SPECS\, QA\, MAPA.md, metricas.csv, manifesto\   ← a régua
    .\tests\acceptance\      os testes, uma pasta por fatia (NNN)
    .\<projeto>\             só software: código e config do stack
    .\dsh.json  .gitignore  .gitattributes

- um único .git, na raiz. `workflow\` e `<projeto>\` não têm repositório;
- a régua (docs\ e tests\) fica FORA do produto, de propósito: é o que impede o programador de
  "ajustar" o teste;
- `dsh.json` na raiz: o `dsh.py` lê o config do diretório de onde é chamado;
- o verificador é sempre `python workflow\tools\dsh.py`, chamado da raiz;
- `workflow\` é cópia vendorizada: não é submódulo e não entra no `.gitignore`.

## Regras

- não escreve código de produção (só a casca 404 e configuração);
- não instala pacote (o shell não tem HTTPS): lista o comando exato e espera eu rodar;
- não escreve fora da raiz;
- um passo por vez: ação, comando, saída esperada, critério de pronto;
- para para minha decisão em: porta, banco, estrutura de pastas, versões;
- não inventa comando, caminho, versão ou porta;
- `allowed_paths` do `dsh.json` = ["<projeto>/", "docs/QA/"];
- a casca responde 200 em `base_url` e 404 em qualquer outra rota;
- toda lista "arquivos que serão tocados" de uma spec usa caminho `<projeto>/...`.

## Sequência

1. Trocar o clone por cópia vendorizada. Se `C:\dev\workflow` não existir:
   `git clone https://github.com/eduardobolz12/workflow.git C:\dev\workflow`.
   Se `.\workflow` já existir e não for a cópia do repositório, pare e pergunte.

       Remove-Item .\workflow -Recurse -Force
       robocopy C:\dev\workflow .\workflow /E /XD .git

   Conferir: `.\workflow\tools\dsh.py` existe e `.\workflow\.git` NÃO existe.
   Código de saída 1–3 do robocopy é sucesso.

2. Esqueleto do template para a raiz, criando as pastas: `dsh.json` (piso), `.gitignore`,
   `.gitattributes`, `ferramentas\`, `docs\SPECS\900.md`, `tests\acceptance\900\`.
   `.gitignore`: `.dsh/`, `docs/manifesto/`, `__pycache__/`, `.pytest_cache/`, `.venv/`,
   `node_modules/`, `bin/`, `obj/`.

3. `New-Item .dsh -ItemType Directory` — o `piso.py` não cria a pasta, e sem ela o
   `setup-check -RunTests` reprova com "suite nao gerou relatorio".

4. Ajustar `.\workflow\tools\setup-check.ps1`: trocar as duas ocorrências de `tools\dsh.py`
   por `workflow\tools\dsh.py`. Registrar em `docs\QA\000-ambiente.md` como divergência local.

5. Se a raiz ainda não for repositório: `git init -b main`. Depois `git add -A` e commit
   `"ambiente: encanamento"`.

6. Teste de fogo:

       python workflow\tools\dsh.py gate 900 --yes
       powershell -File workflow\tools\setup-check.ps1 -Repo . -Workspace . -RunTests

   Esperado: `1 testes, 1 falhas` + manifesto gravado; `=== ambiente pronto ===`.

7. Trocar para o stack: `Copy-Item workflow\template\dsh.<stack>.json dsh.json`; apagar
   `ferramentas\`, `docs\SPECS\900.md`, `tests\acceptance\900\`, `docs\manifesto\900.*`.

8. Criar `.\<projeto>\` e ajustar `dsh.json`: `allowed_paths`, `start_cmd`, `base_url`,
   `regression_cmd`, `runner_configs`. `start_cmd` roda da raiz — use `--project <projeto>` ou
   módulo `<projeto>.app.main:app`, nunca `cd` encadeado. `tests/acceptance/{nnn}` fica como
   está: os testes moram na raiz mesmo.

9. Runner real: rodar uma vez o comando de teste com relatório e provar o arquivo em `.\dsh\`.

10. Casca do app em `.\<projeto>\`: sobe pelo comando oficial, responde 200 em `base_url` e 404
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
| Raiz = pasta atual, inventariada antes | prompt que apaga/sobrescreve arquivo de uma pasta que não era dele |
| Nome, stack e porta perguntados na abertura | prompt decorado com o projeto errado, ou com o stack de outro produto |
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

- **Uma pasta = um projeto.** As fatias numeram 001… no repo inteiro. Se um dia houver dois
  produtos no mesmo repo, prefixe a spec por produto (`docs\SPECS\<projeto>\NNN.md`) e ajuste a
  chave `spec` — fora isso, não muda nada.
- **O prompt não tem projeto embutido.** Nome, stack e porta entram na conversa, não no arquivo.
  Você pode rodar o mesmo texto em qualquer pasta, em qualquer projeto, sem editar nada.
- **Atualizar as ferramentas** é ato deliberado: copiar de `C:\dev\workflow` de novo, conferir
  `python workflow\tools\dsh.py --help`, rodar o teste de fogo, commitar. O `dsh.py` não entra no
  manifesto, então o commit é o único registro de qual versão aprovou cada fatia.

## Onde este prompt mora

Versionado no repositório do workflow, não no produto: `C:\dev\workflow\prompt-organizar-ambiente.md`.
Para começar um projeto, copie o arquivo para a raiz e execute — depois do passo 1 ele existe dos
dois lados, na raiz (se você copiou) e em `.\workflow\`.

Ele **não afeta o projeto**: o `dsh.py` só hasheia `docs/SPECS/`, `tests/acceptance/NNN/` e a
config do runner. O prompt não entra no manifesto, não entra no diff e não é lido pelo `gate` nem
pelo `verify`. É um arquivo inerte no repo — útil como referência, invisível para o processo.
