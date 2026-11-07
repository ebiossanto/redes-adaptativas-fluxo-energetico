-- Lean 4 skeleton for the OTRA‑γ model
-- Imports Mathlib for basic mathematics (real numbers, lists, convexity, etc.)
import Mathlib

-- -------------------------------------------------------------------
-- 1.  Types modelling the network defined in `otra_unified.py`
-- -------------------------------------------------------------------

structure Net where
  -- number of nodes
  n : ℕ
  -- list of edges (i, j) where i, j are node indices
  edges : List (ℕ × ℕ)
  -- source and target nodes for the external source (s‑t)
  s t : ℕ
  -- operating mode: "neumann", "dirichlet" or "thevenin"
  mode : String
  -- external parameters: fem E, internal conductance g_s, imposed current I
  E gs I : ℝ
  -- model parameters appearing in the adaptation law
  k gamma c : ℝ

-- -------------------------------------------------------------------
-- 2.  Conductance vector  g  (list of non‑negative conductances)
-- -------------------------------------------------------------------

def conductance_vector (m : ℕ) := List.range m

-- -------------------------------------------------------------------
-- 3.  Functional  F(g)  (Lyapunov‑type cost)
-- -------------------------------------------------------------------
-- The exact expression from the paper is
--   F(g) = -J(g) + c·Σ g  + (k/γ)·Σ g^γ
-- where J(g) = min_φ Σ g_e (Δφ_e)² + g_s (E - (φ_s - φ_t))² .
-- Below we give a placeholder that mimics the shape of F.

def F (g : List ℝ) (net : Net) : ℝ :=
  let sum_g   := List.sum g in
  let power   := if net.gamma > 0 then
                     List.sum (List.map (λ x => x ^ net.gamma) g) / net.gamma
                 else 0,
  -sum_g + net.c * sum_g + net.k * power

-- -------------------------------------------------------------------
-- 4.  Convexity of the power term  x ↦ x^γ  for γ > 1
-- -------------------------------------------------------------------
-- The function φ(x) = x^γ is convex on [0, ∞) when γ > 1.
-- We state this as a lemma; its proof in Mathlib uses the fact that
-- the second derivative γ(γ‑1)x^{γ‑2} is non‑negative on [0,∞).

lemma convex_power {γ : ℝ} (hγ : γ > 1) :
  convex_on ℝ (λ x => x ^ γ) ℝ (λ h, cond h) := sorry
-- `cond h` denotes the proof that x ≥ 0; in a full development one would
-- restrict the domain to non‑negative reals.

-- -------------------------------------------------------------------
-- 5.  Global convergence for γ > 1
-- -------------------------------------------------------------------
-- When γ > 1 the functional F is strictly convex (the power term
-- dominates) and therefore admits a unique global minimiser, independently
-- of the initial guess.

theorem convex_F_for_gamma_gt_one :
  ∀ {γ : ℝ} (hγ : γ > 1) (net : Net),
    -- F(g) = -J(g) + c·Σg + (k/γ)·Σg^γ is strictly convex in g
    strict_convex_on ℝ (λ g => F g net) ℝ
    -- and therefore has a unique minimiser.
    ∃! (g* : List ℝ), F g* net ≤ F g net ∀ g : List ℝ := sorry
-- The proof would proceed by:
--   • using `convex_power hγ` to obtain convexity of the Σ g^γ term,
--   • noting that the linear terms (‑Σg + c·Σg) are affine, hence convex,
--   • combining convexity with `convex.sum` and `convex.comp`,
--   • applying `exists_unique_of_strict_convex` (Mathlib) to obtain the
--     unique global minimiser g*.

-- -------------------------------------------------------------------
-- 6.  Usage example (optional)
-- -------------------------------------------------------------------
-- After instantiating `Net` with concrete data (e.g. from the Python script),
-- one can apply the theorem to obtain the optimal conductance vector.

example {γ : ℝ} (hγ : γ > 1) (net : Net) (g0 : List ℝ) :
  -- g0 is any initial guess; the theorem guarantees a unique optimum.
  ∃! g*, g* = @convex_F_for_gamma_gt_one hγ net := sorry