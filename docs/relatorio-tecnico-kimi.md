# Relatório técnico — ambiente e verificador

**Para:** Kimi (programador) · **De:** DSH (verificador) · **Data:** 22/10/2026

Não é pedido de revisão. É o estado real das ferramentas, o que já tem solução e o que não tem — para
você não gastar tempo tentando consertar o que não é seu.

## Parte 1 — Problemas com solução

| # | Problema | Efeito no fluxo | Solução | Quem | Quando |
|---|---|---|---|---|---|
| 1 | PATH do shell do DSH não tem node/npm/pnpm | comandos falham se não forem prefixados | prefixo no próprio comando | DSH | feito |
| 2 | Projeto fora do workspace do DSH | gate não grava manifesto nem QA | apontar o workspace para o repo | humano | antes da 001 |
| 3 | Repo dentro do OneDrive | lock e corrupção em `git worktree` | mover o repo para fora do OneDrive | humano | antes da 001 |
| 4 | Suíte sem relatório legível | gate não sabe quantos testes falharam | `--junitxml` (pytest) ou `--reporter=json` (vitest) no comando | humano | antes da 001 |
| 5 | App sem comando único de start | verify roda sem app e passa por padrão | `start_cmd` + `base_url` no `dsh.json` | humano | antes da 001 |
| 6 | Teste sem `CA-N` no nome | gate reprova por rastreabilidade | convenção fixa no template da spec | arquiteto | sempre |
| 7 | Processo órfão no Windows | porta presa depois do verify | `taskkill /T` no `dsh.py` | DSH | antes da 001 |
| 8 | Manifesto do DSH entrando no diff | entrega legítima reprovada como "escopo estourado" | `.dsh/` e `docs/manifesto/` no `.gitignore` | humano | antes da 001 |
| 9 | `commit:` autorreferente | hash declarado nunca fecha se o QA for commitado | QA é evidência **não commitada**; o commit declarado é o do código | você | sempre |
| 10 | Linha preliminar × linha única no CSV | formato ambíguo no manual | estado em `docs/manifesto/NNN.state.json`; CSV recebe uma linha no merge | DSH | feito |
| 11 | DSH sem HTTPS | não instala pacote | instalação é ato do humano | humano | quando precisar |
| 12 | Suíte completa lenta | verify demora | rodar tudo até doer; escopo só depois | — | se acontecer |

### Como vamos resolver, em ordem

1. **Humano:** repo dentro do workspace, fora do OneDrive; `.gitignore` com os dois caminhos; comando de
   teste com relatório; `start_cmd`/`base_url` no `dsh.json`.
2. **DSH:** `taskkill /T` no kill do app; `tools/setup-check.ps1` validando os seis itens de ambiente.
3. **Critério de pronto:** `python tools/dsh.py gate 001 --yes` roda de ponta a ponta num teste de
   exemplo, e `verify` recusa commit divergente e oráculo alterado.

## Parte 2 — Sem solução no desenho atual

| Problema | Por que | O que resta |
|---|---|---|
| **Adulteração deliberada na mesma conta** | não existe defesa dentro do mesmo usuário; só detecção | manifesto e hash de commit pegam acidente, não má-fé |
| **Independência real de modelo** | arquiteto e QA são o mesmo Claude | reduz contaminação de contexto, não vieses |
| **Flakiness** | v0 não tem reexecução automática | falso vermelho ocasional; reexecutar e registrar |

### Desconhecidos (não são problemas, são medições)

| Item | Como resolve |
|---|---|
| Custo real do Kimi por fatia | `/usage` antes/depois, 10 fatias, decisão com número |
| `start_cmd` funcionando no seu runtime | primeiro verify real com app de pé |

## Parte 3 — O que isso muda no seu dia

1. **QA não commitado.** Você commita código; o `docs/QA/NNN.md` fica fora do commit e declara
   `commit: <sha do código>` e `resultado: verde`.
2. **Não commite** `.dsh/` nem `docs/manifesto/` — se aparecerem no diff, a entrega é reprovada.
3. **Falha de ambiente não é bug seu.** Sem relatório, commit divergente ou manifesto alterado: pare,
   registre uma linha em `docs/QA/NNN.md` e devolva ao humano. Não tente consertar o harness.
4. **Teste antigo vermelho é falha sua.** O verify roda a suíte completa.
5. **Falha intermitente:** rode duas vezes; se sumir, registre "flake" com o nome do teste.
6. **Instalação de pacote** não passa pelo DSH. Peça ao humano.

## Parte 4 — O que eu ainda não sei

- Se o `start_cmd` funciona no seu runtime (não testado; só o app real prova).
- Se a suíte completa cabe em tempo aceitável no seu projeto.
