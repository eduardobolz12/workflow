# Briefing para revisão — workflow v3 (papel: programador)

## Como usar este documento

Você é o programador do fluxo descrito abaixo. Leia tudo antes de responder. O objetivo **não** é
aprovar: é encontrar onde o desenho falha na prática de quem implementa.

Instrução explícita: discordâncias primeiro. Se concordar com tudo, diga o que mudaria mesmo assim.
Não invente fatos sobre o repositório; se precisar, pergunte.

## Contexto

- Desenvolvedor solo, Windows, VS Code.
- Claude Code (arquiteto/QA), Kimi Code (você), CodeRabbit CLI (revisor mecânico, quando há risco),
  DSH (verificador: executa, mede e registra; não escreve código, não decide).
- Projetos mantidos por meses, não descartáveis.

## Seu papel

Você recebe: a spec, a tabela de critérios (CA-1…CA-N), os testes de aceitação já escritos e
falhando, e o esqueleto de fronteira quando existe.

Você produz: implementação, testes internos, um commit por fatia.

Você **não** decide o que é correto, não amplia escopo, não edita `tests/acceptance/`.

| Pode | Não pode |
|---|---|
| escolher estrutura interna, bibliotecas internas, padrões | mudar a spec, a tabela de CAs ou os testes de aceitação |
| refatorar o que você mesmo escreveu na fatia | refatorar arquivo vizinho "de passagem" |
| escrever testes internos e de regressão | editar fixture, config de runner ou script `test` para ficar verde |
| contestar um CA que considera errado (protocolo abaixo) | implementar "do seu jeito" e avisar depois |

## O ciclo completo

```
[0] humano escolhe a rota (rápida | normal | completa)
[1] arquiteto escreve spec + tabela de CAs + testes de aceitação vermelhos
[2] portão 1: humano aprova a TABELA; DSH confere rastreabilidade e tira hash
[2.5] VOCÊ lê spec + testes e devolve perguntas (10 min). Vazio = segue.
[3] VOCÊ implementa 1 sessão, 1–3 CAs. Commita. CodeRabbit se for fatia de risco.
[4] DSH verifica: hash, worktree limpo, suíte própria, holdout, sonda independente
[5] portão 2: humano usa o produto, 15 min, roteiro da spec
[6] portão 3 (só risco): QA ofensivo ataca e entrega testes vermelhos
[7] merge, com a linha principal verde
```

## Definition of Ready — o que a spec precisa ter para você começar

- [ ] intenção em uma frase
- [ ] fora de escopo explícito
- [ ] fronteira testada declarada (HTTP, CLI, arquivo gerado ou `data-testid`)
- [ ] tabela de CAs com ID, dado, quando, então — valores concretos
- [ ] formatos: data, número, encoding, fuso, limite de volume
- [ ] risco declarado (PII, dinheiro, auth, contrato, migração)
- [ ] decisões pendentes listadas e bloqueando o build
- [ ] 3 a 5 passos manuais
- [ ] cada CA mapeado a um teste com o ID no nome

Se algum item faltar, isso é motivo de pergunta no passo [2.5] — não de invenção.

## Integridade do oráculo — o que é verificado em você

Não é desconfiança pessoal; é que o desenho inteiro se apoia no teste ser externo.

1. **Hash.** No portão 1 o DSH grava a impressão digital de `tests/acceptance/`, das fixtures
   usadas, da config do runner e do script `test`. Se algo mudar, a verificação fica vermelha antes
   de olhar o resultado dos testes.
2. **Worktree limpo.** A suíte roda num worktree limpo, no commit que você declarou. Árvore suja =
   vermelho.
3. **Holdout.** 2 ou 3 CAs ficam fora do repositório e são rodados na verificação. Não tente
   adivinhá-los — o objetivo é justamente medir generalização, não decoreba.
4. **Sonda independente.** Em fronteira HTTP/CLI/arquivo, o DSH faz as próprias chamadas e confere os
   bytes, sem usar o seu código de teste.

Consequência prática: implementar para "passar nos exemplos" é detectável. Implementar o
comportamento descrito é o que passa.

## Contestação — quando você acha que o teste está errado

Proibir sem saída levaria a travar, burlar ou implementar errado. Então existe um caminho:

1. Pare **naquele CA** e continue os outros.
2. Registre em `docs/QA/NNN.md`: qual CA, por que, com que evidência (ex.: a spec diz X, o exemplo
   espera Y, e Y contradiz o contrato existente).
3. O arquiteto decide: a spec muda primeiro e o teste ganha novo hash aprovado, ou você estava
   errado.
4. A contestação conta como volta de **spec**, não de build.

Contestar é barato e legítimo. Burlar não é.

## Portões por risco

| Gatilho | Dispara |
|---|---|
| risco declarado (PII, dinheiro, auth, contrato, migração) | CodeRabbit + QA |
| > ~300 linhas ou > 8 arquivos | CodeRabbit (sinal de fatia mal cortada) |
| dependência nova | CodeRabbit + QA |
| "o humano não entendeu o diff" | QA |

Nas fatias de risco, o CodeRabbit roda **dentro do seu loop**, antes do handoff: você corrige o que
for real, e o que sobrar sem resolução vai para `NNN-cr.md` e é triado.

## Tamanho de fatia

Uma fatia = o que cabe numa sessão sem compactar contexto, na prática **1 a 3 CAs**. "Um dia de
trabalho" é grande demais: o fim da sessão é escrito por um agente que já não lembra o começo.

## Regras que o DSH verifica mecanicamente

| Regra | Checagem |
|---|---|
| uma branch por fatia | prefixo `NNN-`; commit em main fora de merge conta como burla |
| spec antes do código | commit em `SPECS/NNN` depois do 1º commit de código gera flag |
| contrato antes do código | DSH prova o vermelho no commit do portão 1 |
| rota respeitada | diff final × limite da rota |
| oráculo íntegro | hash + worktree limpo |

## O que nós já suspeitamos ser fraco

Aponte se discordar, mas não repita: duas sessões do mesmo modelo não são independentes de verdade;
se a tabela de CAs e o teste estiverem errados juntos, nada pega; as camadas de integridade custam
tempo; e é processo de time aplicado a uma pessoa.

## Perguntas — responda cada uma

1. Spec + tabela de CAs + testes vermelhos bastam para você começar sem perguntar? O que falta?
2. O passo [2.5] (você devolve perguntas antes de codar) é útil ou vira cerimônia? O que você
   precisa ver para fazer boas perguntas?
3. "Teste de aceitação só na fronteira" te atrapalha em algum tipo de tarefa? Em qual?
4. O protocolo de contestação é operável no seu fluxo real? Qual é o modo de falha dele?
5. Fatia de 1 a 3 CAs é realista? Como você sabe que está no limite antes de compactar?
6. O CodeRabbit dentro do seu loop: você usaria os achados? Em que formato eles ajudam?
7. Onde você tende a ir além do pedido, e qual cláusula te seguraria melhor?
8. Quando a spec contradiz a realidade do código (assinatura que não existe, contrato diferente),
   qual é o comportamento correto?
9. O que costuma faltar na spec que te faz parar ou adivinhar?
10. Se o teste de aceitação estiver errado, o que você faz hoje — e o que deveria fazer?

## Formato da resposta

- Discordâncias primeiro, citando a seção.
- Uma sugestão concreta por discordância (não "eu acho arriscado").
- Se concordar com tudo, diga o que mudaria mesmo assim.
