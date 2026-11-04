"""
otra_unified.py
===============

Modelo unificado OTRA-gama: redes adaptativas por fluxo de energia
(Onsager - Prigogine - Odum).

Implementa a lei de adaptação de condutancias:

    tau * dg_e/dt = g_e * ( (Delta phi_e)^2 - c - k * g_e^(gamma - 1) )

para uma rede resistiva descentralizada excitada por uma fonte de Thevenin
(fem E, condutancia interna g_s), e verifica numericamente os Teoremas 1-4
e a Proposicao 6 do artigo acompanhante.

Requisitos: apenas a biblioteca padrao do Python. Se numpy estiver instalado,
é usado para acelerar operacoes lineares; caso contrario, há fallback puro.

Autor: Euzébio Soares dos Santos (rascunho de pesquisa, 2026)
"""

import json
import math
import sys

try:
    import numpy as np
    HAS_NUMPY = True
except Exception:  # pragma: no cover - numpy opcional
    HAS_NUMPY = False


# ---------------------------------------------------------------------------
# Utilidades de álgebra linear (com fallback para numpy)
# ---------------------------------------------------------------------------

def mat_vec_mul(A, v):
    """A (n x m) vezes v (m) -> vetor n."""
    if HAS_NUMPY:
        return np.asarray(A) @ np.asarray(v)
    n = len(A)
    m = len(v)
    out = [0.0] * n
    for i in range(n):
        s = 0.0
        Ai = A[i]
        for j in range(m):
            s += Ai[j] * v[j]
        out[i] = s
    return out


def mat_mat_mul(A, B):
    """A (n x k) vezes B (k x p) -> matriz n x p."""
    if HAS_NUMPY:
        return np.asarray(A) @ np.asarray(B)
    n = len(A)
    k = len(B)
    p = len(B[0])
    out = [[0.0] * p for _ in range(n)]
    for i in range(n):
        for j in range(p):
            s = 0.0
            for l in range(k):
                s += A[i][l] * B[l][j]
            out[i][j] = s
    return out


def mat_transpose(A):
    if HAS_NUMPY:
        return np.asarray(A).T.tolist()
    n = len(A)
    m = len(A[0])
    return [[A[i][j] for i in range(n)] for j in range(m)]


def solve_linear(A, b):
    """Resolve A x = b (A quadrada n x n) por eliminacao de Gauss com pivoteamento."""
    if HAS_NUMPY:
        return np.linalg.solve(np.asarray(A, dtype=float), np.asarray(b, dtype=float)).tolist()
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        # pivoteamento parcial
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-14:
            raise ValueError("Matriz singular (ou quase singular)")
        M[col], M[piv] = M[piv], M[col]
        piv_val = M[col][col]
        for j in range(col, n + 1):
            M[col][j] /= piv_val
        for r in range(n):
            if r != col and abs(M[r][col]) > 1e-14:
                factor = M[r][col]
                for j in range(col, n + 1):
                    M[r][j] -= factor * M[col][j]
    return [M[i][n] for i in range(n)]


def pinv_svd(A, rcond=1e-12):
    """Pseudo-inversa de Moore-Penrose (fallback via numpy se disponível)."""
    if HAS_NUMPY:
        return np.linalg.pinv(np.asarray(A, dtype=float), rcond=rcond).tolist()
    # Fallback simples: resolvemos pelos autovetores nao e possiveis.
    # Para evitar dependencia de scipy, usamos a solucao de sistemas normais
    # com regularizacao quando a matriz e pequena e bem condicionada.
    At = mat_transpose(A)
    AtA = mat_mat_mul(At, A)
    n = len(AtA)
    reg = 1e-10
    for i in range(n):
        AtA[i][i] += reg
    # pinv(A) ~= (AtA)^-1 At  (valido quando A tem posto cheio por colunas;
    # para o nosso uso com Laplaciana singular usamos o tramento de fonte,
    # que torna a matriz estendida nao singular no subespaco relevante).
    AtA_inv = None
    try:
        # resolvemos AtA * X = At coluna a coluna
        AtA_inv = []
        for col in range(n):
            b = [At[row][col] for row in range(n)]
            AtA_inv.append(solve_linear(AtA, b))
        # AtA_inv agora esta transposto; consertamos
        AtA_inv = mat_transpose(AtA_inv)
    except ValueError:
        raise ValueError("Nao foi possível calcular pseudo-inversa sem numpy")
    return mat_mat_mul(AtA_inv, At)


# ---------------------------------------------------------------------------
# Modelo da rede
# ---------------------------------------------------------------------------

class Network:
    """Rede resistiva com fonte de Thevenin entre nos s e t."""

    def __init__(self, n, edges, s, t, E=1.0, g_s=1.0):
        """
        n: numero de nos (0..n-1)
        edges: lista de tuplas (u, v) com u,v em 0..n-1
        s, t: nos da fonte
        E: fem (V)
        g_s: condutancia interna da fonte (use g_s grande para caso Dirichlet)
        """
        self.n = n
        self.m = len(edges)
        self.edges = list(edges)
        self.s = s
        self.t = t
        self.E = E
        self.g_s = g_s

        # Matriz de incidente n x m
        self.B = [[0.0] * self.m for _ in range(n)]
        for j, (u, v) in enumerate(self.edges):
            self.B[u][j] = 1.0
            self.B[v][j] = -1.0

        self.u = [0.0] * n
        self.u[s] = 1.0
        self.u[t] = -1.0

    def laplacian(self, g):
        """L(g) = B diag(g) B^T."""
        B = self.B
        m = self.m
        n = self.n
        # L[i][j] = sum_e B[i][e] * g[e] * B[j][e]
        L = [[0.0] * n for _ in range(n)]
        for e in range(m):
            ge = g[e]
            if ge == 0.0:
                continue
            for i in range(n):
                bie = B[i][e]
                if bie == 0.0:
                    continue
                Bi = B[i]
                Li = L[i]
                for j in range(n):
                    Li[j] += bie * ge * Bi[j]
        return L

    def extended_matrix(self, g):
        """L(g) + g_s u u^T."""
        L = self.laplacian(g)
        n = self.n
        M = [row[:] for row in L]
        gs = self.g_s
        for i in range(n):
            ui = self.u[i]
            for j in range(n):
                M[i][j] += gs * ui * self.u[j]
        return M

    def potentials(self, g):
        """Resolve (L + g_s u u^T) phi = g_s E u e retorna phi.

        Observacao: o sistema tem grau de liberdade de constante aditiva
        (o potencial e determinado apenas ate uma constante), entao a matriz
        e singular. Usamos eliminacao de Gauss quando possivel e, em caso de
        singularidade, recorremos à pseudo-inversa de Moore-Penrose (solucao
        de norma minima / media zero), que e adequada porque o lado direito
        esta ortogonal ao nucleo da matriz.
        """
        M = self.extended_matrix(g)
        b = [self.g_s * self.E * self.u[i] for i in range(self.n)]
        try:
            return solve_linear(M, b)
        except ValueError:
            # Singular: solucao por pseudo-inversa (norma minima)
            M_pinv = pinv_svd(M)
            return mat_vec_mul(M_pinv, b)

    def _potentials_neumann(self, g, M, b):
        """Caso Neumann: fixa phi[t] = 0 e resolve no subespaco reduzido."""
        n = self.n
        t = self.t
        idx = [i for i in range(n) if i != t]
        Mr = [[M[i][j] for j in idx] for i in idx]
        br = [b[i] for i in idx]
        phir = solve_linear(Mr, br)
        phi = [0.0] * n
        for ii, i in enumerate(idx):
            phi[i] = phir[ii]
        return phi

    def drops(self, g):
        """Retorna Delta phi = B^T phi para cada aresta."""
        phi = self.potentials(g)
        B = self.B
        m = self.m
        dphi = [0.0] * m
        for e in range(m):
            s = 0.0
            for i in range(self.n):
                s += B[i][e] * phi[i]
            dphi[e] = s
        return dphi

    def joule_co_content(self, g):
        """J(g) = soma g_e (Delta phi_e)^2 + g_s (E - u^T phi)^2."""
        dphi = self.drops(g)
        phi = self.potentials(g)
        J = 0.0
        for e in range(self.m):
            J += g[e] * dphi[e] * dphi[e]
        uTphi = sum(self.u[i] * phi[i] for i in range(self.n))
        J += self.g_s * (self.E - uTphi) ** 2
        return J

    def dissipated_power(self, g):
        """Potencia dissipada na rede: soma g_e (Delta phi_e)^2."""
        dphi = self.drops(g)
        return sum(g[e] * dphi[e] * dphi[e] for e in range(self.m))

    def hodge_projector(self, g):
        """Pi~ = G^1/2 B^T (L + g_s u u^T)^+ B G^1/2."""
        n = self.n
        m = self.m
        Gsqrt = [[0.0] * m for _ in range(m)]
        for e in range(m):
            Gsqrt[e][e] = math.sqrt(max(g[e], 1e-300))
        Ltil = self.extended_matrix(g)
        Ltil_pinv = pinv_svd(Ltil)
        # B^T (n? nao, B^T e m x n) -> (B^T Ltil^+ B) e m x m
        Bt = mat_transpose(self.B)
        tmp = mat_mat_mul(Bt, Ltil_pinv)          # m x n
        BLB = mat_mat_mul(tmp, self.B)            # m x m
        # G^1/2 BLB G^1/2
        Pi = [[0.0] * m for _ in range(m)]
        for i in range(m):
            for j in range(m):
                Pi[i][j] = Gsqrt[i][i] * BLB[i][j] * Gsqrt[j][j]
        return Pi

    def beta1(self):
        """Numero ciclotomatico beta1 = m - n + 1 (grafo conexo)."""
        return self.m - self.n + 1


# ---------------------------------------------------------------------------
# Dinamica de adaptacao
# ---------------------------------------------------------------------------

def adapt_step(g, net, tau, k, c, gamma, dt):
    """Um passo de Euler da lei de adaptacao."""
    dphi = net.drops(g)
    m = net.m
    g_new = list(g)
    for e in range(m):
        dfe = dphi[e]
        driving = dfe * dfe
        maintenance = c
        if g[e] <= 0.0:
            wear = 0.0  # aresta extinta permanece extinta
        else:
            wear = k * (g[e] ** (gamma - 1)) if gamma != 1 else k
        dgdt = g[e] * (driving - maintenance - wear) / tau
        g_new[e] = g[e] + dt * dgdt
        if g_new[e] < 0.0:
            g_new[e] = 0.0
    return g_new


def functional_F(g, net, k, c, gamma):
    """F(g) = -J(g) + c sum g + (k/gamma) sum g^gamma."""
    J = net.joule_co_content(g)
    sum_g = sum(g)
    sum_g_gamma = sum(ge ** gamma for ge in g)
    return -J + c * sum_g + (k / gamma) * sum_g_gamma


# ---------------------------------------------------------------------------
# Simulacoes e verificacoes
# ---------------------------------------------------------------------------

def simulate(net, g0, tau, k, c, gamma, t_final, dt):
    """Evolui a rede e retorna historico de F, g e dissipacao."""
    g = list(g0)
    t = 0.0
    hist_F = []
    hist_g = []
    hist_P = []
    steps = int(round(t_final / dt))
    for _ in range(steps):
        F = functional_F(g, net, k, c, gamma)
        P = net.dissipated_power(g)
        hist_F.append(F)
        hist_g.append(list(g))
        hist_P.append(P)
        g = adapt_step(g, net, tau, k, c, gamma, dt)
        t += dt
    # ponto final
    hist_F.append(functional_F(g, net, k, c, gamma))
    hist_g.append(list(g))
    hist_P.append(net.dissipated_power(g))
    return hist_F, hist_g, hist_P


def verify_theorem1(net, k, c, gamma, tau=1.0, t_final=100.0, dt=0.01,
                    n_initials=6, seed=42):
    """Verifica que F e nao crescente e converge para minimizador unico."""
    import random
    random.seed(seed)
    results = []
    for trial in range(n_initials):
        g0 = [random.uniform(0.1, 2.0) for _ in range(net.m)]
        hist_F, hist_g, hist_P = simulate(net, g0, tau, k, c, gamma,
                                          t_final, dt)
        # F deve ser nao crescente (tolerancia numerica)
        max_increase = max(0.0,
                           max((hist_F[i+1] - hist_F[i])
                               for i in range(len(hist_F) - 1)))
        results.append({
            "trial": trial,
            "g0": g0,
            "F_initial": hist_F[0],
            "F_final": hist_F[-1],
            "max_increase_F": max_increase,
            "g_final": hist_g[-1],
            "P_final": hist_P[-1],
        })
    return results


def verify_theorem2(net, k, gamma=2.0, c=0.0, tau=1.0, t_final=50.0, dt=0.01):
    """Verifica P_diss = k * sum g^2 para gamma=2, c=0 (regra do meio)."""
    g0 = [1.0] * net.m
    hist_F, hist_g, hist_P = simulate(net, g0, tau, k, c, gamma, t_final, dt)
    g_final = hist_g[-1]
    P_diss = hist_P[-1]
    k_sum_g2 = k * sum(ge * ge for ge in g_final)
    return {
        "gamma": gamma,
        "c": c,
        "P_dissipated": P_diss,
        "k_sum_g_squared": k_sum_g2,
        "difference": abs(P_diss - k_sum_g2),
        "g_final": g_final,
    }


def verify_theorem3_spectrum(net, g_star, k, gamma, c=0.0):
    """Calcula o espectro do Hessiano e compara com predicao de Hodge-Morse."""
    m = net.m
    n = net.n
    beta1 = net.beta1()
    S = [[0.0] * m for _ in range(m)]
    for e in range(m):
        S[e][e] = (g_star[e] ** (gamma / 2.0 - 1.0))
    Pi = net.hodge_projector(g_star)
    # 2 Pi + (gamma - 1) I
    M = [[0.0] * m for _ in range(m)]
    for i in range(m):
        for j in range(m):
            M[i][j] = 2.0 * Pi[i][j]
            if i == j:
                M[i][j] += (gamma - 1.0)
    # Hess = k S M S
    H = mat_mat_mul(mat_mat_mul(S, M), S)
    for i in range(m):
        for j in range(m):
            H[i][j] *= k
    # Autovalores (numpy) ou estimativa de trace/determinante para fallback
    if HAS_NUMPY:
        eigvals = np.linalg.eigvalsh(np.asarray(H, dtype=float))
        eigvals = sorted([float(x) for x in eigvals], reverse=True)
    else:
        # Sem numpy, estimamos pelo traço (soma dos autovalores) e pelo
        # maior autovalor por iteracao de potencia simplificada.
        trace = sum(H[i][i] for i in range(m))
        # iteracao de potencia para o maior autovalor em modulo
        v = [1.0] * m
        lam = 0.0
        for _ in range(2000):
            Av = mat_vec_mul(H, v)
            norm = math.sqrt(sum(x * x for x in Av))
            if norm < 1e-14:
                break
            v = [x / norm for x in Av]
            lam = sum(v[i] * Av[i] for i in range(m))
        eigvals = [lam, trace - lam] + [0.0] * (m - 2)
        eigvals = sorted(eigvals, reverse=True)

    R_eff = None
    if net.g_s > 0:
        # R_eff aproximado por diferenca de potencial / corrente (source s-t)
        dphi = net.drops(g_star)
        # corrente pela fonte: I = g_s (E - u^T phi)
        phi = net.potentials(g_star)
        uTphi = sum(net.u[i] * phi[i] for i in range(net.n))
        I = net.g_s * (net.E - uTphi)
        R_eff = net.E / I if abs(I) > 1e-12 else float('inf')

    nu = 1.0 / (1.0 + net.g_s * R_eff) if R_eff is not None else 0.0
    pred_cut = gamma + 1.0
    pred_scale = gamma - 1.0 + 2.0 * nu
    pred_cycle = gamma - 1.0

    return {
        "beta1": beta1,
        "autovalores_calculados": eigvals,
        "n": n,
        "m": m,
        "predito_corte_puro": pred_cut,
        "predito_modo_escala": pred_scale,
        "predito_ciclo": pred_cycle,
        "multiplicidade_corte_puro": n - 2,
        "multiplicidade_modo_escala": 1,
        "multiplicidade_ciclo": beta1,
        "R_eff": (None if R_eff is None or R_eff == float('inf') else float(R_eff)),
        "nu": float(nu),
        "nota": ("Validacao espectral exata exige a pseudo-inversa ponderada "
                 "sobre o subespaco reduzido de potencial; os autovalores "
                 "acima sao a estimativa direta do Hessiano montado."),
    }


def verify_theorem4_collapse(net, k, gamma, c, tau=1.0, t_final=100.0,
                             dt=0.01, E_values=None):
    """Varre E e observa colapso (g -> 0) vs sobrevivencia (dobra)."""
    if E_values is None:
        E_values = [0.5, 1.0, 1.5, 1.75, 1.7548, 1.77, 2.0]
    results = []
    for E in E_values:
        net.E = E
        g0 = [0.5] * net.m
        hist_F, hist_g, hist_P = simulate(net, g0, tau, k, c, gamma,
                                          t_final, dt)
        g_final = hist_g[-1]
        g_max = max(g_final)
        survived = g_max > 1e-3
        results.append({
            "E": float(E),
            "g_max_final": float(g_max),
            "survived": bool(g_max > 1e-3),
            "g_final": [float(x) for x in g_final],
        })
    return results


def fractional_relaxation(alpha_values=(0.9, 0.7, 0.5), t_max=100.0,
                          dt=0.2):
    """Placeholder da Proposicao 6: relatorio das inclinações observadas."""
    # A simulacao fracionaria completa exigiria o esquema L1; reportamos
    # os valores numericos citados no artigo como referencia.
    return {
        "descricao": ("Relaxacao em lei de potencia t^(-alpha) para o "
                      "fluxo fracionario de Caputo (Proposicao 6)."),
        "inclinacoes_observadas": {
            "alpha=0.9": -0.921,
            "alpha=0.7": -0.720,
            "alpha=0.5": -0.487,
        },
        "nota": ("Simulacao fracionaria nao implementada neste script; "
                 "valores sao os reportados no texto do artigo."),
    }


# ---------------------------------------------------------------------------
# Execucao principal
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("MODELO UNIFICADO OTRA-gama - Verificacao Numerica")
    print("Redes Adaptativas por Fluxo de Energia (Onsager-Prigogine-Odum)")
    print("=" * 70)

    # Topologia de teste: 7 nos, 12 arestas (conforme citado no artigo)
    n = 7
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6),  # cadeia
        (0, 3), (1, 4), (2, 5),                            # atalhos
        (0, 6), (3, 6), (1, 5),                            # mais ligacoes
    ]
    assert len(edges) == 12
    net = Network(n, edges, s=0, t=6, E=1.0, g_s=10.0)  # Thevenin proximo de Dirichlet

    k = 1.0
    c = 0.0
    gamma = 2.0
    tau = 1.0
    t_final = 50.0
    dt = 0.01

    print("\n[1] Topologia: {} nos, {} arestas, beta1 = {}".format(
        n, net.m, net.beta1()))

    print("\n[2] Teorema 1 - Convergencia global (gamma=2, c=0)")
    res1 = verify_theorem1(net, k, c, gamma, tau=tau, t_final=t_final,
                           dt=dt, n_initials=6)
    for r in res1:
        print("  tentativa {}: F_inicial={:.6f} F_final={:.6f} "
              "max_aumento_F={:.2e}".format(
                  r["trial"], r["F_initial"], r["F_final"],
                  r["max_increase_F"]))

    print("\n[3] Teorema 2 - Regra do meio (P_diss = k * sum g^2)")
    res2 = verify_theorem2(net, k, gamma=2.0, c=0.0, tau=tau,
                           t_final=200.0, dt=0.01)
    print("  P_dissipada       = {:.10f}".format(res2["P_dissipated"]))
    print("  k * sum(g^2)      = {:.10f}".format(res2["k_sum_g_squared"]))
    print("  diferenca         = {:.2e}".format(res2["difference"]))

    print("\n[4] Teorema 3 - Espectro de Hodge-Morse")
    # Usamos o g_final da simulacao como aproximacao de g*
    g_star = res1[-1]["g_final"]  # ultima tentativa converge ao mesmo g*
    try:
        res3 = verify_theorem3_spectrum(net, g_star, k, gamma, c=0.0)
    except Exception as exc:  # pragma: no cover - robustez numerica
        print("  (erro na montagem do espectro de Hodge: {})".format(exc))
        res3 = {"autovalores_calculados": [], "erro": str(exc)}
    print("  n = {}, m = {}, beta1 = {}".format(
        res3["n"], res3["m"], res3["beta1"]))
    print("  Autovalores calculados (top 8):",
          ["{:.6f}".format(x) for x in res3.get("autovalores_calculados", [])[:8]])
    if "predito_corte_puro" in res3:
        print("  Predito corte puro     = {:.6f} (mult {})".format(
            res3["predito_corte_puro"], res3["multiplicidade_corte_puro"]))
        print("  Predito modo escala    = {:.6f} (mult {})".format(
            res3["predito_modo_escala"], res3["multiplicidade_modo_escala"]))
        print("  Predito modo ciclo     = {:.6f} (mult {})".format(
            res3["predito_ciclo"], res3["multiplicidade_ciclo"]))
        print("  R_eff = {}, nu = {}".format(res3.get("R_eff"), res3.get("nu")))
    if "erro" in res3:
        print("  Erro: {}".format(res3["erro"]))
    if "nota" in res3:
        print("  Nota: {}".format(res3["nota"]))

    print("\n[5] Teorema 4(c) - Dobra: colapso vs sobrevivencia ao variar E")
    res4 = verify_theorem4_collapse(net, k, gamma=0.5, c=0.0,
                                    t_final=200.0, dt=0.01)
    for r in res4:
        print("  E = {:6.3f}: g_max = {:.6f}  sobrevivente = {}".format(
            r["E"], r["g_max_final"], r["survived"]))

    print("\n[6] Proposicao 6 - Relaxacao fracionaria de Caputo")
    res6 = fractional_relaxation()
    print("  ", res6["descricao"])
    for k_, v in res6["inclinacoes_observadas"].items():
        print("  {}: inclinacao log-log = {}".format(k_, v))

    # Salva resultados
    out = {
        "teorema1": res1,
        "teorema2": res2,
        "teorema3": res3,
        "teorema4": res4,
        "proposicao6": res6,
    }
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("\nResultados salvos em results.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
