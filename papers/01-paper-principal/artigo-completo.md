# Redes Adaptativas por Fluxo de Energia: um modelo unificado Onsager–Prigogine–Odum, com teoremas de Lyapunov, índice de Morse de Hodge e bifurcações exatas

**Euzébio Soares dos Santos**  
Rascunho 1 — 03/11/2026  
Repositório: https://github.com/ebiossanto/redes-adaptativas-fluxo-energetico  

> **Nota de método:** as demonstrações e o código foram produzidos com apoio de IA e verificados numericamente (script anexo, precisão ~1e-9 nos espectros). Isso não substitui revisão por pares nem formalização independente. As referências bibliográficas foram compiladas de memória: conferir volume, página e ano antes de submeter.

---

## Resumo

Propomos uma lei de adaptação única para as condutâncias de uma rede resistiva descentralizada excitada por uma fonte de Thévenin (fem E, condutância interna g_s):

τ·ġ_e = g_e · (Δφ_e² − c − k·g_e^(γ−1))

A lei é um fluxo de gradiente, com mobilidade g_e, do funcional F(g) = −J(g) + c·Σg + (k/γ)·Σg^γ, em que J é o co-conteúdo de Joule. Principais resultados:

(i) Para γ > 1, F é estritamente convexo e todo estado inicial positivo converge ao único atrator (Teorema 1); o modelo do rascunho inicial (γ = 2, c = 0) está nesse caso e, portanto, **não possui bifurcações**.

(ii) A "regra do meio" de Odum–Pinkerton se torna identidade exata no Estado Estacionário Fora do Equilíbrio (NESS): dissipação = 2 × custo de manutenção (Teorema 2). Com potencial imposto o NESS maximiza a potência líquida (Odum); com corrente imposto minimiza a dissipação (Prigogine/Thomson): duas faces de um mesmo F.

(iii) O Hessiano de F em qualquer estado estacionário interior é congruente a 2Π̃ + (γ − 1)I, onde Π̃ vem da decomposição de Hodge (corte ⊕ ciclo) do espaço de arestas; o índice de Morse é o número de ciclos independentes β₁ = m − n + 1 quando γ < 1, e a instabilidade ocorre exatamente em γ_c = 1 (Teorema 3).

(iv) Pontos críticos exatos: γ_c = 1 (laços); γ_c = (g_s·R − 1)/(g_s·R + 1) (modo de escala); dobra em E_c = (2√k/(1 + γ))·[g_s(1 − γ)/(1 + γ)]^((γ − 1)/2); transcrítica em V_c = N·√c (Teorema 4).

(v) A memória de Caputo troca a relaxação exponencial por uma lei de potência t^(−α) (Proposição 6).

**Palavras-chave:** redes adaptativas, fluxo de energia, termodinâmica de processos irreversíveis, estruturas dissipativas, princípio da potência máxima, Onsager, Prigogine, Odum, Lyapunov, decomposição de Hodge, bifurcação, computação resiliente.

---

## 1. Introdução

Redes adaptativas são sistemas cujos nós e ligações modificam sua própria topologia e condutividade em resposta ao fluxo de energia ou informação que nelas passa. Exemplos abrangem redes elétricas, redes de transporte biológico (veias de folhas, sistemas vasculares), redes ecológicas e redes de comunicação.

Três tradições teóricas clássicas descrevem fenômenos relacionados, mas historicamente foram tratadas como separadas:

1. A **termodinâmica linear de processos irreversíveis** de Lars Onsager, que relaciona fluxos e forças termodinâmicas por coeficientes de acoplamento simétricos.
2. As **estruturas dissipativas** de Ilya Prigogine, que explicam a auto-organização de sistemas abertos longe do equilíbrio.
3. O **princípio da potência máxima** de Howard T. Odum, segundo o qual sistemas naturais tendem a maximizar o processamento de potência útil, com eficiência ótima próxima de 1/2.

Este trabalho mostra que essas três tradições são faces de um mesmo problema. A partir de uma única lei de adaptação de condutâncias, derivamos um funcional de custo F(g) cujos minimizadores descrevem o Estado Estacionário Fora do Equilíbrio (NESS) da rede. Demonstramos teoremas de convergência global, estabilidade espectral via decomposição de Hodge, a regra do meio de Odum–Pinkerton como identidade exata, e pontos críticos exatos de bifurcação.

O rascunho inicial deste projeto propunha simulações de rede de três nós e a noção de "bifurcação de Prigogine" induzida por ruído. Mostramos aqui que essa interpretação não se sustenta para o modelo linear (γ = 2, c = 0), que possui atrator global único; bifurcações exigem extensões com custo côncavo (γ < 1), custo linear de manutenção (c > 0) ou impedância de fonte finita.

---

## 2. O modelo unificado OTRA-γ

### 2.1 Definição da rede e da fonte

Seja G = (V, E) um grafo conexo com n nós e m arestas. Seja B a matriz de incidência n × m e g ∈ ℝ^m o vetor de condutâncias positivas das arestas. A matriz Laplaciana da rede é

L(g) = B · diag(g) · Bᵀ.

Uma fonte de Thévenin liga os nós s e t, com vetor u = e_s − e_t, fem E ∈ ℝ_{>0} e condutância interna g_s ∈ (0, ∞]. Os potenciais nodais φ ∈ ℝ^n resolvem o sistema estendido de Kirchhoff:

(L(g) + g_s·u·uᵀ) φ = g_s · E · u,

e as quedas de potencial nas arestas são Δφ = Bᵀφ.

### 2.2 Co-conteúdo de Joule

Definimos o co-conteúdo de Joule como

J(g) = min_ψ { Σ_{e∈E} g_e (Δψ_e)² + g_s (E − uᵀψ)² }.

J(g) é côncava em g (mínimo ponto a ponto de funções afins) e, pelo teorema do envelope, ∂J/∂g_e = (Δφ_e)².

Limites importantes:
- g_s → ∞: **caso Dirichlet** (potencial E imposto). J = P_V(g), a potência de Joule.
- g_s → 0 com I = g_s·E fixo: **caso Neumann** (corrente imposta). −J → P_N(g) = I²·R_eff(g) − const, convexa.

### 2.3 Lei de adaptação

A condutância de cada aresta evolui segundo

τ · dg_e/dt = g_e · ( (Δφ_e)² − c − k · g_e^(γ−1) ),

com τ > 0, k > 0, c ≥ 0 e γ > 0.

O termo (Δφ_e)² é a potência útil direcionadora; c·g_e é o custo linear de manutenção; k·g_e^γ é o termo de desgaste/dano (quadrático para γ = 2, côncavo do tipo volume para γ < 1).

### 2.4 Funcional de custo e fluxo de gradiente

Definimos

F(g) = −J(g) + c · Σ g_e + (k/γ) · Σ g_e^γ.

Então a dinâmica pode ser escrita como um fluxo de gradiente com métrica diag(1/g_e):

τ · dg_e/dt = −g_e · ∂F/∂g_e.

O parêntese c·Σg + (k/γ)·Σg^γ representa o custo de manutenção da rede; γ = 2 recupera o "dano quadrático" do rascunho inicial, enquanto γ < 1 modela custos côncavos típicos de redes de transporte biológico.

---

## 3. Resultados

### Teorema 1 (Lyapunov e convergência global)

Para γ > 1, k > 0, c ≥ 0, qualquer g_s ∈ (0, ∞] ou o caso Neumann, e qualquer condição inicial g(0) > 0:

1. g_e(t) > 0 para todo t e a solução é global (não explode em tempo finito);
2. dF/dt = −(1/τ) · Σ g_e (∂_eF)² ≤ 0, com igualdade só em pontos estacionários;
3. F é estritamente convexa e possui um único minimizador g* em ℝ^m_{≥0};
4. g(t) → g* e ∫₀^∞ (F(g(t)) − F*) dt < ∞.

Portanto, F é uma função de Lyapunov estrita e a rede converge globalmente ao único NESS.

**Demonstração resumida.** A positividade de g segue de ġ_e = g_e·h_e(g). A monotonia de F segue da regra da cadeia. A estrita convexidade vem de: −J convexa (J côncava), termo linear convexo, e (k/γ)·g^γ estritamente convexa para γ > 1. A coercividade garante existência e unicidade do minimizador. Um funcional auxílio de entropia relativa V(g) = Σ (g_e − g*_e·ln g_e) prova a convergência assintótica (lema de Barbalat).

**Observação (poda):** arestas com Δφ_e → 0 no NESS decaem como g ≈ 1/(k·t), algebricamente, não exponencialmente.

### Teorema 2 (regra do meio e dualidade MPP × produção mínima)

Para γ = 2, c = 0, em todo ponto estacionário:

Σ g_e (Δφ_e)² = k · Σ g_e².

Definindo M := (k/2) · Σ g_e² (custo de manutenção), a potência dissipada na rede é exatamente 2M.

**Consequências:**
- **Caso Dirichlet:** F = −P_V + M, logo o NESS maximiza a potência líquida P_V − M, e nesse máximo P_V − M = P_V/2: eficiência 1/2, o resultado de Odum–Pinkerton e o teorema de máxima transferência de potência (Jacobi) emergindo como identidade exata, sem hipótese sobre a topologia.
- **Caso Neumann:** F = P_N + M, logo o NESS minimiza dissipação + manutenção (Thomson–Prigogine).
- A impedância g_s interpola os dois regimes com a mesma lei de adaptação.

### Teorema 3 (Hodge–Morse)

Seja g* um ponto estacionário interior com c = 0 (orientando cada aresta no sentido Δφ_e > 0). Então

Hess F(g*) = k · S · (2Π̃ + (γ − 1)I) · S,

com S = diag((g*_e)^(γ/2 − 1)) e Π̃ = G*^(1/2) · Bᵀ · (L(g*) + g_s·u·uᵀ)⁺ · B · G*^(1/2), o projetor de Hodge ponderado.

O espectro de (2Π̃ + (γ − 1)I) é exatamente:

| Modo | Autovalor | Multiplicidade |
|------|-----------|----------------|
| Corte puro | γ + 1 | n − 2 |
| Modo de escala | γ − 1 + 2/(1 + g_s·R_eff) | 1 |
| Ciclo | γ − 1 | β₁ = m − n + 1 |

No limite Neumann (ν = 1) há n − 1 autovalores γ + 1; no limite Dirichlet (ν = 0) há β₁ + 1 autovalores γ − 1.

**Corolários:**
- Para γ > 1, todo estacionário interior é estável (todos os autovalores positivos).
- Para γ < 1, todo estacionário interior de um grafo com ciclos tem índice de Morse ≥ β₁ ≥ 1; estados estáveis exigem arestas podadas (as arestas extinguem em tempo finito, pois ġ ≈ −k·g^γ). Isso explica, com limiar exato, a supressão de laços em redes de custo côncavo (redes de transporte biológico).

### Teorema 4 (pontos críticos exatos)

**(a) Laços: γ_c = 1**, independente de E, I e g_s. Em γ = 1 o núcleo tem dimensão β₁ (degenerescência). Para dois canais paralelos, a assimetria |g₁ − g₂|/(g₁ + g₂) é 1 para γ < 1, 0 para γ > 1, e neutra em γ = 1.

**(b) Modo de escala: γ_c = 1 − 2ν = (g_s·R − 1)/(g_s·R + 1)**, com R = R_eff no NESS. O casamento de impedâncias (g_s·R = 1) dá γ_c = 0.

**(c) Dobra (saddle-node), um canal, fonte de Thévenin, γ < 1.**  
F(g) = −E²·g_s·g/(g + g_s) + (k/γ)·g^γ. A condição F′ = F″ = 0 dá

g_c = g_s · (1 − γ)/(1 + γ),  
E_c = (2√k/(1 + γ)) · [g_s · (1 − γ)/(1 + γ)]^((γ − 1)/2).

Para E < E_c, g = 0 é o único atrator. Para E > E_c coexistem g = 0 (estável), um ramo interior estável e uma separatriz instável: **biestabilidade e histerese**. Exemplo: γ = 0,5, k = 1, g_s = 1 dá E_c = 1,7548.

**(d) Emergência por transcrítica (Dirichlet, γ = 2, c > 0).**  
Uma cadeia de N arestas em série tem estacionário g* = ((V/N)² − c)/k, existente sse V > V_c = N · √c. Canais paralelos desacoplam sob Dirichlet, e o canal mais curto emerge primeiro (seleção de caminho mínimo, à la Physarum).

### Proposição 5 (reversibilidade e irreversibilidade)

1. Com acoplamento de Onsager L = S + A (S simétrica ≽ 0, A antissimétrica), a produção de entropia σ = xᵀLx = xᵀSx ≥ 0: a parte antissimétrica (giroscópica/Casimir) não produz entropia.
2. **Seta do tempo na adaptação:** Ḟ = −τ · Σ ġ_e²/g_e ≤ 0, estrito fora de estacionários. Não há órbitas periódicas nem recorrência: a reversão temporal de uma trajetória não-estacionária aumentaria F, logo não é solução.
3. Acoplamento de Casimir no setor g mantém Ḟ ≤ 0 e o conjunto de estacionários, mas pode perder convergência global e aparecer oscilação.

### Proposição 6 (memória fracionária de Caputo)

Substituindo τ·ġ por τ^α · D^α_t g (0 < α < 1), perto de g* cada modo satisfaz

ε_i(t) = E_α(−λ_i·t^α/τ^α) · ε_i(0),

e E_α(−x) ~ 1/(x·Γ(1−α)) para x → ∞. Logo ||g − g*|| ~ t^(−α): **relaxação em lei de potência**, com tempo de relaxação divergente (envelhecimento). Testes numéricos (losango, Neumann, γ = 2, esquema L1) deram inclinações log-log −0,921, −0,720 e −0,487 para α = 0,9, 0,7, 0,5.

---

## 4. Verificação numérica

O script anexo `otra_unified.py` (pasta `codigo/`) reproduz os teoremas com precisão ~1e-9:

| Verificação | Resultado |
|-------------|-----------|
| Teo. 1: F(t) em 3 modos de fonte × 6 condições iniciais (7 nós, 12 arestas) | Maior aumento de F = 0; convergência ao minimizador |
| Teo. 2: P_diss vs k·Σg² | Igualdade exata em Neumann, Dirichlet e Thevenin |
| Teo. 3: γ = 1,5, 6 nós, 9 arestas, β₁ = 4 | Autovalores γ−1 = 0,5 (×4) e γ+1 = 2,5 (×5), erro ~1e-9 |
| Teo. 3: γ = 0,5, losango (β₁ = 1) | −0,5 e 1,5 (×3), conforme predito |
| Teo. 3: Thevenin γ = 0,7, g_s·R = 0,19978 | −0,3; 1,36697 (predito 1,36697); 1,7 (×2) |
| Teo. 4(a): garfo | Assimetria 1 / 0,01 / 0 para γ<1 / =1 / >1 |
| Teo. 4(c): dobra | E_c = 1,7548; bacias de atração conforme previsto |
| Teo. 4(d): transcrítica | Erro ≤ 1,2e-4, V_c = N√c |
| Prop. 6 | Inclinações −0,921 / −0,720 / −0,487 |

Limitação: no esquema L1 explícito com passo h = 0,2–0,3 e α = 0,5, o primeiro passo aumenta F em 8e-4 (artefato de discretização); com h ≤ 0,1, F é monótona. A monotonia contínua do fluxo fracionário não está provada neste trabalho.

---

## 5. Discussão e trabalho relacionado

**Sobre a "bifurcação de Prigogine."** O rascunho inicial afirmava que ruído amplificado numa bifurcação de Prigogine reconfiguraria a rede. Corrigimos: Prigogine não maximiza dissipação longe do equilíbrio (Glansdorff–Prigogine dão apenas uma desigualdade). O modelo γ = 2, c = 0 não bifurca. Bifurcações genuínas requerem γ < 1, c > 0 ou impedância de fonte.

**Relação com redes de transporte biológico.** A poda de laços para γ < 1 (Teorema 3, corolário c) está em linha com trabalhos de Bohn & Magnasco, Katifori et al., Corson, Hu & Cai, que mostram danos e flutuações induzindo laços em redes ótimas — aqui derivado de um limiar exato de índice de Morse.

**Relação com Physarum e caminhos mínimos.** A emergência do canal mais curto sob Dirichlet (Teorema 4d) ecoa Bonifaci, Mehlhorn & Varma (Physarum computa caminhos mínimos) e Tero et al. (design de redes adaptativas inspirado em biologias).

**Referências chave:** Onsager (1931), Prigogine (1947), Glansdorff & Prigogine (1971), Odum & Pinkerton (1955), Odum (1996), Landauer (1961), Lim (2020), Matignon (1996), Podlubny (1999).

---

## 6. Conclusão e trabalhos futuros

Unificamos Onsager, Prigogine e Odum num único funcional F(g) e numa única lei de adaptação, obtendo resultados exatos de convergência, estabilidade espectral, regra do meio e bifurcações. O trabalho fornece uma base matemática para prever o comportamento de redes adaptativas descentralizadas, com verificação numérica rigorosa.

Trabalhos futuros: prova da dobra em redes gerais, demonstração da monotonia do fluxo fracionário, versão estocástica, formalização em verificador de teoremas (Lean 4/Mathlib) e validação experimental em hardware (rede de microcontroladores ou dados ecológicos).

---

## Referências (conferir antes de submeter)

1. Onsager, L. (1931). Reciprocal relations in irreversible processes I–II. Phys. Rev. 37, 405; 38, 2265.
2. Prigogine, I. (1947). Étude thermodynamique des phénomènes irréversibles. Dunod/Desoer.
3. Glansdorff, P.; Prigogine, I. (1971). Thermodynamic Theory of Structure, Stability and Fluctuations. Wiley.
4. Odum, H. T.; Pinkerton, R. C. (1955). Time's speed regulator. American Scientist 43, 331–343.
5. Odum, H. T. (1996). Environmental Accounting: Emergy and Environmental Decision Making. Wiley.
6. Landauer, R. (1961). Irreversibility and heat generation in the computing process. IBM J. Res. Dev. 5, 183–191.
7. Tero, A. et al. (2010). Rules for biologically inspired adaptive network design. Science 327, 439.
8. Bonifaci, V.; Mehlhorn, K.; Varma, G. (2012). Physarum can compute shortest paths. J. Theor. Biol. 309, 121.
9. Hu, D.; Cai, D. (2013). Adaptation and optimization of biological transport networks. Phys. Rev. Lett. 111, 138701.
10. Katifori, E.; Szöllősi, G.; Magnasco, M. (2010). Damage and fluctuations induce loops in optimal transport networks. Phys. Rev. Lett. 104, 048704.
11. Corson, F. (2010). Fluctuations and redundancy in optimal transport networks. Phys. Rev. Lett. 104, 048703.
12. Bohn, S.; Magnasco, M. (2007). Structure, scale, and function of adaptive networks. Phys. Rev. Lett. 98, 088702.
13. Lim, L.-H. (2020). Hodge Laplacians on graphs. SIAM Review 62, 685.
14. Martyushev, L.; Seleznev, V. (2006). Maximum entropy production principle in physics, chemistry and biology. Phys. Rep. 426, 1.
15. Matignon, D. (1996). Stability results for fractional differential equations. CESA'96.
16. Podlubny, I. (1999). Fractional Differential Equations. Academic Press.
17. Tang, T.; Yu, H.; Zhou, T. (2019). On energy dissipation theory and numerical stability for time-fractional phase-field equations. SIAM J. Sci. Comput.

---

## Anexo: arquivos reproduzíveis

- `codigo/otra_unified.py` — modelo, testes numéricos e figuras (Figs. 1–5).
- `results.json` — valores numéricos citados no texto.
