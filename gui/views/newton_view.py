"""Vista de entrada para la interpolación de Newton: pares (x, y) y un punto opcional a evaluar."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any, List

from methods.newton_interpolation import newton_divided_differences


class NewtonInterpolationView(ttk.Frame):
    def __init__(self, parent, on_solve_callback: Callable[[Dict[str, Any]], None], **kwargs):
        super().__init__(parent, **kwargs)
        self.on_solve_callback = on_solve_callback
        self._setup_ui()

    def _setup_ui(self):
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # entradas de x e y
        pts_frame = ttk.Frame(container)
        pts_frame.pack(fill=tk.X, pady=2)

        # x
        lbl_x = ttk.Label(
            pts_frame,
            text="Valores conocidos de la variable X (separados por coma o espacio):",
            font=("Segoe UI", 9, "bold")
        )
        lbl_x.pack(anchor=tk.W)
        self.entry_x = ttk.Entry(pts_frame, font=("Consolas", 10))
        self.entry_x.pack(fill=tk.X, pady=(2, 6))
        self.entry_x.insert(0, "1, 2, 4, 6")

        # y
        lbl_y = ttk.Label(
            pts_frame,
            text="Valores correspondientes de la función Y = f(X) (separados por coma o espacio):",
            font=("Segoe UI", 9, "bold")
        )
        lbl_y.pack(anchor=tk.W)
        self.entry_y = ttk.Entry(pts_frame, font=("Consolas", 10))
        self.entry_y.pack(fill=tk.X, pady=(2, 6))
        self.entry_y.insert(0, "1, 8, 64, 216")

        # fila para evaluar
        eval_frame = ttk.Frame(container)
        eval_frame.pack(fill=tk.X, pady=4)

        ttk.Label(eval_frame, text="Valor de X que deseas estimar o evaluar (x* opcional):", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.entry_x_eval = ttk.Entry(eval_frame, width=14, font=("Consolas", 9))
        self.entry_x_eval.pack(side=tk.LEFT, padx=(0, 15))
        self.entry_x_eval.insert(0, "3.5")

        ttk.Label(eval_frame, text="* Calcula el valor aproximado P(x*) sobre el polinomio resultante.", font=("Segoe UI", 8, "italic"), foreground="#64748b").pack(side=tk.LEFT)

        # botones de ejemplos
        btn_box = ttk.Frame(container)
        btn_box.pack(fill=tk.X, pady=(8, 2))

        btn_ex1 = ttk.Button(btn_box, text="💡 Cargar Ejemplo 1 (Cúbica)", command=self.load_example_1)
        btn_ex1.pack(side=tk.LEFT, padx=(0, 8))

        btn_ex2 = ttk.Button(btn_box, text="💡 Cargar Ejemplo 2 (Física)", command=self.load_example_2)
        btn_ex2.pack(side=tk.LEFT, padx=(0, 8))

        btn_ex3 = ttk.Button(btn_box, text="💡 Cargar Ejemplo 3 (Temperatura)", command=self.load_example_3)
        btn_ex3.pack(side=tk.LEFT, padx=(0, 8))

        btn_clear = ttk.Button(btn_box, text="🗑 Limpiar Puntos", command=self.clear_fields)
        btn_clear.pack(side=tk.LEFT)

    def load_example_1(self):
        # y = x^3: (1,1), (2,8), (4,64), (6,216)
        self.entry_x.delete(0, tk.END)
        self.entry_x.insert(0, "1, 2, 4, 6")
        self.entry_y.delete(0, tk.END)
        self.entry_y.insert(0, "1, 8, 64, 216")
        self.entry_x_eval.delete(0, tk.END)
        self.entry_x_eval.insert(0, "3.5")

    def load_example_2(self):
        # tiempo vs velocidad
        self.entry_x.delete(0, tk.END)
        self.entry_x.insert(0, "0, 10, 15, 20, 22.5")
        self.entry_y.delete(0, tk.END)
        self.entry_y.insert(0, "0, 227.04, 362.78, 517.35, 602.97")
        self.entry_x_eval.delete(0, tk.END)
        self.entry_x_eval.insert(0, "16.0")

    def load_example_3(self):
        # temperatura vs presión
        self.entry_x.delete(0, tk.END)
        self.entry_x.insert(0, "20, 40, 60, 80")
        self.entry_y.delete(0, tk.END)
        self.entry_y.insert(0, "2.34, 7.38, 19.9, 47.3")
        self.entry_x_eval.delete(0, tk.END)
        self.entry_x_eval.insert(0, "50.0")

    def clear_fields(self):
        self.entry_x.delete(0, tk.END)
        self.entry_y.delete(0, tk.END)
        self.entry_x_eval.delete(0, tk.END)

    def solve(self):
        """Valida las entradas y corre la interpolación de Newton."""
        raw_x = self.entry_x.get().strip()
        raw_y = self.entry_y.get().strip()

        if not raw_x or not raw_y:
            messagebox.showerror("Campos Vacíos", "Debes ingresar las listas de valores de X e Y.")
            return

        try:
            x_pts = [float(p) for p in raw_x.replace(",", " ").split() if p]
            y_pts = [float(p) for p in raw_y.replace(",", " ").split() if p]
        except ValueError:
            messagebox.showerror("Error de Formato", "Todos los puntos de X e Y deben ser números reales (ej: 1, 2, 4, 6).")
            return

        if len(x_pts) < 2:
            messagebox.showerror("Puntos Insuficientes", "Se requieren al menos 2 puntos para poder interpolar.")
            return

        if len(x_pts) != len(y_pts):
            messagebox.showerror("Discrepancia de Tamaños", f"La cantidad de valores en X ({len(x_pts)}) no coincide con la cantidad en Y ({len(y_pts)}).")
            return

        x_eval_val = None
        raw_eval = self.entry_x_eval.get().strip()
        if raw_eval:
            try:
                x_eval_val = float(raw_eval)
            except ValueError:
                messagebox.showerror("Error de Formato", "El valor de X a evaluar debe ser un número real o dejarse vacío.")
                return

        res = newton_divided_differences(
            x_points=x_pts,
            y_points=y_pts,
            x_eval=x_eval_val
        )

        if not res.get("success", False):
            messagebox.showwarning("Atención en el Cálculo", res.get("message", "Error al calcular el polinomio."))
            return

        self.on_solve_callback(res)
