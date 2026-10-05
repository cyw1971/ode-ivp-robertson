"""Robertson kinetics and the logistic test problem.

The integrators in methods.py take callables f(t, y) and optionally jac(t, y).
Swap the model by passing a different pair; the time-stepper never hard-codes
species names.
"""

import numpy as np


# --- Robertson chemical kinetics (problem pack topic 3) -------------------

K1 = 0.04
K2 = 3.0e7
K3 = 1.0e4

ROBERTSON_Y0 = np.array([1.0, 0.0, 0.0])
ROBERTSON_T0 = 0.0
ROBERTSON_T1 = 40.0


def robertson_rhs(t, y):
    """Mass-action RHS. y has shape (3,). Time is unused (autonomous)."""
    y1, y2, y3 = y
    return np.array([
        -K1 * y1 + K3 * y2 * y3,
        K1 * y1 - K3 * y2 * y3 - K2 * y2 * y2,
        K2 * y2 * y2,
    ], dtype=float)


def robertson_jacobian(t, y):
    """Analytic 3x3 Jacobian J_f = df/dy."""
    y1, y2, y3 = y
    return np.array([
        [-K1, K3 * y3, K3 * y2],
        [K1, -K3 * y3 - 2.0 * K2 * y2, -K3 * y2],
        [0.0, 2.0 * K2 * y2, 0.0],
    ], dtype=float)


def finite_difference_jacobian(f, t, y, eps=1e-8):
    """Forward-difference Jacobian, used only as a cross-check of J_f."""
    y = np.asarray(y, dtype=float)
    fy = f(t, y)
    d = y.size
    J = np.empty((d, d), dtype=float)
    for j in range(d):
        yp = y.copy()
        yp[j] += eps
        J[:, j] = (f(t, yp) - fy) / eps
    return J


# --- Logistic growth: non-stiff scalar with a closed form -----------------

LOGISTIC_R = 1.0
LOGISTIC_K = 10.0
LOGISTIC_Y0 = np.array([0.5])
LOGISTIC_T0 = 0.0
LOGISTIC_T1 = 10.0


def logistic_rhs(t, y):
    return LOGISTIC_R * y * (1.0 - y / LOGISTIC_K)


def logistic_exact(t, y0=0.5, r=LOGISTIC_R, K=LOGISTIC_K):
    return K / (1.0 + (K / y0 - 1.0) * np.exp(-r * t))
