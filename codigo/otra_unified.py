"""
OTRA unificado: redes adaptativas por fluxo de energia (Onsager-Prigogine-Odum)

Pacote de reproducao numerica do artigo:
"Redes Adaptativas por Fluxo de Energia: um modelo unificado Onsager-Prigogine-Odum,
com teoremas de Lyapunov, indice de Morse de Hodge e bifurcacoes exatas"

Lei de adaptacao (unica):
    tau * dg_e/dt = g_e * ( dphi_e^2 - c - k * g_e^(gamma-1) )
Fonte de Thevenin (E, gs):  gs = inf -> Dirichlet (potencial fixo)
                            gs -> 0 com I = gs*E fixo -> Neumann (corrente fixa)
Funcional de Lyapunov:
    F(g) = -J(g) + c*sum(g) + (k/gamma)*sum(g^gamma),
    J = min_phi [ sum g dphi^2 + gs (E - dphi_st)^2 ]

Testes implementados (Teoremas 1-4, Proposicao 6):
  A   Teorema 1 (Lyapunov / convergencia global)        -> fig1_lyapunov.png
  B   Teorema 3 (Hodge-Morse / espectro do Hessiano)    -> (sem fig)
  pitch  Teorema 4(a) (pitchfork em gamma=1)            -> fig2_pitchfork.png
  chain  Teorema 4(d) (transcritica em cadeia)          -> fig3_chain.png
  fold   Teorema 4(c) (dobra exata / biestabilidade)    -> fig4_fold.png
  frac   Proposicao 6 (memoria fracionaria de Caputo)   -> fig5_fractional.png

Uso:
    python otra_unified.py                 # roda todos os testes (A, B, pitch, chain, fold, frac)
    python otra_unified.py A B fold        # roda somente os testes indicados

Dependencias: numpy, scipy, matplotlib.
Saida:  papers/01-paper-principal/figuras/fig*.png  (figuras)
        codigo/results.json                        (numeros consolidados citados no artigo)
"""

import sys
import json
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize, fsolve, brentq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": .25, "figure.dpi": 130})

# Caminhos relativos ao repositorio (este script fica em codigo/)
ROOT   = Path(__file__).resolve().parent.parent
FIGDIR = ROOT / "papers" / "01-paper-principal" / "figuras"
RESFILE = ROOT / "codigo" / "results.json"
FIGDIR.mkdir(parents=True, exist_ok=True)

FIG = str(FIGDIR) + "/"
RES = {}

# ----------------------------------------------------------------- rede
class Net:
    def __init__(self, n, edges, s, t, mode="neumann", E=1.0, gs=1.0, I=1.0, k=1.0, gamma=2.0, c=0.0):
        self.n, self.edges, self.s, self.t = n, edges, s, t
        self.m = len(edges)
        B = np.zeros((n, self.m))
        for e, (i, j) in enumerate(edges):
            B[i, e], B[j, e] = 1, -1
        self.B = B
        self.mode, self.E, self.gs, self.I = mode, E, gs, I
        self.k, self.gamma, self.c = k, gamma, c

    def potentials(self, g):
        """devolve phi (n,), com phi_t = 0"""
        n, s, t, B = self.n, self.s, self.t, self.B
        L = B @ np.diag(g) @ B.T
        keep = [v for v in range(n) if v != t]
        Lr = L[np.ix_(keep, keep)].copy()
        rhs = np.zeros(n - 1)
        si = keep.index(s)
        if self.mode == "neumann":
            rhs[si] = self.I
        elif self.mode == "dirichlet":
            # elimina no s: phi_s = E
            idx = [i for i in range(n - 1) if i != si]
            phi_r = np.zeros(n - 1)
            phi_r[si] = self.E
            if idx:
                rhs_i = -Lr[np.ix_(idx, [si])][:, 0] * self.E
                phi_r[idx] = np.linalg.solve(Lr[np.ix_(idx, idx)] + 1e-300 * np.eye(len(idx)), rhs_i)
            phi = np.zeros(n)
            phi[keep] = phi_r
            return phi
        else:  # thevenin
            Lr[si, si] += self.gs
            rhs[si] = self.gs * self.E
        phi_r = np.linalg.solve(Lr, rhs)
        phi = np.zeros(n)
        phi[keep] = phi_r
        return phi

    def dphi(self, g):
        return self.B.T @ self.potentials(g)

    def J(self, g):
        """co-conteudo: dissipacao (Dirichlet/Thevenin) ou -P_N (Neumann)"""
        phi = self.potentials(g)
        d = self.B.T @ phi
        dst = phi[self.s] - phi[self.t]
        if self.mode == "neumann":
            return -self.I * dst            # = -P_N
        if self.mode == "dirichlet":
            return float(np.sum(g * d ** 2))
        return float(np.sum(g * d ** 2) + self.gs * (self.E - dst) ** 2)

    def F(self, g):
        g = np.maximum(g, 0)
        return -self.J(g) + self.c * g.sum() + self.k / self.gamma * np.sum(g ** self.gamma)

    def gradF(self, g):
        return -self.dphi(g) ** 2 + self.c + self.k * np.maximum(g, 1e-300) ** (self.gamma - 1)

    def rhs_logg(self, tau=1.0):
        def f(_, u):
            g = np.exp(u)
            return (self.dphi(g) ** 2 - self.c - self.k * g ** (self.gamma - 1)) / tau
        return f

    def run(self, g0, T, tau=1.0, npts=400, tt=None, gmin=1e-9):
        """Integra em u=log g. Para gamma<1 as arestas extinguem em tempo finito: evento terminal
        quando g_e < gmin; a aresta e declarada extinta (g=0) e a integracao continua na subrede."""
        tt = np.linspace(0, T, npts) if tt is None else np.asarray(tt)
        alive = np.ones(self.m, bool)
        u = np.log(np.asarray(g0, float)) if self.gamma >= 1 else np.asarray(g0, float) ** (1 - self.gamma)
        t0 = 0.0
        Tt, Gg = [], []
        while True:
            idx = np.where(alive)[0]
            if self.gamma >= 1:
                def f(_, w, idx=idx):
                    g = np.zeros(self.m); g[idx] = np.exp(w)
                    d = self.dphi(g)[idx]
                    return (d ** 2 - self.c - self.k * np.exp(w * (self.gamma - 1))) / tau
                ev = lambda _, w: np.min(w) - np.log(gmin)
                to_g, meth, thr = np.exp, "LSODA", np.log(gmin)
            else:   # gamma<1: x = g^(1-gamma) regulariza a extincao em tempo finito (x_dot = (1-gamma)(x(dphi^2-c)-k))
                p = 1.0 / (1.0 - self.gamma)
                def f(_, w, idx=idx, p=p):
                    xi = np.maximum(w, 0.0)
                    g = np.zeros(self.m); g[idx] = xi ** p
                    d = self.dphi(g)[idx]
                    return (1 - self.gamma) * (xi * (d ** 2 - self.c) - self.k) / tau
                ev = lambda _, w: np.min(w) - 1e-9
                to_g, meth, thr = (lambda w, p=p: np.maximum(w, 0.0) ** p), "RK45", 1e-9
            # evento terminal apenas quando ha extincao de arestas (gamma<1);
            # para gamma>=1 nao ha extincao, entao nao e terminal (evita brentq
            # sem mudanca de sinal em versoes recentes do scipy)
            ev.terminal = (self.gamma < 1)
            tsel = tt[tt >= t0]
            sol = solve_ivp(f, (t0, tt[-1]), u[idx], t_eval=tsel, method=meth, rtol=1e-9, atol=1e-12, events=ev)
            for j in range(len(sol.t)):
                g = np.zeros(self.m); g[idx] = to_g(sol.y[:, j]); Tt.append(sol.t[j]); Gg.append(g)
            if sol.status != 1:
                break
            wlast = sol.y_events[0][-1]; tev = sol.t_events[0][-1]
            alive[idx[wlast <= thr * (1 + 1e-3) + 1e-12]] = False
            gev = np.zeros(self.m); gev[idx] = to_g(wlast); gev[~alive] = 0.0
            Tt.append(float(tev)); Gg.append(gev)
            if not alive.any():
                break
            t0 = float(tev)
            u = np.full(self.m, -1e3 if self.gamma >= 1 else 0.0); u[idx] = wlast
        Tt, Gg = np.array(Tt), np.array(Gg).T
        if Tt[-1] < tt[-1] - 1e-9:
            extra = tt[tt > Tt[-1]]
            Tt = np.concatenate([Tt, extra]); Gg = np.hstack([Gg, np.tile(Gg[:, [-1]], (1, len(extra)))])
        return Tt, Gg

    def minimizer(self, g0):
        r = minimize(self.F, g0, jac=self.gradF, method="L-BFGS-B", bounds=[(0, None)] * self.m,
                     options=dict(ftol=1e-15, gtol=1e-12, maxiter=5000))
        return r.x


def Reff(net, g):
    L = net.B @ np.diag(g) @ net.B.T
    u = np.zeros(net.n); u[net.s], u[net.t] = 1, -1
    return float(u @ np.linalg.pinv(L) @ u)


def rand_graph(n, m, seed):
    rng = np.random.default_rng(seed)
    edges = [(i, i + 1) for i in range(n - 1)]                      # espinha conexa
    while len(edges) < m:
        i, j = sorted(rng.choice(n, 2, replace=False))
        if (i, j) not in edges:
            edges.append((int(i), int(j)))
    return edges


# ----------------------------------------------------------------- T1 Teorema A (Lyapunov / convergencia global)
def test_theorem_A():
    out = {}
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))
    for col, (mode, kw) in enumerate([("neumann", dict(I=1.0)), ("dirichlet", dict(E=1.0)), ("thevenin", dict(E=1.0, gs=2.0))]):
        n, m = 7, 12
        edges = rand_graph(n, m, 3)
        net = Net(n, edges, 0, n - 1, mode=mode, k=1.0, gamma=2.0, **kw)
        rng = np.random.default_rng(11)
        worst_mono, dist = 0.0, []
        for r in range(6):
            g0 = rng.uniform(0.05, 3.0, m)
            tt, G = net.run(g0, 60, npts=600)
            Fs = np.array([net.F(G[:, i]) for i in range(len(tt))])
            worst_mono = max(worst_mono, float(np.max(np.diff(Fs))))
            gstar = net.minimizer(G[:, -1])
            dist.append(float(np.max(np.abs(G[:, -1] - gstar))))
            ax[col].plot(tt, Fs - net.F(gstar), lw=1.2)
        ax[col].set_yscale("log"); ax[col].set_title(f"{mode}: F(t) - F*"); ax[col].set_xlabel("t")
        gst = net.minimizer(np.ones(m))
        dph = net.dphi(gst)
        P = float(np.sum(gst * dph ** 2))
        out[mode] = dict(max_dF_dt_positive=worst_mono, max_dist_to_minimizer=max(dist),
                         P_diss=P, k_sum_g2=float(net.k * np.sum(gst ** 2)), n_pruned=int(np.sum(gst < 1e-6)))
    plt.tight_layout(); plt.savefig(FIG + "fig1_lyapunov.png"); plt.close()
    RES["theorem_A"] = out


# ----------------------------------------------------------------- T2 Teorema B (Hodge-Morse / espectro do Hessiano)
def hessF_numeric(net, g, h=1e-6):
    m = len(g); H = np.zeros((m, m))
    for j in range(m):
        gp, gm = g.copy(), g.copy()
        gp[j] += h; gm[j] -= h
        H[:, j] = (net.gradF(gp) - net.gradF(gm)) / (2 * h)
    return (H + H.T) / 2


def test_theorem_B():
    out = {}
    # (i) gamma>1 : minimizador interior numa rede com ciclos (neumann)
    n = 6
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5), (2, 4)]
    m = len(edges); beta1 = m - n + 1
    for gam in (1.5, 3.0):
        net = Net(n, edges, 0, n - 1, mode="neumann", I=1.0, k=1.0, gamma=gam)
        tt, G = net.run(np.ones(m), 400, npts=50)
        g = G[:, -1]
        grad = np.max(np.abs(net.gradF(g)))
        S = np.diag(g ** (gam / 2 - 1))
        H = hessF_numeric(net, g)
        M = np.linalg.inv(S) @ H @ np.linalg.inv(S) / net.k
        ev = np.sort(np.linalg.eigvalsh((M + M.T) / 2))
        out[f"neumann_gamma{gam}"] = dict(grad_inf=float(grad), n=n, m=m, beta1=beta1,
                                          eig_min=float(ev[0]), predicted_cycle=gam - 1, predicted_cut=gam + 1,
                                          n_eig_cycle=int(np.sum(np.abs(ev - (gam - 1)) < 1e-3)),
                                          n_eig_cut=int(np.sum(np.abs(ev - (gam + 1)) < 1e-3)),
                                          n_interior=int(np.sum(g > 1e-4)))
    # (ii) gamma<1 : ponto estacionario interior (sela) em grafo simetrico: losango, beta1 = 1
    edges2 = [(0, 1), (0, 2), (1, 3), (2, 3)]     # losango, beta1 = 1
    m2 = 4; n2 = 4
    gam = 0.5
    net = Net(n2, edges2, 0, 3, mode="neumann", I=1.0, k=1.0, gamma=gam)
    sol = brentq(lambda x: net.gradF(np.full(m2, x))[0], 1e-3, 50.0)
    g = np.full(m2, sol)
    S = np.diag(g ** (gam / 2 - 1))
    H = hessF_numeric(net, g)
    M = np.linalg.inv(S) @ H @ np.linalg.inv(S) / net.k
    ev = np.sort(np.linalg.eigvalsh((M + M.T) / 2))
    out["neumann_gamma0.5_diamond"] = dict(grad_inf=float(np.max(np.abs(net.gradF(g)))), eig=ev.tolist(),
                                           predicted=[gam - 1] * 1 + [gam + 1] * 3, beta1=1)
    # (iii) Thevenin: espectro com modo de escala
    gam = 0.7; gs = 3.0
    net = Net(n2, edges2, 0, 3, mode="thevenin", E=8.0, gs=gs, k=1.0, gamma=gam)
    sol = brentq(lambda x: net.gradF(np.full(m2, x))[0], 1e-3, 50.0)
    g = np.full(m2, sol)
    R = Reff(net, g)
    S = np.diag(g ** (gam / 2 - 1))
    H = hessF_numeric(net, g)
    M = np.linalg.inv(S) @ H @ np.linalg.inv(S) / net.k
    ev = np.sort(np.linalg.eigvalsh((M + M.T) / 2))
    pred = sorted([gam - 1] + [gam + 1] * (n2 - 2) + [gam - 1 + 2 / (1 + gs * R)])
    out["thevenin_gamma0.7_diamond"] = dict(grad_inf=float(np.max(np.abs(net.gradF(g)))), eig=ev.tolist(), predicted=pred,
                                            gs_R=gs * R)
    RES["theorem_B"] = out


# ----------------------------------------------------------------- T3 pitchfork em gamma=1 (2 arestas paralelas)
def test_pitchfork():
    gams = np.linspace(0.5, 1.5, 21)
    asym = []
    for gam in gams:
        net = Net(2, [(0, 1), (0, 1)], 0, 1, mode="neumann", I=1.0, k=1.0, gamma=gam)
        tt, G = net.run(np.array([1.0, 1.02]), 400, npts=40)
        g = G[:, -1]
        asym.append(float((g[0] - g[1]) / g.sum()))
    fig, ax = plt.subplots(figsize=(5.8, 3.8))
    ax.plot(gams, np.abs(asym), "o-")
    ax.axvline(1.0, color="r", ls="--", label=r"$\gamma_c = 1$")
    ax.set_xlabel(r"expoente do custo de manutencao $\gamma$"); ax.set_ylabel(r"$|g_1-g_2|/(g_1+g_2)$")
    ax.set_title("2 canais paralelos (Neumann): perda de simetria"); ax.legend()
    plt.tight_layout(); plt.savefig(FIG + "fig2_pitchfork.png"); plt.close()
    RES["pitchfork"] = dict(gamma=gams.tolist(), asym=asym)


# ----------------------------------------------------------------- T4 transcritica em cadeia (Dirichlet + custo linear c)
def test_chain_transcritical():
    c, k = 0.25, 1.0
    fig, ax = plt.subplots(figsize=(6.2, 4))
    out = {}
    for N in (1, 2, 3, 4):
        edges = [(i, i + 1) for i in range(N)]
        Vs = np.linspace(0.05, 5.0, 40)
        gnum, gth = [], []
        for V in Vs:
            net = Net(N + 1, edges, 0, N, mode="dirichlet", E=V, k=k, gamma=2.0, c=c)
            tt, G = net.run(np.full(N, 0.5), 400, npts=20)
            gnum.append(float(G[:, -1].mean()))
            gth.append(max(((V / N) ** 2 - c) / k, 0.0))
        ax.plot(Vs, gnum, "o", ms=3.5, color=f"C{N-1}")
        ax.plot(Vs, gth, "-", color=f"C{N-1}", label=f"N={N}: $V_c=N\\sqrt{{c}}={N*np.sqrt(c):.2f}$")
        out[N] = dict(max_abs_err=float(np.max(np.abs(np.array(gnum) - np.array(gth)))), Vc=float(N * np.sqrt(c)))
    ax.set_xlabel("V (potencial imposto)"); ax.set_ylabel(r"$g^*$ (condutancia por aresta)")
    ax.set_title("Emergencia de canais: transcritica exata em V_c = N sqrt(c)"); ax.legend(fontsize=8)
    plt.tight_layout(); plt.savefig(FIG + "fig3_chain.png"); plt.close()
    RES["chain_transcritical"] = out


# ----------------------------------------------------------------- T5 dobra exata (1 canal + fonte de Thevenin, gamma<1)
def test_fold():
    k, gs, gam = 1.0, 1.0, 0.5
    gc = gs * (1 - gam) / (1 + gam)
    Ec = 2 / (1 + gam) * np.sqrt(k) * gc ** ((gam - 1) / 2)
    out = dict(g_c=gc, E_c=float(Ec))
    surv = {}
    for E in (0.9 * Ec, 1.0 * Ec * 1.01, 1.15 * Ec):
        row = {}
        for g0 in (0.02, 0.2, 1.0, 3.0):
            net = Net(2, [(0, 1)], 0, 1, mode="thevenin", E=E, gs=gs, k=k, gamma=gam)
            tt, G = net.run(np.array([g0]), 200, npts=30)
            row[g0] = float(G[0, -1])
        surv[f"{E:.4f}"] = row
    out["final_g_by_E_and_g0"] = surv
    # diagrama de bifurcacao analitico: ramos estacionarios g(E)
    gg = np.linspace(1e-3, 3, 4000)
    Eg = np.sqrt(k) * gg ** ((gam - 1) / 2) * (gg + gs) / gs     # E(g) de dphi^2 = k g^(gam-1)
    stab = (gam - 1 + 2 * gg / (gg + gs)) > 0
    fig, ax = plt.subplots(figsize=(5.8, 3.9))
    ax.plot(Eg[stab], gg[stab], "b-", label="estavel"); ax.plot(Eg[~stab], gg[~stab], "r--", label="instavel (separatriz)")
    ax.axvline(Ec, color="k", ls=":"); ax.plot([Ec], [gc], "ko")
    ax.set_xlim(1.2, 3.2); ax.set_ylim(0, 3)
    ax.set_xlabel("E (forca imposta)"); ax.set_ylabel(r"$g^*$")
    ax.set_title(r"Dobra exata: $E_c=\frac{2\sqrt{k}}{1+\gamma}\,[g_s\frac{1-\gamma}{1+\gamma}]^{(\gamma-1)/2}$", fontsize=10)
    ax.legend(); plt.tight_layout(); plt.savefig(FIG + "fig4_fold.png"); plt.close()
    RES["fold"] = out


# ----------------------------------------------------------------- T6 memoria fracionaria (Caputo, L1)
def caputo_L1(f, y0, T, N, alpha):
    h = T / N
    t = np.linspace(0, T, N + 1)
    y = np.zeros((N + 1, len(y0))); y[0] = y0
    fv = np.zeros_like(y); fv[0] = f(y0)
    b = np.arange(1, N + 2) ** (1 - alpha) - np.arange(0, N + 1) ** (1 - alpha)   # b_j = (j+1)^(1-a) - j^(1-a)
    from math import gamma as Gam
    c0 = h ** (-alpha) / Gam(2 - alpha)
    for n in range(1, N + 1):
        dy = y[1:n] - y[0:n - 1]                  # dy[i] = y_{i+1}-y_i
        hist = (b[1:n][:, None] * dy[::-1]).sum(axis=0) if n > 1 else np.zeros(len(y0))
        y[n] = y[n - 1] - hist + fv[n - 1] / c0
        y[n] = np.maximum(y[n], 1e-12)
        fv[n] = f(y[n])
    return t, y


def test_fractional():
    n = 5
    edges = [(0, 1), (1, 4), (0, 2), (2, 4), (0, 3), (3, 4), (1, 2)]
    m = len(edges)
    net = Net(n, edges, 0, 4, mode="dirichlet", E=1.0, k=1.0, gamma=2.0)
    gstar = net.minimizer(np.ones(m))
    f = lambda g: g * (net.dphi(g) ** 2 - net.k * g)
    g0 = np.full(m, 0.9)
    out = {}
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.9))
    for a in (1.0, 0.9, 0.7, 0.5):
        N = 600
        T = 120.0
        if a == 1.0:
            tt, G = net.run(g0, T, npts=N + 1)
            G = G.T
        else:
            tt, G = caputo_L1(f, g0, T, N, a)
        err = np.linalg.norm(G - gstar, axis=1)
        Fs = np.array([net.F(G[i]) for i in range(len(tt))])
        ax[0].loglog(tt[1:], err[1:], label=f"alpha={a}")
        ax[1].semilogx(tt[1:], Fs[1:] - Fs.min() + 1e-14, label=f"alpha={a}")
        i0, i1 = int(0.3 * N), int(0.95 * N)
        sl = np.polyfit(np.log(tt[i0:i1]), np.log(err[i0:i1] + 1e-300), 1)[0] if a < 1 else None
        out[str(a)] = dict(F_monotone=bool(np.all(np.diff(Fs) <= 1e-10)), late_slope=None if sl is None else float(sl),
                           min_g=float(G.min()))
    ax[0].set_xlabel("t"); ax[0].set_ylabel(r"$\|g-g^*\|$"); ax[0].set_title("relaxacao: exponencial (a=1) x lei de potencia (a<1)")
    ax[1].set_xlabel("t"); ax[1].set_title("F(t) - F_min (nao crescente)")
    ax[1].set_yscale("log")
    ax[0].legend(); plt.tight_layout(); plt.savefig(FIG + "fig5_fractional.png"); plt.close()
    RES["fractional"] = out


if __name__ == "__main__":
    which = sys.argv[1:] or ["A", "B", "pitch", "chain", "fold", "frac"]
    fn = dict(A=test_theorem_A, B=test_theorem_B, pitch=test_pitchfork, chain=test_chain_transcritical,
              fold=test_fold, frac=test_fractional)
    for w in which:
        fn[w]()
        print(w, "ok", flush=True)
    # Salva resultados consolidados (versao do pacote de reproducao)
    with open(RESFILE, "w", encoding="utf-8") as f:
        json.dump(RES, f, indent=1, default=float)
    print(f"Resultados salvos em {RESFILE}")
    print(f"Figuras salvas em {FIGDIR}")
