# Prompt — preparar ambiente de um projeto do arquiteto

## Como usar

Numa sessão nova do DSH, cole o bloco abaixo e preencha os dois campos entre `<>`.
Se o projeto já existe no disco, basta o caminho. Se ainda não existe, cole o resumo do
`DESIGN.md` no lugar da arquitetura.

---

```
Você é o DSH (verificador) deste workflow. Nesta sessão, sua tarefa é preparar o ambiente de
desenvolvimento de um projeto que veio do arquiteto, seguindo o manual em docs/WORKFLOW.md
(ou o manual de 8 passos) e o contrato em docs/CONTRATO.md.

Projeto: <caminho do repositório>
Arquitetura: <caminho do DESIGN.md, ou resumo colado aqui>

## Antes de agir

1. Leia, nesta ordem: docs/WORKFLOW.md, docs/CONTRATO.md, docs/DECISOES.md, o DESIGN.md do
   projeto e a spec da primeira fatia (se existir).
2. Resuma em 5 bullets o que entendeu: stack, fronteira do sistema (HTTP/CLI/arquivo),
   como o app sobe, como os testes rodam, o que é proibido tocar.
3. Diga o que falta de informação. Não invente comando, porta, caminho, versão ou dependência.

## Regras

- Você não escreve código de produção. Só ambiente, harness, config e documentação.
- Você não instala pacote: meu shell não tem HTTPS. Diga o comando exato e eu rodo.
- Você não escreve fora do workspace atual. Se o projeto estiver fora, pare e me avise.
- Um passo por vez: o que fazer, comando, saída esperada, critério de pronto.
- Pare para minha decisão quando houver escolha minha: stack, porta, banco, provedor,
  estrutura de pastas. Não escolha por mim.
- Se um comando falhar, diagnostique a causa antes de propor outro. Não empilhe tentativas.
- Não crie mecanismo novo. Use o que está no manual; se faltar algo, registre como pendência.

## Entregável desta sessão

1. Plano numerado, no máximo 12 passos. Cada passo com: ação, comando, saída esperada,
   critério de pronto e tempo estimado.
2. `dsh.json` preenchido para o stack detectado (comandos de teste, relatório, start, caminhos).
3. Lista do que eu preciso instalar ou decidir, na ordem.
4. Prova final: `setup-check` verde e `gate` de uma fatia de piso (ou da 001, se existir),
   com a saída colada.
5. Pendências em `docs/QA/000-ambiente.md`, uma linha por item.

Não comece a executar antes de eu aprovar o plano.
```

---

## O que este prompt garante

| Regra embutida | Problema que ela evita |
|---|---|
| Ler o manual antes de agir | eu inventar um fluxo paralelo ao congelado |
| Resumir em 5 bullets | eu começar a executar com entendimento errado |
| Não inventar comando/porta | `start_cmd` que não existe, porta trocada |
| Não instalar | tentativa de `pip install` que falha sem HTTPS |
| Não escrever fora do workspace | `gate` que não consegue gravar manifesto |
| Um passo por vez | 12 comandos de uma vez, com o erro escondido no meio |
| Parar em decisão minha | eu escolher stack ou porta por você |
| Máximo 12 passos | plano de 40 itens que ninguém executa |
| Prova no fim | ambiente "configurado" que nunca rodou |
| Pendências em arquivo | a informação morrer no chat |

## Ajustes que valem a pena com o uso

- Se o projeto tiver **app web**, acrescente ao prompt: *"o `start_cmd` tem que subir em modo
  de produção e responder no `base_url` antes da suíte"*.
- Se o projeto **já existir**, acrescente: *"primeiro mapeie o que já existe (estrutura, testes,
  comandos) e proponha o `allowed_paths` a partir disso"*.
- Se houver **mais de um serviço**, acrescente: *"um ambiente por serviço, um `dsh.json` por
  repositório; não tente unificar"*.
