# Robertson ODE IVP (Project 1)

Team 15. Python 3.11+, numpy/scipy/matplotlib (see `requirements.txt`).

```text
python -m pip install -r requirements.txt
python code/validation_tests.py
python code/run_all.py
```

`run_all.py` regenerates every figure in `figures/` that the report cites. No absolute paths. Cost measure in `fig09_cost_accuracy.png` is **right-hand-side evaluations**, not wall-clock; Jacobian factorisation and plotting are not counted.

| Figure | Claim |
|---|---|
| `fig01_robertson_trajectory.png` | Implicit Euler tracks the BDF oracle |
| `fig02_mass.png` | Linear invariant to round-off |
| `fig03_stability_regions.png` | \(h\lambda\) overlay at \(t=40\), \(h=0.1\) |
| `fig04_order_euler_logistic.png` | Week-3 challenge: Euler slope \(\pm\mathrm{SE}\) and fitted-mean band |
| `fig05_order_rk4_logistic.png` | RK4 observed order 4 |
| `fig06_order_implicit_robertson.png` | Implicit Euler order 1 on Robertson |
| `fig07_explicit_blowup.png` | Explicit Euler \(h=0.01\) diverges |
| `fig08_adaptive_h.png` | Adaptive \(h(t)\) and local \(e(t)\) near tol |
| `fig09_cost_accuracy.png` | RHS cost at comparable error |
| `fig10_eigenvalues.png` | Jacobian spectrum vs \(t\) |
| `fig11_stiffness.png` | \(S(t)\) up to \(\sim 1.58\times 10^5\) |
