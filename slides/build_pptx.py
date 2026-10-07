"""Build the 10-minute seminar deck from report figures. Run: python slides/build_pptx.py"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import nsmap
from pptx.oxml import parse_xml
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parent
FIG = ROOT.parent / "report" / "figures"
OUT = ROOT / "Robertson_Team15_slides.pptx"

NAVY = RGBColor(0x1B, 0x3A, 0x5F)
TEAL = RGBColor(0x1F, 0x6F, 0x8B)
ORANGE = RGBColor(0xC4, 0x5C, 0x26)
INK = RGBColor(0x1F, 0x29, 0x37)
MUTED = RGBColor(0x4B, 0x55, 0x63)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CREAM = RGBColor(0xF4, 0xF1, 0xEA)
LINE = RGBColor(0xD7, 0xD0, 0xC4)


def set_run(run, size=18, bold=False, color=INK, font="Calibri"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font


def add_text_box(slide, l, t, w, h, text, size=18, bold=False, color=INK, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=bold, color=color)
    return box


def add_bullets(slide, l, t, w, h, items, size=16):
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = 0
        p.space_after = Pt(5)
        run = p.add_run()
        run.text = item
        set_run(run, size=size, color=INK)
    return box


def bar(slide, y, color=NAVY, height=0.12):
    shp = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(y), Inches(13.333), Inches(height)
    )
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    return shp


def footer(slide, n, total=11):
    bar(slide, 7.28, color=NAVY, height=0.22)
    add_text_box(slide, 0.4, 7.28, 9.5, 0.22, "Project 1  |  Robertson kinetics  |  Chuyang Wang 2363591",
                 size=11, color=WHITE)
    add_text_box(slide, 11.4, 7.28, 1.6, 0.22, f"{n} / {total}",
                 size=11, color=WHITE, align=PP_ALIGN.RIGHT)


def takeaway(slide, text):
    shp = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(6.52), Inches(12.5), Inches(0.68)
    )
    shp.fill.solid()
    shp.fill.fore_color.rgb = CREAM
    shp.line.color.rgb = ORANGE
    tf = shp.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "Takeaway  |  " + text
    set_run(run, size=15, bold=True, color=ORANGE)


def say_box(slide, text, top=1.02, height=1.15):
    shp = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.35), Inches(top), Inches(12.6), Inches(height)
    )
    shp.fill.solid()
    shp.fill.fore_color.rgb = CREAM
    shp.line.color.rgb = TEAL
    tf = shp.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "READ  |  " + text
    set_run(run, size=14, bold=False, color=INK)


def title_slide(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    shp.fill.solid()
    shp.fill.fore_color.rgb = NAVY
    shp.line.fill.background()
    accent = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.18), Inches(7.5))
    accent.fill.solid()
    accent.fill.fore_color.rgb = ORANGE
    accent.line.fill.background()
    add_text_box(s, 0.7, 1.3, 12, 0.35, "Project 1  ·  ODE IVP  ·  6–8 min", size=16, color=RGBColor(0xC9, 0xD6, 0xE3))
    add_text_box(s, 0.7, 1.75, 12, 1.4, "Numerical Solution of the\nRobertson Kinetics IVP", size=34, bold=True, color=WHITE)
    add_text_box(s, 0.7, 3.5, 12.2, 2.6,
                 "READ  |  This talk is Robertson kinetics: a stiff three-species ODE on [0, 40]. "
                 "There is no closed-form solution. I implemented explicit Euler, RK4, and implicit Euler with Newton, "
                 "plus step-doubling adaptivity. SciPy BDF/Radau is only the oracle. "
                 "The main result: implicit Euler is the right tool, but adaptive step-doubling is more expensive "
                 "in RHS evaluations at the same y(40) error.",
                 size=18, color=RGBColor(0xC9, 0xD6, 0xE3))
    add_text_box(s, 0.7, 6.2, 12, 0.4, "Start on the next slide. Do not introduce name or ID.", size=14, color=ORANGE)


def content_title(slide, title, subtitle=None):
    bar(slide, 0, color=NAVY, height=0.92)
    add_text_box(slide, 0.4, 0.18, 12.5, 0.4, title, size=26, bold=True, color=WHITE)
    if subtitle:
        add_text_box(slide, 0.4, 0.55, 12.5, 0.3, subtitle, size=13, color=RGBColor(0xD4, 0xE0, 0xEC))


def picture(slide, name, l, t, w, h):
    path = FIG / name
    slide.shapes.add_picture(str(path), Inches(l), Inches(t), Inches(w), Inches(h))


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    total = 11

    title_slide(prs)

    # 2 model
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "The problem", "Robertson 1966  ·  no closed form  ·  t in [0, 40],  y(0)=(1,0,0)")
    say_box(s, "Robertson is stiff chemical kinetics. Rates 0.04 vs 10^4 vs 3e7. Mass y1+y2+y3=1 is invariant, so J_f has a structural zero eigenvalue. Stiffness uses only the two nonzero eigenvalues: S(40)=1.58e5, lambda_fast≈−3.39e3. This is a stability problem, not a missing-order problem.")
    picture(s, "fig01_robertson_trajectory.png", 0.35, 2.3, 6.4, 3.95)
    add_bullets(s, 6.9, 2.3, 6.0, 4.0, [
        "IVP: dy/dt = f(y),  no analytic solution.",
        "Oracle y(40) ≈ (0.715827, 9.186e−6, 0.284164).",
        "Figure: implicit Euler h=0.1; y2 scaled ×10^4.",
        "It tracks the slow drift; this plot is NOT the order proof.",
        "Question 1: can implicit Euler be trusted?",
        "Question 2: is adaptivity cheaper at the same error?",
    ], size=15)
    takeaway(s, "No closed form. Trust comes from an oracle + stability, not from the trajectory looking smooth.")
    footer(s, 2, total)

    # 3 methods
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Three methods + Newton  (explicit needs NO Newton)")
    say_box(s, "Explicit Euler and RK4 evaluate f at known points — no Newton. Implicit Euler evaluates f at the unknown new state, so each step solves F(w)=w−yn−h f(t_{n+1},w)=0 by Newton: J_F=I−h J_f, stop when ||F||_∞<1e−12. First-step residual rises 4e−3 → 48 then falls: y2(0)=0, not a wrong Jacobian. A-stability, small ||F||, and accuracy are three different claims.")
    add_bullets(s, 0.45, 2.28, 12.4, 4.0, [
        "Explicit Euler:  y_{n+1}=y_n+h f(t_n,y_n).   Order 1.   R(z)=1+z.   No Newton.",
        "RK4: four stages.   Order 4.   Bounded stability region.   No Newton.",
        "Implicit Euler: y_{n+1}=y_n+h f(t_{n+1},y_{n+1}).   Order 1, A-stable and L-stable.   R(z)=1/(1−z).",
        "Newton: start w=y_n; solve J_F δ = F;  w ← w−δ.  SciPy BDF/Radau is the oracle only, not a method under test.",
        "Three errors:  ||ŷ_h − y_ref||  ≤  ||y_h − y||_discretisation  +  ||ŷ_h − y_h||_Newton  +  ||y − y_ref||_oracle.",
        "Step-doubling: e=||y_fine − y_coarse||_∞. Accept y_fine if e≤tol; else reject and h←h/2. Each accept costs 3 implicit solves.",
    ], size=16)
    takeaway(s, "Newton solves the algebraic step. Step-doubling chooses h. Explicit methods skip Newton.")
    footer(s, 3, total)

    # 4 stability
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Stability: R(z), then the blow-up experiment")
    say_box(s, "On y'=λy, y_{n+1}=R(z)y_n with z=hλ. Absolute stability needs |R(z)|≤1. Explicit Euler needs h<2/|λ|_max=5.90e−4. At working h=0.1, the fast mode is z≈−339: outside both explicit regions, inside implicit Euler. Explicit Euler at h=0.01 blows up. The hλ overlay is a frozen-Jacobian diagnostic, not a nonlinear proof.")
    picture(s, "fig03_stability_regions.png", 0.3, 2.25, 6.5, 2.05)
    picture(s, "fig07_explicit_blowup.png", 6.95, 2.25, 6.0, 2.05)
    picture(s, "fig11_stiffness.png", 0.3, 4.35, 6.5, 2.0)
    add_bullets(s, 6.95, 4.35, 6.0, 2.0, [
        "Eigenvalues at t=40: −3.39e3,  0 (structural),  −0.021.",
        "Drop the zero when computing S(t).",
        "S(40)=1.58e5  from the two nonzero eigenvalues.",
        "Blow-up is stability failure: true y stays on the simplex.",
    ], size=14)
    takeaway(s, "Bounded ≠ accurate. h=0.01 diverges because it leaves the stability region.")
    footer(s, 4, total)

    # 5 orders
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Orders  ·  p±SE is one standard error, not a 95% CI for p")
    say_box(s, "Logistic has a closed form, so it checks Euler and RK4. Robertson has none, so implicit Euler is measured against a BDF/Radau oracle. Slopes: Euler 0.943±0.015 (theory 1), RK4 4.075±0.018 (theory 4), implicit Euler 0.990±0.002 (theory 1). |BDF−Radau|_∞=1.4e−11. At h=0.1 all relative errors <1%.")
    picture(s, "fig04_order_euler_logistic.png", 0.25, 2.25, 4.2, 2.55)
    picture(s, "fig05_order_rk4_logistic.png", 4.55, 2.25, 4.2, 2.55)
    picture(s, "fig06_order_implicit_robertson.png", 8.85, 2.25, 4.2, 2.55)
    add_bullets(s, 0.4, 4.85, 12.5, 1.5, [
        "Left: logistic Euler. Ratios 1.81→1.98 approach 2=2^1. Coarsest h=0.4 is not fully asymptotic, so slope is slightly below 1.",
        "Middle: logistic RK4. Ratios approach 16=2^4. This is the second required order test; it does not use the Robertson oracle.",
        "Right: Robertson implicit Euler. Newton converges on every row, but E(h) still halves → solver convergence is not grid convergence.",
    ], size=14)
    takeaway(s, "Observed slopes match theory once h is in the asymptotic regime.")
    footer(s, 5, total)

    # 6 three diagnostics
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Mass, positivity, and E(h) are three different tests")
    say_box(s, "Mass defect at h=0.1 is 4.4e−16. That only says 1^T y=1. After t=0, min y2>0 even at h=10; clip/reject never fired — observation, not a positivity theorem. Newton 1e−8 vs 1e−12 changes y(40) by 2.21e−7; discretisation E(0.1)=3.48e−4. Accuracy is E(h) versus the oracle.")
    picture(s, "fig02_mass.png", 0.3, 2.28, 6.15, 4.0)
    add_bullets(s, 6.6, 2.28, 6.3, 4.0, [
        "Inequality: ||ŷ−y_ref|| ≤ discr. + Newton + oracle.",
        "Mass: 4.4e−16. Weak: a wrong or negative vector can still sum to 1.",
        "Positivity: min_{t>0} y2 ≈ 9.2e−6 > 0 on every tabulated h.",
        "No convergence guarantee for clip.",
        "Newton sweep, fixed h=0.1:",
        "  ||y(40;1e−8)−y(40;1e−12)||_∞ = 2.21e−7",
        "  E(0.1) = 3.48e−4  →  iteration ≪ discretisation.",
        "Relative errors at h=0.1: 0.049%, 0.147%, 0.122%.",
    ], size=14)
    takeaway(s, "Do not call the solution accurate because mass is conserved or y2≥0.")
    footer(s, 6, total)

    # 7 adaptivity
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Adaptivity: h(t) moves, and e(t) sits near tol")
    say_box(s, "h0=0.1, tol=2e−6, step-doubling. 749 accepted steps, 3 rejected. h shrinks to 1.25e−2 then returns to h0. Max local e=1.13e−6 < tol; 89% of accepted e lie in [tol/10, tol]. Terminal e_∞=8.90e−5, smaller than fixed h=0.1 which had 3.48e−4. Newton chooses w; step-doubling chooses h.")
    picture(s, "fig08_adaptive_h.png", 0.3, 2.28, 7.5, 4.0)
    add_bullets(s, 7.95, 2.28, 5.0, 4.0, [
        "Top: accepted h(t). Not a relabelled fixed grid.",
        "Bottom: e=||y_fine−y_coarse||_∞.",
        "Red line = tol = 2e−6; grey = tol/10 (grow h).",
        "749 accept, 3 reject.",
        "h_min=1.25e−2,  h_final=0.1.",
        "max e=1.13e−6,  median e=3.22e−7.",
        "89% of e in [tol/10, tol].",
        "This slide does not yet say it is cheaper.",
    ], size=14)
    takeaway(s, "The brief asked for changing h AND local error near tol. Both are here.")
    footer(s, 7, total)

    # 8 cost
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Cost = RHS counts at matched y(40) error")
    say_box(s, "RHS means right-hand-side evaluations: each call to f(t,y) inside Newton. Jacobian factorisation is not counted. Fixed h=0.05: e_∞=1.74e−4 with 2424 RHS. Adaptive tol=5e−5: same error with 3680 RHS. Each accepted adaptive step costs three implicit Euler solves. Adaptive stepping is more expensive. Report it because the measurement went that way.")
    picture(s, "fig09_cost_accuracy.png", 0.3, 2.28, 6.6, 4.0)
    add_bullets(s, 7.1, 2.28, 5.8, 4.0, [
        "Cost measure named first: f-evaluations, not wall-clock.",
        "Fixed h=0.05 → 2424 RHS → e=1.74e−4.",
        "Adaptive 5e−5 → 3680 RHS → e=1.74e−4.",
        "Adaptive 2e−6 → 6835 RHS → e=8.90e−5.",
        "Why more work? 1 coarse + 2 half-steps per accept.",
        "Dotted line: the matched-accuracy pair.",
        "Step-doubling = reliability, not a cheaper integrator.",
    ], size=14)
    takeaway(s, "At matched accuracy, adaptive step-doubling spent more RHS evaluations than a tuned fixed step.")
    footer(s, 8, total)

    # 9 limitations
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "What is trusted, and what is not")
    say_box(s, "Trust the orders, the explicit blow-up versus 2/|λ|_max, and Newton error ≪ E(h). Do not treat the hλ overlay as a nonlinear stability theorem. Do not treat clip as a positivity-preserving scheme. Step-doubling needs a smooth O(h^2) expansion. Accuracy evidence is the refined oracle.")
    add_bullets(s, 0.5, 2.3, 12.3, 4.0, [
        "Trusted: logistic Euler/RK4 slopes; Robertson implicit Euler 0.990±0.002 vs tightened BDF/Radau.",
        "Trusted: h=0.01 explicit blow-up matches h<5.90e−4.",
        "Not a theorem: red crosses on the stability plot. J_f varies along the trajectory.",
        "Not a theorem: y2≥0 on this IVP. Clip/reject never fired; no convergence guarantee.",
        "Not implemented: positivity-preserving high-order method; embedded implicit pair.",
        "If short on time, skip this slide and go to Conclusions.",
    ], size=16)
    takeaway(s, "A-stability + small mass defect + small ||F|| still do not prove accuracy.")
    footer(s, 9, total)

    # 10 conclusions
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Conclusions  (end here; backup is Q&A only)")
    say_box(s, "Implicit Euler with analytic Newton solves Robertson with observed order 0.990±0.002. Explicit Euler at h=0.01 diverges as predicted. Mass, positivity and E(h) are separate. Adaptive h really moves and e sits near tol, but at matched accuracy it uses more RHS evaluations. Thank you.")
    add_bullets(s, 0.5, 2.3, 12.3, 4.0, [
        "Order: Euler 0.943±0.015,  RK4 4.075±0.018,  implicit Euler 0.990±0.002.",
        "Stability: explicit bound h<5.90e−4; h=0.01 → NaN; implicit h=0.1 stays bounded.",
        "S(40)=1.58e5 from nonzero eigenvalues only (drop the structural zero).",
        "Newton 1e−8 vs 1e−12: Δy(40)=2.21e−7  ≪  E(0.1)=3.48e−4.",
        "Adaptive: 749 accept, 3 reject, 89% of e in [tol/10,tol]; 3680 vs 2424 RHS at the same error.",
        "Reproduce: python code/run_all.py. Git history is in the code zip.",
    ], size=16)
    takeaway(s, "A stable first-order method is the right tool; adaptivity bought reliability, not cheaper work.")
    footer(s, 10, total)

    # 11 backup
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Backup / Q&A  (do not present this slide)")
    add_bullets(s, 0.45, 1.15, 12.4, 5.9, [
        "Q: bounded but E larger than the target — accurate?  A: No. Bounded = stability. Accurate = E < target. Example: y'=-y, h=1, implicit Euler is stable with error 0.132.",
        "Q: why drop λ=0 in S(t)?  A: 1^T f=0 ⇒ structural zero. Including it makes S=∞. S(40)=1.58e5 from the other two.",
        "Q: Newton vs step-doubling?  A: Newton solves F(w)=0 inside one step. Step-doubling accepts/rejects h using e=||y_fine−y_coarse||.",
        "Q: mass + positivity ⇒ accurate?  A: No. Whole simplex can have 1^T y=1 and y≥0. Accuracy is E vs oracle.",
        "Q: why tighten Radau and compare BDF?  A: oracle error must be ≪ E(h). |BDF−Radau|_∞=1.4e−11 vs E(0.1)=3.48e−4. SciPy Radau is 3-stage Radau IIA (order 5), not implicit Euler.",
        "Oracle y(40)≈(0.715827, 9.186e−6, 0.284164). First Newton ||F||: 4.00e−3, 47.6, …, 5.55e−17 (12 iters). FD Jacobian 3.2e−12.",
    ], size=14)
    footer(s, 11, total)

    prs.save(OUT)
    print("wrote", OUT)

    # 2 model
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "The problem", "Robertson 1966  ·  stiff chemical kinetics on [0, 40]")
    add_bullets(s, 0.45, 1.15, 7.2, 5.0, [
        "y(0) = (1, 0, 0),  three species A, B, C.",
        "Rates span eight orders: 0.04 vs 10^4 vs 3×10^7.",
        "Mass is an invariant:  y1 + y2 + y3 = 1.",
        "J_f always has a structural zero eigenvalue.",
        "Stiffness from the two nonzero eigenvalues:",
        "S(40) = 1.58×10^5,   λ_fast ≈ −3.39×10^3.",
        "Question: can implicit Euler be trusted here,",
        "and is adaptivity cheaper at the same error?",
    ], size=18)
    picture(s, "fig01_robertson_trajectory.png", 7.6, 1.15, 5.3, 3.2)
    add_text_box(s, 7.6, 4.4, 5.3, 0.4, "Implicit Euler, h = 0.1, tracks the slow drift.", size=12, color=MUTED)
    takeaway(s, "This is a stability problem, not a missing-order problem.")
    footer(s, 2, total)

    # 3 methods
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Three one-step methods + Newton", "I implemented the time-steppers; SciPy BDF/Radau is only the oracle.")
    add_bullets(s, 0.45, 1.2, 12.4, 5.0, [
        "Explicit Euler:  y_{n+1} = y_n + h f(t_n, y_n).     Order 1.    R(z) = 1 + z.",
        "Classical RK4: four stages.                         Order 4.    Bounded stability region.",
        "Implicit Euler: y_{n+1} = y_n + h f(t_{n+1}, y_{n+1}).  Order 1, A-stable and L-stable.  R(z) = 1/(1−z).",
        "Newton solves F(w) = w − y_n − h f(t_{n+1}, w) = 0,  with J_F = I − h J_f,  stop at ||F||_∞ < 10^{−12}.",
        "Adaptivity: step-doubling. Accept y_fine if e = ||y_fine − y_coarse||_∞ ≤ tol; else halve h.",
        "First Robertson step: residual rises 4×10^{−3} → 48 before quadratic decay. That is y2(0)=0, not a wrong Jacobian.",
    ], size=17)
    takeaway(s, "A-stability, a small Newton residual, and accuracy are three different claims.")
    footer(s, 3, total)

    # 4 stability
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Stability: prediction, then the experiment", "hλ overlay is a frozen-Jacobian diagnostic, not a nonlinear proof.")
    picture(s, "fig03_stability_regions.png", 0.35, 1.1, 7.7, 2.55)
    picture(s, "fig07_explicit_blowup.png", 8.15, 1.1, 4.8, 2.55)
    picture(s, "fig11_stiffness.png", 0.35, 3.75, 6.2, 2.55)
    add_bullets(s, 6.7, 3.75, 6.2, 2.5, [
        "Explicit Euler needs h < 5.90×10^{−4}.",
        "h = 0.01 already blows up (NaN).",
        "Working implicit step h = 0.1 puts",
        "the fast mode at z ≈ −339, inside IE,",
        "far outside both explicit regions.",
    ], size=16)
    takeaway(s, "Divergence at h = 0.01 is a stability failure. The true solution stays on the mass simplex.")
    footer(s, 4, total)

    # 5 orders
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Orders against an oracle I built", "p ± SE is one standard error, not a 95% CI for p.")
    picture(s, "fig04_order_euler_logistic.png", 0.3, 1.1, 4.2, 3.35)
    picture(s, "fig05_order_rk4_logistic.png", 4.55, 1.1, 4.2, 3.35)
    picture(s, "fig06_order_implicit_robertson.png", 8.8, 1.1, 4.2, 3.35)
    add_text_box(s, 0.3, 4.5, 12.7, 0.85,
                 "Logistic (exact): Euler 0.943 ± 0.015 (theory 1),   RK4 4.075 ± 0.018 (theory 4).\n"
                 "Robertson vs BDF/Radau oracle: implicit Euler 0.990 ± 0.002.  |BDF − Radau|_∞ = 1.4×10^{−11}.\n"
                 "At h = 0.1, componentwise relative errors are all < 1%.",
                 size=16)
    takeaway(s, "Observed slopes match theory once h is in the asymptotic regime.")
    footer(s, 5, total)

    # 6 three diagnostics
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Conservation, positivity, and E(h) are separate", "An inaccurate or even negative vector can still sum to one.")
    picture(s, "fig02_mass.png", 0.35, 1.1, 6.3, 3.3)
    add_bullets(s, 6.9, 1.15, 6.0, 5.0, [
        "Mass defect at h = 0.1:  4.4×10^{−16}  (round-off).",
        "After t = 0, min y2 stays positive for every tabulated h, including h = 10.",
        "Clip / reject never fired. Observation, not a positivity theorem.",
        "Newton sweep at fixed h = 0.1:",
        "||y(40; 10^{−8}) − y(40; 10^{−12})||_∞ = 2.21×10^{−7}.",
        "Time-discretisation error E(0.1) = 3.48×10^{−4}.",
        "Iteration error is ~ 6×10^{−4} of the discrete error.",
    ], size=16)
    takeaway(s, "Accuracy is the oracle comparison E(h), not mass, not ||F||, not y2 ≥ 0.")
    footer(s, 6, total)

    # 7 adaptivity
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Adaptivity: h changes, and e(t) sits near tol", "h0 = 0.1,  tol = 2×10^{−6},  step-doubling.")
    picture(s, "fig08_adaptive_h.png", 0.4, 1.05, 8.0, 5.25)
    add_bullets(s, 8.55, 1.2, 4.4, 5.0, [
        "749 accepted steps.",
        "3 rejected steps.",
        "h shrinks to 1.25×10^{−2}, then grows back to h0.",
        "max local e = 1.13×10^{−6} < tol.",
        "89% of accepted e in [tol/10, tol].",
        "Terminal e_∞ = 8.90×10^{−5},",
        "smaller than fixed h = 0.1.",
    ], size=16)
    takeaway(s, "A relabelled fixed grid would not produce this h(t), and the estimator tracks the tolerance.")
    footer(s, 7, total)

    # 8 cost
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Cost–accuracy at a matched y(40) error", "Cost = RHS evaluations during Newton. Jacobian factorisation is not counted.")
    picture(s, "fig09_cost_accuracy.png", 0.35, 1.1, 7.3, 5.15)
    add_bullets(s, 7.85, 1.2, 5.1, 5.0, [
        "Fixed h = 0.05:  e_∞ = 1.74×10^{−4}  with 2424 RHS.",
        "Adaptive tol = 5×10^{−5}:  same error, 3680 RHS.",
        "Each accepted adaptive step costs three implicit Euler solves.",
        "Step-doubling is a reliability tool, not a cheaper integrator, once a good fixed h is known.",
        "I report this because the measurement went that way.",
    ], size=16)
    takeaway(s, "At matched accuracy, adaptive step-doubling spent more RHS evaluations than a tuned fixed step.")
    footer(s, 8, total)

    # 9 limitations
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "What I trust, and what I do not", "Limitations stated in the same sentence as the claim.")
    add_bullets(s, 0.5, 1.25, 12.3, 5.0, [
        "Trust: orders vs logistic exact + tightened BDF/Radau oracle; explicit blow-up matches 2/|λ|_max; Newton error ≪ E(h).",
        "Do not treat hλ overlays as a nonlinear stability theorem. J_f varies; the overlay is local.",
        "Do not treat clip/reject as a positivity-preserving scheme. They never fired; there is no convergence guarantee.",
        "Step-doubling assumes a smooth O(h^2) error expansion. Fine here; would fail on a non-smooth right-hand side.",
        "I did not implement a positivity-preserving high-order method or an embedded implicit pair.",
    ], size=18)
    takeaway(s, "The evidence for accuracy is the refined oracle, not A-stability or a conserved sum.")
    footer(s, 9, total)

    # 10 conclusions
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Conclusions")
    add_bullets(s, 0.5, 1.2, 12.3, 5.0, [
        "Implicit Euler + analytic Newton Jacobian solves Robertson on [0, 40] with observed order 0.990 ± 0.002.",
        "Explicit Euler at h = 0.01 diverges, as the frozen-Jacobian bound predicted.",
        "Mass, positivity, and E(h) answer different questions; I reported all three.",
        "Adaptive stepping really moves h, and local error stays near tol — but it is more expensive in RHS counts.",
        "Reproducible: python code/run_all.py; git history is iterative, submitted with the code zip.",
    ], size=18)
    takeaway(s, "A stable first-order method is the right tool here; adaptivity bought reliability, not cheaper work.")
    footer(s, 10, total)

    # 11 backup
    s = prs.slides.add_slide(prs.slide_layouts[6])
    content_title(s, "Backup: numbers I may be asked", "Viva / Q&A")
    add_bullets(s, 0.5, 1.15, 12.3, 5.4, [
        "Oracle y(40) ≈ (0.715827,  9.186×10^{−6},  0.284164).  Implicit Euler h=0.1: relative errors 0.049%, 0.147%, 0.122%.",
        "Newton first-step ||F||_∞:  4.00×10^{−3},  47.6,  11.9,  …,  5.55×10^{−17}  (12 iterations).",
        "Jacobian FD check: max |J_an − J_FD| = 3.2×10^{−12}; every column of J_f sums to 0.",
        "Table 2 min_{t>0} y2 at h = 0.8 … 0.05: all ~ 9.2×10^{−6} > 0.",
        "Adaptive vs fixed at matched e_∞ ≈ 1.74×10^{−4}:  3680 RHS vs 2424 RHS.",
        "SciPy Radau in the oracle is 3-stage Radau IIA (order 5). I did not implement it as a method under test.",
    ], size=16)
    footer(s, 11, total)

    prs.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
