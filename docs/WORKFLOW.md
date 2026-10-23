# Workflow — manual de operação (congelado)

Este é o documento que se usa. O `relatorio_workflow_v5.md` vira **referência**, não manual.
Nada aqui muda até 10 fatias rodadas.

## 6 passos

1. **Spec** — Claude, 20 min. Intenção (1 frase), fora de escopo, tabela de 2–3 CAs
   (ID | Dado | Quando | Então, valores concretos), 3 passos de teste manual.
2. **Você aprova a tabela** — 5 min. Lê os exemplos, não o código.
3. **Testes vermelhos** — Claude escreve em `tests/acceptance/NNN/`, só na fronteira (HTTP, CLI, arquivo,
   `data-testid`). Falham.
4. **Build** — Kimi implementa em `feat/NNN-slug`, commita, entrega comando + saída em `docs/QA/NNN.md`.
5. **Prova** — DSH, 10 min: worktree limpo no commit declarado, hash dos testes e da spec confere,
   suíte com comando próprio, diff.
6. **Aceite** — você testa os 3 passos (15 min), faz merge.

Risco alto (auth, dinheiro, PII, contrato, migration, dep nova)? Antes do merge: `cr` no diff e, se
sobrar dúvida, QA ofensivo do Claude.

## 4 arquivos

| Arquivo | Quem escreve |
|---|---|
| `docs/SPECS/NNN.md` | Claude |
| `tests/acceptance/NNN/` | Claude (Kimi não edita) |
| `docs/QA/NNN.md` | DSH + Kimi |
| `docs/metricas.csv` | DSH (uma linha por fatia) |

## 5 regras

1. Teste vermelho **antes** do código.
2. Kimi não edita spec nem `tests/acceptance/` — contesta.
3. Bug conhecido vai para o Kimi **com teste**, não para o arquiteto.
4. Nada é "pronto" sem comando e saída.
5. CR e QA só por risco — nunca "quando o app estiver pronto".

## O que está fora, e quando volta

Manifesto global, holdout, hash encadeado, helper `ca()`, healthcheck, transporte real, isolamento,
rota trivial, máquina de estados, `esperado-verde`.

**Regra de retorno:** um mecanismo só volta quando um defeito escapar e ele for a resposta direta.
Anote em `metricas.csv`: `defeito, fatia, mecanismo_que_teria_pegado`. Sem essa linha, o mecanismo
não volta.

## Os únicos números que importam

- defeitos que escaparam para o merge;
- voltas por fatia;
- tempo por fatia;
- taxa de burla (tarefas fora do fluxo).

Acima de ~30% de burla: corte um passou, não uma regra.

## Decisões fechadas

- 2 CAs por fatia (3 só em caso simples).
- QA ofensivo: adiado até 10 fatias.
- CR: teto de ~5 achados; acima disso, corrija o padrão.
- Rota trivial: não existe por enquanto.
- Contestação: decidida no próximo portão.

## Primeira ação

Escolher **uma** fatia de 2 CAs e rodar o passo 1. Nada mais.
