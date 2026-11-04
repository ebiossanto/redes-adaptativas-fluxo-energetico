# Roadmap de Desenvolvimento — Ideias Organizadas

Este documento organiza as ideias de desenvolvimento do trabalho em fases, do curto ao longo prazo, com entregas e responsáveis sugeridos.

---

## Fase 0 — Consolidação e reprodução (0–2 meses)

**Objetivo:** deixar o código reproduzível e os resultados verificáveis por terceiros.

| ID | Atividade | Entrega | Prioridade |
|----|-----------|---------|------------|
| F0-1 | Limpar e comentar `otra_unified.py`; garantir execução sem dependências externas pesadas | Script rodando sozinho, saída em `results.json` | Alta |
| F0-2 | Reproduzir todos os números da Tabela de Verificação (Teoremas 1–4, Prop. 6) | Relatório de reprodução (Markdown) | Alta |
| F0-3 | Conferir e corrigir referências bibliográficas (volumes, páginas, anos) | `referencias.bib` revisado | Alta |
| F0-4 | Adicionar testes automatizados (pytest) para os teoremas numéricos | Suite de testes com assert ~1e-9 | Média |
| F0-5 | Gerar figuras vetoriais (Figs. 1–5) a partir do script | Pasta `papers/01-paper-principal/figuras/` | Média |

---

## Fase 1 — Formalização e publicação do modelo principal (2–6 meses)

**Objetivo:** transformar o rascunho em artigo científico submetível.

| ID | Atividade | Entrega | Prioridade |
|----|-----------|---------|------------|
| F1-1 | Redigir artigo completo baseado em `01-paper-principal` (Resumo, Intro, Modelo, Resultados, Discussão, Referências) | `papers/01-paper-principal/artigo-completo.md` (e .tex) | Alta |
| F1-2 | Formalizar Teorema 1 em verificador de teoremas (Lean 4 / Mathlib) como prova de conceito | Projeto Lean no repositório | Média |
| F1-3 | Submeter o artigo a periódico de sistemas complexos / física estatística / ecologia de sistemas | Pré-print (arXiv) + submissão | Alta |
| F1-4 | Escrever documento em linguagem simples para divulgação | `docs/documento-linguagem-simples.md` | Alta |

---

## Fase 2 — Extensões teóricas em aberto (6–12 meses)

**Objetivo:** resolver os itens marcados como "Aberto" no trabalho.

| ID | Atividade | Entrega | Prioridade |
|----|-----------|---------|------------|
| F2-1 | Provar a dobra (saddle-node) para redes gerais (n > 2), usando redução por simetria + continuação numérica | Seção no paper ou anexo técnico | Média |
| F2-2 | Provar dissipação de F no fluxo fracionário de Caputo não linear e positividade (g > 0) | Proposição formal + teste numérico | Média |
| F2-3 | Estudar acoplamento de Casimir (Ω ≠ 0): convergência e bifurcação de Hopf (critério de Matignon) | Análise de estabilidade | Baixa |
| F2-4 | Desenvolver versão estocástica (ruído multiplicativo) e selecionar ramos para γ < 1 | Simulações estocásticas | Baixa |

---

## Fase 3 — Validação experimental e hardware (12–18 meses)

**Objetivo:** levar o modelo da simulação ao mundo físico.

| ID | Atividade | Entrega | Prioridade |
|----|-----------|---------|------------|
| F3-1 | Implementar a rede de microcontroladores (nós físicos) com borda distribuída | Prototipo de hardware | Média |
| F3-2 | Implementar a RPU (Unidade de Co-processamento de Resiliência) em FPGA usando `hardware/resilient_r_star_block.v` | Bitstream FPGA + testbench passando | Média |
| F3-3 | Medir convergência ao NESS e comparação com predições do modelo | Relatório experimental | Baixa |
| F3-4 | Comparar com dados ecológicos empíricos (ex.: redes tróficas Ecopath/Ulanowicz) | Artigo de validação empírica | Baixa |

---

## Fase 4 — Integração e ecossistema (18+ meses)

**Objetivo:** unir os eixos em uma plataforma coerente.

| ID | Atividade | Entrega | Prioridade |
|----|-----------|---------|------------|
| F4-1 | Acoplar métrica de resiliência R* à dinâmica de condutâncias g_e (computação resiliente como substrato da rede adaptativa) | Modelo integrado OTRA-γ + RPU | Baixa |
| F4-2 | Publicar biblioteca Python (`otra-py`) no PyPI | Pacote instalável | Baixa |
| F4-3 | Integrar com o simulador SYLVA ODUM (ecossistema regenerativo) | Ligação entre modelos | Baixa |

---

## Métricas de sucesso sugeridas

- Precisão numérica mantida em ≤ 1e-9 nos espectros.
- Todos os teoremas possuem pelo menos um teste automatizado.
- Artigo principal submetido a periódico com revisão por pares.
- Pelo menos uma validação em hardware (simulação Verilog ou microcontroladores).
