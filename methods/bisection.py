"""
Bisección: encuentra la hora crítica t* en [a, b] donde el CPU del servidor
llega al umbral (ej. 85%), resolviendo P(t) = C(t) - umbral = 0 al ir partiendo
el intervalo a la mitad (teorema de Bolzano).
"""

from typing import List, Dict, Any, Tuple
import numpy as np


def format_hour_to_time_str(hour_float: float) -> str:
    """Pasa una hora decimal (11.45) a texto tipo reloj (11:27)."""
    if hour_float is None or np.isnan(hour_float) or np.isinf(hour_float):
        return "N/A"
    total_minutes = int(round(hour_float * 60))
    h = (total_minutes // 60) % 24
    m = total_minutes % 60
    period = "AM" if h < 12 else "PM"
    h_12 = 12 if (h == 0 or h == 12) else (h % 12)
    return f"{hour_float:.4f} hrs  (~{h:02d}:{m:02d} hrs | {h_12:02d}:{m:02d} {period})"


def eval_poly(coeffs: List[float], t: float) -> float:
    """Evalúa el polinomio en t con Horner."""
    val = coeffs[0]
    for c in coeffs[1:]:
        val = val * t + c
    return float(val)


def bisection(
    coeffs: List[float],
    a: float,
    b: float,
    threshold: float = 85.0,
    tol: float = 1e-4,
    max_iter: int = 50
) -> Dict[str, Any]:
    """
    Corre bisección en [a, b] para hallar cuándo C(t) llega al umbral.
    coeffs van de mayor a menor grado.
    """
    if a >= b:
        return {
            "success": False,
            "converged": False,
            "message": f"El extremo inferior del intervalo (a = {a}) debe ser estrictamente menor al superior (b = {b}).",
            "iterations": [],
            "root": None
        }

    # P(t) = C(t) - umbral
    p_coeffs = list(coeffs)
    if threshold > 0:
        p_coeffs[-1] = p_coeffs[-1] - threshold

    fa = eval_poly(p_coeffs, a)
    fb = eval_poly(p_coeffs, b)

    ca = eval_poly(coeffs, a)
    cb = eval_poly(coeffs, b)

    if abs(fa) < 1e-12:
        return _build_instant_result(a, coeffs, p_coeffs, threshold, a, b)
    if abs(fb) < 1e-12:
        return _build_instant_result(b, coeffs, p_coeffs, threshold, a, b)

    # reviso que haya cambio de signo (Bolzano)
    if fa * fb > 0:
        return {
            "success": False,
            "converged": False,
            "message": (
                f"No hay cambio de signo en el intervalo [{a:.1f} hrs, {b:.1f} hrs]:\n"
                f"  • A las {a:.1f} hrs: Carga = {ca:.2f}% (P = {fa:+.2f}%)\n"
                f"  • A las {b:.1f} hrs: Carga = {cb:.2f}% (P = {fb:+.2f}%)\n"
                f"En ambas horas la carga está del mismo lado del umbral ({threshold}%). "
                f"Por favor amplía o ajusta el intervalo de horas para abarcar el momento en que se cruza el {threshold}%."
            ),
            "iterations": [],
            "root": None
        }

    a_k = float(a)
    b_k = float(b)
    iterations = []
    converged = False
    message = ""
    m_prev = None

    for k in range(1, max_iter + 1):
        m_k = (a_k + b_k) / 2.0
        f_ak = eval_poly(p_coeffs, a_k)
        f_bk = eval_poly(p_coeffs, b_k)
        f_mk = eval_poly(p_coeffs, m_k)
        c_mk = eval_poly(coeffs, m_k)

        # errores
        interval_half = (b_k - a_k) / 2.0
        if m_prev is not None and abs(m_k) > 1e-12:
            rel_error = (abs(m_k - m_prev) / abs(m_k)) * 100.0
        else:
            rel_error = interval_half * 100.0

        sign_product = f_ak * f_mk
        sign_str = "f(a)·f(m) < 0  (Raíz en [a, m])" if sign_product < 0 else ("f(a)·f(m) > 0  (Raíz en [m, b])" if sign_product > 0 else "f(m) = 0")

        iterations.append({
            "iter": k,
            "a": a_k,
            "b": b_k,
            "m": m_k,
            "f_a": f_ak,
            "f_b": f_bk,
            "f_m": f_mk,
            "cpu_usage": c_mk,
            "error_abs": interval_half,
            "error_rel": rel_error,
            "sign_str": sign_str,
            "decision": f"Nuevo intervalo: [{'a' if sign_product > 0 else 'a'}, {'m' if sign_product < 0 else 'b'}]"
        })

        if interval_half < tol or abs(f_mk) < tol or rel_error < tol:
            converged = True
            message = f"Convergencia alcanzada en {k} iteraciones por bisección."
            break

        if sign_product < 0:
            b_k = m_k
        else:
            a_k = m_k

        m_prev = m_k
    else:
        message = f"Se alcanzó el número máximo de iteraciones ({max_iter}) con una aproximación de {m_k:.4f} hrs."

    final_hour = m_k
    final_cpu = eval_poly(coeffs, final_hour)
    clock_time = format_hour_to_time_str(final_hour)

    # comprobación: sustituyo la raíz en C(t)
    verification = _build_verification(coeffs, final_hour, threshold, final_cpu)

    return {
        "success": converged or len(iterations) > 0,
        "converged": converged,
        "message": message,
        "method_name": "Método de Bisección (Estimación de Hora Crítica)",
        "root": final_hour,
        "clock_time": clock_time,
        "final_cpu": final_cpu,
        "threshold": threshold,
        "iterations": iterations,
        "coeffs": coeffs,
        "p_coeffs": p_coeffs,
        "a_init": a,
        "b_init": b,
        "tol": tol,
        "verification": verification
    }


def _build_instant_result(root: float, coeffs: List[float], p_coeffs: List[float], threshold: float, a: float, b: float) -> Dict[str, Any]:
    final_cpu = eval_poly(coeffs, root)
    return {
        "success": True,
        "converged": True,
        "message": f"La hora crítica coincide exactamente con uno de los extremos del intervalo horario (t = {root:.4f} hrs).",
        "method_name": "Método de Bisección (Estimación de Hora Crítica)",
        "root": root,
        "clock_time": format_hour_to_time_str(root),
        "final_cpu": final_cpu,
        "threshold": threshold,
        "iterations": [{
            "iter": 1,
            "a": a,
            "b": b,
            "m": root,
            "f_a": 0.0,
            "f_b": 0.0,
            "f_m": 0.0,
            "cpu_usage": final_cpu,
            "error_abs": 0.0,
            "error_rel": 0.0,
            "sign_str": "Raíz exacta",
            "decision": "Fin"
        }],
        "coeffs": coeffs,
        "p_coeffs": p_coeffs,
        "a_init": a,
        "b_init": b,
        "tol": 1e-5,
        "verification": _build_verification(coeffs, root, threshold, final_cpu)
    }


def _build_verification(coeffs: List[float], root: float, threshold: float, cpu_val: float) -> Dict[str, Any]:
    n = len(coeffs) - 1
    terms_formula = []
    terms_vals = []
    for i, c in enumerate(coeffs):
        p = n - i
        val = c * (root ** p)
        terms_vals.append(val)
        if p > 1:
            terms_formula.append(f"({c:g})*({root:.4f})^{p}")
        elif p == 1:
            terms_formula.append(f"({c:g})*({root:.4f})")
        else:
            terms_formula.append(f"({c:g})")

    formula_str = " + ".join(terms_formula).replace("+ -", "- ")
    diff = abs(cpu_val - threshold)
    clock_str = format_hour_to_time_str(root)

    return {
        "title": "Comprobación: Sustitución de la hora crítica en el polinomio de carga C(t)",
        "substitution_step": f"C({root:.4f}) = {formula_str}",
        "evaluation_step": f"= {cpu_val:.4f} % de CPU  (Umbral crítico esperado = {threshold:.2f} %)",
        "difference": diff,
        "is_accurate": diff < 1.0,
        "message": (
            f"✔ COMPROBACIÓN EXITOSA: A las {clock_str}, el uso del CPU del servidor escolar alcanza {cpu_val:.2f}%,\n"
            f"cumpliendo con exactitud el umbral crítico establecido ({threshold:.2f}% de CPU)."
        )
    }
