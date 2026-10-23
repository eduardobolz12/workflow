# O WORKFLOW — Guia completo de execução passo a passo

**Para:** você, o Decisor — a única pessoa que executa este guia com as próprias mãos.
**Promessa:** ao final deste documento, você sabe exatamente o que fazer em cada momento, o que
cada máquina faz sozinha, e onde estão seus quatro momentos de decisão.
**Como estudar:** leia inteiro uma vez. Depois execute acompanhando. Na terceira fatia, você já não
precisa mais dele — e é essa a meta.

---

## PARTE 0 — A VISÃO GERAL (leia até decorar estas cinco linhas)

```
Você decide O QUÊ  (passos 1, 2, 3, 5, 8)     →  quatro assinaturas por fatia
Claude desenha     (passos 1, 2, 3, 4)          →  arquiteto: planta, régua, sensor
Kimi constrói      (passo 6)                    →  pedreiro: liberdade interna, preso por fora
DSH verifica       (passos 5 e 7)               →  inspetor que desconfia de todos, inclusive de você
```

E as três leis que amarram tudo:

1. **Contrato antes do código** — a régua existe antes da parede.
2. **Toda falha volta um passo como teste falhando ou contestação escrita** — nunca como conversa.
3. **Toda transição passa por arquivo ou evidência** — nada existe porque alguém "disse".

**Seu investimento por fatia: ~30 minutos de decisão.** O resto do dia é debate (seu trabalho
intelectual), teste manual (suas mãos e olhos) e vida.

---

## PARTE 1 — OS QUATRO ATORES (quem é quem, em uma frase cada)

| Ator | É como se fosse | Faz | Nunca faz |
|---|---|---|---|
| **Você (Decisor)** | O dono da obra | Decide em 4 momentos; aprova; fecha | Implementa, revisa código |
| **Claude (arquiteto)** | O arquiteto | Passos 1–4: planta, régua, sensor | Código de produção |
| **Kimi (programador)** | O pedreiro | Passo 6: constrói | Toca na régua, no cofre, na spec |
| **DSH (verificador)** | O inspetor de obras + a câmera | Passos 5 e 7: tranca, prova, registra | Decide, escreve código, opina |

**Regra de ouro da divisão:** quem constrói não julga a própria obra; quem julga não constrói;
quem decide é o único que não participou da construção.

---

## PARTE 2 — PREPARAÇÃO (uma vez, antes da fatia 001)

O chão de fábrica. Sem isso, nada liga. Você faz com as próprias mãos ou delega a construção da
casca ao Kimi (com instrução escrita sua — é ambiente, não é fatia).

- [ ] **Repo fora do OneDrive**, dentro do workspace do DSH (o OneDrive corrompe o git)
- [ ] **`.gitignore`** contém: `.dsh/` e `docs/manifesto/`
- [ ] **Comando de teste com relatório legível**: `--junitxml` (pytest) ou `--reporter=json` (vitest)
- [ ] **`dsh.json`** no repo com `start_cmd` (como o app sobe) e `base_url` (onde ele escuta)
- [ ] **Casca do app** (antes da 001): sobe pelo comando oficial, escuta a porta, responde **404**
      para qualquer rota, sem comportamento nenhum. É isso que transforma "conexão recusada"
      (falha técnica, inútil) em "404 ≠ esperado" (falha certa, que mede o trabalho).
- [ ] **Configurações do Claude**: `.claude/settings.json` (identidade "Claude (arquiteto)",
      memória automática desligada, bloqueio de escrita nas pastas de produção), `CLAUDE.md`
      (contrato dele, <200 linhas)
- [ ] **Teste de fogo:** `dsh gate 001 --yes` roda de ponta a ponta num exemplo, e `dsh verify`
      recusa commit divergente e oráculo alterado.

**Quando terminar:** o ambiente está de pé e os três atores têm seus documentos (seu manual,
o contrato do Kimi, o manual do DSH, o CLAUDE.md do arquiteto).

---

## PARTE 3 — OS OITO PASSOS

*Cada passo segue o mesmo molde: para que serve → quem participa → tempo → o que fazer (numerado)
→ o que existe ao final → como saber que pode passar adiante → erros comuns.*

---

### PASSO 1 — Arquitetura Geral
**Para que serve:** decidir a casa antes de pedir tijolo. Acontece **uma vez por projeto** (ou por
serviço novo). Se você se pegar refazendo o passo 1 toda semana, algo escorregou.
**Quem:** você + Claude. **Tempo:** 1–2h.

**O que fazer:**
1. Abra o Claude Code no VSCode, dentro do repo, e explique: o problema, para quem, volume
   esperado, restrições (velocidade, dinheiro, regras do setor). Se for serviço dentro de um
   sistema existente, aponte os contratos com o que já existe.
2. Debata. A pergunta central de cada decisão não é "qual a tecnologia?" — é **"o que me faria
   mudar de ideia?"**.
3. Peça o `DESIGN.md`: decisões numeradas D-001, D-002…, cada uma com **o que foi decidido + a
   alternativa que perdeu + o gatilho de revisão** ("rever quando passar de 10 mil usuários").
4. Serviço do zero: confirme a regra — começa **monólito modular** (partes viram serviços só com
   evidência, depois).

**Ao final existe:** `DESIGN.md` v1.
**Pode passar adiante quando:** para cada decisão você sabe dizer o que a faria rever.
**Erros comuns:** decidir sem gatilho (vira dogma); discutir tecnologia antes de restrição;
escrever decisão sem a alternativa rejeitada (perde-se o porquê).

---

### PASSO 2 — Fatiamento
**Para que serve:** dividir a obra em entregas de um dia, na ordem certa. Acontece logo após o
passo 1, de preferência na mesma sentada.
**Quem:** você + Claude. **Tempo:** 30–60 min.

**O que fazer:**
1. Peça o mapa de fatias: nomeadas (001, 002, 003…), cada uma com **2–3 critérios** (as linhas da
   tabela do passo 3).
2. Confira a **ordem — escrita antes de leitura**: toda fatia que lê dados depende de uma anterior
   que escreve esses dados. Dependência invertida = retrabalho garantido.
3. Confirme que a **fatia 001 é a walking skeleton**: a mais fina possível que atravessa tudo
   (tela → API → banco → deploy) com quase nenhuma funcionalidade. O trabalho dela é provar que a
   arquitetura funciona de verdade — e ela às vezes descobre que não funciona, o que é a utilidade
   dela.
4. Aprove o mapa e a fatia 001. **Esta é sua primeira assinatura.**

**Ao final existe:** `docs/MAPA.md` (uma linha por fatia: número · nome · depende de · como se
sabe que ficou pronta) + a fatia 001 escolhida com 2 CAs.
**Pode passar adiante quando:** para cada fatia você consegue responder "como se sabe que ficou
pronta?".
**Erros comuns:** fatia grande demais (estoura o dia e compacta o contexto do Kimi); mapa sem
ordem de dependência; pular a walking skeleton "para ir mais rápido" (vai mais devagar).

---

### PASSO 3 — Spec da fatia
**Para que serve:** escrever a régua em português — o que significa "pronto" para ESTA fatia, com
exemplos tão concretos que não sobra espaço para interpretação. É o passo que mais vale seu
tempo: 10 minutos aqui economizam o dia inteiro do passo 6.
**Quem:** Claude escreve → você aprova. **Tempo:** ~25 min (15 do Claude + 10 seus).

**O que fazer:**
1. **Claude escreve `docs/SPECS/NNN.md`** com todas as seções: intenção (1 frase, quem usa) ·
   fronteira testada (rota/comando/arquivo exatos) · fora de escopo (bullets negativos) ·
   **tabela de CAs** (2–3 linhas: ID | Dado | Quando | Então, valores concretos) · formatos
   (data, número, encoding, fuso, limite) · risco declarado · como rodar os testes (comando,
   porta) · arquivos que serão tocados (previsão, não contrato) · um arquivo-exemplo · 3 passos
   de teste manual · decisões pendentes (se houver, a fatia NÃO começa).
2. **Você aprova os exemplos da tabela** (~10 min). Seus três checks:
   - cada critério tem valores concretos (nunca "dados válidos");
   - cada resultado é verificável (nunca "fica bom");
   - formatos definidos (o que acontece com vazio, limite, maiúsculas).
   Você lê **exemplos, não código**. Aprovou, trava; contestou, volta ao Claude.

**Ao final existe:** spec aprovada + tabela travada.
**Pode passar adiante quando:** os três checks passam e a seção "decisões pendentes" está vazia.
**Erros comuns:** aprovar no automático (é o modo de falha nº 1 do processo inteiro); deixar
"pendência" escondida na conversa em vez de escrita na spec; deixar o Claude escrever critérios
sem valores ("busca retorna os resultados certos" — certos como?).

---

### PASSO 4 — Testes vermelhos
**Para que serve:** converter a régua em **perguntas de sim/não que a máquem faz sozinha** — o
sensor. A partir daqui, "pronto" deixa de ser opinião.
**Quem:** Claude sozinho. **Tempo:** ~15 min. **Você: nada.**

**O que acontece (você só fiscaliza o resultado):**
1. Claude escreve em `tests/acceptance/NNN/` um teste por CA — o **nome contém o ID**
   (`CA-1` → `test_CA1...`), sem isso o gate reprova.
2. Regras que ele deve seguir (estão no CLAUDE.md dele): só na fronteira (HTTP real, comando,
   arquivo — zero import de código interno); transporte real (a app sobe e o teste fala com ela
   de fora); valores copiados da tabela, nem mais nem menos; ingredientes (fixtures) em arquivos
   reais dentro da pasta; **zero código de produção junto**.
3. Estado exigido: **100% falhando** — e falhando pelo motivo certo (o comportamento não existe;
   a casca do app responde 404 e o teste esperava outra coisa). Falha técnica (import, conexão,
   ingrediente errado) volta ao Claude.

**Ao final existe:** pasta de testes vermelha.
**Pode passar adiante quando:** todo CA tem teste com ID no nome; tudo falha pelo motivo certo.
**Erros comuns:** teste que já nasce verde (reprova o gate — sensor que não dispara não mede nada);
teste que fala com o código por dentro (prende a obra na estrutura); ingrediente inventado em vez
de arquivo real.

---

### PASSO 5 — GATE
**Para que serve:** trancar a régua no cofre e dar o **"pode construir"**. O único portão que não
se negocia nunca.
**Quem:** DSH executa → você aprova. **Tempo:** ~10 min.

**O que acontece:**
1. **DSH confere rastreabilidade:** todo CA da tabela tem teste com ID; nenhum ID órfão.
2. **DSH prova o vermelho:** roda a suíte com o comando dele e exige 100% de falha.
3. **DSH grava o manifesto:** a impressão digital de testes, ingredientes, spec e configuração.
   A partir daqui, qualquer byte alterado = alarme, antes de qualquer resultado.
4. **Você vê a tela:** cada CA com a linha da tabela **e o código do teste ao lado**. Confere uma
   coisa só: a pergunta tem a mesma força da promessa? ("só" virou "exatamente igual" e não "está
   contido"?). Aperta `s`.
5. Manifesto gravado **depois** da sua aprovação — gate rejeitado não deixa estado pendurado.

**Ao final existe:** contrato trancado + vermelho provado + sua segunda assinatura.
**Pode passar adiante quando:** hash gravado + vermelho provado + seu `s`.
**Erros comuns:** aprovar sem ler (o portão vira carimbo — e carimbo silencioso é a pior doença do
processo); discutir código na tela do gate (a tela é para comparar frase com pergunta, não para
revisar programa).

---

### PASSO 6 — Construção
**Para que serve:** a única etapa de "como". O Kimi implementa com liberdade total dentro da
parede e zero liberdade fora dela.
**Quem:** Kimi. **Tempo:** o grosso do dia (4–5h). **Você: nada. Saia.**

**O que acontece (para você saber o que esperar):**
1. Kimi lê spec + testes, abre a branch `feat/NNN-slug`.
2. Implementa CA por CA, com testes internos próprios (a régua de bancada dele — não é o oráculo).
3. Proibições dele (contrato lite): não tocar em testes/ingredientes/spec/cofre; não refatorar
   arquivo vizinho; não ampliar escopo; não "ajustar a pergunta para a resposta"; não ramificar
   comportamento por ambiente; não commitar em main; não commitar `.dsh/` nem `docs/manifesto/`.
4. Entrega: aceitação verde **na máquina dele** → escreve `docs/QA/NNN.md` (**sem commitar**) com
   `commit: <sha>`, `resultado: verde`, comando e saída completos. Commita só código.

**Ao final existe:** código + arquivo de entrega com prova.
**Pode passar adiante quando:** o DoD dele está completo (CAs passando, testes internos, árvore
limpa, QA fora do commit).
**Seu papel aqui:** nenhum. Se você sentir vontade de "só dar uma olhada no código", lembre: sua
olhada é o aceite do passo 8, e ela vale porque vem depois da prova, não antes.

---

### PASSO 7 — Prova
**Para que serve:** a perícia. O DSH não confia na palavra do pedreiro — refaz tudo do jeito dele.
**Quem:** DSH sozinho (+ CodeRabbit e QA ofensivo, **só se a fatia for de risco**: login, dinheiro,
dado de cliente, contrato público, migration, dependência nova). **Tempo:** ~10 min. **Você: nada.**

**O que acontece:**
1. Commit conferido: o `commit:` declarado é o HEAD da branch.
2. Cópia limpa do cômodo (worktree) — nada de "na minha máquina funcionava".
3. **Cofre antes de tudo:** manifesto íntegro? Qualquer diferença = `oráculo adulterado`, falha
   imediata, sem nem olhar resultado.
4. App de verdade sobe (modo produção) e a suíte roda com o comando do DSH.
5. Comparação: verde×verde no mesmo commit = confirmado · vermelho do DSH × verde declarado no
   mesmo commit = **divergência de ambiente** (volta ao Kimi, não conta como volta) · vermelho nos
   dois = falha real (conta).
6. Suíte antiga roda: teste antigo vermelho = a fatia derrubou parede velha.
7. Tudo gravado em evidência.

**Se for de risco, em paralelo:** CodeRabbit lê o diff (Kimi corrige ou registra motivo — nunca
rejeita; acima de ~5 achados, você decide o **padrão**, não item a item). QA ofensivo do Claude
tenta quebrar o sistema e entrega um teste vermelho ou "nada encontrado".

**Ao final existe:** veredito — verde com evidência, ou vermelho com teste falhando anexado.
**Erros comuns:** tratar falso vermelho do DSH como defeito do Kimi (pode ser ambiente — a tabela
de comparação existe justo para isso); deixar o app de pé depois da prova (o DSH mata o processo).
**Intermitente (flake):** se uma falha some na segunda execução, registra-se "flake" com o nome do
teste — não se conserta o que não se entendeu.

---

### PASSO 8 — Aceite
**Para que serve:** você pega no produto com as próprias mãos e fecha a fatia. O único passo em
que a máquina não substitui você.
**Quem:** você. **Tempo:** ~15 min.

**O que fazer:**
1. **Roteiro manual** (os 3 passos da spec): use o produto de verdade. Não lê código, não lê
   relatório — usa. É aqui que se pega o que todas as máquinas passaram: o Excel que abre
   estranho, o contador que não bate, o acento que "estava no teste mas não na tela".
2. **Contestações abertas** (se o Kimi contestou algo): você decide, com a tabela na frente. A
   spec muda **antes** do código — nunca o contrário.
3. **Merge** (história esmagada em um commit por fatia) + o DSH grava a linha no `metricas.csv`.

**Ao final existe:** fatia mergeada + uma linha na planilha-mãe + os testes dela trancados no
cofre para sempre (se daqui a seis meses alguém quebrar essa funcionalidade, o alarme dispara).

**Pode recomeçar quando:** você escolhe a próxima fatia do mapa e volta ao passo 3.
**Erros comuns:** executar o roteiro de cabeça em vez de na tela; "deixar para testar depois"
(não há depois — o aceite É o depois); consertar na mão o que falhou (registra e vira CA novo).

---

## PARTE 4 — O QUE FAZER QUANDO ALGO DÁ ERRADO (plano de bolso)

| Situação | Quem age | O que acontece |
|---|---|---|
| Defeito encontrado no aceite | você registra → Claude vira teste vermelho → Kimi conserta | o defeito nunca mais volta disfarçado |
| Teste quebrado descoberto no build | Kimi contesta → você decide → Claude corrige → novo gate | barato, porque é cedo |
| Spec ambígua no meio do build | Kimi registra e segue os outros CAs; você decide no próximo portão | a fatia nunca trava inteira por uma linha |
| Caso faltante descoberto no build | Kimi registra proposta, não implementa | nasce como CA novo na próxima spec |
| Achado do CodeRabbit | Kimi corrige ou registra motivo; você decide o padrão se > 5 | ninguém rejeita crítica do próprio código |
| Vermelho do DSH × verde do Kimi | divergência de ambiente: volta ao Kimi sem contar volta | não se pune por ambiente |
| Falha intermitente | rodar duas vezes; sumiu = "flake" registrado com nome do teste | não se conserta o que não se entendeu |
| Alguém furou o fluxo ("só dessa vez") | registra como burla no CSV | burla registrada é dado; burla escondida é corrupção |

**A frase que resolve 90% dos casos:** *qualquer falha volta um passo, como teste falhando ou
contestação escrita — nunca como conversa, nunca pulando etapa.*

---

## PARTE 5 — SUAS QUATRO DECISÕES (imprima isto)

| # | Quando | O que você decide | Tempo | Se falhar |
|---|---|---|---|---|
| 1 | Passos 1–2 | arquitetura + mapa de fatias | 1–2h | obra inteira torta |
| 2 | Passo 3 | os exemplos da tabela | ~10 min | "não era isso que eu pedi" |
| 3 | Passo 5 | o gate (frase × pergunta) | ~5 min | régua fraca passa, defeito grave escapa |
| 4 | Passo 8 | aceite manual + merge | ~15 min | defeito vai para produção |

Fora desses quatro momentos, você não trabalha no processo — trabalha **no produto** (debate,
teste manual, próxima ideia) ou não trabalha.

---

## PARTE 6 — AS CINCO REGRAS DURAS (as que não se negociam)

1. Teste vermelho **antes** do código.
2. Kimi não edita spec nem testes — **contesta**.
3. Bug conhecido vai ao Kimi **com teste**, nunca ao arquiteto.
4. Nada é "pronto" sem comando e saída.
5. CR e QA **só por risco** — nunca "quando o app estiver pronto".

---

## PARTE 7 — A PLANILHA QUE MANDA (`metricas.csv`)

Uma linha por fatia, escrita **só pelo DSH**: fatia · rota · CAs · voltas · tempo · gatilhos ·
contestações · defeitos que escaparam · burla · observação.

**Ela é o cérebro de longo prazo porque:**
- todo defeito que escapa vira linha `defeito, fatia, mecanismo_que_teria_pegado` — e só isso
  faz mecanismo congelado voltar (regra do aluguel: sem linha, não volta);
- burla acima de ~30% = processo caro demais → corta **passo**, não regra;
- a revisão das 10 fatias decide tudo com esses números na mesa — zero opinião, zero memória.

---

## PARTE 8 — UM DIA TIPO (para calibrar expectativa)

| Hora | O que acontece | Quem |
|---|---|---|
| 09:00 | debate da fatia + spec (passo 3) | você + Claude |
| 09:25 | você aprova a tabela | você |
| 09:30 | testes vermelhos (passo 4) | Claude |
| 09:45 | **gate** — cofre, vermelho, sua tela | DSH + você |
| 10:00 | **construção** (passo 6) | Kimi — você sai |
| 15:00 | **prova** (passo 7) | DSH (+CR/QA se risco) |
| 16:00 | **aceite**: 3 passos manuais + merge | você |
| 16:20 | linha no CSV; próxima fatia amanhã | DSH |

**1–2 fatias por dia.** Sua presença obrigatória: ~30 min. O resto é debate, uso do produto e vida.

---

## PARTE 9 — GLOSSÁRIO MÍNIMO (cinco palavras e você fala o idioma)

- **CA** (critério de aceite): uma linha da tabela — Dado, Quando, Então. A menor unidade de
  "pronto".
- **Vermelho / verde:** falhou / passou (as cores que o teste mostra na tela).
- **Fixture:** os ingredientes medidos em potinhos — dados de exemplo em arquivo real.
- **Manifesto:** a impressão digital dos arquivos de contrato; se muda um byte, o alarme dispara.
- **Gate:** o portão entre "decidido" e "construir" — cofre trancado + seu "pode".

---

## PARTE 10 — FOLHA DE BOLSO (imprima, dobre, deixe na tela)

```
PRÉ:  repo fora do OneDrive · .gitignore · --junitxml · dsh.json · casca 404

1 ARQUITETURA   debate com Claude → DESIGN.md (cada decisão: o que, alternativa, GATILHO)
2 FATIAMENTO    mapa ordenado (escrita antes de leitura) → 001 = walking skeleton, 2 CAs
3 SPEC          Claude escreve → VOCÊ aprova os EXEMPLOS (valores concretos, formato, fora de escopo)
4 TESTES        Claude → 1 teste por CA, nome com ID, só fronteira, TODOS FALHANDO certo
5 GATE          DSH: rastreio + vermelho + cofre → VOCÊ compara frase × pergunta → [s]
6 CONSTRUÇÃO    Kimi sozinho · você sai
7 PROVA         DSH: commit + cópia limpa + cofre + app real + suíte antiga
                (risco? CR + QA atacam em paralelo)
8 ACEITE        VOCÊ: 3 passos na tela → merge → CSV

LEI 1: contrato antes do código
LEI 2: falha volta um passo como teste vermelho — nunca como conversa
LEI 3: toda transição é arquivo ou evidência

VOCÊ DECIDE 4×: arquitetura · tabela · gate · aceite
O RESTO: máquina
```

---

*Fim do guia. Quando você executar a terceira fatia sem abrir este documento, ele cumpriu o papel —
e o `metricas.csv` já estará mandando mais do que qualquer PDF.*
