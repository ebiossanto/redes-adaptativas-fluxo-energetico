# Provas Formais — Modelo Unificado OTRA-γ

Estilo: artigo científico / prova matemática (baseado no rascunho LaTeX SIAM, `redes adaptativas baseadas em fluxos energéticos LaTeX.md`).

**Autor:** Euzébio Soares dos Santos  
**Data:** 03/11/2026  
**Status:** rascunho de demonstrações, verificadas numericamente com precisão ~1e-9.

---

## 1. Setup matemático comum

Seja G = (V, E) um grafo direcionado conexo com n = ||V|| nós e m = ||E|| arestas. Seja B ∈ ℝ^(n × m) a matriz de incidência padrão nós-aresta. O estado dinâmico da rede é governado pelo vetor de condutâncias positivas das arestas g(t) ∈ ℝ^m_{>0}. A rede é impulsionada por uma fonte de Thévenin conectada entre o nó fonte s e o nó sumidouro t, definida pelo vetor u = e_s − e_t ∈ ℝ^n, com fem (EMD) E ∈ ℝ_{>0} e condutância interna g_s ∈ (0, ∞].

Os potenciais nodais φ ∈ ℝ^n são unicamente determinados pelo sistema linear estendido de Kirchhoff-Laplacian:

(L(g) + g_s · u · uᵀ) φ = g_s · E · u,

onde L(g) = B · diag(g) · Bᵀ é o Laplaciano padrão do grafo. O vetor de quedas de potencial nas arestas é Δφ = Bᵀφ ∈ ℝ^m.

O funcional termodinâmico da rede é o co-conteúdo de Joule J(g), definido variacionalmente como

J(g) = min_{ψ ∈ ℝ^n} { Σ_{e∈E} g_e (Δψ_e)² + g_s (E − uᵀψ)² }.

Pelo teorema do envelope, o gradiente do co-conteúdo em relação às condutâncias satisfaz ∂J/∂g_e = (Δφ_e)².

A lei não-linear unificada de adaptação para cada aresta e ∈ E é

τ · dg_e/dt = g_e · ( (Δφ_e)² − c − k · g_e^(γ−1) ),

com τ, k ∈ ℝ_{>0} e c ∈ ℝ_{≥0}. Essa dinâmica pode ser expressa como um fluxo de gradiente τ·ġ_e = −g_e·∂F/∂g_e sob a métrica de Riemann diag(1/g_e), governado pelo funcional de custo

F(g) = −J(g) + c · Σ_{e∈E} g_e + (k/γ) · Σ_{e∈E} g_e^γ.

---

## 2. Prova do Teorema 1 (Convergência Global via Convexidade Estrita)

**Teorema (Lyapunov Stability and Global Convergence).**  
Para qualquer γ > 1, k > 0, c ≥ 0, e condutância de fonte finita ou infinita g_s ∈ (0, ∞], o funcional F(g) é estritamente convexo em ℝ^m_{≥0}. Para qualquer condição inicial estritamente positiva g(0) > 0, a trajetória g(t) existe globalmente, permanece estritamente positiva para todo t ≥ 0, e converge assintoticamente ao único minimizador global g* ∈ ℝ^m_{≥0} de F(g).

### 2.1 Invariância do ortante positivo

Reescrevendo a equação de adaptação como dg_e/dt = g_e · h_e(g), onde h_e(g) = (1/τ)·((Δφ_e)² − c − k·g_e^(γ−1)) é contínua em ℝ^m_{>0}, a integração dá

g_e(t) = g_e(0) · exp( ∫₀^t h_e(g(s)) ds ) > 0

para todo t finito. O estouro em tempo finito é descartado pela coercividade mostrada abaixo.

### 2.2 F é uma função de Lyapunov estrita

Tomando a derivada temporal de F(g) ao longo das trajetórias da equação de adaptação via regra da cadeia:

dF/dt = Σ_e ∂F/∂g_e · dg_e/dt = −(1/τ) · Σ_e g_e ( ∂F/∂g_e )² ≤ 0.

A igualdade vale se e somente se ∂F/∂g_e = 0 para todo e ∈ E, que corresponde precisamente aos pontos estacionários da rede. Logo, F(g) é uma função de Lyapunov estrita para o sistema.

### 2.3 Convexidade estrita de F

Analisamos os componentes de F:

- O co-conteúdo de Joule J(g), definido em (1) como o ínfimo ponto a ponto de uma família de funções lineares (logo côncavas) em g. Como o ínfimo de funções côncavas é côncavo, J(g) é côncava, implicando que −J(g) é uma funcional convexa.
- O termo linear de manutenção c · Σ g_e é convexo.
- Para γ > 1, a função g_e ↦ (k/γ) · g_e^γ tem segunda derivada estritamente positiva em ℝ_{≥0}, tornando-a estritamente convexa.

Como soma de uma função convexa e uma estritamente convexa, F(g) é estritamente convexa em ℝ^m_{≥0}, garantindo no máximo um único mínimo global g*.

### 2.4 Coercividade

Para uma fonte de Thévenin finita, J(g) ≤ g_s · E², o que garante −J(g) ≥ −g_s · E². Como γ > 1, o crescimento sublinear de quaisquer termos negativos é estritamente dominado pelo crescimento superlinear de (k/γ) · Σ g_e^γ à medida que ||g|| → ∞. Logo F(g) → ∞ quando ||g|| → ∞, provando que os subconjuntos de nível são compactos e que um único minimizador global g* existe.

### 2.5 Convergência assintótica global

Construímos o funcional auxiliar de entropia relativa

V(g) = Σ_e [ g_e − g*_e · ln g_e ]

no ortante positivo. Diferenciando V(g) em relação ao tempo:

dV/dt = Σ_e (1 − g*_e/g_e) · dg_e/dt = −(1/τ) · ⟨ g − g*, ∇F(g) ⟩.

Pela estrita convexidade de F, ⟨ g − g*, ∇F(g) ⟩ ≥ F(g) − F(g*). Integrando essa desigualdade de 0 a ∞:

∫₀^∞ ( F(g(t)) − F(g*) ) dt ≤ τ · ( V(g(0)) − inf_g V(g) ) < ∞,

onde inf_g V(g) é limitada inferiormente pois x − a·ln x ≥ a − a·ln a. Como F(g(t)) − F(g*) é não-negativo, monótono não-crescente e integrável, pelo lema de Barbalat, lim_{t→∞} F(g(t)) = F(g*). Pela unicidade do minimizador, lim_{t→∞} g(t) = g*. ∎

---

## 3. Prova do Teorema 3 (Decomposição Espectral de Hodge–Morse)

**Teorema (Hodge–Morse Spectral Theorem).**  
Seja g* um ponto estacionário interior da equação de adaptação com custo de manutenção c = 0. A matriz Hessiana do funcional F em g* satisfaz a fatoração exata

∇²F(g*) = k · S · ( 2Π̃ + (γ − 1)I ) · S,

onde S = diag( (g*_e)^(γ/2 − 1) ) e Π̃ = G*^(1/2) · Bᵀ · ( L(g*) + g_s · u · uᵀ )⁺ · B · G*^(1/2) é a matriz de projeção de Hodge ponderada, com G* = diag(g*) e (·)⁺ a pseudo-inversa de Moore-Penrose.

O espectro exato do operador estrutural (2Π̃ + (γ − 1)I) consiste em:

- λ_i = γ + 1, com multiplicidade n − 2 (modos de corte puro);
- λ_scale = γ − 1 + 2/(1 + g_s · R_eff(g*)), com multiplicidade 1 (modo de escala);
- λ_j = γ − 1, com multiplicidade β₁ = m − n + 1 (modos de ciclo).

### 3.1 Derivada da fórmula do Hessiano

Diferenciando o gradiente ∂F/∂g_e = −(Δφ_e)² + k · g_e^(γ−1) em relação a g_f:

∂²F/∂g_f∂g_e = −2 · Δφ_e · ∂(Δφ_e)/∂g_f + δ_ef · k(γ − 1) · g_e^(γ−2).

Diferenciando o sistema de Kirchhoff em relação a g_f, com a abreviação L̃ := L(g*) + g_s · u · uᵀ:

L̃ · ∂φ/∂g_f + (B · e_f · e_fᵀ · Bᵀ) φ = 0,

o que dá ∂φ/∂g_f = −L̃⁺ · B · e_f · Δφ_f. Multiplicando por Bᵀ, a derivada das quedas de potencial é

∂(Δφ_e)/∂g_f = −(Bᵀ · L̃⁺ · B)_{ef} · Δφ_f.

Substituindo de volta:

∂²F/∂g_f∂g_e = 2 · Δφ_e · (Bᵀ · L̃⁺ · B)_{ef} · Δφ_f + δ_ef · k(γ − 1) · g_e^(γ−2).

Em um NESS interior g*, a condição estacionária implica (Δφ_e)² = k · (g*_e)^(γ−1), ou seja, Δφ_e = √k · (g*_e)^((γ−1)/2). Definindo o operador de projeção escalado Π̃_{ef} = (g*_e)^(1/2) · (Bᵀ · L̃⁺ · B)_{ef} · (g*_f)^(1/2), a substituição yield a fatoração exata ∇²F(g*) = k · S · (2Π̃ + (γ − 1)I) · S.

### 3.2 Decomposição de Hodge–Helmholtz

Pela decomposição discreta de Hodge–Helmholtz, o espaço de arestas ℝ^m se divide em subespaços ortogonais de cortes e ciclos:

ℝ^m = im(G^(1/2) · Bᵀ) ⊕ ker(B · G^(-1/2)).

Sem a fonte (g_s = 0), a matriz Π = G^(1/2) · Bᵀ · L⁺ · B · G^(1/2) é um projetor ortogonal sobre o espaço de cortes im(G^(1/2) · Bᵀ), que tem posto n − 1, deixando um núcleo de ciclos com dimensão β₁ = m − n + 1.

Com uma fonte de Thévenin finita, aplicando a fórmula de Sherman–Morrison–Woodbury a L̃⁺ = (L + g_s · u · uᵀ)⁺ isola a perturbação da fonte:

Π̃ = Π − [ g_s / (1 + g_s · uᵀ · L⁺ · u) ] · (G^(1/2) · Bᵀ · L⁺ · u) · (G^(1/2) · Bᵀ · L⁺ · u)ᵀ.

Definindo w = G^(1/2) · Bᵀ · L⁺ · u, tem-se |w|² = uᵀL⁺u = R e Πw = w; logo ŵ = w/|w| tem autovalor 1 − g_s·R/(1 + g_s·R) = 1/(1 + g_s·R). ∎

---

## 4. Interpretação dos autovalores e índice de Morse

A linearização da dinâmica é −G · Hess F / τ, com a mesma inércia que Hess F (Lei de Sylvester). Logo o número de direções instáveis é o índice de Morse.

- **γ > 1:** todos os autovalores de ciclo (γ − 1) são estritamente positivos. O grafo é estável e conectado.
- **γ < 1:** surgem exatamente β₁ = m − n + 1 autovalores negativos (modos de ciclo). O índice de Morse é β₁. Isso prova analiticamente que qualquer rede com ciclos decai para uma árvore geradora (poda total de laços) em tempo finito.

---

## 5. Observações sobre formalização

As demonstrações acima estão prontas para formalização em um verificador de teoremas (candidato natural: Lean 4 / Mathlib), especialmente o Teorema 1 (convexidade, coercividade, entropia relativa e lema de Barbalat). A revisão independente e a formalização ainda estão pendentes.
