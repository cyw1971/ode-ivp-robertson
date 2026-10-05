"""Reproduce every figure in the report. Run: python run_all.py"""

from pathlib import Path
import sys
import time

import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from model import (
    robertson_rhs, robertson_jacobian, finite_difference_jacobian,
    ROBERTSON_Y0, ROBERTSON_T0, ROBERTSON_T1,
    logistic_rhs, logistic_exact, LOGISTIC_Y0, LOGISTIC_T0, LOGISTIC_T1,
)
from methods import (
    solve_euler, solve_rk4, solve_implicit_euler, adaptive_implicit_euler,
    newton_implicit_euler,
)
from plots import plot_convergence, plot_stability_regions, savefig
import matplotlib.pyplot as plt

FIG = ROOT.parent / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def build_oracle():
    sol = solve_ivp(
        robertson_rhs, [ROBERTSON_T0, ROBERTSON_T1], ROBERTSON_Y0,
        method="BDF", rtol=1e-12, atol=1e-14, jac=robertson_jacobian,
        dense_output=True,
    )
    sol_tight = solve_ivp(
        robertson_rhs, [ROBERTSON_T0, ROBERTSON_T1], ROBERTSON_Y0,
        method="Radau", rtol=1e-13, atol=1e-15, jac=robertson_jacobian,
    )
    y_bdf = sol.y[:, -1]
    y_rad = sol_tight.y[:, -1]
    disc = np.max(np.abs(y_bdf - y_rad))
    print(f"[oracle] BDF y(40) = {y_bdf}")
    print(f"[oracle] Radau y(40) = {y_rad}")
    print(f"[oracle] |BDF-Radau|_inf = {disc:.3e}")
    return sol, y_bdf, disc


def jacobian_check():
    y = np.array([0.9, 1.0e-5, 0.1])
    Ja = robertson_jacobian(0.0, y)
    # central difference: the 3e7 y2^2 term has large second derivative
    eps = 1e-6
    Jc = np.empty((3, 3))
    for j in range(3):
        yp, ym = y.copy(), y.copy()
        yp[j] += eps
        ym[j] -= eps
        Jc[:, j] = (robertson_rhs(0.0, yp) - robertson_rhs(0.0, ym)) / (2 * eps)
    err = np.max(np.abs(Ja - Jc))
    colsum = Ja.sum(axis=0)
    print(f"[jac] max |analytic-central FD| = {err:.3e}")
    print(f"[jac] column sums (should be ~0): {colsum}")
    return err, colsum


def logistic_orders():
    h_vals = np.array([0.4, 0.2, 0.1, 0.05, 0.025])
    y0 = LOGISTIC_Y0
    t0, t1 = LOGISTIC_T0, LOGISTIC_T1
    exact = lambda tt: np.array([logistic_exact(tt, y0[0])])

    err_e, err_r = [], []
    for h in h_vals:
        _, ye, _ = solve_euler(logistic_rhs, y0, t0, t1, h)
        _, yr, _ = solve_rk4(logistic_rhs, y0, t0, t1, h)
        err_e.append(np.linalg.norm(ye[-1] - exact(t1)))
        err_r.append(np.linalg.norm(yr[-1] - exact(t1)))
    err_e, err_r = np.array(err_e), np.array(err_r)

    print("[logistic Euler] h, error:")
    for h, e in zip(h_vals, err_e):
        print(f"  {h:8.4f}  {e:.6e}")
    s_e, se_e = plot_convergence(
        h_vals, err_e, 1.0, "explicit Euler (logistic)",
        FIG / "fig04_order_euler_logistic.png",
    )
    print("[logistic RK4] h, error:")
    for h, e in zip(h_vals, err_r):
        print(f"  {h:8.4f}  {e:.6e}")
    s_r, se_r = plot_convergence(
        h_vals, err_r, 4.0, "RK4 (logistic)",
        FIG / "fig05_order_rk4_logistic.png",
    )
    print(f"[logistic] Euler slope = {s_e:.3f} ± {se_e:.3f}")
    print(f"[logistic] RK4   slope = {s_r:.3f} ± {se_r:.3f}")
    return h_vals, err_e, err_r, s_e, se_e, s_r, se_r


def robertson_implicit_order(y_oracle):
    h_vals = np.array([0.8, 0.4, 0.2, 0.1, 0.05])
    errs, n_rhs_list, wall, min_y2 = [], [], [], []
    for h in h_vals:
        t0 = time.perf_counter()
        _, y, n_rhs = solve_implicit_euler(
            robertson_rhs, robertson_jacobian,
            ROBERTSON_Y0, ROBERTSON_T0, ROBERTSON_T1, h,
        )
        wall.append(time.perf_counter() - t0)
        errs.append(np.linalg.norm(y[-1] - y_oracle, np.inf))
        n_rhs_list.append(n_rhs)
        # y2(0)=0 by construction; the positivity column is min after t=0
        min_y2.append(float(np.min(y[1:, 1])))
        print(f"  h={h:.3f}  e_inf={errs[-1]:.4e}  n_rhs={n_rhs}  wall={wall[-1]:.3f}s"
              f"  min_t>0 y2={min_y2[-1]:.4e}  y={y[-1]}")
    errs = np.array(errs)
    s, se = plot_convergence(
        h_vals, errs, 1.0, "implicit Euler (Robertson)",
        FIG / "fig06_order_implicit_robertson.png",
        annotate_floor=False,
    )
    print(f"[Robertson implicit] slope = {s:.3f} ± {se:.3f}")
    return h_vals, errs, np.array(n_rhs_list), np.array(wall), np.array(min_y2), s, se


def trajectory_and_mass(y_oracle):
    t, y, _ = solve_implicit_euler(
        robertson_rhs, robertson_jacobian,
        ROBERTSON_Y0, ROBERTSON_T0, ROBERTSON_T1, 0.1,
    )
    mass = y.sum(axis=1)
    mass_err = np.max(np.abs(mass - 1.0))
    print(f"[mass] max|sum-1| = {mass_err:.3e}")
    print(f"[traj] implicit Euler h=0.1  y(40)={y[-1]}")
    rel = np.abs(y[-1] - y_oracle) / np.maximum(np.abs(y_oracle), 1e-30)
    print(f"[traj] rel. err vs oracle = {rel}")

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.plot(t, y[:, 0], color="tab:blue", label=r"$y_1$ (A)")
    ax.plot(t, y[:, 1] * 1e4, color="tab:orange", label=r"$y_2\times 10^{4}$ (B)")
    ax.plot(t, y[:, 2], color="tab:green", label=r"$y_3$ (C)")
    ax.axhline(y_oracle[0], color="tab:blue", ls=":", lw=1)
    ax.axhline(y_oracle[2], color="tab:green", ls=":", lw=1)
    ax.set_xscale("log")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("concentration [-]")
    ax.set_title("Robertson: implicit Euler h=0.1 tracks the BDF oracle")
    ax.legend()
    ax.grid(True, which="both", ls=":", alpha=0.6)
    savefig(fig, FIG / "fig01_robertson_trajectory.png")

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.semilogy(t, np.maximum(np.abs(mass - 1.0), 1e-18), color="tab:blue")
    ax.set_xlabel("t [s]")
    ax.set_ylabel(r"$|y_1+y_2+y_3-1|$ [-]")
    ax.set_title("Linear invariant held to round-off (not a proof of accuracy)")
    ax.grid(True, which="both", ls=":", alpha=0.6)
    savefig(fig, FIG / "fig02_mass.png")
    return t, y, mass_err, rel


def stiffness_and_stability(sol, y_end):
    t_log = np.logspace(-6, np.log10(ROBERTSON_T1), 80)
    eigs = []
    ratios = []
    for tt in t_log:
        yy = sol.sol(tt)
        lam = np.linalg.eigvals(robertson_jacobian(tt, yy))
        eigs.append(np.sort(lam.real))
        nz = lam[np.abs(lam) > 1e-8]
        ratios.append(np.max(np.abs(nz.real)) / np.min(np.abs(nz.real)))
    eigs = np.array(eigs)
    ratios = np.array(ratios)

    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.semilogx(t_log, eigs[:, 0], color="tab:blue", label=r"$\lambda_{\min}$")
    ax.semilogx(t_log, eigs[:, 1], color="tab:orange", label=r"$\lambda_{\mathrm{mid}}$")
    ax.semilogx(t_log, eigs[:, 2], color="tab:green", label=r"$\lambda_{\max}$ (structural 0)")
    ax.set_xlabel("t [s]")
    ax.set_ylabel(r"$\mathrm{Re}\,\lambda$ [1/s]")
    ax.set_title("Robertson Jacobian: one structural zero, one growing fast mode")
    ax.legend()
    ax.grid(True, which="both", ls=":", alpha=0.6)
    savefig(fig, FIG / "fig10_eigenvalues.png")

    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.loglog(t_log, ratios, color="tab:blue")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("stiffness ratio S(t) [-]")
    ax.set_title(fr"$S(t)$ grows to ${ratios[-1]:.2e}$ at $t=40$ (nonzero eigenvalues only)")
    ax.grid(True, which="both", ls=":", alpha=0.6)
    savefig(fig, FIG / "fig11_stiffness.png")

    J40 = robertson_jacobian(ROBERTSON_T1, y_end)
    lam40 = np.linalg.eigvals(J40)
    lam_fast = lam40[np.argmin(lam40.real)]
    h_stab = 2.0 / abs(lam_fast.real)
    print(f"[stiff] eig(J(40)) = {lam40}")
    print(f"[stiff] S(40) = {ratios[-1]:.4e}")
    print(f"[stiff] explicit Euler bound h < {h_stab:.3e}")

    # Overlay at a stable explicit-scale h and at the implicit working h
    plot_stability_regions(
        FIG / "fig03_stability_regions.png",
        J=J40, h=0.1, extra_label=r"$h\lambda$ at $t=40$, $h=0.1$",
    )
    return ratios[-1], h_stab, lam40


def explicit_blowup():
    with np.errstate(over="ignore", invalid="ignore"):
        t, y, _ = solve_euler(
            robertson_rhs, ROBERTSON_Y0, ROBERTSON_T0, ROBERTSON_T1, 0.01,
        )
    finite = np.all(np.isfinite(y))
    print(f"[blowup] explicit Euler h=0.01 over T=40: finite={finite}")
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    y1 = y[:, 0]
    mask = np.isfinite(y1)
    ax.plot(t[mask], y1[mask], color="tab:orange", label="explicit Euler, h=0.01")
    ax.set_xlabel("t [s]")
    ax.set_ylabel(r"$y_1$ [-]")
    ax.set_title("Explicit Euler on Robertson leaves the stability region and diverges")
    ax.legend()
    ax.grid(True, ls=":", alpha=0.6)
    savefig(fig, FIG / "fig07_explicit_blowup.png")
    return finite


def adaptivity(y_oracle):
    tA, yA, hA, eA, n_rhs, n_rej = adaptive_implicit_euler(
        robertson_rhs, robertson_jacobian,
        ROBERTSON_Y0, ROBERTSON_T0, ROBERTSON_T1,
        h0=0.1, tol=2e-6,
    )
    e_ad = np.linalg.norm(yA[-1] - y_oracle, np.inf)
    tol = 2e-6
    print(f"[adapt] accepted steps={len(hA)}  rejects={n_rej}  n_rhs={n_rhs}")
    print(f"[adapt] h min={hA.min():.3e}  h final={hA[-1]:.3e}  e_inf={e_ad:.3e}")
    print(f"[adapt] local e: min={eA.min():.3e}  median={np.median(eA):.3e}  "
          f"max={eA.max():.3e}  frac in [tol/10,tol]={np.mean((eA >= tol/10) & (eA <= tol)):.3f}")
    print(f"[adapt] y(40)={yA[-1]}")

    fig, axes = plt.subplots(2, 1, figsize=(7.2, 6.4), sharex=True)
    axes[0].semilogy(tA[:-1], hA, ".", ls="-", color="tab:blue", label="accepted h")
    axes[0].axhline(0.1, color="0.2", ls=":", label="fixed h=0.1")
    axes[0].set_ylabel("accepted step h [-]")
    axes[0].set_title("Step-doubling: h changes, and local error sits near tol")
    axes[0].legend()
    axes[0].grid(True, which="both", ls=":", alpha=0.6)

    axes[1].semilogy(tA[:-1], eA, ".", ls="-", color="tab:orange", label=r"local $e(t)$")
    axes[1].axhline(tol, color="tab:red", ls="--", label=r"tol $=2\times 10^{-6}$")
    axes[1].axhline(tol / 10.0, color="0.4", ls=":", label=r"tol$/10$ (grow $h$)")
    axes[1].set_xlabel("t [s]")
    axes[1].set_ylabel(r"$\|y_{\mathrm{fine}}-y_{\mathrm{coarse}}\|_\infty$ [-]")
    axes[1].legend()
    axes[1].grid(True, which="both", ls=":", alpha=0.6)
    savefig(fig, FIG / "fig08_adaptive_h.png")
    return tA, yA, hA, eA, n_rhs, n_rej, e_ad


def cost_accuracy(h_vals, errs, n_rhs, y_oracle):
    """Matched-accuracy comparison: implicit Euler vs adaptive, cost = RHS evals."""
    # Also run a few adaptive tolerances
    tols = [5e-5, 2e-6, 5e-7]
    ad_err, ad_rhs = [], []
    for tol in tols:
        t0 = time.perf_counter()
        _, yA, hA, _, n_rhs_a, _ = adaptive_implicit_euler(
            robertson_rhs, robertson_jacobian,
            ROBERTSON_Y0, ROBERTSON_T0, ROBERTSON_T1,
            h0=0.1, tol=tol,
        )
        wall = time.perf_counter() - t0
        ad_err.append(np.linalg.norm(yA[-1] - y_oracle, np.inf))
        ad_rhs.append(n_rhs_a)
        print(f"[cost] adaptive tol={tol:.1e}  e={ad_err[-1]:.3e}  n_rhs={n_rhs_a}  "
              f"steps={len(hA)}  wall={wall:.3f}s")

    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    ax.loglog(n_rhs, errs, "o-", color="tab:blue", label="fixed-h implicit Euler")
    ax.loglog(ad_rhs, ad_err, "s-", color="tab:orange", label="adaptive (step doubling)")
    ax.axhline(1.74e-4, color="0.35", ls=":", label=r"matched $e_\infty\approx 1.74\times 10^{-4}$")
    ax.set_xlabel("right-hand-side evaluations [-]")
    ax.set_ylabel(r"$\|y(40)-y_{\mathrm{oracle}}\|_\infty$ [-]")
    ax.set_title("Cost–accuracy: RHS count at comparable y(40) error (setup not counted)")
    ax.legend()
    ax.grid(True, which="both", ls=":", alpha=0.6)
    savefig(fig, FIG / "fig09_cost_accuracy.png")
    return tols, ad_err, ad_rhs


def newton_tolerance_sweep(y_oracle):
    """Show that Newton residual error is far below time-discretisation error."""
    h = 0.1
    tols = [1e-4, 1e-6, 1e-8, 1e-10, 1e-12]
    rows = []
    y_tight = None
    for tol in tols:
        _, y, n_rhs = solve_implicit_euler(
            robertson_rhs, robertson_jacobian,
            ROBERTSON_Y0, ROBERTSON_T0, ROBERTSON_T1, h,
            newton_tol=tol,
        )
        e_ref = np.linalg.norm(y[-1] - y_oracle, np.inf)
        rows.append((tol, y[-1].copy(), e_ref, n_rhs))
        if tol == 1e-12:
            y_tight = y[-1].copy()
        print(f"[newton-tol] tol={tol:.0e}  y(40)={y[-1]}  "
              f"E={e_ref:.4e}  n_rhs={n_rhs}")

    print("[newton-tol] ||y(40; tol) - y(40; 1e-12)||_inf:")
    for tol, y_end, e_ref, n_rhs in rows:
        dy = np.linalg.norm(y_end - y_tight, np.inf)
        print(f"  tol={tol:.0e}  delta={dy:.4e}  E_vs_oracle={e_ref:.4e}")
    return rows


def positivity_probe(y_oracle):
    """Conservation, positivity and full-state error are reported separately.

    Implicit Euler has no positivity guarantee. I test whether large h makes
    y2 undershoot, then try a clip and a reject-negative rule. Neither rule
    comes with a convergence theorem.
    """
    h_vals = [0.05, 0.1, 0.2, 0.4, 0.8, 2.0, 5.0, 10.0]
    print("[positivity] accepted states after t=0 (y2(0)=0 by the IVP)")
    for h in h_vals:
        try:
            _, y, _ = solve_implicit_euler(
                robertson_rhs, robertson_jacobian,
                ROBERTSON_Y0, ROBERTSON_T0, ROBERTSON_T1, h,
                positivity="none",
            )
            min_y2 = float(np.min(y[1:, 1]))
            n_neg = int(np.sum(y[:, 1] < 0.0))
            mass = np.max(np.abs(y.sum(axis=1) - 1.0))
            e_inf = np.linalg.norm(y[-1] - y_oracle, np.inf)
            print(f"  h={h:5.2f}  min_{{t>0}} y2={min_y2:.4e}  n_neg={n_neg:4d}  "
                  f"|1^T y-1|_max={mass:.2e}  E={e_inf:.3e}")
        except RuntimeError as exc:
            print(f"  h={h:5.2f}  FAILED: {exc}")

    print("[positivity] Newton-iterate min w2 on the first step (t=0, various h)")
    for h in (0.1, 0.8, 2.0, 5.0, 10.0):
        w, n_iter, ok, n_rhs, min_w = newton_implicit_euler(
            robertson_rhs, robertson_jacobian, h, ROBERTSON_Y0, h,
        )
        print(f"  h={h:5.2f}  converged={ok}  n_iter={n_iter}  "
              f"accepted y2={w[1]:.4e}  min_iterate w2={min_w[1]:.4e}")

    print("[positivity] clip vs reject at large h")
    for mode in ("clip", "reject"):
        for h in (0.1, 2.0, 5.0, 10.0):
            try:
                _, y, _ = solve_implicit_euler(
                    robertson_rhs, robertson_jacobian,
                    ROBERTSON_Y0, ROBERTSON_T0, ROBERTSON_T1, h,
                    positivity=mode,
                )
                min_y2 = float(np.min(y[1:, 1]))
                mass = np.max(np.abs(y.sum(axis=1) - 1.0))
                e_inf = np.linalg.norm(y[-1] - y_oracle, np.inf)
                print(f"  mode={mode:6s}  h={h:5.2f}  min_{{t>0}} y2={min_y2:.4e}  "
                      f"|1^T y-1|_max={mass:.2e}  E={e_inf:.3e}")
            except RuntimeError as exc:
                print(f"  mode={mode:6s}  h={h:5.2f}  FAILED: {exc}")


def first_newton_residual():
    print("[newton] first-step residuals at t=0.1, h=0.1")
    w = ROBERTSON_Y0.copy()
    y_n = ROBERTSON_Y0
    h = 0.1
    t_next = 0.1
    for k in range(20):
        F = w - y_n - h * robertson_rhs(t_next, w)
        r = np.linalg.norm(F, np.inf)
        print(f"  iter {k:2d}  ||F||_inf = {r:.3e}")
        if r < 1e-12:
            break
        JF = np.eye(3) - h * robertson_jacobian(t_next, w)
        w = w - np.linalg.solve(JF, F)


def main():
    print("=" * 64)
    print("run_all.py  —  Robertson ODE IVP, regenerates report figures")
    print("=" * 64)
    jacobian_check()
    first_newton_residual()
    sol, y_oracle, disc = build_oracle()
    t, y, mass_err, rel = trajectory_and_mass(y_oracle)
    logistic_orders()
    h_vals, errs, n_rhs, wall, min_y2, s_imp, se_imp = robertson_implicit_order(y_oracle)
    newton_tolerance_sweep(y_oracle)
    positivity_probe(y_oracle)
    S40, h_stab, lam40 = stiffness_and_stability(sol, y_oracle)
    finite = explicit_blowup()
    tA, yA, hA, eA, n_rhs_a, n_rej, e_ad = adaptivity(y_oracle)
    cost_accuracy(h_vals, errs, n_rhs, y_oracle)
    print("=" * 64)
    print("figures written to", FIG)
    print("=" * 64)


if __name__ == "__main__":
    main()
