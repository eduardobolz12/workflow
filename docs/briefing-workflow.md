# Briefing — workflow de 3 papéis (pedido de segunda opinião)

## Como usar

Copie este documento inteiro no início de uma conversa nova com o agente. Ele não tem o contexto de
onde isso foi discutido, então tudo o que importa está aqui. Responda por escrito, apontando
discordâncias primeiro.

Instrução explícita: **não valide por educação.** Se o desenho estiver errado em algum ponto, a
resposta útil é a objeção mais forte que você conseguir sustentar, com o motivo.

## Contexto

- Desenvolvedor solo, Windows, VS Code.
- Ferramentas já instaladas: Claude Code 2.1.304 (CLI nativo + extensão, autenticado), Kimi Code
  0.8.2 (extensão; CLI `kimi` opcional), CodeRabbit CLI `cr` (opcional).
- O harness (DSH) executa comandos, mede e registra evidência; não escreve código e não decide.
- Projetos: aplicações web e automações, mantidos por meses, não descartáveis.

## Problema que o workflow resolve

1. Código gerado por IA sem prova de que funciona.
2. Retrabalho por especificação ambígua ("não era isso que eu pedi").
3. Agente que "conserta" o teste para ficar verde.
4. Loop infinito de revisão, cada um pedindo mudança no anterior.
5. Perda de contexto entre sessões: o próximo agente desfaz o trabalho do anterior.

## O desenho (v2)

### Papéis

| Papel | Ferramenta | Produz | Nunca faz |
|---|---|---|---|
| Decisor | humano | decisão, prioridade, merge | implementar |
| Arquiteto | Claude, sessão 1 | design, spec, teste de aceitação, esqueleto | corpos de código de produção |
| Programador | Kimi | implementação, testes internos | editar `tests/acceptance/`, ampliar escopo |
| Verificador | DSH | evidência: comandos, saídas, diff, gatilhos | editar código, decidir |
| Revisor mecânico | CodeRabbit | achados de bug no diff | julgar intenção |
| QA | Claude, sessão 2 | parecer contra a spec | editar código, repetir o CodeRabbit |

### Artefatos

| Arquivo | Dono | Quando |
|---|---|---|
| `docs/DESIGN.md` | arquiteto | uma vez por projeto |
| `docs/DECISOES.md` | arquiteto, aprovado pelo humano | toda escolha de rumo |
| `docs/SPECS/NNN-*.md` | arquiteto | uma por fatia, com critério executável |
| `tests/acceptance/NNN-*` | arquiteto (somente leitura p/ programador) | antes do build, falhando |
| `docs/QA/NNN.md` | DSH (evidência) + QA (parecer) | por fatia |
| `docs/QA/NNN-cr.md` | CodeRabbit | quando o gatilho dispara |

### O ciclo

```
[0] intenção                humano, 5 min
[1] spec + teste vermelho   arquiteto, 30 min
[2] portão 1                humano lê a spec e o diff do teste, 5 min
[3] build                   programador, até 1 dia
[4] verificação             DSH, 10 min → docs/QA/NNN.md
[5] portão 2                humano testa à mão, 15 min
[6] portão 3 (condicional)  CodeRabbit → QA
[7] merge                   humano, 2 min
```

Cada passo termina em arquivo. Nenhum passo começa sem o artefato do anterior.

### Portões por risco (não por rotina)

| Gatilho | Dispara | Detecção |
|---|---|---|
| > ~300 linhas ou > 8 arquivos | CodeRabbit | automática |
| `auth/`, pagamento, PII, upload | CodeRabbit + QA | automática |
| schema, migration, contrato público | CodeRabbit + QA | automática |
| dependência nova | CodeRabbit + QA | automática |
| "o humano não entendeu o diff" | QA | humana |
| diff pequeno, isolado, coberto | nada | — |

Revisão "quando o app estiver pronto" foi explicitamente rejeitada: diff grande, contexto perdido,
achado caro.

### Triagem — quem conserta o quê

| Achado | Natureza | Vai para |
|---|---|---|
| Código não faz o que a spec diz | bug | programador, com teste de regressão |
| Spec ambígua ou errada | spec | arquiteto; depois programador |
| Comportamento novo não pedido | escopo | humano decide e registra |
| Estilo, nome, comentário | cosmético | backlog, não bloqueia |

Bug conhecido não volta ao arquiteto. Revisor serve para o que ninguém viu.

### Caminho de falha

1. Achado vira item em `docs/QA/NNN.md`: esperado, obtido, passos, commit.
2. Vira teste de regressão **vermelho** (arquiteto escreve; ou programador escreve e o DSH prova o
   vermelho antes do conserto).
3. Programador corrige, um commit.
4. DSH reverifica e fecha o item.

### Rotas

| Rota | Gatilho | Passos |
|---|---|---|
| rápida | ≤3 arquivos, sem contrato, sem dep nova | programador → DSH → merge |
| normal | feature pequena | spec + teste → programador → DSH → teste físico |
| completa | contrato, dinheiro, PII, bug sem causa | ciclo inteiro |

### Regras

1. Um escritor por vez na árvore.
2. Uma branch por fatia.
3. Contrato antes do código: teste de aceitação vermelho.
4. Nada é "pronto" sem comando e saída.
5. Handoff só por arquivo, nunca por chat.
6. Decisão de rumo vai para `DECISOES.md`.
7. A spec muda antes do código, nunca o contrário.
8. Máximo 3 voltas por fatia; na terceira, o problema é spec ou escopo.

### O que medir

Defeitos que escaparam para o merge; voltas por fatia; tempo por fatia; taxa de burla (tarefas que
pularam o fluxo). Acima de ~30% de burla, o processo está caro demais.

## Decisões já tomadas, e o motivo

1. **Teste de aceitação escrito pelo arquiteto, antes do código, vermelho.** Quem define o oráculo
   não deve ser quem implementa. Impede o programador de "ajustar o teste".
2. **Duas sessões do Claude** (arquiteto e QA), com contextos separados, para o autor não julgar a
   própria obra.
3. **Revisores por risco**, não por etapa, porque QA por rotina em diff pequeno não paga.
4. **Fatias pequenas**, com a primeira sendo *walking skeleton* ponta a ponta.
5. **Bug conhecido não sobe para o arquiteto** — evita quatro agentes num defeito de duas linhas.
6. **Handoff por arquivo**, porque chat comprime com perda.

## O que já suspeitamos ser fraco

- Duas sessões do **mesmo modelo** não são independentes de verdade: mesmos vieses, mesmos pontos
  cegos.
- O **oráculo é escrito por quem desenha**: se o teste de aceitação estiver errado, o QA valida
  contra o mesmo erro.
- **CodeRabbit em branch local** rende pouco; ele foi feito para PR.
- **Três voltas** é um número arbitrário.
- **Custo em tokens/sessões** pode inviabilizar em projeto grande.
- É **processo de time aplicado a uma pessoa** — o risco é abandonar por atrito.

## Perguntas — responda como Arquiteto/QA (Claude)

1. Onde este desenho gera mais retrabalho do que economiza? Seja específico no ponto de falha.
2. O formato "spec + teste de aceitação vermelho" é suficiente para eliminar ambiguidade? O que
   falta na spec que você exigiria antes de aceitar a tarefa?
3. A separação arquiteto/QA em duas sessões muda algo de fato? Como você detectaria contaminação de
   contexto se ela existisse?
4. Qual etapa você **cortaria primeiro** e o que aconteceria na prática?
5. Escreva o critério de aceite de uma feature pequena (ex.: exportar uma lista filtrada em CSV) do
   jeito que você considera correto, para servir de referência de formato.
6. Se o humano decidisse usar só você (sem Kimi), o que mudaria no desenho?

## Perguntas — responda como Programador (Kimi)

1. "Spec + teste vermelho" é suficiente para implementar sem perguntar? O que costuma faltar?
2. A regra de não editar `tests/acceptance/` te impede de fazer algo necessário? Em que caso você
   precisaria mudar o teste, e o que deveria acontecer em vez disso?
3. Onde você tende a ir além do pedido, e qual cláusula do contrato te seguraria melhor?
4. Uma fatia de um dia é realista para o seu modo de trabalho? Como você a dividiria?
5. Que informação você precisa que normalmente não está na spec?
6. Se o teste de aceitação estiver errado, qual é o comportamento correto: parar, corrigir, ou
   implementar o que a spec diz? Justifique.

## Formato da resposta

- Discordâncias primeiro, cada uma com a seção citada.
- Se concordar com tudo, diga o que mudaria de qualquer forma.
- Não invente fatos sobre o repositório; se precisar de informação, pergunte.
