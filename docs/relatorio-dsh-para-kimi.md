# A parte do DSH — o que eu executo e o que espero de você

**Para:** Kimi (programador) · **De:** DSH (verificador) · **Data:** 22/10/2026

Este relatório cobre **só a minha parte**: o que eu executo, o que já foi provado, o que ainda não foi, e
o que cada mensagem minha significa para você.

## 1. Escopo

| Eu executo | Eu nunca executo |
|---|---|
| rodo comando e suíte de teste | escrevo ou corrijo código |
| calculo hash, manifesto, worktree | decido se o comportamento está certo |
| comparo commits, diff, resultados | negocio prazo, escopo ou exceção |
| registro evidência em arquivo | aceito "deve funcionar" como prova |
| anexo métrica | conserto o harness no meio da fatia |

## 2. As três operações

### `dsh gate NNN` — antes de você codar

1. **Rastreabilidade:** todo CA da tabela tem teste com o ID no nome; nenhum teste com ID órfão.
2. **Vermelho provado:** rodo a suíte com **meu** comando e exijo 100% de falha. Teste que já passa
   antes do build reprova o gate.
3. **Manifesto:** hash de `tests/acceptance/NNN/`, fixtures, spec e config do runner.
   Gravado **depois** da aprovação humana — gate rejeitado não deixa manifesto.
4. **Tela de aprovação:** cada CA com a linha da spec e o **código do teste inteiro** ao lado.
5. **Estado:** `docs/manifesto/NNN.state.json` (commit aprovado, data).

### `dsh verify NNN` — depois da sua entrega

1. **Commit:** o `commit:` do `docs/QA/NNN.md` tem que ser o HEAD da branch.
2. **Worktree limpo** nesse commit — não rodo na sua árvore.
3. **Manifesto íntegro antes de olhar resultado:** qualquer diferença = `oráculo adulterado`.
4. **App de verdade:** se `start_cmd` existir no `dsh.json`, subo o app antes da suíte.
5. **Suíte com meu comando** e comparação: verde×verde = confirmado; vermelho meu×verde seu = ambiente;
   vermelho nos dois = falha real.
6. **Suíte de regressão** (`regression_cmd`), se configurada: teste antigo vermelho reprova.
7. **Diff confinado** aos arquivos declarados na spec (ou `allowed_paths`).
8. **Evidência** em `docs/QA/NNN.md` sob `## Prova do DSH`. Processo do app morto com `taskkill /T`.

### `dsh metrics` — no aceite

Uma linha em `docs/metricas.csv`: fatia, rota, CAs, voltas, tempo, gatilhos, contestações, escapados,
burla, observação. Notas só via `dsh note "texto"`.

## 3. O que eu preciso da sua entrega

- commit na branch `feat/NNN-*` ou `fix/NNN-*`, árvore limpa;
- `docs/QA/NNN.md` **não commitado**, com `commit: <sha do código>` e `resultado: verde`;
- comando e saída da suíte colados nesse arquivo;
- nada de `.dsh/` nem `docs/manifesto/` no commit.

## 4. O que cada mensagem minha significa

| Mensagem | Causa | Quem age |
|---|---|---|
| `rastreabilidade falhou` | CA sem teste, ou teste sem CA | arquiteto |
| `vermelho nao provado` | teste já verde, suíte vazia, ou saiu com 0 | arquiteto |
| `o comando nao gerou relatorio` | runner sem flag de relatório | humano (ambiente) |
| `oraculo adulterado` | teste, fixture, spec ou runner mudou após o gate | você reverte; se foi legítimo, contesta |
| `commit divergente` | QA declara um commit, HEAD é outro | você reentrega |
| `suite de regressao falhou` | teste antigo quebrou | você corrige |
| `escopo estourado` | arquivo fora do declarado na spec | você ou o humano (se o escopo mudou de verdade) |
| `entrega confirmada` | tudo conferido | humano: aceite |

## 5. O que já foi provado

Executado ponta a ponta num repositório git real, com app simulado:

- gate: vermelho 2/2, manifesto, tela de aprovação, estado;
- verify: worktree limpo, manifesto íntegro, diff confinado, evidência;
- **teste negativo:** teste alterado depois do gate → `oráculo adulterado`, exit 2;
- regressão quebrada, commit divergente, diff fora de escopo: todos reprovam;
- métrica e nota anexadas.

## 6. O que ainda não foi provado

| Item | Por quê | Risco |
|---|---|---|
| `start_cmd` com app real | nunca rodei com servidor de verdade | app não sobe → falso vermelho |
| runner real (pytest/vitest) | o demo usa um stub que emite JUnit | relatório real pode ter formato diferente |
| suíte longa | não medi tempo | verify lento |

Nenhum desses muda o contrato com você. Mudam o meu tempo e podem gerar 2–3 correções na primeira
fatia real.

## 7. Se eu falhar

Falso vermelho ou falso verde é defeito meu. Registre uma linha em `docs/QA/NNN.md` (`atrito: ...`) e
siga; o humano decide na hora, e o caso entra na revisão das 10 fatias. Não tente compensar no código —
"consertar para o verificador passar" é o começo da fraude que o manifesto existe para pegar.
