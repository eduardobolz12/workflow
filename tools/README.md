# DSH v0

Verificador do ciclo: `gate` (antes do build), `verify` (depois), `metrics`.
Só biblioteca padrão do Python 3.12 — não precisa instalar nada.

## Comandos

```powershell
python tools/dsh.py gate 001            # interativo: mostra CA + teste e pede aprovação
python tools/dsh.py gate 001 --yes      # aprovação automática (CI / teste)
python tools/dsh.py verify 001
python tools/dsh.py metrics 001 --rota normal --cas 2 --voltas 0 --tempo 45 --burla nao
python tools/dsh.py note "atrito: pytest 6min lento"
```

Sai com `0` = passou, `1` = verificação falhou, `2` = erro de operação.

## Configuração — `dsh.json` na raiz do projeto

| Chave | Exemplo | Para quê |
|---|---|---|
| `spec` | `docs/SPECS/{nnn}.md` | fonte da tabela de CAs |
| `acceptance_dir` | `tests/acceptance/{nnn}` | testes de aceitação (protegidos) |
| `acceptance_cmd` | `["python","-m","pytest","-q","--junitxml={report}"]` | **seu** comando |
| `report_path` | `.dsh/report-{nnn}.xml` | relatório legível pelo DSH |
| `report_format` | `junit` ou `vitest` | formato do relatório |
| `runner_configs` | `["pytest.ini","package.json"]` | entram no hash |
| `start_cmd` | `["pnpm","start"]` | sobe o app antes da suíte (opcional) |
| `base_url` | `http://127.0.0.1:3000` | usado para esperar o app |
| `regression_cmd` | `["pnpm","test"]` | suíte completa; roda depois da aceitação |
| `base_branch` | `main` | base do diff |
| `allowed_paths` | `["src/","app/","docs/QA/"]` | onde o diff pode tocar |

O diff é conferido contra a seção `## Arquivos que serão tocados` da spec quando ela existe; sem ela,
vale `allowed_paths`.

O repositório precisa ignorar os artefatos do verificador:

```
.dsh/
docs/manifesto/
```

## Duas decisões que divergem do manual v0

1. **Linha preliminar do gate.** O manual pede linha no `metricas.csv` no gate (passo 5) e
   "uma linha por fatia" no merge (seção 5) — as duas coisas não cabem no mesmo formato. O gate grava
   `docs/manifesto/NNN.state.json`; o CSV recebe uma linha só, no merge.
2. **`commit:` = HEAD.** Se o programador commitar o `docs/QA/NNN.md` junto com o código, o hash
   declarado nunca fecha (autorreferência). Regra: o QA é evidência **não commitada**; o commit
   declarado é o do código.

## O que ainda não existe

Holdout, `ca()` em Python, classificação do esqueleto, CR/QA automáticos, reexecução automática de
flake. Entram quando um defeito escapar e o mecanismo for a resposta direta.

## Antes de cada projeto

```powershell
powershell -File tools/setup-check.ps1 -Repo <caminho> -Workspace <workspace> -RunTests
```

Seis itens: localização, OneDrive, git/main, `.gitignore`, `dsh.json`, harness respondendo — e, com
`-RunTests`, se a suíte gera relatório.

## Testes do próprio DSH

```powershell
python tools/test_dsh.py
```

Dez casos: gate verde só com vermelho total, gate rejeitando teste que já passa, buraco de
rastreabilidade, entrega confirmada, oráculo adulterado, commit divergente, diff fora de escopo,
diff fora dos arquivos declarados na spec, regressão quebrada, métricas + nota.
