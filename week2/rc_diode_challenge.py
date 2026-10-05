"""
rc_diode_challenge.py - Full vs adaptive-damped Newton for one implicit
Euler step in a two-node RC circuit with a diode.

Individual challenge, Tutorial 2.
"""

from pathlib import Path

import numpy as np

R1 = R2 = 100.0
C1 = C2 = 10e-6
Vs = 5.0
Is = 1e-12
VT = 0.02585
T = 20e-3
GRID_MS = [0.1, 0.2, 0.4, 0.8, 1.0, 2.0, 4.0, 8.0, 20.0]
MAX_NEWTON_ITER = 10


def F(v, v_n, h):
    v1, v2 = v
    v1n, v2n = v_n
    with np.errstate(over="ignore"):
        diode = Is * (np.exp(np.clip(v2 / VT, None, 80.0)) - 1.0)
    return np.array([
        C1 * (v1 - v1n) / h - (Vs - v1) / R1 + (v1 - v2) / R2,
        C2 * (v2 - v2n) / h - (v1 - v2) / R2 + diode,
    ])


def J(v, h):
    v1, v2 = v
    with np.errstate(over="ignore"):
        dI_dv2 = (Is / VT) * np.exp(np.clip(v2 / VT, None, 80.0))
    return np.array([
        [C1 / h + 1 / R1 + 1 / R2, -1 / R2],
        [-1 / R2, C2 / h + 1 / R2 + dI_dv2],
    ])


def newton_step(v_n, h, mode, tol=1e-12, max_iter=300, trace=False):
    w = v_n.copy().astype(float)
    n_iter = 0
    residuals = []
    v2_hist = []
    for _ in range(max_iter):
        f = F(w, v_n, h)
        r = np.linalg.norm(f)
        residuals.append(r)
        v2_hist.append(w[1])
        if trace:
            print(f"    iter={n_iter:3d}  ||F||={r:.3e}  v=({w[0]:.6f}, {w[1]:.6f})")
        if r < tol:
            return w, n_iter, True, residuals, v2_hist
        delta = np.linalg.solve(J(w, h), -f)
        if mode == "full":
            w = w + delta
            n_iter += 1
        else:
            lam = 1.0
            accepted = False
            w_try = w + lam * delta
            for _bt in range(60):
                r_try = np.linalg.norm(F(w_try, v_n, h))
                if r_try < r:
                    w = w_try
                    n_iter += 1
                    accepted = True
                    break
                lam *= 0.5
                w_try = w + lam * delta
            if not accepted:
                return w, n_iter, False, residuals, v2_hist
    return w, n_iter, False, residuals, v2_hist


def simulate(h, mode):
    n_steps = max(1, int(round(T / h)))
    v = np.zeros(2)
    max_iter = 0
    for _ in range(n_steps):
        v, n_iter, ok, _, _ = newton_step(v, h, mode)
        max_iter = max(max_iter, n_iter)
        if not ok:
            return v, max_iter, False
    return v, max_iter, True


def first_step_story():
    h = 1e-3
    v0 = np.zeros(2)
    print("-" * 68)
    print("First-step traces at h = 1 ms from v = (0, 0)")
    print("Expected: full Newton spikes then retreats ~VT/iter (21 iters);")
    print("          damped Newton monotone drop (6 iters).")
    print("-" * 68)
    print("[full]")
    vf, nf, okf, rf, v2f = newton_step(v0, h, "full", trace=True)
    print(f"  -> n_iter={nf}, converged={okf}, v={vf}")
    if len(v2f) >= 3:
        print(f"  v2 after first update: {v2f[1]:.4f} V (overshoot)")
        dv = np.diff(v2f[1:min(6, len(v2f))])
        print(f"  subsequent Delta v2: {dv}  (theory ~ -VT = {-VT:.5f})")
    print("[damped]")
    vd, nd, okd, rd, v2d = newton_step(v0, h, "damped", trace=True)
    print(f"  -> n_iter={nd}, converged={okd}, v={vd}")
    return nf, nd


def main():
    print("=" * 68)
    print("rc_diode_challenge.py - full vs adaptive-damped Newton")
    print("criterion: every Newton solve over [0, 20 ms] converges")
    print(f"           in <= {MAX_NEWTON_ITER} iterations")
    print("=" * 68)

    n_full_first, n_damped_first = first_step_story()

    print()
    print(f"{'h[ms]':>8} | {'full maxit':>10} | {'damped maxit':>12} | "
          f"{'full<=10?':>10} | {'damped<=10?':>12}")
    print("-" * 68)

    full_pass = []
    damped_pass = []
    rows = []
    for h_ms in GRID_MS:
        h = h_ms * 1e-3
        _, full_it, full_ok = simulate(h, "full")
        _, damp_it, damp_ok = simulate(h, "damped")
        full_le10 = bool(full_ok and full_it <= MAX_NEWTON_ITER)
        damp_le10 = bool(damp_ok and damp_it <= MAX_NEWTON_ITER)
        if full_le10:
            full_pass.append(h_ms)
        if damp_le10:
            damped_pass.append(h_ms)
        rows.append((h_ms, full_it, damp_it, full_ok, damp_ok, full_le10, damp_le10))
        print(f"{h_ms:8.1f} | {full_it:10d} | {damp_it:12d} | "
              f"{str(full_le10):>10} | {str(damp_le10):>12}"
              f"  (conv full={full_ok}, damped={damp_ok})")

    h_full = max(full_pass) if full_pass else None
    h_damped = max(damped_pass) if damped_pass else None

    def fmt(h):
        if h is None:
            return "none"
        if abs(h - T * 1e3) < 1e-12:
            return "20.0 = T"
        return f"{h} ms"

    print()
    print("largest h with every step <= 10 iterations:  "
          f"full = {fmt(h_full)}, damped = {fmt(h_damped)}")
    print()
    print("Submission pair:")
    print(f"  h_max(full) -> h_max(damped)  =  {h_full} ms -> {h_damped} ms")
    print(f"  first-step h=1 ms iterations: full={n_full_first}, damped={n_damped_first}")

    out = Path(__file__).resolve().parent / "rc_diode_challenge_result.txt"
    lines = [
        f"first_step_full_iters={n_full_first}",
        f"first_step_damped_iters={n_damped_first}",
        f"h_max_full_ms={h_full}",
        f"h_max_damped_ms={h_damped}",
        "table:",
    ]
    for row in rows:
        lines.append(
            f"  h={row[0]} ms  full_maxit={row[1]}  damped_maxit={row[2]}  "
            f"full_ok={row[3]}  damped_ok={row[4]}  "
            f"full_le10={row[5]}  damped_le10={row[6]}"
        )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
