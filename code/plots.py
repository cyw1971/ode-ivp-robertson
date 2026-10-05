"""Figure helpers following the course visualization guide."""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from methods import R_euler, R_rk4, R_implicit_euler


def savefig(fig, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fit_loglog(h, err):
    h = np.asarray(h, dtype=float)
    err = np.asarray(err, dtype=float)
    coef, cov = np.polyfit(np.log(h), np.log(err), 1, cov=True)
    slope, intercept = coef
    slope_err = float(np.sqrt(cov[0, 0]))
    return slope, intercept, slope_err, cov


def plot_convergence(h, err, order_ref, method_label, path, annotate_floor=True):
    """Log-log error vs h with theoretical slope, fit ± SE, and fitted-mean band."""
    h = np.asarray(h, dtype=float)
    err = np.asarray(err, dtype=float)
    slope, intercept, slope_err, cov = fit_loglog(h, err)

    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    ax.loglog(h, err, "o-", color="tab:blue", label=method_label)

    h_lin = np.logspace(np.log10(h.min()), np.log10(h.max()), 60)
    c_ref = err[0] / h[0] ** order_ref
    ax.loglog(h_lin, c_ref * h_lin ** order_ref, "k--",
              label=f"order-{order_ref:g} reference")

    lx = np.linspace(np.log(h.min()), np.log(h.max()), 80)
    line = slope * lx + intercept
    se = np.sqrt(cov[1, 1] + 2.0 * lx * cov[0, 1] + lx ** 2 * cov[0, 0])
    ax.loglog(np.exp(lx), np.exp(line), color="tab:orange", ls="--",
              label=fr"fit ${slope:.2f}\pm{slope_err:.2f}$")
    ax.fill_between(np.exp(lx), np.exp(line - 1.96 * se), np.exp(line + 1.96 * se),
                    color="tab:orange", alpha=0.25,
                    label="fitted-mean $\\pm 1.96\\,\\mathrm{SE}$")

    if annotate_floor:
        idx = int(np.argmin(err))
        ax.annotate("round-off / residual floor",
                    xy=(h[idx], err[idx]),
                    xytext=(h[idx] * 3.0, err[idx] * 4.0),
                    arrowprops=dict(arrowstyle="->", color="0.3"),
                    color="0.3")

    ax.set_xlabel("step size h [-]")
    ax.set_ylabel("global error at T [-]")
    ax.set_title(f"{method_label}: observed order {slope:.2f} (theory {order_ref:g})")
    ax.legend(loc="best")
    ax.grid(True, which="both", ls=":", alpha=0.6)
    savefig(fig, path)
    return slope, slope_err


def plot_stability_regions(path, J=None, h=None, extra_label=None):
    re = np.linspace(-6.0, 3.0, 500)
    im = np.linspace(-4.0, 4.0, 500)
    Re, Im = np.meshgrid(re, im)
    Z = Re + 1j * Im

    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.6), sharey=True)
    specs = [
        (R_euler, "Explicit Euler", "tab:blue"),
        (R_rk4, "RK4", "tab:orange"),
        (R_implicit_euler, "Implicit Euler", "tab:green"),
    ]
    for ax, (R, title, color) in zip(axes, specs):
        mask = np.abs(R(Z)) <= 1.0
        ax.contourf(Re, Im, mask.astype(float), levels=[-0.1, 0.5, 1.5],
                    colors=["white", color], alpha=0.35)
        ax.contour(Re, Im, np.abs(R(Z)), levels=[1.0], colors=["k"], linewidths=1.0)
        ax.axhline(0.0, color="0.5", lw=0.6)
        ax.axvline(0.0, color="0.5", lw=0.6)
        ax.set_title(title)
        ax.set_xlabel(r"$\mathrm{Re}(z)=h\lambda$")
        ax.set_aspect("equal")
        ax.set_xlim(re.min(), re.max())
        ax.set_ylim(im.min(), im.max())
        if J is not None and h is not None:
            lam = np.linalg.eigvals(np.atleast_2d(J))
            pts = h * lam
            ax.scatter(pts.real, pts.imag, marker="x", s=55, color="tab:red",
                       label=extra_label or r"$h\lambda$", zorder=5)
            ax.legend(loc="lower left", fontsize=8)
    axes[0].set_ylabel(r"$\mathrm{Im}(z)$")
    fig.suptitle("Absolute-stability regions; red marks are a frozen-Jacobian diagnostic")
    savefig(fig, path)
