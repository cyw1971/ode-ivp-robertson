"""PASS/FAIL checks used in the report's validation section."""

import sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, str(Path(__file__).resolve().parent))

from model import (
    robertson_rhs, robertson_jacobian, logistic_rhs, logistic_exact,
    ROBERTSON_Y0, ROBERTSON_T0, ROBERTSON_T1, LOGISTIC_Y0,
)
from methods import solve_euler, solve_rk4, solve_implicit_euler


def test_logistic_euler_order():
    h = np.array([0.4, 0.2, 0.1, 0.05])
    err = []
    for hh in h:
        _, y, _ = solve_euler(logistic_rhs, LOGISTIC_Y0, 0.0, 10.0, hh)
        err.append(abs(y[-1, 0] - logistic_exact(10.0, LOGISTIC_Y0[0])))
    slope = np.polyfit(np.log(h), np.log(err), 1)[0]
    assert 0.7 <= slope <= 1.3, slope
    print("PASS logistic Euler order", f"{slope:.2f}")


def test_logistic_rk4_order():
    h = np.array([0.4, 0.2, 0.1, 0.05])
    err = []
    for hh in h:
        _, y, _ = solve_rk4(logistic_rhs, LOGISTIC_Y0, 0.0, 10.0, hh)
        err.append(abs(y[-1, 0] - logistic_exact(10.0, LOGISTIC_Y0[0])))
    slope = np.polyfit(np.log(h), np.log(err), 1)[0]
    assert 3.5 <= slope <= 4.5, slope
    print("PASS logistic RK4 order", f"{slope:.2f}")


def test_mass_and_oracle():
    _, y, _ = solve_implicit_euler(
        robertson_rhs, robertson_jacobian, ROBERTSON_Y0,
        ROBERTSON_T0, ROBERTSON_T1, 0.1,
    )
    mass_err = np.max(np.abs(y.sum(axis=1) - 1.0))
    assert mass_err < 1e-10, mass_err
    sol = solve_ivp(
        robertson_rhs, [0.0, 40.0], ROBERTSON_Y0,
        method="BDF", rtol=1e-12, atol=1e-14, jac=robertson_jacobian,
    )
    rel = np.abs(y[-1] - sol.y[:, -1]) / np.abs(sol.y[:, -1])
    assert np.all(rel < 0.01), rel
    print("PASS mass", f"{mass_err:.2e}", "and oracle rel", rel)


def test_positivity_y2():
    _, y, _ = solve_implicit_euler(
        robertson_rhs, robertson_jacobian, ROBERTSON_Y0,
        ROBERTSON_T0, ROBERTSON_T1, 0.1,
    )
    min_y2 = float(np.min(y[:, 1]))
    assert min_y2 >= 0.0, min_y2
    print("PASS positivity min y2", f"{min_y2:.4e}")


def test_jacobian_column_sum():
    y = np.array([0.7, 1e-5, 0.3])
    col = robertson_jacobian(0.0, y).sum(axis=0)
    assert np.max(np.abs(col)) < 1e-10, col
    print("PASS Jacobian column sums", col)


if __name__ == "__main__":
    test_logistic_euler_order()
    test_logistic_rk4_order()
    test_jacobian_column_sum()
    test_mass_and_oracle()
    test_positivity_y2()
    print("ALL TESTS PASS")
