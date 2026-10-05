"""Minimal Robertson implicit-Euler + scipy oracle for Week 2 issue-ticket numbers."""

import numpy as np
from scipy.integrate import solve_ivp


def robertson_rhs(t, y):
    y1, y2, y3 = y
    return np.array([
        -0.04 * y1 + 1e4 * y2 * y3,
        0.04 * y1 - 1e4 * y2 * y3 - 3e7 * y2 * y2,
        3e7 * y2 * y2,
    ])


def robertson_jacobian(t, y):
    y1, y2, y3 = y
    return np.array([
        [-0.04, 1e4 * y3, 1e4 * y2],
        [0.04, -1e4 * y3 - 6e7 * y2, -1e4 * y2],
        [0.0, 6e7 * y2, 0.0],
    ])


def newtonsolve_implicit_euler(f, jac, t_next, y_n, h, tol=1e-12, max_iter=30,
                              damping=1.0, trace=False):
    w = y_n.copy()
    residuals = []
    for _ in range(max_iter):
        F = w - y_n - h * f(t_next, w)
        residual_norm = np.linalg.norm(F, np.inf)
        residuals.append(residual_norm)
        if trace:
            print(f"        ||F||_inf = {residual_norm:.3e}")
        if residual_norm < tol:
            return w, True, residuals
        JF = np.eye(len(w)) - h * jac(t_next, w)
        delta = np.linalg.solve(JF, F)
        w = w - damping * delta
    return w, False, residuals


def implicit_euler_step(f, jac, t, y, h):
    y_next, converged, _ = newtonsolve_implicit_euler(f, jac, t + h, y, h)
    if not converged:
        raise RuntimeError(f"Newton failed at t={t:.3f}")
    return y_next


def solve_implicit_euler(f, jac, y0, t0, t1, h):
    n_steps = int(np.ceil((t1 - t0) / h))
    t = np.empty(n_steps + 1)
    t[0] = t0
    y = np.zeros((n_steps + 1,) + np.shape(y0))
    y[0] = y0
    for n in range(n_steps):
        step = min(h, t1 - t[n])
        t[n + 1] = t[n] + step
        y[n + 1] = implicit_euler_step(f, jac, t[n], y[n], step)
    return t, y


def finite_diff_jac(f, t, y, eps=1e-8):
    d = len(y)
    J = np.zeros((d, d))
    fy = f(t, y)
    for j in range(d):
        yp = y.copy()
        yp[j] += eps
        J[:, j] = (f(t, yp) - fy) / eps
    return J


def main():
    y0 = np.array([1.0, 0.0, 0.0])
    t0, t1 = 0.0, 40.0
    h = 0.1

    print("Newton residual on first step t=0.1 (expect rise then quadratic drop)")
    _, ok, res = newtonsolve_implicit_euler(
        robertson_rhs, robertson_jacobian, t0 + h, y0, h, trace=True
    )
    print(f"  converged={ok}, n_printed={len(res)}")

    y_sample = np.array([0.9, 1e-5, 0.1])
    Ja = robertson_jacobian(0.0, y_sample)
    Jn = finite_diff_jac(robertson_rhs, 0.0, y_sample)
    jac_err = np.max(np.abs(Ja - Jn))
    print(f"Analytic vs FD Jacobian max |diff| = {jac_err:.3e} (want ~1e-8)")
    print(f"Row sums of J (mass invariant => ~0): {Ja.sum(axis=1)}")

    t, y = solve_implicit_euler(robertson_rhs, robertson_jacobian, y0, t0, t1, h)
    y_end = y[-1]
    mass_err = np.max(np.abs(y.sum(axis=1) - 1.0))
    print(f"implicit Euler h=0.1  y(40) = {y_end}")
    print(f"mass max|sum-1| = {mass_err:.3e}")
    print(f"min components = {y.min(axis=0)}  (should stay >= 0)")

    sol = solve_ivp(
        robertson_rhs, [t0, t1], y0, method="BDF", rtol=1e-12, atol=1e-14,
        jac=robertson_jacobian,
    )
    y_oracle = sol.y[:, -1]
    sol2 = solve_ivp(
        robertson_rhs, [t0, t1], y0, method="Radau", rtol=1e-14, atol=1e-16,
        jac=robertson_jacobian,
    )
    y_oracle2 = sol2.y[:, -1]
    print(f"BDF oracle  y(40) = {y_oracle}")
    print(f"Radau tight y(40) = {y_oracle2}")
    print("componentwise rel. err (implicit Euler vs BDF):")
    for i, name in enumerate(["y1", "y2", "y3"]):
        rel = abs(y_end[i] - y_oracle[i]) / abs(y_oracle[i])
        print(f"  {name}: euler={y_end[i]:.8e}  oracle={y_oracle[i]:.8e}  rel={rel:.3%}")
    print("oracle self-check |BDF - Radau|:", np.abs(y_oracle - y_oracle2))

    eig = np.linalg.eigvals(robertson_jacobian(40.0, y_oracle))
    print(f"Jacobian eigenvalues at t=40: {eig}")
    nonzero = eig[np.abs(eig) > 1e-8]
    S = np.max(np.abs(nonzero.real)) / np.min(np.abs(nonzero.real))
    print(f"stiffness ratio (nonzero eigs) ~ {S:.3e}")
    lam_max = np.max(np.abs(eig.real))
    print(f"|Re lambda|_max ~ {lam_max:.3e}, explicit Euler needs h < {2.0 / lam_max:.3e}")


if __name__ == "__main__":
    main()
