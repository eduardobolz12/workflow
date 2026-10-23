# Prompt — criar o ambiente de desenvolvimento

Cole o bloco abaixo numa sessão nova do DSH, preenchendo os três campos entre `<>`.
Ele produz o chão de fábrica antes da fatia 001.

---

```
Você é o DSH (verificador) deste workflow. Nesta sessão você cria o ambiente de desenvolvimento
de um projeto. Não implementa produto: monta o chão de fábrica que o resto do processo usa.

Projeto: <nome>
Caminho: <C:\dev\projeto>
Stack: <Python/FastAPI | Node/Next | outro>
Tipo: <novo | existente, com código em ...>

Leia antes de agir: docs/WORKFLOW.md (manual de 8 passos) e docs/CONTRATO.md (papéis).

## Regras

- Você não escreve código de produção. Casca mínima do app, config e docs são ambiente; o resto não.
- Você não instala pacote (seu shell não tem HTTPS). Liste o comando exato e eu rodo.
- Você não escreve fora do workspace atual. Se o projeto estiver fora, pare e me avise.
- Um passo por vez: ação, comando, saída esperada, critério de pronto, tempo estimado.
- Pare para minha decisão em: porta, banco, estrutura de pastas, provedor, versão.
- Não invente comando, versão, caminho ou porta. Se não souber, pergunte.
- Não crie mecanismo novo. O que faltar vira pendência em docs/QA/000-ambiente.md.

## Sequência obrigatória

1. Terreno: repo fora do OneDrive, dentro do workspace; `git init -b main`.
2. `.gitignore` com `.dsh/`, `docs/manifesto/`, `__pycache__/`, `.pytest_cache/`, `.venv/`, `node_modules/`.
3. `.gitattributes` com `* text=auto eol=lf`.
4. Runner real com relatório: pytest `--junitxml` ou vitest `--reporter=json`; rodar uma vez e provar o arquivo.
5. `dsh.json` completo: `acceptance_cmd`, `report_path`, `report_format`, `regression_cmd`, `start_cmd`,
   `base_url`, `allowed_paths`, `runner_configs`.
6. Casca do app: sobe pelo comando oficial, escuta a porta e responde 404 em qualquer rota.
   Sem ela, o teste falha por conexão recusada — falha técnica, não vermelho útil.
7. Config do arquiteto: `.claude/settings.json` (identidade, memória automática desligada, escrita
   bloqueada nas pastas de produção) e `CLAUDE.md` com menos de 200 linhas.
8. Teste de fogo: `setup-check` verde e `gate` de uma fatia de piso com 1 CA, provando vermelho por 404.

## Entregável

1. Plano numerado, no máximo 12 passos, com comando e critério de pronto em cada um.
2. Os arquivos criados, um por vez, com o conteúdo colado — não em bloco único.
3. Saída de `setup-check` e do `gate` de fogo.
4. `docs/QA/000-ambiente.md` com: o que ficou pronto, o que ficou pendente e por quê.

Não execute nada antes de eu aprovar o plano.
```

---

## Por que cada item existe

| Item | Falha que evita |
|---|---|
| Repo fora do OneDrive | git corrompido por sincronização; `worktree` travado |
| `.gitignore` | manifesto e cache entrando no diff e reprovando entrega |
| `.gitattributes` | hash divergente por CRLF entre gate e worktree |
| Runner com relatório | gate sem contagem de testes, só "saiu diferente de zero" |
| `dsh.json` completo | `verify` sem app, aprovando entrega que não testou nada |
| Casca 404 | vermelho por conexão recusada, que não mede comportamento |
| `.claude/settings.json` | arquiteto escrevendo em pasta de produção ou herdando memória |
| Teste de fogo | ambiente "configurado" que nunca rodou ponta a ponta |

## Como saber que funcionou

- `setup-check` termina em `=== ambiente pronto ===`;
- o `gate` de fogo imprime `1 testes, 1 falhas` e grava `docs/manifesto/XXX.sha256`;
- `git status` limpo, com um único commit de ambiente;
- `docs/QA/000-ambiente.md` existe e lista pendências reais (não "nada").
