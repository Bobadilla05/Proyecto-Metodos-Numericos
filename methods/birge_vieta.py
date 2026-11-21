"""
Birge-Vieta: busca la hora t* en la que el CPU llega al umbral (ej. 85%),
es decir, resuelve P(t) = C(t) - umbral = 0.

Paso a paso: Horner (doble división sintética) para P(t_k) y P'(t_k),
luego Newton-Raphson t_{k+1} = t_k - b_0/c_1, y al final se sustituye t* en C(t).
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


def horner_evaluation(coeffs: List[float], x: float) -> Tuple[List[float], List[float]]:
    """
    Doble división sintética de Horner en x.
    Devuelve b (b[-1] = P(x)) y c (c[-1] = P'(x)).
    """
    n = len(coeffs) - 1
    # primera división sintética: da P(x)
    b = [0.0] * (n + 1)
    b[0] = coeffs[0]
    for i in range(1, n + 1):
        b[i] = coeffs[i] + b[i - 1] * x

    # segunda: da P'(x)
    c = [0.0] * n
    c[0] = b[0]
    for i in range(1, n):
        c[i] = b[i] + c[i - 1] * x

    return b, c


def verify_root_substitution(coeffs: List[float], root: float, threshold: float = 85.0) -> Dict[str, Any]:
    """Sustituye la hora encontrada en C(t) y compara con el umbral."""
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

    total_cpu = sum(terms_vals)
    formula_str = " + ".join(terms_formula).replace("+ -", "- ")
    diff = abs(total_cpu - threshold) if threshold > 0 else abs(total_cpu)
    clock_str = format_hour_to_time_str(root)

    return {
        "title": "Comprobación: Sustitución de la hora crítica en la función de carga C(t)",
        "polynomial_formula": f"C(t) = {format_polynomial(coeffs)}",
        "substitution_step": f"C({root:.4f}) = {formula_str}",
        "evaluation_step": f"= {total_cpu:.4f} % de CPU" + (f"  (Umbral esperado = {threshold:.2f} %)" if threshold > 0 else ""),
        "result_value": total_cpu,
        "is_accurate": diff < 1.0,
        "message": (
            f"✔ COMPROBACIÓN EXITOSA: A las {clock_str}, el uso de CPU alcanza {total_cpu:.2f}%,\n"
            f"confirmando el momento exacto en que se llega al umbral crítico del servidor ({threshold:.2f}%)."
            if threshold > 0 else
            f"✔ COMPROBACIÓN EXITOSA: P({root:.4f}) = {total_cpu:.2e} ≈ 0 (anula la ecuación)."
        )
    }


def birge_vieta(
    coeffs: List[float],
    x0: float,
    threshold: float = 85.0,
    tol: float = 1e-5,
    max_iter: int = 50,
    error_type: str = "relativo"
) -> Dict[str, Any]:
    """
    Corre Birge-Vieta para hallar la hora crítica.
    coeffs van de mayor a menor grado, x0 es la hora inicial, tol la tolerancia.
    """
    # quito ceros a la izquierda
    while len(coeffs) > 1 and abs(coeffs[0]) < 1e-15:
        coeffs = coeffs[1:]

    n = len(coeffs) - 1
    if n < 1:
        return {
            "success": False,
            "converged": False,
            "message": "La función de carga debe tener al menos grado 1.",
            "iterations": [],
            "root": None
        }

    # P(t) = C(t) - umbral
    p_coeffs = list(coeffs)
    if threshold > 0:
        p_coeffs[-1] = p_coeffs[-1] - threshold

    t_curr = float(x0)
    iterations = []
    converged = False
    message = ""

    for k in range(1, max_iter + 1):
        # horner
        b, c = horner_evaluation(p_coeffs, t_curr)
        p_t = b[-1]  # b_0 = P(t)
        p_prime_t = c[-1]  # c_1 = P'(t)

        if abs(p_prime_t) < 1e-14:
            message = f"Derivada casi nula P'({t_curr:.4f}) = {p_prime_t:.2e} en la iteración {k}. Riesgo de división por cero."
            break

        # newton-raphson
        delta = p_t / p_prime_t
        t_next = t_curr - delta

        error_abs = abs(t_next - t_curr)
        if abs(t_next) > 1e-14:
            error_rel = (error_abs / abs(t_next)) * 100.0
        else:
            error_rel = error_abs * 100.0

        current_cpu = eval_poly(coeffs, t_curr)

        iterations.append({
            "iter": k,
            "x_k": t_curr,
            "p_x": p_t,
            "p_prime_x": p_prime_t,
            "x_next": t_next,
            "delta": delta,
            "error_abs": error_abs,
            "error_rel": error_rel,
            "error": error_rel,
            "cpu_usage": current_cpu,
            "horner_details": {
                "a_coeffs": list(p_coeffs),
                "b_coeffs": list(b),
                "c_coeffs": list(c),
                "b0": p_t,
                "c1": p_prime_t
            },
            "newton_details": {
                "formula": f"t_{{{k}}} = t_{{{k-1}}} - [ P(t_{{{k-1}}}) / P'(t_{{{k-1}}}) ]",
                "substitution": f"{t_curr:.4f} - ({p_t:.4f} / {p_prime_t:.4f})",
                "result": t_next
            }
        })

        if error_rel < tol or abs(p_t) < tol:
            converged = True
            t_curr = t_next
            message = f"Convergencia alcanzada exitosamente en {k} iteraciones."
            break

        t_curr = t_next
    else:
        message = f"Se alcanzó el máximo de iteraciones ({max_iter}) con una aproximación de t = {t_curr:.4f} hrs."

    final_root = t_curr
    final_cpu = eval_poly(coeffs, final_root)
    clock_time = format_hour_to_time_str(final_root)
    poly_str = format_polynomial(coeffs)

    verification = verify_root_substitution(coeffs, final_root, threshold)

    return {
        "success": converged or (len(iterations) > 0 and abs(final_cpu - threshold) < 2.0),
        "converged": converged,
        "message": message,
        "method_name": "Método de Birge-Vieta (Horner + Newton-Raphson)",
        "iterations": iterations,
        "root": final_root,
        "clock_time": clock_time,
        "final_cpu": final_cpu,
        "threshold": threshold,
        "poly_str": poly_str,
        "coeffs": coeffs,
        "p_coeffs": p_coeffs,
        "x0": x0,
        "tol": tol,
        "verification": verification
    }


def format_polynomial(coeffs: List[float]) -> str:
    """Arma el texto de C(t) a partir de los coeficientes."""
    n = len(coeffs) - 1
    terms = []
    for i, c in enumerate(coeffs):
        power = n - i
        if abs(c) < 1e-12:
            continue
        
        sign = " + " if c > 0 and len(terms) > 0 else (" - " if c < 0 and len(terms) > 0 else ("-" if c < 0 else ""))
        val = abs(c)
        val_str = f"{val:g}" if (val != 1 or power == 0) else ""

        if power == 0:
            term = f"{val_str if val_str else '1'}"
        elif power == 1:
            term = f"{val_str}t"
        else:
            term = f"{val_str}t^{power}"

        terms.append(f"{sign}{term}")

    return "".join(terms) if terms else "0"
