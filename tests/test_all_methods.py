"""Pruebas de los métodos numéricos (carga de CPU de un servidor escolar)."""

import unittest
import numpy as np

from methods.birge_vieta import birge_vieta, format_polynomial
from methods.bisection import bisection, format_hour_to_time_str
from methods.gauss_seidel import gauss_seidel, check_diagonal_dominance


class TestNumericalMethods(unittest.TestCase):

    def test_bisection_server_load(self):
        # C(t) = -2.5 t^2 + 60 t - 270
        # umbral 85%
        # raíz esperada en [8, 12]: t ≈ 10.5858
        coeffs = [-2.5, 60.0, -270.0]
        res = bisection(coeffs, a=8.0, b=12.0, threshold=85.0, tol=1e-4)
        self.assertTrue(res["converged"])
        self.assertAlmostEqual(res["root"], 10.5858, places=3)
        self.assertAlmostEqual(res["final_cpu"], 85.0, delta=0.1)
        self.assertTrue(res["verification"]["is_accurate"])

    def test_bisection_cubic(self):
        # cúbica: C(t) = -0.2 t^3 + 4.5 t^2 - 15 t - 40
        # umbral 85%, intervalo [10, 13]
        coeffs = [-0.2, 4.5, -15.0, -40.0]
        res = bisection(coeffs, a=10.0, b=13.0, threshold=85.0, tol=1e-4)
        self.assertTrue(res["converged"])
        self.assertAlmostEqual(res["final_cpu"], 85.0, delta=0.1)

    def test_birge_vieta_server_load(self):
        # mismo C(t), umbral 85%, t0 = 9.0
        coeffs = [-2.5, 60.0, -270.0]
        res = birge_vieta(coeffs, x0=9.0, threshold=85.0, tol=1e-5)
        self.assertTrue(res["converged"])
        self.assertAlmostEqual(res["root"], 10.5858, places=3)
        self.assertAlmostEqual(res["final_cpu"], 85.0, delta=0.01)
        self.assertTrue(res["verification"]["is_accurate"])

    def test_birge_vieta_polynomial_standard(self):
        # P(x) = x^3 - 6x^2 + 11x - 6 = (x-1)(x-2)(x-3)
        res = birge_vieta([1, -6, 11, -6], x0=3.5, threshold=0.0, tol=1e-5)
        self.assertTrue(res["converged"])
        self.assertAlmostEqual(res["root"], 3.0, places=4)

    def test_gauss_seidel_cluster(self):
        # sistema de 3 servidores:
        # 10x1 - x2 + 2x3 = 60
        # -x1 + 11x2 - x3 = 85
        # 2x1 - x2 + 10x3 = 45
        A = [
            [10.0, -1.0, 2.0],
            [-1.0, 11.0, -1.0],
            [2.0, -1.0, 10.0]
        ]
        b = [60.0, 85.0, 45.0]

        is_dom, _ = check_diagonal_dominance(np.array(A))
        self.assertTrue(is_dom)

        res = gauss_seidel(A, b, tol=1e-5, max_iter=50)
        self.assertTrue(res["converged"])
        sol = res["solution"]

        # reviso Ax - b
        residual = np.dot(np.array(A), np.array(sol)) - np.array(b)
        for r in residual:
            self.assertAlmostEqual(r, 0.0, places=3)
        self.assertTrue(res["verification"]["is_accurate"])


if __name__ == "__main__":
    unittest.main()
