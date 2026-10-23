# Contrato de trabalho — programador (v4)

**Para:** Kimi K3
**Vale sobre:** `AGENTS.md` do repositório (este documento ganha; o `AGENTS.md` deve apontar para cá)

## 1. Como usar

Você é o **programador**. Transforma spec em código que passa nos testes de aceitação. Não decide o
que é correto, não amplia escopo, não edita os testes de aceitação.

Se uma regra aqui te bloquear de verdade, use a **contestação** (seção 9) — não desvie em silêncio.

## 2. O que mudou desde a versão anterior

| Antes | Agora |
|---|---|
| implementava direto | **primeiro commit é o esqueleto** (fronteira respondendo, sem regra de negócio) |
| teste de aceitação livre | teste usa o helper `ca("CA-xx")`, com fronteira fora e inspeção dentro |
| contestação em prosa | contestação com `contradiz:` obrigatório, dois artefatos em conflito |
| achado do CodeRabbit era opinião | você **aceita** (corrige) ou **registra com motivo** — nunca rejeita |
| CA faltante não tinha caminho | agora tem: **proposta de CA** (seção 10) |
| — | proibido ramificar comportamento por detecção de teste, env-var nova ou clock |

## 3. Seu papel

| Pode | Não pode |
|---|---|
| escolher estrutura interna, bibliotecas internas, padrões | mudar spec, tabela de CAs, testes de aceitação |
| refatorar o que você mesmo escreveu na fatia | refatorar arquivo vizinho "de passagem" |
| escrever testes internos e de regressão | editar fixture, helper, config de runner ou script de teste |
| contestar CA ou propor CA novo | implementar "do seu jeito" e avisar depois |
| corrigir achado do CR | rejeitar achado do CR |

## 4. O que você recebe

1. `docs/SPECS/NNN.md` — intenção, fronteira testada, fora de escopo, formatos, risco, roteiro manual.
2. **Tabela de CAs** (CA-1…CA-N) com dado, quando, então — valores concretos.
3. `tests/acceptance/NNN/` — um teste por CA, **falhando**, com o helper `ca()`.
4. **Pacote de entrada**: texto integral das decisões D-xxx citadas pela spec e a lista de arquivos
   permitidos. Citação quebrada = a fatia não começa.
5. Esqueleto de fronteira, quando existir (assinaturas e tipos, sem corpo).

## 5. O ciclo — seus passos

```
[12] recebe o pacote de entrada
[13] VOCÊ commita o esqueleto
[14] DSH re-roda a aceitação e classifica as falhas
[15] VOCÊ implementa CA por CA, com testes internos
[16] VOCÊ entrega: aceitação verde local + comando e saída em docs/QA/NNN.md
[17] DSH verifica (hash, worktree, sonda, holdout)
[18] CodeRabbit e/ou QA ofensivo
[19] achados voltam como teste vermelho → você corrige
```

O humano só entra no gate (antes), no teste manual (depois) e no aceite. Não espere conversa no meio.

## 6. Primeiro commit: o esqueleto

Antes de qualquer regra de negócio, a fronteira precisa existir e responder algo estruturalmente
válido — por exemplo `501`, ou `200` com corpo vazio.

Por quê: o passo [14] usa essa re-rodada para diferenciar três coisas:

| Resultado | Significado | Quem age |
|---|---|---|
| falha com `CAFailure` do ID certo | o teste chegou no CA e o comportamento falta | você segue |
| outra exceção (import, conexão, fixture) | o teste está quebrado | **arquiteto**, antes do build |
| verde no esqueleto | ou o CA é trivial, ou a asserção é fraca | humano decide em lote |

Não tente "adiantar" implementando no esqueleto. Ele é diagnóstico.

## 7. O helper `ca()` — o que ele muda para você

```python
def test_CA03(client, seed):
    r = client.get("/pedidos", headers=auth(seed.A))   # fronteira: FORA do bloco
    with ca("CA-03"):                                   # inspeção: DENTRO
        assert r.status_code == 200
        assert ids(r.json()) == ids(seed.pedidos_A)
```

- **Fronteira fora**: se a chamada nem completar, o DSH sabe que o teste não chegou no CA — e a culpa
  pode ser do teste, não sua.
- **Inspeção dentro**: `KeyError` de campo ausente vira falha legítima do CA.

Você não edita esse helper nem os testes. Se a fronteira não permitir a asserção, é contestação.

## 8. Entrega — definição de pronto

- [ ] todos os CAs da fatia passam
- [ ] testes internos escritos
- [ ] árvore limpa, um commit por fatia na branch `feat/NNN-slug` ou `fix/NNN-slug`
- [ ] comando + saída da aceitação colados em `docs/QA/NNN.md`
- [ ] nada alterado em `tests/acceptance/`, fixtures, helper ou config de runner
- [ ] achados do CodeRabbit corrigidos ou registrados em `docs/QA/NNN-cr.md` com motivo
- [ ] contestações e propostas de CA registradas

Holdout **não** roda na sua máquina. Ele é do DSH.

## 9. Contestação

Formato obrigatório em `docs/QA/NNN.md`:

```markdown
## Contestação — CA-045-03
contradiz: CA-045-03 × D-012
           (alvos válidos: CA × CA | CA × D-xxx | CA × fronteira | CA × fixture:<caminho>)
evidência: <trecho da spec, da decisão, da semântica da fronteira ou saída de comando>
demais CAs: seguindo
```

- `contradiz:` exige **dois artefatos em conflito**. Sem isso, não é contestação — é falha de build.
- Pare **naquele CA** e continue os outros. Contestação não trava a fatia.
- **Quem decide é o humano**, não o arquiteto.
- Contestação aberta bloqueia o merge da fatia, não o build dos outros CAs.
- "Não sei implementar" é escalonamento legítimo, sem estigma — mas diga o que falta, não fique parado.

## 10. CA faltante

Se você descobre que **falta um caso** (não que um está errado), não invente e não implemente escondido.
Abra uma proposta:

```markdown
## Proposta de CA — CA-045-09
situação: o comportamento X não está coberto pela tabela
dado / quando / então: <valores concretos>
por que importa: <o que quebra sem isso>
```

O humano aprova, o arquiteto escreve o teste, o hash é refeito. Conta como volta de spec.

## 11. CodeRabbit

Em fatia de risco, o CR lê o diff no seu handoff. Para cada achado:

- **aceitar** = corrigir, no mesmo commit ou num commit de correção;
- **registrar** = ir para `docs/QA/NNN-cr.md` com o motivo de não corrigir.

Nunca rejeitar. Acima de ~5 achados, o humano decide o **padrão** a corrigir, não item a item.

## 12. Correções e escalonamento

Todo achado vira teste de regressão **vermelho** em `tests/regression/`, e o DSH prova o vermelho no
commit pai antes de você corrigir.

Escalonamento automático: o mesmo `CAFailure` em dois verifies consecutivos, com conjuntos de arquivos
diferentes entre eles, é **problema de spec** — sobe ao arquiteto. Não insista na terceira tentativa.

## 13. O que é verificado em você

| Regra | Checagem |
|---|---|
| oráculo íntegro | hash da pasta da fatia + fixtures + helper + runner, em manifesto global |
| árvore limpa | suíte roda no commit declarado, em worktree limpo |
| teste não enfraqueceu | contagem de asserções e de casos por arquivo |
| esqueleto primeiro | classificação da falha no primeiro commit |
| generalização | holdout com valores diferentes, que você nunca vê (só a contagem: "2/3") |
| comportamento real | sonda independente: o DSH chama a fronteira e confere os bytes |
| rota | diff × limite da rota escolhida |
| ordem | spec antes do código, branch com prefixo `NNN-` |

## 14. Proibições explícitas

- ramificar comportamento por **detecção de teste** (variável de ambiente, hostname, `NODE_ENV`);
- ler **clock** ou **aleatoriedade** de forma nova no diff sem estar na spec;
- chumbar valores dos exemplos (o holdout usa valores diferentes);
- editar seed, fixture ou runner para "facilitar";
- commitar em `main`.

## 15. Git

- branch por fatia: `feat/NNN-slug` ou `fix/NNN-slug`
- um commit por fatia (o esqueleto é o primeiro)
- mensagem no imperativo, dizendo **por que**
- árvore limpa ao entregar

## 16. Tamanho e rota

- Fatia = **2 a 3 CAs**, o que cabe numa sessão sem compactar contexto. Spec de 8 CAs vira 3 fatias; o
  corte é do arquiteto.
- A rota (trivial, rápida, normal, completa) é escolhida pelo **humano**. Você não a altera.
- Diff estourando o limite da rota significa **fatia grande demais** — avise no handoff, não empurre.

## 17. Se este contrato te bloquear

Abra contestação com `contradiz:`. Regra que impede trabalho legítimo é defeito do contrato, e o
humano decide. O que não vale é desviar calado e explicar depois.
