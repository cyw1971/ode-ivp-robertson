"""Build a Group-N-style seminar PDF from the Robertson report.

Run: python slides/build_slides_pdf.py
Output: slides/Robertson_Team15_slides.pdf
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parent
FIG = ROOT.parent / "report" / "figures"
OUT = ROOT / "Robertson_Team15_slides.pdf"

# Layout (widescreen, similar to Group N)
W, H = 13.333, 7.5
SECTIONS = [
    "Motivation",
    "Model & Methods",
    "Stability",
    "Validation",
    "Efficiency & Insight",
]
NAVY = "#1B3A5F"
TEAL = "#1F6F8B"
ORANGE = "#C45C26"
INK = "#1F2937"
MUTED = "#4B5563"
CREAM = "#F4F1EA"
LINE = "#D7D0C4"
WHITE = "#FFFFFF"
LIGHT = "#EEF2F6"


def fig_ax():
    fig = plt.figure(figsize=(W, H), facecolor=WHITE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    return fig, ax


def draw_nav(ax, active):
    """Top section strip like Group N."""
    ax.add_patch(Rectangle((0, H - 0.55), W, 0.55, facecolor=NAVY, edgecolor="none"))
    n = len(SECTIONS)
    gap = 0.15
    left = 0.35
    usable = W - 0.7
    width = (usable - gap * (n - 1)) / n
    for i, name in enumerate(SECTIONS):
        x = left + i * (width + gap)
        on = name == active
        ax.add_patch(
            FancyBboxPatch(
                (x, H - 0.48),
                width,
                0.38,
                boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor=ORANGE if on else "#2A4A70",
                edgecolor="none",
            )
        )
        ax.text(
            x + width / 2,
            H - 0.29,
            name,
            ha="center",
            va="center",
            fontsize=9,
            color=WHITE,
            fontweight="bold" if on else "normal",
            fontfamily="sans-serif",
        )


def footer(ax, page, total):
    ax.add_patch(Rectangle((0, 0), W, 0.38, facecolor=NAVY, edgecolor="none"))
    ax.text(
        0.4,
        0.19,
        "Project 1  |  Robertson kinetics  |  Chuyang Wang 2363591",
        ha="left",
        va="center",
        fontsize=9,
        color=WHITE,
    )
    ax.text(
        W - 0.4,
        0.19,
        f"{page} / {total}",
        ha="right",
        va="center",
        fontsize=9,
        color=WHITE,
    )


def title(ax, text, y=H - 1.05):
    ax.text(0.45, y, text, ha="left", va="top", fontsize=22, fontweight="bold", color=NAVY)


def subtitle(ax, text, y=H - 1.35):
    ax.text(0.45, y, text, ha="left", va="top", fontsize=11, color=MUTED, style="italic")


def takeaway(ax, text):
    ax.add_patch(
        FancyBboxPatch(
            (0.4, 0.55),
            W - 0.8,
            0.72,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor=CREAM,
            edgecolor=ORANGE,
            linewidth=1.5,
        )
    )
    ax.text(
        0.65,
        0.91,
        "Takeaway  |  " + text,
        ha="left",
        va="center",
        fontsize=11,
        color=ORANGE,
        fontweight="bold",
        wrap=True,
    )


def bullets(ax, items, x=0.5, y=H - 1.7, size=12, dy=0.42, color=INK, max_width=12):
    for i, item in enumerate(items):
        ax.text(x, y - i * dy, "•  " + item, ha="left", va="top", fontsize=size, color=color)


def put_image(ax, name, left, bottom, width, height):
    path = FIG / name
    img = mpimg.imread(path)
    # axes fraction within figure coordinates
    # Use inset axes
    # Convert inches to figure fraction
    ax_img = ax.figure.add_axes([left / W, bottom / H, width / W, height / H])
    ax_img.imshow(img)
    ax_img.axis("off")
    for spine in ax_img.spines.values():
        spine.set_visible(False)
    return ax_img


def card(ax, x, y, w, h, face=LIGHT):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor=face,
            edgecolor=LINE,
            linewidth=1.0,
        )
    )


TOTAL = 12


def page_title(pdf):
    fig, ax = fig_ax()
    ax.add_patch(Rectangle((0, 0), W, H, facecolor=NAVY, edgecolor="none"))
    ax.add_patch(Rectangle((0, 0), 0.18, H, facecolor=ORANGE, edgecolor="none"))
    ax.text(0.7, 5.9, "MTH321 · Numerical Analysis of ODEs and PDEs", fontsize=12, color="#C9D6E3")
    ax.text(0.7, 4.7, "Numerical Solution of the\nRobertson Kinetics IVP", fontsize=30, fontweight="bold", color=WHITE, linespacing=1.25)
    ax.text(0.7, 3.2, "Chuyang Wang   ·   2363591   ·   Team 15", fontsize=16, color=WHITE)
    ax.text(
        0.7,
        2.2,
        "Stiff chemical kinetics · implicit Euler + Newton · step-doubling\n"
        "No closed form · BDF/Radau oracle · cost = RHS evaluations",
        fontsize=13,
        color="#C9D6E3",
        linespacing=1.4,
    )
    ax.text(0.7, 0.7, "Xi'an Jiaotong-Liverpool University   ·   5 October 2026", fontsize=11, color="#A8B8C8")
    ax.text(W - 0.5, 0.4, f"1 / {TOTAL}", ha="right", color=WHITE, fontsize=10)
    pdf.savefig(fig)
    plt.close(fig)


def page_roadmap(pdf):
    fig, ax = fig_ax()
    draw_nav(ax, "Motivation")
    title(ax, "Presentation Roadmap")
    rows = [
        ("1", "Motivation", "Why is this problem hard?"),
        ("2", "Model & Methods", "What do we solve, and how?"),
        ("3", "Stability", "Can we predict the step-size limit?"),
        ("4", "Validation", "Can we trust the numbers?"),
        ("5", "Efficiency & Insight", "Who is cheapest at matched error?"),
    ]
    for i, (num, head, sub) in enumerate(rows):
        y = 5.5 - i * 0.85
        card(ax, 0.6, y - 0.15, 12.1, 0.7)
        ax.add_patch(
            FancyBboxPatch(
                (0.85, y),
                0.55,
                0.45,
                boxstyle="round,pad=0.02,rounding_size=0.1",
                facecolor=ORANGE,
                edgecolor="none",
            )
        )
        ax.text(1.125, y + 0.22, num, ha="center", va="center", fontsize=16, fontweight="bold", color=WHITE)
        ax.text(1.7, y + 0.32, head, ha="left", va="center", fontsize=16, fontweight="bold", color=NAVY)
        ax.text(1.7, y + 0.05, sub, ha="left", va="center", fontsize=12, color=MUTED)
    footer(ax, 2, TOTAL)
    pdf.savefig(fig)
    plt.close(fig)


def page_hard(pdf):
    fig, ax = fig_ax()
    draw_nav(ax, "Motivation")
    title(ax, "What Makes This Problem Hard?")
    subtitle(ax, "Stiffness here = a stability restriction, not an accuracy restriction")
    # rate bars as text cards
    for i, (lab, val) in enumerate([("k1", "0.04"), ("k3", "10^4"), ("k2", "3×10^7")]):
        x = 0.6 + i * 4.1
        card(ax, x, 4.55, 3.8, 1.15)
        ax.text(x + 1.9, 5.35, lab, ha="center", fontsize=12, color=MUTED)
        ax.text(x + 1.9, 4.9, val, ha="center", fontsize=22, fontweight="bold", color=NAVY)
    ax.text(6.65, 4.2, "k2 / k1 = 7.5×10^8   ·   no closed-form solution", ha="center", fontsize=12, color=ORANGE, fontweight="bold")
    cards = [
        ("No closed form", "Needs a verified oracle\n(BDF + tightened Radau)"),
        ("Exact invariant, y ≥ 0", "Checkable separately\nfrom accuracy E(h)"),
        ("Predictable limit", "Explicit bound\nh < 2/|λ|_max ≈ 5.90×10^−4"),
    ]
    for i, (h, b) in enumerate(cards):
        x = 0.6 + i * 4.1
        card(ax, x, 1.7, 3.8, 2.1, face=CREAM)
        ax.text(x + 0.25, 3.45, f"{i+1}", fontsize=18, fontweight="bold", color=ORANGE)
        ax.text(x + 0.7, 3.5, h, fontsize=13, fontweight="bold", color=NAVY)
        ax.text(x + 0.25, 2.55, b, fontsize=11, color=INK, linespacing=1.4)
    takeaway(ax, "This is a stability problem for explicit methods, not a missing-order problem.")
    footer(ax, 3, TOTAL)
    pdf.savefig(fig)
    plt.close(fig)


def page_model(pdf):
    fig, ax = fig_ax()
    draw_nav(ax, "Model & Methods")
    title(ax, "The Robertson System")
    subtitle(ax, "Mass-action ODE · y(0)=(1,0,0)^T · t ∈ [0, 40]")
    card(ax, 0.45, 2.6, 7.6, 3.5)
    ax.text(
        0.7,
        5.7,
        r"$y_1' = -0.04\,y_1 + 10^4 y_2 y_3$" + "\n"
        r"$y_2' = 0.04\,y_1 - 10^4 y_2 y_3 - 3\times 10^7 y_2^2$" + "\n"
        r"$y_3' = 3\times 10^7 y_2^2$",
        fontsize=15,
        color=INK,
        family="serif",
        linespacing=1.7,
        va="top",
    )
    ax.text(
        0.7,
        3.5,
        r"$1^\top f(y)\equiv 0 \;\Rightarrow\; y_1+y_2+y_3=1$" + "\n"
        r"$\Rightarrow$ structural zero eigenvalue of $J_f$",
        fontsize=13,
        color=NAVY,
        family="serif",
        linespacing=1.5,
        va="top",
    )
    card(ax, 8.3, 4.55, 4.5, 1.55)
    ax.text(8.55, 5.7, "Stiffness ratio", fontsize=12, fontweight="bold", color=NAVY, va="top")
    ax.text(
        8.55,
        5.2,
        r"$S=\dfrac{\max_{\lambda\neq 0}|\mathrm{Re}\,\lambda|}"
        r"{\min_{\lambda\neq 0}|\mathrm{Re}\,\lambda|}$",
        fontsize=13,
        color=INK,
        family="serif",
        va="top",
    )
    card(ax, 8.3, 2.6, 4.5, 1.75)
    ax.text(8.55, 4.05, "At t = 40 (oracle)", fontsize=12, fontweight="bold", color=NAVY, va="top")
    ax.text(
        8.55,
        3.55,
        "λ ≈ −3.39×10³,  0,  −0.021\n"
        "S(40) = 1.58×10⁵\n"
        "Drop the structural zero",
        fontsize=12,
        color=INK,
        linespacing=1.45,
        va="top",
    )
    put_image(ax, "fig01_robertson_trajectory.png", 0.5, 0.55, 6.2, 1.95)
    ax.text(7.0, 1.7, "Implicit Euler h=0.1\ntracks the slow drift\n(y2 scaled ×10⁴).\nNot the order proof.", fontsize=11, color=MUTED, va="top")
    footer(ax, 4, TOTAL)
    pdf.savefig(fig)
    plt.close(fig)


def page_methods(pdf):
    fig, ax = fig_ax()
    draw_nav(ax, "Model & Methods")
    title(ax, "Numerical Methods: Three Integrators + Newton")
    subtitle(ax, "Test equation y'=λy, z=hλ · y_{n+1}=R(z) y_n")
    # table header
    headers = ["Method", "R(z)", "Order", "Type", "Stability"]
    rows = [
        ["Explicit Euler", "1+z", "1", "explicit", "bounded disk"],
        ["RK4", "1+z+z²/2+z³/6+z⁴/24", "4", "explicit", "bounded"],
        ["Implicit Euler", "1/(1−z)", "1", "implicit", "A- and L-stable"],
    ]
    xs = [0.5, 3.2, 8.0, 9.3, 10.7]
    y0 = 5.55
    for j, h in enumerate(headers):
        ax.text(xs[j], y0, h, fontsize=11, fontweight="bold", color=NAVY)
    ax.plot([0.45, 12.9], [y0 - 0.2, y0 - 0.2], color=LINE, lw=1)
    for i, row in enumerate(rows):
        y = y0 - 0.55 - i * 0.48
        for j, cell in enumerate(row):
            ax.text(xs[j], y, cell, fontsize=11, color=INK, family="sans-serif")
    bullets(
        ax,
        [
            "Implicit stages: Newton on F(w)=w−y_n−h f(t_{n+1},w)=0,  J_F=I−h J_f, stop ||F||_∞<10^{−12}.",
            "Explicit Euler / RK4 need NO Newton (f evaluated at known points only).",
            "Adaptivity: step-doubling; accept y_fine if e=||y_fine−y_coarse||_∞ ≤ tol; else h←h/2.",
            "Each accepted adaptive step costs THREE implicit Euler solves (1 coarse + 2 half-steps).",
            "Oracle: SciPy BDF (rtol=10^{−12}) cross-checked with Radau (rtol=10^{−13}); not a method under test.",
            "Three errors: ||ŷ−y_ref|| ≤ discretisation + Newton + oracle reference.",
        ],
        y=3.7,
        size=11.5,
        dy=0.38,
    )
    takeaway(ax, "A-stability, a small Newton residual, and accuracy are three different claims.")
    footer(ax, 5, TOTAL)
    pdf.savefig(fig)
    plt.close(fig)


def page_stability(pdf):
    fig, ax = fig_ax()
    draw_nav(ax, "Stability")
    title(ax, "Stability Regions")
    subtitle(ax, "|R(z)|≤1 (shaded) · hλ overlay is a frozen-Jacobian diagnostic, not a nonlinear proof")
    put_image(ax, "fig03_stability_regions.png", 0.35, 1.55, 8.2, 3.7)
    bullets(
        ax,
        [
            "Explicit Euler: disk |z+1|≤1;",
            "  real axis needs h ≤ 2/|λ|.",
            "RK4: larger but still bounded.",
            "Implicit Euler: left half-plane",
            "  (A-stable); R(z)→0 ⇒ L-stable.",
            "At h=0.1, t=40: fast mode",
            "  z ≈ −339 — outside both",
            "  explicit regions, inside IE.",
        ],
        x=8.7,
        y=5.3,
        size=11,
        dy=0.36,
    )
    takeaway(ax, "Bounded ≠ accurate. A-stable means the linear test does not explode; it does not fix the O(h) error.")
    footer(ax, 6, TOTAL)
    pdf.savefig(fig)
    plt.close(fig)


def page_eigen(pdf):
    fig, ax = fig_ax()
    draw_nav(ax, "Stability")
    title(ax, "Eigenvalues and Stiffness Ratio")
    subtitle(ax, "Along the BDF/Radau oracle · structural zero excluded from S(t)")
    put_image(ax, "fig10_eigenvalues.png", 0.3, 1.55, 6.2, 3.7)
    put_image(ax, "fig11_stiffness.png", 6.7, 1.55, 6.2, 3.7)
    takeaway(ax, "S(40)=1.58×10⁵ from the two nonzero eigenvalues. The fast rate is O(10³), not 3×10⁷.")
    footer(ax, 7, TOTAL)
    pdf.savefig(fig)
    plt.close(fig)


def page_bound(pdf):
    fig, ax = fig_ax()
    draw_nav(ax, "Stability")
    title(ax, "Testable Step-Size Boundary")
    subtitle(ax, r"Prediction: $h_{\mathrm{crit}}=2/|\lambda|_{\max}=2/(3.393\times 10^3)\approx 5.90\times 10^{-4}$")
    put_image(ax, "fig07_explicit_blowup.png", 0.35, 1.55, 7.0, 3.7)
    card(ax, 7.6, 2.0, 5.2, 3.2)
    ax.text(7.85, 4.9, "Explicit Euler experiment", fontsize=12, fontweight="bold", color=NAVY, va="top")
    ax.text(
        7.85,
        4.35,
        "h = 0.01  (≈ 17 × h_crit)\n"
        "→ Inf / NaN on [0, 40]\n\n"
        "True solution stays on the\n"
        "mass simplex — this is a\n"
        "stability failure, not a large\n"
        "truncation error on a bounded orbit.",
        fontsize=12,
        color=INK,
        linespacing=1.45,
        va="top",
    )
    takeaway(ax, "Divergence at h=0.01 matches the frozen-Jacobian bound. Adaptivity does not lift the explicit limit.")
    footer(ax, 8, TOTAL)
    pdf.savefig(fig)
    plt.close(fig)


def page_validation(pdf):
    fig, ax = fig_ax()
    draw_nav(ax, "Validation")
    title(ax, "Are the Numerical Results Trustworthy?")
    subtitle(ax, "p ± SE is one standard error, not a 95% CI for p · oracle error ≪ E(h)")
    put_image(ax, "fig04_order_euler_logistic.png", 0.25, 2.55, 4.15, 2.85)
    put_image(ax, "fig05_order_rk4_logistic.png", 4.5, 2.55, 4.15, 2.85)
    put_image(ax, "fig06_order_implicit_robertson.png", 8.75, 2.55, 4.15, 2.85)
    card(ax, 0.35, 1.55, 12.6, 0.85)
    ax.text(
        0.55,
        2.15,
        "Logistic (exact): Euler 0.943±0.015 (theory 1)   ·   RK4 4.075±0.018 (theory 4)\n"
        "Robertson vs BDF/Radau: IE 0.990±0.002   ·   |BDF−Radau|_∞ = 1.4×10^{−11}   ·   "
        "y_ref(40)≈(0.715827, 9.186×10^{−6}, 0.284164)",
        fontsize=11,
        color=INK,
        va="top",
        linespacing=1.4,
    )
    takeaway(ax, "Observed slopes match theory once h is asymptotic. Newton converging ≠ grid converging.")
    footer(ax, 9, TOTAL)
    pdf.savefig(fig)
    plt.close(fig)


def page_diagnostics(pdf):
    fig, ax = fig_ax()
    draw_nav(ax, "Validation")
    title(ax, "Diagnostics: Three Checks Fail Independently")
    subtitle(ax, "Conservation · positivity · full-state error E(h) must be reported apart")
    put_image(ax, "fig02_mass.png", 0.3, 1.55, 6.0, 3.7)
    card(ax, 6.5, 1.55, 6.4, 3.7)
    ax.text(6.75, 5.0, "What the numbers say", fontsize=12, fontweight="bold", color=NAVY, va="top")
    ax.text(
        6.75,
        4.5,
        "Mass defect (h=0.1): 4.4×10^{−16}\n"
        "  → pass, but a weak test\n\n"
        "min_{t>0} y2 > 0 for all tabulated h\n"
        "  (even h=10); clip/reject never fired\n"
        "  → observation, not a theorem\n\n"
        "Newton tol 10^{−8} vs 10^{−12}:\n"
        "  Δy(40) = 2.21×10^{−7}\n"
        "E(0.1) = 3.48×10^{−4}\n"
        "  → iteration ≪ discretisation",
        fontsize=11.5,
        color=INK,
        linespacing=1.35,
        va="top",
    )
    takeaway(ax, "Accuracy is the oracle comparison E(h), not mass, not ||F||, not y2≥0.")
    footer(ax, 10, TOTAL)
    pdf.savefig(fig)
    plt.close(fig)


def page_efficiency(pdf):
    fig, ax = fig_ax()
    draw_nav(ax, "Efficiency & Insight")
    title(ax, "Efficiency at a Matched y(40) Error")
    subtitle(ax, "Cost = RHS evaluations inside Newton · Jacobian factorisation not counted")
    put_image(ax, "fig09_cost_accuracy.png", 0.3, 1.55, 6.4, 3.7)
    put_image(ax, "fig08_adaptive_h.png", 6.9, 1.55, 6.0, 3.7)
    takeaway(
        ax,
        "Fixed h=0.05 → 2424 RHS at e=1.74×10^{−4}; adaptive same error → 3680 RHS. "
        "h(t) moves and e sits near tol (749 accept / 3 reject), but step-doubling is more expensive.",
    )
    footer(ax, 11, TOTAL)
    pdf.savefig(fig)
    plt.close(fig)


def page_conclude(pdf):
    fig, ax = fig_ax()
    draw_nav(ax, "Efficiency & Insight")
    title(ax, "What I Learned")
    items = [
        (
            "1",
            "Results are trustworthy",
            "Orders 0.943 / 4.075 / 0.990; |BDF−Radau|_∞=1.4×10^{−11}; "
            "Newton Δy ≪ E(h); mass at round-off.",
        ),
        (
            "2",
            "Stiffness = stability restriction",
            "h_crit≈5.90×10^{−4}; explicit h=0.01 diverges. "
            "Adaptivity changes h but does not lift the explicit limit.",
        ),
        (
            "3",
            "L-stable implicit Euler works",
            "IE is A- and L-stable; at h=0.1 tracks the oracle with "
            "componentwise relative errors <1%.",
        ),
        (
            "4",
            "Keep diagnostics apart",
            "Conservation, positivity, Newton residual and E(h) fail independently. "
            "Adaptive reliability ≠ cheaper RHS cost.",
        ),
    ]
    for i, (num, head, body) in enumerate(items):
        y = 5.35 - i * 1.0
        card(ax, 0.5, y - 0.15, 12.3, 0.85)
        ax.add_patch(
            FancyBboxPatch(
                (0.7, y + 0.15),
                0.5,
                0.45,
                boxstyle="round,pad=0.02,rounding_size=0.1",
                facecolor=ORANGE,
                edgecolor="none",
            )
        )
        ax.text(0.95, y + 0.37, num, ha="center", va="center", fontsize=14, fontweight="bold", color=WHITE)
        ax.text(1.45, y + 0.5, head, fontsize=13, fontweight="bold", color=NAVY, va="top")
        ax.text(1.45, y + 0.15, body, fontsize=11, color=INK, va="top")
    ax.text(
        W / 2,
        0.95,
        "Practical recommendation: use L-stable implicit Euler; drive Newton below y2; "
        "monitor E(h), not just mass.   Thank you — Questions?",
        ha="center",
        fontsize=11,
        color=ORANGE,
        fontweight="bold",
    )
    footer(ax, 12, TOTAL)
    pdf.savefig(fig)
    plt.close(fig)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(OUT) as pdf:
        page_title(pdf)
        page_roadmap(pdf)
        page_hard(pdf)
        page_model(pdf)
        page_methods(pdf)
        page_stability(pdf)
        page_eigen(pdf)
        page_bound(pdf)
        page_validation(pdf)
        page_diagnostics(pdf)
        page_efficiency(pdf)
        page_conclude(pdf)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
