import streamlit as st

import math
import re
from collections import Counter
import sympy as sp

# ==============================================================================
# PAGE CONFIGURATION & STYLING
# ==============================================================================
st.set_page_config(
    page_title="MathSolve Pro • Slide-Wise Mathematics Suite",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background:
      radial-gradient(circle at 10% 0%, rgba(99,102,241,0.06), transparent 25%),
      radial-gradient(circle at 90% 10%, rgba(14,165,233,0.05), transparent 25%),
      #f8fafc;
}

/* Slide Deck Header Banner */
.slide-banner {
    padding: 24px 30px;
    border-radius: 20px;
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 55%, #0f766e 100%);
    color: #ffffff;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.15);
    margin-bottom: 24px;
}
.slide-badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.15);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.slide-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 32px;
    font-weight: 700;
    line-height: 1.15;
    margin: 0 0 8px;
}
.slide-desc {
    font-size: 15px;
    color: #e2e8f0;
    margin: 0;
    max-width: 800px;
    line-height: 1.5;S
}

/* Math Card */
.math-card {
    padding: 24px;
    border-radius: 18px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04);
    margin-bottom: 20px;
}

/* Step-by-Step Item */
.step-item {
    padding: 14px 18px;
    margin: 8px 0;
    border-radius: 12px;
    background: #f8fafc;
    border-left: 4px solid #4f46e5;
    color: #1e293b;
    font-size: 14.5px;
    line-height: 1.5;
}

/* Final Answer Box */
.final-answer-box {
    padding: 20px 24px;
    border-radius: 16px;
    background: linear-gradient(135deg, #eef2ff 0%, #f0fdf4 100%);
    border: 1.5px solid #818cf8;
    color: #0f172a;
    font-size: 22px;
    font-weight: 800;
    margin-top: 15px;
    box-shadow: 0 4px 15px rgba(79, 70, 229, 0.08);
}

/* Topic Card for Dashboard */
.topic-tile {
    padding: 20px;
    border-radius: 16px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
    min-height: 170px;
}
.topic-icon {
    font-size: 28px;
    margin-bottom: 8px;
}
.topic-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 6px;
}
.topic-desc {
    color: #64748b;
    font-size: 13.5px;
    line-height: 1.45;
}

div.stButton > button {
    border-radius: 12px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# MATHEMATICAL SOLVER ENGINES
# ==============================================================================

# 1. DIVISIBILITY CHECKER
def check_divisibility(a: int, b: int):
    if b == 0:
        return {"success": False, "error": "Division by zero is mathematically undefined. Divisor (b) cannot be 0."}
    q = a // b
    r = a % b
    is_divisible = (r == 0)
    division_latex = rf"{a} = {b} \times ({q}) + {r}"
    steps = [
        f"Apply Division Algorithm: For integers $a$ and $b$ ($b \\neq 0$), $a = bq + r$ with $0 \\le r < |b|$.",
        f"Compute quotient: $q = \\lfloor {a} / {b} \\rfloor = {q}$",
        f"Compute remainder: $r = {a} - ({b} \\times {q}) = {r}$",
        f"Division form: $${division_latex}$$"
    ]
    if is_divisible:
        conclusion = f"Since remainder $r = 0$, **{a} is divisible by {b}** (i.e. ${b} \\mid {a}$)."
    else:
        conclusion = f"Since remainder $r = {r} \\neq 0$, **{a} is NOT divisible by {b}** (i.e. ${b} \\nmid {a}$)."
    steps.append(conclusion)
    return {"success": True, "a": a, "b": b, "quotient": q, "remainder": r, "division_latex": division_latex, "steps": steps, "conclusion": conclusion}

def get_factors(n: int):
    n_abs = abs(n)
    if n_abs == 0:
        return {"factors": [0], "factor_count": "Infinite", "prime_factors": {}}
    factors = []
    for i in range(1, int(n_abs**0.5) + 1):
        if n_abs % i == 0:
            factors.append(i)
            if i * i != n_abs:
                factors.append(n_abs // i)
    factors.sort()
    temp, prime_factors, d = n_abs, {}, 2
    while d * d <= temp:
        while temp % d == 0:
            prime_factors[d] = prime_factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        prime_factors[temp] = prime_factors.get(temp, 0) + 1
    pf_str = " \\times ".join(f"{p}^{{{exp}}}" if exp > 1 else str(p) for p, exp in prime_factors.items()) if prime_factors else "1"
    return {"factors": factors, "factor_count": len(factors), "prime_factors": prime_factors, "prime_factorization_latex": pf_str}

def test_divisibility_rules(n: int):
    val = abs(n)
    digits = [int(ch) for ch in str(val)]
    sum_digits = sum(digits)
    last_digit = digits[-1]
    last2 = int(str(val)[-2:]) if val >= 10 else val
    last3 = int(str(val)[-3:]) if val >= 100 else val
    alt_sum = sum(d if i % 2 == 0 else -d for i, d in enumerate(reversed(digits)))
    return [
        {"divisor": 2, "passed": (last_digit % 2 == 0), "explanation": f"Last digit is {last_digit} (even: {last_digit % 2 == 0})."},
        {"divisor": 3, "passed": (sum_digits % 3 == 0), "explanation": f"Sum of digits = {sum_digits} (divisible by 3: {sum_digits % 3 == 0})."},
        {"divisor": 4, "passed": (last2 % 4 == 0), "explanation": f"Last two digits: {last2} ({last2} % 4 = {last2 % 4})."},
        {"divisor": 5, "passed": (last_digit in (0, 5)), "explanation": f"Last digit is {last_digit}."},
        {"divisor": 6, "passed": (last_digit % 2 == 0 and sum_digits % 3 == 0), "explanation": f"Divisible by 2 and 3: {last_digit % 2 == 0 and sum_digits % 3 == 0}."},
        {"divisor": 8, "passed": (last3 % 8 == 0), "explanation": f"Last three digits: {last3} ({last3} % 8 = {last3 % 8})."},
        {"divisor": 9, "passed": (sum_digits % 9 == 0), "explanation": f"Sum of digits = {sum_digits} (divisible by 9: {sum_digits % 9 == 0})."},
        {"divisor": 10, "passed": (last_digit == 0), "explanation": f"Last digit is {last_digit}."},
        {"divisor": 11, "passed": (alt_sum % 11 == 0), "explanation": f"Alternating sum = {alt_sum} ({alt_sum} % 11 = {alt_sum % 11})."}
    ]

# 2. GCD CALCULATOR
def compute_gcd_steps(a: int, b: int):
    orig_a, orig_b = a, b
    a_abs, b_abs = abs(a), abs(b)
    if a_abs == 0 and b_abs == 0:
        return {"success": False, "error": "GCD(0, 0) is undefined."}
    if a_abs == 0:
        return {"success": True, "a": a, "b": b, "gcd": b_abs, "lcm": 0, "steps": [f"$\\gcd(0, {b}) = {b_abs}$"], "bezout": {"equation_latex": rf"(0) + ({b})(1) = {b_abs}"}, "is_coprime": (b_abs == 1)}
    if b_abs == 0:
        return {"success": True, "a": a, "b": b, "gcd": a_abs, "lcm": 0, "steps": [f"$\\gcd({a}, 0) = {a_abs}$"], "bezout": {"equation_latex": rf"({a})(1) + (0) = {a_abs}"}, "is_coprime": (a_abs == 1)}
    x, y = max(a_abs, b_abs), min(a_abs, b_abs)
    steps, step_num = [], 1
    while y != 0:
        q, r = x // y, x % y
        eq = rf"{x} = {y} \times {q} + {r}"
        steps.append(f"Step {step_num}: Divide {x} by {y} $\\implies$ Quotient $q = {q}$, Remainder $r = {r}$. Equation: $${eq}$$")
        x, y = y, r
        step_num += 1
    gcd_val = x
    lcm_val = (a_abs * b_abs) // gcd_val
    old_r, r, old_s, s, old_t, t = a, b, 1, 0, 0, 1
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    if old_r < 0:
        old_r, old_s, old_t = -old_r, -old_s, -old_t
    bezout_eq = rf"({a}) \times ({old_s}) + ({b}) \times ({old_t}) = {gcd_val}"
    steps.append(f"Last non-zero remainder is **{gcd_val}**, so $\\gcd({orig_a}, {orig_b}) = {gcd_val}$.")
    return {"success": True, "a": orig_a, "b": orig_b, "gcd": gcd_val, "lcm": lcm_val, "steps": steps, "bezout": {"x": old_s, "y": old_t, "equation_latex": bezout_eq}, "is_coprime": (gcd_val == 1)}

# 3. COMPLEX NUMBERS
def format_complex_latex(real: float, imag: float) -> str:
    r = round(real, 4) if abs(real - round(real)) > 1e-6 else int(round(real))
    i = round(imag, 4) if abs(imag - round(imag)) > 1e-6 else int(round(imag))
    if i == 0:
        return f"{r}"
    if r == 0:
        return "i" if i == 1 else ("-i" if i == -1 else f"{i}i")
    sign = "+" if i > 0 else "-"
    abs_i = abs(i)
    i_str = "i" if abs_i == 1 else f"{abs_i}i"
    return f"{r} {sign} {i_str}"

def analyze_single_complex(a: float, b: float, power_n: int = 2):
    z_latex = format_complex_latex(a, b)
    conj_latex = format_complex_latex(a, -b)
    mod_sq = a**2 + b**2
    mod = math.sqrt(mod_sq)
    theta_rad = math.atan2(b, a)
    theta_deg = math.degrees(theta_rad)
    mod_disp = round(mod, 4) if abs(mod - round(mod)) > 1e-6 else int(round(mod))
    theta_rad_disp = round(theta_rad, 4)
    theta_deg_disp = round(theta_deg, 2)
    polar_latex = rf"{mod_disp} \left( \cos({theta_rad_disp}) + i \sin({theta_rad_disp}) \right)"
    euler_latex = rf"{mod_disp} \, e^{{ {theta_rad_disp} i }}"
    pow_r = mod ** power_n
    pow_theta = power_n * theta_rad
    power_latex = format_complex_latex(pow_r * math.cos(pow_theta), pow_r * math.sin(pow_theta))
    steps = [
        f"**Given complex number:** $z = {z_latex}$",
        f"**Conjugate $\\bar{{z}}$:** ${conj_latex}$",
        f"**Modulus $|z|$:** $\\sqrt{{{a}^2 + ({b})^2}} = \\sqrt{{{round(mod_sq, 4)}}} \\approx {mod_disp}$",
        f"**Argument $\\theta$:** $\\operatorname{{atan2}}({b}, {a}) = {theta_rad_disp} \\text{{ rad}} = {theta_deg_disp}^\\circ$",
        f"**Polar Form:** $z = {polar_latex}$",
        f"**Euler Form:** $z = {euler_latex}$",
        f"**Power $z^{{{power_n}}}$ (De Moivre):** $z^{{{power_n}}} = {power_latex}$"
    ]
    return {"z_latex": z_latex, "conjugate_latex": conj_latex, "modulus": mod_disp, "argument_deg": theta_deg_disp, "polar_latex": polar_latex, "euler_latex": euler_latex, "power_n": power_n, "power_latex": power_latex, "steps": steps}

def operations_two_complex(a: float, b: float, c: float, d: float):
    z1_latex, z2_latex = format_complex_latex(a, b), format_complex_latex(c, d)
    add_latex = format_complex_latex(a + c, b + d)
    sub_latex = format_complex_latex(a - c, b - d)
    mul_latex = format_complex_latex((a * c) - (b * d), (a * d) + (b * c))
    denom = c**2 + d**2
    div_possible = (denom != 0)
    div_steps, div_latex = [], ""
    if div_possible:
        div_r = ((a * c) + (b * d)) / denom
        div_i = ((b * c) - (a * d)) / denom
        div_latex = format_complex_latex(div_r, div_i)
        div_steps = [
            rf"\frac{{{z1_latex}}}{{{z2_latex}}} = \frac{{({z1_latex})({format_complex_latex(c, -d)})}}{{{c}^2 + ({d})^2}} = {div_latex}"
        ]
    else:
        div_latex = "\\text{Undefined}"
    return {
        "z1_latex": z1_latex, "z2_latex": z2_latex,
        "add": {"result": add_latex, "formula": rf"({z1_latex}) + ({z2_latex}) = {add_latex}"},
        "sub": {"result": sub_latex, "formula": rf"({z1_latex}) - ({z2_latex}) = {sub_latex}"},
        "mul": {"result": mul_latex, "formula": rf"({z1_latex}) \times ({z2_latex}) = {mul_latex}"},
        "div": {"possible": div_possible, "result": div_latex, "steps": div_steps}
    }

# 4. PERMUTATIONS
def compute_npr(n: int, r: int):
    if n < 0 or r < 0:
        return {"success": False, "error": "n and r must be non-negative integers."}
    if r > n:
        return {"success": True, "n": n, "r": r, "result": 0, "steps": [f"Cannot choose $r={r}$ items from $n={n}$ items. Value is 0."]}
    result = math.factorial(n) // math.factorial(n - r)
    diff = n - r
    if r == 0:
        terms_str = "1"
    else:
        terms = list(range(n, diff, -1))
        terms_str = " \\times ".join(map(str, terms))
    steps = [
        r"_nP_r = \frac{n!}{(n-r)!}",
        rf"_{{{n}}}P_{{{r}}} = \frac{{{n}!}}{{({n}-{r})!}} = \frac{{{n}!}}{{{diff}!}}",
        rf"\text{{Cancellation: }} {terms_str} = {result}"
    ]
    return {"success": True, "n": n, "r": r, "result": result, "steps": steps}

def compute_circular_permutation(n: int):
    if n <= 0:
        return {"success": False, "error": "n must be a positive integer."}
    ans = math.factorial(n - 1)
    steps = [r"P_{\text{circular}} = (n-1)!", rf"({n}-1)! = {n-1}! = {ans}"]
    return {"success": True, "n": n, "result": ans, "steps": steps}

def compute_repetition_permutation(word: str):
    cleaned = word.strip().upper().replace(" ", "")
    if not cleaned:
        return {"success": False, "error": "Input string is empty."}
    counts = Counter(cleaned)
    n = len(cleaned)
    denom, parts = 1, []
    for c, cnt in counts.items():
        if cnt > 1:
            denom *= math.factorial(cnt)
            parts.append(f"{cnt}!")
    denom_str = " \\times ".join(parts) if parts else "1!"
    ans = math.factorial(n) // denom
    steps = [
        rf"\text{{Total characters }} n = {n}",
        rf"\text{{Frequencies: }} {dict(counts)}",
        rf"\frac{{{n}!}}{{{denom_str}}} = \frac{{{math.factorial(n)}}}{{{denom}}} = {ans}"
    ]
    return {"success": True, "input": cleaned, "result": ans, "steps": steps}

# 5. COMBINATIONS
def compute_ncr(n: int, r: int):
    if n < 0 or r < 0:
        return {"success": False, "error": "n and r must be non-negative integers."}
    if r > n:
        return {"success": True, "n": n, "r": r, "result": 0, "steps": [f"Cannot choose $r={r}$ items from $n={n}$ items. Value is 0."]}
    result = math.comb(n, r)
    diff = n - r
    k = min(r, diff)
    num_str = " \\times ".join(map(str, range(n, n - k, -1))) if k > 0 else "1"
    den_str = " \\times ".join(map(str, range(1, k + 1))) if k > 0 else "1"
    steps = [
        r"\binom{n}{r} = \frac{n!}{r!(n-r)!}",
        rf"\binom{{{n}}}{{{r}}} = \binom{{{n}}}{{{k}}} = \frac{{{num_str}}}{{{den_str}}} = {result}"
    ]
    return {"success": True, "n": n, "r": r, "result": result, "steps": steps, "diff": diff}

def generate_pascals_triangle(n: int):
    n = max(0, min(n, 12))
    return [[math.comb(i, j) for j in range(i + 1)] for i in range(n + 1)]

# 6. LIMIT CALCULATOR
def compute_limit(expr_str: str, var_str: str = "x", point_str: str = "0", direction: str = "+-"):
    try:
        cleaned_expr = expr_str.strip().replace("^", "**").replace("ln(", "log(")
        x = sp.Symbol(var_str.strip() or "x")
        expr = sp.sympify(cleaned_expr, evaluate=True)
        cleaned_point = point_str.strip().lower()
        if cleaned_point in ("oo", "inf", "infinity", "+oo", "+inf"):
            point, point_latex = sp.oo, r"\infty"
        elif cleaned_point in ("-oo", "-inf", "-infinity"):
            point, point_latex = -sp.oo, r"-\infty"
        elif cleaned_point == "pi":
            point, point_latex = sp.pi, r"\pi"
        elif cleaned_point == "e":
            point, point_latex = sp.E, "e"
        else:
            point = sp.sympify(cleaned_point)
            point_latex = sp.latex(point)
        expr_latex = sp.latex(expr)
        steps = [rf"Expression: $$f({x}) = {expr_latex}$$"]
        dir_symbol = ""
        if direction == "+":
            lim_val = sp.limit(expr, x, point, dir="+")
            dir_symbol = "^+"
            steps.append(rf"Right-Hand Limit as ${x} \to {point_latex}^+$: ${sp.latex(lim_val)}$")
        elif direction == "-":
            lim_val = sp.limit(expr, x, point, dir="-")
            dir_symbol = "^-"
            steps.append(rf"Left-Hand Limit as ${x} \to {point_latex}^-$: ${sp.latex(lim_val)}$")
        else:
            rhl = sp.limit(expr, x, point, dir="+")
            lhl = sp.limit(expr, x, point, dir="-")
            steps.append(rf"Left-Hand Limit: $\lim_{{{x} \to {point_latex}^-}} f({x}) = {sp.latex(lhl)}$")
            steps.append(rf"Right-Hand Limit: $\lim_{{{x} \to {point_latex}^+}} f({x}) = {sp.latex(rhl)}$")
            lim_val = lhl if lhl == rhl else sp.nan
            steps.append(rf"Limits match $\implies$ Limit exists: ${sp.latex(lim_val)}$" if lhl == rhl else r"LHL $\neq$ RHL $\implies$ Two-sided limit does NOT exist.")
        ans_latex = sp.latex(lim_val)
        full_problem_latex = rf"\lim_{{{x} \to {point_latex}{dir_symbol}}} \left( {expr_latex} \right) = {ans_latex}"
        return {"success": True, "full_problem_latex": full_problem_latex, "steps": steps, "result": str(lim_val)}
    except Exception as e:
        return {"success": False, "error": f"Error: {str(e)}. Example: sin(x)/x as x -> 0."}


# ==============================================================================
# SLIDE DECK NAVIGATION
# ==============================================================================
SLIDES = [
    {"id": 0, "title": "Welcome & Course Overview", "icon": "🏠", "badge": "MATHSOLVE PRO • DASHBOARD", "desc": "An interactive slide-based mathematics learning suite covering all 6 essential syllabus topics."},
    {"id": 1, "title": "Divisibility Checker", "icon": "🔢", "badge": "SLIDE 1 • NUMBER THEORY", "desc": "Check integer divisibility (b | a), quotient-remainder theorem (a = bq + r), factors, and divisibility rules."},
    {"id": 2, "title": "GCD Calculator", "icon": "🧮", "badge": "SLIDE 2 • EUCLIDEAN ALGORITHM", "desc": "Calculate GCD/HCF, LCM, and Bézout's Identity with full Euclidean algorithm steps."},
    {"id": 3, "title": "Complex Numbers", "icon": "⚡", "badge": "SLIDE 3 • COMPLEX ANALYSIS", "desc": "Analyze complex numbers (modulus, argument, polar/Euler forms, powers) and arithmetic operations."},
    {"id": 4, "title": "Permutation", "icon": "🔄", "badge": "SLIDE 4 • COMBINATORICS", "desc": "Calculate arrangements (nPr) with factorial expansions, circular permutations, and repetition."},
    {"id": 5, "title": "Combination", "icon": "🎯", "badge": "SLIDE 5 • COMBINATORICS", "desc": "Calculate selections (nCr) with step-by-step cancellations, symmetry, and Pascal's Triangle."},
    {"id": 6, "title": "Limit Calculator", "icon": "♾️", "badge": "SLIDE 6 • CALCULUS", "desc": "Analytical limit evaluation using SymPy, supporting one-sided limits and indeterminate forms."}
]

if "slide_idx" not in st.session_state:
    st.session_state.slide_idx = 0

def set_slide(idx: int):
    st.session_state.slide_idx = max(0, min(idx, len(SLIDES) - 1))

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 📑 Slide Deck Navigation")
    st.caption("Click any slide to jump directly:")
    for s in SLIDES:
        active = (s["id"] == st.session_state.slide_idx)
        label = f"{s['icon']} {s['title']}"
        if active:
            st.button(f"👉 {label}", key=f"sb_{s['id']}", use_container_width=True, type="primary")
        else:
            if st.button(label, key=f"sb_{s['id']}", use_container_width=True):
                set_slide(s["id"])
                st.rerun()

    st.markdown("---")
    st.markdown("#### 🚀 Slide Progress")
    st.progress((st.session_state.slide_idx + 1) / len(SLIDES))
    st.caption(f"Slide {st.session_state.slide_idx + 1} of {len(SLIDES)}")

# Top Navigation Bar
curr_slide = SLIDES[st.session_state.slide_idx]
c_prev, c_stat, c_next = st.columns([1.2, 3, 1.2])

with c_prev:
    if st.button("◀ Previous Slide", disabled=(st.session_state.slide_idx == 0), use_container_width=True):
        set_slide(st.session_state.slide_idx - 1)
        st.rerun()

with c_stat:
    st.markdown(
        f"<div style='text-align:center; padding:6px; font-weight:700; color:#334155; font-size:15px;'>"
        f"Slide {st.session_state.slide_idx + 1} of {len(SLIDES)} : {curr_slide['icon']} {curr_slide['title']}"
        f"</div>",
        unsafe_allow_html=True
    )

with c_next:
    if st.button("Next Slide ▶", disabled=(st.session_state.slide_idx == len(SLIDES) - 1), use_container_width=True, type="secondary"):
        set_slide(st.session_state.slide_idx + 1)
        st.rerun()

# Banner
st.markdown(f"""
<div class="slide-banner">
  <div class="slide-badge">{curr_slide['badge']}</div>
  <h1 class="slide-title">{curr_slide['icon']} {curr_slide['title']}</h1>
  <p class="slide-desc">{curr_slide['desc']}</p>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# SLIDE CONTENT
# ==============================================================================

# SLIDE 0: DASHBOARD
if st.session_state.slide_idx == 0:
    st.markdown("### 📌 Syllabus Topics Deck")
    st.markdown("Select any topic below or use the slide navigation buttons to explore each topic step-by-step.")
    cols = st.columns(3)
    for i, s in enumerate(SLIDES[1:]):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="topic-tile">
              <div class="topic-icon">{s['icon']}</div>
              <div class="topic-name">{s['title']}</div>
              <div class="topic-desc">{s['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            if st.button(f"Go to {s['title']} ➔", key=f"dash_{s['id']}", use_container_width=True):
                set_slide(s["id"])
                st.rerun()

# SLIDE 1: DIVISIBILITY CHECKER
elif st.session_state.slide_idx == 1:
    tab1, tab2 = st.tabs(["🔍 Divisibility & Algorithm", "📋 Factors & Divisibility Rules"])
    with tab1:
        st.markdown('<div class="math-card">', unsafe_allow_html=True)
        st.subheader("Division Algorithm ($a = bq + r$)")
        c1, c2 = st.columns(2)
        with c1:
            a_val = st.number_input("Dividend (a)", value=48, step=1, key="div_a")
        with c2:
            b_val = st.number_input("Divisor (b)", value=6, step=1, key="div_b")
        if st.button("✨ Check Divisibility", type="primary", key="btn_check_div"):
            res = check_divisibility(a_val, b_val)
            if not res["success"]:
                st.error(res["error"])
            else:
                st.markdown("#### 📝 Step-by-Step Derivation")
                for s in res["steps"]:
                    st.markdown(f'<div class="step-item">{s}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="final-answer-box">🎯 Final Result: {res["conclusion"]}</div>', unsafe_allow_html=True)
                st.write("")
                st.latex(rf"\text{{Division Form: }} {res['division_latex']}")
        st.markdown('</div>', unsafe_allow_html=True)
    with tab2:
        st.markdown('<div class="math-card">', unsafe_allow_html=True)
        st.subheader("Factors & Standard Divisibility Rules")
        target_n = st.number_input("Enter integer (N)", value=36, step=1, key="div_n_rules")
        if st.button("🔍 Find Factors & Test Rules", type="primary", key="btn_rules"):
            fac_info = get_factors(target_n)
            rules_info = test_divisibility_rules(target_n)
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                st.markdown("#### 📦 Factors")
                st.write(f"**Total Positive Factors:** {fac_info['factor_count']}")
                st.code(str(fac_info['factors']), language="text")
                if fac_info['prime_factors']:
                    st.markdown("**Prime Factorization:**")
                    st.latex(rf"{abs(target_n)} = {fac_info['prime_factorization_latex']}")
            with c_f2:
                st.markdown("#### ⚖️ Divisibility Rules")
                for r in rules_info:
                    st.markdown(f"**{'✅' if r['passed'] else '❌'} Divisible by {r['divisor']}?** {r['explanation']}")
        st.markdown('</div>', unsafe_allow_html=True)

# SLIDE 2: GCD CALCULATOR
elif st.session_state.slide_idx == 2:
    st.markdown('<div class="math-card">', unsafe_allow_html=True)
    st.subheader("Euclidean Algorithm for GCD / HCF & LCM")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        gcd_a = st.number_input("Integer A", value=48, step=1, key="gcd_a")
    with col_g2:
        gcd_b = st.number_input("Integer B", value=18, step=1, key="gcd_b")
    col_p = st.columns(4)
    with col_p[0]:
        if st.button("Example: 48 & 18", use_container_width=True):
            gcd_a, gcd_b = 48, 18
    with col_p[1]:
        if st.button("Example: 252 & 105", use_container_width=True):
            gcd_a, gcd_b = 252, 105
    with col_p[2]:
        if st.button("Example: 1071 & 462", use_container_width=True):
            gcd_a, gcd_b = 1071, 462
    with col_p[3]:
        if st.button("Example: 37 & 13", use_container_width=True):
            gcd_a, gcd_b = 37, 13
    st.write("")
    if st.button("🧮 Compute GCD & Steps", type="primary", key="btn_gcd"):
        res = compute_gcd_steps(gcd_a, gcd_b)
        if not res["success"]:
            st.error(res["error"])
        else:
            st.markdown("#### 📝 Euclidean Algorithm Steps")
            for s in res["steps"]:
                st.markdown(f'<div class="step-item">{s}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="final-answer-box">🎯 GCD({res["a"]}, {res["b"]}) = {res["gcd"]} &nbsp;|&nbsp; LCM = {res["lcm"]}</div>', unsafe_allow_html=True)
            st.write("")
            st.markdown("#### 🔗 Bézout's Identity")
            st.latex(res["bezout"]["equation_latex"])
            st.info(f"**Coprime Test:** {'✅ Yes, Coprime!' if res['is_coprime'] else '❌ Not Coprime'}")
    st.markdown('</div>', unsafe_allow_html=True)

# SLIDE 3: COMPLEX NUMBERS
elif st.session_state.slide_idx == 3:
    tab_c1, tab_c2 = st.tabs(["✨ Single Complex Analysis ($z = a + bi$)", "➕ Binary Operations ($z_1$ and $z_2$)"])
    with tab_c1:
        st.markdown('<div class="math-card">', unsafe_allow_html=True)
        st.subheader("Properties, Polar & Euler Form, Powers")
        c_a1, c_b1, c_pow = st.columns([1, 1, 1])
        with c_a1:
            real_part = st.number_input("Real Part (a)", value=3.0, step=0.5, key="comp_a")
        with c_b1:
            imag_part = st.number_input("Imaginary Part (b)", value=4.0, step=0.5, key="comp_b")
        with c_pow:
            power_val = st.number_input("Power exponent (n)", value=2, step=1, key="comp_n")
        if st.button("⚡ Analyze Complex Number", type="primary", key="btn_comp_single"):
            res = analyze_single_complex(real_part, imag_part, power_val)
            st.markdown("#### 📝 Step-by-Step Breakdown")
            for s in res["steps"]:
                st.markdown(f'<div class="step-item">{s}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="final-answer-box">🎯 Modulus: {res["modulus"]} &nbsp;|&nbsp; Argument: {res["argument_deg"]}° &nbsp;|&nbsp; Conjugate: {res["conjugate_latex"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab_c2:
        st.markdown('<div class="math-card">', unsafe_allow_html=True)
        st.subheader("Arithmetic ($z_1 \\pm z_2, z_1 \\times z_2, z_1 / z_2$)")
        col_z1, col_z2 = st.columns(2)
        with col_z1:
            st.markdown("**First Complex Number ($z_1 = a + bi$)**")
            z1_r = st.number_input("z1 Real (a)", value=1.0, step=0.5, key="z1_r")
            z1_i = st.number_input("z1 Imaginary (b)", value=2.0, step=0.5, key="z1_i")
        with col_z2:
            st.markdown("**Second Complex Number ($z_2 = c + di$)**")
            z2_r = st.number_input("z2 Real (c)", value=3.0, step=0.5, key="z2_r")
            z2_i = st.number_input("z2 Imaginary (d)", value=4.0, step=0.5, key="z2_i")
        if st.button("➕ Compute All Operations", type="primary", key="btn_comp_ops"):
            ops = operations_two_complex(z1_r, z1_i, z2_r, z2_i)
            c_op1, c_op2 = st.columns(2)
            with c_op1:
                st.markdown("##### ➕ Addition & Subtraction")
                st.latex(ops["add"]["formula"])
                st.latex(ops["sub"]["formula"])
            with c_op2:
                st.markdown("##### ✖️ Multiplication")
                st.latex(ops["mul"]["formula"])
            st.markdown("##### ➗ Division")
            if ops["div"]["possible"]:
                for step in ops["div"]["steps"]:
                    st.latex(step)
            else:
                st.error("Division by zero is undefined.")
            st.markdown(f'<div class="final-answer-box">🎯 (+): {ops["add"]["result"]} | (-): {ops["sub"]["result"]} | (×): {ops["mul"]["result"]} | (÷): {ops["div"]["result"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# SLIDE 4: PERMUTATION
elif st.session_state.slide_idx == 4:
    tab_p1, tab_p2, tab_p3 = st.tabs(["🔢 Standard $nPr$", "🔄 Circular $(n-1)!$", "🔤 Repetition (Word Problems)"])
    with tab_p1:
        st.markdown('<div class="math-card">', unsafe_allow_html=True)
        st.subheader("Permutation Formula: $_nP_r = \\frac{n!}{(n - r)!}$")
        cp_n, cp_r = st.columns(2)
        with cp_n:
            pn_val = st.number_input("Total Items (n)", value=5, min_value=0, step=1, key="perm_n")
        with cp_r:
            pr_val = st.number_input("Items to Arrange (r)", value=2, min_value=0, step=1, key="perm_r")
        if st.button("🔄 Calculate Permutations", type="primary", key="btn_perm"):
            res = compute_npr(pn_val, pr_val)
            if not res["success"]:
                st.error(res["error"])
            else:
                for s in res["steps"]:
                    st.latex(s)
                st.markdown(f'<div class="final-answer-box">🎯 Final Answer: _{{{res["n"]}}}P_{{{res["r"]}}} = {res["result"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab_p2:
        st.markdown('<div class="math-card">', unsafe_allow_html=True)
        st.subheader("Circular Permutations: $P_{\\text{circular}} = (n - 1)!$")
        circ_n = st.number_input("Number of items in circle (n)", value=5, min_value=1, step=1, key="circ_n")
        if st.button("🔄 Compute Circular Permutations", type="primary", key="btn_circ"):
            res = compute_circular_permutation(circ_n)
            if not res["success"]:
                st.error(res["error"])
            else:
                for s in res["steps"]:
                    st.latex(s)
                st.markdown(f'<div class="final-answer-box">🎯 Circular Arrangements: ({circ_n} - 1)! = {res["result"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab_p3:
        st.markdown('<div class="math-card">', unsafe_allow_html=True)
        st.subheader("Permutations with Repetition: $\\frac{n!}{n_1! n_2! \\dots}$")
        word_input = st.text_input("Enter a word or letter sequence", value="MISSISSIPPI", key="rep_word")
        if st.button("🔤 Calculate Word Permutations", type="primary", key="btn_rep"):
            res = compute_repetition_permutation(word_input)
            if not res["success"]:
                st.error(res["error"])
            else:
                for s in res["steps"]:
                    st.latex(s)
                st.markdown(f'<div class="final-answer-box">🎯 Permutations of \'{res["input"]}\': {res["result"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# SLIDE 5: COMBINATION
elif st.session_state.slide_idx == 5:
    tab_cb1, tab_cb2 = st.tabs(["🎯 Standard Selection $\\binom{n}{r}$", "📐 Pascal's Triangle"])
    with tab_cb1:
        st.markdown('<div class="math-card">', unsafe_allow_html=True)
        st.subheader("Combination Formula: $\\binom{n}{r} = \\frac{n!}{r!(n - r)!}$")
        cc_n, cc_r = st.columns(2)
        with cc_n:
            cn_val = st.number_input("Total Items (n)", value=5, min_value=0, step=1, key="comb_n")
        with cc_r:
            cr_val = st.number_input("Items to Choose (r)", value=2, min_value=0, step=1, key="comb_r")
        if st.button("🎯 Calculate Combinations", type="primary", key="btn_comb"):
            res = compute_ncr(cn_val, cr_val)
            if not res["success"]:
                st.error(res["error"])
            else:
                for s in res["steps"]:
                    st.latex(s)
                st.markdown(f'<div class="final-answer-box">🎯 Final Answer: \\binom{{{res["n"]}}}{{{res["r"]}}} = {res["result"]}</div>', unsafe_allow_html=True)
                st.info(f"**Symmetry Property:** $\\binom{{{res['n']}}}{{{res['r']}}} = \\binom{{{res['n']}}}{{{res['diff']}}}$ holds true.")
        st.markdown('</div>', unsafe_allow_html=True)
    with tab_cb2:
        st.markdown('<div class="math-card">', unsafe_allow_html=True)
        st.subheader("Pascal's Triangle Generator")
        pt_n = st.slider("Number of Rows (n)", min_value=0, max_value=10, value=5, key="pt_slider")
        triangle = generate_pascals_triangle(pt_n)
        for row_idx, row in enumerate(triangle):
            row_str = " & ".join(map(str, row))
            st.latex(rf"\text{{Row {row_idx}: }}\quad [ {row_str} ] \implies \sum = 2^{{{row_idx}}} = {2**row_idx}")
        st.markdown('</div>', unsafe_allow_html=True)

# SLIDE 6: LIMIT CALCULATOR
elif st.session_state.slide_idx == 6:
    st.markdown('<div class="math-card">', unsafe_allow_html=True)
    st.subheader("Symbolic Limit Calculator: $\\lim_{x \\to a} f(x)$")
    col_l1, col_l2, col_l3 = st.columns([2.5, 1, 1.5])
    with col_l1:
        expr_input = st.text_input("Expression f(x)", value="sin(x)/x", key="lim_expr")
    with col_l2:
        point_input = st.text_input("Target point (a)", value="0", key="lim_point")
    with col_l3:
        dir_choice = st.selectbox("Direction", ["Two-sided (+-)", "From Right (x -> a+)", "From Left (x -> a-)"], key="lim_dir")
    dir_map = {"Two-sided (+-)": "+-", "From Right (x -> a+)": "+", "From Left (x -> a-)": "-"}
    lim_presets = st.columns(4)
    with lim_presets[0]:
        if st.button("Preset: sin(x)/x as x→0", use_container_width=True):
            expr_input, point_input = "sin(x)/x", "0"
    with lim_presets[1]:
        if st.button("Preset: (x^2-4)/(x-2) as x→2", use_container_width=True):
            expr_input, point_input = "(x^2 - 4)/(x - 2)", "2"
    with lim_presets[2]:
        if st.button("Preset: (1+1/x)^x as x→oo", use_container_width=True):
            expr_input, point_input = "(1 + 1/x)**x", "oo"
    with lim_presets[3]:
        if st.button("Preset: (1-cos(x))/x^2 as x→0", use_container_width=True):
            expr_input, point_input = "(1 - cos(x))/(x**2)", "0"
    st.write("")
    if st.button("♾️ Evaluate Limit", type="primary", key="btn_lim"):
        res = compute_limit(expr_input, "x", point_input, dir_map[dir_choice])
        if not res["success"]:
            st.error(res["error"])
        else:
            st.markdown("#### 📝 Step-by-Step Analysis")
            for s in res["steps"]:
                st.markdown(f'<div class="step-item">{s}</div>', unsafe_allow_html=True)
            st.markdown('<div class="final-answer-box">🎯 Limit Evaluation:</div>', unsafe_allow_html=True)
            st.latex(res["full_problem_latex"])
            st.code(f"Result: {res['result']}", language="text")
    st.markdown('</div>', unsafe_allow_html=True)

# Bottom Navigation Bar
st.write("")
st.markdown("---")
b_col1, b_col2, b_col3 = st.columns([1.5, 3, 1.5])
with b_col1:
    if st.button("⬅️ Previous Slide", key="bottom_prev", disabled=(st.session_state.slide_idx == 0), use_container_width=True):
        set_slide(st.session_state.slide_idx - 1)
        st.rerun()
with b_col2:
    st.markdown(f"<div style='text-align:center; color:#64748b; font-size:14px; font-weight:600; padding-top:8px;'>Slide {st.session_state.slide_idx + 1} of {len(SLIDES)} • Use Previous / Next to browse</div>", unsafe_allow_html=True)
with b_col3:
    if st.button("Next Slide ➡️", key="bottom_next", disabled=(st.session_state.slide_idx == len(SLIDES) - 1), use_container_width=True, type="primary"):
        set_slide(st.session_state.slide_idx + 1)
        st.rerun()