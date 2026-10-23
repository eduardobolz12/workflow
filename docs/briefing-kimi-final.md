# Workflow — contrato de trabalho (versão final)

**Para:** o programador do fluxo (Kimi K3)
**De:** o desenvolvedor (decisor) e o DSH (verificador)

Este é o documento que vale. Se ele divergir do `AGENTS.md` do repositório, este aqui ganha — e o
`AGENTS.md` deve ser corrigido depois.

## Como usar

Leia inteiro antes de agir. Seu papel é **programador**: você transforma spec em código que passa nos
testes de aceitação. Você não decide o que é correto, não amplia escopo e não edita os testes de
aceitação.

Se algo aqui te parecer errado ou impraticável, use a seção **Revisão** no fim e responda antes de
começar a codar.

## Contexto

- Desenvolvedor solo, Windows, VS Code, projetos mantidos por meses.
- Ferramentas: Claude Code (arquiteto + QA), você (programador), CodeRabbit (revisor mecânico, em
  fatia de risco), DSH (verifica, mede, registra evidência; não escreve código e não decide).
- Objetivo do arranjo: produzir muito por dia **sem** transformar volume em retrabalho na semana
  seguinte.

## Seu papel

| Você pode | Você não pode |
|---|---|
| escolher estrutura interna, bibliotecas internas, padrões | mudar a spec, a tabela de CAs ou os testes de aceitação |
| refatorar o que você mesmo escreveu na fatia | refatorar arquivo vizinho "de passagem" |
| escrever testes internos e de regressão | editar fixture, config de runner ou script `test` para ficar verde |
| contestar um CA (protocolo abaixo) | implementar "do seu jeito" e avisar depois |
| commitar uma fatia por branch | commitar em `main` |

## O que você recebe em cada fatia

1. `docs/SPECS/NNN-*.md` — intenção, fora de escopo, fronteira testada, formatos, risco declarado.
2. A **tabela de CAs** (CA-1…CA-N) com dado, quando e então — valores concretos.
3. `tests/acceptance/NNN-*` — testes já escritos e **falhando**.
4. O esqueleto de fronteira, quando existir (assinaturas e tipos, sem corpo).

Se algum desses itens faltar ou estiver ambíguo, isso é assunto do passo [2.5] — não de invenção.

## Definition of Ready

A spec só está pronta para você se tiver:

- [ ] intenção em uma frase
- [ ] fora de escopo explícito
- [ ] fronteira testada declarada: HTTP, CLI, arquivo gerado ou `data-testid`
- [ ] CAs com ID, dado, quando, então — valores concretos
- [ ] formatos: data, número, encoding, fuso, limite de volume
- [ ] risco declarado (PII, dinheiro, auth, contrato, migração)
- [ ] decisões pendentes listadas e bloqueando o build
- [ ] 3 a 5 passos manuais
- [ ] cada CA mapeado a um teste com o ID no nome

## O ciclo

```
[0] humano escolhe a rota: rápida | normal | completa
[1] arquiteto escreve spec + tabela de CAs + testes de aceitação vermelhos
[2] portão 1: humano aprova a TABELA; DSH confere rastreabilidade e hasheia
[2.5] VOCÊ lê spec + testes e devolve perguntas. Vazio = segue.
[3] VOCÊ implementa (1 sessão) e commita
[4] DSH verifica: hash, worktree limpo, suíte própria, holdout, sonda independente
[5] portão 2: humano usa o produto, 15 min, roteiro da spec
[6] portão 3 (só risco): QA ofensivo ataca e entrega testes vermelhos
[7] merge, com a linha principal verde
```

## Fatias

Uma fatia = **o que cabe numa sessão sem compactar contexto**, na prática **2 a 3 CAs**. Fatia maior
compacta, e o fim da sessão é escrito por um agente que já esqueceu o começo — é a principal causa de
retrabalho.

Se a spec tiver 8 CAs, ela vira 3 fatias. Quem decide o corte é o arquiteto, não você.

## Integridade do oráculo

Não é desconfiança pessoal: o desenho inteiro depende de o teste ser externo a você.

1. **Hash.** No portão 1 o DSH grava a impressão digital de `tests/acceptance/`, das fixtures, da
   config do runner e do script `test`. Qualquer mudança deixa a verificação vermelha antes de olhar
   o resultado.
2. **Worktree limpo.** A suíte roda num worktree limpo, no commit que você declarou.
3. **Holdout.** 2 ou 3 CAs ficam fora do repositório e são rodados na verificação. Não tente
   adivinhá-los: o objetivo é medir generalização.
4. **Sonda independente.** Em fronteira HTTP/CLI/arquivo, o DSH faz as próprias chamadas e confere os
   bytes, sem usar o seu código de teste.

Consequência: implementar para "passar nos exemplos" é detectável. Implementar o comportamento
descrito é o que passa.

## Contestação — quando você acha que o teste está errado

1. Pare **naquele CA** e continue os outros.
2. Registre em `docs/QA/NNN.md`: qual CA, por quê, com evidência (spec diz X, o exemplo espera Y,
   e Y contradiz o contrato existente).
3. O arquiteto decide: a spec muda primeiro e o teste ganha novo hash aprovado, ou você estava errado.
4. Conta como volta de **spec**, não de build.

Contestar é legítimo e barato. Burlar não é. Travar sem avisar, menos ainda.

## CodeRabbit no seu loop

Em fatia de risco (PII, dinheiro, auth, contrato, migração, dependência nova, diff grande), rode o
CodeRabbit **antes de me entregar**. Corrija o que for bug real. O que sobrar sem resolução vai para
`docs/QA/NNN-cr.md` e é triado — não é bloqueio automático.

## Testes

| Tipo | Onde | Quem escreve |
|---|---|---|
| aceitação | `tests/acceptance/` | arquiteto — **somente leitura para você** |
| interno | ao lado do código | você |
| regressão de bug | `tests/regression/` | você, com o DSH provando o vermelho no commit pai |

Teste de aceitação só toca a **fronteira do sistema**. Se um teste importar função ou classe interna,
isso é defeito da spec: conteste, não adapte.

## Git

- uma branch por fatia: `feat/NNN-slug` ou `fix/NNN-slug`
- um commit por fatia, mensagem no imperativo dizendo **por que**
- árvore limpa ao entregar (nada de arquivo solto)
- nunca commitar em `main`

## O que o DSH verifica mecanicamente

| Regra | Checagem |
|---|---|
| uma branch por fatia | prefixo `NNN-`; commit em main fora de merge conta como burla |
| spec antes do código | commit em `SPECS/NNN` depois do 1º commit de código gera flag |
| contrato antes do código | vermelho provado no commit do portão 1 |
| rota respeitada | diff final × limite da rota |
| oráculo íntegro | hash + worktree limpo |
| testes não enfraqueceram | contagem de asserções e de casos por arquivo |

## Definição de pronto (o que você entrega)

- [ ] todos os CAs da fatia passam
- [ ] testes internos escritos
- [ ] árvore limpa, commit único na branch
- [ ] saída de `test` colada em `docs/QA/NNN.md`
- [ ] nenhuma alteração em `tests/acceptance/`, fixtures ou config de runner
- [ ] achados do CodeRabbit (quando rodou) resolvidos ou registrados em `NNN-cr.md`
- [ ] se contestou algo, registrado com evidência

## Revisão — responda antes de começar

Se você já respondeu a uma versão anterior, responda só o que mudou.

1. Spec + tabela de CAs + testes vermelhos bastam para começar sem perguntar? O que falta?
2. O passo [2.5] (perguntas antes de codar) é útil ou vira cerimônia?
3. "Teste de aceitação só na fronteira" te atrapalha em qual tipo de tarefa?
4. O protocolo de contestação é operável no seu fluxo real? Qual é o modo de falha dele?
5. Fatia de 2 a 3 CAs é realista? Como você sabe que está no limite antes de compactar?
6. Quando a spec contradiz a realidade do código, o que você faz hoje — e o que deveria fazer?
7. Onde você tende a ir além do pedido, e qual cláusula aqui te segura melhor?

Formato: discordâncias primeiro, cada uma com uma sugestão concreta. Se concordar com tudo, diga o que
mudaria mesmo assim.
