"""
Prueba de la interfaz Tkinter sin interacción: Bisección, Birge-Vieta, Gauss-Seidel,
comprobaciones y el toggle del procedimiento.
"""

import unittest
from gui.app import NumericalMethodsApp


class TestGUIIntegration(unittest.TestCase):

    def test_app_lifecycle_and_methods(self):
        app = NumericalMethodsApp()
        app.withdraw()

        # al inicio los resultados deben estar ocultos
        self.assertFalse(app.result_section.winfo_ismapped())
        self.assertFalse(app.procedure_visible)

        # birge-vieta
        app.selected_method.set("birge_vieta")
        app._on_method_selected()
        bv_view = app.views["birge_vieta"]
        bv_view.load_example_1()
        bv_view.solve()

        self.assertIsNotNone(app.last_result)
        self.assertIn("Birge-Vieta", app.last_result["method_name"])
        self.assertTrue(app.last_result["converged"])
        self.assertTrue(app.result_section.winfo_ismapped())
        self.assertIn("verification", app.last_result)
        self.assertTrue(app.last_result["verification"]["is_accurate"])

        # toggle del procedimiento
        self.assertFalse(app.procedure_visible)
        app.toggle_procedure_view()
        self.assertTrue(app.procedure_visible)
        proc_text = app.lbl_proc_summary.cget("text").upper()
        self.assertIn("HORNER", proc_text)
        self.assertIn("NEWTON-RAPHSON", proc_text)
        app.toggle_procedure_view()
        self.assertFalse(app.procedure_visible)

        # bisección
        app.selected_method.set("bisection")
        app._on_method_selected()
        self.assertFalse(app.result_section.winfo_ismapped())

        bisect_view = app.views["bisection"]
        bisect_view.load_example_1()
        bisect_view.solve()

        self.assertIsNotNone(app.last_result)
        self.assertIn("Bisección", app.last_result["method_name"])
        self.assertTrue(app.last_result["converged"])
        self.assertTrue(app.result_section.winfo_ismapped())
        self.assertIn("verification", app.last_result)
        self.assertTrue(app.last_result["verification"]["is_accurate"])

        # gauss-seidel
        app.selected_method.set("gauss_seidel")
        app._on_method_selected()
        self.assertFalse(app.result_section.winfo_ismapped())

        gs_view = app.views["gauss_seidel"]
        gs_view.load_example_1()
        gs_view.solve()

        self.assertIsNotNone(app.last_result)
        self.assertIn("Gauss-Seidel", app.last_result["method_name"])
        self.assertTrue(app.last_result["converged"])
        self.assertTrue(app.result_section.winfo_ismapped())
        self.assertIn("verification", app.last_result)
        self.assertTrue(app.last_result["verification"]["is_accurate"])

        # cierro la ventana
        app.destroy()


if __name__ == "__main__":
    unittest.main()
