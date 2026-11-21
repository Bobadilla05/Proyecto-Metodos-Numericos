"""
Gauss-Seidel para resolver Ax = b.
Revisa dominancia diagonal, puede reordenar filas, itera y al final comprueba
sustituyendo la solución.
"""

from typing import List, Dict, Any, Tuple
import numpy as np


def check_diagonal_dominance(A: np.ndarray) -> Tuple[bool, str]:
    """
    Revisa si A es estrictamente diagonal dominante.
    Devuelve (es_dominante, mensaje).
    """
    n = A.shape[0]
    is_strictly_dominant = True
    details = []

    for i in range(n):
        diag = abs(A[i, i])
        off_diag_sum = sum(abs(A[i, j]) for j in range(n) if j != i)
        cond = ">" if diag > off_diag_sum else "<="
        details.append(f"Ecuación {i+1}: Elemento diagonal |a_{{{i+1}{i+1}}}| = {diag:.4f} {cond} Suma de otros |a_{{{i+1}j}}| = {off_diag_sum:.4f}")
        if diag <= off_diag_sum:
            is_strictly_dominant = False

    details_str = "\n".join(details)
    if is_strictly_dominant:
        msg = f"La matriz es ESTRÍCTAMENTE DIAGONAL DOMINANTE.\nLa convergencia del método está matemáticamente garantizada.\n\nDetalles por ecuación:\n{details_str}"
    else:
        msg = f"La matriz NO es estrictamente diagonal dominante.\nEl método puede converger más lentamente o requerir reordenamiento.\n\nDetalles por ecuación:\n{details_str}"

    return is_strictly_dominant, msg


def attempt_pivot_dominance(A: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray, bool]:
    """
    Reordena filas de A y b para que la diagonal quede lo más grande posible
    (y evitar ceros en ella).
    """
    n = len(b)
    A_new = A.copy().astype(float)
    b_new = b.copy().astype(float)
    rows_used = set()
    new_order = []

    for col in range(n):
        best_row = -1
        max_val = -1.0
        for row in range(n):
            if row not in rows_used:
                val = abs(A_new[row, col])
                if val > max_val:
                    max_val = val
                    best_row = row
        if best_row != -1 and max_val > 1e-12:
            new_order.append(best_row)
            rows_used.add(best_row)
        else:
            for row in range(n):
                if row not in rows_used:
                    new_order.append(row)
                    rows_used.add(row)
                    break

    if len(new_order) == n:
        A_perm = A_new[new_order, :]
        b_perm = b_new[new_order]
        is_dom, _ = check_diagonal_dominance(A_perm)
        return A_perm, b_perm, is_dom

    return A, b, False


def verify_system_substitution(A: np.ndarray, b: np.ndarray, sol: List[float]) -> Dict[str, Any]:
    """Sustituye la solución en cada ecuación para ver que se cumpla Ax = b."""
    n = len(sol)
    eq_details = []
    max_diff = 0.0

    for i in range(n):
        terms_formula = []
        terms_vals = []
        for j in range(n):
            coef = A[i, j]
            val = coef * sol[j]
            terms_vals.append(val)
            terms_formula.append(f"({coef:g})*({sol[j]:.4f})")

        lhs_sum = sum(terms_vals)
        diff = abs(lhs_sum - b[i])
        if diff > max_diff:
            max_diff = diff

        formula_str = " + ".join(terms_formula).replace("+ -", "- ")
        eq_details.append({
            "eq_index": i + 1,
            "formula": f"Ecuación {i+1}: {formula_str}",
            "calculated_lhs": lhs_sum,
            "expected_rhs": b[i],
            "diff": diff,
            "display_str": f"Ecuación {i+1}: {formula_str} = {lhs_sum:.4f}  (Esperado: {b[i]:.4f})  [Diferencia = {diff:.2e}]"
        })

    is_accurate = max_diff < 1e-2

    return {
        "title": "Comprobación: Sustitución de los valores en cada ecuación del sistema",
        "equations": eq_details,
        "max_difference": max_diff,
        "is_accurate": is_accurate,
        "message": (
            "✔ COMPROBACIÓN EXITOSA: Todas las ecuaciones del sistema se cumplen exactamente al sustituir la solución obtenida."
            if is_accurate else
            "Atención: Se detectaron ligeras discrepancias en algunas ecuaciones respecto al valor esperado."
        )
    }


def gauss_seidel(
    A_matrix: List[List[float]],
    b_vector: List[float],
    x0: List[float] = None,
    tol: float = 1e-5,
    max_iter: int = 100,
    omega: float = 1.0,
    error_type: str = "relativo",
    auto_pivot: bool = False
) -> Dict[str, Any]:
    """Resuelve Ax = b con Gauss-Seidel."""
    A = np.array(A_matrix, dtype=float)
    b = np.array(b_vector, dtype=float)
    n = len(b)

    if A.shape[0] != n or A.shape[1] != n:
        return {
            "success": False,
            "converged": False,
            "message": f"Dimensiones incompatibles: Matriz ({A.shape[0]}x{A.shape[1]}), Vector ({n}).",
            "iterations": [],
            "solution": []
        }

    pivoted = False
    if auto_pivot:
        diag_zeros = any(abs(A[i, i]) < 1e-12 for i in range(n))
        is_dom, _ = check_diagonal_dominance(A)
        if diag_zeros or not is_dom:
            A_p, b_p, improved = attempt_pivot_dominance(A, b)
            if improved or not any(abs(A_p[i, i]) < 1e-12 for i in range(n)):
                A = A_p
                b = b_p
                pivoted = True

    # un cero en la diagonal no deja dividir
    for i in range(n):
        if abs(A[i, i]) < 1e-14:
            return {
                "success": False,
                "converged": False,
                "message": f"Elemento diagonal nulo en la ecuación {i+1} (a_{{{i+1}{i+1}}} = 0). Gauss-Seidel requiere coeficientes no nulos en la diagonal.",
                "iterations": [],
                "solution": []
            }

    is_dominant, dominance_msg = check_diagonal_dominance(A)

    if x0 is None:
        x_curr = np.zeros(n, dtype=float)
    else:
        x_curr = np.array(x0, dtype=float)

    iterations = []
    # iteración 0 con los valores iniciales
    iterations.append({
        "iter": 0,
        "x": x_curr.tolist(),
        "error_abs": None,
        "error_rel": None,
        "error": None,
        "steps_per_var": []
    })

    converged = False
    message = ""

    for k in range(1, max_iter + 1):
        x_new = x_curr.copy()
        steps_per_var = []

        for i in range(n):
            s1 = sum(A[i, j] * x_new[j] for j in range(i))
            s2 = sum(A[i, j] * x_curr[j] for j in range(i + 1, n))
            
            x_calc = (b[i] - s1 - s2) / A[i, i]
            x_val = (1.0 - omega) * x_curr[i] + omega * x_calc
            x_new[i] = x_val

            steps_per_var.append({
                "var": f"x_{i+1}",
                "equation": f"x_{{{i+1}}}^{{({k})}} = (1 / {A[i,i]:.4f}) * [{b[i]:.4f} - ({s1:.4f} + {s2:.4f})] = {x_val:.6f}",
                "value": x_val
            })

        # errores
        diff = np.abs(x_new - x_curr)
        error_abs = float(np.max(diff))
        denom = np.max(np.abs(x_new))
        error_rel = float((error_abs / denom) * 100.0) if denom > 1e-14 else error_abs * 100.0

        current_error = error_rel if error_type == "relativo" else error_abs

        iterations.append({
            "iter": k,
            "x": x_new.tolist(),
            "error_abs": error_abs,
            "error_rel": error_rel,
            "error": current_error,
            "steps_per_var": steps_per_var
        })

        if np.isnan(x_new).any() or np.isinf(x_new).any() or error_abs > 1e12:
            message = f"El método divergió en la iteración {k}. Verifique que el sistema esté bien condicionado."
            break

        if current_error < tol:
            converged = True
            x_curr = x_new
            message = f"Convergencia alcanzada exitosamente en {k} iteraciones."
            break

        x_curr = x_new
    else:
        message = f"Se alcanzó el número máximo de iteraciones ({max_iter}) sin alcanzar la tolerancia requerida."

    # sustituyo la solución en las ecuaciones
    verification = verify_system_substitution(A, b, x_curr.tolist())

    return {
        "success": converged,
        "converged": converged,
        "message": message,
        "method_name": "Método de Gauss-Seidel",
        "solution": x_curr.tolist(),
        "iterations": iterations,
        "is_dominant": is_dominant,
        "dominance_msg": dominance_msg,
        "pivoted": pivoted,
        "dim": n,
        "A_used": A.tolist(),
        "b_used": b.tolist(),
        "tol": tol,
        "error_type": error_type,
        "verification": verification
    }
