# Playbook — 3 agentes: Harness (executa), Claude (arquiteta + QA), Kimi K3 (programa)

Regra fundadora: **chat é efêmero, arquivo é protocolo.** Os três agentes não conversam entre si;
eles leem e escrevem os mesmos artefatos. Se a informação só existe na conversa, ela morre quando a
sessão fecha — e o próximo agente desfaz o trabalho do anterior.

---

## 1. Papéis

| Papel | Ferramenta | Decide | Produz | Nunca faz |
|---|---|---|---|---|
| Decisor | **você** | escopo, trade-off, "pronto" | aprovação, merge | escrever spec no lugar do arquiteto |
| Arquiteto | **Claude** | desenho técnico, critérios de aceite | `docs/SPECS/*.md`, parecer de QA | implementar (quando no papel de arquiteto) |
| Programador | **Kimi K3** | como codar dentro da spec | código, testes, commit | decidir arquitetura ou ampliar escopo |
| Verificador | **DSH (eu)** | nada | evidência: comandos, saídas, diff, falhas | prosa criativa, decisão de produto |

O verificador existe porque **QA sem execução é opinião**. Claude revisa o mérito; eu provo o fato.

## 2. O ciclo (um ciclo = uma tarefa)

```
  [1] SPEC            [2] BUILD           [3] VERIFY          [4] QA            [5] MERGE
  Claude escreve  →   Kimi implementa  →  DSH executa     →  Claude revisa →   você
  docs/SPECS/NNN.md   branch + testes     docs/QA/NNN.md     diff x spec       main
```

Artefato de cada fronteira:

| Passo | Artefato | Critério para avançar |
|---|---|---|
| 1 | `docs/SPECS/NNN-nome.md` | você aprovou (leu, não "achou ok") |
| 2 | branch `feat/NNN-nome` + commit + testes | Kimi roda os testes e cola a saída |
| 3 | `docs/QA/NNN-verificacao.md` | critérios de aceite um por um: passou / falhou / não testado |
| 4 | parecer no mesmo arquivo | aprovado, ou lista priorizada `arquivo:linha` |
| 5 | merge + `docs/DECISOES.md` | decisão registrada em arquivo |

## 3. Templates (copiar e colar)

### 3.1 Claude como arquiteto

```
Papel: arquiteto. Não escreva código nesta rodada.
Repositório: <caminho>  Branch: main
Objetivo: <uma frase, resultado observável>
Contexto que importa: <arquivos que ele PRECISA ler, não o repo inteiro>
Restrições: <não mudar API X; não instalar dependência; Python 3.12>

Entregue docs/SPECS/NNN-<nome>.md com:
1. Comportamento esperado — entrada e saída exatas (exemplo real, não descrição)
2. Casos de borda numerados (o que acontece em cada um)
3. O que NÃO pode mudar (contrato existente)
4. Critérios de aceite — cada um verificável por um comando concreto
5. A menor fatia que já entrega valor
6. 3 riscos, com o sinal que indicaria que o risco se materializou

Pergunte só o que for bloqueante. Suposições vão marcadas como SUPOSIÇÃO no topo.
```

### 3.2 Kimi K3 como programador

```
Implemente docs/SPECS/NNN-<nome>.md no repositório <caminho>.
Regras:
- Só o que a spec pede. Não refatore arquivo vizinho, não "melhore" código de fora.
- Um commit por fatia da spec, mensagem no imperativo.
- Antes de dizer pronto: rode <comando de teste> e cole a saída.
- Spec ambígua = pare e pergunte. Não invente requisito.
- Não toque em: <arquivos proibidos> (ex.: migrations, decisoes.md, dados de entrada)
```

### 3.3 DSH como verificador

```
Verifique docs/SPECS/NNN-<nome>.md contra a branch <x>.
- Rode: <comandos de teste/build>
- Para cada critério de aceite: passou / falhou / não testado (com o comando usado)
- Liste (a) o que a spec pediu e não foi feito, (b) o que foi feito sem a spec pedir
- Mostre o diff resumido por arquivo
- Não edite nada nesta rodada
Saída: docs/QA/NNN-verificacao.md + resumo em 5 linhas
```

### 3.4 Claude como QA

```
Revise o diff da branch <x> contra docs/SPECS/NNN.md e docs/QA/NNN-verificacao.md.
Aponte apenas: (a) desvio da spec, (b) risco de regressão no que já funcionava,
(c) caso de borda sem teste.
Não reescreva o código. Devolva lista priorizada (bloqueante / importante / cosmético),
cada item com arquivo:linha e o motivo.
Se não houver achado bloqueante, diga "aprovado" explicitamente.
```

## 4. As cinco regras de convivência

1. **Um escritor por vez na árvore.** Kimi editando + Claude editando + eu rodando = três versões da verdade.
   Quem não está no papel de escritor fica em leitura.
2. **Uma branch por tarefa**, nunca por ferramenta. `git switch -c feat/NNN`. Merge só após parecer.
3. **A spec é a única fonte de verdade.** Se durante a implementação a spec se mostrar errada,
   a spec muda primeiro (Claude), depois o código. Não o contrário.
4. **Nada é "pronto" sem prova.** Teste automatizado quando existe; senão, evidência de execução
   (comando + saída). "Deve funcionar" não conta.
5. **Decisão sem registro é decisão perdida.** Toda escolha de rumo vai para `docs/DECISOES.md`
   com data e motivo. É o que impede o agente seguinte de reabrir o que você já decidiu.

## 5. Roteamento — quando NÃO usar o ciclo completo

| Situação | Faça | Custo |
|---|---|---|
| typo, rename, 1 linha | Kimi direto, sem spec | minutos |
| bug com teste que falha | você → Kimi (reproduzir) → eu (verificar) | 1 ciclo curto |
| funcionalidade nova | ciclo completo | horas |
| decisão de arquitetura | Claude + spec, sem código | 1 sessão |
| auditoria de código existente | Claude lê + eu executo | 1 sessão |
| conteúdo editorial (roteiros) | **fora deste ciclo** (ver seção 7) | — |

## 6. Onde cada um falha (para você me usar direito)

- **Kimi:** refatora além do pedido, e sem testes não tem freio. Sempre que ele tocar código
  sem rede de proteção, o primeiro item do backlog é criar a rede.
- **Claude (arquiteto/QA):** excelente em mérito e coerência; ruim em fato não lido. QA sem fonte
  vira opinião — por isso o seu pipeline usa `livro.py trecho` e `conferir`.
- **Eu (harness):** executo, meço, comparo. **Não instalo pacote** (meu shell não tem HTTPS),
  não decido produto e não escrevo prosa criativa no seu padrão editorial.

## 7. Exceção: o projeto de roteiros

O `roteiros-youtube` não é software; é produção editorial. Aplicar o ciclo de 3 agentes na escrita
de capítulos troca voz por velocidade. Ali o desenho correto é:

- **DSH:** `livro.py` (converter, trecho, conferir, contar, validar-indice), integridade de arquivos, git.
- **Claude:** todo o pipeline editorial (13 etapas) como está hoje.
- **Kimi:** só a engenharia de apoio — testes do `livro.py`, conversores, scripts de conferência.

## 8. Ritual de sessão

**Início (2 min):**
1. `git status` — árvore limpa? Se não, o que está pendente é seu primeiro assunto.
2. Leia a spec ou o status atual (`docs/SPECS/` ou `ficha.md` do tema).
3. Diga ao agente o papel e o alvo, em uma frase.

**Fim (2 min):**
1. Rode o comando de verificação e guarde a saída.
2. Atualize o artefato (spec, `docs/QA/`, `decisoes.md`).
3. Commit com mensagem que diga *por que*, não *o que*.

## 9. Primeira tarefa de calibração (recomendada)

Alvo: `ferramentas/livro.py` (103 KB, 20 subcomandos, **zero testes**).

| Passo | Quem | Entrega |
|---|---|---|
| 1 | Claude | `docs/SPECS/001-testes-livro.md`: o que testar, entradas fixas, saídas esperadas |
| 2 | Kimi | `ferramentas/test_livro.py` cobrindo `trecho`, `contar`, `validar-indice` |
| 3 | DSH | roda os testes, mede cobertura dos subcomandos, relatório |
| 4 | Claude | QA contra a spec |

Resultado: uma rede de proteção antes de qualquer refatoração — e os três calibrados com risco baixo.
