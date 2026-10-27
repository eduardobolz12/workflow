# workflow

Protocolo e ferramenta do fluxo de desenvolvimento com três papéis: **arquiteto** (Claude),
**programador** (Kimi) e **verificador** (DSH), com o **Decisor** humano em quatro momentos.

A regra que amarra tudo: **o que significa "pronto" está escrito e executável antes do código existir.**
Chat é efêmero; arquivo é protocolo.

## Conteúdo

| Caminho | O que é |
|---|---|
| `prompt-criar-ambiente.md` | prompt para montar o chão de fábrica de um projeto novo |
| `prompt-organizar-ambiente.md` | mesmo chão de fábrica, com o repo na raiz e o produto em subpasta |
| `prompt-claude-arquiteto.md` | contrato do arquiteto (Claude): passos 1–4, gate, contestação, QA |
| `docs/WORKFLOW.md` | manual de operação (6 passos, congelado) |
| `docs/` (demais) | contrato, briefing do programador, relatórios, tarefas |
| `tools/dsh.py` | verificador: `gate`, `verify`, `metrics`, `note` (Python stdlib) |
| `tools/setup-check.ps1` | checagem de ambiente (6 itens) |
| `tools/test_dsh.py` | 11 testes do próprio verificador |
| `template/` | projeto-base: git, config, fatia de piso para provar o encanamento |

## Como usar

1. **Ambiente de um projeto novo:** cole o prompt de `prompt-criar-ambiente.md` numa sessão nova
   (ou `prompt-organizar-ambiente.md`, quando o repo for a raiz e o produto uma subpasta).
2. **Provar o encanamento:** copie `template/` para o projeto, rode `gate` na fatia de piso.
3. **Ciclo normal:** spec com tabela de CAs → teste vermelho → gate → build → verify → aceite.

## Estado

- `dsh.py` validado com **11 testes** e execução ponta a ponta em repositório real (gate, verify,
  detecção de oráculo adulterado, diff fora de escopo, regressão, métricas).
- Não provado ainda: `start_cmd` com app real e runner de Node (vitest).
- Fora do escopo deste repositório: instalação de pacotes, autenticação e `push` (o shell do DSH
  não tem HTTPS).

## Princípios

1. Contrato antes do código.
2. Toda falha volta um passo como teste falhando ou contestação escrita — nunca como conversa.
3. Toda transição passa por arquivo ou evidência.
