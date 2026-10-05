"""Time-stepping methods. Integrators depend only on f (and jac for implicit)."""

import numpy as np


def euler_step(f, t, y, h):
    return y + h * f(t, y)


def rk4_step(f, t, y, h):
    k1 = f(t, y)
    k2 = f(t + 0.5 * h, y + 0.5 * h * k1)
    k3 = f(t + 0.5 * h, y + 0.5 * h * k2)
    k4 = f(t + h, y + h * k3)
    return y + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def newton_implicit_euler(f, jac, t_next, y_n, h, tol=1e-12, max_iter=40,
                          damping=1.0):
    """Solve F(w) = w - y_n - h f(t_next, w) = 0.

    Returns (w, n_iter, converged, n_rhs, min_w). min_w is the smallest
    componentwise value seen among the Newton iterates (including the
    accepted state). Used only for the positivity audit.
    """
    w = np.array(y_n, dtype=float, copy=True)
    min_w = w.copy()
    n_rhs = 0
    for k in range(max_iter):
        fw = f(t_next, w)
        n_rhs += 1
        F = w - y_n - h * fw
        if np.linalg.norm(F, np.inf) < tol:
            min_w = np.minimum(min_w, w)
            return w, k, True, n_rhs, min_w
        JF = np.eye(w.size) - h * jac(t_next, w)
        delta = np.linalg.solve(JF, F)
        w = w - damping * delta
        min_w = np.minimum(min_w, w)
    return w, max_iter, False, n_rhs, min_w


def apply_positivity(y, mode):
    """Empirical positivity fix. No convergence theory is claimed.

    mode='none'   : leave the Newton update unchanged
    mode='clip'   : replace negative entries by 0 (does not restore mass)
    mode='reject' : return None if any entry is negative
    """
    y = np.asarray(y, dtype=float)
    if mode == "none":
        return y
    if mode == "clip":
        return np.maximum(y, 0.0)
    if mode == "reject":
        if np.any(y < 0.0):
            return None
        return y
    raise ValueError(f"unknown positivity mode {mode!r}")


def implicit_euler_step(f, jac, t, y, h, newton_tol=1e-12, positivity="none"):
    y_next, _, ok, n_rhs, min_w = newton_implicit_euler(
        f, jac, t + h, y, h, tol=newton_tol,
    )
    if not ok:
        raise RuntimeError(f"Newton failed at t={t:.6g}, h={h:.3e}")
    if positivity == "clip":
        y_next = apply_positivity(y_next, "clip")
    elif positivity == "reject":
        if np.any(y_next < 0.0) or np.any(min_w < 0.0):
            raise RuntimeError(f"negative component rejected at t={t:.6g}, h={h:.3e}")
    return y_next, n_rhs


def _fixed_step(stepper, f, y0, t0, t1, h, jac=None, stepper_kwargs=None):
    stepper_kwargs = stepper_kwargs or {}
    n_steps = int(np.ceil((t1 - t0) / h))
    t = np.empty(n_steps + 1)
    t[0] = t0
    y = np.zeros((n_steps + 1,) + np.shape(y0))
    y[0] = np.asarray(y0, dtype=float)
    n_rhs = 0
    for n in range(n_steps):
        step = min(h, t1 - t[n])
        t[n + 1] = t[n] + step
        if jac is None:
            y[n + 1] = stepper(f, t[n], y[n], step)
            n_rhs += 1 if stepper is euler_step else 4
        else:
            y[n + 1], nr = stepper(f, jac, t[n], y[n], step, **stepper_kwargs)
            n_rhs += nr
    return t, y, n_rhs


def solve_euler(f, y0, t0, t1, h):
    t, y, n_rhs = _fixed_step(euler_step, f, y0, t0, t1, h)
    return t, y, n_rhs


def solve_rk4(f, y0, t0, t1, h):
    t, y, n_rhs = _fixed_step(rk4_step, f, y0, t0, t1, h)
    return t, y, n_rhs


def solve_implicit_euler(f, jac, y0, t0, t1, h, newton_tol=1e-12,
                         positivity="none"):
    t, y, n_rhs = _fixed_step(
        implicit_euler_step, f, y0, t0, t1, h, jac=jac,
        stepper_kwargs={"newton_tol": newton_tol, "positivity": positivity},
    )
    return t, y, n_rhs


def adaptive_implicit_euler(f, jac, y0, t0, t1, h0, tol, h_min=1e-12,
                            newton_tol=1e-12):
    """Step-doubling controller. Accepts y_fine; h grows at most back to h0."""
    t_list = [float(t0)]
    y_list = [np.asarray(y0, dtype=float).copy()]
    h_used = []
    e_used = []
    n_rhs = 0
    n_reject = 0
    h = float(h0)
    while t_list[-1] < t1 - 1e-15:
        h = min(h, t1 - t_list[-1], h0)
        if h < h_min:
            raise RuntimeError("adaptive h fell below h_min")
        y_coarse, n1 = implicit_euler_step(
            f, jac, t_list[-1], y_list[-1], h, newton_tol=newton_tol,
        )
        y_half, n2 = implicit_euler_step(
            f, jac, t_list[-1], y_list[-1], 0.5 * h, newton_tol=newton_tol,
        )
        y_fine, n3 = implicit_euler_step(
            f, jac, t_list[-1] + 0.5 * h, y_half, 0.5 * h, newton_tol=newton_tol,
        )
        n_rhs += n1 + n2 + n3
        e = np.linalg.norm(y_fine - y_coarse, np.inf)
        if e <= tol:
            t_list.append(t_list[-1] + h)
            y_list.append(y_fine)
            h_used.append(h)
            e_used.append(e)
            if e < tol / 10.0:
                h = min(2.0 * h, h0)
        else:
            h *= 0.5
            n_reject += 1
    return (np.array(t_list), np.array(y_list), np.array(h_used),
            np.array(e_used), n_rhs, n_reject)


def R_euler(z):
    return 1.0 + z


def R_rk4(z):
    return 1.0 + z + z ** 2 / 2.0 + z ** 3 / 6.0 + z ** 4 / 24.0


def R_implicit_euler(z):
    return 1.0 / (1.0 - z)
