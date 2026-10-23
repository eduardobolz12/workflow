# Workflow completo — v3

Status: consolidado após revisão adversarial. Substitui a v2. Vale para projeto mantido; protótipo
descartável usa a rota rápida.

## O que mudou da v2

| Mudança | Motivo |
|---|---|
| Portão 1 vale na rota normal também | o erro caro é o oráculo, no começo, não o QA no fim |
| O humano aprova **tabela de exemplos** (CA-1…CA-N), não código de teste | ler teste é aprovação por cansaço; ler 8 linhas de tabela é 2 min |
| Rastreabilidade CA ↔ teste conferida pelo DSH | critério sem teste é promessa, teste sem CA é código órfão |
| Novo passo [2.5]: programador devolve perguntas antes de codar | única leitura do oráculo por outro modelo; custa 10 min |
| Integridade do oráculo: hash + comando próprio + holdout + sonda independente | permissão de agente não é autoridade; diretório protegido não é prova |
| Protocolo de contestação do teste | proibir sem saída gera travamento, burla ou implementação errada |
| Teste de aceitação só na fronteira do sistema | teste amarrado a interface interna devolve a fatia ao arquiteto toda hora |
| Fatia dimensionada por sessão (1–3 CAs), não "até 1 dia" | um dia de agente atravessa compactações e o fim não lembra o começo |
| CodeRabbit dentro do loop do programador, em fatia de risco | corrigir antes do handoff não custa volta; gate depois do build custa |
| QA ofensivo: ataca e entrega teste vermelho | parecer em prosa não é falsificável |
| Regras movidas para checagem do DSH | regra que depende de memória morre na primeira semana corrida |
| "3 voltas" → "o mesmo CA falhou 2× com consertos diferentes" | 3 voltas em CAs diferentes é progresso normal |
| Risco declarado na spec; path é segunda rede | PII e contrato não se detectam por caminho de arquivo |
| DESIGN/DECISOES em entradas curtas numeradas (D-001…) | o maior gasto de token é reler documento inteiro por sessão |

## Princípio

Chat é efêmero, arquivo é protocolo. E o que significa "pronto" é executável antes do código existir.

## Papéis

| Papel | Ferramenta | Produz | Nunca faz |
|---|---|---|---|
| Decisor | humano | rota, prioridade, merge | implementar |
| Arquiteto | Claude, sessão 1 | DESIGN, spec, tabela de CAs, testes de aceitação, esqueleto de fronteira | corpos de código de produção |
| Programador | Kimi | implementação, testes internos, correções | editar `tests/acceptance/`, ampliar escopo |
| Verificador | DSH | integridade, execução, sonda, gatilhos, métricas | editar código, decidir |
| Revisor mecânico | CodeRabbit | achados no diff, dentro do build | bloquear sozinho |
| QA | Claude, sessão 2 | ataques → testes vermelhos; parecer só para o não testável | editar código de produção |

## Definition of Ready — sem isto, o build não começa

- [ ] intenção em uma frase
- [ ] fora de escopo explícito
- [ ] fronteira testada declarada: HTTP, CLI, arquivo gerado ou `data-testid`
- [ ] tabela de CAs com ID, dado, quando, então — valores concretos, não adjetivos
- [ ] formatos: data, número, encoding, fuso, limite de volume
- [ ] risco declarado pelo arquiteto (PII, dinheiro, auth, contrato, migração)
- [ ] decisões pendentes listadas e bloqueando o build
- [ ] 3 a 5 passos manuais, só para o que a automação não vê
- [ ] cada CA mapeado a um teste com o ID no nome

## Ciclo

```
[0] intenção + rota           humano, 5 min
[1] spec + CAs + testes       arquiteto, 30 min
[2] portão 1                  humano aprova a TABELA; DSH confere rastreabilidade e hasheia
[2.5] perguntas               programador, 10 min (vazio = segue)
[3] build                     programador, 1 sessão, 1–3 CAs; CodeRabbit se risco
[4] verificação               DSH, 10 min → docs/QA/NNN.md
[5] portão 2                  humano, 15 min, roteiro da spec
[6] portão 3 (condicional)    QA ofensivo → testes vermelhos
[7] merge                     humano, 2 min; main verde; revert-first
```

Nenhum passo começa sem o artefato do anterior.

## Integridade do oráculo

Quatro camadas, cada uma cobrindo o buraco da outra:

1. **Hash no portão 1.** O DSH grava hash de `tests/acceptance/`, fixtures usadas, config do runner,
   script `test` do `package.json` e do mapa CA→teste. Divergência na verificação = vermelho, sem
   olhar o resultado dos testes.
2. **Comando próprio, árvore limpa.** O DSH roda a suíte de aceitação num worktree limpo, no commit
   declarado, com comando dele. Árvore suja = vermelho.
3. **Holdout.** 2 ou 3 CAs guardados fora do repositório (armazenamento do DSH), copiados só na
   verificação. Defesa contra implementação que reconhece os exemplos.
4. **Sonda independente.** Em fronteira HTTP, CLI ou arquivo, o DSH faz as próprias chamadas e
   confere bytes, sem usar código de teste do repositório.

Limites honestos: hash prova imutabilidade, não qualidade; holdout prova generalização, não intenção;
sonda prova comportamento na fronteira, não correção interna. Se a tabela de CAs e o teste estiverem
os dois errados, nada disso pega — o humano é a última linha.

## Contestação — o caminho oficial para "o teste está errado"

1. O programador para **naquele CA**, continua os outros, e registra em `docs/QA/NNN.md`: qual CA,
   por quê, com que evidência.
2. O arquiteto decide: ou a spec muda primeiro (regra 7) e o teste ganha novo hash aprovado, ou o
   programador estava errado.
3. Conta como volta de **spec**, não de build — alimenta a métrica certa.

## Portões por risco

| Gatilho | Dispara | Detecção |
|---|---|---|
| risco declarado na spec (PII, dinheiro, auth, contrato, migração) | CodeRabbit + QA | spec, com path como 2ª rede |
| > ~300 linhas ou > 8 arquivos | CodeRabbit | automática — se frequente, a fatia está mal cortada |
| dependência nova | CodeRabbit + QA | automática |
| "o humano não entendeu o diff" | QA | humana |
| diff pequeno, isolado, coberto | nada | — |

Divergência entre risco declarado e detecção por path gera flag — é sinal de spec incompleta.

## QA ofensivo (portão 3)

Recebe spec + app rodando. Tenta quebrar: dado vazio, valor extremo, encoding, concorrência,
permissão, repetição de requisição.

- Achado testável → teste vermelho em `tests/regression/`, que o DSH roda.
- "Nada encontrado" **só vale com o log de ataques tentados**.
- Achado não testável (cheiro de design, postura de segurança) → parecer em prosa, marcado como
  opinião, e não bloqueia sozinho.

## Triagem

| Achado | Natureza | Vai para |
|---|---|---|
| Código não faz o que a spec diz | bug | programador, com teste de regressão |
| Spec ambígua ou errada | spec | arquiteto; depois programador |
| Comportamento novo não pedido | escopo | humano decide e registra |
| Estilo, nome, comentário | cosmético | backlog |

## Caminho de falha

1. Achado vira item em `docs/QA/NNN.md`: esperado, obtido, passos, commit.
2. O programador escreve o teste de regressão em `tests/regression/`; o DSH prova o **vermelho no
   commit pai**.
3. O programador corrige, um commit.
4. O DSH reverifica e fecha o item.

O arquiteto só entra se o achado for de spec — o resto não sobe.

## Rotas

| Rota | Gatilho | Passos |
|---|---|---|
| rápida | ≤3 arquivos, sem contrato, sem dep nova | teste vermelho provado → programador → DSH → merge |
| normal | feature pequena | spec + CAs → portão 1 → programador → DSH → portão 2 |
| completa | risco declarado, contrato, dinheiro, PII, bug sem causa | ciclo inteiro, com CodeRabbit e QA ofensivo |

Quem escolhe a rota é o humano, no passo [0]. O DSH confere no fim se o diff coube na rota escolhida;
se estourou, reclassifica e avisa.

## Regras mecânicas (o DSH verifica)

| Regra | Checagem | Consequência |
|---|---|---|
| uma branch por fatia | prefixo `NNN-`; commit em main fora de merge = burla | flag no relatório |
| spec muda antes do código | commit em `SPECS/NNN` depois do 1º commit de código | flag |
| contrato antes do código | DSH prova o vermelho no commit do portão 1 | sem prova, não verifica |
| rota escolhida | diff final × limite da rota | reclassifica e avisa |
| oráculo íntegro | hash + worktree limpo | vermelho automático |
| métricas | uma linha por fatia em CSV | taxa de burla deixa de ser autodeclarada |

## Métricas

`docs/metricas.csv`, uma linha por fatia: rota, voltas, causa da volta (build/spec), tempo por etapa,
gatilhos, burla. Acima de ~30% de burla, o processo está caro.

## O que continua fraco

- Se o CA e o teste estiverem errados juntos, ninguém pega além do humano.
- Diversidade real de modelo só existe no [2.5]; se o programador concordar com tudo, não houve
  independência.
- As camadas de integridade custam tempo; em fatia muito pequena, a sonda pode custar mais que o
  build.
- CodeRabbit dentro do loop pode custar 7–30 min por execução; só compensa em fatia de risco.
