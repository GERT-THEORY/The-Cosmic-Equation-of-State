#!/usr/bin/env python3
"""
GERT Paper 10 — EXPLORATORY: The Fabric of Time
================================================
Why does time stop at the speed of light?
The thermodynamic origin of time dilation and the meaning of mass.

dτ_GERT = W_rate(x) × dτ_Einstein

Central discoveries:
  1. c is a thermodynamic limit: v = c ↔ zero internal process
  2. The Lorentz factor = fraction of energy available for Work
  3. φ < 1/2 (cosmic) and v < c (particle) are the SAME barrier
  4. Mass = crystallized Work capacity (E = mc² = Cauldron investment)
  5. κ(x) = (fL-fM)(H-H_QV)/H for comoving observers
  6. Einstein described the geometry of time. GERT describes the content.

Veronica Padilha Dutra (2026)
"""

import numpy as np
from scipy.special import expit
from scipy.integrate import solve_ivp

# ── Paper I parameters (frozen) ───────────────────────────────────
FM_I, FM_F = 0.7831, 0.5851
FL_I, FL_M = 1.3414, 1.1236
LOG_RHO_M, D_M = -20.30, 1.0
FM_PEAK = 0.37; LOG_RHO_C = -17.41; SIGMA_C = 1.0
LOG_RHO_L, D_L = -25.60, 2.0
FL_PEAK = 4.6245; LOG_RHO_L2 = -23.93; SIGMA_L2 = 1.0
C = 2.998e8; G = 6.674e-11; MPC = 3.0857e22
H0 = 72.5e3 / MPC
H_QV = 0.001

def logistic(x, x0, d): return expit(-(x - x0) / d)
def gauss(x, x0, s): return np.exp(-0.5 * ((x - x0) / s)**2)

def fM(x):
    b = FM_I + (FM_F - FM_I) * logistic(x, LOG_RHO_M, D_M)
    return b * (1 + FM_PEAK * gauss(x, LOG_RHO_C, SIGMA_C))

def fL(x):
    b = FL_I + (FL_M - FL_I) * logistic(x, LOG_RHO_L, D_L)
    return b * (1 + FL_PEAK * gauss(x, LOG_RHO_L2, SIGMA_L2))


# ══════════════════════════════════════════════════════════════════════
#  THE CENTRAL EQUATION
# ══════════════════════════════════════════════════════════════════════
#
#  dτ_GERT = W_rate(x) × dτ_Einstein
#
#  where:
#    dτ_Einstein = dt × √(g_μν dx^μ dx^ν)    (GR proper time)
#    W_rate(x) = (fL(x) - fM(x)) × (H - H_QV)/H  (thermodynamic factor)
#
#  For a particle at velocity v in potential Φ:
#    dτ_GERT = W_rate(x) × √(1 + 2Φ/c²) × √(1 - v²/c²) × dt
#
#  Consequences:
#    v = c  → √(1-v²/c²) = 0 → dτ = 0 (time stops: pure transport)
#    v = 0  → √(1-v²/c²) = 1 → dτ = W_rate × dτ_Einstein (max Work)
#    φ = ½  → W_rate → 0 → dτ = 0 (time stops: equilibrium)
#
# ══════════════════════════════════════════════════════════════════════


def W_rate(x, H_enth):
    """Thermodynamic Work rate at density x with enthalpy H."""
    return (fL(x) - fM(x)) * (H_enth - H_QV) / max(H_enth, 1e-30)


def kappa(x, H_enth, v=0.0, Phi=0.0):
    """Full κ function: dτ_GERT/dt.

    κ(x, H, v, Φ) = W_rate(x, H) × √(1 - v²/c²) × √(1 + 2Φ/c²)

    For comoving cosmological observers: v = 0, Φ = 0.
    """
    gamma_thermo = np.sqrt(max(0, 1 - v**2 / C**2))
    grav_factor = np.sqrt(max(0, 1 + 2 * Phi / C**2))
    return W_rate(x, H_enth) * gamma_thermo * grav_factor


def kappa_profile():
    """Compute κ along the Cauldron trajectory."""
    def cauldron(tau, state):
        h, x = state
        fm = fM(x); fl = fL(x)
        tension = fl - fm; p = fm / (fm + fl)
        if h <= H_QV: return [0.0, 0.0]
        W = tension * (h - H_QV)
        return [-W, -5.0 * (1 - p) * W / max(h, 1e-30)]

    sol = solve_ivp(cauldron, (0, 500), [1.0, -5.0],
                    method='RK45', max_step=0.01,
                    rtol=1e-11, atol=1e-13)
    return sol.t, sol.y[0], sol.y[1]


if __name__ == '__main__':
    print()
    print("GERT Paper 10 — The Fabric of Time (exploratory)")
    print("Dutra V P (2026)")
    print()

    # ── κ profile ──────────────────────────────────────────────────
    tau, H_s, x_s = kappa_profile()

    print("  κ(x) = (fL-fM)(H-H_QV)/H  for comoving observers:")
    print()
    print(f"  {'x':<8} {'fL-fM':<10} {'H/H_M':<10} {'κ':<12} {'Phase'}")
    print(f"  {'-'*55}")

    for x_val, phase in [(-5, "Cauldron start"),
                          (-10, "Mid Cauldron"),
                          (-17.41, "Recombination"),
                          (-20.30, "Builder→Maint"),
                          (-23.93, "L2 peak (trigger)"),
                          (-25.60, "fL logistic (accel)"),
                          (-26.53, "Today")]:
        idx = np.argmin(np.abs(x_s - x_val))
        k = kappa(x_s[idx], H_s[idx])
        tension = fL(x_s[idx]) - fM(x_s[idx])
        print(f"  {x_val:<8.2f} {tension:<10.4f} {H_s[idx]:<10.4f} "
              f"{k:<12.4f} {phase}")

    # ── The two barriers ───────────────────────────────────────────
    print(f"""
  ══════════════════════════════════════════════════════════════
  THE TWO BARRIERS ARE THE SAME BARRIER:

    Cosmic scale:   φ = 1/2 → ΔG = 0 → dτ = 0
    Particle scale: v = c   → f_int = 0 → dτ = 0

    Both: Work → 0 → time stops.
  ══════════════════════════════════════════════════════════════

  WHAT GERT ADDS TO EINSTEIN:
    Einstein described the geometry of time.
    GERT describes the content.

    The clock slows because there is less to do.
    The clock stops because there is nothing to do.
""")
