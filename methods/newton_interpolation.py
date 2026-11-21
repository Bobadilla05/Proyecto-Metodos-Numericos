"""
Interpolación de Newton con diferencias divididas.
Arma la tabla, el polinomio en forma de Newton y en forma normal, evalúa en un
punto y comprueba con los puntos dados.
"""

from typing import List, Dict, Any, Tuple
import numpy as np


def verify_interpolation_substitution(
    x_points: List[float],
    y_points: List[float],
    poly_canonical: np.poly1d,
    x_eval: float = None,
    y_eval: float = None
) -> Dict[str, Any]:
    """Sustituye cada x_i en P(x) y revisa que dé y_i."""
    point_details = []
    max_diff = 0.0

    for i in range(len(x_points)):
        xi = x_points[i]
        yi_expected = y_points[i]
        yi_calc = float(poly_canonical(xi))
        diff = abs(yi_calc - yi_expected)
        if diff > max_diff:
            max_diff = diff

        point_details.append({
            "index": i + 1,
            "x": xi,
            "y_expected": yi_expected,
            "y_calc": yi_calc,
            "diff": diff,
            "display_str": f"Punto {i+1} (X = {xi:g}): P({xi:g}) = {yi_calc:.6f}  (Valor esperado Y = {yi_expected:g})  ✔ Exacto"
        })

    eval_detail = None
    if x_eval is not None and y_eval is not None:
        eval_detail = {
            "x_eval": x_eval,
            "y_eval": y_eval,
            "display_str": f"Valor estimado para X = {x_eval:g}:  P({x_eval:g}) = {y_eval:.6f}"
        }

    is_accurate = max_diff < 1e-3

    return {
        "title": "Comprobación: Sustitución de los puntos en el polinomio P(x)",
        "points": point_details,
        "eval_detail": eval_detail,
        "max_difference": max_diff,
        "is_accurate": is_accurate,
        "message": (
            "✔ COMPROBACIÓN EXITOSA: El polinomio interpolante pasa exactamente por cada uno de los puntos conocidos dados."
            if is_accurate else
            "Atención: Se encontraron desviaciones numéricas en algunos puntos."
        )
    }


def newton_divided_differences(
    x_points: List[float],
    y_points: List[float],
    x_eval: float = None
) -> Dict[str, Any]:
    """Interpolación de Newton por diferencias divididas."""
    n = len(x_points)
    if n < 2:
        return {
            "success": False,
            "message": "Se requieren al menos 2 puntos para interpolar.",
            "table": [],
            "coefficients": []
        }

    if len(y_points) != n:
        return {
            "success": False,
            "message": f"La cantidad de valores de X ({n}) y Y ({len(y_points)}) debe coincidir.",
            "table": [],
            "coefficients": []
        }

    # x repetidas no sirven
    for i in range(n):
        for j in range(i + 1, n):
            if abs(x_points[i] - x_points[j]) < 1e-12:
                return {
                    "success": False,
                    "message": f"Los valores de X deben ser distintos. x[{i}] y x[{j}] son prácticamente iguales ({x_points[i]}).",
                    "table": [],
                    "coefficients": []
                }

    # tabla de diferencias divididas
    table = np.zeros((n, n), dtype=float)
    for i in range(n):
        table[i, 0] = y_points[i]

    diff_steps = []
    for j in range(1, n):
        for i in range(n - j):
            denom = x_points[i + j] - x_points[i]
            numer = table[i + 1, j - 1] - table[i, j - 1]
            val = numer / denom
            table[i, j] = val
            diff_steps.append({
                "order": j,
                "i": i,
                "calc_str": f"Diferencia de orden {j} entre x_{i} y x_{i+j}: ({table[i+1, j-1]:.4f} - {table[i, j-1]:.4f}) / ({x_points[i+j]:.4f} - {x_points[i]:.4f}) = {val:.6f}"
            })

    # coeficientes b_0 ... b_{n-1}
    coeffs_newton = [float(table[0, j]) for j in range(n)]

    # forma de Newton
    newton_terms = []
    for j in range(n):
        c = coeffs_newton[j]
        if abs(c) < 1e-12 and j > 0:
            continue
        
        c_str = f"{c:+.6g}"
        factors = "".join([f"(x - {x_points[k]:g})" if x_points[k] >= 0 else f"(x + {abs(x_points[k]):g})" for k in range(j)])
        if j == 0:
            newton_terms.append(f"{c:g}")
        else:
            newton_terms.append(f"{c_str}{factors}")

    newton_str = " ".join(newton_terms) if newton_terms else "0"
    if newton_str.startswith("+"):
        newton_str = newton_str[1:].strip()

    # lo expando a forma normal
    poly_canonical = np.poly1d([0.0])
    for j in range(n):
        term_poly = np.poly1d([coeffs_newton[j]])
        for k in range(j):
            term_poly = term_poly * np.poly1d([1.0, -x_points[k]])
        poly_canonical = poly_canonical + term_poly

    canonical_coeffs = poly_canonical.coefficients.tolist()
    canonical_str = format_canonical_polynomial(canonical_coeffs)

    # evalúo si dieron x
    y_eval = None
    eval_steps = []
    if x_eval is not None:
        p = coeffs_newton[-1]
        eval_steps.append(f"Iniciando cálculo con el coeficiente superior: b_{n-1} = {p:.6f}")
        for i in range(n - 2, -1, -1):
            term_factor = (x_eval - x_points[i])
            p_prev = p
            p = p * term_factor + coeffs_newton[i]
            eval_steps.append(f"Multiplicando por (x* - x_{i}) y sumando b_{i}: ({p_prev:.6f}) * ({x_eval} - {x_points[i]}) + {coeffs_newton[i]:.6f} = {p:.6f}")
        y_eval = float(p)

    # tabla para mostrar
    table_formatted = []
    for i in range(n):
        row_dict = {
            "i": i,
            "x": x_points[i],
            "y": y_points[i],
            "diffs": [table[i, j] if i <= n - 1 - j else None for j in range(1, n)]
        }
        table_formatted.append(row_dict)

    # compruebo con los puntos originales
    verification = verify_interpolation_substitution(x_points, y_points, poly_canonical, x_eval, y_eval)

    return {
        "success": True,
        "message": f"Polinomio de grado {n-1} obtenido exitosamente a partir de {n} puntos.",
        "method_name": "Polinomio de Interpolación de Newton",
        "degree": n - 1,
        "coefficients_newton": coeffs_newton,
        "newton_formula": f"P(x) = {newton_str}",
        "canonical_coeffs": canonical_coeffs,
        "canonical_formula": f"P(x) = {canonical_str}",
        "table_matrix": table.tolist(),
        "table_formatted": table_formatted,
        "diff_steps": diff_steps,
        "x_points": x_points,
        "y_points": y_points,
        "x_eval": x_eval,
        "y_eval": y_eval,
        "eval_steps": eval_steps,
        "verification": verification
    }


def format_canonical_polynomial(coeffs: List[float]) -> str:
    """Texto de P(x) a partir de los coeficientes."""
    n = len(coeffs) - 1
    terms = []
    for i, c in enumerate(coeffs):
        power = n - i
        if abs(c) < 1e-10:
            continue
        
        sign = " + " if c > 0 and len(terms) > 0 else (" - " if c < 0 and len(terms) > 0 else ("-" if c < 0 else ""))
        val = abs(c)
        val_str = f"{val:.6g}" if (val != 1 or power == 0) else ""

        if power == 0:
            term = f"{val_str if val_str else '1'}"
        elif power == 1:
            term = f"{val_str}x"
        else:
            term = f"{val_str}x^{power}"

        terms.append(f"{sign}{term}")

    return "".join(terms) if terms else "0"
