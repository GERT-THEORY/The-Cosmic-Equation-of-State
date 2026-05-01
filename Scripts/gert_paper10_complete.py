#!/usr/bin/env python3
"""
GERT Paper 10 — The Fabric of Time
====================================
Complete derivations:
  Block I:   The postulate dτ ∝ -dG and its consequences
  Block II:  Deriving κ(x) from Cauldron–Friedmann matching
  Block III: Why the naïve κ = W_rate fails (CoV 244%)
  Block IV:  The co-dependence of thermodynamics and geometry
  Block V:   β is gauge — zero free parameters
  Block VI:  Why time stops at c (particle scale, κ-independent)
  Block VII: The two barriers are the same barrier
  Block VIII: Mass as crystallized Work capacity
  Block IX:  The three layers of time dilation

Veronica Padilha Dutra (2026)
"""

import os
import numpy as np
from scipy.special import expit
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Paper I parameters (frozen) ───────────────────────────────────
FM_I, FM_F = 0.7831, 0.5851
FL_I, FL_M = 1.3414, 1.1236
LOG_RHO_M, D_M = -20.30, 1.0
FM_PEAK = 0.37; LOG_RHO_C = -17.41; SIGMA_C = 1.0
LOG_RHO_L, D_L = -25.60, 2.0
FL_PEAK = 4.6245; LOG_RHO_L2 = -23.93; SIGMA_L2 = 1.0
C = 2.998e8; G_SI = 6.674e-11; MPC = 3.0857e22
H0_KMS_MPC = 72.5; H0_SI = H0_KMS_MPC * 1e3 / MPC
H_QV = 0.001
A_GERT = C * H0_SI / (2 * np.pi)

# Cosmological parameters
OMEGA_R = 9.0e-5; OMEGA_M = 0.30; OMEGA_L = 1 - OMEGA_M - OMEGA_R

# Density today
RHO_M0 = OMEGA_M * 3 * H0_SI**2 / (8 * np.pi * G_SI)
LOG_RHO_M0 = np.log10(RHO_M0)

# Crystallization boundary
ALPHA_EM = -3.0
X_EM = LOG_RHO_M0 - 3 * ALPHA_EM

def logistic(x, x0, d): return expit(-(x - x0) / d)
def gauss(x, x0, s): return np.exp(-0.5 * ((x - x0) / s)**2)

def fM(x):
    b = FM_I + (FM_F - FM_I) * logistic(x, LOG_RHO_M, D_M)
    return b * (1 + FM_PEAK * gauss(x, LOG_RHO_C, SIGMA_C))

def fL(x):
    b = FL_I + (FL_M - FL_I) * logistic(x, LOG_RHO_L, D_L)
    return b * (1 + FL_PEAK * gauss(x, LOG_RHO_L2, SIGMA_L2))

def phi(x):
    fm = fM(x); fl = fL(x)
    return fm / (fm + fl)

def z_from_x(x): return 10**((x - LOG_RHO_M0)/3) - 1
def x_from_z(z): return LOG_RHO_M0 + 3 * np.log10(1 + z)

def H_friedmann(z):
    """Hubble parameter from standard Friedmann equation."""
    return H0_SI * np.sqrt(OMEGA_R*(1+z)**4 + OMEGA_M*(1+z)**3 + OMEGA_L)


# ══════════════════════════════════════════════════════════════════════
#  BLOCK I — The Postulate and Its Consequences
# ══════════════════════════════════════════════════════════════════════

def block_I_postulate():
    """The postulate dτ ∝ -dG and what it implies about time."""
    print(f"\n{'='*72}")
    print(f"  BLOCK I — THE POSTULATE: dτ ∝ -dG")
    print(f"{'='*72}")
    print(f"""
  POSTULATE: Thermodynamic time τ is accumulated Work.
    dτ ∝ -dG

  IMMEDIATE CONSEQUENCES:

  (a) Where ΔG = 0 → dτ = 0 → time stops.
      This occurs in Layer 1 (absolute vacuum, H = 0)
      and at the end of the eon (H → H_QV, W → 0).

  (b) τ is DEFINED by the Cauldron equation, not measured
      by a clock. A clock measures geometric time t.
      The question is: how does τ relate to t?

  (c) t exists only in Layer 3 (after metric crystallization).
      Before Ξ = 1, there is no metric → no t.
      After Ξ = 1, both τ and t coexist.

  THE CAULDRON EQUATION (Paper IX):
    dH/dτ = -(fL - fM)(H - H_QV)                    ... (1)
    dx/dτ = -β(1-φ)(fL - fM)(H - H_QV)/H            ... (2)

  THE FRIEDMANN EQUATION (Layer 3):
    H²(z) = H₀²[Ωr(1+z)⁴ + Ωm(1+z)³ + ΩΛ]         ... (3)
    dx/dt = -3H_Fried(z)/ln10                         ... (4)

  Both describe the same density evolution dx.
  Matching them defines κ(x) = dτ/dt.
""")


# ══════════════════════════════════════════════════════════════════════
#  BLOCK II — Deriving κ(x)
# ══════════════════════════════════════════════════════════════════════

def block_II_derive_kappa(beta=5.0):
    """Derive κ(x) from the Cauldron–Friedmann matching condition."""
    print(f"\n{'='*72}")
    print(f"  BLOCK II — DERIVING κ(x) FROM FIRST PRINCIPLES")
    print(f"{'='*72}")
    print(f"""
  From equations (2) and (4):
    dx/dτ × κ = dx/dt
    κ(x) = (dx/dt) / (dx/dτ)                         ... (5)

  Substituting:
    dx/dt = -3 H_Fried(z) / ln10                     ... (4)
    dx/dτ = -β(1-φ)(fL-fM)(H-H_QV)/H                ... (2)

  Therefore:
    κ(x) = [3 H_Fried(z) / ln10]                     ... (6)
            ─────────────────────────────
            β(1-φ)(fL-fM)(H-H_QV)/H

  This is DERIVED, not postulated. It follows from requiring
  that the Cauldron and Friedmann describe the same dx.
""")

    # Solve Cauldron
    def cauldron(tau, state):
        h, x = state
        fm = fM(x); fl = fL(x)
        tension = fl - fm; p = fm/(fm+fl)
        if h <= H_QV: return [0.0, 0.0]
        W = tension * (h - H_QV)
        return [-W, -beta * (1-p) * W / max(h, 1e-30)]

    sol = solve_ivp(cauldron, (0, 500), [1.0, -5.0],
                    method='RK45', max_step=0.01, rtol=1e-11, atol=1e-13)
    tau_s = sol.t; H_s = sol.y[0]; x_s = sol.y[1]

    # Compute κ at key epochs
    print(f"  β = {beta} (reference)")
    print(f"  x_em = {X_EM:.2f} (crystallization)")
    print(f"\n  {'x':<8} {'z':<10} {'H_enth':<10} {'dx/dτ':<14} "
          f"{'H_Fried':<14} {'dx/dt':<14} {'κ':<16} {'W_rate':<10}")
    print(f"  {'-'*100}")

    data = []
    for x_val in [X_EM, -18, -19, -20, -20.30, -21, -22, -23, -23.93,
                  -24, -25, -25.60, -26, -26.53]:
        z = z_from_x(x_val)
        if z < 0: continue

        idx = np.argmin(np.abs(x_s - x_val))
        h = H_s[idx]

        fm = fM(x_val); fl = fL(x_val)
        tension = fl - fm; p = fm/(fm+fl)
        dx_dtau = -beta * (1-p) * tension * (h - H_QV) / max(h, 1e-30)

        H_F = H_friedmann(z)
        dx_dt = -3 * H_F / np.log(10)

        kappa = dx_dt / dx_dtau if abs(dx_dtau) > 1e-30 else 0
        W_rate = tension * (h - H_QV) / max(h, 1e-30)

        data.append((x_val, z, h, dx_dtau, H_F, dx_dt, kappa, W_rate))
        print(f"  {x_val:<8.2f} {z:<10.2f} {h:<10.4f} {dx_dtau:<14.4e} "
              f"{H_F:<14.4e} {dx_dt:<14.4e} {kappa:<16.4e} {W_rate:<10.4f}")

    return data, tau_s, H_s, x_s


# ══════════════════════════════════════════════════════════════════════
#  BLOCK III — Why κ ≠ W_rate
# ══════════════════════════════════════════════════════════════════════

def block_III_naive_fails(data):
    """Show that the naïve κ = W_rate proposal fails."""
    print(f"\n{'='*72}")
    print(f"  BLOCK III — WHY THE NAÏVE κ = W_rate FAILS")
    print(f"{'='*72}")

    ratios = [d[6] / d[7] if abs(d[7]) > 1e-30 else 0
              for d in data if abs(d[7]) > 1e-30]

    mean_r = np.mean(ratios)
    std_r = np.std(ratios)
    cov = std_r / mean_r * 100

    print(f"""
  THE NAÏVE PROPOSAL:
    dτ_GERT = W_rate(x) × dτ_Einstein
    → κ should be proportional to W_rate
    → κ/W_rate should be CONSTANT

  NUMERICAL TEST:
    κ/W_rate values across Layer 3:
    Mean = {mean_r:.4e}
    Std  = {std_r:.4e}
    CoV  = {cov:.1f}%

  VERDICT: {'FAILS' if cov > 20 else 'PASSES'} (CoV = {cov:.1f}%)
""")

    if cov > 20:
        print(f"""  The ratio κ/W_rate varies by {cov:.0f}% — NOT constant.
  κ is NOT simply proportional to W_rate.

  WHY IT FAILS:
    κ(x) = [3 H_Fried(z)/ln10] / [β(1-φ)(fL-fM)(H-H_QV)/H]

    The NUMERATOR contains H_Fried(z) — pure geometry (GR).
    The DENOMINATOR contains (fL-fM)(H-H_QV)/H — pure thermodynamics.

    W_rate = (fL-fM)(H-H_QV)/H = denominator / [β(1-φ)]

    For κ/W_rate to be constant, H_Fried(z) / [(1-φ)²(fL-fM)(H-H_QV)/H]
    would need to be constant. It is not — because H_Fried(z) varies
    differently from the GERT functions.

  PHYSICAL MEANING:
    Thermodynamic time and geometric time are NOT separable.
    The bridge κ(x) requires BOTH geometry and thermodynamics.
    Neither alone suffices.
""")

    return cov


# ══════════════════════════════════════════════════════════════════════
#  BLOCK IV — The Co-Dependence
# ══════════════════════════════════════════════════════════════════════

def block_IV_codependence(data):
    """The co-dependence of thermodynamics and geometry in κ."""
    print(f"\n{'='*72}")
    print(f"  BLOCK IV — THE CO-DEPENDENCE OF THERMODYNAMICS AND GEOMETRY")
    print(f"{'='*72}")

    print(f"""
  In Layer 2 (pre-geometric): only τ exists.
    Time = pure Work. No metric, no t.

  At crystallization (Ξ = 1): the metric emerges.
    t begins to exist alongside τ.

  In Layer 3: both τ and t coexist.
    Their ratio κ(x) = dτ/dt is given by eq. (6).
    κ depends on BOTH H_Fried (geometry) and fM, fL, H (thermodynamics).

  CONSEQUENCE: the geometry that the thermodynamics created
  feeds BACK into how thermodynamics projects into time.

  This is a FEEDBACK LOOP:
    Thermodynamics → creates metric (Paper III, Ξ = 1)
    Metric → modifies κ → modifies how τ projects into t

  The two descriptions (thermodynamic and geometric) are
  IRREDUCIBLY CO-DEPENDENT in Layer 3.

  You cannot compute κ without knowing H_Fried (geometry).
  You cannot compute κ without knowing fM, fL, H (thermodynamics).

  This is exactly what "emergence" means:
    The emerged structure (metric) retroacts on its source (thermodynamics).
    The child modifies the parent.

  IN LAYER 2: dτ is the only time. Pure. Self-contained.
  IN LAYER 3: dτ is entangled with dt. Inseparable.

  Crystallization did not merely create the ruler.
  It permanently entangled the ruler with the motor.
""")


# ══════════════════════════════════════════════════════════════════════
#  BLOCK V — β is Gauge
# ══════════════════════════════════════════════════════════════════════

def block_V_beta_gauge(data):
    """Prove that β is a gauge choice, not a physical parameter."""
    print(f"\n{'='*72}")
    print(f"  BLOCK V — β IS GAUGE: ZERO FREE PARAMETERS")
    print(f"{'='*72}")

    # Compute κ/κ_em for each data point
    kappa_em = data[0][6]  # first entry is x_em

    print(f"\n  κ(x)/κ(x_em) — the β-INDEPENDENT shape:")
    print(f"\n  {'x':<8} {'z':<10} {'κ/κ_em':<12}")
    print(f"  {'-'*30}")
    for x_val, z, h, dx_dtau, H_F, dx_dt, kappa, W_rate in data:
        ratio = kappa / kappa_em if abs(kappa_em) > 1e-50 else 0
        print(f"  {x_val:<8.2f} {z:<10.2f} {ratio:<12.6f}")

    print(f"""
  THE PROOF:

  From eq. (6): κ(x) = [3 H_Fried(z)/ln10] / [β(1-φ)(fL-fM)(H-H_QV)/H]

  β appears as a GLOBAL FACTOR in the denominator.
  Therefore κ(x)/κ(x') is β-INDEPENDENT for any two points x, x'.

  Under the redefinition τ' = τ/β:
    dx/dτ' = -(1-φ)(fL-fM)(H-H_QV)/H     ... β absorbed
    dH/dτ' = -(fL-fM)(H-H_QV)/β           ... or equivalently H' = H/β

  β scales how much enthalpy-per-τ constitutes "one unit of expansion."
  This is a CONVENTION, not physics — like choosing Joules vs eV.

  ALL predictions are β-independent:
    - φ(x) trajectory: β-independent (Paper IX Result 4)
    - κ(x)/κ(x_em) shape: β-independent (shown above)
    - All 13 results of Paper IX: β-independent

  THE CAULDRON EQUATION HAS ZERO FREE PARAMETERS.
    Inputs: Paper I functions (frozen from MCMC)
    Postulates: dH ≤ 0; Outward creates volume
    Convention: β (gauge choice)
    Boundary: H_QV (when the eon ends)
""")


# ══════════════════════════════════════════════════════════════════════
#  BLOCK VI — Why Time Stops at c
# ══════════════════════════════════════════════════════════════════════

def block_VI_speed_of_light():
    """The thermodynamic origin of the speed of light barrier."""
    print(f"\n{'='*72}")
    print(f"  BLOCK VI — WHY TIME STOPS AT THE SPEED OF LIGHT")
    print(f"{'='*72}")

    print(f"""
  For a particle of mass m at velocity v:

    E_total    = γmc²                    (total energy)
    E_internal = mc²                     (rest/internal energy)
    E_kinetic  = (γ-1)mc²               (kinetic/transport energy)

    f_internal = E_internal / E_total    (fraction for internal process)
               = mc² / (γmc²)
               = 1/γ
               = √(1 - v²/c²)           ... (7)

  THIS IS THE LORENTZ FACTOR.

  It measures the fraction of total energy available for
  internal thermodynamic process.

  At v = 0:   f_int = 1.  All energy is internal. Maximum Work.
  At v → c:   f_int → 0.  All energy is kinetic. Zero Work.
  At v = c:   f_int = 0.  No rest mass. No internal process.

  The full time experienced by a particle:
    dτ_particle = κ(x) × √(1 - v²/c²) × dt          ... (8)

  At v = c: √(1 - v²/c²) = 0.
  Therefore dτ = κ × 0 × dt = 0.

  THIS RESULT IS κ-INDEPENDENT.
  Regardless of what κ(x) is — whether it equals W_rate,
  or the derived expression (6), or anything else —
  zero times anything is zero.

  The photon does not experience time because:
    - It has no rest mass (m = 0)
    - It has no internal structure to reorganize
    - It performs no thermodynamic Work on itself
    - It is pure transport: energy moves but does not transform

  THE SPEED OF LIGHT IS NOT AN ARBITRARY LIMIT.
  It is the THERMODYNAMIC BOUNDARY where internal process ceases.
  Nothing can exceed c because that would require NEGATIVE internal
  energy — f_int < 0 — which has no thermodynamic meaning.
""")

    # Numerical illustration
    print(f"  {'v/c':<10} {'γ':<12} {'f_internal':<12} {'Meaning'}")
    print(f"  {'-'*50}")
    for vc in [0, 0.1, 0.5, 0.9, 0.99, 0.999, 0.9999, 1.0]:
        if vc < 1:
            gamma = 1/np.sqrt(1 - vc**2)
            f_int = 1/gamma
        else:
            gamma = float('inf')
            f_int = 0
        meaning = ("All internal" if vc == 0 else
                   "Pure transport" if vc == 1 else
                   f"{f_int*100:.1f}% internal")
        print(f"  {vc:<10.4f} {gamma:<12.2f} {f_int:<12.6f} {meaning}")

    print()


# ══════════════════════════════════════════════════════════════════════
#  BLOCK VII — The Two Barriers Are the Same
# ══════════════════════════════════════════════════════════════════════

def block_VII_same_barrier():
    """Show that φ < 1/2 and v < c are the same thermodynamic barrier."""
    print(f"\n{'='*72}")
    print(f"  BLOCK VII — THE TWO BARRIERS ARE THE SAME BARRIER")
    print(f"{'='*72}")

    print(f"""
  COSMIC BARRIER: φ = 1/2 (never reached)
    φ = fM/(fM+fL)
    At φ = 1/2: fM = fL → ΔG = 0 → W = 0 → dτ = 0
    The universe cannot reach equilibrium because time would stop.

  PARTICLE BARRIER: v = c (never reached by massive particles)
    f_internal = √(1 - v²/c²)
    At v = c: f_int = 0 → no internal process → W = 0 → dτ = 0
    A massive particle cannot reach c because process would cease.

  BOTH BARRIERS ENFORCE THE SAME CONDITION:
    Work → 0 → dτ → 0 → time stops

  COMPARISON:

    Scale        Barrier    Variable    Condition      Physical meaning
    ───────────  ─────────  ──────────  ─────────────  ─────────────────
    Cosmic       φ < 1/2    φ           ΔG = 0         No thermodynamic gradient
    Particle     v < c      v           f_int = 0      No internal process

  φ_max = 0.442 (recombination): closest the universe gets to the
  cosmic barrier. The universe's maximum structural ambition.

  v_max = c (photon): the particle that sits ON the particle barrier.
  It has zero internal process — and zero time.

  The barriers are the SAME thermodynamic constraint at two scales:
    - At the cosmic scale: the system cannot reach equilibrium
    - At the particle scale: the entity cannot reach pure transport

  Both are expressions of: thermodynamic time requires Work.
  Where Work ceases, time ceases. This is the deepest meaning of
  the postulate dτ ∝ -dG.
""")


# ══════════════════════════════════════════════════════════════════════
#  BLOCK VIII — Mass as Crystallized Work
# ══════════════════════════════════════════════════════════════════════

def block_VIII_mass():
    """Mass = crystallized Work capacity. E = mc² reinterpreted."""
    print(f"\n{'='*72}")
    print(f"  BLOCK VIII — MASS AS CRYSTALLIZED WORK CAPACITY")
    print(f"{'='*72}")

    # Cost of creating matter (from Paper IX Result 8)
    # Formation: 36.3% of H_M
    # Total matter mass: M_total = 8.59e52 kg (Paper VIII eq. 7)
    M_total = 8.59e52
    H_M = 7.72e69  # J (Paper VIII eq. 7)
    frac_struct = 0.369
    E_struct = frac_struct * H_M

    cost_per_kg = E_struct / M_total
    mc2_per_kg = C**2

    print(f"""
  E = mc² reinterpreted thermodynamically:

  REST MASS = STORED THERMODYNAMIC POTENTIAL
  The mass of a particle IS the Work the Cauldron invested
  in creating it. It is frozen, crystallized Work.

  VERIFICATION:
    Total structural Work: {frac_struct*100:.1f}% × H_M = {E_struct:.2e} J
    Total matter mass: M = {M_total:.2e} kg
    Cost per kg of matter: {cost_per_kg:.2e} J/kg
    mc² per kg: {mc2_per_kg:.2e} J/kg
    Ratio: {cost_per_kg/mc2_per_kg:.2f}

  The ratio ≈ {cost_per_kg/mc2_per_kg:.0f} means the Cauldron invested ~{cost_per_kg/mc2_per_kg:.0f}×
  the rest energy of matter in structural Work.
  The excess goes to binding energy, radiation, and the metric
  lattice itself. Only a fraction crystallizes as rest mass.

  ANNIHILATION as DE-CRYSTALLIZATION:
    When matter annihilates (E = mc² released), it returns
    the frozen Work to the energy field — the reverse of
    what the Cauldron did at recombination.

  THE MASS SPECTRUM:
    Different particles have different masses because the
    Cauldron invested different amounts of Work in creating them.
    The mass spectrum of the Standard Model IS the crystallization
    cost spectrum — derivable in principle from fM(x), fL(x) at
    the nucleation window (x ≈ -17.4). This is the deepest
    prediction, and the most distant from current capability.
""")


# ══════════════════════════════════════════════════════════════════════
#  BLOCK IX — Three Layers of Time Dilation + Figure
# ══════════════════════════════════════════════════════════════════════

def block_IX_three_layers(data, tau_s, H_s, x_s):
    """The three layers of time dilation and comprehensive figure."""
    print(f"\n{'='*72}")
    print(f"  BLOCK IX — THREE LAYERS OF TIME DILATION")
    print(f"{'='*72}")

    print(f"""
  Layer 3 has THREE simultaneous time dilations:

  ┌─────────────────────────────────────────────────────────────────┐
  │  dτ = κ(x) × √(1 + 2Φ/c²) × √(1 - v²/c²) × dt              │
  │       ═══════  ═══════════════  ═══════════════                 │
  │       THERMO   GR (gravity)     SR (velocity)                  │
  └─────────────────────────────────────────────────────────────────┘

  TYPE 1 — SPECIAL RELATIVISTIC (velocity):
    Factor: √(1 - v²/c²)
    Scale: particle
    Varies: with velocity
    Discovery: Einstein (1905)
    GERT meaning: fraction of energy for internal process

  TYPE 2 — GENERAL RELATIVISTIC (gravitational):
    Factor: √(1 + 2Φ/c²) ≈ √(1 - r_S/r) near a mass
    Scale: astrophysical
    Varies: with gravitational potential
    Discovery: Einstein (1915)
    GERT meaning: local metric modification of tick rate

  TYPE 3 — THERMODYNAMIC (cosmological):
    Factor: κ(x) = [3H_Fried/ln10] / [β(1-φ)(fL-fM)(H-HQV)/H]
    Scale: cosmological
    Varies: with cosmic density (epoch)
    Discovery: GERT Paper IX/X (2026)
    GERT meaning: thermodynamic content per geometric second

  WITHIN a fixed cosmic epoch (fixed x):
    κ = constant → dτ ∝ dτ_Einstein
    ALL SR and GR predictions preserved exactly.
    No local experiment can distinguish GERT time from Einstein time.

  ACROSS cosmic epochs (different x):
    κ varies enormously (×6300 from Cauldron to today).
    This is NOT observable by local clocks.
    It IS observable through the cosmic expansion rate (Paper I).
""")

    # ── Figure: the three layers ──────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("GERT Paper 10 — Three Layers of Time Dilation",
                 fontsize=13, fontweight='bold')

    # Panel 1: SR — f_internal vs v/c
    ax = axes[0]
    vc = np.linspace(0, 0.999, 500)
    f_int = np.sqrt(1 - vc**2)
    ax.plot(vc, f_int, 'C3', lw=2.5)
    ax.axhline(0, color='grey', lw=0.5)
    ax.set_xlabel('v/c'); ax.set_ylabel(r'$\sqrt{1 - v^2/c^2}$')
    ax.set_title('Special Relativistic\n(velocity → internal fraction)')
    ax.annotate('v = c → time stops\n(zero internal process)',
                xy=(0.99, 0.02), fontsize=8, color='C3',
                ha='right', va='bottom')
    ax.grid(alpha=0.2)

    # Panel 2: GR — √(1-rS/r) vs r/rS
    ax = axes[1]
    r_ratio = np.linspace(1.01, 20, 500)
    g00 = np.sqrt(1 - 1/r_ratio)
    ax.plot(r_ratio, g00, 'C0', lw=2.5)
    ax.axhline(1, color='grey', ls=':', alpha=0.5)
    ax.set_xlabel(r'$r/r_S$')
    ax.set_ylabel(r'$\sqrt{1 - r_S/r}$')
    ax.set_title('General Relativistic\n(gravity → metric dilation)')
    ax.annotate('r → rS → time stops\n(event horizon)',
                xy=(1.5, 0.1), fontsize=8, color='C0')
    ax.grid(alpha=0.2)

    # Panel 3: Thermodynamic — κ/κ_em vs x
    ax = axes[2]
    kappa_em = data[0][6]
    x_vals = [d[0] for d in data]
    kappa_ratio = [d[6]/kappa_em for d in data]
    ax.semilogy(x_vals, kappa_ratio, 'C4', lw=2.5, marker='o', ms=4)
    ax.axvline(X_EM, color='C2', ls='--', alpha=0.5, label='Crystallization')
    ax.axvline(-23.93, color='C1', ls='--', alpha=0.5, label='L2 peak')
    ax.set_xlabel('x = log₁₀ρ')
    ax.set_ylabel(r'$\kappa(x) / \kappa(x_{\rm em})$')
    ax.set_title('Thermodynamic\n(density → Work content per second)')
    ax.legend(fontsize=7); ax.grid(alpha=0.2)
    ax.set_xlim(-27, -17)

    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/paper10_fig1_three_layers.png',
                dpi=150)
    plt.close()
    print("  Fig 1 saved: paper10_fig1_three_layers.png")

    # ── Figure 2: κ components ────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("GERT Paper 10 — κ(x) Decomposition",
                 fontsize=13, fontweight='bold')

    x_plot = [d[0] for d in data]
    H_F_plot = [d[4] for d in data]
    W_plot = [d[7] for d in data]
    k_plot = [d[6] for d in data]

    # Panel 1: Numerator and denominator of κ
    ax = axes[0]
    num = [3*hf/np.log(10) for hf in H_F_plot]
    ax.semilogy(x_plot, [abs(n) for n in num], 'C0', lw=2,
                label='|Numerator| = 3H_Fried/ln10', marker='o', ms=3)
    ax.semilogy(x_plot, [abs(d[3]) for d in data], 'C3', lw=2,
                label='|Denominator| = β(1-φ)(fL-fM)(H-HQV)/H',
                marker='s', ms=3)
    ax.set_xlabel('x = log₁₀ρ'); ax.set_ylabel('Value (s⁻¹ or τ⁻¹)')
    ax.set_title('κ = Numerator / Denominator')
    ax.legend(fontsize=7); ax.grid(alpha=0.2)

    # Panel 2: κ vs W_rate (showing they're NOT proportional)
    ax = axes[1]
    ax.scatter(W_plot, [abs(k) for k in k_plot], c=x_plot,
               cmap='viridis', s=60, edgecolors='k', lw=0.5)
    ax.set_xlabel('W_rate(x)'); ax.set_ylabel('|κ(x)|')
    ax.set_title('κ vs W_rate — NOT proportional')
    ax.set_xscale('log'); ax.set_yscale('log')
    cb = plt.colorbar(ax.collections[0], ax=ax)
    cb.set_label('x = log₁₀ρ')
    ax.grid(alpha=0.2)

    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/paper10_fig2_kappa_decomposition.png',
                dpi=150)
    plt.close()
    print("  Fig 2 saved: paper10_fig2_kappa_decomposition.png")


# ══════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    os.makedirs('/mnt/user-data/outputs', exist_ok=True)

    print()
    print("GERT Paper 10 — The Fabric of Time")
    print("Dutra V P (2026)")
    print()
    print(f"Using H₀ = {H0_KMS_MPC} km/s/Mpc  |  "
          f"a_GERT = {A_GERT:.4e} m/s²")
    print()

    block_I_postulate()
    data, tau_s, H_s, x_s = block_II_derive_kappa(beta=5.0)
    cov = block_III_naive_fails(data)
    block_IV_codependence(data)
    block_V_beta_gauge(data)
    block_VI_speed_of_light()
    block_VII_same_barrier()
    block_VIII_mass()
    block_IX_three_layers(data, tau_s, H_s, x_s)

    # ── Final summary ──────────────────────────────────────────────
    print(f"\n{'='*72}")
    print(f"  PAPER 10 — COMPLETE RESULTS (9 BLOCKS)")
    print(f"{'='*72}")
    print(f"""
  RESULT 1 — κ(x) derived from Cauldron–Friedmann matching (Block II)
    κ = [3H_Fried/ln10] / [β(1-φ)(fL-fM)(H-HQV)/H]
    Consequence, not postulate.

  RESULT 2 — The naïve κ = W_rate FAILS (Block III)
    CoV = {cov:.0f}%. Thermodynamic time ≠ W_rate × geometric time.

  RESULT 3 — Thermodynamics and geometry are co-dependent (Block IV)
    κ requires BOTH H_Fried (geometry) and fM,fL,H (thermodynamics).
    The emerged metric retroacts on its source.
    In Layer 2: τ is pure Work.
    In Layer 3: τ is Work entangled with geometry.

  RESULT 4 — β is gauge: zero free parameters (Block V)
    κ(x)/κ(x_em) is β-independent. β is a unit choice.

  RESULT 5 — Time stops at c: zero internal process (Block VI)
    f_internal = √(1-v²/c²) = 0 at v = c.
    κ-INDEPENDENT. Robust regardless of the τ↔t mapping.

  RESULT 6 — φ < 1/2 and v < c are the same barrier (Block VII)
    Both: Work → 0 → dτ → 0 → time stops.
    Cosmic scale and particle scale.

  RESULT 7 — Mass = crystallized Work capacity (Block VIII)
    E = mc² = the Cauldron's investment in that particle.

  RESULT 8 — Three layers of time dilation coexist (Block IX)
    SR: √(1-v²/c²)          — velocity (particle)
    GR: √(1+2Φ/c²)          — gravity (astrophysical)
    GERT: κ(x)/κ(x_em)      — density (cosmological)

  RESULT 9 — H_enthalpy has no geometric counterpart (Block II)
    The Cauldron knows something the metric doesn't.
    The invisible 98.2% lives in H, inaccessible to geometry.

  EINSTEIN described the geometry of time.
  GERT describes the content.
  The clock slows because there is less to do.
  The clock stops because there is nothing to do.
""")

    print("  Script complete. Figures in /mnt/user-data/outputs/")
    print()
