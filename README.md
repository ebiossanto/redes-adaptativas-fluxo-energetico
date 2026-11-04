# Redes Adaptativas por Fluxo de Energia

Um modelo unificado de redes adaptativas baseado na unificação da **Termodinâmica Linear de Processos Irreversíveis (Onsager)**, das **Estruturas Dissipativas (Prigogine)** e do **Princípio da Potência Máxima (Odum)**, com formalização matemática rigorosa (teoremas de Lyapunov, índice de Morse de Hodge, bifurcações exatas) e uma camada de **computação resiliente por design**.

> Status: rascunho de pesquisa / pré-print. Os resultados foram verificados numericamente com precisão ~1e-9 nos espectros, mas ainda aguardam revisão por pares e formalização independente.

---

## O que é este trabalho

Este repositório reúne o desenvolvimento de uma teoria de redes adaptativas descentralizadas: redes (nós e ligações) que modificam sua própria topologia e condutividade em resposta ao fluxo de energia ou informação que nelas passa, visando processar a maior quantidade possível de fluxo útil enquanto dissipam o gradiente imposto pelo ambiente.

O ponto central é uma **lei única de adaptação** para a condutância de cada ligação:

```
τ·ġ_e = g_e · (Δφ_e² − c − k·g_e^(γ−1))
```

que pode ser lida como um fluxo de gradiente de um funcional de custo `F(g)`. A partir dela são demonstrados:

1. **Convergência global** para um único estado estacionário estável fora do equilíbrio (NESS) quando γ > 1.
2. **A "regra do meio" de Odum–Pinkerton** como identidade exata: dissipação = 2 × custo de manutenção.
3. **Dupla face do mesmo funcional:** com potencial imposto o NESS maximiza potência líquida (Odum); com corrente imposto minimiza dissipação (Prigogine/Thomson).
4. **Estabilidade espectral** via decomposição de Hodge (cortes ⊕ ciclos): o índice de Morse é o número de ciclos independentes β₁ = m − n + 1 quando γ < 1, prevendo a poda de laços.
5. **Pontos críticos exatos de bifurcação:** γ_c = 1 (laços), γ_c = (g_s·R − 1)/(g_s·R + 1) (escala), E_c (dobra/biestabilidade), V_c = N√c (emergência).
6. **Memória fracionária de Caputo:** relaxação em lei de potência t^(−α) em vez de exponencial.

Adicionalmente, o repositório inclui uma proposta de **camada binária resiliente** (aritmética com automonitoramento de dano/entropia, inspirada no limite de Landauer), com protótipos em Julia e especificação de hardware em Verilog.

---

## Estrutura do repositório

```
redes-adaptativas-fluxo-energetico/
├── README.md                    # Este arquivo
├── LICENSE                      # Licença MIT
├── CITATION.cff                 # Como citar este trabalho
├── .gitignore
│
├── docs/                        # Documentação analítica e de planejamento
│   ├── analise-trabalho.md              # Análise crítica do corpo de trabalho
│   ├── roadmap-desenvolvimento.md       # Ideias de desenvolvimento organizadas
│   └── documento-linguagem-simples.md   # Explicação detalhada em linguagem simples
│
├── papers/                      # Artigos científicos em português
│   ├── 01-paper-principal/          # Modelo unificado OTRA-γ (teoremas 1–4)
│   ├── 02-provas-formais/             # Provas formais em estilo SIAM/LaTeX
│   ├── 03-hodge-morse/                # Extensão alta dimensão (Laplaciano de Hodge)
│   └── 04-computacao-resiliente/      # Camada binária resiliente / linguagem segura
│
├── codigo/                      # Scripts reproduzíveis
│   └── otra_unified.py              # Modelo, testes numéricos e figuras
│
├── hardware/                    # Especificação de hardware (Verilog RTL)
│   ├── resilient_r_star_block.v
│   └── resilient_r_star_tb.v
│
└── anexos/                      # Material de apoio e rascunhos originais
    ├── rascunho-inicial.md
    ├── matriz-laplaciana-hodge.md
    └── linguagem-segura.md
```

---

## Como usar os códigos

### Simulação numérica (Python)

O script `codigo/otra_unified.py` implementa o modelo unificado OTRA-γ e reproduz as verificações numéricas dos teoremas (convergência de F, regra do meio, espectro de Hodge, pontos críticos).

```bash
python codigo/otra_unified.py
```

Requer apenas a biblioteca padrão do Python (ou NumPy, se disponível). Os resultados são impressos no terminal e podem ser salvos em `results.json`.

### Hardware (Verilog)

Os arquivos em `hardware/` descrevem a Unidade de Co-processamento de Resiliência (RPU): um bloco RTL que calcula o índice de resiliência `R* = λ_adapt / λ_damage` por comparação de magnitude (sem divisão), acionando um gatilho de mitigação homeostática quando `R* ≤ 1`.

Simule o testbench em qualquer simulador Verilog (Icarus Verilog, ModelSim, Vivado, EDA Playground).

---

## Como citar

Se você utilizar este trabalho em pesquisa, ensino ou desenvolvimento, cite como:

```
Santos, E. S. dos (2026). Redes Adaptativas por Fluxo de Energia: um modelo
unificado Onsager–Prigogine–Odum. Repositório de pesquisa.
https://github.com/ebiossanto/redes-adaptativas-fluxo-energetico
```

Veja `CITATION.cff` para citação em formatos de software (CFF/BibTeX).

---

## Licença

Este trabalho está licenciado sob a [Licença MIT](LICENSE) — você é livre para usar, modificar e distribuir, desde que mantenha os avisos de autoria.

---

## Aviso de método

As demonstrações e o código foram produzidos com apoio de IA e verificados numericamente. Isso não substitui revisão por pares nem formalização matemática independente. As referências bibliográficas foram compiladas de memória e devem ser conferidas (volume, página e ano) antes de qualquer submissão a periódicos.
